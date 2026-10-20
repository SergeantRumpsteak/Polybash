"""Polybash - Polytown neu fuer das Spiel exportieren (reines Python, ohne Blender).

Baut dieselbe Szene wie polytown_neu.py (mit einer Attrappe fuer bpy), faengt dabei alle Meshes, Materialien und
Kollisionsquader (Bau.bx) ab und schreibt sie als  maps/polytown.ptmap  - die Standardkarte des Spiels.

Start:   python3 export_spiel.py [Ausgabedatei]          (Standard: ../../../maps/polytown.ptmap)

Inhalt der Datei (spiel.py: load_ptmap / build_pt_scene):
  * Darstellung: Flaechen in 32-m-Bloecken, je Block vier Klassen (0 opak, 1 opak zweiseitig, 2 durchsichtig, 3 leuchtend).
    Die Beleuchtung (Sonne + Umgebung wie Mesh.tri im Spiel) steckt schon in den Vertexfarben; Normalen fuer die Schatten.
  * Kollision: Gelaende-Dreiecke (TriMesh der Engine) + Quader (Bau.bx, benachbarte Kacheln verschmolzen).
  * Spiel-Daten: Startpunkte, Fahrzeuge, Helipad, Kisten, Minimap.
Der statische Kampfhubschrauber der Blender-Szene wird weggelassen: auf dem Helipad steht der flugfaehige Spiel-Hubschrauber.
"""
import array
import collections
import json
import math
import os
import re
import struct
import sys
import zlib
from unittest.mock import MagicMock

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))            # .../Polybash
if "bpy" not in sys.modules:
    sys.modules["bpy"] = MagicMock()

import burg as B  # noqa: E402
import talkessel as T  # noqa: E402

PT_MAGIC = b"PBPT1\n"
PT_FORMAT = "polybash-ptmap"
PT_ID = "b1e55ed9a07c3d42"                       # feste Kennung der Karte (Mitspieler finden die Datei damit)
CH = 32.0                                         # Blockgroesse der Darstellung (m)
MAXV = 60000                                      # Vertices je Geom (16-Bit-Indizes)
WELT = 300.0
SPIN_NAMEN = {"tower_radar": 6.0 * 24.0}          # drehende Teile: Grad pro Sekunde (6 Grad je Bild bei 24 B/s wie in Blender)
BODEN = ("wiese", "berge", "burg_gelaende", "bruch_grube", "umgebung_wege", "stadt_wege", "umgebung_landebahn",
         "umgebung_helipad", "hof_boden", "acker", "ruine_weg")                  # begehbares Gelaende (Kollision als Dreiecke)

# ------------------------------------------------------------------ Abfangen der Blender-Aufrufe
MATS = {}
TEILE = []
BAUS = {}


class _Ob:
    def __init__(self):
        self.location = (0.0, 0.0, 0.0)
        self.rotation_euler = (0.0, 0.0, 0.0)
        self.data = MagicMock()

    def __getattr__(self, k):
        return MagicMock()


def _material(name, rgb, rauh=0.95, emit=0.0, alpha=1.0):
    MATS[name] = (tuple(rgb[:3]), rauh, emit, alpha)
    return name


def _add_mesh(coll, name, verts, faces, mats, mat_index=None, edges=None):
    ob = _Ob()
    TEILE.append(dict(name=name, v=verts, f=faces, mats=list(mats), idx=None if mat_index is None else list(mat_index), ob=ob,
                      bau=BAUS.get(id(verts))))
    return ob


_bau_init = B.Bau.__init__


def _init(self, name):
    _bau_init(self, name)
    BAUS[id(self.v)] = self


def licht_konstanten():
    """SUN, AMBIENT, DIFFUSE aus spiel.py (damit die Farben zu den anderen Spielobjekten passen)."""
    sun, amb, dif = (0.45, 0.30, 0.84), 0.60, 0.66
    try:
        with open(os.path.join(REPO, "spiel.py"), encoding="utf-8") as f:
            kopf = f.read(80000)
        m = re.search(r"^SUN = \(([^)]*)\)", kopf, re.M)
        if m:
            sun = tuple(float(s) for s in m.group(1).split(","))
        m = re.search(r"^AMBIENT, DIFFUSE = ([0-9.]+), ([0-9.]+)", kopf, re.M)
        if m:
            amb, dif = float(m.group(1)), float(m.group(2))
    except OSError:
        pass
    ln = math.sqrt(sum(c * c for c in sun))
    return tuple(c / ln for c in sun), amb, dif


