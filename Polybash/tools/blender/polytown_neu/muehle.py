"""Polybash - Muehle, Koehlerhuette und Jagdhuette im Huegelland nordlich des Flugplatzes (x 205..298, y 248..298).

Der dichte Wald dort ist gelichtet (wald.py); Huegel, Bodenrauschen, Gras und einzelne Baeume bleiben. Die drei Gebaeude stehen auf ebenen Bauplaetzen
(umgebung.PLATEAUS), sind mit KEINER Strasse und keinem Weg verbunden und liegen weit auseinander:
  * Bockwindmuehle auf der Kuppe (236, 276): Holzrumpf auf Hausbaum und Kreuzschwellen, aussen Treppe zur Tuer, innen Mahlgang, Trichter, Kammrad,
    Mehlsaecke; vier Fluegel mit Latten und Segeltuch.
  * Koehlerhuette (262, 260): Reisig-Rasenhuette (A-Rahmen) mit Feuerstelle und Strohlager, Kohlenmeiler mit Russflecken und Leiter, Reisigwand,
    Holzstapel, Unterstand mit Kohlesaecken.
  * Jagdhuette (286, 269): Blockhaus mit Veranda, Geweihen, Etagenbett, Tisch, Ofen mit Rohr, Waffenschrank und Brennholzschuppen; dazu ein Hochsitz
    (258, 288) mit Treppe und eine Futterkrippe.
Alle Bauteile sind begehbar (Treppen max. 0,31 m), die Innenraeume haben Tueren; Fluegel, Dachflaechen und feine Reliefs sind kein Hindernis."""
import math
import random

import stadt as S
from stadt import Lok, wand, fensterschmuck, tuerrahmen, dach
import altbau
import bahn as BA
import umgebung as U
from burg import Bau

S.FARBEN.update({
    "Segel":   ((0.80, 0.74, 0.60), 1.0, 0.0),
    "Meiler":  ((0.20, 0.16, 0.12), 1.0, 0.0),
    "Fell":    ((0.42, 0.30, 0.20), 1.0, 0.0),
    "Geweih":  ((0.78, 0.72, 0.58), 0.9, 0.0),
    "Reisig":  ((0.36, 0.27, 0.17), 1.0, 0.0),
    "Rinde":   ((0.26, 0.19, 0.12), 1.0, 0.0),
})
for _n, _c in (("Sack", ((0.66, 0.60, 0.46), 1.0, 0.0)), ("Kohle", ((0.07, 0.07, 0.07), 1.0, 0.0)), ("Russ", ((0.05, 0.05, 0.05), 1.0, 0.0)),
               ("Eisen", ((0.22, 0.22, 0.22), 0.5, 0.0)), ("Dielen", ((0.46, 0.34, 0.22), 0.9, 0.0)), ("Teppich", ((0.45, 0.20, 0.16), 1.0, 0.0)),
               ("Moos", ((0.24, 0.34, 0.14), 1.0, 0.0)), ("Heu", ((0.74, 0.62, 0.28), 1.0, 0.0)),
               ("Gras 2", ((0.36, 0.52, 0.19), 1.0, 0.0)), ("Gras 3", ((0.21, 0.37, 0.13), 1.0, 0.0)), ("Bruch Erde", ((0.34, 0.27, 0.20), 1.0, 0.0)), ("Stroh", ((0.82, 0.72, 0.40), 1.0, 0.0))):
    S.FARBEN.setdefault(_n, _c)

MUEHLE = (270.0, 284.0, -45.0)           # Mitte, Drehung in Grad (-45: Fluegel nach Suedwesten; schraege Hindernisse werden als Kacheln gebaut)
KOEHLER = (279.5, 264.0, 90.0)           # Huette, Tuer nach Osten zum Meiler
MEILER = (288.5, 264.0)
JAGD = (255.3, 263.5, 0.0)               # Blockhaus, Tuer nach Sueden
HOCHSITZ = (94.5, 264.0, -90.0)          # Hochsitz in der oestlichen Sattelsenke der Burgruine (flach, 2,9 m); Treppe zeigt nach Westen zur Ruine
FUTTER = (240.0, 272.0, 0.0)             # Futterkrippe am Waldrand
ZELT = (290.0, 290.0)                     # Zeltplatz mit Feuerstelle in der Nordostecke
HOCHSITZ_WALD = (250.0, 43.0, -90.0)     # zweiter Hochsitz im Wald suedlich des Flugplatzes
BAUPLAETZE = ((270.0, 284.0, 15.0), (257.0, 262.0, 10.0), (285.0, 264.0, 12.0), (94.5, 264.0, 7.0), (290.0, 290.0, 9.0), (240.0, 272.0, 4.0), (250.0, 43.0, 7.0))


def _wr(cx, cy, th, x0, y0, x1, y1, m=0.4):
    """Achsenparalleles Weltrechteck um das lokale Rechteck (fuer Belegt/Gras/Baeume)."""
    c, s = math.cos(math.radians(th)), math.sin(math.radians(th))
    ps = [(cx + x * c - y * s, cy + x * s + y * c) for x, y in ((x0, y0), (x1, y0), (x1, y1), (x0, y1))]
    return (min(p[0] for p in ps) - m, min(p[1] for p in ps) - m, max(p[0] for p in ps) + m, max(p[1] for p in ps) + m)


def _belegt():
    out = []
    mx, my, mt = MUEHLE
    out.append(_wr(mx, my, mt, -2.6, -2.8, 2.6, 2.8, 0.6))                                   # Rumpf samt Kreuzschwellen
    for k in range(5):                                                                      # Treppe (Stufen von der Tuer weg)
        out.append(_wr(mx, my, mt, -0.9, 2.8 + 1.5 * k, 0.9, 4.3 + 1.5 * k, 0.4))
    kx, ky, kt = KOEHLER
    out.append(_wr(kx, ky, kt, -2.3, -2.4, 2.3, 2.4, 0.5))
    out.append((MEILER[0] - 4.3, MEILER[1] - 4.3, MEILER[0] + 4.3, MEILER[1] + 4.3))
    out.append((MEILER[0] - 4.4, MEILER[1] + 4.2, MEILER[0] - 1.8, MEILER[1] + 6.6))         # Holzstapel
    out.append((MEILER[0] + 2.0, MEILER[1] - 4.8, MEILER[0] + 4.8, MEILER[1] - 1.6))         # Reisighaufen
    out.append(_wr(kx, ky, kt, 2.8, -3.4, 7.7, 1.6, 0.3))                                       # Unterstand
    jx, jy, jt = JAGD
    out.append(_wr(jx, jy, jt, -3.5, -4.3, 5.9, 2.7, 0.5))                                   # Haus, Veranda, Schuppen
    hx, hy, ht = HOCHSITZ
    out.append(_wr(hx, hy, ht, -1.3, -4.6, 1.3, 1.3, 0.4))
    hx2, hy2, ht2 = HOCHSITZ_WALD
    out.append(_wr(hx2, hy2, ht2, -1.3, -4.6, 1.3, 1.3, 0.4))
    out.append((ZELT[0] - 7.5, ZELT[1] - 7.5, ZELT[0] + 7.5, ZELT[1] + 7.5))
    fx, fy, _ = FUTTER
    out.append((fx - 2.0, fy - 1.4, fx + 2.0, fy + 1.4))
    return out


BELEGT = tuple(_belegt())


FLUEGEL_ACHSE = {}                          # Name des Fluegelobjekts -> (Drehpunkt (x, y, z), waagerechte Wellenrichtung (dx, dy)); fuer den Spiel-Export


def _bm(g, a, b, w, h, mat):
    """Balken in lokalen Koordinaten (kein Hindernis)."""
    g.b.beam(g.P(a), g.P(b), w, h, mat)


def _z(x, y):
    return U.gelaende_hoehe(x, y)


