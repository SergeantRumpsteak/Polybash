"""Polybash - Bauernhof zwischen Steinbruch und Ort (x 34..64, y 64..95): Wohnhaus (Fachwerk, begehbar), grosse Scheune mit Heuboden und Treppe, Stall,
Silo, Brunnen, Heu- und Strohhaufen, Misthaufen, Weidezaun und Schotterzufahrt von der Werkstrasse. Alles aus den Altbau-Bausteinen (altbau.py, rustik.py)."""
import math
import random

import stadt as S
from stadt import Lok, pbox, wand, aussenwand, fensterschmuck, tuerrahmen, dach, haus, F0, F1, WD, TH
import bahn as BA
import rustik
from burg import Bau

S.FARBEN.update({
    "Hofboden": ((0.40, 0.33, 0.24), 1.0, 0.0),
    "Heu":      ((0.74, 0.62, 0.28), 1.0, 0.0),
    "Stroh":    ((0.82, 0.72, 0.40), 1.0, 0.0),
    "Silo":     ((0.60, 0.60, 0.56), 0.9, 0.0),
})
BELEGT = ((33.0, 62.5, 65.0, 93.5), (62.0, 73.0, 90.5, 79.0))          # Hof, Zufahrt
HAUS = (48.0, 87.5)                                                    # Wohnhaus 13 x 8.6, Tuer nach Sueden (zum Hof)
SCHEUNE = (38.0, 74.0)                                                 # 15 x 10, Tor nach Osten
STALL = (57.5, 74.0)                                                   # 12 x 7, Tuer nach Westen
SILO = (60.0, 88.0)
BRUNNEN = (48.0, 74.0)
ZUFAHRT_Y = 76.0


def halle(b, cx, cy, theta, w, d, H, rh, wm, dm, tor, fenster, rnd, zusatz=None):
    """Hohle, begehbare Landwirtschaftshalle (Fassade -y): Aussenwaende mit Tor (Breite/Hoehe), Fenstern mit Laeden, Sparrendach mit Belag,
    Erdboden, Querbalken. zusatz(g, ix0, ix1, iy0, iy1) baut das Innere."""
    g = Lok(b, cx, cy, 0.0, theta)
    hw, hd = w / 2, d / 2
    tw, th = tor
    ow, oh_ = [(-tw / 2, tw / 2, F0, F0 + th)], []
    oef_v = list(ow) + [(a - 0.5, a + 0.5, 2.2 - 0.5, 2.2 + 0.5) for a in fenster.get("v", ())]
    oef_h = [(a - 0.5, a + 0.5, 2.2 - 0.5, 2.2 + 0.5) for a in fenster.get("h", ())]
    oef_w = [(a - 0.5, a + 0.5, 2.2 - 0.5, 2.2 + 0.5) for a in fenster.get("w", ())] + [(-0.5, 0.5, 3.6, 4.4)]
    oef_o = [(a - 0.5, a + 0.5, 2.2 - 0.5, 2.2 + 0.5) for a in fenster.get("o", ())] + [(-0.5, 0.5, 3.6, 4.4)]
    aussenwand(g, "x", -hd, -1, -hw, hw, H, wm, oef_v)
    aussenwand(g, "x", hd, 1, -hw, hw, H, wm, oef_h)
    aussenwand(g, "y", -hw, -1, -hd + WD, hd - WD, H, wm, oef_w)
    aussenwand(g, "y", hw, 1, -hd + WD, hd - WD, H, wm, oef_o)
    for (ach, aus, sg, lst) in (("x", -hd, -1, fenster.get("v", ())), ("x", hd, 1, fenster.get("h", ())), ("y", -hw, -1, fenster.get("w", ())), ("y", hw, 1, fenster.get("o", ()))):
        for a in lst:
            fensterschmuck(g, ach, aus, sg, a, 2.2, 1.0, 1.0, "Laden braun alt", rnd.choice(("ok", "ok", "kaputt", "bretter")), (rnd.choice(("ok", "schief", "fehlt")), "ok"))
    for (ach, aus, sg) in (("y", -hw, -1), ("y", hw, 1)):                                  # Giebelluken
        pbox(g, ach, -0.5, 0.5, *sorted((aus - 0.0, aus + sg * -0.2)), 3.6, 4.4, "Heu")
    g.box(-tw / 2 - 0.25, -hd - 0.12, F0 + th, tw / 2 + 0.25, -hd + 0.2, F0 + th + 0.3, "Holz dunkel")   # Sturz
    for sx in (-1, 1):                                                                       # offene Torfluegel an die Wand geklappt
        xa = sx * tw / 2
        g.box(min(xa, xa + sx * 0.05), -hd - 0.1, F0, max(xa, xa + sx * 0.05), -hd - 0.1 + 0.04, F0 + th, "Holz")
        g.box(xa + sx * 0.02, -hd - 0.1 - tw / 2, F0 + 0.05, xa + sx * 0.08, -hd - 0.1, F0 + th - 0.05, "Holz alt")
    g.box(-hw + WD, -hd + WD, -0.7, hw - WD, hd - WD, F0, "Hofboden")
    for x in [-hw + 2.5 + 3.0 * k for k in range(int((w - 3.0) / 3.0))]:                      # Querbalken
        g.box(x - 0.12, -hd + WD, H - 0.55, x + 0.12, hd - WD, H - 0.3, "Holz dunkel")
    if zusatz:
        zusatz(g, -hw + WD, hw - WD, -hd + WD, hd - WD)
    rz = dach(g, "x", w, d, H, rh, dm, wm, e=0.6)
    return g


