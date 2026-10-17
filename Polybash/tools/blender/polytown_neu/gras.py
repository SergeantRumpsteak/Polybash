"""Kleine und hohe 3D-Graeser, Blumen, Farn und Schilf auf allen Grasflaechen der Map - auch auf den Gruenflaechen des Flugplatzes.

Arten (jeweils als Rauschen: Flecken dichter Bestaende, dazwischen Lichtungen):
  * Kurzgras: Buschel aus drei dreiseitigen Halmspitzen, 12..40 cm.
  * Hohes Gras: 7 geneigte Halme, 50..120 cm, mit Samenstand (nicht am Flugplatz in Pistennaehe).
  * Pfeifengras: dichter Horst aus 9 ueberhaengenden Halmen, 70..130 cm.
  * Blumen (weiss, gelb, violett, rosa): Stiel und sechseckige Bluete, 25..55 cm.
  * Farn: Faecher aus 6 Wedeln in Waldnaehe und an Huegeln; Schilf/Rohrkolben an den Teichen (1,2..2 m).
Nicht gewachsen wird auf Strassen, Wegen, Plaetzen, in/an Gebaeuden, Hoefen, Feldern, im Steinbruch, im Burgumfeld nur auf Graben, Bruecken und Ringweg (die Wiese zwischen Festung und Kreisstrasse waechst zu), an den Gleisen und auf
dem Burgplateau. Am Flugplatz wachsen sie dort, wo kein Belag, keine Halle, kein Zaun usw. ist (Raster aus allen Flaechen der Umgebung); die Halme
sind kein Hindernis."""
import math

import burg as B
import stadt as S
import talkessel as T
import umgebung as U
from burg import Bau

S.FARBEN.update({"Gras 1": ((0.27, 0.44, 0.15), 1.0, 0.0), "Gras 2": ((0.36, 0.52, 0.19), 1.0, 0.0), "Gras 3": ((0.21, 0.37, 0.13), 1.0, 0.0),
                 "Gras trocken": ((0.52, 0.52, 0.26), 1.0, 0.0), "Gras hoch 1": ((0.40, 0.52, 0.20), 1.0, 0.0), "Gras hoch 2": ((0.55, 0.58, 0.28), 1.0, 0.0),
                 "Gras hoch 3": ((0.30, 0.45, 0.17), 1.0, 0.0), "Samen": ((0.72, 0.62, 0.34), 1.0, 0.0), "Pfeifengras": ((0.46, 0.50, 0.22), 1.0, 0.0),
                 "Bluete weiss": ((0.92, 0.92, 0.86), 0.9, 0.0), "Bluete gelb": ((0.93, 0.78, 0.15), 0.9, 0.0), "Bluete violett": ((0.55, 0.32, 0.72), 0.9, 0.0),
                 "Bluete rosa": ((0.88, 0.45, 0.58), 0.9, 0.0), "Stiel": ((0.25, 0.42, 0.15), 1.0, 0.0), "Farn": ((0.22, 0.34, 0.14), 1.0, 0.0),
                 "Schilf": ((0.50, 0.56, 0.28), 1.0, 0.0), "Rohrkolben": ((0.30, 0.18, 0.10), 1.0, 0.0)})
RASTER = 1.8
_MASKE = {}


def _flug_raster():
    """Belegte 1-m-Zellen im Flugplatzgebiet: alle Flaechen/Quader der Umgebung (Belag, Hallen, Tower, Zaun ...) samt Rand."""
    if "flug" in _MASKE:
        return _MASKE["flug"]
    belegt = set()
    for g in U.baue_alles():
        if g.name == "umgebung_wege":                                                    # Wege: ueber Abstandspruefung (Mittellinien)
            continue
        for f in g.f:
            vs = [g.v[i] for i in f]
            if min(v[2] for v in vs) > 0.8:
                continue
            x0, x1 = min(v[0] for v in vs), max(v[0] for v in vs)
            y0, y1 = min(v[1] for v in vs), max(v[1] for v in vs)
            if x1 < 195.0 or x0 > 300.0:
                continue
            m = 1.2
            for ix in range(int(x0 - m), int(x1 + m) + 1):
                for iy in range(int(y0 - m), int(y1 + m) + 1):
                    belegt.add((ix, iy))
    _MASKE["flug"] = belegt
    return belegt


