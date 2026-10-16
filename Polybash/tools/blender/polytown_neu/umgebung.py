"""Polybash - Umgebung der Burg: Ringweg, Flughafen mit Landebahn, Vorfeld, Hangars, Tower und Wegen.

Lage (Spielflaeche 0..300 m, Burgmitte C = 150/150, Tore der Burg im Norden und Sueden):
  * Die Ostmauer der Burg hat keinen Ausgang -> die Ostkante der Karte (x = 300) ist die Bezugskante.
  * Ringweg um die Burg (Mittelradius 52 m, ausserhalb des Wassergrabens) mit Zufahrten von den Bruecken.
  * Flughafen im Osten, Landebahn Nord-Sued (150 x 14 m) bei x = 256:
      - westlich der Bahn die Flughafenstrasse (x = 226): an ihr enden die beiden Abzweige vom Ring (45 Grad) und der Zubringer;
        Tower am Nordende, grosser Hangar am Suedende (offen zur Bahn), je ein Fussweg bzw. eine Zufahrt zur Strasse;
      - oestlich der Bahn: Rollweg (parallel, ueber drei Anschluesse an die Bahn und an den Enden um die Bahn herum mit der
        Strasse verbunden), Vorfeld und davor die Reihe aus sechs Hangars, alle zur Burg (nach Westen) offen.
Noch ohne Texturen (nur Farben); die Bahn hat weisse Markierungen: Zebrastreifen an beiden Enden, Aufsetzzonen in beide
Richtungen, in der Mitte nur Striche.
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

# Landebahn (Nord-Sued), Mitte (BX, BY), Laenge BL (150 m = 1,5 x die 100 m des klassischen Polytown), Breite BW
BX, BY, BL, BW = 256.0, 150.0, 150.0, 14.0
BAHN = (BX - BW / 2, BY - BL / 2, BX + BW / 2, BY + BL / 2)          # x0, y0, x1, y1  = (249, 75, 263, 225)
# Flughafenstrasse westlich der Bahn und Rollweg oestlich
SX = 226.0
Y_SUED, Y_NORD = 66.0, 234.0                                          # Umfahrung der Bahnenden
TAXI_X, TAXI_B = 272.0, 8.0
ANSCHLUESSE = (80.0, 150.0, 220.0)                                    # Rollweg-Anschluesse an die Bahn (y)
# Vorfeld und Hangarreihe (offen nach Westen)
VORFELD = (276.0, 88.0, 283.0, 212.0)
REIHE_N, REIHE_B, REIHE_T, REIHE_LUECKE, REIHE_H = 6, 16.0, 12.0, 3.0, 6.0   # Anzahl, Breite (y), Tiefe (x), Abstand, Hoehe
REIHE_X0 = 283.0
# Grosser Hangar am Suedende westlich der Bahn, offen nach Osten (zur Bahn)
HX, HY, HW, HD, HH = 239.5, 90.0, 15.0, 14.0, 6.0                    # Mitte, Breite (x), Tiefe (y), Hoehe
HANGAR = (HX - HW / 2, HY - HD / 2, HX + HW / 2, HY + HD / 2)
# Tower am Nordende westlich der Bahn
TX, TY = 240.0, 212.0
TOWER_ANNEX = (TX - 5.0, TY - 4.0, TX + 5.0, TY + 4.0)

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
    # Flughafenstrasse (Nord-Sued) westlich der Bahn, mit Umfahrung der Bahnenden zum Rollweg
    streifen(b, (SX, Y_SUED), (SX, Y_NORD), BREITE_WEG, Z_WEG, "Weg")
    streifen(b, (SX, Y_SUED), (TAXI_X, Y_SUED), BREITE_WEG, Z_WEG, "Weg")
    streifen(b, (SX, Y_NORD), (TAXI_X, Y_NORD), BREITE_WEG, Z_WEG, "Weg")
    # zwei gerade Abzweige vom Ring (bei +-45 Grad); sie enden dort, wo sie auf die Flughafenstrasse treffen
    for s in (-1, 1):
        u = (math.sqrt(0.5), s * math.sqrt(0.5))
        a0 = (C + u[0] * RING_R, C + u[1] * RING_R)
        d_end = (SX - C) / u[0]
        a1 = (C + u[0] * d_end, C + u[1] * d_end)
        streifen(b, a0, a1, BREITE_WEG, Z_WEG, "Weg")
    # Zubringer vom Ring nach Osten: ueber die Strasse bis zur Bahnmitte (Rollweg-Anschluss von Westen)
    streifen(b, (C + RING_R, C), (BAHN[0], C), BREITE_WEG, Z_WEG, "Weg")
    # Zugang zum Tower (Westtuer) und zum Hangar (Westtuer) von der Strasse
    streifen(b, (SX + BREITE_WEG / 2 - 0.5, TY), (TOWER_ANNEX[0], TY), 3.0, Z_WEG, "Weg")
    streifen(b, (SX + BREITE_WEG / 2 - 0.5, HY), (HANGAR[0], HY), 3.0, Z_WEG, "Weg")
    return b


# ------------------------------------------------------------------ Landebahn, Rollweg, Vorfeld
def landebahn():
    b = Bau("umgebung_landebahn")
    x0, y0, x1, y1 = BAHN
    b.box(x0, y0, -0.12, x1, y1, Z_BAHN, "Piste")
    # Rollweg (parallel zur Bahn, oestlich) mit den Anschluessen an die Bahn
    b.box(TAXI_X - TAXI_B / 2, Y_SUED - BREITE_WEG / 2, -0.12, TAXI_X + TAXI_B / 2, Y_NORD + BREITE_WEG / 2, Z_VORFELD, "Vorfeld")
    for yc in ANSCHLUESSE:
        b.box(x1, yc - TAXI_B / 2, -0.12, TAXI_X - TAXI_B / 2, yc + TAXI_B / 2, Z_VORFELD, "Vorfeld")
    # Vorfeld vor der Hangarreihe (zwischen Rollweg und Hallen)
    vx0, vy0, vx1, vy1 = VORFELD
    b.box(vx0, vy0, -0.12, vx1, vy1, Z_VORFELD - 0.005, "Vorfeld")
    # Vorfeld vor dem grossen Hangar (verbindet ihn mit der Bahn) und Einmuendung der Zufahrt von Westen (breiter Rollweg)
    b.box(HANGAR[2], HANGAR[1] - 1.0, -0.12, x0, HANGAR[3] + 1.0, Z_VORFELD, "Vorfeld")
    b.box(x0 - 12.0, C - 6.0, -0.12, x0, C + 6.0, Z_VORFELD, "Vorfeld")
    # ---- weisse Markierungen (Oberkante Z_MARK) ----
    m = "Markierung weiss"

    def mk(xa, ya, xb, yb):
        b.box(xa, ya, Z_BAHN, xb, yb, Z_MARK, m)

    # Mittellinie: Striche 4 m lang, alle 8 m, symmetrisch zur Bahnmitte, zwischen den Schwellen (17 m Abstand zu den Enden)
    for k in range(15):
        ya = BY - 58.0 + 8.0 * k
        mk(BX - 0.2, ya, BX + 0.2, ya + 4.0)
    for ende in (-1, 1):                                          # -1 = Suedende, +1 = Nordende; jede Richtung gleich ausgestattet
        def y_ab(d0, d1):
            """Abstand d0..d1 (m) von der Schwelle am Ende -> (ya, yb)"""
            return (y0 + d0, y0 + d1) if ende < 0 else (y1 - d1, y1 - d0)
        # Zebrastreifen an der Schwelle: 5 Streifen je Seite, 9 m lang, 3 m hinter dem Bahnende
        ya, yb = y_ab(3.0, 12.0)
        for k in range(5):
            off = 0.9 + 1.2 * k
            for sgn in (-1, 1):
                mk(BX + sgn * off - 0.4, ya, BX + sgn * off + 0.4, yb)
        # Aufsetzzonen-Markierungen (Touchdown) in dieser Anflugrichtung
        for d0, anz in ((22.0, 3), (32.0, 2)):                    # Gruppen aus 3 und 2 Balken je Seite (5 m lang)
            ya, yb = y_ab(d0, d0 + 5.0)
            for k in range(anz):
                off = 2.2 + 0.9 * k
                for sgn in (-1, 1):
                    mk(BX + sgn * off - 0.22, ya, BX + sgn * off + 0.22, yb)
        ya, yb = y_ab(42.0, 54.0)                                 # Zielpunkt: zwei breite Balken
        for sgn in (-1, 1):
            mk(BX + sgn * 4.4 - 0.9, ya, BX + sgn * 4.4 + 0.9, yb)
        for d0 in (60.0, 69.0):                                   # je ein Balken pro Seite
            ya, yb = y_ab(d0, d0 + 5.0)
            for sgn in (-1, 1):
                mk(BX + sgn * 2.8 - 0.22, ya, BX + sgn * 2.8 + 0.22, yb)
    return b


# ------------------------------------------------------------------ Hangars
def halle(b, x0, y0, x1, y1, offen, h=6.0, kisten=False):
    """Halle mit Boden, Waenden und Dach; 'offen' = Seite ohne Wand ('W' oder 'O'); das Dach ragt dort 1,2 m ueber."""
    t = 0.4
    b.box(x0, y0, -0.12, x1, y1, 0.07, "Hangar Boden")
    b.box(x0, y0, 0.07, x1, y0 + t, h, "Hangar Wand")                                    # Suedwand
    b.box(x0, y1 - t, 0.07, x1, y1, h, "Hangar Wand")                                    # Nordwand
    if offen == "W":
        b.box(x1 - t, y0, 0.07, x1, y1, h, "Hangar Wand")                                # Rueckwand Ost
        b.box(x0 - 1.2, y0 - 0.3, h, x1 + 0.3, y1 + 0.3, h + 0.45, "Hangar Dach")
        xs = [x0 + 2.0 + k * (x1 - x0 - 4.0) / 2.0 for k in range(3)]
    else:
        b.box(x0, y0, 0.07, x0 + t, y1, h, "Hangar Wand")                                # Rueckwand West
        b.box(x0 - 0.3, y0 - 0.3, h, x1 + 1.2, y1 + 0.3, h + 0.45, "Hangar Dach")
        xs = [x0 + 2.0 + k * (x1 - x0 - 4.0) / 2.0 for k in range(3)]
    for xx in xs:                                                                        # Dachbinder unter dem Dach
        b.box(xx - 0.15, y0 + t, h - 0.45, xx + 0.15, y1 - t, h, "Metall")
    if kisten:
        xk = x0 + 1.0 if offen == "O" else x1 - 3.4
        b.box(xk, y1 - 3.4, 0.07, xk + 2.4, y1 - 1.0, 1.3, "Kiste")
        b.box(xk, y1 - 3.4, 1.3, xk + 1.2, y1 - 2.2, 2.6, "Kiste")
        b.box(xk, y0 + 1.0, 0.07, xk + 3.4, y0 + 2.2, 1.0, "Metall")


def hangar():
    """Grosser Hangar am Suedende westlich der Bahn, offen nach Osten; Zugang durch die Westtuer von der Strasse."""
    b = Bau("umgebung_hangar")
    x0, y0, x1, y1 = HANGAR
    halle(b, x0, y0, x1, y1, "O", HH, kisten=True)
    b.box(x0 - 0.06, HY - 0.55, 0.07, x0, HY + 0.55, 2.3, "Tuer")
    for dx in (-3.5, 3.5):
        B.fenster(b, HX + dx, y1, 3.0, 1.6, 1.1, 0, 1)
        B.fenster(b, HX + dx, y0, 3.0, 1.6, 1.1, 0, -1)
    for dy in (-3.5, 3.5):
        B.fenster(b, x0, HY + dy, 3.0, 1.6, 1.1, -1, 0)
    return b


def hangarreihe():
    """Sechs gleiche Hangars nebeneinander zwischen Vorfeld und Bergen, alle nach Westen (zur Burg) offen."""
    b = Bau("umgebung_hangarreihe")
    gesamt = REIHE_N * REIHE_B + (REIHE_N - 1) * REIHE_LUECKE
    ya0 = BY - gesamt / 2
    for i in range(REIHE_N):
        y0 = ya0 + i * (REIHE_B + REIHE_LUECKE)
        y1 = y0 + REIHE_B
        x0, x1 = REIHE_X0, REIHE_X0 + REIHE_T
        halle(b, x0, y0, x1, y1, "W", REIHE_H, kisten=(i % 2 == 0))
        B.fenster(b, x1, (y0 + y1) / 2, 3.4, 2.0, 1.2, 1, 0)                              # Fenster in der Rueckwand
    return b


# ------------------------------------------------------------------ Tower
def tower():
    b = Bau("umgebung_tower")
    # Sockelgebaeude 10 x 8 m, 3,4 m hoch, Flachdach; Schaft 4 x 4 m bis 13 m; Kanzel 7 x 7 m mit Glasband
    ax0, ay0, ax1, ay1 = TOWER_ANNEX
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
    for sx in (-1, 1):                                                                       # Eckpfosten
        for sy in (-1, 1):
            b.box(TX + sx * 3.5 - 0.15, TY + sy * 3.5 - 0.15, 13.9, TX + sx * 3.5 + 0.15, TY + sy * 3.5 + 0.15, 15.2, "Tower Beton")
    b.box(kx0 - 0.5, ky0 - 0.5, 15.2, kx1 + 0.5, ky1 + 0.5, 15.6, "Tower Dach")               # Kanzeldach
    b.box(TX - 0.08, TY - 0.08, 15.6, TX + 0.08, TY + 0.08, 19.0, "Metall")                   # Antennenmast
    b.box(TX - 1.2, TY - 0.05, 18.0, TX + 1.2, TY + 0.05, 18.2, "Metall")                     # Querantenne
    b.box(TX + 1.6, TY + 1.6, 15.6, TX + 2.4, TY + 2.4, 16.4, "Metall")                       # Geraetekasten
    # Eingang auf der Westseite (zur Strasse), Fenster an den uebrigen Seiten des Sockelgebaeudes
    b.box(ax0 - 0.06, TY - 0.55, 0.0, ax0, TY + 0.55, 2.3, "Tuer")
    for dy in (-2.4, 2.4):
        B.fenster(b, ax1, TY + dy, 1.9, 1.5, 1.0, 1, 0)
    for dx in (-3.2, 0.0, 3.2):
        B.fenster(b, TX + dx, ay0, 1.9, 1.5, 1.0, 0, -1)
        B.fenster(b, TX + dx, ay1, 1.9, 1.5, 1.0, 0, 1)
    return b


def baue_alles():
    """Gibt die Baugruppen zurueck (ohne bpy aufrufbar)."""
    return [wege(), landebahn(), hangar(), hangarreihe(), tower()]


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
