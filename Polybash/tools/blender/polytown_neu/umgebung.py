"""Polybash - Umgebung der Burg: Ringweg, Abzweige zu den Ostecken, Landebahn mit Markierungen, Hangar und Tower.

Lage (Spielflaeche 0..300 m, Burgmitte C = 150/150, Tore der Burg im Norden und Sueden):
  * Die Ostmauer der Burg hat keinen Ausgang -> die Ostkante der Karte (x = 300) ist die Bezugskante.
  * Ringweg um die Burg (Mittelradius 52 m, ausserhalb des Wassergrabens), dazu Zufahrten von den Bruecken (Nord/Sued)
    zum Ring und zwei gerade Abzweige vom Ring in Richtung der beiden Eckpunkte (300/300) und (300/0).
  * Landebahn parallel zur Ostkante (Nord-Sued, 100 x 14 m wie die Landebahn des klassischen Polytown), 30 m von der Kante.
  * Westlich der Bahn: Hangar (offen zur Bahn, am Suedende) und Tower (in der Mitte), Zubringer vom Ring, Wege.
Noch ohne Texturen (nur Farben); die Bahn hat bereits weisse Markierungen wie eine echte Landebahn.
Ohne bpy testbar (baue_alles); bauen() legt die Objekte in der Collection "Umgebung" an.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bpy  # noqa: E402
import talkessel as T  # noqa: E402
import burg as B  # noqa: E402
from burg import Bau  # noqa: E402

C = B.C
BREITE_WEG = 8.0          # Fahrbahnbreite aller Wege (wie die Bruecken der Burg)
RING_R = 52.0             # Mittelradius des Ringwegs (Innenkante 48 m: Graben endet bei ca. 45,6 m)
Z_RING, Z_WEG = 0.050, 0.051           # Oberkanten der Wege (knapp ueber der Wiese bei z = 0)
Z_BAHN, Z_VORFELD, Z_MARK = 0.080, 0.070, 0.100

# Landebahn (Nord-Sued), Mitte (BX, BY)
BX, BY, BL, BW = 270.0, 150.0, 100.0, 14.0
BAHN = (BX - BW / 2, BY - BL / 2, BX + BW / 2, BY + BL / 2)          # x0, y0, x1, y1
# Hangar am Suedende, offen nach Osten (zur Bahn)
HX, HY, HW, HD, HH = 238.0, 112.0, 15.0, 14.0, 6.0                   # Mitte, Breite (x), Tiefe (y), Hoehe
HANGAR = (HX - HW / 2, HY - HD / 2, HX + HW / 2, HY + HD / 2)
# Tower westlich der Bahnmitte
TX, TY = 252.0, 161.0
ZUBRINGER_Y = C                                                       # Zubringer vom Ring nach Osten

FARBEN = {
    "Weg":             ((0.30, 0.29, 0.27), 0.95, 0.0),
    "Piste":           ((0.24, 0.24, 0.27), 0.95, 0.0),
    "Vorfeld":         ((0.27, 0.27, 0.29), 0.95, 0.0),
    "Markierung weiss": ((0.93, 0.93, 0.90), 0.8, 0.0),
    "Hangar Wand":     ((0.55, 0.57, 0.60), 0.9, 0.0),
    "Hangar Dach":     ((0.40, 0.42, 0.45), 0.8, 0.0),
    "Hangar Boden":    ((0.50, 0.50, 0.50), 0.95, 0.0),
    "Tower Beton":     ((0.68, 0.67, 0.64), 0.9, 0.0),
    "Tower Dach":      ((0.35, 0.36, 0.38), 0.8, 0.0),
    "Glas":            ((0.12, 0.20, 0.26), 0.1, 0.0),
    "Tuer":            ((0.30, 0.20, 0.14), 0.8, 0.0),
    "Kiste":           ((0.45, 0.34, 0.20), 0.9, 0.0),
    "Metall":          ((0.30, 0.32, 0.30), 0.5, 0.0),
    "Fenster":         ((0.07, 0.09, 0.11), 0.2, 0.0),
    "Rahmen":          ((0.84, 0.83, 0.78), 0.9, 0.0),
}


# ------------------------------------------------------------------ flache Wegstuecke (Oberflaechen)
def streifen(b, p0, p1, w, z, mat):
    """Gerades Wegstueck von p0 nach p1 (Breite w) als ebene Flaeche bei Hoehe z, Normale nach oben."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy)
    nx, ny = -dy / ln * w / 2, dx / ln * w / 2
    v = [(p0[0] + nx, p0[1] + ny, z), (p0[0] - nx, p0[1] - ny, z), (p1[0] - nx, p1[1] - ny, z), (p1[0] + nx, p1[1] + ny, z)]
    b.add(v, [(0, 1, 2, 3)], mat)