def szene_bauen():
    T.material, T.add_mesh = _material, _add_mesh
    B.Bau.__init__ = _init
    import polytown_neu as P
    P.main()
    B.Bau.__init__ = _bau_init


# ------------------------------------------------------------------ Hilfen
def newell(pts):
    nx = ny = nz = 0.0
    for i in range(len(pts)):
        a, b = pts[i], pts[(i + 1) % len(pts)]
        nx += (a[1] - b[1]) * (a[2] + b[2])
        ny += (a[2] - b[2]) * (a[0] + b[0])
        nz += (a[0] - b[0]) * (a[1] + b[1])
    ln = math.sqrt(nx * nx + ny * ny + nz * nz)
    return None if ln < 1e-12 else (nx / ln, ny / ln, nz / ln)


def oct_code(n):
    """Einheitsnormale -> 16 Bit (Oktaeder-Kodierung)."""
    x, y, z = n
    s = abs(x) + abs(y) + abs(z)
    x, y = x / s, y / s
    if z < 0.0:
        x, y = (1.0 - abs(y)) * (1.0 if x >= 0 else -1.0), (1.0 - abs(x)) * (1.0 if y >= 0 else -1.0)
    return (int(round((x * 0.5 + 0.5) * 255)) << 8) | int(round((y * 0.5 + 0.5) * 255))


def teile_umrechnen():
    """Teile in Weltkoordinaten (Objektposition/-drehung anwenden); drehende Teile bleiben lokal."""
    out = []
    for t in TEILE:
        if not t["f"]:
            continue
        loc, rot = t["ob"].location, t["ob"].rotation_euler
        try:
            lx, ly, lz = (float(c) for c in loc)
            rz = float(rot[2])
        except (TypeError, ValueError):
            lx = ly = lz = rz = 0.0
        spin = SPIN_NAMEN.get(t["name"])
        v = [tuple(p) for p in t["v"]]
        if (lx or ly or lz or rz) and spin is None:
            cs, sn = math.cos(rz), math.sin(rz)
            v = [(lx + x * cs - y * sn, ly + x * sn + y * cs, lz + z) for x, y, z in v]
            t["verschoben"] = True
        t["w"] = v
        t["spin"] = None if spin is None else dict(x=lx, y=ly, z=lz, h0=math.degrees(rz), speed=spin)
        namen = t["mats"]
        t["fm"] = [namen[i] for i in t["idx"]] if t["idx"] is not None else [namen[0]] * len(t["f"])
        out.append(t)
    return out


# ------------------------------------------------------------------ Darstellung
class Gruppe:
    def __init__(self, cls, spin, key=None):
        self.cls, self.spin, self.key = cls, spin, key
        self.P, self.N, self.C, self.I = array.array("f"), array.array("H"), bytearray(), array.array("H")
        self.nv = 0


def ausrichten(v, faces, zaehl):
    """Geschlossene Koerper (Boxen, Prismen, Lofts: zusammenhaengende Indizes, jede Kante in genau zwei Flaechen) mit negativem
    Volumen haben nach innen zeigende Flaechen - die wuerde das Spiel wegen Backface-Culling nicht zeichnen. Sie werden umgedreht."""
    par = {}

    def find(a):
        while par.setdefault(a, a) != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for fc in faces:
        r = find(fc[0])
        for i in fc[1:]:
            q = find(i)
            if q != r:
                par[q] = r
    komp = collections.defaultdict(list)
    for k, fc in enumerate(faces):
        komp[find(fc[0])].append(k)
    out = list(faces)
    for ks in komp.values():
        kanten = collections.Counter()
        vol = 0.0
        for k in ks:
            fc = faces[k]
            n = len(fc)
            for i in range(n):
                a, b = fc[i], fc[(i + 1) % n]
                kanten[(a, b) if a < b else (b, a)] += 1
            p0 = v[fc[0]]
            for i in range(1, n - 1):
                p1, p2 = v[fc[i]], v[fc[i + 1]]
                vol += (p0[0] * (p1[1] * p2[2] - p1[2] * p2[1]) - p0[1] * (p1[0] * p2[2] - p1[2] * p2[0])
                        + p0[2] * (p1[0] * p2[1] - p1[1] * p2[0])) / 6.0
        if any(c != 2 for c in kanten.values()):
            zaehl["offen"] += len(ks)
            continue
        zaehl["geschlossen"] += len(ks)
        if vol < -1e-9:
            zaehl["umgedreht"] += len(ks)
            for k in ks:
                out[k] = tuple(reversed(faces[k]))
    return out


