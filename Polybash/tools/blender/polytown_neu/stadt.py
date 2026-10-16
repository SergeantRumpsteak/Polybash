"""Polybash - kleine Stadt um Burg und Flughafen (noch ohne Texturen, nur Farben).

Aufbau (Spielflaeche 0..300 m, Burg in der Mitte, Ringweg, Flughafen im Osten - siehe umgebung.py):
  * Stadt im Westen: Hauptstrasse vom Ringweg zum Marktplatz (30 x 30 m) mit Brunnen und Marktstaenden; am Platz das Rathaus
    (mit Uhrturm) im Norden, das Gasthaus im Sueden und je zwei Laeden im Westen und Osten. Um den Platz laeuft die runde
    Marktring-Strasse, an ihr und an der Hauptstrasse stehen die Wohnhaeuser.
  * Zwei Querspangen verbinden die Stadt mit der Nord- und der Suedstrasse (die vom Ringweg an den Burgtoren nach Norden bzw.
    Sueden fuehren) - dort liegt je ein Dorf mit Kreisverkehr, Dorfbrunnen, Bauernhof und Haeusern.
  * Teiche: vier Stueck in Mulden des Gelaendes (siehe umgebung.TEICHE).
  * Jedes Haus steht mit der Tuer zu einer Strasse und ist ueber einen Pfad mit ihr verbunden; Haeuser stehen nie auf Strassen,
    Plaetzen, Teichen oder im Burggelaende und nur auf ebenem Grund (umgebung.STADT_ZONEN). Das Wegenetz ist zusammenhaengend.
Ohne bpy testbar (baue_alles); bauen() legt die Objekte in der Collection "Stadt" an.
"""
import math
import os
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
DORF_N, DORF_S = (150.0, 250.0), (150.0, 50.0)           # Mitten der Kreisverkehre
KV_R, KV_B = 9.0, 5.0                                    # Kreisverkehr: Mittelradius, Breite

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
}


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
    add("Suedstrasse", (rings, (DORF_S[0], DORF_S[1] + KV_R)), 0.0)
    for nm, (cx, cy) in (("Kreisverkehr Nord", DORF_N), ("Kreisverkehr Sued", DORF_S)):
        kreis = [(cx + KV_R * math.cos(2 * math.pi * k / 24), cy + KV_R * math.sin(2 * math.pi * k / 24)) for k in range(24)]
        L.append({"name": nm, "roh": kreis, "pts": kreis, "w": KV_B, "zu": True})
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

    def __init__(self, b, cx, cy, zb, theta):
        self.b, self.cx, self.cy, self.zb = b, cx, cy, zb
        self.c, self.s = math.cos(theta), math.sin(theta)

    def P(self, p):
        return (self.cx + p[0] * self.c - p[1] * self.s, self.cy + p[0] * self.s + p[1] * self.c, self.zb + p[2])

    def box(self, x0, y0, z0, x1, y1, z1, mat):
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
        n = [0.0, 0.0, 0.0]
        for k in range(len(verts)):
            a, c = verts[k], verts[(k + 1) % len(verts)]
            n[0] += (a[1] - c[1]) * (a[2] + c[2]); n[1] += (a[2] - c[2]) * (a[0] + c[0]); n[2] += (a[0] - c[0]) * (a[1] + c[1])
        if n[0] * richtung[0] + n[1] * richtung[1] + n[2] * richtung[2] < 0:
            verts = verts[::-1]
        self.b.add([self.P(p) for p in verts], [tuple(range(len(verts)))], mat)

    def prism(self, x, y, z0, r, h, n, mat):
        px, py, _ = self.P((x, y, 0.0))
        self.b.prism(px, py, self.zb + z0, r, h, n, mat)


# ------------------------------------------------------------------ Gebaeude
def satteldach(g, w, d, h, rh, mat_dach, mat_giebel, ueber=0.4):
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


def haus(b, cx, cy, zb, theta, w, d, h, rh, wand, dach, kamin=True, stock=1):
    """Wohnhaus: w (x) x d (y), Tuer auf der -y-Seite (Strassenseite), Satteldach, Fenster, Kamin."""
    g = Lok(b, cx, cy, zb, theta)
    g.box(-w / 2, -d / 2, -1.0, w / 2, d / 2, h, wand)
    satteldach(g, w, d, h, rh, dach, wand)
    g.box(-0.55, -d / 2 - 0.08, 0.0, 0.55, -d / 2, 2.1, "Tuer")
    g.box(-0.8, -d / 2 - 0.3, 0.0, 0.8, -d / 2 + 0.0, 0.12, "Stein")                                           # Trittstein
    for zc in ([1.5] if stock == 1 else [1.4, 4.1]):
        for sx in (-1, 1):
            fenster_l(g, sx * w / 4.2, -d / 2, 0, -1, zc)
            fenster_l(g, sx * w / 4.2, d / 2, 0, 1, zc)
        fenster_l(g, w / 2, 0.0, 1, 0, zc)
        fenster_l(g, -w / 2, 0.0, -1, 0, zc)
    if stock == 2:
        fenster_l(g, 0.0, -d / 2, 0, -1, 4.1)
    if kamin:
        g.box(w / 4 - 0.35, d / 4 - 0.35, h, w / 4 + 0.35, d / 4 + 0.35, h + rh + 0.9, "Stein")
    return g