def ring(b, r, w, z, mat, n=120):
    """Kreisring (Mittelradius r, Breite w) um die Burgmitte aus n Vierecken, Normale nach oben."""
    ri, ra = r - w / 2, r + w / 2
    v = []
    for i in range(n):
        a = 2 * math.pi * i / n
        v += [(C + ri * math.cos(a), C + ri * math.sin(a), z), (C + ra * math.cos(a), C + ra * math.sin(a), z)]
    f = []
    for i in range(n):
        j = (i + 1) % n
        f.append((2 * i, 2 * i + 1, 2 * j + 1, 2 * j))                 # innen, aussen, aussen weiter, innen weiter
    b.add(v, f, mat)


def platte(b, x0, y0, x1, y1, z_oben, mat, dicke=0.12):
    b.box(x0, y0, z_oben - dicke, x1, y1, z_oben, mat)


# ------------------------------------------------------------------ Wege
def wege():
    b = Bau("umgebung_wege")
    ring(b, RING_R, BREITE_WEG, Z_RING, "Weg")
    # Zufahrten von den beiden Bruecken (Bruecken enden bei C +- 36,5) bis zur Mitte des Rings
    for s in (-1, 1):
        streifen(b, (C, C + s * (B.A + 11.0)), (C, C + s * RING_R), BREITE_WEG, Z_WEG, "Weg")
    # zwei gerade Abzweige vom Ring (bei +-45 Grad) in Richtung der Ostecken (300/300) und (300/0), enden 9 m vor der Ecke
    for s in (-1, 1):
        ex, ey = C + 150.0, C + s * 150.0
        d = math.hypot(ex - C, ey - C)
        u = ((ex - C) / d, (ey - C) / d)
        a0 = (C + u[0] * RING_R, C + u[1] * RING_R)
        a1 = (C + u[0] * (d - 9.0), C + u[1] * (d - 9.0))
        streifen(b, a0, a1, BREITE_WEG, Z_WEG, "Weg")
    # Zubringer vom Ring nach Osten bis zur Landebahn (Rollweg-Einmuendung)
    streifen(b, (C + RING_R, ZUBRINGER_Y), (BAHN[0], ZUBRINGER_Y), BREITE_WEG, Z_WEG, "Weg")
    # Fussweg zum Tower, Zufahrt zur Nordtuer des Hangars
    streifen(b, (TX, ZUBRINGER_Y + BREITE_WEG / 2), (TX, TY - 4.0), 3.0, Z_WEG, "Weg")
    streifen(b, (HX, ZUBRINGER_Y - BREITE_WEG / 2), (HX, HANGAR[3] + 0.5), 4.0, Z_WEG, "Weg")
    return b