def darstellung(teile):
    sun, amb, dif = licht_konstanten()
    gruppen = {}
    fertig = []
    zaehl = collections.Counter()

    def gruppe(cls, key, spin):
        g = gruppen.get((cls, key))
        if g is None:
            g = gruppen[(cls, key)] = Gruppe(cls, spin, None if spin else list(key))
        return g

    for t in teile:
        v, faces, fm = t["w"], t["f"], t["fm"]
        kanten = collections.Counter()
        vk = [(round(p[0] * 1000), round(p[1] * 1000), round(p[2] * 1000)) for p in v]
        for fc in faces:
            n = len(fc)
            for i in range(n):
                a, b = vk[fc[i]], vk[fc[(i + 1) % n]]
                kanten[(a, b) if a < b else (b, a)] += 1
        faces = ausrichten(v, faces, zaehl)
        for fc, mn in zip(faces, fm):
            if mn.startswith("Heli "):
                zaehl["heli"] += 1
                continue
            pts = [v[i] for i in fc]
            nrm = newell(pts)
            if nrm is None or len(fc) < 3:
                zaehl["entartet"] += 1
                continue
            rgb, _rauh, emit, alpha = MATS[mn]
            if emit >= 1.0:
                cls, f3 = 3, (1.0, 1.0, 1.0)
            else:
                d = max(0.0, nrm[0] * sun[0] + nrm[1] * sun[1] + nrm[2] * sun[2])
                kd = dif * d
                f3 = (amb * 0.94 + kd * 1.07, amb + kd, amb * 1.07 + kd * 0.9)
                cls = 2 if alpha < 1.0 else 0
            if cls == 0:
                n = len(fc)
                for i in range(n):
                    a, b = vk[fc[i]], vk[fc[(i + 1) % n]]
                    if kanten[(a, b) if a < b else (b, a)] == 1:
                        cls = 1
                        break
            col = bytes((min(255, int(rgb[0] * f3[0] * 255 + 0.5)), min(255, int(rgb[1] * f3[1] * 255 + 0.5)),
                         min(255, int(rgb[2] * f3[2] * 255 + 0.5)), min(255, int(alpha * 255 + 0.5))))
            if t["spin"]:
                key = ("spin", t["name"])
            else:
                cx = sum(p[0] for p in pts) / len(pts)
                cy = sum(p[1] for p in pts) / len(pts)
                key = (int(math.floor(cx / CH)), int(math.floor(cy / CH)))
            g = gruppe(cls, key, t["spin"])
            if g.nv + len(pts) > MAXV:
                fertig.append(gruppen.pop((cls, key)))
                g = gruppe(cls, key, t["spin"])
            base = g.nv
            code = oct_code(nrm)
            for p in pts:
                g.P.extend(p)
                g.N.append(code)
                g.C += col
            for i in range(1, len(pts) - 1):
                g.I.extend((base, base + i, base + i + 1))
            g.nv += len(pts)
            zaehl["flaechen"] += 1
    fertig.extend(gruppen.values())
    fertig.sort(key=lambda g: (g.key or [-9999, -9999], g.cls))
    print("[Export] Darstellung:", dict(zaehl), "Gruppen", len(fertig), "Vertices", sum(g.nv for g in fertig))
    return fertig


# ------------------------------------------------------------------ Kollision
def gelaende_dreiecke(teile):
    verts, tris = [], []
    for t in teile:
        if t["name"] not in BODEN:
            continue
        v = t["w"]
        off = len(verts)
        verts.extend(v)
        for fc, mn in zip(t["f"], t["fm"]):
            if t["name"] == "berge":
                cx = sum(v[i][0] for i in fc) / len(fc)
                cy = sum(v[i][1] for i in fc) / len(fc)
                if not (-60.0 <= cx <= WELT + 60.0 and -60.0 <= cy <= WELT + 60.0):
                    continue
            for i in range(1, len(fc) - 1):
                tris.append((off + fc[0], off + fc[i], off + fc[i + 1]))
    # nur benutzte Vertices behalten
    benutzt = sorted({i for tr in tris for i in tr})
    neu = {a: k for k, a in enumerate(benutzt)}
    verts2 = [verts[a] for a in benutzt]
    tris2 = [(neu[a], neu[b], neu[c]) for a, b, c in tris]
    print("[Export] Gelaende-Kollision:", len(verts2), "Vertices,", len(tris2), "Dreiecke")
    return verts2, tris2


