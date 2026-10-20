"""Polybash - Bauernhof zwischen Steinbruch und Ort (x 34..64, y 64..95): Wohnhaus (Fachwerk, begehbar), grosse Scheune mit Heuboden und Treppe, Stall,
Silo, Brunnen, Heu- und Strohhaufen, Misthaufen, Weidezaun und geschwungene Schotterzufahrt von der Werkstrasse. Alles aus den Altbau-Bausteinen (altbau.py, rustik.py)."""
import math
import random

import stadt as S
from stadt import Lok, pbox, wand, aussenwand, fensterschmuck, tuerrahmen, dach, haus, F0, F1, WD, TH
import bahn as BA
import rustik
import baumarten as BM
import talkessel as TK
from burg import Bau

S.FARBEN.update({
    "Gewaechshaus Glas": ((0.72, 0.88, 0.86), 0.05, 0.0, 0.28),
    "Gewaechshaus Rahmen": ((0.86, 0.87, 0.84), 0.5, 0.0),
    "Tomate": ((0.74, 0.12, 0.09), 0.7, 0.0),
    "Hofboden": ((0.40, 0.33, 0.24), 1.0, 0.0),
    "Heu":      ((0.74, 0.62, 0.28), 1.0, 0.0),
    "Stroh":    ((0.82, 0.72, 0.40), 1.0, 0.0),
    "Silo":     ((0.60, 0.60, 0.56), 0.9, 0.0),
})
GH = (76.0, 90.0)                                                      # Gewaechshaus (Halbzylinder, Laengsachse west-ost), Tuer im Westgiebel zum Hof
GH_L, GH_R = 16.0, 3.4
BELEGT = ((33.0, 62.5, 65.0, 93.5), (62.0, 72.0, 90.5, 83.5), (64.0, 84.5, 86.5, 95.0))          # Hof, Zufahrt (geschwungen), Gewaechshaus
HAUS = (48.0, 87.5)                                                    # Wohnhaus 13 x 8.6, Tuer nach Sueden (zum Hof)
SCHEUNE = (38.0, 74.0)                                                 # 15 x 10, Tor nach Osten
STALL = (57.5, 74.0)                                                   # 12 x 7, Tuer nach Westen
SILO = (60.0, 88.0)
BRUNNEN = (48.0, 74.0)
ZUFAHRT_Y = 76.0
ZUFAHRT_PUNKTE = ((90.4, 75.2), (85.0, 76.8), (79.5, 75.9), (74.0, 78.3), (68.6, 80.9), (63.0, 81.3), (58.0, 80.7), (53.6, 80.0))     # Mittellinie des Hofwegs


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
    teile = [(0.0, ln)] if not luecke else [(0.0, luecke[0]), (luecke[1], ln)]
    for (ta, tb) in teile:                                                                    # Spiel: durchgehende, dicke Zaunwand
        if tb - ta > 0.05:
            xa, ya, xb, yb = x0 + ux * ta, y0 + uy * ta, x0 + ux * tb, y0 + uy * tb
            b.kol.append((min(xa, xb) - 0.3, min(ya, yb) - 0.3, 0.0, max(xa, xb) + 0.3, max(ya, yb) + 0.3, 1.4))
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
    # Zufahrt: geschwungener Schotterweg von der Werkstrasse (x ~ 90) in den Hof, zwischen Stall (Nordwand y = 77.5) und Wohnhaus (Suedwand y = 83.2)
    # hindurch zum Brunnen - nicht gerade gegen die Stallrueckwand
    import umgebung as U
    track = ZUFAHRT_PUNKTE
    U.pfad(bo, track, 3.8, z + 0.003, "Schotterstrasse", schritt=2.0)
    for sg in (-1, 1):                                                                       # zwei Fahrspuren (Radspuren) entlang der Mittellinie
        spur = []
        for i, p in enumerate(track):
            a = track[max(0, i - 1)]
            c = track[min(len(track) - 1, i + 1)]
            dx, dy = c[0] - a[0], c[1] - a[1]
            ln = math.hypot(dx, dy) or 1.0
            spur.append((p[0] - dy / ln * 0.95 * sg, p[1] + dx / ln * 0.95 * sg))
        U.pfad(bo, spur, 0.55, z + 0.006, "Fahrspur", schritt=2.0)
    U.pfad(bo, ((65.0, 81.2), (64.6, 84.8), (65.4, 88.0), (67.0, 90.0)), 1.3, z + 0.004, "Pfad", schritt=1.5)               # Fussweg zum Gewaechshaus
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
    BA.kegel(de, 60.6, 67.0, 0.0, 2.4, 1.3, "Bruch Erde", n=9)                                # Misthaufen (abseits des Wegs)
    BA.kegel(de, 59.6, 68.8, 0.0, 1.2, 0.8, "Stroh", n=7)
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
        BM.obstbaum(de, x, y, 0.0, lambda i, k=k: TK._h01(k + 3, i, 515))
    return [bo, ha, sc, de, gewaechshaus()]