# ------------------------------------------------------------------ Landebahn
def landebahn():
    b = Bau("umgebung_landebahn")
    x0, y0, x1, y1 = BAHN
    b.box(x0, y0, -0.12, x1, y1, Z_BAHN, "Piste")
    # Vorfeld vor dem Hangar (verbindet Hangar und Bahn)
    b.box(HANGAR[2], HANGAR[1] - 1.0, -0.12, x0, HANGAR[3] + 1.0, Z_VORFELD, "Vorfeld")
    # Rollweg-Einmuendung des Zubringers (breiter, damit die Einfahrt zur Bahn glatt ist)
    b.box(x0 - 14.0, ZUBRINGER_Y - 6.0, -0.12, x0, ZUBRINGER_Y + 6.0, Z_VORFELD, "Vorfeld")
    # ---- weisse Markierungen wie bei einer echten Landebahn (Oberkante Z_MARK) ----
    m = "Markierung weiss"
    zb = Z_BAHN

    def mk(xa, ya, xb, yb):
        b.box(xa, ya, zb, xb, yb, Z_MARK, m)

    # Randlinien ueber die ganze Laenge
    for sgn in (-1, 1):
        mk(BX + sgn * (BW / 2 - 0.6) - 0.15, y0 + 0.5, BX + sgn * (BW / 2 - 0.6) + 0.15, y1 - 0.5)
    # Mittellinie: Striche 4 m lang, alle 8 m, zwischen den Schwellen (symmetrisch zur Mitte)
    for k in range(9):
        ya = BY - 34.0 + 8.0 * k
        mk(BX - 0.2, ya, BX + 0.2, ya + 4.0)
    for ende in (-1, 1):                                          # -1 = Suedende, +1 = Nordende
        def y_von_ende(d0, d1):
            """Abstand d0..d1 (m) von der Schwelle am jeweiligen Ende -> (ya, yb)"""
            if ende < 0:
                return y0 + d0, y0 + d1
            return y1 - d1, y1 - d0
        # Schwellenstreifen ("Klaviertasten"): 8 Streifen, 6 m lang, 2 m hinter der Schwelle
        ya, yb = y_von_ende(2.0, 8.0)
        for k in range(4):
            off = 1.1 + 1.4 * k
            for sgn in (-1, 1):
                mk(BX + sgn * off - 0.4, ya, BX + sgn * off + 0.4, yb)
        # Zielpunkt-Markierung: zwei breite Balken, 28..38 m hinter der Schwelle
        ya, yb = y_von_ende(28.0, 38.0)
        for sgn in (-1, 1):
            mk(BX + sgn * 3.4 - 0.8, ya, BX + sgn * 3.4 + 0.8, yb)
        # Aufsetzzonen-Markierung: zwei Paare kurzer Balken bei 40 und 45 m
        for d0 in (40.0, 45.0):
            ya, yb = y_von_ende(d0, d0 + 3.0)
            for off in (2.2, 4.6):
                for sgn in (-1, 1):
                    mk(BX + sgn * off - 0.3, ya, BX + sgn * off + 0.3, yb)
    return b


# ------------------------------------------------------------------ Hangar
def hangar():
    b = Bau("umgebung_hangar")
    x0, y0, x1, y1 = HANGAR
    h, t = HH, 0.4
    cx = HX
    b.box(x0, y0, -0.12, x1, y1, 0.07, "Hangar Boden")                                  # Boden
    b.box(x0, y0, 0.07, x0 + t, y1, h, "Hangar Wand")                                   # Rueckwand (West)
    b.box(x0, y0, 0.07, x1, y0 + t, h, "Hangar Wand")                                   # Suedwand
    b.box(x0, y1 - t, 0.07, x1, y1, h, "Hangar Wand")                                   # Nordwand
    b.box(x0 - 0.5, y0 - 0.5, h, x1 + 1.2, y1 + 0.5, h + 0.5, "Hangar Dach")            # Dach mit Ueberstand zur Bahn
    for k in range(4):                                                                   # Dachtraeger sichtbar unter dem Dach
        xx = x0 + 1.0 + k * (HW - 2.0) / 3.0
        b.box(xx - 0.15, y0 + t, h - 0.45, xx + 0.15, y1 - t, h, "Metall")
    # Nordtuer (Zugang vom Weg) und Fenster
    b.box(cx - 0.55, y1, 0.07, cx + 0.55, y1 + 0.06, 2.3, "Tuer")
    for dx in (-4.5, 4.5):
        B.fenster(b, cx + dx, y1, 3.0, 1.6, 1.1, 0, 1)
        B.fenster(b, cx + dx, y0, 3.0, 1.6, 1.1, 0, -1)
    for dy in (-3.5, 3.5):
        B.fenster(b, x0, HY + dy, 3.0, 1.6, 1.1, -1, 0)
    # Einrichtung: Kisten und Werkbank im Hangar
    b.box(x0 + 1.0, y1 - 3.4, 0.07, x0 + 3.4, y1 - 1.0, 1.3, "Kiste")
    b.box(x0 + 1.0, y1 - 3.4, 1.3, x0 + 2.2, y1 - 2.2, 2.6, "Kiste")
    b.box(x0 + 1.0, y0 + 1.0, 0.07, x0 + 4.4, y0 + 2.2, 1.0, "Metall")
    return b