GRUPPEN = []                  # alle fertigen Baugruppen (von stadt.baue_alles gesetzt): Grundlage fuer den Belag-Raster der Grosszonen
GROSSZONE = 700.0             # Rechtecke ab dieser Flaeche sind Zonen (Bahnhof, Steinbruch, Hof ...), keine Gebaeude: dort zaehlt nur echter Belag
_ZONEN_AUS = ((40.0, 135.0, 70.0, 165.0),)                               # Marktplatz: gepflastert, bleibt gesperrt


def _grosszonen(P):
    return [r for r in P["belegt"].rechtecke if (r[2] - r[0]) * (r[3] - r[1]) >= GROSSZONE and tuple(r) not in _ZONEN_AUS]


def _belag_raster(P):
    """0,5-m-Zellen in den Grosszonen, die von echter Geometrie belegt sind (Flaechen/Waende/Quader knapp ueber dem Boden, Grube/Loecher)."""
    key = ("belag", id(P))
    if key in _MASKE:
        return _MASKE[key]
    zonen = _grosszonen(P)
    belegt = set()
    Q = 0.5

    def in_zone(x0, y0, x1, y1):
        return any(x0 < r[2] and x1 > r[0] and y0 < r[3] and y1 > r[1] for r in zonen)

    for g in GRUPPEN:
        if g.name in ("gras", "wald", "laternen") or g.name.startswith("grenze"):
            continue
        v = g.v
        for f in g.f:
            vs = [v[i] for i in f]
            x0, x1 = min(p[0] for p in vs), max(p[0] for p in vs)
            y0, y1 = min(p[1] for p in vs), max(p[1] for p in vs)
            if not in_zone(x0, y0, x1, y1):
                continue
            zmin = min(p[2] for p in vs)
            if zmin > U.gelaende_hoehe((x0 + x1) / 2, (y0 + y1) / 2) + 1.0 and zmin > 1.5:
                continue
            # flache Polygone (Belag): Zellmitten im Polygon; steile/duenne (Waende, Pfosten): Bounding Box
            n = len(vs)
            area = 0.0
            for k in range(n):
                area += vs[k][0] * vs[(k + 1) % n][1] - vs[(k + 1) % n][0] * vs[k][1]
            area = abs(area) / 2
            ix0, ix1, iy0, iy1 = int(x0 / Q), int(x1 / Q), int(y0 / Q), int(y1 / Q)
            if area < 0.02 or (ix1 - ix0 + 1) * (iy1 - iy0 + 1) <= 4:
                for ix in range(ix0, ix1 + 1):
                    for iy in range(iy0, iy1 + 1):
                        belegt.add((ix, iy))
                continue
            for ix in range(ix0, ix1 + 1):
                px = (ix + 0.5) * Q
                for iy in range(iy0, iy1 + 1):
                    py = (iy + 0.5) * Q
                    ins = False
                    j = n - 1
                    for k in range(n):
                        if (vs[k][1] > py) != (vs[j][1] > py) and px < (vs[j][0] - vs[k][0]) * (py - vs[k][1]) / (vs[j][1] - vs[k][1]) + vs[k][0]:
                            ins = not ins
                        j = k
                    if ins:
                        belegt.add((ix, iy))
    _MASKE[key] = belegt
    return belegt