# ------------------------------------------------------------------ Bockwindmuehle
def muehle(b):
    cx, cy, th = MUEHLE
    zb = _z(cx, cy)
    g = Lok(b, cx, cy, zb, math.radians(th))
    g.kachel = 0.25
    rnd = random.Random(404)
    ZF, hw, hd, t = 2.8, 1.9, 2.5, 0.14
    H = ZF + 3.1
    zh = ZF + 1.9                                                                           # Hoehe der Fluegelwelle
    # Untergestell: Kreuzschwellen auf Steinbloecken, Hausbaum, Streben
    g.box(-2.7, -0.22, 0.3, 2.7, 0.22, 0.7, "Holz dunkel")
    g.box(-0.22, -2.7, 0.7, 0.22, 2.7, 1.1, "Holz dunkel")
    for (sx, sy) in ((-2.45, 0.0), (2.45, 0.0), (0.0, -2.45), (0.0, 2.45)):
        g.box(sx - 0.38, sy - 0.38, 0.0, sx + 0.38, sy + 0.38, 0.3 if sy == 0.0 else 0.7, "Stein alt")
    g.box(-0.32, -0.32, 0.7, 0.32, 0.32, ZF - 0.4, "Holz")
    for s_ in (-1, 1):
        _bm(g, (s_ * 2.3, 0.0, 0.7), (s_ * 0.3, 0.0, ZF - 0.9), 0.2, 0.2, "Holz dunkel")
        _bm(g, (0.0, s_ * 2.4, 1.1), (0.0, s_ * 0.3, ZF - 0.9), 0.2, 0.2, "Holz dunkel")
    # Boden und Waende
    g.box(-hw, -hd, ZF - 0.4, hw, hd, ZF, "Holz dunkel")
    altbau.Deko(g).box(-hw + t, -hd + t, ZF, hw - t, hd - t, ZF + 0.02, "Dielen")
    wand(g, "x", -hd, -hd + t, -hw, hw, ZF, H, "Holz alt", [(-0.3, 0.3, zh - 0.3, zh + 0.3)])
    wand(g, "x", hd - t, hd, -hw, hw, ZF, H, "Holz alt", [(-0.5, 0.5, ZF, ZF + 2.0)])
    fen = [(0.35, 0.85, ZF + 1.2, ZF + 1.8)]
    for sx in (-1, 1):
        wand(g, "y", sx * hw - (t if sx > 0 else 0.0), sx * hw + (0.0 if sx > 0 else t), -hd + t, hd - t, ZF, H, "Holz alt", fen)
        fensterschmuck(g, "y", sx * hw, sx, 0.6, ZF + 1.5, 0.5, 0.6, "Laden braun alt")
    for (ach, aus, sg, a0, a1) in (("x", -hd, -1, -hw, hw), ("x", hd, 1, -hw, hw), ("y", -hw, -1, -hd + t, hd - t), ("y", hw, 1, -hd + t, hd - t)):
        altbau.scheunen_latten(g, ach, aus, sg, a0, a1, ZF + 0.1, H)
    tuerrahmen(g, "x", hd - t, hd, -0.5, 0.5, ZF, ZF + 2.0, "Holz dunkel")
    g.box(0.58, hd, ZF, 0.64, hd + 0.9, ZF + 2.0, "Tuer")                                    # Tuerblatt aufgeklappt
    dach(g, "y", 2 * hw, 2 * hd, H, 1.9, "Dach grau alt", "Holz alt", e=0.35)
    # Aussentreppe: Absatz an der Tuer, 13 Stufen (Steigung 0,2 m) nach hinten; Handlaeufe beidseitig
    n, rise, run, y0 = 14, ZF / 14.0, 0.45, hd + 1.1
    g.box(-0.8, hd, ZF - 0.15, 0.8, y0, ZF, "Holz")
    for i in range(1, n):
        g.box(-0.45, y0 + (i - 1) * run, 0.0, 0.45, y0 + i * run, ZF - i * rise, "Holz" if i % 2 else "Holz alt")
    for sx in (-0.52, 0.52):
        _bm(g, (sx, y0, ZF + 0.9), (sx, y0 + (n - 1) * run, 0.9), 0.07, 0.07, "Holz dunkel")
        for k in range(0, n, 3):
            yy = y0 + k * run
            _bm(g, (sx, yy, max(ZF - k * rise, 0.0)), (sx, yy, max(ZF - k * rise, 0.0) + 0.9), 0.07, 0.07, "Holz dunkel")
    # Innenausbau: Mahlgang mit Trichter, Kammrad, Saecke, Fass, Werkbank
    g.box(-0.75, -1.4, ZF, 0.75, 0.1, ZF + 0.75, "Holz")
    g.prism(0.0, -0.65, ZF + 0.75, 0.62, 0.16, 10, "Stein")
    for (px, py) in ((-0.5, -1.15), (0.5, -1.15), (-0.5, -0.15), (0.5, -0.15)):
        _bm(g, (px, py, ZF + 0.9), (px, py, ZF + 2.3), 0.07, 0.07, "Holz dunkel")
    ring = [(0.55 * math.cos(2 * math.pi * k / 8), -0.65 + 0.55 * math.sin(2 * math.pi * k / 8), ZF + 2.4) for k in range(8)]
    g.b.add([g.P(p) for p in ring] + [g.P((0.0, -0.65, ZF + 1.4))], [tuple(range(7, -1, -1))] + [(k, (k + 1) % 8, 8) for k in range(8)], "Holz alt")
    _bm(g, (0.0, -hd - 1.0, zh), (0.0, -0.9, zh), 0.34, 0.34, "Holz dunkel")                  # Fluegelwelle
    ykr = -1.35
    for k in range(6):                                                                      # Kammrad: Speichen und Kranz
        a = k * math.pi / 3
        _bm(g, (0.0, ykr, zh), (0.9 * math.cos(a), ykr, zh + 0.9 * math.sin(a)), 0.1, 0.1, "Holz")
        a2 = a + math.pi / 3
        _bm(g, (0.9 * math.cos(a), ykr, zh + 0.9 * math.sin(a)), (0.9 * math.cos(a2), ykr, zh + 0.9 * math.sin(a2)), 0.13, 0.13, "Holz dunkel")
    for k, (px, py) in enumerate(((-1.55, 1.2), (-1.55, 1.85), (-0.95, 1.85))):
        g.box(px - 0.3, py - 0.3, ZF, px + 0.3, py + 0.3, ZF + 0.55 + (0.5 if k == 2 else 0.0) * 0, "Sack")
    g.box(-1.55 - 0.3, 1.2 - 0.3, ZF + 0.55, -1.55 + 0.3, 1.2 + 0.3, ZF + 1.05, "Sack")
    g.prism(1.35, 1.7, ZF, 0.35, 0.9, 8, "Holz alt")
    g.box(1.0, 1.35, ZF + 0.9, 1.7, 2.05, ZF + 0.95, "Holz dunkel")
    g.box(1.15, -2.0, ZF, 1.7, -1.1, ZF + 0.45, "Holz")                                      # Mehlkasten
    # Fluegelkreuz an der Welle (eigenes Objekt, im Spiel drehbar um die Welle)
    fl = Bau("nord_muehle_fluegel")
    b.fluegel = fl
    gf = Lok(fl, cx, cy, zb, math.radians(th))
    FLUEGEL_ACHSE["nord_muehle_fluegel"] = (gf.P((0.0, -hd - 0.9, zh)), (-math.sin(math.radians(th)), math.cos(math.radians(th))))
    yh = -hd - 0.9
    gf.box(-0.28, yh - 0.45, zh - 0.28, 0.28, -hd - 0.05, zh + 0.28, "Holz dunkel")
    ph = math.radians(22.0)
    for k in range(4):
        a = ph + k * math.pi / 2
        u = (math.cos(a), 0.0, math.sin(a))
        w = (-math.sin(a), 0.0, math.cos(a))
        P = lambda r, o, dy=0.0: (u[0] * r + w[0] * o, yh + dy, zh + u[2] * r + w[2] * o)
        _bm(gf, P(0.3, 0.0), P(4.4, 0.0), 0.22, 0.2, "Holz dunkel")
        _bm(gf, P(0.9, 1.15), P(4.3, 1.15), 0.09, 0.09, "Holz")
        _bm(gf, P(0.9, 0.0), P(0.9, 1.15), 0.09, 0.09, "Holz")
        _bm(gf, P(4.3, 0.0), P(4.3, 1.15), 0.09, 0.09, "Holz")
        r = 1.3
        while r < 4.3:
            _bm(gf, P(r, 0.0, 0.02), P(r, 1.15, 0.02), 0.07, 0.07, "Holz alt")
            r += 0.45
        if k % 2 == 0 or k == 3:                                                           # Segeltuch (zwei Sichtseiten)
            for dy, nz in ((0.05, 1), (0.03, -1)):
                vs = [P(1.0, 0.1, dy), P(4.2, 0.1, dy), P(4.2, 1.1, dy), P(1.0, 1.1, dy)]
                gf.poly(vs, (0.0, nz, 0.0), "Segel")
    # Wetterfahne am First
    g.box(-0.04, -0.04, H + 1.9, 0.04, 0.04, H + 2.5, "Eisen")


