"""Polybash - Burg (Radarstation) in der Mitte des Talkessels.

Nachbau der Burg aus der Standardkarte (spiel.py bleibt unveraendert): quadratische Betonburg 44 x 44 m mit zwei Toren
(Nord, Ssued) samt Wachhaeusern und Schranken, Ecktuerme, Bergfried mit Radarschuessel, zwei Flak-Geschuetzen auf den
Tuermen NW und SO, zwei Freya-Antennen auf den Tuermen SW und NO, Kasematten, Wassergraben mit zwei Bruecken (Nord, Sued) vor den beiden Toren.
West- und Ostmauer haben keinen Eingang und damit auch keinen Uebergang ueber den Graben.

Dieses Modul wird von polytown_neu.py benutzt; einzeln ausfuehren geht nicht (es braucht das Tal darunter).
Alle Masse in Metern; die Burg steht auf der ebenen Wiese bei z = 0 mit der Mitte bei (150, 150).
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bpy  # noqa: E402
import talkessel as T  # noqa: E402

# ------------------------------------------------------------------ Masse (wie in spiel.py)
C = T.TAL / 2.0
H = 22.0                       # Mitte bis Aussenkante der Mauer
TD = 3.0                       # Mauerdicke
ZW = 5.0                       # Hoehe der Mauer (Wehrgang)
ZT = 8.0                       # Hoehe der Ecktuerme
PW = 0.6                       # Dicke der Bruestung
G = 4.0                        # halbe Torbreite
A = 25.5                       # Graben um das Quadrat C +- A (Aussenkante der Tuerme)
GRABEN = (0.8, 4.4, 6.0, 9.5, 2.0)   # Abstaende o0..o3 vom Quadrat und Tiefe (m)
WASSER = -1.2                  # Wasserspiegel
PATCH = 40.0                   # Halbe Kantenlaenge des Burggelaendes (Quadrat um die Mitte)
RASTER = 1.0                   # Gitterweite des Burggelaendes
LOCH = (C - PATCH, C - PATCH, C + PATCH, C + PATCH)   # hier ist die Wiese ausgespart
DAEMME = []                    # keine Daemme: die Burg hat nur das Nord- und das Suedtor (je mit Bruecke)

# Materialien: Name -> (Farbe, Rauheit, Leuchten)
FARBEN = {
    "Beton hell":    ((0.64, 0.62, 0.57), 0.95, 0.0),
    "Beton dunkel":  ((0.52, 0.50, 0.46), 0.95, 0.0),
    "Mauerwerk":       ((0.64, 0.62, 0.57), 0.95, 0.0),   # Mauern, Tuerme, Wachhaeuser (hier kommt die Steintextur drauf)
    "Mauerwerk dunkel": ((0.52, 0.50, 0.46), 0.95, 0.0),  # Sockel, Pfeiler, Bruestungen daran
    "Beton grau":    ((0.55, 0.55, 0.57), 0.95, 0.0),
    "Brueckenbeton": ((0.47, 0.47, 0.49), 0.95, 0.0),
    "Bruestung":     ((0.64, 0.63, 0.60), 0.95, 0.0),
    "Hof":           ((0.50, 0.50, 0.52), 0.95, 0.0),
    "Stufen":        ((0.44, 0.42, 0.40), 0.95, 0.0),
    "Stahl":         ((0.36, 0.40, 0.34), 0.55, 0.0),
    "Metall":        ((0.30, 0.32, 0.30), 0.5, 0.0),
    "Metall hell":   ((0.55, 0.57, 0.58), 0.5, 0.0),
    "Oliv":          ((0.36, 0.40, 0.28), 0.8, 0.0),
    "Fenster":       ((0.07, 0.09, 0.11), 0.2, 0.0),
    "Rahmen":        ((0.84, 0.83, 0.78), 0.9, 0.0),
    "Rot":           ((0.80, 0.12, 0.10), 0.7, 0.0),
    "Weiss":         ((0.90, 0.90, 0.86), 0.7, 0.0),
    "Draht":         ((0.16, 0.16, 0.17), 0.6, 0.0),
    "Fahrbahn":      ((0.33, 0.33, 0.34), 0.95, 0.0),
    "Markierung":    ((0.90, 0.90, 0.80), 0.9, 0.0),
    "Radar innen":   ((0.80, 0.82, 0.84), 0.45, 0.0),
    "Radar aussen":  ((0.55, 0.57, 0.59), 0.5, 0.0),
    "Radar Rand":    ((0.36, 0.38, 0.40), 0.5, 0.0),
    "Fahne gelb":    ((0.55, 0.45, 0.20), 0.9, 0.0),
    "Fahne weiss":   ((0.85, 0.84, 0.78), 0.9, 0.0),
    "Fahne oliv":    ((0.36, 0.40, 0.28), 0.9, 0.0),
    "Lampe":         ((1.00, 0.90, 0.65), 0.4, 6.0),
    "Wasser":        ((0.10, 0.34, 0.58), 0.1, 0.0),
    "Schlamm":       ((0.33, 0.28, 0.20), 0.95, 0.0),
    "Boeschung":     ((0.27, 0.43, 0.19), 0.95, 0.0),
}


# ------------------------------------------------------------------ Geometrie (ohne bpy)
BOX_FACES = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]


def _norm(v):
    l = math.sqrt(sum(k * k for k in v)) or 1.0
    return tuple(k / l for k in v)


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


class Bau:
    """Sammelt Quader, Balken und Dreiecke in einem Mesh; jede Flaeche merkt sich ihr Material (Name)."""

    def __init__(self, name):
        self.name = name
        self.v, self.f, self.m = [], [], []
        self.bx = []                  # achsenparallele Quader (x0, y0, z0, x1, y1, z1) - fuer Pruefungen

    def add(self, verts, faces, mat):
        o = len(self.v)
        self.v.extend(verts)
        for fc in faces:
            self.f.append(tuple(i + o for i in fc))
            self.m.append(mat)

    def box(self, x0, y0, z0, x1, y1, z1, mat):
        x0, x1 = min(x0, x1), max(x0, x1)
        y0, y1 = min(y0, y1), max(y0, y1)
        z0, z1 = min(z0, z1), max(z0, z1)
        if x1 - x0 < 1e-6 or y1 - y0 < 1e-6 or z1 - z0 < 1e-6:
            return
        v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
             (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
        self.add(v, BOX_FACES, mat)
        self.bx.append((x0, y0, z0, x1, y1, z1))

    def cbox(self, cx, cy, cz, dx, dy, dz, mat):
        """Quader um den Mittelpunkt (cx, cy, cz) mit den Massen dx, dy, dz."""
        self.box(cx - dx / 2, cy - dy / 2, cz - dz / 2, cx + dx / 2, cy + dy / 2, cz + dz / 2, mat)

    def beam(self, a, b, w, h, mat, up=(0.0, 0.0, 1.0)):
        """Balken mit Querschnitt w x h von Punkt a nach Punkt b."""
        d = _norm(tuple(b[i] - a[i] for i in range(3)))
        if abs(_dot(d, up)) > 0.98:
            up = (1.0, 0.0, 0.0) if abs(d[0]) < 0.9 else (0.0, 1.0, 0.0)
        u = _norm(_cross(up, d))
        v = _cross(d, u)
        ring = lambda p: [tuple(p[i] + u[i] * sx * w / 2 + v[i] * sy * h / 2 for i in range(3))
                          for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        self.add(ring(a) + ring(b), BOX_FACES, mat)

    def prism(self, cx, cy, z0, r, hoehe, n, mat):
        """Senkrechte n-Eck-Saeule (Rohre, Scheinwerfer)."""
        bot = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n), z0) for k in range(n)]
        top = [(p[0], p[1], z0 + hoehe) for p in bot]
        faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))]
        faces += [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
        self.add(bot + top, faces, mat)

    def tri_zu(self, a, b, c, ref, mat):
        """Dreieck, dessen Normale zum Punkt ref zeigt."""
        n = _cross(tuple(b[i] - a[i] for i in range(3)), tuple(c[i] - a[i] for i in range(3)))
        mid = tuple((a[i] + b[i] + c[i]) / 3 for i in range(3))
        if _dot(n, tuple(ref[i] - mid[i] for i in range(3))) < 0:
            b, c = c, b
        self.add([a, b, c], [(0, 1, 2)], mat)

    def merge(self, other, ox=0.0, oy=0.0, oz=0.0, rot=0.0):
        """Fuegt other ein, um rot Grad um z gedreht und nach (ox, oy, oz) verschoben."""
        cs, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
        o = len(self.v)
        self.v.extend((ox + x * cs - y * sn, oy + x * sn + y * cs, oz + z) for x, y, z in other.v)
        self.f.extend(tuple(i + o for i in fc) for fc in other.f)
        self.m.extend(other.m)


def treppe(b, x, y, d, n, w, base, mat="Stufen", sh=0.5, sd=0.8):
    """Treppe aus n Stufen (Hoehe sh, Tiefe sd, Breite w) wie im Spiel; (x, y) = Ecke der untersten Stufe."""
    z0 = 0.0 if base == 0 else base
    for i in range(n):
        top = base + (i + 1) * sh
        if d == "N":
            b.box(x, y + i * sd, z0, x + w, y + (i + 1) * sd, top, mat)
        elif d == "S":
            b.box(x, y - (i + 1) * sd, z0, x + w, y - i * sd, top, mat)
        elif d == "E":
            b.box(x + i * sd, y, z0, x + (i + 1) * sd, y + w, top, mat)
        else:
            b.box(x - (i + 1) * sd, y, z0, x - i * sd, y + w, top, mat)


def fenster(b, cx, cy, zc, w, h, nx, ny, tiefe=0.05):
    """Fenster in einer Aussenwand: dunkle Scheibe, weisser Rahmen mit Kreuz; (nx, ny) zeigt aus der Wand heraus.
    (cx, cy) liegt auf der Wandoberflaeche."""
    def leiste(dw, dh, off_w, off_h, dt):
        if ny:
            b.box(cx + off_w - dw / 2, cy, zc + off_h - dh / 2, cx + off_w + dw / 2, cy + ny * dt, zc + off_h + dh / 2, "Rahmen")
        else:
            b.box(cx, cy + off_w - dw / 2, zc + off_h - dh / 2, cx + nx * dt, cy + off_w + dw / 2, zc + off_h + dh / 2, "Rahmen")
    if ny:
        b.box(cx - w / 2, cy, zc - h / 2, cx + w / 2, cy + ny * 0.02, zc + h / 2, "Fenster")
    else:
        b.box(cx, cy - w / 2, zc - h / 2, cx + nx * 0.02, cy + w / 2, zc + h / 2, "Fenster")
    r = 0.07
    leiste(w + 2 * r, r, 0.0, h / 2 + r / 2, 0.07)      # oben
    leiste(w + 2 * r, r, 0.0, -h / 2 - r / 2, 0.07)     # unten
    leiste(r, h, -w / 2 - r / 2, 0.0, 0.07)             # links
    leiste(r, h, w / 2 + r / 2, 0.0, 0.07)              # rechts
    leiste(r * 0.7, h, 0.0, 0.0, 0.05)                  # Mittelsprosse


def fahne(b, x, y, z, h, mat, w=2.0, hh=1.2, ang=0.0):
    """Fahnenmast (z = Fuss, h = Hoehe) mit einer Fahne, die vom Mast aus nach +x (um ang gedreht) weht."""
    b.box(x - 0.08, y - 0.08, z, x + 0.08, y + 0.08, z + h, "Metall")
    f = Bau("fahne")
    f.box(0.08, -0.015, -hh, 0.08 + w, 0.015, 0.0, mat)
    b.merge(f, x, y, z + h - 0.1, ang)
    cs, sn = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    ecken = [(x + px * cs - py * sn, y + px * sn + py * cs) for px, py in ((0.08, -0.015), (0.08 + w, -0.015), (0.08 + w, 0.015), (0.08, 0.015))]
    b.bx.append((min(e[0] for e in ecken), min(e[1] for e in ecken), z + h - 0.1 - hh,
                 max(e[0] for e in ecken), max(e[1] for e in ecken), z + h - 0.1))


# ------------------------------------------------------------------ Teile der Burg
def mauern(b):
    x0, x1, y0, y1 = C - H, C + H, C - H, C + H
    g0, g1 = C - G, C + G
    for a, bb, c, d in ((x0, y0, g0, y0 + TD), (g1, y0, x1, y0 + TD), (x0, y1 - TD, g0, y1), (g1, y1 - TD, x1, y1),
                        (x0, y0, x0 + TD, y1), (x1 - TD, y0, x1, y1)):
        b.box(a, bb, 0.0, c, d, ZW, "Mauerwerk")                       # Mauern mit Wehrgang
    for a, bb, c, d in ((x0, y0, g0, y0 + PW), (g1, y0, x1, y0 + PW), (x0, y1 - PW, g0, y1), (g1, y1 - PW, x1, y1),
                        (x0, y0, x0 + PW, y1), (x1 - PW, y0, x1, y1)):
        b.box(a, bb, ZW, c, d, ZW + 1.2, "Mauerwerk dunkel")                # Bruestung aussen
    # Fassade: Sockel, Gesims, Fugen, Schlitzfenster, Pfeiler, Stacheldraht
    walls = [("S", C - H, [(C - H, g0), (g1, C + H)]), ("N", C + H, [(C - H, g0), (g1, C + H)]),
             ("W", C - H, [(C - H, C + H)]), ("E", C + H, [(C - H, C + H)])]
    for s, pos, spans in walls:
        nrm = {"S": (0, -1), "N": (0, 1), "W": (-1, 0), "E": (1, 0)}[s]
        for a0, a1 in spans:
            L = a1 - a0

            def wb(c0, c1, z0, z1, o0, o1, mat):
                if s in "NS":
                    b.box(c0, pos + nrm[1] * o0, z0, c1, pos + nrm[1] * o1, z1, mat)
                else:
                    b.box(pos + nrm[0] * o0, c0, z0, pos + nrm[0] * o1, c1, z1, mat)

            wb(a0, a1, 0.0, 1.0, 0.0, 0.2, "Mauerwerk dunkel")                       # Sockel
            wb(a0, a1, ZW - 0.35, ZW, 0.0, 0.22, "Mauerwerk")                   # Kranzgesims
            ns = max(2, int(L // 4.0))
            for k in range(1, ns):                                               # Dehnungsfugen
                cc = a0 + L * k / ns
                wb(cc - 0.04, cc + 0.04, 1.0, ZW - 0.35, 0.0, 0.03, "Draht")
            for k in range(ns):                                                  # liegende Schlitzfenster
                cc = a0 + L * (k + 0.5) / ns
                wb(cc - 0.8, cc + 0.8, 2.45, 2.9, 0.0, 0.02, "Mauerwerk")
                wb(cc - 0.7, cc + 0.7, 2.5, 2.85, 0.0, 0.04, "Fenster")
            for k in range(0, ns + 1):                                           # Pfeiler
                cc = a0 + L * k / ns
                if k in (0, ns) and s in "NS" and (a0 == C - H and k == 0 or a1 == C + H and k == ns):
                    continue
                wb(cc - 0.3, cc + 0.3, 0.0, ZW - 0.35, 0.0, 0.4, "Mauerwerk dunkel")
            # Stacheldraht auf der Bruestung: Pfosten mit Y-Arm und drei Draehte
            zt_ = ZW + 1.2
            nposts = max(2, int(L // 2.0))
            for k in range(nposts + 1):
                cc = a0 + L * k / nposts
                wb(cc - 0.04, cc + 0.04, zt_, zt_ + 0.95, -0.35, -0.27, "Draht")
                wb(cc - 0.04, cc + 0.04, zt_ + 0.95, zt_ + 1.15, -0.15, -0.05, "Draht")
            for zz in (zt_ + 0.4, zt_ + 0.7, zt_ + 1.0):
                wb(a0, a1, zz, zz + 0.03, -0.32, -0.29, "Draht")
            wb(a0, a1, zt_ + 1.1, zt_ + 1.13, -0.12, -0.08, "Draht")


def ecktuerme(b):
    n, sd = 6, 0.7
    for sx in (-1, 1):
        for sy in (-1, 1):
            tx, ty = C + sx * H, C + sy * H
            b.box(tx - 3.5, ty - 3.5, 0.0, tx + 3.5, ty + 3.5, ZT, "Mauerwerk")                 # Turm
            ex, ey = tx + sx * 3.5, ty + sy * 3.5
            b.box(min(ex, ex - sx * PW), ty - 3.5, ZT, max(ex, ex - sx * PW), ty + 3.5, ZT + 1.2, "Mauerwerk dunkel")
            b.box(tx - 3.5, min(ey, ey - sy * PW), ZT, tx + 3.5, max(ey, ey - sy * PW), ZT + 1.2, "Mauerwerk dunkel")
            fx, fy = tx - sx * 3.5, ty - sy * 3.5                    # Innenkanten des Turms
            wy = (C - H + PW) if sy < 0 else (C + H - TD)            # Wehrgang der Nord/Sued-Mauer
            wxx = (C - H + PW) if sx < 0 else (C + H - TD)           # Wehrgang der West/Ost-Mauer
            if sx < 0:
                treppe(b, fx + n * sd, wy, "W", n, TD - PW, ZW, sd=sd)
            else:
                treppe(b, fx - n * sd, wy, "E", n, TD - PW, ZW, sd=sd)
            if sy < 0:
                treppe(b, wxx, fy + n * sd, "S", n, TD - PW, ZW, sd=sd)
            else:
                treppe(b, wxx, fy - n * sd, "N", n, TD - PW, ZW, sd=sd)
            # Bunkerturm: Schlitzbaender an den beiden Aussenseiten, Dachrand
            for side in ((sx, 0), (0, sy)):
                for zz in (3.2, 5.6):
                    if side[0]:
                        xf = tx + side[0] * 3.5
                        b.box(xf, ty - 2.75, zz - 0.35, xf + side[0] * 0.05, ty + 2.75, zz + 0.35, "Mauerwerk")
                        b.box(xf, ty - 2.6, zz - 0.25, xf + side[0] * 0.08, ty + 2.6, zz + 0.25, "Fenster")
                    else:
                        yf = ty + side[1] * 3.5
                        b.box(tx - 2.75, yf, zz - 0.35, tx + 2.75, yf + side[1] * 0.05, zz + 0.35, "Mauerwerk")
                        b.box(tx - 2.6, yf, zz - 0.25, tx + 2.6, yf + side[1] * 0.08, zz + 0.25, "Fenster")
                if side[0]:
                    b.cbox(tx + side[0] * 3.6, ty, ZT - 0.2, 0.3, 7.3, 0.4, "Mauerwerk")
                else:
                    b.cbox(tx, ty + side[1] * 3.6, ZT - 0.2, 7.3, 0.3, 0.4, "Mauerwerk")
    # Treppen im Hof hinauf zu den Wehrgaengen West und Ost
    treppe(b, C - H + TD, C - 10, "N", 10, 2.5, 0, sd=0.8)
    treppe(b, C + H - TD - 2.5, C + 10, "S", 10, 2.5, 0, sd=0.8)


def tore(b):
    g0, g1 = C - G, C + G
    for sgn in (1, -1):
        yw = (C + H) if sgn > 0 else (C - H)                         # Aussenseite der Mauer
        ya, yb = (yw, yw + 2.7) if sgn > 0 else (yw - 2.7, yw)
        wy0, wy1 = (C + H - TD, C + H) if sgn > 0 else (C - H, C - H + TD)
        b.box(g0, wy0, 4.0, g1, wy1, ZW, "Mauerwerk")                # Sturz ueber dem Tor
        # Warnstreifen (rot/weiss) an der Aussenseite des Sturzes
        nst = 16
        wst = (g1 - g0) / nst
        for k in range(nst):
            xa = g0 + wst * k
            b.box(xa, yw, 4.05, xa + wst, yw + sgn * 0.04, 4.95, "Rot" if k % 2 == 0 else "Weiss")
        # hochgeklappte Schranken (rot/weiss) mit Gegengewicht
        for sx_, dx_ in ((g0 + 1.0, 1), (g1 - 1.0, -1)):
            yy = yw - sgn * 0.8
            b.cbox(sx_, yy, 0.55, 0.45, 0.45, 1.1, "Metall")
            L, ang = 3.0, math.radians(68.0)
            piv = (sx_, yy, 1.0)
            tip = (sx_ + dx_ * L * math.cos(ang), yy, 1.0 + L * math.sin(ang))
            nseg = 6
            for k in range(nseg):
                pa = tuple(piv[i] + (tip[i] - piv[i]) * k / nseg for i in range(3))
                pb = tuple(piv[i] + (tip[i] - piv[i]) * (k + 1) / nseg for i in range(3))
                b.beam(pa, pb, 0.13, 0.13, "Rot" if k % 2 == 0 else "Weiss", up=(0.0, 1.0, 0.0))
            gew = (sx_ - dx_ * 0.9, yy, 1.0 - 0.9 * math.sin(ang) + 0.4)
            b.beam(piv, gew, 0.13, 0.13, "Draht", up=(0.0, 1.0, 0.0))
            b.cbox(gew[0], gew[1], gew[2] - 0.15, 0.3, 0.3, 0.3, "Metall")
        # Wachhaeuser links und rechts vom Tor
        for gx0, gx1 in ((g0 - 3.0, g0), (g1, g1 + 3.0)):
            b.box(gx0, ya, 0.0, gx1, yb, 7.2, "Mauerwerk")
            b.box(gx0, ya, 7.2, gx1, yb, 7.5, "Mauerwerk dunkel")
            outer = (yb - 0.45, yb) if sgn > 0 else (ya, ya + 0.45)
            b.box(gx0, outer[0], 7.5, gx1, outer[1], 8.2, "Mauerwerk dunkel")
            if gx0 < C:
                b.box(gx0, ya, 7.5, gx0 + 0.45, yb, 8.2, "Mauerwerk dunkel")
            else:
                b.box(gx1 - 0.45, ya, 7.5, gx1, yb, 8.2, "Mauerwerk dunkel")
            cxm = (gx0 + gx1) / 2
            yface = yb if sgn > 0 else ya                              # Aussenwand des Wachhauses
            for zz0 in (2.4, 4.8):                                      # Fensterbaender zur Strasse
                fenster(b, cxm, yface, zz0 + 0.6, 1.8, 0.8, 0, sgn)
            # Suchscheinwerfer auf dem Dach
            px, py = cxm, yw + sgn * 1.4
            b.prism(px, py, 7.5, 0.3, 0.5, 8, "Metall")
            b.cbox(px, py + sgn * 0.2, 8.3, 0.9, 0.6, 0.6, "Metall")
            b.cbox(px, py + sgn * 0.55, 8.3, 0.5, 0.06, 0.4, "Lampe")
        for gx in (g0 - 1.5, g1 + 1.5):                                 # Fahnen an den Wachhaeusern
            fahne(b, gx, (ya + yb) / 2, 7.5, 4.7, "Fahne weiss" if sgn > 0 else "Fahne gelb", 2.2, 1.3, 90.0 if sgn > 0 else -90.0)


def bergfried(b):
    c = C
    b.box(c - 4, c - 4, 0.0, c + 4, c + 4, 6.0, "Beton hell")                     # Betriebsgebaeude
    b.box(c - 4, c + 4 - PW, 6.0, c + 4, c + 4, 7.2, "Beton dunkel")               # Bruestung Nord
    b.box(c - 4, c - 4, 6.0, c - 4 + PW, c + 4, 7.2, "Beton dunkel")               # Bruestung West
    # Treppe aufs Dach an der Ostseite (die Suedseite hat den Eingang): steigt von Norden nach Sueden und endet an der
    # offenen Suedost-Ecke des Daches (Bruestung nur Nord und West)
    treppe(b, c + 4, c - 4 + 12 * 0.8, "S", 12, 2.5, 0, sd=0.8)
    # Eingang auf der Suedseite, Vordach, Fenster
    kx, ky = c, c - 4.0
    b.cbox(kx, ky - 0.1, 1.3, 2.6, 0.2, 2.6, "Beton hell")
    b.cbox(kx, ky - 0.2, 1.15, 1.7, 0.1, 2.3, "Oliv")
    b.cbox(kx, ky - 0.27, 1.15, 0.05, 0.05, 2.3, "Draht")
    b.cbox(kx, ky - 0.7, 2.75, 3.4, 1.2, 0.18, "Beton hell")                       # Vordach
    b.cbox(kx - 1.0, ky - 0.2, 2.5, 0.2, 0.2, 0.24, "Lampe")
    for dx in (-2.6, 2.6):
        fenster(b, kx + dx, ky, 3.2, 1.3, 1.0, 0, -1)
    for ox_, ux_ in ((-4.0, 0), (0.0, 1)):                                          # Ostseite: Treppe davor, dort keine Fenster
        for dd in (-2.0, 2.0):
            if ux_ == 0:
                fenster(b, c + ox_, c + dd, 3.0, 1.5, 1.2, 1 if ox_ > 0 else -1, 0)
            else:
                fenster(b, c + dd, c + 4.0, 3.0, 1.5, 1.2, 0, 1)
    # Dachaufbauten, Fundament des Drehkranzes
    for dx, dy, hh in ((-2.4, -2.4, 0.9), (2.5, 2.4, 0.7)):
        b.cbox(c + dx, c + dy, 6.0 + hh / 2, 1.0, 1.0, hh, "Metall hell")
        b.prism(c + dx, c + dy, 6.0 + hh, 0.3, 0.25, 8, "Metall")
    b.cbox(c, c, 6.15, 3.2, 3.2, 0.3, "Beton dunkel")


def hof(b):
    c = C
    x0, x1, y0, y1 = c - H, c + H, c - H, c + H
    b.box(x0 + TD, y0 + TD, 0.0, x1 - TD, y1 - TD, 0.02, "Hof")                      # Pflaster im Hof
    # niedrige Deckung: Betonbarrieren auf den Bruecken vor den Toren, im Hof quer
    for s in (-1, 1):
        for a, bb in ((c - 3.3, c - 1.4), (c + 1.4, c + 3.3)):
            b.box(a, c + s * 28.0, 0.0, bb, c + s * 28.0 + 0.7, 1.2, "Brueckenbeton")
        b.box(c - 5, c + s * 14, 0.0, c + 5, c + s * 14 + 0.7, 1.2, "Beton dunkel")

    def kasematte(xa, ya, xb, yb, front):
        b.box(xa, ya, 3.0, xb, yb, 3.5, "Beton dunkel")                               # Dach
        if front in "NS":
            b.box(xa, ya, 0.0, xa + PW, yb, 3.0, "Beton hell")
            b.box(xb - PW, ya, 0.0, xb, yb, 3.0, "Beton hell")
            fy = yb - PW if front == "N" else ya
            for k in (1 / 3, 2 / 3):
                px = xa + (xb - xa) * k
                b.box(px - 0.35, fy, 0.0, px + 0.35, fy + PW, 3.0, "Beton hell")
        else:
            b.box(xa, ya, 0.0, xb, ya + PW, 3.0, "Beton hell")
            b.box(xa, yb - PW, 0.0, xb, yb, 3.0, "Beton hell")
            fx_ = xb - PW if front == "E" else xa
            for k in (1 / 3, 2 / 3):
                py = ya + (yb - ya) * k
                b.box(fx_, py - 0.35, 0.0, fx_ + PW, py + 0.35, 3.0, "Beton hell")

    kasematte(c - 14, c - 19, c - 6, c - 14, "N")
    kasematte(c + 6, c - 19, c + 14, c - 14, "N")
    kasematte(c - 14, c + 14, c - 6, c + 19, "S")
    kasematte(c - 19, c + 4, c - 14, c + 14, "E")
    kasematte(c + 14, c - 14, c + 19, c - 4, "W")
    # freistehende Mauerstuecke um den Bergfried und Sprengschutz hinter den Toren
    for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
        b.box(c + sx * 10 - 2.5, c + sy * 10, 0.0, c + sx * 10 + 2.5, c + sy * 10 + 0.6, 2.0, "Beton dunkel")
    for sy in (-1, 1):
        b.box(c - 2, c + sy * 17, 0.0, c + 2, c + sy * 17 + 0.6, 2.2, "Beton dunkel")
    # Loeschwasserbehaelter im Hof
    wx, wy = c + 8.0, c - 8.0
    for a, bb, c2, d2 in ((wx - 1.1, wy - 1.1, wx + 1.1, wy - 0.7), (wx - 1.1, wy + 0.7, wx + 1.1, wy + 1.1),
                          (wx - 1.1, wy - 0.7, wx - 0.7, wy + 0.7), (wx + 0.7, wy - 0.7, wx + 1.1, wy + 0.7)):
        b.box(a, bb, 0.0, c2, d2, 0.95, "Beton hell")
    b.box(wx - 0.7, wy - 0.7, 0.0, wx + 0.7, wy + 0.7, 0.7, "Wasser")
    # Lampenmasten im Hof
    for fx, fy in ((c - 6.0, c - 16.0), (c + 6.0, c - 16.0), (c - 6.0, c + 16.0), (c + 6.0, c + 16.0)):
        b.beam((fx, fy, 0.0), (fx, fy, 4.6), 0.14, 0.14, "Metall")
        b.beam((fx, fy, 4.5), (fx + 0.7, fy, 4.75), 0.1, 0.1, "Metall")
        b.cbox(fx + 0.8, fy, 4.62, 0.5, 0.3, 0.14, "Lampe")


def radarschuessel(b, R=5.9, tiefe=1.8, elev=50.0, hz=4.4, N=16, K=4):
    """Parabolschuessel (Wuerzburg-Riese) auf Drehkranz, in Ortskoordinaten um den Drehpunkt (Blick nach +y)."""
    e = math.radians(elev)
    d = (0.0, math.cos(e), math.sin(e))
    u = (1.0, 0.0, 0.0)
    v = (0.0, -math.sin(e), math.cos(e))
    f = R * R / (4.0 * tiefe)
    Cc = (0.0, 0.8, hz)

    def P(r, phi, off=0.0):
        z_ = r * r / (4.0 * f)
        rc, rs = r * math.cos(phi), r * math.sin(phi)
        return tuple(Cc[i] + u[i] * rc + v[i] * rs + d[i] * (z_ + off) for i in range(3))

    front = tuple(Cc[i] + d[i] * f for i in range(3))
    back = tuple(Cc[i] - d[i] * 4.0 for i in range(3))
    for k in range(K):
        r0, r1 = R * k / K, R * (k + 1) / K
        for i in range(N):
            p0, p1 = 2 * math.pi * i / N, 2 * math.pi * (i + 1) / N
            if k == 0:
                b.tri_zu(P(0, 0), P(r1, p0), P(r1, p1), front, "Radar innen")
                b.tri_zu(P(0, 0, -0.12), P(r1, p0, -0.12), P(r1, p1, -0.12), back, "Radar aussen")
            else:
                for q in ((P(r0, p0), P(r1, p0), P(r1, p1)), (P(r0, p0), P(r1, p1), P(r0, p1))):
                    b.tri_zu(*q, front, "Radar innen")
                for q in ((P(r0, p0, -0.12), P(r1, p0, -0.12), P(r1, p1, -0.12)),
                          (P(r0, p0, -0.12), P(r1, p1, -0.12), P(r0, p1, -0.12))):
                    b.tri_zu(*q, back, "Radar aussen")
    for i in range(N):                                                         # Randwulst
        p0, p1 = 2 * math.pi * i / N, 2 * math.pi * (i + 1) / N
        b.beam(P(R, p0, -0.05), P(R, p1, -0.05), 0.2, 0.2, "Radar Rand", up=d)
    for i in range(8):                                                         # Rippen auf der Rueckseite
        phi = 2 * math.pi * i / 8
        b.beam(P(0.3, phi, -0.2), P(R * 0.97, phi, -0.2), 0.16, 0.16, "Radar Rand", up=d)
    for r_ in (R * 0.35, R * 0.68):
        for i in range(N):
            p0, p1 = 2 * math.pi * i / N, 2 * math.pi * (i + 1) / N
            b.beam(P(r_, p0, -0.2), P(r_, p1, -0.2), 0.1, 0.1, "Radar Rand", up=d)
    fh = P(0, 0, f)                                                            # Erreger im Brennpunkt, Streben
    for i in range(4):
        phi = math.pi / 4 + i * math.pi / 2
        b.beam(P(R, phi, -0.05), fh, 0.12, 0.12, "Radar Rand", up=d)
    b.cbox(fh[0], fh[1], fh[2], 0.28, 0.32, 0.28, "Metall")
    # Drehgestell: Plattform, Boecke, Achse, Geraetekabine
    for sx in (-1, 1):
        b.beam((sx * 1.25, 0.8, 0.45), (sx * 1.25, 0.8, hz + 0.1), 0.34, 0.34, "Metall")
        b.beam((sx * 1.25, 0.1, 0.45), (sx * 1.25, 0.8, hz - 0.6), 0.2, 0.2, "Metall")
        b.beam((sx * 1.25, 1.5, 0.45), (sx * 1.25, 0.8, hz - 0.6), 0.2, 0.2, "Metall")
    b.beam((-1.4, 0.8, hz), (1.4, 0.8, hz), 0.3, 0.3, "Metall hell")
    b.cbox(0.0, 0.8, 0.28, 3.4, 2.2, 0.5, "Metall")
    b.cbox(0.0, -1.2, 1.15, 1.9, 1.6, 1.5, "Oliv")


def freya(b, W=5.4, Hh=3.2, mast=4.2):
    """Freya-Antenne: Gittermast mit Dipolwand, in Ortskoordinaten (Wand blickt nach +y)."""
    leg = 0.9
    for sx in (-1, 1):
        for sy in (-1, 1):
            b.beam((sx * leg, sy * leg, 0.0), (sx * 0.28, sy * 0.28, mast), 0.13, 0.13, "Metall hell")
    for k in range(1, 4):
        z = mast * k / 4
        rr = leg - (leg - 0.28) * k / 4
        for a, c in (((-1, -1), (1, -1)), ((1, -1), (1, 1)), ((1, 1), (-1, 1)), ((-1, 1), (-1, -1))):
            b.beam((a[0] * rr, a[1] * rr, z), (c[0] * rr, c[1] * rr, z), 0.07, 0.07, "Metall hell")
    z0 = mast + 0.2
    b.beam((0, 0, 0), (0, 0, z0 + Hh / 2), 0.18, 0.18, "Metall")
    for sx in (-1, 1):
        b.beam((sx * W / 2, 0.0, z0), (sx * W / 2, 0.0, z0 + Hh), 0.14, 0.14, "Metall hell")
    for zz in (z0, z0 + Hh):
        b.beam((-W / 2, 0.0, zz), (W / 2, 0.0, zz), 0.14, 0.14, "Metall hell")
    nrow, ncol = 4, 7
    for r_ in range(nrow):
        zz = z0 + Hh * (r_ + 0.5) / nrow
        b.beam((-W / 2, 0.0, zz), (W / 2, 0.0, zz), 0.05, 0.05, "Metall hell")
        for c_ in range(ncol):
            xx = -W / 2 + W * (c_ + 0.5) / ncol
            b.beam((xx - 0.28, 0.35, zz), (xx + 0.28, 0.35, zz), 0.06, 0.06, "Weiss")
            b.beam((xx, 0.0, zz), (xx, 0.35, zz), 0.04, 0.04, "Metall")
    for c_ in range(ncol + 1):                                                 # Reflektorgitter dahinter
        xx = -W / 2 + W * c_ / ncol
        b.beam((xx, -0.12, z0), (xx, -0.12, z0 + Hh), 0.03, 0.03, "Radar Rand")
    for r_ in range(nrow * 2 + 1):
        zz = z0 + Hh * r_ / (nrow * 2)
        b.beam((-W / 2, -0.12, zz), (W / 2, -0.12, zz), 0.03, 0.03, "Radar Rand")
    b.cbox(0.0, -0.9, z0 + 0.7, 1.2, 0.9, 1.1, "Oliv")


ELEV = 55.0     # Rohrerhoehung des modellierten Geschuetzes (Grad)


def flak_sockel(b, tx, ty):
    """Fester Teil der Flak auf dem Eckturm (tx, ty): Sockel und Drehkranz."""
    b.box(tx - 0.45, ty - 0.45, ZT, tx + 0.45, ty + 0.45, ZT + 0.9, "Metall")
    b.prism(tx, ty, ZT + 0.9, 0.38, 0.45, 10, "Metall hell")


def flak_rohr(g):
    """Drehbares Geschuetz in Ortskoordinaten um den Drehpunkt (Rohre zeigen nach +y, um ELEV nach oben)."""
    el = math.radians(ELEV)
    d = (0.0, math.cos(el), math.sin(el))
    side = (-1.0, 0.0, 0.0)
    g.cbox(0.0, 0.0, 0.0, 0.9, 0.9, 0.6, "Oliv")                                   # Lafette
    for sg in (-1, 1):                                                              # zwei Rohre
        a = tuple(side[i] * 0.25 * sg for i in range(3))
        e = tuple(a[i] + d[i] * 3.2 for i in range(3))
        g.beam(a, e, 0.16, 0.16, "Metall", up=side)
        m = tuple(a[i] + d[i] * 3.0 for i in range(3))
        g.beam(m, e, 0.24, 0.24, "Metall hell", up=side)                            # Muendungsbremse
    s0 = tuple(d[i] * 0.45 for i in range(3))
    s1 = tuple(d[i] * 0.55 for i in range(3))
    g.beam(s0, s1, 1.3, 0.8, "Oliv", up=side)                                       # Schutzschild
    g.cbox(0.0, -0.7, -0.15, 0.5, 0.5, 0.4, "Metall")                               # Munitionskasten


def antennen():
    """Drehbare Teile als eigene Objekte: Liste (Name, Bau in Ortskoordinaten, Drehpunkt, Drehung um z in Grad).

    Die Drehpunkte sind dort, wo sich die Teile im Spiel drehen; so lassen sie sich in Blender mit R, Z auch von Hand drehen."""
    teile = []
    sch = Bau("radar_schuessel")
    radarschuessel(sch)
    teile.append(("radar_schuessel", sch, (C, C, 6.3), 20.0))
    for name, (sx, sy) in (("freya_sw", (-1, -1)), ("freya_no", (1, 1))):
        ff = Bau(name)
        freya(ff)
        teile.append((name, ff, (C + sx * H, C + sy * H, ZT + 0.08), 90.0 * sx))
    for name, (sx, sy) in (("flak_nw", (-1, 1)), ("flak_so", (1, -1))):
        tx, ty = C + sx * H, C + sy * H
        g = Bau(name)
        flak_rohr(g)
        winkel = math.degrees(math.atan2(-(C - tx), C - ty))                       # Rohr zeigt zur Burgmitte (wie im Spiel)
        teile.append((name, g, (tx, ty, ZT + 1.35), winkel))
    return teile


# ------------------------------------------------------------------ Graben und Bruecken
def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3.0 - 2.0 * t)


def graben_tiefe(x, y):
    """Tiefe des Wassergrabens an (x, y) in Metern (0 ausserhalb); Formel aus spiel.py (ohne Daemme)."""
    o0, o1, o2, o3, dp = GRABEN
    ox, oy = abs(x - C) - A, abs(y - C) - A
    if ox >= o3 or oy >= o3:
        return 0.0
    o = math.hypot(max(ox, 0.0), max(oy, 0.0))
    if o <= o0 or o >= o3:
        return 0.0
    tt = smoothstep(o0, o1, o) if o < o1 else ((1.0 - smoothstep(o2, o3, o)) if o > o2 else 1.0)
    for bx0, by0, bx1, by1 in DAEMME:
        if bx0 - 0.8 < x < bx1 + 0.8 and by0 - 0.8 < y < by1 + 0.8:
            tt *= smoothstep(0.0, 0.8, math.hypot(max(bx0 - x, 0.0, x - bx1), max(by0 - y, 0.0, y - by1)))
    return dp * tt


def gelaende_netz():
    """Burggelaende (Quadrat PATCH um die Mitte) als Dreiecke mit dem Graben; Rueckgabe (verts, tris, materialnamen)."""
    n = int(round(2 * PATCH / RASTER))
    verts = []
    for j in range(n + 1):
        for i in range(n + 1):
            x, y = C - PATCH + i * RASTER, C - PATCH + j * RASTER
            verts.append((x, y, -graben_tiefe(x, y)))
    tris, mats = [], []
    for j in range(n):
        for i in range(n):
            a, bb, c, e = j * (n + 1) + i, j * (n + 1) + i + 1, (j + 1) * (n + 1) + i + 1, (j + 1) * (n + 1) + i
            if (i + j) % 2 == 0:
                q = [(a, bb, c), (a, c, e)]
            else:
                q = [(a, bb, e), (bb, c, e)]
            for t in q:
                tris.append(t)
                dip = -sum(verts[k][2] for k in t) / 3.0
                mats.append("Schlamm" if dip > 1.35 else ("Boeschung" if dip > 0.03 else "Wiese"))
    return verts, tris, mats


def kontur(o, schritt=1.0, n_arc=8):
    """Punkte im Abstand o um das Quadrat C +- A (abgerundete Ecken), gegen den Uhrzeigersinn, mit feinen Geradenstuecken."""
    ecken = [(C + A, C + A), (C - A, C + A), (C - A, C - A), (C + A, C - A)]
    bogen = []
    for qa, (cx_, cy_) in enumerate(ecken):
        bogen.append([(cx_ + math.cos(math.radians(qa * 90 + 90.0 * k / n_arc)) * o,
                       cy_ + math.sin(math.radians(qa * 90 + 90.0 * k / n_arc)) * o) for k in range(n_arc + 1)])
    pts = []
    for qa in range(4):
        pts.extend(bogen[qa])
        p, q = bogen[qa][-1], bogen[(qa + 1) % 4][0]
        m = max(1, int(math.ceil(math.hypot(q[0] - p[0], q[1] - p[1]) / schritt)))
        for k in range(1, m):
            pts.append((p[0] + (q[0] - p[0]) * k / m, p[1] + (q[1] - p[1]) * k / m))
    return pts


def wasser_netz():
    """Wasserflaeche des Grabens (z = WASSER) als geschlossener Ring."""
    o0, o1, o2, o3, dp = GRABEN
    o_in = o0 + (o1 - o0) * 0.567 - 0.15
    o_out = o2 + (o3 - o2) * 0.433 + 0.15
    ri, ra = kontur(o_in), kontur(o_out)
    verts = [(x, y, WASSER) for x, y in ri] + [(x, y, WASSER) for x, y in ra]
    n = len(ri)
    faces = []
    for i in range(n):
        j = (i + 1) % n
        faces += [(i, n + i, n + j), (i, n + j, j)]
    return verts, faces


def bruecken(b):
    c = C
    hwb = 4.0
    x0, x1 = c - hwb, c + hwb
    # Nordbruecke (Stahlfachwerk, Bailey): Fahrbahn bei z = 0, ueber dem Wasser
    ya, yb = c + 24.6, c + A + 11.0
    n = int((yb - ya) / 0.6)
    cx = c
    for k in range(n):
        zz = ya + (yb - ya) * (k + 0.5) / n
        b.cbox(cx, zz, -0.03, x1 - x0 - 0.5, (yb - ya) / n - 0.04, 0.1, "Fahrbahn")
    for sx_ in (c - 1.6, c + 1.6):                                           # Laengstraeger
        b.box(sx_ - 0.15, ya, -0.55, sx_ + 0.15, yb, -0.1, "Stahl")
    nseg = max(3, int(round((yb - ya) / 1.5)))
    for k in range(nseg + 1):                                                # Quertraeger
        yy = ya + (yb - ya) * k / nseg
        b.beam((x0 + 0.1, yy, -0.28), (x1 - 0.1, yy, -0.28), 0.22, 0.28, "Stahl")
    for sx_ in (x0 + 0.25, x1 - 0.25):                                       # Fachwerk links/rechts
        b.box(sx_ - 0.1, ya, 0.0, sx_ + 0.1, yb, 0.18, "Stahl")              # Untergurt
        b.box(sx_ - 0.1, ya, 1.4, sx_ + 0.1, yb, 1.58, "Stahl")              # Obergurt
        for k in range(nseg + 1):
            yy = ya + (yb - ya) * k / nseg
            b.box(sx_ - 0.06, yy - 0.06, 0.0, sx_ + 0.06, yy + 0.06, 1.5, "Stahl")
        for k in range(nseg):
            y_a = ya + (yb - ya) * k / nseg
            y_b = ya + (yb - ya) * (k + 1) / nseg
            if k % 2 == 0:
                b.beam((sx_, y_a, 0.1), (sx_, y_b, 1.45), 0.1, 0.1, "Stahl")
            else:
                b.beam((sx_, y_a, 1.45), (sx_, y_b, 0.1), 0.1, 0.1, "Stahl")
        for yy in (ya + 0.2, yb - 0.2):
            b.cbox(sx_, yy, 1.78, 0.2, 0.2, 0.24, "Lampe")
    for sx_ in (x0 + 0.35, x1 - 0.35):                                       # Widerlager am Ufer
        b.cbox(sx_, yb + 0.1, -0.35, 1.2, 1.3, 0.9, "Brueckenbeton")
    b.box(x0, c + H - TD, 0.0, x1, ya, 0.02, "Fahrbahn")                    # Zufahrt durch das Tor bis zur Bruecke
    b.box(x0, c + 22.0, 0.02, x1, c + 22.9, 0.24, "Brueckenbeton")             # Schwelle am Tor
    # Suedbruecke (Beton mit Bruestung)
    ys0, ys1 = c - A - 11.0, c - 24.6
    L = ys1 - ys0
    b.box(x0, ys0, -0.5, x1, ys1, 0.02, "Fahrbahn")
    for k in range(0, int(L / 0.7), 3):                                      # Mittelstreifen
        zz = ys0 + 0.35 + k * 0.7
        b.box(c - 0.07, zz, 0.02, c + 0.07, zz + 0.9, 0.04, "Markierung")
    for sx in (x0, x1):
        px = sx + (0.2 if sx == x0 else -0.2)
        b.cbox(px, (ys0 + ys1) / 2, 0.8, 0.55, L + 0.2, 0.9, "Bruestung")
        b.cbox(px, (ys0 + ys1) / 2, 1.3, 0.7, L + 0.3, 0.12, "Brueckenbeton")
        for yy in (ys0 + 0.6, ys1 - 0.6):
            b.cbox(px, yy, 0.8, 0.8, 0.8, 1.8, "Brueckenbeton")
            b.cbox(px, yy, 1.95, 0.28, 0.28, 0.36, "Lampe")
    b.box(x0, ys1, 0.0, x1, c - H + TD, 0.02, "Fahrbahn")                   # Zufahrt durch das Tor bis zur Bruecke
    b.box(x0, c - 22.9, 0.02, x1, c - 22.0, 0.24, "Brueckenbeton")             # Schwelle am Tor


# ------------------------------------------------------------------ Aufbau in Blender
def marken_liste():
    """Platzhalter-Daten der Spielobjekte: (Name, x, y, z, Art, Groesse)."""
    out = [("kiste_burg_0", C - 12.0, C + 8.0, 0.0, 'CUBE', 0.4), ("kiste_burg_1", C + 12.0, C - 8.0, 0.0, 'CUBE', 0.4),
           ("koth_zone", C, C, 0.1, 'CIRCLE', 15.0)]
    for name, (sx, sy) in (("flak_nw", (-1, 1)), ("flak_so", (1, -1))):
        out.append(("marker_" + name, C + sx * H, C + sy * H, ZT + 1.35, 'SPHERE', 0.8))
    return out


def uv_in_metern(ob):
    """Legt UVs an, die der Groesse in Metern entsprechen (1 UV-Einheit = 1 m, je Flaeche entlang der dominanten Achse
    projiziert). So haben Texturen ueberall dieselbe Dichte; die Kachelgroesse stellt texturen.py im Material ein."""
    me = ob.data
    if not len(me.polygons):
        return
    uvl = me.uv_layers.new(name="UVMap")
    for p in me.polygons:
        n = p.normal
        ax = 0 if (abs(n.x) >= abs(n.y) and abs(n.x) >= abs(n.z)) else (1 if abs(n.y) >= abs(n.z) else 2)
        for li in p.loop_indices:
            co = me.vertices[me.loops[li].vertex_index].co
            uvl.data[li].uv = ((co.y, co.z), (co.x, co.z), (co.x, co.y))[ax]


def baue_alles():
    """Gibt (feste Baugruppen, Gelaende, Wasser, Marken, drehbare Teile) zurueck - ohne bpy aufrufbar (zum Testen)."""
    mauer, turm, tor, berg, hf, br = (Bau("burg_mauern"), Bau("burg_ecktuerme"), Bau("burg_tore"),
                                      Bau("burg_bergfried"), Bau("burg_hof"), Bau("burg_bruecken"))
    mauern(mauer)
    ecktuerme(turm)
    tore(tor)
    bergfried(berg)
    hof(hf)
    bruecken(br)
    for sx, sy in ((-1, 1), (1, -1)):
        flak_sockel(turm, C + sx * H, C + sy * H)
    return ([mauer, turm, tor, berg, hf, br], gelaende_netz(), wasser_netz(), marken_liste(), antennen())


def bauen():
    """Legt die Burg in der aktuellen Blender-Szene an (Collection "Burg")."""
    gruppen, (gv, gt, gm), (wv, wf), marken, dreh = baue_alles()
    coll = T.collection("Burg")
    for g in gruppen:
        namen = []
        for mname in g.m:
            if mname not in namen:
                namen.append(mname)
        mats = [T.material(n, *FARBEN[n]) if n in FARBEN else T.material(n, dict(T.STOFFE)[n]) for n in namen]
        idx = [namen.index(mname) for mname in g.m]
        ob = T.add_mesh(coll, g.name, g.v, g.f, mats, idx)
        uv_in_metern(ob)
    namen = []
    for mname in gm:
        if mname not in namen:
            namen.append(mname)
    mats = [T.material(n, *FARBEN[n]) if n in FARBEN else T.material(n, dict(T.STOFFE)[n]) for n in namen]
    T.add_mesh(coll, "burg_gelaende", gv, gt, mats, [namen.index(mname) for mname in gm])
    T.add_mesh(coll, "burggraben_wasser", wv, wf, [T.material("Wasser", *FARBEN["Wasser"])])
    nf = sum(len(g.f) for g in gruppen)
    for name, g, (px, py, pz), rot in dreh:                      # drehbare Teile: Objektursprung = Drehpunkt
        namen = []
        for mname in g.m:
            if mname not in namen:
                namen.append(mname)
        mats = [T.material(n, *FARBEN[n]) for n in namen]
        ob = T.add_mesh(coll, name, g.v, g.f, mats, [namen.index(mname) for mname in g.m])
        ob.location = (px, py, pz)
        ob.rotation_euler = (0.0, 0.0, math.radians(rot))
        nf += len(g.f)
    mc = T.collection("Burg-Marker")
    for name, x, y, z, art, gr in marken:
        T.marker(mc, name, x, y, z, art, gr)
    T.kamera(mc, "kamera_burg_sued", (C, C - 75.0, 24.0), (C, C, 5.0), 28.0)
    T.kamera(mc, "kamera_burg_ecke", (C - 58.0, C - 58.0, 30.0), (C, C, 4.0), 28.0)
    return nf