class Maske:
    """Entscheidet, ob (x, y) Grasflaeche ist (fuer Gras und Baeume)."""

    def __init__(self, P):
        import ruine as RU
        self.P = P
        self.strs = P["strs"]
        self.aussen = list(U.strassen_achsen()) + [(a, c) for a, c in zip(RU.WEG, RU.WEG[1:])]
        um = U.rund(U.UMFAHRUNG, U.RC, geschlossen=True)
        self.aussen += [(um[i], um[(i + 1) % len(um)]) for i in range(len(um))]
        self.flug = _flug_raster()
        self.haus_kreise = {(round(h["x"], 3), round(h["y"], 3)) for h in P["haeuser"]}
        self.haus_rechtecke = [(h["x"], h["y"], math.cos(h["theta"]), math.sin(h["theta"]), h["w"] / 2, h["d"] / 2) for h in P["haeuser"]]
        self.zonen = _grosszonen(P)

    def _burg_gras(self, x, y):
        """Gras im Burgumfeld nur dort, wo wirklich Wiese ist: nicht in der Burg, im Graben samt Boeschung, auf den Bruecken-Zufahrten und dem Ringweg."""
        dx, dy = abs(x - U.C), abs(y - U.C)
        if max(dx, dy) > 70.0:
            return True
        o = math.hypot(max(dx - B.A, 0.0), max(dy - B.A, 0.0))                      # Abstand zum Burgquadrat (wie burg.graben_tiefe)
        if o < B.GRABEN[3] + 1.2:
            return False
        if dx < 5.6 and dy < B.A + 12.0:                                              # Bruecken und ihre Zufahrten
            return False
        return abs(math.hypot(x - U.C, y - U.C) - U.ring_r(math.atan2(y - U.C, x - U.C))) > U.BREITE_WEG / 2 + 0.7

    @property
    def belag(self):
        return _belag_raster(self.P) if GRUPPEN else set()

    def im_flug(self, x, y):
        return x >= 200.0 and 46.0 <= y <= 254.0

    def grund(self, x, y, flug_gras=True, baum=False):
        """Grund, warum (x, y) keine Grasflaeche ist (None = Grasflaeche)."""
        P = self.P
        if not (1.0 < x < 299.0 and 1.0 < y < 299.0):
            return 'rand'
        if baum and math.hypot(x - U.C, y - U.C) < 63.0:                                 # Baeume: nicht rund um die Burg und den Ringweg
            return 'baum_burg'
        if not self._burg_gras(x, y):
            return 'burg'
        if 19.0 < y < 35.0 and x > 84.0:                                                  # Gleiskorridor
            return 'gleis'
        if math.hypot(x - U.RUINE[0], y - U.RUINE[1]) < 15.5:                            # Burgplateau
            return 'ruine'
        if baum:                                                                          # Baeume: nur der eingezaeunte Flugplatz ist tabu (Wald reicht bis an den Zaun)
            gx0, gy0, gx1, gy1 = U.ZAUN
            if gx0 - 3.0 < x and gy0 - 2.5 < y < gy1 + 2.5:
                return 'baum_flug'
        elif self.im_flug(x, y):
            if not flug_gras or (int(x), int(y)) in self.flug:
                return 'flug'
        b = P["belegt"]
        for (x0, y0, x1, y1) in b.rechtecke:
            if x0 - 0.5 < x < x1 + 0.5 and y0 - 0.5 < y < y1 + 0.5:
                if not baum and (x1 - x0) * (y1 - y0) >= GROSSZONE and tuple((x0, y0, x1, y1)) not in _ZONEN_AUS and self.belag:
                    if (int(x / 0.5), int(y / 0.5)) in self.belag or U.gelaende_hoehe(x, y) < -0.4:
                        return 'belag'
                    continue
                return 'rechtecke'
        for (cx, cy, r) in b.kreise:
            if math.hypot(x - cx, y - cy) < r + 0.3 and (round(cx, 3), round(cy, 3)) not in self.haus_kreise:
                return 'kreise'
        for (hx, hy, c, sn, w2, d2) in self.haus_rechtecke:                               # Haeuser: nur der echte Grundriss samt Stufen (nicht der Sicherheitskreis)
            if abs(x - hx) < 12.0 and abs(y - hy) < 12.0:
                dx, dy = x - hx, y - hy
                lx, ly = dx * c + dy * sn, -dx * sn + dy * c
                if abs(lx) < w2 + 0.9 and -d2 - 1.8 < ly < d2 + 0.9:
                    return 'haus'
        for (x0, y0, x1, y1) in P["plaetze"]:
            if x0 - 0.5 < x < x1 + 0.5 and y0 - 0.5 < y < y1 + 0.5:
                return 'plaetze'
        for tx, ty, tr in U.TEICHE:
            if math.hypot(x - tx, y - ty) < tr + 1.2:
                return 'teich'
        if S.strassenabstand(x, y, self.strs) < 0.6:
            return 'strasse'
        for a, c in P["pfade"]:
            if U._seg_abstand(x, y, a, c) < 1.4:
                return 'pfad'
        for a, c in self.aussen:
            if U._seg_abstand(x, y, a, c) < U.BREITE_WEG / 2 + 0.6:
                return 'aussen'
        return None

    def ok(self, x, y, flug_gras=True, baum=False):
        return self.grund(x, y, flug_gras, baum) is None

    def pistennah(self, x, y):
        """Abstand zum Belag am Flugplatz < 4 m (dort nur Kurzgras)."""
        if not self.im_flug(x, y):
            return False
        for dx in (-4, 0, 4):
            for dy in (-4, 0, 4):
                if (int(x) + dx, int(y) + dy) in self.flug:
                    return True
        return False