def quader_sammeln(teile):
    boxes = set()
    for t in teile:
        bau = t["bau"]
        if bau is None or t["spin"] is not None or t.get("verschoben"):
            continue
        for b in bau.bx:
            x0, y0, z0, x1, y1, z1 = b
            if x1 < -2.0 or x0 > WELT + 2.0 or y1 < -2.0 or y0 > WELT + 2.0:
                continue
            boxes.add(tuple(round(c, 4) for c in (min(x0, x1), min(y0, y1), min(z0, z1), max(x0, x1), max(y0, y1), max(z0, z1))))
    return sorted(boxes)


def quader_verschmelzen(boxes):
    """Nebeneinanderliegende Quader mit gleichem Querschnitt zu einem verschmelzen (gedrehte Waende sind aus Kacheln)."""
    def pass_(bs, ax):
        o = (1, 2) if ax == 0 else ((0, 2) if ax == 1 else (0, 1))
        grp = collections.defaultdict(list)
        for b in bs:
            grp[(b[o[0]], b[o[1]], b[o[0] + 3], b[o[1] + 3])].append(b)
        out = []
        for lst in grp.values():
            lst.sort(key=lambda b: b[ax])
            cur = list(lst[0])
            for b in lst[1:]:
                if b[ax] <= cur[ax + 3] + 1e-4:
                    cur[ax + 3] = max(cur[ax + 3], b[ax + 3])
                else:
                    out.append(tuple(cur))
                    cur = list(b)
            out.append(tuple(cur))
        return out
    n0 = len(boxes)
    for _ in range(2):
        for ax in (0, 1, 2):
            boxes = pass_(boxes, ax)
    print("[Export] Quader:", n0, "->", len(boxes))
    return sorted(boxes)


# ------------------------------------------------------------------ Raster fuer Spiel-Daten
class Raster:
    """Gelaendehoehe (0,5 m), Hindernisse, Wasser, Wege - nur fuer Startpunkte, Fahrzeuge und Minimap."""
    S = 0.5

    def __init__(self, teile, boxes):
        n = int(WELT / self.S)
        self.n = n
        self.H = [[-99.0] * n for _ in range(n)]
        self.wasser = [[False] * n for _ in range(n)]
        self.weg = [[False] * n for _ in range(n)]
        self.sperr = [[False] * n for _ in range(n)]
        for t in teile:
            if t["name"] in BODEN:
                weg = t["name"] in ("umgebung_wege", "stadt_wege", "umgebung_landebahn")
                for fc in t["f"]:
                    ps = [t["w"][i] for i in fc]
                    for i in range(1, len(ps) - 1):
                        self._dreieck(ps[0], ps[i], ps[i + 1], self.H, None, True)
                        if weg:
                            self._dreieck(ps[0], ps[i], ps[i + 1], None, self.weg, False)
        for t in teile:
            for fc, mn in zip(t["f"], t["fm"]):
                if "wasser" in mn.lower():
                    ps = [t["w"][i] for i in fc]
                    for i in range(1, len(ps) - 1):
                        self._dreieck(ps[0], ps[i], ps[i + 1], None, self.wasser, False)
        for x0, y0, z0, x1, y1, z1 in boxes:
            for i in range(max(0, int(x0 / self.S)), min(n, int(x1 / self.S) + 1)):
                for j in range(max(0, int(y0 / self.S)), min(n, int(y1 / self.S) + 1)):
                    g = self.H[j][i]
                    if z1 > g + 0.4 and z0 < g + 1.8:
                        self.sperr[j][i] = True

    def _dreieck(self, a, b, c, hoehe, flag, nur_oben):
        S, n = self.S, self.n
        x0, x1 = min(a[0], b[0], c[0]), max(a[0], b[0], c[0])
        y0, y1 = min(a[1], b[1], c[1]), max(a[1], b[1], c[1])
        det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
        if abs(det) < 1e-12:
            return
        if nur_oben and det < 0:                                  # Unterseite / senkrecht
            return
        for i in range(max(0, int(x0 / S)), min(n, int(x1 / S) + 1)):
            px = (i + 0.5) * S
            for j in range(max(0, int(y0 / S)), min(n, int(y1 / S) + 1)):
                py = (j + 0.5) * S
                l1 = ((b[1] - c[1]) * (px - c[0]) + (c[0] - b[0]) * (py - c[1])) / det
                l2 = ((c[1] - a[1]) * (px - c[0]) + (a[0] - c[0]) * (py - c[1])) / det
                l3 = 1.0 - l1 - l2
                if l1 < -0.02 or l2 < -0.02 or l3 < -0.02:
                    continue
                if hoehe is not None:
                    z = l1 * a[2] + l2 * b[2] + l3 * c[2]
                    if z > hoehe[j][i]:
                        hoehe[j][i] = z
                if flag is not None:
                    flag[j][i] = True

    def h(self, x, y):
        i, j = min(self.n - 1, max(0, int(x / self.S))), min(self.n - 1, max(0, int(y / self.S)))
        return self.H[j][i]

    def frei(self, x, y, r, wasser=True):
        """Kreis (x,y,r): flach, kein Hindernis, kein Wasser."""
        S = self.S
        h0 = self.h(x, y)
        if h0 < -5.0:
            return False
        k = int(r / S)
        i0, j0 = int(x / S), int(y / S)
        for di in range(-k, k + 1):
            for dj in range(-k, k + 1):
                i, j = i0 + di, j0 + dj
                if not (0 <= i < self.n and 0 <= j < self.n) or di * di + dj * dj > k * k:
                    continue
                if self.sperr[j][i] or (wasser and self.wasser[j][i]) or abs(self.H[j][i] - h0) > 0.45:
                    return False
        return True

    def bebaut(self, x, y, r):
        S = self.S
        k = int(r / S)
        i0, j0 = int(x / S), int(y / S)
        tot = bel = 0
        for di in range(-k, k + 1, 2):
            for dj in range(-k, k + 1, 2):
                i, j = i0 + di, j0 + dj
                if 0 <= i < self.n and 0 <= j < self.n:
                    tot += 1
                    bel += self.sperr[j][i]
        return bel / max(1, tot)