# ------------------------------------------------------------------ Koehlerhuette und Meiler
def koehlerhuette(b):
    cx, cy, th = KOEHLER
    g = Lok(b, cx, cy, _z(cx, cy), math.radians(th))
    rnd = random.Random(505)
    HW, Hh, L = 2.0, 2.7, 2.1
    nl = 14
    dz = Hh / nl
    g.box(-HW + 0.1, -L, 0.0, HW - 0.1, L, 0.06, "Bruch Erde")                                  # gestampfter Boden
    for sy in (-1, 1):                                                                       # Giebelbretter (vorn mit Tuer 0,95 m x 1,93 m)
        for k in range(nl):
            z0, z1 = k * dz, (k + 1) * dz
            hwk = HW * (1.0 - z1 / Hh) + 0.03
            mat = rnd.choice(("Holz", "Holz alt", "Holz dunkel"))
            ya, yb = (sy * L - 0.1, sy * L + 0.1)
            if sy < 0 and k < 10:
                g.box(-hwk, ya, z0, -0.48, yb, z1, mat)
                g.box(0.48, ya, z0, hwk, yb, z1, mat)
            else:
                g.box(-hwk, ya, z0, hwk, yb, z1, mat)
    tuerrahmen(g, "x", -L - 0.1, -L + 0.1, -0.48, 0.48, 0.0, 10 * dz, "Holz dunkel")
    HWo, Ho, ye = HW + 0.18, Hh + 0.1, L + 0.2                                                # Rasensoden-Dach beiderseits bis zum Boden
    for sx in (-1, 1):
        for j in range(6):
            ya, yb = -ye + j * 2 * ye / 6, -ye + (j + 1) * 2 * ye / 6
            mat = ("Moos", "Bruch Erde", "Gras 3", "Moos", "Gras 2", "Bruch Erde")[(j + (0 if sx < 0 else 3)) % 6]
            g.poly([(sx * HWo, ya, 0.0), (sx * HWo, yb, 0.0), (0.0, yb, Ho), (0.0, ya, Ho)], (sx * Ho, 0.0, HWo), mat)
        g.poly([(sx * (HW - 0.05), -ye, 0.0), (sx * (HW - 0.05), ye, 0.0), (0.0, ye, Hh - 0.1), (0.0, -ye, Hh - 0.1)], (-sx * Hh, 0.0, -HW), "Holz dunkel")
    for sy in (-1, 1):                                                                       # Stirnseiten der Sodendecke
        g.poly([(-HWo, sy * ye, 0.0), (HWo, sy * ye, 0.0), (0.0, sy * ye, Ho)], (0.0, sy, 0.0), "Bruch Erde")
    for y in (-1.5, -0.5, 0.5, 1.5):                                                         # Stangenpaare und Firststange
        for sx in (-1, 1):
            _bm(g, (sx * (HW - 0.12), y, 0.0), (0.0, y, Hh - 0.15), 0.1, 0.1, "Holz")
    _bm(g, (0.0, -L, Hh - 0.15), (0.0, L, Hh - 0.15), 0.14, 0.14, "Holz dunkel")
    ring = [(0.45 * math.cos(2 * math.pi * k / 8), 0.3 + 0.45 * math.sin(2 * math.pi * k / 8)) for k in range(8)]       # Feuerstelle
    for (px, py) in ring:
        g.box(px - 0.1, py - 0.1, 0.0, px + 0.1, py + 0.1, 0.16, "Stein dunkel")
    altbau.Deko(g).box(-0.3, 0.0, 0.06, 0.3, 0.6, 0.075, "Russ")
    for sx in (-0.6, 0.6):
        _bm(g, (sx, 0.3, 0.0), (0.0, 0.3, 1.5), 0.05, 0.05, "Holz dunkel")
    g.prism(0.0, 0.3, 0.9, 0.17, 0.26, 8, "Eisen")                                            # Kessel am Dreibein
    g.box(-1.5, 0.7, 0.06, -0.55, 1.95, 0.28, "Stroh")                                       # Strohlager mit Fell
    altbau.Deko(g).box(-1.4, 0.8, 0.28, -0.7, 1.7, 0.3, "Fell")
    g.box(0.8, 1.1, 0.06, 1.65, 1.9, 0.55, "Sack")                                           # Kohlesaecke
    g.box(0.9, 1.2, 0.55, 1.55, 1.8, 0.95, "Sack")
    g.box(-1.6, -1.8, 0.06, -1.1, -1.4, 0.4, "Holz alt")                                      # Kistchen
    for (a, c) in (((1.5, -1.5, 0.0), (1.1, -1.4, 1.6)), ((1.4, -1.3, 0.0), (1.1, -1.5, 1.7))):   # Rechen und Schaufel lehnen an der Wand
        _bm(g, a, c, 0.05, 0.05, "Holz")
    g.box(0.55, -1.65, 0.9, 0.95, -1.62, 1.1, "Eisen")


def meiler(b):
    """Kohlenmeiler (Haufen aus Holz, mit Rasen und Erde abgedeckt, Russflecken) mit Leiter, Reisigwand, Holzstapel und Unterstand."""
    x, y = MEILER
    z = _z(x, y)
    rnd = random.Random(606)
    lagen = ((3.4, 0.0), (3.35, 0.45), (3.0, 0.95), (2.4, 1.45), (1.5, 1.85), (0.55, 2.1))
    n = 14
    rings = []
    for (r, zz) in lagen:
        rings.append([(x + r * (0.94 + 0.12 * rnd.random()) * math.cos(2 * math.pi * k / n), y + r * (0.94 + 0.12 * rnd.random()) * math.sin(2 * math.pi * k / n), z + zz) for k in range(n)])
    for i in range(len(rings) - 1):
        for k in range(n):
            k2 = (k + 1) % n
            mat = "Meiler" if (i + k) % 5 else "Russ"
            if i == 0 and k % 3 == 0:
                mat = "Holz dunkel"
            b.add([rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]], [(0, 1, 2, 3)], mat)
    b.add(rings[-1], [tuple(range(n - 1, -1, -1))], "Russ")
    b.prism(x, y, z + 2.1, 0.28, 0.2, 8, "Russ")                                              # Fuellschacht-Kamin
    b.bx.append((x - 2.6, y - 2.6, z, x + 2.6, y + 2.6, z + 1.3))
    ring = [(x + 4.6 * (0.9 + 0.15 * rnd.random()) * math.cos(2 * math.pi * k / 16), y + 4.6 * (0.9 + 0.15 * rnd.random()) * math.sin(2 * math.pi * k / 16), z + 0.035) for k in range(16)]
    b.add(ring, [tuple(range(16))], "Russ")
    la, lb = (x + 3.4, y - 1.2, z + 0.1), (x + 0.9, y - 0.5, z + 1.95)                       # Leiter
    for dy in (-0.25, 0.25):
        b.beam((la[0], la[1] + dy, la[2]), (lb[0], lb[1] + dy, lb[2]), 0.07, 0.07, "Holz")
    for k in range(1, 7):
        t = k / 7.0
        b.beam((la[0] + (lb[0] - la[0]) * t, la[1] - 0.3 + (lb[1] - la[1]) * t, la[2] + (lb[2] - la[2]) * t),
               (la[0] + (lb[0] - la[0]) * t, la[1] + 0.3 + (lb[1] - la[1]) * t, la[2] + (lb[2] - la[2]) * t), 0.05, 0.05, "Holz")
    for (a0, a1) in ((0.5 * math.pi, 0.78 * math.pi), (1.22 * math.pi, 1.5 * math.pi)):     # Windwand aus Reisig (NW/SW, in der Mitte Durchgang zur Huette)
        ws = []
        for k in range(6):
            a = a0 + (a1 - a0) * k / 5
            px, py = x + 5.6 * math.cos(a), y + 5.6 * math.sin(a)
            ws.append((px, py))
            b.box(px - 0.06, py - 0.06, z, px + 0.06, py + 0.06, z + 1.7, "Holz dunkel")
        for (p, q) in zip(ws, ws[1:]):
            for z0_ in (0.35, 0.7, 1.05, 1.4):
                b.beam((p[0], p[1], z + z0_), (q[0], q[1], z + z0_ + 0.04), 0.13, 0.1, "Reisig")
    # Holzstapel
    out.append((MEILER[0] + 2.0, MEILER[1] - 4.8, MEILER[0] + 4.8, MEILER[1] - 1.6))         # Reisighaufen
    out.append(_wr(kx, ky, kt, 2.8, -3.4, 7.7, 1.6, 0.3))                                       # Unterstand
    jx, jy, jt = JAGD
    out.append(_wr(jx, jy, jt, -3.5, -4.3, 5.9, 2.7, 0.5))                                   # Haus, Veranda, Schuppen
    hx, hy, ht = HOCHSITZ
    out.append(_wr(hx, hy, ht, -1.3, -4.6, 1.3, 1.3, 0.4))
    hx2, hy2, ht2 = HOCHSITZ_WALD
    out.append(_wr(hx2, hy2, ht2, -1.3, -4.6, 1.3, 1.3, 0.4))
    out.append((ZELT[0] - 7.5, ZELT[1] - 7.5, ZELT[0] + 7.5, ZELT[1] + 7.5))
    fx, fy, _ = FUTTER
    out.append((fx - 2.0, fy - 1.4, fx + 2.0, fy + 1.4))
    return out