def gewaechshaus():
    """Halbzylinderfoermiges Gewaechshaus (16 x 6,8 m, First 3,8 m) aus durchsichtigem Glas (Material mit Alpha) auf einem niedrigen Steinsockel; weisse
    Rippen alle 2 m, Giebelwaende mit Tuer (Westseite, Richtung Hof) und Lueftungsklappe. Innen begehbar: Mittelgang, links und rechts Beete mit Tomaten
    und Salat, am Ostende ein Pflanztisch. Glas und Sockel sind Hindernisse, die Rippen nicht."""
    from math import cos, sin, pi
    b = Bau("hof_gewaechshaus")
    cx, cy = GH
    L, R = GH_L, GH_R
    x0, x1 = cx - L / 2, cx + L / 2
    zs = 0.4                                                       # Sockelhoehe, ab hier beginnt der Bogen
    N = 14
    ang = [pi * k / N for k in range(N + 1)]
    bog = lambda x, k, r=R: (x, cy + r * cos(ang[k]), zs + r * sin(ang[k]))
    rippen = [x0 + L * i / 8 for i in range(9)]
    for i in range(len(rippen) - 1):                               # Glasbahnen zwischen den Rippen (beidseitig sichtbar)
        for k in range(N):
            q = [bog(rippen[i], k), bog(rippen[i], k + 1), bog(rippen[i + 1], k + 1), bog(rippen[i + 1], k)]
            b.add(q, [(0, 1, 2, 3), (3, 2, 1, 0)], "Gewaechshaus Glas")
    for x in rippen:                                               # Rippen: Bogenstuecke als Balken
        for k in range(N):
            b.beam(bog(x, k, R + 0.03), bog(x, k + 1, R + 0.03), 0.07, 0.07, "Gewaechshaus Rahmen")
    for k in range(N + 1):                                         # Laengsstreben
        if k % 2 == 0:
            b.beam(bog(x0, k, R + 0.03), bog(x1, k, R + 0.03), 0.05, 0.05, "Gewaechshaus Rahmen")
    # Giebelwaende (Halbscheiben aus Glas), Westgiebel mit Tuer
    for xg, tuer in ((x1, False), (x0, True)):
        for k in range(N):
            ya, za, yb, zb_ = bog(xg, k)[1:] + bog(xg, k + 1)[1:]
            if tuer and (abs(ya - cy) < 0.75 and abs(yb - cy) < 0.75) and za < 2.6:
                continue
            b.add([(xg, ya, za), (xg, yb, zb_), (xg, yb, zs), (xg, ya, zs)], [(0, 1, 2, 3), (3, 2, 1, 0)], "Gewaechshaus Glas")
    # Tuer im Westgiebel: Rahmen, offenes Blatt
    b.box(x0 - 0.05, cy - 0.85, 0.0, x0 + 0.05, cy - 0.75, 2.5, "Gewaechshaus Rahmen")
    b.bx.pop()
    b.box(x0 - 0.05, cy + 0.75, 0.0, x0 + 0.05, cy + 0.85, 2.5, "Gewaechshaus Rahmen")
    b.bx.pop()
    b.box(x0 - 0.05, cy - 0.85, 2.5, x0 + 0.05, cy + 0.85, 2.6, "Gewaechshaus Rahmen")
    b.bx.pop()
    b.add([(x0 - 0.7, cy - 0.8, 0.0), (x0 - 0.7, cy - 0.8, 2.45), (x0 - 0.05, cy - 0.8, 2.45), (x0 - 0.05, cy - 0.8, 0.0)], [(0, 1, 2, 3), (3, 2, 1, 0)], "Gewaechshaus Glas")
    b.box(x0 - 1.4, cy - 0.9, -0.1, x0 - 0.05, cy + 0.9, 0.05, "Stein")                  # Trittplatte vor der Tuer
    b.bx.pop()
    # Sockel (Stein) beidseitig, Giebelsockel; Boden
    for sg in (-1, 1):
        b.box(x0, cy + sg * R - 0.09, 0.0, x1, cy + sg * R + 0.09, zs, "Stein")
    b.box(x1 - 0.09, cy - R, 0.0, x1 + 0.09, cy + R, zs, "Stein")
    b.box(x0 - 0.09, cy - R, 0.0, x0 + 0.09, cy - 0.85, zs, "Stein")
    b.box(x0 - 0.09, cy + 0.85, 0.0, x0 + 0.09, cy + R, zs, "Stein")
    b.add([(x0, cy - R, 0.03), (x1, cy - R, 0.03), (x1, cy + R, 0.03), (x0, cy + R, 0.03)], [(0, 1, 2, 3)], "Hofboden")
    b.add([(x0 + 0.3, cy - 0.7, 0.045), (x1 - 0.3, cy - 0.7, 0.045), (x1 - 0.3, cy + 0.7, 0.045), (x0 + 0.3, cy + 0.7, 0.045)], [(0, 1, 2, 3)], "Pfad")
    # Hindernisse: Glaswaende als duenne Quader (Hoehe 1,9 m: darueber neigt sich der Bogen nach innen), Ostgiebel, Westgiebel neben der Tuer
    for sg in (-1, 1):
        ya, yb = sorted((cy + sg * (R - 0.1), cy + sg * (R + 0.1)))
        b.bx.append((x0, ya, 0.0, x1, yb, 1.9))
    b.bx.append((x1 - 0.1, cy - R, 0.0, x1 + 0.1, cy + R, 3.9))
    b.bx.append((x0 - 0.1, cy - R, 0.0, x0 + 0.1, cy - 0.85, 3.9))
    b.bx.append((x0 - 0.1, cy + 0.85, 0.0, x0 + 0.1, cy + R, 3.9))
    # Beete links und rechts vom Mittelgang mit Pflanzen
    for sg in (-1, 1):
        ya, yb = sorted((cy + sg * 1.0, cy + sg * 2.5))
        b.box(x0 + 1.0, ya, 0.0, x1 - 2.6, yb, 0.55, "Holz alt")
        b.box(x0 + 1.12, ya + 0.12, 0.5, x1 - 2.72, yb - 0.12, 0.62, "Bruch Erde")
        rnd = random.Random(900 + sg)
        for i in range(8):
            px = x0 + 1.7 + i * 1.45
            for row in (-1, 1):
                py = cy + sg * 1.75 + row * 0.38
                if sg < 0 and i % 2:
                    b.prism(px, py, 0.55, 0.22, 0.14, 6, "Weizen gruen hell")                  # Salat
                    continue
                for (dx, ang_, hh) in ((0.0, 0.0, 1.7 + 0.5 * rnd.random()),):
                    b.beam((px, py, 0.55), (px + 0.05, py, 0.55 + hh), 0.04, 0.04, "Holz alt")  # Stab
                    b.prism(px + 0.02, py, 0.9, 0.28, 0.85, 6, "Weizen gruen")
                    for t in range(3):
                        b.prism(px + 0.15 * (t - 1), py + 0.12, 1.0 + 0.25 * t, 0.07, 0.14, 5, "Tomate")
    b.box(x1 - 2.4, cy - 1.0, 0.0, x1 - 0.5, cy + 1.0, 0.85, "Holz alt")                      # Pflanztisch am Ostende mit Toepfen
    for k in range(5):
        b.prism(x1 - 2.1 + 0.4 * k, cy + (0.45 if k % 2 else -0.45), 0.85, 0.13, 0.2, 7, "Ziegel dunkel alt" if "Ziegel dunkel alt" in S.FARBEN else "Holz dunkel")
    b.box(x0 + 0.5, cy - 2.9, 0.0, x0 + 1.0, cy - 2.4, 0.45, "Holz alt")                        # Giesskannen-Kiste
    return b