def spiel_daten(R):
    cand = []
    for gx in range(12, 289, 6):
        for gy in range(12, 289, 6):
            x, y = gx + 0.0, gy + 0.0
            if R.frei(x, y, 1.5) and R.bebaut(x, y, 6.0) < 0.35 and R.h(x, y) > -1.0:
                cand.append((x, y))
    print("[Export] Startpunkt-Kandidaten:", len(cand))

    def streuen(punkte, n, start):
        gew = [min(punkte, key=lambda p: math.hypot(p[0] - start[0], p[1] - start[1]))]
        rest = [p for p in punkte if p != gew[0]]
        while rest and len(gew) < n:
            nxt = max(rest, key=lambda p: min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in gew))
            rest.remove(nxt)
            gew.append(nxt)
        return gew
    spawns = streuen(cand, 64, (150.0, 60.0))
    rest = [p for p in cand if p not in spawns and 0.04 < R.bebaut(p[0], p[1], 5.0) < 0.3]
    crates = streuen(rest, 12, (150.0, 150.0)) if rest else []
    # Fahrzeuge auf Wegen (frei, flach), Front zur Burgmitte
    wege = [(x, y) for x, y in ((gx * 1.0, gy * 1.0) for gx in range(20, 281, 2) for gy in range(20, 281, 2))
            if R.weg[int(y / R.S)][int(x / R.S)] and R.frei(x, y, 3.0, True) and R.bebaut(x, y, 8.0) < 0.2]
    fahrzeuge = []
    for ziel in ((150.0, 70.0), (150.0, 232.0)):
        if wege:
            x, y = min(wege, key=lambda p: math.hypot(p[0] - ziel[0], p[1] - ziel[1]))
            hd = math.degrees(math.atan2(-(150.0 - x), 150.0 - y))
            fahrzeuge.append([round(x, 2), round(y, 2), round(hd, 1)])
    print("[Export] Startpunkte", len(spawns), "Kisten", len(crates), "Fahrzeuge", fahrzeuge)
    return ([[round(x, 2), round(y, 2), round(R.h(x, y), 3)] for x, y in spawns],
            [[round(x, 2), round(y, 2)] for x, y in crates], fahrzeuge)