def scheune_zusatz(g, ix0, ix1, iy0, iy1):
    # Heuboden ueber der Osthaelfte, Treppe an der Nordwand, Gelaender zur offenen Seite, Heu
    x0 = 2.4
    zl = 3.0
    g.box(x0, iy0, zl - 0.2, ix1, iy1, zl, "Holz alt")
    for k in range(5):
        g.box(x0 + 0.1, iy0, zl - 0.55 - 0.0, x0 + 0.35, iy1, zl - 0.2, "Holz dunkel") if k == 0 else None
    n = 12
    rise = (zl - F0) / n
    run = 0.29
    for k in range(n):
        xa = x0 - (n - k) * run
        g.box(xa, iy1 - 1.1, F0, xa + run + 0.02, iy1 + 0.1, F0 + (k + 1) * rise, "Holz")
        zt = F0 + (k + 1) * rise
        g.box(xa, iy1 - 1.17, zt + 0.45, xa + run, iy1 - 1.1, zt + 0.5, "Holz alt")                # Gelaender an der offenen Seite
        g.box(xa, iy1 - 1.17, zt + 0.92, xa + run, iy1 - 1.1, zt + 0.97, "Holz alt")
        if k % 3 == 0:
            g.box(xa + 0.1, iy1 - 1.18, zt, xa + 0.17, iy1 - 1.1, zt + 0.97, "Holz alt")
    for (ya, yb) in ((iy0, iy1 - 1.1),):                                                      # Gelaender an der offenen Westkante
        g.box(x0 - 0.07, ya, zl + 0.45, x0 + 0.05, yb, zl + 0.55, "Holz alt")
        g.box(x0 - 0.07, ya, zl + 0.95, x0 + 0.05, yb, zl + 1.05, "Holz alt")
        for yy in (ya + 0.05, (ya + yb) / 2, yb - 0.05):
            g.box(x0 - 0.07, yy - 0.05, zl, x0 + 0.05, yy + 0.05, zl + 1.05, "Holz alt")
    g.box(x0 - 0.07, iy1 - 1.1 - 0.12, zl, x0 + 0.05, iy1 - 1.1, zl + 1.05, "Holz alt")
    for (hx, hy, lx, ly, hh) in ((3.0, iy0 + 0.4, 1.0, 2.2, 1.1), (4.2, iy0 + 0.4, 2.4, 2.0, 0.8), (3.4, 0.0, 3.2, 2.4, 1.3)):
        g.box(hx, hy, zl, hx + lx, hy + ly, zl + hh, "Heu")                                    # Heuhaufen oben
    g.box(ix0 + 0.4, iy0 + 0.4, F0, ix0 + 2.2, iy0 + 1.8, F0 + 1.0, "Heu")                     # Heuballen unten
    g.box(ix0 + 0.4, iy0 + 0.4, F0 + 1.0, ix0 + 2.2, iy0 + 1.8, F0 + 1.7, "Stroh")
    g.box(-1.2, 0.5, F0, 0.2, 2.2, F0 + 0.9, "Stroh")
    g.box(ix0 + 0.3, 0.0, F0, ix0 + 1.4, 1.5, F0 + 1.2, "Holz alt")                             # Kisten / Fass-Ecke
    g.prism(ix0 + 1.0, -1.2, F0, 0.4, 1.0, 8, "Faesser rot")
    # Handpflug + Egge als Gerumpel
    g.box(-3.0, iy0 + 0.5, F0, -1.2, iy0 + 0.62, F0 + 0.12, "Rost")
    g.box(-3.0, iy0 + 1.3, F0, -1.2, iy0 + 1.42, F0 + 0.12, "Rost")
    g.box(-3.0, iy0 + 0.5, F0 + 0.12, -2.9, iy0 + 1.42, F0 + 0.2, "Rost")