# ------------------------------------------------------------------ Tower
def tower():
    b = Bau("umgebung_tower")
    # Sockelgebaeude 10 x 8 m, 3,4 m hoch, Flachdach; Schaft 4 x 4 m bis 13 m; Kanzel 7 x 7 m mit Glasband
    ax0, ay0, ax1, ay1 = TX - 5.0, TY - 4.0, TX + 5.0, TY + 4.0
    b.box(ax0, ay0, 0.0, ax1, ay1, 3.4, "Tower Beton")
    b.box(ax0 - 0.2, ay0 - 0.2, 3.4, ax1 + 0.2, ay1 + 0.2, 3.7, "Tower Dach")                 # Dachrand
    b.box(TX - 2.0, TY - 2.0, 3.7, TX + 2.0, TY + 2.0, 13.0, "Tower Beton")                   # Schaft
    for zz in (6.5, 9.5):                                                                    # Fensterschlitze am Schaft
        for sx in (-1, 1):
            b.box(TX + sx * 2.0, TY - 0.6, zz, TX + sx * 2.05, TY + 0.6, zz + 0.7, "Fenster")
        for sy in (-1, 1):
            b.box(TX - 0.6, TY + sy * 2.0, zz, TX + 0.6, TY + sy * 2.05, zz + 0.7, "Fenster")
    kx0, ky0, kx1, ky1 = TX - 3.5, TY - 3.5, TX + 3.5, TY + 3.5
    b.box(kx0 - 0.3, ky0 - 0.3, 13.0, kx1 + 0.3, ky1 + 0.3, 13.3, "Tower Dach")               # Kanzelboden
    b.box(kx0, ky0, 13.3, kx1, ky1, 13.9, "Tower Beton")                                      # Bruestung
    b.box(kx0, ky0, 13.9, kx1, ky1, 15.2, "Glas")                                             # Glasband rundum
    for sx in (-1, 1):                                                                       # Eckpfosten und Mittelpfosten
        for sy in (-1, 1):
            b.box(TX + sx * 3.5 - 0.15, TY + sy * 3.5 - 0.15, 13.9, TX + sx * 3.5 + 0.15, TY + sy * 3.5 + 0.15, 15.2, "Tower Beton")
    b.box(kx0 - 0.5, ky0 - 0.5, 15.2, kx1 + 0.5, ky1 + 0.5, 15.6, "Tower Dach")               # Kanzeldach
    b.box(TX - 0.08, TY - 0.08, 15.6, TX + 0.08, TY + 0.08, 19.0, "Metall")                   # Antennenmast
    b.box(TX - 1.2, TY - 0.05, 18.0, TX + 1.2, TY + 0.05, 18.2, "Metall")                     # Querantenne
    b.box(TX + 1.6, TY + 1.6, 15.6, TX + 2.4, TY + 2.4, 16.4, "Metall")                       # Geraetekasten
    # Eingang (Sued, zum Weg), Fenster am Sockelgebaeude
    b.box(TX - 0.55, ay0 - 0.06, 0.0, TX + 0.55, ay0, 2.3, "Tuer")
    for dx in (-3.2, 3.2):
        B.fenster(b, TX + dx, ay0, 1.9, 1.5, 1.0, 0, -1)
    for dx in (-3.2, 0.0, 3.2):
        B.fenster(b, TX + dx, ay1, 1.9, 1.5, 1.0, 0, 1)
    return b


def baue_alles():
    """Gibt die Baugruppen zurueck (ohne bpy aufrufbar)."""
    return [wege(), landebahn(), hangar(), tower()]


def bauen():
    """Legt Wege, Landebahn, Hangar und Tower in der Szene an (Collection "Umgebung"). Rueckgabe: Zahl der Flaechen."""
    coll = T.collection("Umgebung")
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