def scheune(b, cx, cy, zb, theta, w=12.0, d=9.0):
    """Bauernscheune: grosses Holzhaus mit Doppeltor auf der Strassenseite."""
    g = Lok(b, cx, cy, zb, theta)
    h, rh = 4.6, 3.4
    g.box(-w / 2, -d / 2, -1.0, w / 2, d / 2, h, "Holz")
    satteldach(g, w, d, h, rh, "Dach grau", "Holz")
    g.box(-1.6, -d / 2 - 0.08, 0.0, 1.6, -d / 2, 3.4, "Tuer")
    g.box(-0.05, -d / 2 - 0.12, 0.0, 0.05, -d / 2, 3.4, "Stein")
    for sx in (-1, 1):
        g.box(sx * 4.2 - 0.5, -d / 2 - 0.05, 3.0, sx * 4.2 + 0.5, -d / 2, 3.9, "Fenster")
    return g


def rathaus(b, cx, cy, theta):
    """Rathaus (22 x 12 m) mit Uhrturm ueber dem Eingang; Tuer/Fassade zeigt in lokale -y-Richtung (zum Platz)."""
    g = Lok(b, cx, cy, 0.0, theta)
    w, d, h, rh = 22.0, 12.0, 7.6, 3.6
    g.box(-w / 2, -d / 2, -1.0, w / 2, d / 2, h, "Rathaus")
    g.box(-w / 2 - 0.2, -d / 2 - 0.2, 0.0, w / 2 + 0.2, d / 2 + 0.2, 0.5, "Stein")                           # Sockel
    satteldach(g, w, d, h, rh, "Dach rot", "Rathaus")
    # Turm: 5 x 5 m, ragt 1,5 m vor die Fassade, 17 m hoch, Pyramidendach, Uhren auf allen vier Seiten
    ty0, ty1 = -d / 2 - 1.5, -d / 2 + 3.5
    g.box(-2.5, ty0, -1.0, 2.5, ty1, 17.0, "Rathaus")
    tc = (ty0 + ty1) / 2
    apex = (0.0, tc, 22.0)
    ecken = [(-3.0, ty0 - 0.5, 17.0), (3.0, ty0 - 0.5, 17.0), (3.0, ty1 + 0.5, 17.0), (-3.0, ty1 + 0.5, 17.0)]
    g.poly(ecken[::-1], (0.0, 0.0, -1.0), "Dach Kupfer")
    for k in range(4):
        a, c = ecken[k], ecken[(k + 1) % 4]
        mx, my = (a[0] + c[0]) / 2 - apex[0], (a[1] + c[1]) / 2 - apex[1]
        g.poly([a, c, apex], (mx, my, 3.0), "Dach Kupfer")
    for (nx, ny, px, py) in ((0, -1, 0.0, ty0), (0, 1, 0.0, ty1), (-1, 0, -2.5, tc), (1, 0, 2.5, tc)):
        if nx:
            g.box(px, tc - 1.1, 13.0, px + nx * 0.08, tc + 1.1, 15.2, "Uhr")
        else:
            g.box(-1.1, py, 13.0, 1.1, py + ny * 0.08, 15.2, "Uhr")
    # Portal mit Freitreppe
    g.box(-1.5, ty0 - 0.08, 0.0, 1.5, ty0, 3.2, "Tuer")
    for k in range(3):
        g.box(-2.2, ty0 - 0.5 - 0.5 * k, 0.0, 2.2, ty0, 0.5 - 0.17 * k, "Stein")
    # Fenster: zwei Reihen links und rechts vom Turm, sowie Seiten und Rueckseite
    for zc in (1.9, 5.0):
        for sx in (-1, 1):
            for off in (4.0, 6.8, 9.4):
                fenster_l(g, sx * off, -d / 2, 0, -1, zc, 1.0, 1.5)
        for off in (-7.5, -2.5, 2.5, 7.5):
            fenster_l(g, off, d / 2, 0, 1, zc, 1.0, 1.5)
        for yy in (-2.5, 2.5):
            fenster_l(g, w / 2, yy, 1, 0, zc, 1.0, 1.5)
            fenster_l(g, -w / 2, yy, -1, 0, zc, 1.0, 1.5)
    return g