def stall_zusatz(g, ix0, ix1, iy0, iy1):
    # Boxen mit Trennwaenden (niedrig, 1.1 m) an der Rueckwand, Futtertrog, Heuraufe, Stroh
    for k in range(4):
        x = ix0 + 1.0 + k * 2.6
        g.box(x - 0.05, iy1 - 3.0, F0, x + 0.05, iy1, F0 + 1.1, "Holz alt")
        g.box(x - 1.2, iy1 - 0.3, F0 + 0.5, x + 1.2, iy1 - 0.1, F0 + 0.8, "Holz dunkel")       # Trog
        g.box(x - 1.2, iy1 - 1.8, F0, x + 1.2, iy1 - 0.4, F0 + 0.08, "Stroh")
    g.box(ix1 - 1.6, iy0 + 0.3, F0, ix1 - 0.3, iy0 + 1.3, F0 + 0.8, "Heu")
    g.box(ix0 + 0.3, iy0 + 0.3, F0, ix0 + 1.4, iy0 + 1.2, F0 + 0.6, "Stroh")
    g.prism(ix0 + 4.5, iy0 + 0.9, F0, 0.35, 0.9, 8, "Faesser rot")


def silo(b, x, y):
    n = 16
    r = 2.1
    for (z0, z1, m) in ((0.0, 3.0, "Silo"), (3.0, 6.0, "Stein alt"), (6.0, 9.0, "Silo")):
        b.prism(x, y, z0, r, z1 - z0, n, m)
    for k in range(1, 5):                                                                    # Eisenringe
        b.prism(x, y, 2.0 * k + 0.2, r + 0.05, 0.12, n, "Rost")
    ring = [(x + (r + 0.2) * math.cos(2 * math.pi * k / n), y + (r + 0.2) * math.sin(2 * math.pi * k / n), 9.0) for k in range(n)]
    b.add(ring + [(x, y, 11.0)], [tuple(range(n - 1, -1, -1))] + [(i, (i + 1) % n, n) for i in range(n)], "Dach grau alt")
    b.box(x + r - 0.15, y - 0.25, 0.0, x + r + 0.15, y + 0.25, 8.6, "Metall")             # Leiter (Holme)
    for k in range(18):
        b.box(x + r - 0.2, y - 0.25, 0.4 + k * 0.45, x + r + 0.2, y + 0.25, 0.46 + k * 0.45, "Metall")
    b.box(x - 0.3, y - r - 0.4, 0.0, x + 0.3, y - r, 1.8, "Rost")                           # Auslauf
    b.bx.append((x - r, y - r, 0.0, x + r + 0.2, y + r, 9.0))