BELEGT = tuple(_belegt())


def _bm(g, a, b, w, h, mat):
    """Balken in lokalen Koordinaten (kein Hindernis)."""
    g.b.beam(g.P(a), g.P(b), w, h, mat)


def _z(x, y):
    return U.gelaende_hoehe(x, y)


# ------------------------------------------------------------------ Bockwindmuehle
def muehle(b):
    cx, cy, th = MUEHLE
    zb = _z(cx, cy)
    g = Lok(b, cx, cy, zb, math.radians(th))
    g.kachel = 0.25
    rnd = random.Random(404)
    ZF, hw, hd, t = 2.8, 1.9, 2.5, 0.14
    H = ZF + 3.1
    zh = ZF + 1.9                                                                           # Hoehe der Fluegelwelle
    # Untergestell: Kreuzschwellen auf Steinbloecken, Hausbaum, Streben
    g.box(-2.7, -0.22, 0.3, 2.7, 0.22, 0.7, "Holz dunkel")
    g.box(-0.22, -2.7, 0.7, 0.22, 2.7, 1.1, "Holz dunkel")
    for (sx, sy) in ((-2.45, 0.0), (2.45, 0.0), (0.0, -2.45), (0.0, 2.45)):
        g.box(sx - 0.38, sy - 0.38, 0.0, sx + 0.38, sy + 0.38, 0.3 if sy == 0.0 else 0.7, "Stein alt")
    g.box(-0.32, -0.32, 0.7, 0.32, 0.32, ZF - 0.4, "Holz")
    for s_ in (-1, 1):
        _bm(g, (s_ * 2.3, 0.0, 0.7), (s_ * 0.3, 0.0, ZF - 0.9), 0.2, 0.2, "Holz dunkel")
        _bm(g, (0.0, s_ * 2.4, 1.1), (0.0, s_ * 0.3, ZF - 0.9), 0.2, 0.2, "Holz dunkel")
    # Boden und Waende
    g.box(-hw, -hd, ZF - 0.4, hw, hd, ZF, "Holz dunkel")
    altbau.Deko(g).box(-hw + t, -hd + t, ZF, hw - t, hd - t, ZF + 0.02, "Dielen")
    wand(g, "x", -hd, -hd + t, -hw, hw, ZF, H, "Holz alt", [(-0.3, 0.3, zh - 0.3, zh + 0.3)])
    wand(g, "x", hd - t, hd, -hw, hw, ZF, H, "Holz alt", [(-0.5, 0.5, ZF, ZF + 2.0)])
    fen = [(0.35, 0.85, ZF + 1.2, ZF + 1.8)]
    for sx in (-1, 1):
        wand(g, "y", sx * hw - (t if sx > 0 else 0.0), sx * hw + (0.0 if sx > 0 else t), -hd + t, hd - t, ZF, H, "Holz alt", fen)
        fensterschmuck(g, "y", sx * hw, sx, 0.6, ZF + 1.5, 0.5, 0.6, "Laden braun alt")
    for (ach, aus, sg, a0, a1) in (("x", -hd, -1, -hw, hw), ("x", hd, 1, -hw, hw), ("y", -hw, -1, -hd + t, hd - t), ("y", hw, 1, -hd + t, hd - t)):
        altbau.scheunen_latten(g, ach, aus, sg, a0, a1, ZF + 0.1, H)
    tuerrahmen(g, "x", hd - t, hd, -0.5, 0.5, ZF, ZF + 2.0, "Holz dunkel")
    g.box(0.58, hd, ZF, 0.64, hd + 0.9, ZF + 2.0, "Tuer")                                    # Tuerblatt aufgeklappt
    dach(g, "y", 2 * hw, 2 * hd, H, 1.9, "Dach grau alt", "Holz alt", e=0.35)
    # Aussentreppe: Absatz an der Tuer, 13 Stufen (Steigung 0,2 m) nach hinten; Handlaeufe beidseitig
    n, rise, run, y0 = 14, ZF / 14.0, 0.45, hd + 1.1
    g.box(-0.8, hd, ZF - 0.15, 0.8, y0, ZF, "Holz")
    for i in range(1, n):
        g.box(-0.45, y0 + (i - 1) * run, 0.0, 0.45, y0 + i * run, ZF - i * rise, "Holz" if i % 2 else "Holz alt")
    for sx in (-0.52, 0.52):
        _bm(g, (sx, y0, ZF + 0.9), (sx, y0 + (n - 1) * run, 0.9), 0.07, 0.07, "Holz dunkel")
        for k in range(0, n, 3):
            yy = y0 + k * run
            _bm(g, (sx, yy, max(ZF - k * rise, 0.0)), (sx, yy, max(ZF - k * rise, 0.0) + 0.9), 0.07, 0.07, "Holz dunkel")
    # Innenausbau: Mahlgang mit Trichter, Kammrad, Saecke, Fass, Werkbank
    g.box(-0.75, -1.4, ZF, 0.75, 0.1, ZF + 0.75, "Holz")
    g.prism(0.0, -0.65, ZF + 0.75, 0.62, 0.16, 10, "Stein")
    for (px, py) in ((-0.5, -1.15), (0.5, -1.15), (-0.5, -0.15), (0.5, -0.15)):
        _bm(g, (px, py, ZF + 0.9), (px, py, ZF + 2.3), 0.07, 0.07, "Holz dunkel")
    ring = [(0.55 * math.cos(2 * math.pi * k / 8), -0.65 + 0.55 * math.sin(2 * math.pi * k / 8), ZF + 2.4) for k in range(8)]
    g.b.add([g.P(p) for p in ring] + [g.P((0.0, -0.65, ZF + 1.4))], [tuple(range(7, -1, -1))] + [(k, (k + 1) % 8, 8) for k in range(8)], "Holz alt")
    _bm(g, (0.0, -hd - 1.0, zh), (0.0, -0.9, zh), 0.34, 0.34, "Holz dunkel")                  # Fluegelwelle
    ykr = -1.35
    for k in range(6):                                                                      # Kammrad: Speichen und Kranz
        a = k * math.pi / 3
        _bm(g, (0.0, ykr, zh), (0.9 * math.cos(a), ykr, zh + 0.9 * math.sin(a)), 0.1, 0.1, "Holz")
        a2 = a + math.pi / 3
        _bm(g, (0.9 * math.cos(a), ykr, zh + 0.9 * math.sin(a)), (0.9 * math.cos(a2), ykr, zh + 0.9 * math.sin(a2)), 0.13, 0.13, "Holz dunkel")
    for k, (px, py) in enumerate(((-1.55, 1.2), (-1.55, 1.85), (-0.95, 1.85))):
        g.box(px - 0.3, py - 0.3, ZF, px + 0.3, py + 0.3, ZF + 0.55 + (0.5 if k == 2 else 0.0) * 0, "Sack")
    g.box(-1.55 - 0.3, 1.2 - 0.3, ZF + 0.55, -1.55 + 0.3, 1.2 + 0.3, ZF + 1.05, "Sack")
    g.prism(1.35, 1.7, ZF, 0.35, 0.9, 8, "Holz alt")
    g.box(1.0, 1.35, ZF + 0.9, 1.7, 2.05, ZF + 0.95, "Holz dunkel")
    g.box(1.15, -2.0, ZF, 1.7, -1.1, ZF + 0.45, "Holz")                                      # Mehlkasten
    # Fluegelkreuz an der Welle (eigenes Objekt, im Spiel drehbar um die Welle)
    fl = Bau("nord_muehle_fluegel")
    b.fluegel = fl
    gf = Lok(fl, cx, cy, zb, math.radians(th))
    FLUEGEL_ACHSE["nord_muehle_fluegel"] = (gf.P((0.0, -hd - 0.9, zh)), (-math.sin(math.radians(th)), math.cos(math.radians(th))))
    yh = -hd - 0.9
    gf.box(-0.28, yh - 0.45, zh - 0.28, 0.28, -hd - 0.05, zh + 0.28, "Holz dunkel")
    ph = math.radians(22.0)
    for k in range(4):
        a = ph + k * math.pi / 2
        u = (math.cos(a), 0.0, math.sin(a))
        w = (-math.sin(a), 0.0, math.cos(a))
        P = lambda r, o, dy=0.0: (u[0] * r + w[0] * o, yh + dy, zh + u[2] * r + w[2] * o)
        _bm(gf, P(0.3, 0.0), P(4.4, 0.0), 0.22, 0.2, "Holz dunkel")
        _bm(gf, P(0.9, 1.15), P(4.3, 1.15), 0.09, 0.09, "Holz")
        _bm(gf, P(0.9, 0.0), P(0.9, 1.15), 0.09, 0.09, "Holz")
        _bm(gf, P(4.3, 0.0), P(4.3, 1.15), 0.09, 0.09, "Holz")
        r = 1.3
        while r < 4.3:
            _bm(gf, P(r, 0.0, 0.02), P(r, 1.15, 0.02), 0.07, 0.07, "Holz alt")
            r += 0.45
        if k % 2 == 0 or k == 3:                                                           # Segeltuch (zwei Sichtseiten)
            for dy, nz in ((0.05, 1), (0.03, -1)):
                vs = [P(1.0, 0.1, dy), P(4.2, 0.1, dy), P(4.2, 1.1, dy), P(1.0, 1.1, dy)]
                gf.poly(vs, (0.0, nz, 0.0), "Segel")
    # Wetterfahne am First
    g.box(-0.04, -0.04, H + 1.9, 0.04, 0.04, H + 2.5, "Eisen")