def maske(P):
    if _MASKE.get("P") is not P:
        _MASKE["P"], _MASKE["m"] = P, Maske(P)
    return _MASKE["m"]


def _spitze(b, x, y, z0, h, lean, r, ph, mat):
    base = [(x + r * math.cos(ph + 2.094 * k), y + r * math.sin(ph + 2.094 * k), z0) for k in range(3)]
    b.add(base + [(x + lean[0], y + lean[1], z0 + h)], [(0, 1, 3), (1, 2, 3), (2, 0, 3)], mat)


def _kurz(b, x, y, z0, ix, iy):
    t = T._h01(ix, iy, 5004)
    mat = "Gras 1" if t < 0.4 else ("Gras 2" if t < 0.72 else ("Gras 3" if t < 0.93 else "Gras trocken"))
    hs = 0.12 + 0.28 * T.noise(x / 6.0, y / 6.0, T.SEED + 403) + 0.1 * T._h01(ix, iy, 5005)
    ph = T._h01(ix, iy, 5006) * 6.28
    for k in range(3):
        ox, oy = 0.1 * math.cos(ph + 2.1 * k), 0.1 * math.sin(ph + 2.1 * k)
        lean = (0.07 * math.cos(ph + 1.7 * k + 0.5) + 0.03, 0.07 * math.sin(ph + 1.7 * k + 0.5))
        _spitze(b, x + ox, y + oy, z0, hs * (1.0 - 0.18 * k), lean, 0.035, ph + k, mat)


def _hoch(b, x, y, z0, ix, iy):
    ph = T._h01(ix, iy, 5010) * 6.28
    t = T._h01(ix, iy, 5011)
    mat = "Gras hoch 1" if t < 0.4 else ("Gras hoch 2" if t < 0.7 else "Gras hoch 3")
    hs = 0.5 + 0.7 * T.noise(x / 9.0, y / 9.0, T.SEED + 411)
    for k in range(7):
        a = ph + 0.9 * k
        r = 0.12 + 0.05 * (k % 3)
        ox, oy = r * math.cos(a), r * math.sin(a)
        h = hs * (0.7 + 0.3 * ((k * 37) % 10) / 10.0)
        lean = (0.22 * math.cos(a + 0.4) * h, 0.22 * math.sin(a + 0.4) * h)
        _spitze(b, x + ox, y + oy, z0, h, lean, 0.03, a, mat)
        if k % 2 == 0:                                                                    # Samenstand
            tx, ty = x + ox + lean[0] * 0.92, y + oy + lean[1] * 0.92
            _spitze(b, tx, ty, z0 + h * 0.8, h * 0.28, (lean[0] * 0.2, lean[1] * 0.2), 0.045, a, "Samen")


def _horst(b, x, y, z0, ix, iy):
    ph = T._h01(ix, iy, 5020) * 6.28
    hs = 0.7 + 0.6 * T._h01(ix, iy, 5021)
    for k in range(9):
        a = ph + 0.7 * k
        r = 0.05 + 0.06 * (k % 3)
        lean = (0.38 * hs * math.cos(a), 0.38 * hs * math.sin(a))
        _spitze(b, x + r * math.cos(a), y + r * math.sin(a), z0, hs * (0.8 + 0.2 * (k % 2)), lean, 0.032, a, "Pfeifengras" if k % 4 else "Gras hoch 2")


def _blume(b, x, y, z0, ix, iy):
    h = 0.25 + 0.3 * T._h01(ix, iy, 5030)
    ph = T._h01(ix, iy, 5031) * 6.28
    t = T._h01(ix, iy, 5032)
    mat = "Bluete weiss" if t < 0.3 else ("Bluete gelb" if t < 0.6 else ("Bluete violett" if t < 0.82 else "Bluete rosa"))
    lx, ly = 0.05 * math.cos(ph), 0.05 * math.sin(ph)
    _spitze(b, x, y, z0, h, (lx, ly), 0.012, ph, "Stiel")
    cx, cy, cz = x + lx, y + ly, z0 + h
    n = 6
    ring = [(cx + 0.065 * math.cos(ph + 2 * math.pi * k / n), cy + 0.065 * math.sin(ph + 2 * math.pi * k / n), cz) for k in range(n)]
    b.add(ring + [(cx, cy, cz + 0.035)], [(k, (k + 1) % n, n) for k in range(n)], mat)