def heuballen(b, x, y, theta, z=0.0, n=1):
    for k in range(n):
        BA.zyl_x(b, x - 0.6, x + 0.6, y, z + 0.6 + k * 1.2, 0.6, "Heu" if k % 2 == 0 else "Stroh", n=10)
    b.bx.append((x - 0.6, y - 0.6, z, x + 0.6, y + 0.6, z + 0.6 * 2 * n))


def zaun(b, x0, y0, x1, y1, luecke=None, mat="Holz alt"):
    ln = math.hypot(x1 - x0, y1 - y0)
    n = max(1, int(ln / 2.2))
    ux, uy = (x1 - x0) / ln, (y1 - y0) / ln
    for i in range(n + 1):
        t = ln * i / n
        px, py = x0 + ux * t, y0 + uy * t
        if luecke and luecke[0] < t < luecke[1]:
            continue
        b.box(px - 0.08, py - 0.08, 0.0, px + 0.08, py + 0.08, 1.35, "Holz dunkel")
    for z in (0.55, 1.05):
        a = 0.0
        while a < ln:
            c = min(ln, a + 2.2)
            if luecke and a < luecke[1] and c > luecke[0]:
                if a < luecke[0]:
                    c = luecke[0]
                else:
                    a = luecke[1]
                    continue
            if c - a > 0.1:
                b.beam((x0 + ux * a, y0 + uy * a, z), (x0 + ux * c, y0 + uy * c, z), 0.14, 0.12, mat)
            a = c if not (luecke and a < luecke[0] < c + 0.01) else luecke[1]
            if luecke and a == c and c >= luecke[0] and c < luecke[1]:
                a = luecke[1]