# ------------------------------------------------------------------ Koehlerhuette und Meiler
def koehlerhuette(b):
    cx, cy, th = KOEHLER
    g = Lok(b, cx, cy, _z(cx, cy), math.radians(th))
    rnd = random.Random(505)
    HW, Hh, L = 2.0, 2.7, 2.1
    nl = 14
    dz = Hh / nl
    g.box(-HW + 0.1, -L, 0.0, HW - 0.1, L, 0.06, "Bruch Erde")                                  # gestampfter Boden
    for sy in (-1, 1):                                                                       # Giebelbretter (vorn mit Tuer 0,95 m x 1,93 m)
        for k in range(nl):
            z0, z1 = k * dz, (k + 1) * dz
            hwk = HW * (1.0 - z1 / Hh) + 0.03
            mat = rnd.choice(("Holz", "Holz alt", "Holz dunkel"))
            ya, yb = (sy * L - 0.1, sy * L + 0.1)
            if sy < 0 and k < 10:
                g.box(-hwk, ya, z0, -0.48, yb, z1, mat)
                g.box(0.48, ya, z0, hwk, yb, z1, mat)
            else:
                g.box(-hwk, ya, z0, hwk, yb, z1, mat)
    tuerrahmen(g, "x", -L - 0.1, -L + 0.1, -0.48, 0.48, 0.0, 10 * dz, "Holz dunkel")
    HWo, Ho, ye = HW + 0.18, Hh + 0.1, L + 0.2                                                # Rasensoden-Dach beiderseits bis zum Boden
    for sx in (-1, 1):
        for j in range(6):
            ya, yb = -ye + j * 2 * ye / 6, -ye + (j + 1) * 2 * ye / 6
            mat = ("Moos", "Bruch Erde", "Gras 3", "Moos", "Gras 2", "Bruch Erde")[(j + (0 if sx < 0 else 3)) % 6]
            g.poly([(sx * HWo, ya, 0.0), (sx * HWo, yb, 0.0), (0.0, yb, Ho), (0.0, ya, Ho)], (sx * Ho, 0.0, HWo), mat)
        g.poly([(sx * (HW - 0.05), -ye, 0.0), (sx * (HW - 0.05), ye, 0.0), (0.0, ye, Hh - 0.1), (0.0, -ye, Hh - 0.1)], (-sx * Hh, 0.0, -HW), "Holz dunkel")
    for sy in (-1, 1):                                                                       # Stirnseiten der Sodendecke
        g.poly([(-HWo, sy * ye, 0.0), (HWo, sy * ye, 0.0), (0.0, sy * ye, Ho)], (0.0, sy, 0.0), "Bruch Erde")
    for y in (-1.5, -0.5, 0.5, 1.5):                                                         # Stangenpaare und Firststange
        for sx in (-1, 1):
            _bm(g, (sx * (HW - 0.12), y, 0.0), (0.0, y, Hh - 0.15), 0.1, 0.1, "Holz")
    _bm(g, (0.0, -L, Hh - 0.15), (0.0, L, Hh - 0.15), 0.14, 0.14, "Holz dunkel")
    ring = [(0.45 * math.cos(2 * math.pi * k / 8), 0.3 + 0.45 * math.sin(2 * math.pi * k / 8)) for k in range(8)]       # Feuerstelle
    for (px, py) in ring:
        g.box(px - 0.1, py - 0.1, 0.0, px + 0.1, py + 0.1, 0.16, "Stein dunkel")
    altbau.Deko(g).box(-0.3, 0.0, 0.06, 0.3, 0.6, 0.075, "Russ")
    for sx in (-0.6, 0.6):
        _bm(g, (sx, 0.3, 0.0), (0.0, 0.3, 1.5), 0.05, 0.05, "Holz dunkel")
    g.prism(0.0, 0.3, 0.9, 0.17, 0.26, 8, "Eisen")                                            # Kessel am Dreibein
    g.box(-1.5, 0.7, 0.06, -0.55, 1.95, 0.28, "Stroh")                                       # Strohlager mit Fell
    altbau.Deko(g).box(-1.4, 0.8, 0.28, -0.7, 1.7, 0.3, "Fell")
    g.box(0.8, 1.1, 0.06, 1.65, 1.9, 0.55, "Sack")                                           # Kohlesaecke
    g.box(0.9, 1.2, 0.55, 1.55, 1.8, 0.95, "Sack")
    g.box(-1.6, -1.8, 0.06, -1.1, -1.4, 0.4, "Holz alt")                                      # Kistchen
    for (a, c) in (((1.5, -1.5, 0.0), (1.1, -1.4, 1.6)), ((1.4, -1.3, 0.0), (1.1, -1.5, 1.7))):   # Rechen und Schaufel lehnen an der Wand
        _bm(g, a, c, 0.05, 0.05, "Holz")
    g.box(0.55, -1.65, 0.9, 0.95, -1.62, 1.1, "Eisen")


def meiler(b):
    """Kohlenmeiler (Haufen aus Holz, mit Rasen und Erde abgedeckt, Russflecken) mit Leiter, Reisigwand, Holzstapel und Unterstand."""
    x, y = MEILER
    z = _z(x, y)
    rnd = random.Random(606)
    lagen = ((3.4, 0.0), (3.35, 0.45), (3.0, 0.95), (2.4, 1.45), (1.5, 1.85), (0.55, 2.1))
    n = 14
    rings = []
    for (r, zz) in lagen:
        rings.append([(x + r * (0.94 + 0.12 * rnd.random()) * math.cos(2 * math.pi * k / n), y + r * (0.94 + 0.12 * rnd.random()) * math.sin(2 * math.pi * k / n), z + zz) for k in range(n)])
    for i in range(len(rings) - 1):
        for k in range(n):
            k2 = (k + 1) % n
            mat = "Meiler" if (i + k) % 5 else "Russ"
            if i == 0 and k % 3 == 0:
                mat = "Holz dunkel"
            b.add([rings[i][k], rings[i][k2], rings[i + 1][k2], rings[i + 1][k]], [(0, 1, 2, 3)], mat)
    b.add(rings[-1], [tuple(range(n - 1, -1, -1))], "Russ")
    b.prism(x, y, z + 2.1, 0.28, 0.2, 8, "Russ")                                              # Fuellschacht-Kamin
    b.bx.append((x - 2.6, y - 2.6, z, x + 2.6, y + 2.6, z + 1.3))
    ring = [(x + 4.6 * (0.9 + 0.15 * rnd.random()) * math.cos(2 * math.pi * k / 16), y + 4.6 * (0.9 + 0.15 * rnd.random()) * math.sin(2 * math.pi * k / 16), z + 0.035) for k in range(16)]
    b.add(ring, [tuple(range(16))], "Russ")
    la, lb = (x + 3.4, y - 1.2, z + 0.1), (x + 0.9, y - 0.5, z + 1.95)                       # Leiter
    for dy in (-0.25, 0.25):
        b.beam((la[0], la[1] + dy, la[2]), (lb[0], lb[1] + dy, lb[2]), 0.07, 0.07, "Holz")
    for k in range(1, 7):
        t = k / 7.0
        b.beam((la[0] + (lb[0] - la[0]) * t, la[1] - 0.3 + (lb[1] - la[1]) * t, la[2] + (lb[2] - la[2]) * t),
               (la[0] + (lb[0] - la[0]) * t, la[1] + 0.3 + (lb[1] - la[1]) * t, la[2] + (lb[2] - la[2]) * t), 0.05, 0.05, "Holz")
    ws = []                                                                                  # Windwand aus Reisig (Halbkreis im Westen)
    for k in range(9):
        a = math.pi * 0.62 + math.pi * 0.76 * k / 8
        px, py = x + 5.6 * math.cos(a), y + 5.6 * math.sin(a)
        ws.append((px, py))
        b.box(px - 0.06, py - 0.06, z, px + 0.06, py + 0.06, z + 1.7, "Holz dunkel")
    for (p, q) in zip(ws, ws[1:]):
        for z0_ in (0.35, 0.7, 1.05, 1.4):
            b.beam((p[0], p[1], z + z0_), (q[0], q[1], z + z0_ + 0.04), 0.13, 0.1, "Reisig")
    # Holzstapel (Scheite quer), 4 Lagen
    sx0, sy0 = x - 4.2, y + 4.4
    for r_ in range(4):
        for j in range(5 - r_):
            BA.zyl_x(b, sx0, sx0 + 2.2, sy0 + 0.2 + 0.36 * j + 0.18 * r_, z + 0.18 + 0.32 * r_, 0.17, "Holz" if (j + r_) % 2 else "Holz alt", n=8)
    b.bx.append((sx0, sy0, z, sx0 + 2.2, sy0 + 2.0, z + 1.25))
    BA.kegel(b, x + 3.4, y - 3.2, z, 1.5, 0.9, "Reisig", n=9, rot=0.4)                      # Reisighaufen
    BA.kegel(b, x - 1.6, y - 3.8, z, 1.1, 0.7, "Kohle", n=8, rot=0.2)                         # Kohlehaufen
    # Unterstand mit Kohlesaecken neben der Huette: vier Pfosten, Pultdach
    hx, hy, ht = KOEHLER
    g = Lok(b, hx, hy, _z(hx, hy), math.radians(ht))
    for (px, py) in ((3.2, -2.8), (7.3, -2.8), (3.2, 1.0), (7.3, 1.0)):
        g.box(px - 0.1, py - 0.1, 0.0, px + 0.1, py + 0.1, 2.4 if py < -1 else 1.9, "Holz dunkel")
    g.poly([(3.0, -3.2, 2.4), (7.5, -3.2, 2.4), (7.5, 1.4, 1.9), (3.0, 1.4, 1.9)], (0.0, 0.1, 1.0), "Holz alt")
    g.poly([(3.0, -3.2, 2.35), (3.0, 1.4, 1.85), (7.5, 1.4, 1.85), (7.5, -3.2, 2.35)], (0.0, -0.1, -1.0), "Holz dunkel")
    for (px, py, k) in ((3.9, -2.4, 3), (5.0, -2.4, 2), (6.1, -2.4, 3), (7.0, -2.4, 1), (4.1, -0.8, 2)):
        for j in range(k):
            g.box(px - 0.4, py - 0.3, 0.55 * j, px + 0.4, py + 0.3, 0.55 * (j + 1), "Sack" if j % 2 == 0 else "Kohle")