def minimap(teile, R, px=2.0):
    """Draufsicht 150 x 150 (2 m je Pixel): oberste nach oben zeigende Flaeche, mit Materialfarbe."""
    n = int(WELT / px)
    top = [[-1e9] * n for _ in range(n)]
    col = [[(0.07, 0.09, 0.12)] * n for _ in range(n)]
    for t in teile:
        if t["name"] == "berge":
            continue
        v = t["w"]
        for fc, mn in zip(t["f"], t["fm"]):
            if mn.startswith("Heli ") or MATS[mn][3] < 0.5 or MATS[mn][2] >= 1.0:
                continue
            ps = [v[i] for i in fc]
            nrm = newell(ps)
            if nrm is None or nrm[2] < 0.3:
                continue
            xs = [p[0] for p in ps]
            ys = [p[1] for p in ps]
            zc = sum(p[2] for p in ps) / len(ps)
            rgb = MATS[mn][0]
            for i in range(max(0, int(min(xs) / px)), min(n, int(max(xs) / px) + 1)):
                for j in range(max(0, int(min(ys) / px)), min(n, int(max(ys) / px) + 1)):
                    cx, cy = (i + 0.5) * px, (j + 0.5) * px
                    if len(ps) == 3 and (max(xs) - min(xs) > px or max(ys) - min(ys) > px):
                        a, b, c = ps
                        det = (b[1] - c[1]) * (a[0] - c[0]) + (c[0] - b[0]) * (a[1] - c[1])
                        if abs(det) < 1e-12:
                            continue
                        l1 = ((b[1] - c[1]) * (cx - c[0]) + (c[0] - b[0]) * (cy - c[1])) / det
                        l2 = ((c[1] - a[1]) * (cx - c[0]) + (a[0] - c[0]) * (cy - c[1])) / det
                        if l1 < 0 or l2 < 0 or l1 + l2 > 1:
                            continue
                    if zc > top[j][i]:
                        top[j][i] = zc
                        col[j][i] = rgb
    out = bytearray(n * n * 3)
    for j in range(n):
        for i in range(n):
            z = top[j][i]
            k = (j * n + i) * 3
            hx = R.h((i + 1.5) * px, (j + 0.5) * px) - R.h((i - 0.5) * px, (j + 0.5) * px)
            sh = 0.92 - 0.06 * max(-3.0, min(3.0, hx))
            r, g, b = col[j][i]
            out[k], out[k + 1], out[k + 2] = (min(255, int(c * sh * 255 + 0.5)) for c in (r, g, b))
    return n, bytes(out)


# ------------------------------------------------------------------ Schreiben
def schreiben(pfad, gruppen, verts, tris, boxes, spawns, crates, fahrzeuge, mm):
    little = sys.byteorder == "little"

    def b(a):
        if not little:
            a = array.array(a.typecode, a)
            a.byteswap()
        return a.tobytes()
    meta = dict(name="Polytown", id=PT_ID, size=WELT, groups=[], ncm=[len(verts), len(tris)], nbox=len(boxes), mm=mm[0],
                spawns=spawns, crates=crates, vehicles=fahrzeuge, pads=[[240.0, 184.0, 110.0]],
                gras_hoehe=None)
    blob = bytearray()
    for g in gruppen:
        meta["groups"].append(dict(c=g.cls, nv=g.nv, ni=len(g.I), sp=g.spin, k=g.key))
        blob += b(g.P) + b(g.N) + bytes(g.C) + b(g.I)
    va = array.array("f")
    for p in verts:
        va.extend(p)
    ta = array.array("I")
    for t in tris:
        ta.extend(t)
    blob += b(va) + b(ta)
    ba = array.array("f")
    for q in boxes:
        ba.extend(q)
    blob += b(ba)
    blob += mm[1]
    mj = json.dumps(meta, separators=(",", ":")).encode("utf-8")
    raw = struct.pack("<I", len(mj)) + mj + bytes(blob)
    comp = zlib.compress(raw, 9)
    head = json.dumps(dict(format=PT_FORMAT, id=PT_ID, name="Polytown", author="Polybash"), separators=(",", ":")).encode("utf-8")
    os.makedirs(os.path.dirname(os.path.abspath(pfad)), exist_ok=True)
    with open(pfad, "wb") as f:
        f.write(PT_MAGIC + struct.pack("<I", len(head)) + head + struct.pack("<I", len(comp)) + comp)
    print(f"[Export] {pfad}: roh {len(raw) / 1e6:.1f} MB, Datei {len(comp) / 1e6:.1f} MB")


def main():
    pfad = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO, "maps", "polytown.ptmap")
    szene_bauen()
    teile = teile_umrechnen()
    gruppen = darstellung(teile)
    verts, tris = gelaende_dreiecke(teile)
    boxes = quader_verschmelzen(quader_sammeln(teile))
    R = Raster(teile, boxes)
    spawns, crates, fahrzeuge = spiel_daten(R)
    mm = minimap(teile, R)
    schreiben(pfad, gruppen, verts, tris, boxes, spawns, crates, fahrzeuge, mm)


if __name__ == "__main__":
    main()