def bauen_hof():
    """Liefert [hof_boden, hof_haus, hof_scheunen, hof_deko]."""
    rnd = random.Random(77)
    bo = Bau("hof_boden")
    z = 0.032
    bo.add([(35.0, 65.0, z), (63.0, 65.0, z), (63.0, 83.0, z), (35.0, 83.0, z)], [(0, 1, 2, 3)], "Hofboden")
    bo.add([(62.0, ZUFAHRT_Y - 2.0, z + 0.003), (90.5, ZUFAHRT_Y - 2.0, z + 0.003), (90.5, ZUFAHRT_Y + 2.0, z + 0.003), (62.0, ZUFAHRT_Y + 2.0, z + 0.003)], [(0, 1, 2, 3)], "Schotterstrasse")
    for dy in (-1.0, 1.0):
        bo.add([(62.0, ZUFAHRT_Y + dy - 0.35, z + 0.006), (90.5, ZUFAHRT_Y + dy - 0.35, z + 0.006), (90.5, ZUFAHRT_Y + dy + 0.35, z + 0.006), (62.0, ZUFAHRT_Y + dy + 0.35, z + 0.006)], [(0, 1, 2, 3)], "Fahrspur")
    bo.add([(46.0, 83.0, z + 0.004), (50.0, 83.0, z + 0.004), (50.0, 89.0, z + 0.004), (46.0, 89.0, z + 0.004)], [(0, 1, 2, 3)], "Pfad")
    # Wohnhaus
    ha = Bau("hof_haus")
    T = dict(S._A, w=13.0, d=8.6, wand="Putz sand", dach="Ziegel", laden="Laden braun", dachform="x", fachwerk=True, gauben=(-3.6, 3.0), kamin=4.2, spiegel=1,
             verfall=1, eingang="vordach_giebel", tuerfarbe="Tuer rot", rh=3.8,
             fw_eg=(-5.0, -2.8, -0.6), fw_og=(-5.0, -2.8, -0.6, 2.4), bw_eg=(-5.0, -2.6, -0.4, 2.0, 4.6), bw_og=(-5.0, -2.6, -0.4, 2.0, 4.6))
    haus(ha, HAUS[0], HAUS[1], 0.0, 0.0, T, seed=311)
    # Scheune und Stall
    sc = Bau("hof_scheunen")
    halle(sc, SCHEUNE[0], SCHEUNE[1], math.pi / 2, 15.0, 10.0, 5.4, 4.2, "Holz alt", "Ziegel dunkel alt", (3.8, 3.8), {"v": (-5.5, 5.5), "h": (-5.2, 5.2), "w": (-2.0, 2.0), "o": ()}, rnd, scheune_zusatz)
    halle(sc, STALL[0], STALL[1], -math.pi / 2, 12.0, 7.0, 3.2, 2.6, "Putz weiss alt", "Ziegel dunkel alt", (1.1, 2.1), {"v": (-4.0, 4.0), "h": (-3.0, 0.0, 3.0), "w": (), "o": (-1.5, 1.5)}, rnd, stall_zusatz)
    silo(sc, *SILO)
    de = Bau("hof_deko")
    S.dorfbrunnen(de, *BRUNNEN)
    heuballen(de, 44.5, 80.5, 0.0, n=2)
    heuballen(de, 46.2, 80.4, 0.0, n=1)
    heuballen(de, 38.0, 85.0, 0.0, n=2)
    for (hx, hy, r_, hh) in ((37.5, 89.5, 2.4, 3.6), (36.5, 86.2, 1.6, 2.4)):               # Heuschober
        BA.kegel(de, hx, hy, 0.0, r_, hh, "Heu", n=9, rot=0.3)
    BA.kegel(de, 62.0, 80.2, 0.0, 2.6, 1.3, "Bruch Erde", n=9)                                # Misthaufen
    BA.kegel(de, 61.2, 78.6, 0.0, 1.2, 0.8, "Stroh", n=7)
    de.box(51.0, 79.6, 0.0, 52.8, 80.0, 0.45, "Holz alt")                                    # Wassertrog
    de.box(51.0, 79.6, 0.45, 52.8, 79.7, 0.8, "Holz alt")
    de.box(51.0, 79.9, 0.45, 52.8, 80.0, 0.8, "Holz alt")
    de.box(51.0, 79.7, 0.4, 52.8, 79.9, 0.5, "Teichwasser")
    # Ackerwagen
    wx, wy = 53.2, 70.0
    de.box(wx - 1.3, wy - 0.8, 0.55, wx + 1.3, wy + 0.8, 0.7, "Holz alt")
    for sy in (-1, 1):
        de.box(wx - 1.3, wy + sy * 0.8 - 0.04, 0.7, wx + 1.3, wy + sy * 0.8 + 0.04, 1.15, "Holz alt")
    de.box(wx - 1.3, wy - 0.8, 0.7, wx - 1.22, wy + 0.8, 1.15, "Holz alt")
    for sx in (-0.9, 0.9):
        for sy in (-0.95, 0.95):
            BA.zyl_x(de, wx + sx - 0.04, wx + sx + 0.04, wy + sy, 0.45, 0.45, "Holz dunkel", n=10)
    de.box(wx + 1.3, wy - 0.05, 0.5, wx + 2.5, wy + 0.05, 0.6, "Holz alt")                    # Deichsel
    # Zaun: Weide Suedseite mit Tor, Ost-/Westflanke
    zaun(de, 34.0, 63.5, 64.0, 63.5, luecke=(11.0, 14.5))
    zaun(de, 34.0, 63.5, 34.0, 66.0)
    zaun(de, 64.0, 63.5, 64.0, 66.0)
    zaun(de, 35.0, 92.5, 35.0, 83.5)
    for k in range(3):                                                                       # Obstbaeume (Staemme mit breiter Krone)
        x, y = 37.0 + 3.0 * k, 92.0 - 0.3 * k
        S.baum(de, x, y, 0.0, k % 2)
    return [bo, ha, sc, de]
