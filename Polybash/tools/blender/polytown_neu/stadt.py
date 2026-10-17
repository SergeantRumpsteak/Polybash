"""Polybash - kleine Stadt um Burg und Flughafen (noch ohne Texturen, nur Farben).

Aufbau (Spielflaeche 0..300 m, Burg in der Mitte, Ringweg, Flughafen im Osten - siehe umgebung.py):
  * Stadt im Westen: Hauptstrasse vom Ringweg zum Marktplatz (30 x 30 m) mit Brunnen und Marktstaenden; am Platz das Rathaus
    (mit Uhrturm) im Norden, das Gasthaus im Sueden und je zwei Laeden im Westen und Osten. Um den Platz laeuft die runde
    Marktring-Strasse, an ihr und an der Hauptstrasse stehen die Wohnhaeuser.
  * Zwei Querspangen verbinden die Stadt mit der Nord- und der Suedstrasse (die vom Ringweg an den Burgtoren nach Norden bzw.
    Sueden fuehren). Im Norden liegt ein Dorf mit Kreisverkehr, Dorfbrunnen, Bauernhof und Haeusern; die Suedstrasse endet dagegen am
    Bahnhofsvorplatz (bahn.py). Von der Spange Sued fuehrt die Werkstrasse zum Steinbruch (steinbruch.py) im Suedwesten, von dort die
    Gueterstrasse ueber einen Bahnuebergang zum Gueterschuppen; die Gleise (Steinbruch -> Bahnhof) liegen auf y = 27 ... 34.
  * Teiche: vier Stueck in Mulden des Gelaendes (siehe umgebung.TEICHE).
  * Jedes Haus steht mit der Tuer zu einer Strasse und ist ueber einen Pfad mit ihr verbunden; Haeuser stehen nie auf Strassen,
    Plaetzen, Teichen oder im Burggelaende und nur auf ebenem Grund (umgebung.STADT_ZONEN). Das Wegenetz ist zusammenhaengend.
Ohne bpy testbar (baue_alles); bauen() legt die Objekte in der Collection "Stadt" an.
"""
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bpy  # noqa: E402,F401
import talkessel as T  # noqa: E402
import burg as B  # noqa: E402
import umgebung as U  # noqa: E402
from burg import Bau  # noqa: E402

C = B.C
Z_STR, Z_PFAD, Z_PLATZ = 0.052, 0.056, 0.064
W_STR, W_PFAD = 6.0, 1.6
PLATZ = (40.0, 135.0, 70.0, 165.0)                       # Marktplatz 30 x 30 m
PLATZ_M = (55.0, 150.0)
DORF_N = (150.0, 250.0)                                  # Mitte des Kreisverkehrs im Norden
KV_R, KV_B = 9.0, 5.0                                    # Kreisverkehr: Mittelradius, Breite
SUED_ENDE = (150.0, 62.0)                                # Suedstrasse endet am Bahnhofsvorplatz
WERK_ABZW = (92.3, 100.0)                                # Abzweig der Werkstrasse von der Spange Sued

FARBEN = {
    "Strasse":       ((0.33, 0.31, 0.28), 0.95, 0.0),
    "Pfad":          ((0.52, 0.46, 0.36), 0.95, 0.0),
    "Pflaster":      ((0.58, 0.55, 0.50), 0.9, 0.0),
    "Putz weiss":    ((0.88, 0.86, 0.80), 0.9, 0.0),
    "Putz gelb":     ((0.86, 0.74, 0.46), 0.9, 0.0),
    "Putz rot":      ((0.70, 0.40, 0.32), 0.9, 0.0),
    "Putz blau":     ((0.52, 0.62, 0.72), 0.9, 0.0),
    "Dach rot":      ((0.55, 0.22, 0.16), 0.8, 0.0),
    "Dach grau":     ((0.30, 0.31, 0.34), 0.8, 0.0),
    "Dach Kupfer":   ((0.30, 0.55, 0.50), 0.6, 0.2),
    "Holz":          ((0.42, 0.29, 0.18), 0.9, 0.0),
    "Stein":         ((0.62, 0.61, 0.58), 0.9, 0.0),
    "Rathaus":       ((0.82, 0.78, 0.68), 0.9, 0.0),
    "Tuer":          ((0.30, 0.20, 0.14), 0.8, 0.0),
    "Fenster":       ((0.07, 0.09, 0.11), 0.2, 0.0),
    "Uhr":           ((0.92, 0.91, 0.86), 0.6, 0.0),
    "Markt rot":     ((0.72, 0.16, 0.12), 0.8, 0.0),
    "Markt weiss":   ((0.92, 0.90, 0.84), 0.8, 0.0),
    "Brunnenwasser": ((0.22, 0.45, 0.62), 0.1, 0.0),
    "Teichwasser":   ((0.16, 0.34, 0.44), 0.1, 0.0),
    "Stamm":         ((0.32, 0.22, 0.14), 0.9, 0.0),
    "Laub":          ((0.18, 0.40, 0.16), 0.9, 0.0),
    "Laub hell":     ((0.30, 0.50, 0.20), 0.9, 0.0),
    "Metall":        ((0.30, 0.32, 0.30), 0.5, 0.0),
    "Putz gruen":    ((0.66, 0.72, 0.58), 0.9, 0.0),
    "Putz grau":     ((0.72, 0.70, 0.66), 0.9, 0.0),
    "Putz sand":     ((0.80, 0.72, 0.58), 0.9, 0.0),
    "Sockel":        ((0.42, 0.40, 0.37), 0.95, 0.0),
    "Rahmen weiss":  ((0.93, 0.92, 0.88), 0.7, 0.0),
    "Laden gruen":   ((0.22, 0.38, 0.26), 0.8, 0.0),
    "Laden braun":   ((0.38, 0.24, 0.16), 0.8, 0.0),
    "Ziegel":        ((0.52, 0.22, 0.15), 0.85, 0.0),
    "Ziegel dunkel": ((0.34, 0.16, 0.12), 0.85, 0.0),
    "Klinker":       ((0.44, 0.21, 0.15), 0.95, 0.0),
    "Innenwand":     ((0.90, 0.88, 0.80), 0.9, 0.0),
    "Dielen":        ((0.50, 0.36, 0.22), 0.8, 0.0),
    "Decke":         ((0.92, 0.91, 0.86), 0.9, 0.0),
    "Holz alt":      ((0.20, 0.14, 0.10), 0.95, 0.0),
    "Tuer gruen":    ((0.20, 0.34, 0.24), 0.8, 0.0),
    "Tuer rot":      ((0.50, 0.14, 0.11), 0.8, 0.0),
    "Tuer blau":     ((0.20, 0.29, 0.44), 0.8, 0.0),
    "Tuer grau":     ((0.40, 0.40, 0.38), 0.8, 0.0),
    "Schmutz":       ((0.27, 0.25, 0.21), 1.0, 0.0),
    "Pappe":         ((0.10, 0.10, 0.11), 1.0, 0.0),
    "Moos":          ((0.24, 0.31, 0.17), 1.0, 0.0),
}


def _verwittert(rgb, hell=0.80, grau=0.30):
    g = sum(rgb) / 3.0
    return tuple(max(0.0, min(1.0, (c * (1 - grau) + g * grau) * hell)) for c in rgb)


for _n in ("Putz weiss", "Putz gelb", "Putz rot", "Putz blau", "Putz gruen", "Putz grau", "Putz sand", "Ziegel", "Ziegel dunkel", "Laden gruen",
           "Laden braun", "Klinker", "Dach grau", "Rahmen weiss", "Stein"):
    FARBEN[_n + " alt"] = (_verwittert(FARBEN[_n][0]), min(1.0, FARBEN[_n][1] + 0.05), 0.0)       # verwitterte Varianten (heruntergekommen)


# ------------------------------------------------------------------ Strassennetz
def strassen():
    """Alle Strassen als (Name, Linienzug nach dem Abrunden, Breite, geschlossen) - gleichzeitig Grundlage fuer Abstandspruefungen.

    'roh' enthaelt die geraden Teilstuecke vor dem Abrunden (fuer die Haeuser)."""
    ringw = U.ring_punkt(math.pi)
    ringn = U.ring_punkt(math.pi / 2)
    rings = U.ring_punkt(-math.pi / 2)
    L = []

    def add(name, roh, r, w=W_STR, geschlossen=False):
        pts = U.rund(roh, r, geschlossen) if r > 0 else [tuple(p) for p in roh]
        L.append({"name": name, "roh": [tuple(p) for p in roh], "pts": pts, "w": w, "zu": geschlossen})

    add("Marktring", ((28, 112), (82, 112), (82, 188), (28, 188)), 8.0, geschlossen=True)
    add("Hauptstrasse", (ringw, (82, 150)), 0.0)
    add("Markt West", ((28, 150), (40, 150)), 0.0)                      # Marktring -> Platz, zwischen den Laeden
    add("Markt Ost", ((82, 150), (70, 150)), 0.0)
    add("Spange Nord", ((82, 178), (96, 208), (150, 226)), 14.0)
    add("Spange Sued", ((82, 122), (96, 92), (150, 74)), 14.0)
    add("Nordstrasse", (ringn, (DORF_N[0], DORF_N[1] - KV_R)), 0.0)
    add("Suedstrasse", (rings, SUED_ENDE), 0.0)
    add("Werkstrasse", (WERK_ABZW, (88.0, 58.0)), 0.0)                    # Spange Sued -> Steinbruch (Einfahrt am Tor)
    add("Gueterstrasse", ((88.0, 58.0), (98.0, 44.0), (108.0, 38.0), (108.0, 12.0), (126.0, 12.0)), 8.0)   # Hof -> Bahnuebergang -> Gueterschuppen
    cx, cy = DORF_N
    kreis = [(cx + KV_R * math.cos(2 * math.pi * k / 24), cy + KV_R * math.sin(2 * math.pi * k / 24)) for k in range(24)]
    L.append({"name": "Kreisverkehr Nord", "roh": kreis, "pts": kreis, "w": KV_B, "zu": True})
    return L


def _polylinie_abstand(x, y, pts, geschlossen):
    m = len(pts)
    best = 1e9
    for i in range(m if geschlossen else m - 1):
        p, q = pts[i], pts[(i + 1) % m]
        dx, dy = q[0] - p[0], q[1] - p[1]
        l2 = dx * dx + dy * dy
        t = 0.0 if l2 == 0 else max(0.0, min(1.0, ((x - p[0]) * dx + (y - p[1]) * dy) / l2))
        best = min(best, math.hypot(x - p[0] - t * dx, y - p[1] - t * dy))
    return best


def strassenabstand(x, y, strs, ohne=None):
    """Kleinster Abstand von (x, y) zur Strassenkante (Mittellinienabstand minus halbe Breite); auch der Ringweg zaehlt."""
    best = 1e9
    for s in strs:
        if s is ohne:
            continue
        best = min(best, _polylinie_abstand(x, y, s["pts"], s["zu"]) - s["w"] / 2)
    a = math.atan2(y - C, x - C)
    best = min(best, abs(math.hypot(x - C, y - C) - U.ring_r(a)) - U.BREITE_WEG / 2)
    return best