def gasthaus(b, cx, cy, theta):
    g = Lok(b, cx, cy, 0.0, theta)
    w, d, h, rh = 18.0, 10.0, 6.6, 3.4
    g.box(-w / 2, -d / 2, -1.0, w / 2, d / 2, h, "Putz gelb")
    satteldach(g, w, d, h, rh, "Dach rot", "Putz gelb")
    g.box(-0.8, -d / 2 - 0.08, 0.0, 0.8, -d / 2, 2.3, "Tuer")
    for k in range(2):
        g.box(-1.3, -d / 2 - 0.4 - 0.4 * k, 0.0, 1.3, -d / 2, 0.36 - 0.18 * k, "Stein")
    for zc in (1.6, 4.5):
        for off in (-6.5, -3.5, 3.5, 6.5):
            fenster_l(g, off, -d / 2, 0, -1, zc, 1.1, 1.4)
        for off in (-6.0, 0.0, 6.0):
            fenster_l(g, off, d / 2, 0, 1, zc, 1.1, 1.4)
    g.box(2.2, -d / 2 - 1.3, 3.6, 2.4, -d / 2, 3.8, "Metall")                                                  # Ausleger fuers Schild
    g.box(2.2, -d / 2 - 1.3, 2.4, 3.6, -d / 2 - 1.25, 3.7, "Markt rot")                                         # Wirtshausschild
    g.box(w / 2 - 0.3, -d / 2 + 1.2, h, w / 2 + 0.5, -d / 2 + 2.0, h + rh + 0.9, "Stein")
    return g


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


def eben(x, y, r, tol=0.35):
    zs = [U.gelaende_hoehe(x + r * math.cos(a), y + r * math.sin(a)) for a in (0.0, 1.57, 3.14, 4.71)] + [U.gelaende_hoehe(x, y)]
    return max(abs(z) for z in zs) < tol, sum(zs) / len(zs)


HAUSTYPEN = [  # w, d, h, rh, Wand, Dach, Stockwerke
    (8.0, 7.0, 3.2, 2.6, "Putz weiss", "Dach rot", 1),
    (9.0, 7.5, 5.6, 3.0, "Putz gelb", "Dach rot", 2),
    (7.0, 6.5, 3.0, 2.4, "Putz rot", "Dach grau", 1),
    (8.5, 7.0, 5.4, 3.0, "Putz blau", "Dach grau", 2),
    (7.5, 7.0, 3.1, 2.5, "Putz weiss", "Dach grau", 1),
]


def setze_haus(zb_, b, wege_b, belegt, hausliste, x, y, nx, ny, hr, typ, rand_strasse_pt=None, scheune_=False):
    """Versucht, ein Haus bei (x, y) mit Tuer in Richtung (nx, ny) zu setzen und mit einem Pfad zur Strasse zu verbinden.

    hr = Abstand der Strassenkante von der Strassenmitte am Pfadanfang. Rueckgabe True bei Erfolg."""
    return False


def haeuser_entlang(L, p, q, strs, belegt, haeuser, pfade, abstand=14.0, rand=11.0, setback=3.2, zaehler=[0], seiten=(1, -1), strasse=None):
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
            zaehler[0] += 1
            typ = HAUSTYPEN[zaehler[0] % len(HAUSTYPEN)]
            w, d = typ[0], typ[1]
            off = hr + setback + d / 2
            hx, hy = p[0] + ux * t + s * nrm[0] * off, p[1] + uy * t + s * nrm[1] * off
            r = math.hypot(w + 0.8, d + 0.8) / 2
            ok_e, zb = eben(hx, hy, r * 0.8)
            if not (ok_e and belegt.frei(hx, hy, r, rand=0.5)):
                continue
            theta = math.atan2(-s * nrm[0], s * nrm[1]) if False else None
            nx_, ny_ = -s * nrm[0], -s * nrm[1]                 # Richtung zur Strasse (Tuerseite)
            theta = math.atan2(nx_, -ny_)
            belegt.kreise.append((hx, hy, r))
            haeuser.append({"x": hx, "y": hy, "r": r, "theta": theta, "typ": typ, "zb": zb, "w": w, "d": d, "strasse": strasse["name"]})
            door = (p[0] + ux * t + s * nrm[0] * (hr + setback), p[1] + uy * t + s * nrm[1] * (hr + setback))
            start = (p[0] + ux * t + s * nrm[0] * (hr - 0.3), p[1] + uy * t + s * nrm[1] * (hr - 0.3))
            pfade.append((start, door))