# ------------------------------------------------------------------ Jagdhuette
def geweih(g, x, y, z, ny):
    """Geweih an der Wand bei (x, y) in Richtung ny (Dekoration)."""
    d = altbau.Deko(g)
    d.box(x - 0.2, y - 0.04, z, x + 0.2, y + 0.04, z + 0.3, "Holz")
    for sx in (-1, 1):
        _bm(g, (x + sx * 0.12, y + ny * 0.06, z + 0.3), (x + sx * 0.4, y + ny * 0.18, z + 0.7), 0.04, 0.04, "Geweih")
        _bm(g, (x + sx * 0.26, y + ny * 0.12, z + 0.5), (x + sx * 0.5, y + ny * 0.2, z + 0.52), 0.035, 0.035, "Geweih")
        _bm(g, (x + sx * 0.4, y + ny * 0.18, z + 0.7), (x + sx * 0.36, y + ny * 0.22, z + 0.95), 0.035, 0.035, "Geweih")


def jagdhuette(b):
    cx, cy, th = JAGD
    zb = _z(cx, cy)
    g = Lok(b, cx, cy, zb, math.radians(th))
    rnd = random.Random(707)
    W, D, FZ, t = 6.4, 4.8, 0.3, 0.26
    nc = 11
    ch = 2.6 / nc
    H = FZ + 2.6
    g.box(-W / 2, -D / 2, -0.6, W / 2, D / 2, FZ, "Stein alt")                                 # Fundament samt Fussboden
    altbau.Deko(g).box(-W / 2 + t, -D / 2 + t, FZ, W / 2 - t, D / 2 - t, FZ + 0.02, "Dielen")
    door = (-1.65, -0.7)
    ofront = [(door[0], door[1], FZ, FZ + 2.0), (0.95, 2.05, FZ + 0.9, FZ + 1.9)]
    oback = [(-2.3, -1.3, FZ + 0.9, FZ + 1.9), (1.1, 2.1, FZ + 0.9, FZ + 1.9)]
    oleft = [(-0.5, 0.5, FZ + 0.9, FZ + 1.9)]
    for c in range(nc):                                                                      # Blockbohlen, Ecken ueberkreuzt
        z0, z1 = FZ + c * ch, FZ + (c + 1) * ch
        mat = "Holz" if c % 2 else "Holz alt"
        ext = 0.2 if c % 2 == 0 else 0.0
        la0, la1 = (-W / 2 - ext, W / 2 + ext) if c % 2 == 0 else (-W / 2 + t, W / 2 - t)
        sa = 0.2 if c % 2 == 1 else -t
        sa0, sa1 = -D / 2 - sa, D / 2 + sa
        wand(g, "x", -D / 2, -D / 2 + t, la0, la1, z0, z1, mat, ofront)
        wand(g, "x", D / 2 - t, D / 2, la0, la1, z0, z1, mat, oback)
        wand(g, "y", -W / 2, -W / 2 + t, sa0, sa1, z0, z1, mat, oleft)
        wand(g, "y", W / 2 - t, W / 2, sa0, sa1, z0, z1, mat, [])
    tuerrahmen(g, "x", -D / 2, -D / 2 + t, door[0], door[1], FZ, FZ + 2.0, "Holz dunkel")
    g.box(door[1] + 0.02, -D / 2 - 0.9, FZ, door[1] + 0.08, -D / 2, FZ + 2.0, "Tuer")        # Tuerblatt aufgeklappt
    fensterschmuck(g, "x", -D / 2, -1, 1.5, FZ + 1.4, 1.1, 1.0, "Laden gruen alt")
    for ac in (-1.8, 1.6):
        fensterschmuck(g, "x", D / 2, 1, ac, FZ + 1.4, 1.0, 1.0, "Laden gruen alt")
    fensterschmuck(g, "y", -W / 2, -1, 0.0, FZ + 1.4, 1.0, 1.0, "Laden gruen alt")
    dach(g, "x", W, D, H, 1.7, "Ziegel dunkel alt", "Holz alt", e=0.8)
    # Veranda mit Stufe, Pfosten, Gelaender (mit Luecke an der Treppe)
    g.box(-W / 2 - 0.2, -D / 2 - 1.5, FZ - 0.12, W / 2 + 0.2, -D / 2, FZ, "Dielen")
    g.box(door[0] - 0.4, -D / 2 - 1.95, 0.0, door[1] + 0.4, -D / 2 - 1.5, 0.15, "Stein")
    for px in (-W / 2 + 0.1, -0.4, W / 2 - 0.1):
        g.box(px - 0.09, -D / 2 - 1.4 - 0.09, FZ, px + 0.09, -D / 2 - 1.4 + 0.09, H - 0.35, "Holz dunkel")
    _bm(g, (-W / 2 + 0.1, -D / 2 - 1.4, H - 0.3), (W / 2 - 0.1, -D / 2 - 1.4, H - 0.3), 0.14, 0.14, "Holz dunkel")
    for (xa, xb) in ((-W / 2 + 0.1, door[0] - 0.5), (door[1] + 0.5, W / 2 - 0.1)):
        _bm(g, (xa, -D / 2 - 1.4, FZ + 0.95), (xb, -D / 2 - 1.4, FZ + 0.95), 0.07, 0.07, "Holz")
        x_ = xa
        while x_ < xb:
            _bm(g, (x_, -D / 2 - 1.4, FZ), (x_, -D / 2 - 1.4, FZ + 0.95), 0.05, 0.05, "Holz")
            x_ += 0.35
    geweih(g, door[1] + 1.0, -D / 2 - 0.02, FZ + 2.05, -1.0)                                 # Geweih ueber der Tuer / am Giebel
    g.box(1.05, -D / 2 - 1.2, FZ, 2.55, -D / 2 - 0.6, FZ + 0.5, "Holz")                       # Bank auf der Veranda
    g.box(1.05, -D / 2 - 0.65, FZ + 0.5, 2.55, -D / 2 - 0.58, FZ + 0.95, "Holz alt")
    # Innen: Etagenbett, Tisch mit Baenken, Ofen mit Rohr, Anrichte, Waffenschrank, Fell, Geweihe
    ix0, ix1, iy0, iy1 = -W / 2 + t, W / 2 - t, -D / 2 + t, D / 2 - t
    g.box(ix0, iy1 - 1.8, FZ, ix0 + 0.95, iy1, FZ + 0.55, "Holz")
    g.box(ix0, iy1 - 1.8, FZ + 1.3, ix0 + 0.95, iy1, FZ + 1.45, "Holz")
    for (px, py) in ((ix0, iy1 - 1.8), (ix0 + 0.88, iy1 - 1.8), (ix0, iy1 - 0.08), (ix0 + 0.88, iy1 - 0.08)):
        g.box(px, py, FZ + 0.55, px + 0.07, py + 0.08, FZ + 1.3, "Holz dunkel")
    altbau.Deko(g).box(ix0 + 0.05, iy1 - 1.75, FZ + 0.55, ix0 + 0.9, iy1 - 0.1, FZ + 0.62, "Teppich")
    altbau.Deko(g).box(ix0 + 0.05, iy1 - 1.75, FZ + 1.45, ix0 + 0.9, iy1 - 0.1, FZ + 1.52, "Fell")
    tx, ty = 0.0, -0.4
    g.box(tx - 0.9, ty - 0.5, FZ + 0.72, tx + 0.9, ty + 0.5, FZ + 0.8, "Holz")
    for (px, py) in ((-0.8, -0.4), (0.8, -0.4), (-0.8, 0.4), (0.8, 0.4)):
        g.box(tx + px - 0.05, ty + py - 0.05, FZ, tx + px + 0.05, ty + py + 0.05, FZ + 0.72, "Holz dunkel")
    for sy in (-1, 1):
        g.box(tx - 0.85, ty + sy * 0.85 - 0.14, FZ, tx + 0.85, ty + sy * 0.85 + 0.14, FZ + 0.45, "Holz alt")
    g.prism(tx - 0.2, ty, FZ + 0.8, 0.09, 0.14, 8, "Eisen")
    g.box(tx + 0.3, ty - 0.12, FZ + 0.8, tx + 0.65, ty + 0.12, FZ + 0.84, "Eisen")
    g.box(ix1 - 0.7, -0.3, FZ, ix1, 0.4, FZ + 0.9, "Eisen")                                   # Kanonenofen
    g.prism(ix1 - 0.35, 0.05, FZ + 0.9, 0.07, 3.6, 8, "Eisen")                                # Ofenrohr durch das Dach
    g.box(ix1 - 1.2, 0.0, FZ, ix1 - 0.75, 0.3, FZ + 0.3, "Holz")                              # Holzkorb
    g.box(0.9, iy1 - 0.7, FZ, ix1 - 0.1, iy1, FZ + 0.9, "Holz")                              # Anrichte
    g.box(0.85, iy1 - 0.75, FZ + 0.9, ix1 - 0.05, iy1 + 0.0, FZ + 0.96, "Holz dunkel")
    g.box(-0.9, iy1 - 0.35, FZ, 0.45, iy1, FZ + 1.9, "Regal")                                 # Waffenschrank
    for k in range(4):
        _bm(g, (-0.8 + 0.3 * k, iy1 - 0.4, FZ + 0.15), (-0.75 + 0.3 * k, iy1 - 0.4, FZ + 1.7), 0.04, 0.04, "Eisen")
    altbau.Deko(g).box(-1.0, -1.7, FZ + 0.02, 1.0, -1.1, FZ + 0.045, "Fell")
    geweih(g, ix0 + 0.02, 0.0, FZ + 1.7, 1.0)
    geweih(g, 1.0, iy1 - 0.02, FZ + 2.0, -1.0)
    # Brennholzschuppen an der Ostseite: Pfosten, Pultdach, gestapelte Scheite
    for (px, py) in ((W / 2 + 0.15, -D / 2 + 0.3), (W / 2 + 0.15, D / 2 - 0.3), (W / 2 + 2.3, -D / 2 + 0.3), (W / 2 + 2.3, D / 2 - 0.3)):
        g.box(px - 0.1, py - 0.1, 0.0, px + 0.1, py + 0.1, 2.3 if px < W / 2 + 1 else 1.8, "Holz dunkel")
    g.poly([(W / 2, -D / 2 - 0.3, 2.35), (W / 2 + 2.6, -D / 2 - 0.3, 1.85), (W / 2 + 2.6, D / 2 + 0.3, 1.85), (W / 2, D / 2 + 0.3, 2.35)], (0.1, 0.0, 1.0), "Ziegel dunkel alt")
    g.poly([(W / 2, -D / 2 - 0.3, 2.3), (W / 2, D / 2 + 0.3, 2.3), (W / 2 + 2.6, D / 2 + 0.3, 1.8), (W / 2 + 2.6, -D / 2 - 0.3, 1.8)], (-0.1, 0.0, -1.0), "Holz dunkel")
    for k in range(3):
        g.box(W / 2 + 0.3, -D / 2 + 0.5 + 1.1 * k, 0.0, W / 2 + 1.5, -D / 2 + 0.5 + 1.1 * k + 1.0, 1.0 + 0.35 * (k % 2), "Holz alt")
    g.box(W / 2 + 0.3, -D / 2 + 0.5, 1.0, W / 2 + 1.5, -D / 2 + 1.5, 1.2, "Holz")
    BA.kegel(b, *g.P((W / 2 + 1.8, D / 2 - 1.0, 0.0))[:2], zb, 0.7, 0.45, "Reisig", n=7)