# ------------------------------------------------------------------ lokaler Bauplatz (Drehung und Verschiebung)
class Lok:
    """Wie Bau.box/add, aber in lokalen Koordinaten (Haus um (0,0), Tuer auf der -y-Seite) mit Drehung theta und Fusshoehe zb."""

    def __init__(self, b, cx, cy, zb, theta, sx=1):
        self.b, self.cx, self.cy, self.zb = b, cx, cy, zb
        self.c, self.s = math.cos(theta), math.sin(theta)
        self.sx = sx                                   # -1: Haus an der lokalen x-Achse gespiegelt (Tuer links statt rechts)

    def P(self, p):
        return (self.cx + p[0] * self.c - p[1] * self.s, self.cy + p[0] * self.s + p[1] * self.c, self.zb + p[2])

    def box(self, x0, y0, z0, x1, y1, z1, mat):
        x0, x1 = x0 * self.sx, x1 * self.sx
        x0, x1, y0, y1, z0, z1 = min(x0, x1), max(x0, x1), min(y0, y1), max(y0, y1), min(z0, z1), max(z0, z1)
        if x1 - x0 < 1e-6 or y1 - y0 < 1e-6 or z1 - z0 < 1e-6:
            return
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0), (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        w = [self.P(p) for p in v]
        self.b.add(w, B.BOX_FACES, mat)
        self.b.bx.append((min(p[0] for p in w), min(p[1] for p in w), min(p[2] for p in w),
                          max(p[0] for p in w), max(p[1] for p in w), max(p[2] for p in w)))

    def poly(self, verts, richtung, mat):
        """Vieleck (lokal) mit Normale in 'richtung' (lokal)."""
        verts = [(p[0] * self.sx, p[1], p[2]) for p in verts]
        richtung = (richtung[0] * self.sx, richtung[1], richtung[2])
        n = [0.0, 0.0, 0.0]
        for k in range(len(verts)):
            a, c = verts[k], verts[(k + 1) % len(verts)]
            n[0] += (a[1] - c[1]) * (a[2] + c[2]); n[1] += (a[2] - c[2]) * (a[0] + c[0]); n[2] += (a[0] - c[0]) * (a[1] + c[1])
        if n[0] * richtung[0] + n[1] * richtung[1] + n[2] * richtung[2] < 0:
            verts = verts[::-1]
        self.b.add([self.P(p) for p in verts], [tuple(range(len(verts)))], mat)

    def prism(self, x, y, z0, r, h, n, mat):
        px, py, _ = self.P((x * self.sx, y, 0.0))
        self.b.prism(px, py, self.zb + z0, r, h, n, mat)


# ------------------------------------------------------------------ Gebaeude
def satteldach(g, w, d, h, rh, mat_dach, mat_giebel, ueber=0.4):
    g = altbau.DachLok(g, mat_dach)
    """Satteldach mit First in x-Richtung ueber dem Grundriss w x d (Traufe auf Hoehe h, First h + rh)."""
    x0, x1, y0, y1 = -w / 2 - ueber, w / 2 + ueber, -d / 2 - ueber, d / 2 + ueber
    g.poly([(x0, y0, h), (x1, y0, h), (x1, 0.0, h + rh), (x0, 0.0, h + rh)], (0.0, -rh, d / 2), mat_dach)
    g.poly([(x0, y1, h), (x0, 0.0, h + rh), (x1, 0.0, h + rh), (x1, y1, h)], (0.0, rh, d / 2), mat_dach)
    g.poly([(x0, y0, h), (x0, y1, h), (x1, y1, h), (x1, y0, h)], (0.0, 0.0, -1.0), mat_dach)             # Unterseite
    for sx in (-1, 1):
        g.poly([(sx * w / 2, -d / 2, h), (sx * w / 2, d / 2, h), (sx * w / 2, 0.0, h + rh)], (sx, 0.0, 0.0), mat_giebel)


def fenster_l(g, x, y, nx, ny, zc, w=0.9, h=1.2):
    """Fensterflaeche (flacher dunkler Quader) auf einer Wand bei (x, y) mit Wandnormale (nx, ny)."""
    if nx:
        g.box(x, y - w / 2, zc - h / 2, x + nx * 0.05, y + w / 2, zc + h / 2, "Fenster")
    else:
        g.box(x - w / 2, y, zc - h / 2, x + w / 2, y + ny * 0.05, zc + h / 2, "Fenster")


F0, F1 = 0.2, 3.25                    # Fussbodenhoehe Erdgeschoss / Obergeschoss (ueber der Fusshoehe zb)
WD = 0.30                             # Aussenwandstaerke (0,24 Putz + 0,06 Innenputz)
TH = 2.2                              # Tuerhoehe


def pbox(g, ach, a0, a1, p0, p1, z0, z1, mat):
    """Quader mit Laengsachse ach ('x' oder 'y'): a = Koordinate laengs, p = quer dazu. Leere/negative Quader werden uebersprungen."""
    if z1 - z0 < 1e-4 or a1 - a0 < 1e-4:
        return
    if ach == "x":
        g.box(a0, p0, z0, a1, p1, z1, mat)
    else:
        g.box(p0, a0, z0, p1, a1, z1, mat)


def wand(g, ach, p0, p1, a0, a1, z0, z1, mat, oeff=()):
    """Wandstueck (Dicke p0..p1) von a0 bis a1 und z0..z1, ausgespart um die Oeffnungen (alo, ahi, zlo, zhi)."""
    pts = sorted({a0, a1} | {x for o in oeff for x in (o[0], o[1]) if a0 < x < a1})
    for lo, hi in zip(pts, pts[1:]):
        cuts = sorted((min(max(o[2], z0), z1), max(min(o[3], z1), z0)) for o in oeff if o[0] <= lo + 1e-9 and o[1] >= hi - 1e-9)
        z = z0
        for c0, c1 in cuts:
            pbox(g, ach, lo, hi, p0, p1, z, max(z, c0), mat)
            z = max(z, c1)
        pbox(g, ach, lo, hi, p0, p1, z, z1, mat)


def aussenwand(g, ach, aussen, sg, a0, a1, z1, mat, oeff, sockel=True):
    """Aussenwand: Kern + Innenputz + Sockelvorsatz; aussen = Koordinate der Aussenflaeche, sg = Richtung nach aussen (+-1)."""
    for (o0, o1, m, zl, zh) in ((-0.24, 0.0, mat, -1.0, z1), (-WD, -0.24, "Innenwand", -1.0, z1)):
        p0, p1 = sorted((aussen + sg * o0, aussen + sg * o1))
        wand(g, ach, p0, p1, a0, a1, zl, zh, m, oeff)
    if sockel:
        altbau.sockel(g, ach, aussen, sg, a0, a1, oeff)
    altbau.putz_flecken(g, ach, aussen, sg, a0, a1, z1, mat, oeff)


def _lok(ach, aussen, sg, a, o, z):
    """(Laengskoordinate a, Abstand o nach aussen, Hoehe z) einer Wand -> lokale Hausposition."""
    p = aussen + sg * o
    return (a, p, z) if ach == "x" else (p, a, z)


def fensterschmuck(g, ach, aussen, sg, ac, zc, w, h, laden, zustand="ok", lz=("ok", "ok")):
    """Fenster in einer Aussenwand: Scheibe mit Sprossenkreuz, Rahmen, Fensterbank, Fensterlaeden.

    zustand: 'ok' | 'kaputt' (Scheibe nur unten) | 'bretter' (zugenagelt); lz = Zustand (links, rechts) der Laeden: 'ok' | 'fehlt' | 'schief'."""
    def pb(a0, a1, o0, o1, z0, z1, m):
        p0, p1 = sorted((aussen + sg * o0, aussen + sg * o1))
        pbox(g, ach, a0, a1, p0, p1, z0, z1, m)
    zl, zh, al, ah, t = zc - h / 2, zc + h / 2, ac - w / 2, ac + w / 2, 0.09
    ztop = zh if zustand != "kaputt" else zl + 0.45 * h
    pb(al, ah, -0.17, -0.13, zl, ztop, "Fenster")
    pb(ac - 0.025, ac + 0.025, -0.19, -0.11, zl, zh, "Rahmen weiss alt" if "Rahmen weiss alt" in FARBEN else "Rahmen weiss")
    pb(al, ah, -0.19, -0.11, zc + h / 6 - 0.025, zc + h / 6 + 0.025, "Rahmen weiss")
    pb(al - t, al, 0.0, 0.05, zl - t, zh + t, "Rahmen weiss")
    pb(ah, ah + t, 0.0, 0.05, zl - t, zh + t, "Rahmen weiss")
    pb(al, ah, 0.0, 0.05, zh, zh + t, "Rahmen weiss")
    pb(al, ah, 0.0, 0.05, zl - t, zl, "Rahmen weiss")
    pb(al - 0.12, ah + 0.12, 0.0, 0.15, zl - t - 0.06, zl - t, "Stein")
    altbau.fenster_zierde(g, ach, aussen, sg, ac, zc, w, h)
    if zustand == "bretter":                                                            # zugenagelt: drei Bretter quer
        for k, zz in enumerate((zl + 0.1, zc - 0.1, zh - 0.35)):
            da = 0.12 * (k - 1)
            pb(al - 0.15 + da, ah + 0.15 - 0.1 * (k % 2), 0.05, 0.09, zz, zz + 0.2, "Holz alt")
    if laden:
        for k, (lo, hi) in enumerate(((al - t - 0.52, al - t - 0.02), (ah + t + 0.02, ah + t + 0.52))):
            if lz[k] == "ok":
                pb(lo, hi, 0.0, 0.05, zl - t, zh + t, laden)
                for j in range(1, 6):                                                   # Lamellen
                    zz = zl - t + j * (zh - zl + 2 * t) / 6
                    pb(lo + 0.03, hi - 0.03, 0.05, 0.07, zz - 0.02, zz + 0.02, laden)
            elif lz[k] == "schief":                                                     # haengt an einem Scharnier schief nach aussen
                for sgn in (1, -1):
                    pts = [_lok(ach, aussen, sg, lo, 0.06, zh + t), _lok(ach, aussen, sg, hi, 0.06, zh + t),
                           _lok(ach, aussen, sg, hi, 0.5, zl + 0.15), _lok(ach, aussen, sg, lo, 0.5, zl + 0.15)]
                    rv = (0.0, sg * 0.9 * sgn, 0.49 * sgn) if ach == "x" else (sg * 0.9 * sgn, 0.0, 0.49 * sgn)
                    g.poly(pts, rv, laden)


def tuerrahmen(g, ach, p0, p1, a_lo, a_hi, z0, z1, mat="Rahmen weiss", t=0.07, v=0.03):
    """Rahmen einer Tuer/Durchgangs (Pfosten + Sturz) um die Oeffnung, ueberlappt die Wand beidseitig um v."""
    pbox(g, ach, a_lo - t, a_lo, p0 - v, p1 + v, z0, z1 + t, mat)
    pbox(g, ach, a_hi, a_hi + t, p0 - v, p1 + v, z0, z1 + t, mat)
    pbox(g, ach, a_lo, a_hi, p0 - v, p1 + v, z1, z1 + t, mat)


def gaube(g, ax, H, rh, d, wand_m, dach_m):
    """Dachgaube (Schleppgaube mit kleinem Giebel) auf der vorderen (-y) Dachseite bei x = ax."""
    sl = rh / (d / 2.0)
    yf = -d / 2 + 1.0
    zf = H + sl * 1.0
    bw = 0.8
    g.box(ax - bw, yf, zf - 0.35, ax + bw, yf + 0.18, zf + 1.3, wand_m)
    g.box(ax - 0.4, yf - 0.04, zf + 0.15, ax + 0.4, yf, zf + 1.05, "Fenster")
    g.box(ax - 0.025, yf - 0.06, zf + 0.15, ax + 0.025, yf - 0.02, zf + 1.05, "Rahmen weiss")
    g.box(ax - 0.4, yf - 0.06, zf + 0.58, ax + 0.4, yf - 0.02, zf + 0.64, "Rahmen weiss")
    for sgn in (-1, 1):
        g.box(ax + sgn * 0.4 - (0.07 if sgn > 0 else 0), yf - 0.06, zf + 0.1, ax + sgn * 0.4 + (0.0 if sgn > 0 else 0.07), yf - 0.02, zf + 1.1, "Rahmen weiss")
    ys = 1.11                                                     # Traufe der Gaube trifft hier auf die Dachflaeche
    yr = 1.6                                                      # First trifft hier auf die Dachflaeche
    zr = lambda yy: zf + sl * yy
    A = (ax - bw - 0.12, yf - 0.15, zf + 1.3); B = (ax + bw + 0.12, yf - 0.15, zf + 1.3); Cp = (ax, yf - 0.15, zf + 1.85)
    E1 = (ax - bw - 0.12, yf + ys, zr(ys)); E2 = (ax + bw + 0.12, yf + ys, zr(ys)); R = (ax, yf + yr, zr(yr))
    g.poly([A, Cp, R, E1], (-1.0, 0.2, 1.0), dach_m)
    g.poly([B, E2, R, Cp], (1.0, 0.2, 1.0), dach_m)
    g.poly([A, B, Cp], (0.0, -1.0, 0.0), wand_m)
    for sgn in (-1, 1):
        xx = ax + sgn * bw
        g.poly([(xx, yf, zf), (xx, yf, zf + 1.3), (xx, yf + ys, zr(ys))], (sgn, 0.0, 0.0), wand_m)


def dach(g, form, w, d, H, rh, dm, gm, e=0.45):
    """Siehe _dach_roh; zusaetzlich Ziegel-/Schieferbelag auf allen Dachflaechen und Sparrenkoepfe (altbau.py)."""
    rz = _dach_roh(altbau.DachLok(g, dm), form, w, d, H, rh, dm, gm, e)
    altbau.sparren(g, form, w, d, H, rh, e)
    return rz


def _dach_roh(g, form, w, d, H, rh, dm, gm, e=0.45):
    """Dach ueber dem Grundriss w x d (Traufe auf Hoehe H, Ueberstand e). form: 'x' Satteldach (First laengs, Traufe zur Strasse),
    'y' Satteldach (Giebel zur Strasse), 'walm' Walmdach, 'mansard' Mansarddach, 'pult' Pultdach. Rueckgabe: Dachhoehe z(x, y) (zum Aufsetzen von Kamin, Flicken)."""
    hw, hd = w / 2.0, d / 2.0
    ZB = "Rahmen weiss"

    def unterseite(zu):
        g.poly([(-hw - e, -hd - e, zu), (-hw - e, hd + e, zu), (hw + e, hd + e, zu), (hw + e, -hd - e, zu)], (0.0, 0.0, -1.0), dm)

    if form == "x":
        s = rh / hd
        zE = H - s * e
        g.poly([(-hw - e, -hd - e, zE), (hw + e, -hd - e, zE), (hw + e, 0.0, H + rh), (-hw - e, 0.0, H + rh)], (0.0, -s, 1.0), dm)
        g.poly([(-hw - e, hd + e, zE), (-hw - e, 0.0, H + rh), (hw + e, 0.0, H + rh), (hw + e, hd + e, zE)], (0.0, s, 1.0), dm)
        unterseite(zE)
        for sx in (-1, 1):
            g.poly([(sx * hw, -hd, H), (sx * hw, hd, H), (sx * hw, 0.0, H + rh)], (sx, 0.0, 0.0), gm)
            g.poly([(sx * (hw + e), -hd - e, zE), (sx * (hw + e), hd + e, zE), (sx * (hw + e), 0.0, H + rh)], (sx, 0.0, 0.0), dm)
        for sy in (-1, 1):
            g.box(-hw - e, sy * (hd + e) - (0.05 if sy > 0 else 0.0), zE - 0.22, hw + e, sy * (hd + e) + (0.0 if sy > 0 else 0.05), zE + 0.02, ZB)
        g.box(-hw - e, -0.1, H + rh - 0.02, hw + e, 0.1, H + rh + 0.1, "Ziegel dunkel")
        return lambda x, y: H + rh * max(0.0, 1 - abs(y) / hd)
    if form == "y":
        s = rh / hw
        zE = H - s * e
        g.poly([(-hw - e, -hd - e, zE), (-hw - e, hd + e, zE), (0.0, hd + e, H + rh), (0.0, -hd - e, H + rh)], (-s, 0.0, 1.0), dm)
        g.poly([(hw + e, -hd - e, zE), (0.0, -hd - e, H + rh), (0.0, hd + e, H + rh), (hw + e, hd + e, zE)], (s, 0.0, 1.0), dm)
        unterseite(zE)
        for sy in (-1, 1):
            g.poly([(-hw, sy * hd, H), (hw, sy * hd, H), (0.0, sy * hd, H + rh)], (0.0, sy, 0.0), gm)
            g.poly([(-hw - e, sy * (hd + e), zE), (hw + e, sy * (hd + e), zE), (0.0, sy * (hd + e), H + rh)], (0.0, sy, 0.0), dm)
        for sx in (-1, 1):
            g.box(sx * (hw + e) - (0.05 if sx > 0 else 0.0), -hd - e, zE - 0.22, sx * (hw + e) + (0.0 if sx > 0 else 0.05), hd + e, zE + 0.02, ZB)
        g.box(-0.1, -hd - e, H + rh - 0.02, 0.1, hd + e, H + rh + 0.1, "Ziegel dunkel")
        return lambda x, y: H + rh * max(0.0, 1 - abs(x) / hw)
    if form == "walm":
        L = max(0.0, (w - d) / 2.0)
        s = rh / hd
        zE = H - s * e
        g.poly([(-hw - e, -hd - e, zE), (hw + e, -hd - e, zE), (L, 0.0, H + rh), (-L, 0.0, H + rh)], (0.0, -s, 1.0), dm)
        g.poly([(-hw - e, hd + e, zE), (-L, 0.0, H + rh), (L, 0.0, H + rh), (hw + e, hd + e, zE)], (0.0, s, 1.0), dm)
        g.poly([(hw + e, -hd - e, zE), (hw + e, hd + e, zE), (L, 0.0, H + rh)], (s, 0.0, 1.0), dm)
        g.poly([(-hw - e, -hd - e, zE), (-L, 0.0, H + rh), (-hw - e, hd + e, zE)], (-s, 0.0, 1.0), dm)
        unterseite(zE)
        for sy in (-1, 1):
            g.box(-hw - e, sy * (hd + e) - (0.05 if sy > 0 else 0.0), zE - 0.22, hw + e, sy * (hd + e) + (0.0 if sy > 0 else 0.05), zE + 0.02, ZB)
        if L > 0.15:
            g.box(-L, -0.1, H + rh - 0.02, L, 0.1, H + rh + 0.1, "Ziegel dunkel")
        return lambda x, y: H + rh * max(0.0, 1 - max(abs(y), abs(x) - L) / hd)
    if form == "mansard":
        kb = 1.3                                              # Breite des Steilteils
        zb_ = 2.3                                             # Hoehe des Knicks ueber der Traufe
        ss = zb_ / kb
        s2 = (rh - zb_) / (hd - kb)
        zE = H - ss * e
        for sy in (-1, 1):
            g.poly([(-hw - e, sy * (hd + e), zE), (hw + e, sy * (hd + e), zE), (hw + e, sy * (hd - kb), H + zb_), (-hw - e, sy * (hd - kb), H + zb_)], (0.0, sy * ss, 1.0), dm)
            g.poly([(-hw - e, sy * (hd - kb), H + zb_), (hw + e, sy * (hd - kb), H + zb_), (hw + e, 0.0, H + rh), (-hw - e, 0.0, H + rh)], (0.0, sy * s2, 1.0), dm)
            g.box(-hw - e, sy * (hd + e) - (0.05 if sy > 0 else 0.0), zE - 0.22, hw + e, sy * (hd + e) + (0.0 if sy > 0 else 0.05), zE + 0.02, ZB)
        unterseite(zE)
        for sx in (-1, 1):
            g.poly([(sx * hw, -hd, H), (sx * hw, hd, H), (sx * hw, hd - kb, H + zb_), (sx * hw, 0.0, H + rh), (sx * hw, -(hd - kb), H + zb_)], (sx, 0.0, 0.0), gm)
            g.poly([(sx * (hw + e), -hd - e, zE), (sx * (hw + e), hd + e, zE), (sx * (hw + e), hd - kb, H + zb_), (sx * (hw + e), 0.0, H + rh),
                    (sx * (hw + e), -(hd - kb), H + zb_)], (sx, 0.0, 0.0), dm)
        g.box(-hw - e, -0.1, H + rh - 0.02, hw + e, 0.1, H + rh + 0.1, "Ziegel dunkel")

        def rz(x, y):
            a = abs(y)
            return H + ss * (hd - a) if a >= hd - kb else H + zb_ + s2 * (hd - kb - a)
        return rz
    # Pultdach: steigt von der Strasse (vorn) nach hinten
    s = rh / d
    zf, zh_ = H - s * e, H + rh + s * e
    g.poly([(-hw - e, -hd - e, zf), (hw + e, -hd - e, zf), (hw + e, hd + e, zh_), (-hw - e, hd + e, zh_)], (0.0, -s, 1.0), dm)
    g.poly([(-hw - e, -hd - e, zf), (-hw - e, hd + e, zf), (hw + e, hd + e, zf), (hw + e, -hd - e, zf)], (0.0, 0.0, -1.0), dm)
    g.poly([(-hw - e, hd + e, zf), (hw + e, hd + e, zf), (hw + e, hd + e, zh_), (-hw - e, hd + e, zh_)], (0.0, 1.0, 0.0), dm)
    g.box(-hw, hd - 0.25, H, hw, hd, H + rh, gm)
    for sx in (-1, 1):
        g.poly([(sx * hw, -hd, H), (sx * hw, hd, H), (sx * hw, hd, H + rh)], (sx, 0.0, 0.0), gm)
        g.poly([(sx * (hw + e), -hd - e, zf), (sx * (hw + e), hd + e, zf), (sx * (hw + e), hd + e, zh_)], (sx, 0.0, 0.0), dm)
    g.box(-hw - e, -hd - e, zf - 0.2, hw + e, -hd - e + 0.05, zf + 0.02, ZB)
    return lambda x, y: H + rh * (y + hd) / d


def fachwerk(g, wd, H, stock, holz="Holz alt"):
    """Sichtbares Fachwerk auf einer Aussenwand wd = (ach, aussen, sg, a0, a1, oeff): Schwelle, Geschossbalken, Rahmen, Staender, Streben
    in den Eckfeldern; alles wird um die Fenster/Tuer ausgespart."""
    ach, aussen, sg, a0, a1, oeff = wd
    lo_e, hi_e = (a0, a1) if ach == "x" else (a0 - WD, a1 + WD)

    def pb(aa0, aa1, z0, z1):
        p0, p1 = sorted((aussen, aussen + sg * 0.07))
        wand(g, ach, p0, p1, aa0, aa1, z0, z1, holz, oeff)
    rails = [(0.6, 0.8)] + ([(F1 - 0.2, F1 + 0.05)] if stock == 2 else []) + [(H - 0.2, H)]
    for z0, z1 in rails:
        pb(lo_e, hi_e, z0, z1)
    zones = [(rails[k][1], rails[k + 1][0]) for k in range(len(rails) - 1)]
    n = max(2, int(round((hi_e - lo_e) / 1.55)))
    pos = [lo_e + (hi_e - lo_e) * k / n for k in range(n + 1)]
    for k, a in enumerate(pos):
        if k == 0:
            xa, xb = lo_e, lo_e + 0.2
        elif k == n:
            xa, xb = hi_e - 0.2, hi_e
        else:
            xa, xb = a - 0.06, a + 0.06
        for z0, z1 in zones:
            pb(xa, xb, z0, z1)
    # Streben in den beiden Eckfeldern jedes Geschosses (fallen zum Eckpfosten), nur wenn das Feld fensterfrei ist
    for (pa, pbb, ecke) in ((pos[0] + 0.2, pos[1] - 0.06, -1), (pos[-2] + 0.06, pos[-1] - 0.2, 1)):
        for z0, z1 in zones:
            if any(o[0] < pbb and o[1] > pa and o[2] < z1 and o[3] > z0 for o in oeff):
                continue
            za, zb2 = z0 + 0.12, z1 - 0.12
            if ecke < 0:
                a_lo, a_hi = pa + 0.0, pbb
                pts = [(a_lo, za), (a_lo + 0.14, za), (a_hi, zb2), (a_hi - 0.14, zb2)]
            else:
                a_lo, a_hi = pa, pbb
                pts = [(a_hi, za), (a_hi - 0.14, za), (a_lo, zb2), (a_lo + 0.14, zb2)]
            P = [_lok(ach, aussen, sg, a, 0.075, z) for a, z in pts]
            rv = (0.0, sg, 0.0) if ach == "x" else (sg, 0.0, 0.0)
            g.poly(P, rv, holz)


def verfall_aussen(g, waende, H, rnd, lvl):
    """Verfall der Fassade: Schmutzband am Sockel, abgeplatzter Putz (Ziegel scheint durch), Regenstreifen."""
    for (ach, aussen, sg, a0, a1, oeff) in waende:
        lo_e, hi_e = (a0, a1) if ach == "x" else (a0 - WD, a1 + WD)
        p0, p1 = sorted((aussen, aussen + sg * 0.012))
        wand(g, ach, p0, p1, lo_e, hi_e, 0.6, 1.2 + 0.4 * (lvl - 1), "Schmutz", oeff)
    for _ in range(2 + 4 * (lvl - 1) + rnd.randint(0, 2)):
        ach, aussen, sg, a0, a1, oeff = waende[rnd.randrange(len(waende))]
        bw_, bh_ = rnd.uniform(0.5, 1.3), rnd.uniform(0.4, 1.0)
        ac = rnd.uniform(a0 + 0.4 + bw_ / 2, a1 - 0.4 - bw_ / 2) if a1 - a0 > bw_ + 1.0 else (a0 + a1) / 2
        zc = rnd.uniform(1.3, H - 1.0)
        if any(o[0] - 0.2 < ac + bw_ / 2 and o[1] + 0.2 > ac - bw_ / 2 and o[2] - 0.2 < zc + bh_ / 2 and o[3] + 0.2 > zc - bh_ / 2 for o in oeff):
            continue
        p0, p1 = sorted((aussen + sg * 0.012, aussen + sg * 0.03))
        pbox(g, ach, ac - bw_ / 2, ac + bw_ / 2, p0, p1, zc - bh_ / 2, zc + bh_ / 2, "Klinker alt")
    for _ in range(1 + lvl):                                       # Regenstreifen unter der Traufe
        ach, aussen, sg, a0, a1, oeff = waende[rnd.randrange(len(waende))]
        ac = rnd.uniform(a0 + 0.5, a1 - 0.5)
        zl = rnd.uniform(2.6, 3.6)
        if any(o[0] - 0.1 < ac + 0.1 and o[1] + 0.1 > ac - 0.1 and o[2] < H and o[3] > zl for o in oeff):
            continue
        p0, p1 = sorted((aussen + sg * 0.012, aussen + sg * 0.02))
        pbox(g, ach, ac - 0.15, ac + 0.15, p0, p1, zl, H - 0.25, "Schmutz")


def verfall_dach(g, form, rz, w, d, H, rnd, lvl):
    """Flicken aus Dachpappe und Moos auf ebenen Dachflaechen (nur dort, wo z(x, y) tatsaechlich eine Ebene ist)."""
    hw, hd = w / 2.0, d / 2.0
    n = 2 + 3 * (lvl - 1) + rnd.randint(0, 2)
    for _ in range(n):
        bw_, bh_ = rnd.uniform(0.8, 1.8), rnd.uniform(0.7, 1.5)
        mat = rnd.choice(("Pappe", "Pappe", "Moos"))
        if form in ("x", "walm"):
            L = max(0.0, (w - d) / 2.0)
            sy = rnd.choice((-1, 1))
            y0 = rnd.uniform(0.5, hd - 0.7 - bh_)
            xm = (L + y0) - 0.4 - bw_
            if xm < 0.3:
                continue
            x0 = rnd.uniform(-xm, xm)
            pts = [(x0, sy * y0), (x0 + bw_, sy * y0), (x0 + bw_, sy * (y0 + bh_)), (x0, sy * (y0 + bh_))]
        elif form == "y":
            sx = rnd.choice((-1, 1))
            x0 = rnd.uniform(0.5, hw - 0.7 - bw_)
            y0 = rnd.uniform(-hd + 0.7, hd - 0.7 - bh_)
            pts = [(sx * x0, y0), (sx * (x0 + bw_), y0), (sx * (x0 + bw_), y0 + bh_), (sx * x0, y0 + bh_)]
        elif form == "pult":
            x0 = rnd.uniform(-hw + 0.6, hw - 0.6 - bw_)
            y0 = rnd.uniform(-hd + 0.6, hd - 0.6 - bh_)
            pts = [(x0, y0), (x0 + bw_, y0), (x0 + bw_, y0 + bh_), (x0, y0 + bh_)]
        else:
            continue
        P = [(x, y, rz(x, y) + 0.11) for x, y in pts]
        g.poly(P, (0.0, 0.0, 1.0), mat)


VORBAU = {"vordach": 0.95, "vordach_giebel": 1.2, "windfang": 2.3, "veranda": 2.4, "portal": 1.0, "schlicht": 0.7, "rundbogen": 1.0}


def eingang(g, art, tx, d, mat, lvl, tuerm="Tuer"):
    """Haustuer-Vorbau auf der lokalen -y-Seite bei x = tx (Tuerbreite 1,1 m). Arten: vordach (flaches Vordach auf Pfosten), vordach_giebel
    (kleines Satteldach auf Konsolen), windfang (geschlossener Vorbau mit Fenstern), veranda (offene Holzveranda mit Gelaender),
    portal (Pilaster mit Gebaelk und Dreiecksgiebel), schlicht (nur Stufe und Laterne), rundbogen (Rundbogenblende ueber der Tuer)."""
    y0 = -d / 2
    t0, t1 = tx - 0.55, tx + 0.55
    st, rw = ("Stein alt" if lvl else "Stein"), ("Rahmen weiss alt" if lvl else "Rahmen weiss")
    dm = "Dach grau alt" if lvl else "Dach grau"
    if art == "vordach":
        g.box(t0 - 0.25, y0 - 0.95, -0.6, t1 + 0.25, y0 - 0.5, 0.1, st)
        g.box(t0 - 0.25, y0 - 0.5, -0.6, t1 + 0.25, y0 - 0.07, F0, st)
        g.box(t0 - 0.55, y0 - 1.15, 2.75, t1 + 0.55, y0 - 0.07, 2.87, dm)
        for xx in (t0 - 0.5, t1 + 0.5):
            g.box(xx - 0.06, y0 - 1.1, -0.6, xx + 0.06, y0 - 1.0, 2.75, rw)
    elif art == "vordach_giebel":
        g.box(t0 - 0.3, y0 - 1.2, -0.6, t1 + 0.3, y0 - 0.6, 0.1, st)
        g.box(t0 - 0.3, y0 - 0.6, -0.6, t1 + 0.3, y0 - 0.07, F0, st)
        for sx in (-1, 1):                                                   # Konsolen und Dachflaeche des Giebelvordachs
            xx = tx + sx * 0.85
            g.box(xx - 0.05, y0 - 1.0, 2.2, xx + 0.05, y0 - 0.07, 2.3, "Holz alt")
            g.box(xx - 0.04, y0 - 0.95, 2.3, xx + 0.04, y0 - 0.9, 2.75, "Holz alt")
        zs, zf = 2.75, 3.35
        g.poly([(tx - 1.05, y0 - 1.2, zs), (tx + 1.05, y0 - 1.2, zs), (tx + 1.05, y0 - 0.07, zf), (tx - 1.05, y0 - 0.07, zf)], (0.0, -0.5, 1.0), dm)
        g.poly([(tx - 1.05, y0 - 1.2, zs), (tx - 1.05, y0 - 0.07, zf), (tx + 1.05, y0 - 0.07, zf), (tx + 1.05, y0 - 1.2, zs)], (0.0, 0.5, -1.0), dm)
    elif art == "windfang":
        wo = 1.05                                                            # halbe Aussenbreite
        yf = y0 - 1.5
        g.box(tx - wo, yf, -0.6, tx + wo, y0, F0, st)                         # Boden
        for sx in (-1, 1):                                                   # Seitenwaende mit kleinem Fenster
            xa, xb = (tx - wo, tx - wo + 0.2) if sx < 0 else (tx + wo - 0.2, tx + wo)
            wand(g, "y", xa, xb, yf, y0, -0.6, 2.55, mat, [(yf + 0.45, yf + 1.15, 1.1, 1.9)])
            g.box(xa - 0.02 if sx < 0 else xa + 0.08, yf + 0.45, 1.1, xb - 0.08 if sx < 0 else xb + 0.02, yf + 1.15, 1.9, "Fenster")
        wand(g, "x", yf, yf + 0.2, tx - wo, tx + wo, -0.6, 2.55, mat, [(t0 + 0.05, t1 - 0.05, F0, F0 + 2.1)])           # Vorderwand mit Tuer
        tuerrahmen(g, "x", yf, yf + 0.2, t0 + 0.05, t1 - 0.05, F0, F0 + 2.1)
        g.box(tx - wo - 0.15, yf - 0.1, 2.55, tx + wo + 0.15, y0, 2.7, dm)
        g.box(tx - wo, yf - 0.55, -0.6, tx + wo, yf, 0.1, st)                 # Stufe
    elif art == "veranda":
        wv, dv = 1.9, 1.9
        g.box(tx - wv, y0 - dv, -0.6, tx + wv, y0, F0, "Holz alt")             # Holzboden
        for xx in (tx - wv + 0.08, tx + wv - 0.08):
            for yy in (y0 - dv + 0.08, y0 - 0.2):
                g.box(xx - 0.07, yy - 0.07, -0.6, xx + 0.07, yy + 0.07, 2.75, rw)
        g.box(tx - wv - 0.15, y0 - dv - 0.15, 2.75, tx + wv + 0.15, y0, 2.87, dm)
        for (xa, ya, xb, yb) in ((tx - wv, y0 - dv + 0.08, tx - wv + 0.16, y0 - 0.2), (tx + wv - 0.16, y0 - dv + 0.08, tx + wv, y0 - 0.2),
                                 (tx - wv + 0.08, y0 - dv, tx - 0.85, y0 - dv + 0.16), (tx + 0.85, y0 - dv, tx + wv - 0.08, y0 - dv + 0.16)):
            g.box(xa, ya, F0 + 0.9, xb, yb, F0 + 0.96, rw)                     # Handlauf
            g.box(xa, ya, F0 + 0.45, xb, yb, F0 + 0.5, rw)
        g.box(tx - 0.85, y0 - dv - 0.5, -0.6, tx + 0.85, y0 - dv, 0.1, st)     # Stufe
    elif art == "portal":
        g.box(t0 - 0.5, y0 - 1.0, -0.6, t1 + 0.5, y0 - 0.5, 0.1, st)
        g.box(t0 - 0.5, y0 - 0.5, -0.6, t1 + 0.5, y0 - 0.07, F0, st)
        for xx in (t0 - 0.45, t1 + 0.15):                                     # Pilaster
            g.box(xx, y0 - 0.3, F0, xx + 0.3, y0, 2.9, rw)
            g.box(xx - 0.05, y0 - 0.34, F0, xx + 0.35, y0, F0 + 0.25, st)
            g.box(xx - 0.05, y0 - 0.34, 2.75, xx + 0.35, y0, 2.9, st)
        g.box(t0 - 0.6, y0 - 0.38, 2.9, t1 + 0.6, y0, 3.15, rw)               # Gebaelk
        g.poly([(t0 - 0.6, y0 - 0.38, 3.15), (t1 + 0.6, y0 - 0.38, 3.15), (tx, y0 - 0.38, 3.65)], (0.0, -1.0, 0.0), rw)
        g.poly([(t0 - 0.6, y0 - 0.38, 3.15), (tx, y0 - 0.38, 3.65), (tx, y0, 3.65), (t0 - 0.6, y0, 3.15)], (-0.5, 0.0, 1.0), dm)
        g.poly([(t1 + 0.6, y0 - 0.38, 3.15), (t1 + 0.6, y0, 3.15), (tx, y0, 3.65), (tx, y0 - 0.38, 3.65)], (0.5, 0.0, 1.0), dm)
    elif art == "rundbogen":
        g.box(t0 - 0.25, y0 - 1.0, -0.6, t1 + 0.25, y0 - 0.5, 0.1, st)
        g.box(t0 - 0.25, y0 - 0.5, -0.6, t1 + 0.25, y0 - 0.07, F0, st)
        zc = F0 + TH + 0.08
        n = 10
        for k in range(n):                                                     # Bogenring (Stein) und Fuellung (Holz) ueber dem Sturz
            a0, a1 = math.pi * k / n, math.pi * (k + 1) / n
            for (ra, rb, m) in ((0.0, 0.55, tuerm), (0.55, 0.8, st)):
                P = [(tx + ra * math.cos(a0), y0 - 0.02, zc + ra * math.sin(a0)), (tx + rb * math.cos(a0), y0 - 0.02, zc + rb * math.sin(a0)),
                     (tx + rb * math.cos(a1), y0 - 0.02, zc + rb * math.sin(a1)), (tx + ra * math.cos(a1), y0 - 0.02, zc + ra * math.sin(a1))]
                if ra == 0.0:
                    P = [P[1], P[2], P[3]] if False else [(tx, y0 - 0.02, zc), P[1], P[2]]
                g.poly(P, (0.0, -1.0, 0.0), m)
        g.box(tx - 0.12, y0 - 0.08, zc + 0.78, tx + 0.12, y0, zc + 0.95, st)       # Schlussstein
        g.box(t0 - 0.14, y0 - 0.08, F0, t0 - 0.02, y0, zc, st)                      # Gewaende
        g.box(t1 + 0.02, y0 - 0.08, F0, t1 + 0.14, y0, zc, st)
    else:                                                                    # schlicht: nur Stufe, Schwelle, Laterne, Hausnummernschild
        g.box(t0 - 0.2, y0 - 0.7, -0.6, t1 + 0.2, y0 - 0.07, F0, st)
        g.box(t1 + 0.35, y0 - 0.14, 1.9, t1 + 0.5, y0, 2.3, "Metall")
        g.box(t1 + 0.3, y0 - 0.2, 2.3, t1 + 0.55, y0, 2.45, "Metall")
        g.box(t0 - 0.55, y0 - 0.03, 1.5, t0 - 0.25, y0, 1.7, "Rahmen weiss")


def haus(b, cx, cy, zb, theta, T, seed=0):
    """Wohnhaus im Stil der 1940er Jahre (verwitterte Siedlungs-/Stadthaeuser, teils Fachwerk): Putz oder Fachwerk auf Sockel,
    Sprossenfenster, Fensterlaeden (teils defekt), Haustuer mit Freitreppe und Vordach; Dachformen x/y/walm/mansard/pult mit Gauben und Kamin.
    Innen: Flur mit Treppe, 2-3 Zimmer je Etage, bei stock == 2 begehbares Obergeschoss (Treppenloch mit Gelaender).
    Tuer auf der lokalen -y-Seite; T['tuer_x'] = Lage der Tuer, T['spiegel'] = +-1, T['verfall'] 0..2, T['dachform'], T['fachwerk']."""
    rnd = random.Random(seed * 7919 + 17)
    g = Lok(b, cx, cy, zb, theta, T.get("spiegel", 1))
    w, d, st, rh = T["w"], T["d"], T["stock"], T["rh"]
    lvl = T.get("verfall", 0)
    mat = (T["wand"] + " alt") if lvl and (T["wand"] + " alt") in FARBEN else T["wand"]
    dach_m = (T["dach"] + " alt") if lvl and (T["dach"] + " alt") in FARBEN else T["dach"]
    laden = T.get("laden")
    if laden and lvl and (laden + " alt") in FARBEN:
        laden = laden + " alt"
    form = T.get("dachform", "x")
    H = (F1 + 2.65) if st == 2 else (F0 + 2.85)
    tx = T["tuer_x"]
    ix0, ix1, iy0, iy1 = -w / 2 + WD, w / 2 - WD, -d / 2 + WD, d / 2 - WD
    px = T["px"]                                                  # Trennwand (Flur | Zimmer) bei x = px
    qy = T.get("qy")                                              # Trennwand zwischen den Zimmern bei y = qy
    ew, ow = 1.1, 1.5                                             # Fensterbreite / -hoehe
    zc_eg, zc_og = F0 + 1.55, F1 + 1.4

    def zustaende():
        r = rnd.random()
        zu = "ok"
        if lvl == 1:
            zu = "kaputt" if r < 0.10 else ("bretter" if r < 0.14 else "ok")
        elif lvl >= 2:
            zu = "kaputt" if r < 0.22 else ("bretter" if r < 0.42 else "ok")
        lz = []
        for _ in range(2):
            r = rnd.random()
            if lvl == 0:
                lz.append("ok")
            elif lvl == 1:
                lz.append("fehlt" if r < 0.2 else ("schief" if r < 0.35 else "ok"))
            else:
                lz.append("fehlt" if r < 0.35 else ("schief" if r < 0.6 else "ok"))
        return zu, tuple(lz)

    def fens(lst_eg, lst_og):
        r = [(a, zc_eg, zustaende()) for a in lst_eg] + [(a, zc_og, zustaende()) for a in (lst_og if st == 2 else ())]
        return r
    wins = {"v": fens(T["fw_eg"], T["fw_og"]), "h": fens(T["bw_eg"], T["bw_og"]), "w": fens(T["ww_eg"], T["ww_og"]), "o": fens(T["ow_eg"], T["ow_og"])}
    oeffs = {k: [(a - ew / 2, a + ew / 2, zc - ow / 2, zc + ow / 2) for (a, zc, _z) in v] for k, v in wins.items()}
    tuer = (tx - 0.55, tx + 0.55, F0, F0 + TH)
    oeffs["v"].append(tuer)
    waende = [("x", -d / 2, -1, -w / 2, w / 2, oeffs["v"]), ("x", d / 2, 1, -w / 2, w / 2, oeffs["h"]),
              ("y", -w / 2, -1, -d / 2 + WD, d / 2 - WD, oeffs["w"]), ("y", w / 2, 1, -d / 2 + WD, d / 2 - WD, oeffs["o"])]
    for wd, key in zip(waende, ("v", "h", "w", "o")):
        ach, aussen, sg, a0, a1, oeff = wd
        aussenwand(g, ach, aussen, sg, a0, a1, H, mat, oeff)
        for (a, zc, (zu, lz)) in wins[key]:
            fensterschmuck(g, ach, aussen, sg, a, zc, ew, ow, laden, zu, lz)
        if T.get("fachwerk"):
            fachwerk(g, wd, H, st)
    if lvl:
        verfall_aussen(g, waende, H, rnd, lvl)
    # Haustuer: Rahmen, Schwelle, offenes Tuerblatt (nach innen, an der Flurwand)
    tuerrahmen(g, "x", -d / 2 - 0.07, -d / 2 + 0.0, tuer[0], tuer[1], F0, F0 + TH)
    g.box(tuer[0], -d / 2 - 0.05, F0 - 0.04, tuer[1], -d / 2 + WD, F0, "Stein")
    g.box(tuer[1] - 0.05, iy0, F0, tuer[1], iy0 + 0.95, F0 + TH - 0.05, T.get("tuerfarbe", "Tuer"))
    eingang(g, T.get("eingang", "vordach"), tx, d, mat, lvl, T.get("tuerfarbe", "Tuer"))
    # Geschossdecken, Boden
    g.box(ix0, iy0, -0.7, ix1, iy1, F0, "Dielen")
    sx0 = px + 2.1                                                # Treppenband: x = sx0 .. ix1
    ys = -1.2                                                     # Treppenfuss, 15 Steigungen zu je 0,27 m Auftritt
    nst = 15
    rise = (F1 - F0) / nst
    if st == 2:
        hy0, hy1 = ys + 4 * 0.27, ys + nst * 0.27                 # Treppenloch in der OG-Decke

        def platte(x0, y0, x1, y1):
            g.box(x0, y0, F1 - 0.25, x1, y1, F1 - 0.05, "Decke")
            g.box(x0, y0, F1 - 0.05, x1, y1, F1, "Dielen")
        platte(ix0, iy0, sx0, iy1)
        platte(sx0, iy0, ix1, hy0)
        platte(sx0, hy1, ix1, iy1)
        for k in range(nst):                                      # Treppe (massive Stufen) + Gelaender an der offenen Seite
            y0 = ys + k * 0.27
            zt = F0 + (k + 1) * rise
            g.box(sx0, y0, F0, ix1, y0 + 0.27, zt, "Holz")
            g.box(sx0 - 0.07, y0, zt + 0.45, sx0 - 0.02, y0 + 0.27, zt + 0.5, "Holz")
            g.box(sx0 - 0.07, y0, zt + 0.92, sx0 - 0.02, y0 + 0.27, zt + 0.97, "Holz")
            if k % 3 == 0:
                g.box(sx0 - 0.08, y0 + 0.1, zt, sx0 - 0.01, y0 + 0.17, zt + 0.97, "Holz")
        for (x0, y0, x1, y1) in ((sx0 - 0.07, hy0, sx0 - 0.02, hy1), (sx0, hy0 - 0.07, ix1, hy0 - 0.02)):         # Gelaender OG um das Loch
            g.box(x0, y0, F1 + 0.45, x1, y1, F1 + 0.5, "Holz")
            g.box(x0, y0, F1 + 0.95, x1, y1, F1 + 1.0, "Holz")
        for (xx, yy) in ((sx0 - 0.045, hy0 - 0.045), (sx0 - 0.045, (hy0 + hy1) / 2), (sx0 - 0.045, hy1 - 0.1)):
            g.box(xx - 0.04, yy - 0.04, F1, xx + 0.04, yy + 0.04, F1 + 1.0, "Holz")
        g.box(ix0, iy0, H - 0.25, ix1, iy1, H, "Decke")
    else:
        g.box(ix0, iy0, H - 0.25, ix1, iy1, H, "Decke")
    # Innenwaende (EG und OG): Flurwand bei x = px mit Tuer, Zimmertrennwand bei y = qy mit Tuer
    for (zlo, zhi) in ((F0, (F1 - 0.25) if st == 2 else H - 0.25),) + (((F1, H - 0.25),) if st == 2 else ()):
        o1 = [(-1.55, -0.55, zlo, zlo + 2.1)]
        wand(g, "y", px - 0.06, px + 0.06, iy0, iy1, zlo, zhi, "Innenwand", o1)
        tuerrahmen(g, "y", px - 0.06, px + 0.06, o1[0][0], o1[0][1], zlo, zlo + 2.1)
        if qy is not None:
            o2 = [(-2.6, -1.6, zlo, zlo + 2.1)]
            wand(g, "x", qy - 0.06, qy + 0.06, ix0, px - 0.06, zlo, zhi, "Innenwand", o2)
            tuerrahmen(g, "x", qy - 0.06, qy + 0.06, o2[0][0], o2[0][1], zlo, zlo + 2.1)
    # Dach
    rz = dach(g, form, w, d, H, rh, dach_m, mat)
    if lvl:
        verfall_dach(g, form, rz, w, d, H, rnd, lvl)
    if form in ("x", "walm"):
        L = max(0.0, (w - d) / 2.0) if form == "walm" else 99.0
        for ax in T.get("gauben", ()):
            if abs(ax) + 1.0 <= L + d / 2 - 1.0:
                gaube(g, ax, H, rh, d, mat, dach_m)
    if form in ("x", "mansard"):
        for sgn in (-1, 1):                                                   # Giebelfenster
            xo = sgn * w / 2
            zg = H + (0.6 if form == "x" else 1.1)
            g.box(min(xo, xo + sgn * 0.06), -0.35, zg, max(xo, xo + sgn * 0.06), 0.35, zg + 0.9, "Fenster")
            g.box(min(xo, xo + sgn * 0.08), -0.04, zg, max(xo, xo + sgn * 0.08), 0.04, zg + 0.9, "Rahmen weiss")
    if form == "y":
        for sy in (-1, 1):                                                    # Giebelfenster an Vorder- und Rueckseite
            yo = sy * d / 2
            g.box(-0.4, min(yo, yo + sy * 0.06), H + 0.8, 0.4, max(yo, yo + sy * 0.06), H + 1.8, "Fenster")
            g.box(-0.04, min(yo, yo + sy * 0.08), H + 0.8, 0.04, max(yo, yo + sy * 0.08), H + 1.8, "Rahmen weiss")
    ch = T["kamin"]
    cy_ = {"y": (d / 2 - 1.6) * (1 if ch >= 0 else -1), "pult": d / 2 - 1.0}.get(form, 0.0)
    kx, ky = (0.0, cy_) if form == "y" else (ch, cy_)
    ztop = max(rz(kx + a, ky + c) for a in (-0.45, 0.45) for c in (-0.45, 0.45)) + 0.9
    rustik.kamin(g, kx, ky, H - 0.1, ztop + 0.1, rnd, 0.8)
    if lvl >= 2 and rnd.random() < 0.6:                                       # abgebrochener Kaminkopf: Ziegelhaufen daneben
        g.box(kx + 0.5, ky - 0.2, rz(kx + 0.5, ky) + 0.0, kx + 1.0, ky + 0.2, rz(kx + 1.0, ky) + 0.25, "Klinker alt")
    g.box(w / 2 - 0.15, -d / 2 - 0.12, 0.0, w / 2 - 0.03, -d / 2 - 0.02, H - 0.3, "Metall")                 # Fallrohr
    return g


def scheune(b, cx, cy, zb, theta, w=12.0, d=9.0):
    """Bauernscheune: grosses Holzhaus mit Doppeltor auf der Strassenseite."""
    g = Lok(b, cx, cy, zb, theta)
    h, rh = 4.6, 3.4
    g.box(-w / 2, -d / 2, -1.0, w / 2, d / 2, h, "Holz")
    satteldach(g, w, d, h, rh, "Dach grau", "Holz")
    dk = altbau.Deko(g)
    for (ach, aus, sg, a0, a1) in (("x", -d / 2, -1, -w / 2, w / 2), ("x", d / 2, 1, -w / 2, w / 2), ("y", -w / 2, -1, -d / 2, d / 2), ("y", w / 2, 1, -d / 2, d / 2)):
        altbau.scheunen_latten(dk, ach, aus, sg, a0, a1, 0.0, h)
    altbau.sockel(g, "x", -d / 2, -1, -w / 2, w / 2, [(-1.6, 1.6, -1, 3.4)])
    altbau.sockel(g, "x", d / 2, 1, -w / 2, w / 2, [])
    g.box(-1.6, -d / 2 - 0.08, 0.0, 1.6, -d / 2, 3.4, "Tuer")
    g.box(-0.05, -d / 2 - 0.12, 0.0, 0.05, -d / 2, 3.4, "Stein")
    for sx in (-1, 1):
        g.box(sx * 4.2 - 0.5, -d / 2 - 0.05, 3.0, sx * 4.2 + 0.5, -d / 2, 3.9, "Fenster")
    return g


def rathaus(b, cx, cy, theta):
    """Altes Rathaus mit Uhrturm (rustikal, viele Polygone) - siehe rustik.py."""
    import rustik
    return rustik.rathaus(b, cx, cy, theta)


def gasthaus(b, cx, cy, theta):
    """Altes Gasthaus mit Fachwerkobergeschoss - siehe rustik.py."""
    import rustik
    return rustik.gasthaus(b, cx, cy, theta)


def laden(b, cx, cy, theta):
    """Laden (8 x 10 m) mit Markise ueber dem Schaufenster."""
    g = Lok(b, cx, cy, 0.0, theta)
    w, d, h, rh = 8.0, 10.0, 4.4, 2.4
    g.box(-w / 2, -d / 2, -1.0, w / 2, d / 2, h, "Putz blau" if (round(cx) % 2) else "Putz weiss")
    satteldach(g, w, d, h, rh, "Dach grau", "Putz weiss")
    g.box(-w / 2 + 1.0, -d / 2 - 0.05, 0.9, w / 2 - 1.0, -d / 2, 2.6, "Fenster")
    g.box(-0.5, -d / 2 - 0.08, 0.0, 0.5, -d / 2, 2.1, "Tuer")
    for k in range(4):
        g.box(-w / 2 + 0.6 + k * 1.7, -d / 2 - 1.1, 2.7 - 0.0, -w / 2 + 0.6 + (k + 1) * 1.7, -d / 2 - 0.05, 3.0, "Markt rot" if k % 2 == 0 else "Markt weiss")
    return g


def brunnen(b, cx, cy):
    b.prism(cx, cy, 0.0, 3.4, 0.5, 8, "Stein")                         # Becken
    b.prism(cx, cy, 0.4, 2.9, 0.15, 8, "Brunnenwasser")
    b.prism(cx, cy, 0.4, 0.45, 2.3, 8, "Stein")                        # Saeule
    b.prism(cx, cy, 2.4, 1.3, 0.25, 8, "Stein")                        # obere Schale
    b.prism(cx, cy, 2.6, 0.9, 0.12, 8, "Brunnenwasser")


def marktstand(b, cx, cy, theta, farbe):
    g = Lok(b, cx, cy, 0.0, theta)
    g.box(-1.5, -0.6, 0.0, 1.5, 0.6, 0.95, "Holz")                                                              # Tisch
    for sx in (-1, 1):
        for sy in (-1, 1):
            g.box(sx * 1.45 - 0.05, sy * 1.0 - 0.05, 0.0, sx * 1.45 + 0.05, sy * 1.0 + 0.05, 2.5, "Holz")      # Pfosten
    for k in range(6):
        g.box(-1.65 + k * 0.55, -1.2, 2.5, -1.65 + (k + 1) * 0.55, 1.2, 2.62, farbe if k % 2 == 0 else "Markt weiss")
    g.box(-1.0, -0.4, 0.95, 0.0, 0.4, 1.3, "Putz gelb")                                                         # Ware
    g.box(0.3, -0.4, 0.95, 1.2, 0.4, 1.2, "Markt rot")


def baum(b, x, y, zb, kind=0):
    b.prism(x, y, zb, 0.22, 2.2, 6, "Stamm")
    for k, (r, z0, hh) in enumerate(((1.9, 1.6, 2.6), (1.4, 3.3, 2.3))):
        n = 7
        mat = "Laub" if kind == 0 else "Laub hell"
        ring = [(x + r * math.cos(2 * math.pi * i / n), y + r * math.sin(2 * math.pi * i / n), zb + z0) for i in range(n)]
        apex = (x, y, zb + z0 + hh)
        b.add(ring + [apex], [tuple(range(n - 1, -1, -1))] + [(i, (i + 1) % n, n) for i in range(n)], mat)
        # Bodenflaeche zeigt nach unten (Index n-1..0), Seiten nach aussen (gegen den Uhrzeigersinn von oben gesehen)
    b.bx.append((x - 1.9, y - 1.9, zb, x + 1.9, y + 1.9, zb + 6.0))


def dorfbrunnen(b, cx, cy):
    b.prism(cx, cy, 0.0, 1.3, 0.9, 8, "Stein")
    b.prism(cx, cy, 0.6, 0.95, 0.4, 8, "Brunnenwasser")
    for sx in (-1, 1):
        b.box(cx + sx * 1.1 - 0.08, cy - 0.08, 0.9, cx + sx * 1.1 + 0.08, cy + 0.08, 2.6, "Holz")
    b.box(cx - 1.4, cy - 0.9, 2.6, cx + 1.4, cy + 0.9, 2.8, "Dach rot")


# ------------------------------------------------------------------ Platzierung
class Belegt:
    """Verwaltet belegte Flaechen (Kreise) fuer Haeuser, Baeume und andere Bauten."""

    def __init__(self, strs):
        self.strs = strs
        self.kreise = []                      # (x, y, r)
        self.rechtecke = []                   # (x0, y0, x1, y1)

    def frei(self, x, y, r, rand=0.4, strasse=True):
        ra = math.hypot(x - C, y - C)
        if ra < U.ring_r(math.atan2(y - C, x - C)) + U.BREITE_WEG / 2 + r + 8.0 or max(abs(x - C), abs(y - C)) < 46.0 + r:
            return False                                   # Burg, Graben und Ringweg
        if not (4.0 + r < x < 296.0 - r and 4.0 + r < y < 296.0 - r):
            return False
        for tx, ty, tr in U.TEICHE:
            if math.hypot(x - tx, y - ty) < tr + 5.0 + r:
                return False
        if strasse and strassenabstand(x, y, self.strs) < r + rand:
            return False
        for (x0, y0, x1, y1) in self.rechtecke:
            if x0 - r - rand < x < x1 + r + rand and y0 - r - rand < y < y1 + r + rand:
                return False
        for (cx, cy, cr) in self.kreise:
            if math.hypot(x - cx, y - cy) < r + cr + rand:
                return False
        return True


def _frei_haus(self, hx, hy, theta, w, d, vorbau=1.3):
    """Platzpruefung fuer ein Haus (Grundriss w x d, Stufen/Vordach 1,2 m davor): Stuetzpunkte auf dem Grundriss muessen frei von
    Strassen, Plaetzen/Gebaeuden und Teichen sein; Burg, Rand, Flughafen und andere Haeuser (Kreis max(w,d)/2 + 1) wie bei frei()."""
    r = max(w, d) / 2 + 1.0
    rb = math.hypot(w, d) / 2 + 1.0
    if not self.frei(hx, hy, rb, rand=0.0, strasse=False):
        return False
    c, s_ = math.cos(theta), math.sin(theta)
    for ix in range(-int(w / 2.5) - 1, int(w / 2.5) + 2):
        for iy in range(-int(d / 2.5) - 1, int(d / 2.5) + 3):
            lx = max(-w / 2 - 0.8, min(w / 2 + 0.8, ix * 2.5))
            ly = max(-d / 2 - vorbau - 0.3, min(d / 2 + 0.8, iy * 2.5))
            px, py = hx + lx * c - ly * s_, hy + lx * s_ + ly * c
            if strassenabstand(px, py, self.strs) < 0.5:
                return False
            for (x0, y0, x1, y1) in self.rechtecke:
                if x0 - 0.5 < px < x1 + 0.5 and y0 - 0.5 < py < y1 + 0.5:
                    return False
    for (cx_, cy_, cr) in self.kreise:
        if math.hypot(hx - cx_, hy - cy_) < r + cr:
            return False
    return True


Belegt.frei_haus = _frei_haus


def eben(x, y, r, tol=0.35):
    zs = [U.gelaende_hoehe(x + r * math.cos(a), y + r * math.sin(a)) for a in (0.0, 1.57, 3.14, 4.71)] + [U.gelaende_hoehe(x, y)]
    return max(abs(z) for z in zs) < tol, sum(zs) / len(zs)


_A = dict(stock=2, rh=3.1, px=1.0, qy=0.3, tuer_x=2.4, fw_eg=(-2.6, -0.4), fw_og=(-2.6, -0.4, 2.4), bw_eg=(-2.6, -0.4, 2.0), bw_og=(-2.6, -0.4, 2.0),
          ww_eg=(-1.8, 1.8), ww_og=(-1.8, 1.8), ow_eg=(-2.4,), ow_og=(-2.4,))
_C = dict(stock=1, rh=3.0, px=0.5, qy=None, tuer_x=2.0, fw_eg=(-2.4, -0.3), fw_og=(), bw_eg=(-2.2, 2.0), bw_og=(), ww_eg=(0.0,), ww_og=(), ow_eg=(-1.5,), ow_og=())
HAUSTYPEN = [   # heruntergekommener 1940er-Stil; dachform: x/y/walm/mansard/pult; fachwerk: sichtbares Holzgeruest; verfall: 0..2
    dict(_A, w=9.6, d=8.4, wand="Putz weiss", dach="Ziegel", laden="Laden gruen", dachform="x", gauben=(-1.8, 1.8), kamin=-3.3, spiegel=1, verfall=1, eingang="vordach", tuerfarbe="Tuer"),
    dict(_A, w=9.0, d=8.0, wand="Putz gelb", dach="Ziegel dunkel", laden="Laden braun", dachform="walm", rh=2.7, gauben=(0.0,), kamin=-1.0, spiegel=-1, verfall=2, eingang="windfang", tuerfarbe="Tuer gruen"),
    dict(_A, w=10.2, d=8.0, wand="Putz weiss", dach="Ziegel", laden=None, dachform="y", rh=3.7, fachwerk=True, kamin=1.0, spiegel=1, verfall=1, eingang="veranda", tuerfarbe="Tuer rot"),
    dict(_A, w=9.0, d=8.6, wand="Putz grau", dach="Dach grau", laden="Laden gruen", dachform="mansard", rh=3.5, kamin=2.4, spiegel=-1, verfall=2, eingang="portal", tuerfarbe="Tuer blau"),
    dict(_C, w=8.0, d=7.0, wand="Putz gruen", dach="Ziegel", laden="Laden braun", dachform="x", gauben=(-1.2,), kamin=-2.8, spiegel=1, verfall=1, eingang="schlicht", tuerfarbe="Tuer grau"),
    dict(_C, w=8.6, d=7.4, wand="Putz rot", dach="Ziegel dunkel", laden="Laden gruen", dachform="pult", rh=1.7, kamin=2.4, spiegel=-1, verfall=2, eingang="vordach_giebel", tuerfarbe="Tuer"),
    dict(_A, w=9.6, d=8.0, wand="Putz sand", dach="Ziegel", laden="Laden braun", dachform="x", fachwerk=True, gauben=(-2.0,), kamin=3.3, spiegel=-1, verfall=1, eingang="windfang", tuerfarbe="Tuer rot"),
    dict(_C, w=7.6, d=6.8, wand="Putz weiss", dach="Ziegel", laden=None, dachform="y", rh=3.2, fachwerk=True, kamin=1.0, spiegel=1, verfall=2, eingang="rundbogen", tuerfarbe="Tuer gruen"),
    dict(_A, w=9.4, d=8.2, wand="Putz blau", dach="Ziegel dunkel", laden="Laden gruen", dachform="y", rh=3.5, kamin=-1.0, spiegel=-1, verfall=1, eingang="veranda", tuerfarbe="Tuer blau"),
    dict(_A, w=10.0, d=8.4, wand="Klinker", dach="Ziegel", laden="Laden braun", dachform="walm", rh=2.8, gauben=(-1.8, 1.8), kamin=-1.0, spiegel=1, verfall=0, eingang="portal", tuerfarbe="Tuer"),
]


def setze_haus(zb_, b, wege_b, belegt, hausliste, x, y, nx, ny, hr, typ, rand_strasse_pt=None, scheune_=False):
    """Versucht, ein Haus bei (x, y) mit Tuer in Richtung (nx, ny) zu setzen und mit einem Pfad zur Strasse zu verbinden.

    hr = Abstand der Strassenkante von der Strassenmitte am Pfadanfang. Rueckgabe True bei Erfolg."""
    return False


def haeuser_entlang(L, p, q, strs, belegt, haeuser, pfade, abstand=15.5, rand=11.0, setback=3.2, zaehler=[0], seiten=(1, -1), strasse=None):
    dx, dy = q[0] - p[0], q[1] - p[1]
    ln = math.hypot(dx, dy)
    if ln < 2 * rand + 4:
        return
    ux, uy = dx / ln, dy / ln
    nrm = (-uy, ux)
    hr = strasse["w"] / 2
    n = int((ln - 2 * rand) // abstand) + 1
    t0 = rand + ((ln - 2 * rand) - (n - 1) * abstand) / 2
    for k in range(n):
        t = t0 + k * abstand
        for s in seiten:
            nx_, ny_ = -s * nrm[0], -s * nrm[1]                 # Richtung zur Strasse (Tuerseite)
            dx_, dy_ = p[0] + ux * t + s * nrm[0] * (hr + setback), p[1] + uy * t + s * nrm[1] * (hr + setback)   # Tuer-/Stufenpunkt
            theta = math.atan2(nx_, -ny_)
            for typ in typ_folge(len(haeuser)):                  # erster Typ, der an diese Stelle passt (Abwechslung der Typen)
                w, d = typ["w"], typ["d"]
                tdx = typ["tuer_x"] * typ["spiegel"]
                hx, hy = dx_ - nx_ * d / 2 - (-ny_) * tdx, dy_ - ny_ * d / 2 - nx_ * tdx
                ok_e, zb = eben(hx, hy, min(w, d) / 2, 0.15)
                if ok_e and belegt.frei_haus(hx, hy, theta, w, d, typ_vorbau(typ)):
                    break
            else:
                continue
            r = max(w, d) / 2 + 1.0
            belegt.kreise.append((hx, hy, r))
            haeuser.append({"seed": len(haeuser) + 1, "x": hx, "y": hy, "r": r, "theta": theta, "typ": typ, "zb": zb, "w": w, "d": d, "strasse": strasse["name"]})
            door = (dx_ + nx_ * (typ_vorbau(typ) + 0.05), dy_ + ny_ * (typ_vorbau(typ) + 0.05))
            start = (p[0] + ux * t + s * nrm[0] * (hr - 0.3), p[1] + uy * t + s * nrm[1] * (hr - 0.3))
            pfade.append((start, door))


def typ_vorbau(typ):
    return VORBAU[typ.get("eingang", "vordach")]


def typ_folge(n):
    """Reihenfolge der Haustypen, die fuer das n-te Haus der Reihe nach probiert werden (springt ueber die 10 Typen)."""
    return [HAUSTYPEN[(n * 7 + j * 3) % len(HAUSTYPEN)] for j in range(5)]


def kreis_haeuser(zentrum, r_innen, strs, belegt, haeuser, pfade, n=9, ohne=(-math.pi / 2,), versatz=0.0, strasse=None, scheune_idx=3):
    cx, cy = zentrum
    zaehler = 0
    for k in range(n):
        a = versatz + 2 * math.pi * k / n
        if any(abs((a - o + math.pi) % (2 * math.pi) - math.pi) < 0.5 for o in ohne):
            continue
        sched = k == scheune_idx
        rad = r_innen + 3.2
        theta = math.atan2(-math.cos(a), math.sin(a))              # Tuer zeigt zur Mitte: Richtung (-cos a, -sin a)
        for typ in (typ_folge(len(haeuser)) if not sched else [HAUSTYPEN[0]]):
            w, d = (12.0, 9.0) if sched else (typ["w"], typ["d"])
            tdx = 0.0 if sched else typ["tuer_x"] * typ["spiegel"]
            # Tuerpunkt D liegt auf dem Radius rad; Mittelpunkt = D - n*d/2 - xachse*tdx mit n = (-cos a, -sin a), xachse = (sin a, -cos a)
            hx = cx + rad * math.cos(a) + math.cos(a) * d / 2 - math.sin(a) * tdx
            hy = cy + rad * math.sin(a) + math.sin(a) * d / 2 + math.cos(a) * tdx
            ok_e, zb = eben(hx, hy, min(w, d) / 2, 0.15)
            if ok_e and belegt.frei_haus(hx, hy, theta, w, d, 1.3 if sched else typ_vorbau(typ)):
                break
        else:
            continue
        r = max(w, d) / 2 + 1.0
        belegt.kreise.append((hx, hy, r))
        haeuser.append({"seed": len(haeuser) + 1, "x": hx, "y": hy, "r": r, "theta": theta, "typ": typ, "zb": zb, "w": w, "d": d, "scheune": sched, "strasse": strasse["name"]})
        vb = 0.95 if sched else typ_vorbau(typ) + 0.05
        door = (cx + (r_innen + 3.2 - vb) * math.cos(a), cy + (r_innen + 3.2 - vb) * math.sin(a))
        start = (cx + (r_innen - 0.3) * math.cos(a), cy + (r_innen - 0.3) * math.sin(a))
        pfade.append((start, door))


# ------------------------------------------------------------------ Oeffentliche Gebaeude (ersetzen Wohnhaeuser)
def _fuss(art, cx, cy, theta, zus=0.0):
    """Grundriss-Rechteck (x0, y0, x1, y1) eines oeffentlichen Gebaeudes; theta ist ein Vielfaches von 90 Grad."""
    w, d, vor = {"feuerwehr": (40.0, 8.4, 1.2), "supermarkt": (12.0, 9.0, 1.7), "post": (11.0, 9.0, 1.7), "kirche": (10.6 + 1.2, 26.0, 1.7)}[art]
    c, s_ = math.cos(theta), math.sin(theta)
    pts = []
    for lx, ly in ((-w / 2 - 0.4, -d / 2 - vor), (w / 2 + 0.4, -d / 2 - vor), (w / 2 + 0.4, d / 2 + 0.6), (-w / 2 - 0.4, d / 2 + 0.6)):
        if art == "feuerwehr":
            lx = max(-w / 2 - 0.4, min(lx, w / 2 + 0.4))
        pts.append((cx + lx * c - ly * s_, cy + lx * s_ + ly * c))
    return (min(p[0] for p in pts), min(p[1] for p in pts), max(p[0] for p in pts), max(p[1] for p in pts))


def _flaeche_frei(belegt, rc, ignoriere=()):
    """Ist das Rechteck rc frei von Strassen, Plaetzen/Gebaeuden, Teichen, Burg und anderen Haeusern (Kreise ausser 'ignoriere')?"""
    x0, y0, x1, y1 = rc
    if not (4.0 < x0 and x1 < 296.0 and 4.0 < y0 and y1 < 296.0):
        return False
    nx_ = int((x1 - x0) / 1.5) + 2
    ny_ = int((y1 - y0) / 1.5) + 2
    for i in range(nx_ + 1):
        for j in range(ny_ + 1):
            px, py = x0 + (x1 - x0) * i / nx_, y0 + (y1 - y0) * j / ny_
            ra = math.hypot(px - C, py - C)
            if ra < U.ring_r(math.atan2(py - C, px - C)) + U.BREITE_WEG / 2 + 8.0 or max(abs(px - C), abs(py - C)) < 46.0:
                return False
            if strassenabstand(px, py, belegt.strs) < 0.5:
                return False
            for tx, ty, tr in U.TEICHE:
                if math.hypot(px - tx, py - ty) < tr + 2.0:
                    return False
            for (a0, b0, a1, b1) in belegt.rechtecke:
                if a0 - 0.5 < px < a1 + 0.5 and b0 - 0.5 < py < b1 + 0.5:
                    return False
            for k in belegt.kreise:
                if k not in ignoriere and math.hypot(px - k[0], py - k[1]) < k[2]:
                    return False
            if abs(U.gelaende_hoehe(px, py)) > 0.15:
                return False
    return True


def setze_spezial(strs, belegt, haeuser, pfade):
    """Ersetzt einzelne Wohnhaeuser durch Feuerwehr, Supermarkt, Post und Kirche (gleiche Tuerseite/Strassenanbindung). Rueckgabe: (spezial, plaetze)."""
    def finde(x, y, strasse="Marktring"):
        for i, h in enumerate(haeuser):
            if h["strasse"] == strasse and abs(h["x"] - x) < 1.0 and abs(h["y"] - y) < 1.0:
                return i
        return None

    def tuer(h):
        th = h["theta"]
        n = (math.sin(th), -math.cos(th))
        xa = (math.cos(th), math.sin(th))
        t = h["typ"]
        tdx = t["tuer_x"] * t["spiegel"]
        return (h["x"] + n[0] * h["d"] / 2 + xa[0] * tdx, h["y"] + n[1] * h["d"] / 2 + xa[1] * tdx), n, xa

    auftraege = [("feuerwehr", [(17.6, 140.1), (17.6, 155.1), (17.6, 170.1)]), ("supermarkt", [(72.3, 125.5)]), ("post", [(72.4, 198.2)]),
                 ("kirche", [(57.0, 197.9), (37.6, 198.2)])]
    spezial, plaetze, entfernen = [], [], []
    for art, orte in auftraege:
        idx = [finde(*o) for o in orte]
        if None in idx:
            continue
        hs = [haeuser[i] for i in idx]
        kreise = [(h["x"], h["y"], h["r"]) for h in hs]
        th = hs[0]["theta"]
        n = (math.sin(th), -math.cos(th))
        xa = (math.cos(th), math.sin(th))
        if art == "feuerwehr":
            cx = sum(h["x"] for h in hs) / len(hs)
            cy = sum(h["y"] for h in hs) / len(hs)
            vor = 1.2
        else:
            ds = [tuer(h)[0] for h in hs]
            D = (sum(p[0] for p in ds) / len(ds), sum(p[1] for p in ds) / len(ds))
            w, d, tdx = {"supermarkt": (12.0, 9.0, 3.8), "post": (11.0, 9.0, 0.0), "kirche": (10.6, 26.0, 0.0)}[art]
            cx, cy = D[0] - n[0] * d / 2 - xa[0] * tdx, D[1] - n[1] * d / 2 - xa[1] * tdx
            vor = 1.7
        rc = _fuss(art, cx, cy, th)
        if not _flaeche_frei(belegt, rc, ignoriere=kreise):
            print("Hinweis: %s passt nicht, Wohnhaeuser bleiben" % art)
            continue
        zb = sum(h["zb"] for h in hs) / len(hs)
        if art == "feuerwehr":
            c_, s_ = math.cos(th), math.sin(th)
            tdoor = (cx + 15.6 * c_ + 4.2 * s_, cy + 15.6 * s_ - 4.2 * c_)                # Turmtuer (lokal x = 15,6; Fassade y = -4,2)
            st0 = pfade[idx[1]][0]
            start = (st0[0], tdoor[1]) if abs(n[0]) > 0.5 else (tdoor[0], st0[1])
            ziel = (tdoor[0] + n[0] * 0.9, tdoor[1] + n[1] * 0.9)
            pfade_neu = [(start, ziel)]
            fx = (cx + n[0] * 4.2, cy + n[1] * 4.2)
            plaetze.append((min(fx[0], st0[0]) if abs(n[0]) > 0.5 else cx - 20.0, cy - 20.0 if abs(n[0]) > 0.5 else min(fx[1], st0[1]),
                            max(fx[0], st0[0]) if abs(n[0]) > 0.5 else cx + 20.0, cy + 20.0 if abs(n[0]) > 0.5 else max(fx[1], st0[1])))
        else:
            a = pfade[idx[0]]
            sv = (D[0] - tuer(hs[0])[0][0], D[1] - tuer(hs[0])[0][1])
            pfade_neu = [((a[0][0] + sv[0], a[0][1] + sv[1]), (D[0] + n[0] * (vor + 0.05), D[1] + n[1] * (vor + 0.05)))]
        entfernen += idx
        spezial.append({"art": art, "x": cx, "y": cy, "theta": th, "zb": zb, "rc": rc, "pfade": pfade_neu, "kreise": kreise})
    for i in sorted(set(entfernen), reverse=True):
        del haeuser[i]
        del pfade[i]
    for sp in spezial:
        for k in sp["kreise"]:
            if k in belegt.kreise:
                belegt.kreise.remove(k)
        belegt.rechtecke.append(sp["rc"])
        pfade.extend(sp["pfade"])
    for pl in plaetze:
        belegt.rechtecke.append(pl)
    return spezial, plaetze


def plane_stadt():
    """Berechnet das ganze Layout: Strassen, Gebaeude am Platz, Haeuser, Pfade, Baeume. Rueckgabe: dict."""
    strs = strassen()
    S = {s["name"]: s for s in strs}
    belegt = Belegt(strs)
    haeuser, pfade = [], []
    # Zentrum: Rathaus, Gasthaus, Laeden (fest platziert)
    x0, y0, x1, y1 = PLATZ
    zentrum = [
        ("rathaus", 55.0, 171.0, 0.0, (44.0, 165.0, 66.0, 177.0)),                         # Nordseite, Fassade zum Platz (-y)
        ("gasthaus", 55.0, 130.0, math.pi, (46.0, 125.0, 64.0, 135.0)),                     # Suedseite, Fassade nach Norden
        ("laden", 35.0, 142.0, math.pi / 2, (30.0, 137.0, 40.0, 147.0)),                    # Westseite, Fassade nach Osten (+x)
        ("laden", 35.0, 158.0, math.pi / 2, (30.0, 153.0, 40.0, 163.0)),
        ("laden", 75.0, 142.0, -math.pi / 2, (70.0, 137.0, 80.0, 147.0)),                   # Ostseite, Fassade nach Westen
        ("laden", 75.0, 158.0, -math.pi / 2, (70.0, 153.0, 80.0, 163.0)),
    ]
    for _, _, _, _, rc in zentrum:
        belegt.rechtecke.append(rc)
    belegt.rechtecke.append(PLATZ)
    import bahn as BA                                  # Steinbruch + Bahnhof (importieren stadt -> erst hier)
    import steinbruch as SB
    belegt.rechtecke.extend(BA.BELEGT + SB.BELEGT)
    # Haeuser entlang der Strassen
    zaehler = [0]
    for nm in ("Marktring",):
        s = S[nm]
        roh = s["roh"]
        for i in range(len(roh)):
            haeuser_entlang(None, roh[i], roh[(i + 1) % len(roh)], strs, belegt, haeuser, pfade, abstand=15.0, zaehler=zaehler, strasse=s)
    haeuser_entlang(None, S["Hauptstrasse"]["roh"][0], S["Hauptstrasse"]["roh"][1], strs, belegt, haeuser, pfade, abstand=15.0, rand=6.0, zaehler=zaehler, strasse=S["Hauptstrasse"])
    for nm in ("Spange Nord", "Spange Sued"):
        s = S[nm]
        for i in range(len(s["roh"]) - 1):
            haeuser_entlang(None, s["roh"][i], s["roh"][i + 1], strs, belegt, haeuser, pfade, abstand=15.5, rand=13.0, zaehler=zaehler, strasse=s)
    for nm in ("Nordstrasse", "Suedstrasse"):
        s = S[nm]
        a, e = s["roh"]
        haeuser_entlang(None, a, e, strs, belegt, haeuser, pfade, abstand=15.5, rand=14.0, zaehler=zaehler, strasse=s)
    # Dorf um den Kreisverkehr im Norden
    kreis_haeuser(DORF_N, KV_R + KV_B / 2, strs, belegt, haeuser, pfade, n=9, ohne=(-math.pi / 2,), strasse=S["Kreisverkehr Nord"], scheune_idx=3)
    spezial, plaetze = setze_spezial(strs, belegt, haeuser, pfade)
    # Baeume: deterministisch gestreut in den Zonen, nur auf freiem Boden
    baeume = []
    for ix in range(0, 300, 6):
        for iy in range(0, 300, 6):
            h = T._h01(ix, iy, 991)
            if h > 0.42:
                continue
            x = ix + 6 * T._h01(ix, iy, 992)
            y = iy + 6 * T._h01(ix, iy, 993)
            if not any(z0 - 6 <= x <= z2 + 6 and z1 - 6 <= y <= z3 + 6 for z0, z1, z2, z3 in U.STADT_ZONEN):
                continue
            if abs(U.gelaende_hoehe(x, y)) > 0.35 or not belegt.frei(x, y, 2.0, rand=1.5):
                continue
            if any(math.hypot(x - c[0], y - c[1]) < 6.0 for c in baeume):
                continue
            baeume.append((x, y, int(T._h01(ix, iy, 994) * 2)))
    for (x, y, _k) in baeume:
        belegt.kreise.append((x, y, 2.0))
    return {"strs": strs, "S": S, "zentrum": zentrum, "haeuser": haeuser, "pfade": pfade, "baeume": baeume, "belegt": belegt, "spezial": spezial, "plaetze": plaetze}


# ------------------------------------------------------------------ Bau der Objekte
def baue_alles():
    P = plane_stadt()
    # Wege
    w = Bau("stadt_wege")
    for s in P["strs"]:
        U.pfad(w, s["pts"], s["w"], Z_STR, "Strasse", geschlossen=s["zu"])
    x0, y0, x1, y1 = PLATZ
    w.add([(x0, y0, Z_PLATZ), (x1, y0, Z_PLATZ), (x1, y1, Z_PLATZ), (x0, y1, Z_PLATZ)], [(0, 1, 2, 3)], "Pflaster")
    for (px0, py0, px1, py1) in P["plaetze"]:
        w.add([(px0, py0, Z_PLATZ), (px1, py0, Z_PLATZ), (px1, py1, Z_PLATZ), (px0, py1, Z_PLATZ)], [(0, 1, 2, 3)], "Pflaster")
    for a, c in P["pfade"]:
        U.streifen(w, a, c, W_PFAD, Z_PFAD, "Pfad")
    # Gebaeude im Zentrum
    z = Bau("stadt_zentrum")
    for art, x, y, th, _rc in P["zentrum"]:
        {"rathaus": lambda: rathaus(z, x, y, th), "gasthaus": lambda: gasthaus(z, x, y, th), "laden": lambda: laden(z, x, y, th)}[art]()
    brunnen(z, *PLATZ_M)
    for (x, y, th, farbe) in ((46.0, 159.0, 0.0, "Markt rot"), (55.0, 159.0, 0.0, "Markt weiss"), (64.0, 159.0, 0.0, "Markt rot"),
                              (46.0, 141.0, math.pi, "Markt weiss"), (55.0, 141.0, math.pi, "Markt rot"), (64.0, 141.0, math.pi, "Markt weiss")):
        marktstand(z, x, y, th, farbe)
    dorfbrunnen(z, *DORF_N)
    # Haeuser
    h = Bau("stadt_haeuser")
    for H in P["haeuser"]:
        if H.get("scheune"):
            scheune(h, H["x"], H["y"], H["zb"], H["theta"], H["w"], H["d"])
        else:
            haus(h, H["x"], H["y"], H["zb"], H["theta"], H["typ"], seed=H["seed"])
    # Oeffentliche Gebaeude (Feuerwehr, Supermarkt, Post, Kirche)
    import oeffentlich as OE
    oe = Bau("stadt_oeffentlich")
    for sp in P["spezial"]:
        getattr(OE, sp["art"])(oe, sp["x"], sp["y"], sp["zb"], sp["theta"])
    # Baeume
    bm = Bau("stadt_baeume")
    for x, y, k in P["baeume"]:
        baum(bm, x, y, 0.0, k)
    # Teiche
    t = Bau("stadt_teiche")
    for tx, ty, tr in U.TEICHE:
        n = 24
        rr = tr + 1.4
        t.add([(tx + rr * math.cos(2 * math.pi * i / n), ty + rr * math.sin(2 * math.pi * i / n), U.TEICH_Z) for i in range(n)], [tuple(range(n))], "Teichwasser")
    import bahn as BA                                  # Gleise, Bahnhof, Zuege und Steinbruch (steinbruch.py)
    import steinbruch as SB
    return [w, z, h, oe, bm, t] + BA.bauen_bahn() + SB.bauen_bruch()


def bauen():
    """Legt die Stadt in der Szene an (Collection "Stadt"). Rueckgabe: Zahl der Flaechen."""
    coll = T.collection("Stadt")
    nf = 0
    for g in baue_alles():
        namen = []
        for mname in g.m:
            if mname not in namen:
                namen.append(mname)
        mats = [T.material(n, *FARBEN[n]) for n in namen]
        T.add_mesh(coll, g.name, g.v, g.f, mats, [namen.index(mname) for mname in g.m])
        nf += len(g.f)
    return nf


import altbau  # noqa: E402  (Altbau-Bausteine; benutzt stadt.FARBEN)
import rustik  # noqa: E402,F401  (Rathaus/Gasthaus; definiert Materialien)