def kreis_haeuser(zentrum, r_innen, strs, belegt, haeuser, pfade, n=9, ohne=(-math.pi / 2,), versatz=0.0, strasse=None, scheune_idx=3):
    cx, cy = zentrum
    zaehler = 0
    for k in range(n):
        a = versatz + 2 * math.pi * k / n
        if any(abs((a - o + math.pi) % (2 * math.pi) - math.pi) < 0.5 for o in ohne):
            continue
        typ = HAUSTYPEN[(k + 2) % len(HAUSTYPEN)]
        sched = k == scheune_idx
        w, d = (12.0, 9.0) if sched else (typ[0], typ[1])
        rad = r_innen + 3.2 + d / 2
        hx, hy = cx + rad * math.cos(a), cy + rad * math.sin(a)
        r = math.hypot(w + 0.8, d + 0.8) / 2
        ok_e, zb = eben(hx, hy, r * 0.8)
        if not (ok_e and belegt.frei(hx, hy, r, rand=0.5)):
            continue
        theta = math.atan2(-math.cos(a), math.sin(a))              # Tuer zeigt zur Mitte: Richtung (-cos a, -sin a)
        belegt.kreise.append((hx, hy, r))
        haeuser.append({"x": hx, "y": hy, "r": r, "theta": theta, "typ": typ, "zb": zb, "w": w, "d": d, "scheune": sched, "strasse": strasse["name"]})
        door = (cx + (r_innen + 3.2) * math.cos(a), cy + (r_innen + 3.2) * math.sin(a))
        start = (cx + (r_innen - 0.3) * math.cos(a), cy + (r_innen - 0.3) * math.sin(a))
        pfade.append((start, door))


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
    # Haeuser entlang der Strassen
    zaehler = [0]
    for nm in ("Marktring",):
        s = S[nm]
        roh = s["roh"]
        for i in range(len(roh)):
            haeuser_entlang(None, roh[i], roh[(i + 1) % len(roh)], strs, belegt, haeuser, pfade, abstand=13.0, zaehler=zaehler, strasse=s)
    haeuser_entlang(None, S["Hauptstrasse"]["roh"][0], S["Hauptstrasse"]["roh"][1], strs, belegt, haeuser, pfade, abstand=13.0, rand=6.0, zaehler=zaehler, strasse=S["Hauptstrasse"])
    for nm in ("Spange Nord", "Spange Sued"):
        s = S[nm]
        for i in range(len(s["roh"]) - 1):
            haeuser_entlang(None, s["roh"][i], s["roh"][i + 1], strs, belegt, haeuser, pfade, abstand=14.0, rand=13.0, zaehler=zaehler, strasse=s)
    for nm in ("Nordstrasse", "Suedstrasse"):
        s = S[nm]
        a, e = s["roh"]
        haeuser_entlang(None, a, e, strs, belegt, haeuser, pfade, abstand=14.0, rand=14.0, zaehler=zaehler, strasse=s)
    # Doerfer um die Kreisverkehre
    kreis_haeuser(DORF_N, KV_R + KV_B / 2, strs, belegt, haeuser, pfade, n=9, ohne=(-math.pi / 2,), strasse=S["Kreisverkehr Nord"], scheune_idx=3)
    kreis_haeuser(DORF_S, KV_R + KV_B / 2, strs, belegt, haeuser, pfade, n=9, ohne=(math.pi / 2,), strasse=S["Kreisverkehr Sued"], scheune_idx=6)
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
    return {"strs": strs, "S": S, "zentrum": zentrum, "haeuser": haeuser, "pfade": pfade, "baeume": baeume, "belegt": belegt}


# ------------------------------------------------------------------ Bau der Objekte
def baue_alles():
    P = plane_stadt()
    # Wege
    w = Bau("stadt_wege")
    for s in P["strs"]:
        U.pfad(w, s["pts"], s["w"], Z_STR, "Strasse", geschlossen=s["zu"])
    x0, y0, x1, y1 = PLATZ
    w.add([(x0, y0, Z_PLATZ), (x1, y0, Z_PLATZ), (x1, y1, Z_PLATZ), (x0, y1, Z_PLATZ)], [(0, 1, 2, 3)], "Pflaster")
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
    dorfbrunnen(z, *DORF_S)
    # Haeuser
    h = Bau("stadt_haeuser")
    for H in P["haeuser"]:
        if H.get("scheune"):
            scheune(h, H["x"], H["y"], H["zb"], H["theta"], H["w"], H["d"])
        else:
            w_, d_, hh, rh, wand, dach, st = H["typ"]
            haus(h, H["x"], H["y"], H["zb"], H["theta"], w_, d_, hh, rh, wand, dach, stock=st)
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
    return [w, z, h, bm, t]


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