def hochsitz(b, site=None):
    cx, cy, th = site or HOCHSITZ
    zb = _z(cx, cy)
    g = Lok(b, cx, cy, zb, math.radians(th))
    FZ = 3.19
    for (sx, sy) in ((-1, -1), (1, -1), (-1, 1), (1, 1)):                                      # vier schraege Beine
        _bm(g, (sx * 1.0, sy * 1.0, -0.4), (sx * 0.62, sy * 0.62, FZ), 0.16, 0.16, "Holz dunkel")
        g.box(sx * 0.62 - 0.1, sy * 0.62 - 0.1, FZ - 0.5, sx * 0.62 + 0.1, sy * 0.62 + 0.1, FZ, "Holz dunkel")
    for z_ in (1.0, 2.0):                                                                    # Querstreben
        w_ = 1.0 - 0.38 * (z_ + 0.4) / (FZ + 0.4)
        for s_ in (-1, 1):
            _bm(g, (-w_, s_ * w_, z_), (w_, s_ * w_, z_), 0.08, 0.08, "Holz")
            _bm(g, (s_ * w_, -w_, z_), (s_ * w_, w_, z_), 0.08, 0.08, "Holz")
    g.box(-0.95, -0.95, FZ - 0.15, 0.95, 0.95, FZ, "Dielen")
    for (xa, ya, xb, yb) in ((-0.95, 0.85, 0.95, 0.95), (-0.95, -0.95, -0.85, 0.95), (0.85, -0.95, 0.95, 0.95)):    # Bruestung
        g.box(xa, ya, FZ, xb, yb, FZ + 1.05, "Holz alt")
    for sx in (-1, 1):
        g.box(sx * 0.95 - 0.05, -0.95, FZ, sx * 0.95 + 0.05, -0.8, FZ + 1.9, "Holz dunkel")
        g.box(sx * 0.95 - 0.05, 0.85, FZ, sx * 0.95 + 0.05, 0.95, FZ + 1.9, "Holz dunkel")
    g.poly([(-1.15, -1.15, FZ + 1.9), (1.15, -1.15, FZ + 1.9), (1.15, 1.15, FZ + 1.55), (-1.15, 1.15, FZ + 1.55)], (0.0, 0.1, 1.0), "Ziegel dunkel alt")
    g.poly([(-1.15, -1.15, FZ + 1.85), (-1.15, 1.15, FZ + 1.5), (1.15, 1.15, FZ + 1.5), (1.15, -1.15, FZ + 1.85)], (0.0, -0.1, -1.0), "Holz dunkel")
    g.box(-0.3, 0.45, FZ, 0.3, 0.85, FZ + 0.45, "Holz")                                      # Sitzbank
    n, rise, run = 11, 0.29, 0.34
    for i in range(1, n):                                                                    # Treppe nach vorn (-y)
        g.box(-0.4, -0.95 - i * run, -0.5, 0.4, -0.95 - (i - 1) * run, FZ - i * rise, "Holz" if i % 2 else "Holz alt")
    for sx in (-0.46, 0.46):
        _bm(g, (sx, -0.95, FZ + 0.95), (sx, -0.95 - (n - 1) * run, 0.95), 0.07, 0.07, "Holz dunkel")
    g.box(-0.4, -0.95 - 0.0, FZ - 0.04, 0.4, -0.9, FZ, "Holz")