def _farn(b, x, y, z0, ix, iy):
    ph = T._h01(ix, iy, 5040) * 6.28
    hs = 0.35 + 0.35 * T._h01(ix, iy, 5041)
    for k in range(6):
        a = ph + 1.05 * k
        ex, ey = x + 0.55 * hs * math.cos(a) * 1.6, y + 0.55 * hs * math.sin(a) * 1.6
        mx, my = x + 0.3 * math.cos(a) * hs * 1.6, y + 0.3 * math.sin(a) * hs * 1.6
        px, py = -math.sin(a) * 0.09, math.cos(a) * 0.09
        b.add([(x, y, z0), (mx + px, my + py, z0 + hs * 0.85), (mx - px, my - py, z0 + hs * 0.85), (ex, ey, z0 + hs * 0.35)],
              [(0, 1, 3), (0, 3, 2), (0, 2, 1), (1, 2, 3)], "Farn")


def _schilf(b, x, y, z0, ix, iy):
    ph = T._h01(ix, iy, 5050) * 6.28
    for k in range(5):
        a = ph + 1.3 * k
        h = 1.2 + 0.8 * T._h01(ix, iy + k, 5051)
        ox, oy = 0.12 * math.cos(a), 0.12 * math.sin(a)
        lean = (0.12 * math.cos(a + 0.7), 0.12 * math.sin(a + 0.7))
        _spitze(b, x + ox, y + oy, z0, h, lean, 0.03, a, "Schilf")
        if k % 2 == 0:                                                                    # Rohrkolben
            tx, ty = x + ox + lean[0] * 0.85, y + oy + lean[1] * 0.85
            b.prism(tx, ty, z0 + h * 0.74, 0.045, 0.28, 5, "Rohrkolben")


def bauen_gras(P):
    M = maske(P)
    b = Bau("gras")
    n = int(300.0 / RASTER)
    for ix in range(n):
        for iy in range(n):
            x = ix * RASTER + T._h01(ix, iy, 5001) * RASTER
            y = iy * RASTER + T._h01(ix, iy, 5002) * RASTER
            fl = T.fbm(x / 11.0, y / 11.0, T.SEED + 401, 3)                              # Flecken
            dichte = 0.08 + 0.85 * B.smoothstep(0.38, 0.62, fl)
            if T._h01(ix, iy, 5003) > dichte:
                continue
            if not M.ok(x, y):
                continue
            z0 = U.gelaende_hoehe(x, y) - 0.02
            # Art nach Rauschfeldern: hohe Gras-Flecken, Bluetenwiesen, Pfeifengras-Horste
            hoch = T.fbm(x / 13.0, y / 13.0, T.SEED + 421, 2)
            blum = T.fbm(x / 9.0, y / 9.0, T.SEED + 431, 2)
            r = T._h01(ix, iy, 5060)
            nah = M.pistennah(x, y)
            if not nah and hoch > 0.58 and r < 0.8:
                (_horst if r < 0.12 else _hoch)(b, x, y, z0, ix, iy)
            elif blum > 0.6 and r < 0.55:
                _blume(b, x, y, z0, ix, iy)
                if r < 0.2:
                    _kurz(b, x + 0.3, y + 0.2, z0, ix, iy)
            else:
                _kurz(b, x, y, z0, ix, iy)
    # Farn: im Unterholz der Waldflaechen und an Huegelkuppen; Schilf: an den Teichen
    import wald as W
    for (tx, ty, _k) in W.alle_baeume(P):
        if T._h01(int(tx * 3), int(ty * 3), 5070) < 0.22:
            fx, fy = tx + 1.6 * math.cos(tx * 7.0), ty + 1.6 * math.sin(ty * 5.0)
            if M.ok(fx, fy, flug_gras=False):
                _farn(b, fx, fy, U.gelaende_hoehe(fx, fy) - 0.02, int(fx * 3), int(fy * 3))
    for tx, ty, tr in U.TEICHE:
        for k in range(int(tr * 3.2)):
            a = 2 * math.pi * T._h01(k, int(tx), 5080)
            rr = tr + 1.5 + 2.2 * T._h01(k, int(ty), 5081)
            sx, sy = tx + rr * math.cos(a), ty + rr * math.sin(a)
            if M.ok(sx, sy, flug_gras=False) and T._h01(k, int(tx + ty), 5082) < 0.7:
                _schilf(b, sx, sy, U.gelaende_hoehe(sx, sy) - 0.02, k, int(tx))
    return b