def futterkrippe(b):
    fx, fy, th = FUTTER
    g = Lok(b, fx, fy, _z(fx, fy), math.radians(th))
    for sx in (-1.7, 1.7):
        g.box(sx - 0.08, -0.1, -1.0, sx + 0.08, 0.1, 1.9, "Holz dunkel")
    g.poly([(-2.1, -0.9, 1.7), (2.1, -0.9, 1.7), (2.1, 0.0, 2.3), (-2.1, 0.0, 2.3)], (0.0, -0.6, 1.0), "Holz alt")
    g.poly([(-2.1, 0.9, 1.7), (-2.1, 0.0, 2.3), (2.1, 0.0, 2.3), (2.1, 0.9, 1.7)], (0.0, 0.6, 1.0), "Holz alt")
    g.box(-1.5, -0.35, 0.0, 1.5, 0.35, 0.45, "Holz alt")                                      # Trog mit Heu
    g.box(-1.4, -0.28, 0.45, 1.4, 0.28, 0.6, "Heu")
    g.box(-1.6, 0.8, 0.0, -0.4, 1.3, 0.5, "Heu")
    g.box(1.0, 0.8, 0.0, 1.5, 1.3, 0.3, "Stein alt")                                          # Salzleckstein


S.FARBEN.update({"Zelt gruen": ((0.22, 0.34, 0.20), 1.0, 0.0), "Zelt ocker": ((0.62, 0.50, 0.28), 1.0, 0.0), "Zelt grau": ((0.45, 0.47, 0.46), 1.0, 0.0),
                 "Glut": ((1.0, 0.45, 0.10), 0.8, 3.0), "Asche": ((0.16, 0.15, 0.14), 1.0, 0.0)})


def zelt(b, x, y, th, mat):
    """Firstzelt (Zeltbahn ueber Firststange, offene Vorderseite mit dunklem Eingang), 2,4 x 3,2 m, 1,6 m hoch; Kern als niedriges Hindernis."""
    g = Lok(b, x, y, _z(x, y), math.radians(th))
    hw, hd, h = 1.2, 1.6, 1.6
    for sx in (-1, 1):
        g.poly([(sx * hw, -hd, 0.0), (sx * hw, hd, 0.0), (0.0, hd, h), (0.0, -hd, h)], (sx * h, 0.0, hw), mat)
        g.poly([(sx * (hw - 0.04), -hd, 0.0), (0.0, -hd, h - 0.04), (0.0, hd, h - 0.04), (sx * (hw - 0.04), hd, 0.0)], (-sx * h, 0.0, -hw), "Holz dunkel")
    g.poly([(-hw, hd, 0.0), (hw, hd, 0.0), (0.0, hd, h)], (0.0, 1.0, 0.0), mat)
    g.poly([(-hw, -hd, 0.0), (hw, -hd, 0.0), (0.0, -hd, h)], (0.0, -1.0, 0.0), "Zelt grau")
    g.poly([(-0.45, -hd - 0.01, 0.0), (0.45, -hd - 0.01, 0.0), (0.0, -hd - 0.01, 1.2)], (0.0, -1.0, 0.0), "Fenster")
    for sx in (-1, 1):
        _bm(g, (sx * 0.9, -hd - 0.6, 0.0), (0.0, -hd, h), 0.04, 0.04, "Holz")           # abgespannte Leinen
        g.box(sx * 0.9 - 0.03, -hd - 0.63, 0.0, sx * 0.9 + 0.03, -hd - 0.57, 0.15, "Holz dunkel")
    g.box(-0.9, -1.3, 0.0, 0.9, 1.3, 0.8, "Zelt grau")                                         # Hindernis (Zeltkoerper unten)
    g.box(-0.5, -hd - 0.9, 0.0, 0.5, -hd - 0.4, 0.4, "Sack")                                   # Rucksack vor dem Eingang


def zeltplatz(b):
    """Zeltplatz mit Feuerstelle in der Nordostecke: drei Zelte im Kreis, Steinring mit Glut, Baumstamm-Sitze, Tisch mit Baenken, Holzstapel, Dreibein."""
    x, y = ZELT
    z = _z(x, y)
    n = 10
    ring = [(x + 1.1 * math.cos(2 * math.pi * k / n), y + 1.1 * math.sin(2 * math.pi * k / n), z + 0.03) for k in range(n)]
    b.add(ring, [tuple(range(n))], "Asche")
    for k in range(n):                                                                       # Steinring
        a = 2 * math.pi * k / n
        px, py = x + 1.2 * math.cos(a), y + 1.2 * math.sin(a)
        b.box(px - 0.17, py - 0.17, z, px + 0.17, py + 0.17, z + 0.22 + 0.04 * (k % 3), "Stein dunkel" if k % 2 else "Stein alt")
    BA.kegel(b, x, y, z + 0.03, 0.55, 0.3, "Glut", n=6)
    for (a, l) in ((0.4, 1.4), (-0.7, 1.2), (2.6, 1.3)):                                    # Holzscheite im Feuer
        b.beam((x - 0.5 * math.cos(a), y - 0.5 * math.sin(a), z + 0.28), (x + 0.5 * math.cos(a), y + 0.5 * math.sin(a), z + 0.4), 0.1, 0.1, "Rinde")
    for sx in (-0.75, 0.75):                                                                # Dreibein mit Kessel
        b.beam((x + sx * 1.6, y + 0.3, z), (x, y, z + 1.9), 0.06, 0.06, "Holz dunkel")
    b.beam((x, y - 1.6, z), (x, y, z + 1.9), 0.06, 0.06, "Holz dunkel")
    b.prism(x, y, z + 0.95, 0.2, 0.28, 8, "Eisen")
    for (a, l) in ((0.3, 2.6), (1.9, 2.6), (3.6, 2.6), (5.0, 2.6)):                         # liegende Baumstaemme als Sitze
        cx_, cy_ = x + l * math.cos(a), y + l * math.sin(a)
        tx, ty = -math.sin(a), math.cos(a)
        b.beam((cx_ - tx * 0.9, cy_ - ty * 0.9, z + 0.2), (cx_ + tx * 0.9, cy_ + ty * 0.9, z + 0.2), 0.36, 0.34, "Rinde")
        b.bx.append((cx_ - 0.5, cy_ - 0.5, z, cx_ + 0.5, cy_ + 0.5, z + 0.38))
    for (tx_, ty_, th, mat) in ((x - 5.2, y + 1.0, 100.0, "Zelt gruen"), (x + 1.5, y + 5.0, -10.0, "Zelt ocker"), (x - 3.0, y - 5.0, 190.0, "Zelt gruen")):
        zelt(b, tx_, ty_, th - th % 90.0 if th % 90.0 else th, mat)
    tx, ty = x + 4.6, y - 3.4                                                               # Tisch mit Baenken
    b.box(tx - 0.9, ty - 0.45, z + 0.72, tx + 0.9, ty + 0.45, z + 0.8, "Holz")
    for (px, py) in ((-0.8, -0.35), (0.8, -0.35), (-0.8, 0.35), (0.8, 0.35)):
        b.box(tx + px - 0.05, ty + py - 0.05, z, tx + px + 0.05, ty + py + 0.05, z + 0.72, "Holz dunkel")
    for sy in (-0.85, 0.85):
        b.box(tx - 0.85, ty + sy - 0.14, z, tx + 0.85, ty + sy + 0.14, z + 0.44, "Holz alt")
    for k in range(3):                                                                       # Holzstapel
        b.box(x + 3.0, y + 4.6 + 0.0, z + 0.35 * k, x + 5.0, y + 5.4, z + 0.35 * (k + 1), "Holz" if k % 2 else "Holz alt")
    b.prism(x - 4.2, y - 2.0, z, 0.35, 0.9, 8, "Holz alt")                                  # Wasserfass


def bauen_nord():
    """Liefert [nord_muehle, nord_koehler, nord_jagd, nord_zeltplatz, wald_hochsitz, nord2_muehle, nord2_schaefer]."""
    a, c, d, e, f = Bau("nord_muehle"), Bau("nord_koehler"), Bau("nord_jagd"), Bau("nord_zeltplatz"), Bau("wald_hochsitz")
    muehle(a)
    koehlerhuette(c)
    meiler(c)
    jagdhuette(d)
    hochsitz(d)
    futterkrippe(d)
    zeltplatz(e)
    hochsitz(f, HOCHSITZ_WALD)
    import muehle2 as M2
    return [a, a.fluegel, c, d, e, f] + M2.bauen_ne()

import muehle2 as _M2  # noqa: E402  (zweite Muehle und Schaeferhuette: Belegung und Lichtungen)
BELEGT = BELEGT + _M2.BELEGT
BAUPLAETZE = BAUPLAETZE + _M2.BAUPLAETZE
