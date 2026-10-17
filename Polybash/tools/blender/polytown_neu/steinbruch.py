"""Polybash - Steinbruch in der Suedwestecke der Map (Norden = +y): abgetreppte Grube mit Rampe, Schraegaufzug, Brecherturm, Verladebunker ueber dem
Gleis, Werkstatt (begehbar), Sprengstoffhaeuschen, Bagger, Kipper, Fels- und Schotterhaufen.

Die Grube ist ein Loch in der Wiese (talkessel.wiesen_netz) mit selbst gebautem Boden aus 1,25-m-Zellen (Hoehenfeld mit Baenken zu je 3 m Hoehe).
Wird von stadt.baue_alles() eingebunden."""
import math

import stadt as S
from stadt import Lok, pbox, wand, aussenwand, fensterschmuck, tuerrahmen, dach, F0, WD, TH
import bahn as BA
import oeffentlich as O
import talkessel as T
from burg import Bau

S.FARBEN.update({
    "Tank gruen":  ((0.20, 0.30, 0.22), 0.6, 0.2),
    "Faesser rot": ((0.60, 0.15, 0.10), 0.6, 0.2),
    "Reifen":      ((0.07, 0.07, 0.07), 1.0, 0.0),
    "Kipper blau": ((0.18, 0.30, 0.45), 0.7, 0.1),
})

PIT = (15.0, 15.0, 60.0, 55.0)                  # Loch in der Wiese (Raster 5 m)
PIT_Z = -9.0
G = 1.25                                          # Zellengroesse der Grube
RAMPE = (15.0, 20.0)                              # Rampe: y-Streifen am Suedrand, steigt von x = 15 (z = -9) nach x = 60 (z = 0)
ZONE = (8.0, 8.0, 100.0, 74.0)                   # ebener Baugrund (STADT_ZONEN)
YARD = (60.0, 14.0, 90.0, 60.0)                  # Schotterplatz oestlich der Grube
GLEIS_Y = BA.GLEIS_Y[3]                          # Verladegleis (y = 27)
WERKSTATT = (74.0, 63.0)                         # Mitte (16 x 10 m, Tuer nach Sueden)
BRECHER = (62.0, 30.0, 68.0, 36.0)
BUNKER = (72.0, 22.0, 80.0, 32.0)
SPRENG = (28.0, 64.0)                            # Sprengstoffhaeuschen
BELEGT = ((12.0, 12.0, 63.0, 58.0),              # Grube mit Rand
          (60.0, 12.0, 100.0, 64.0),             # Schotterhof, Brecher, Bunker, Lager, Tor, Waechterhaus
          (62.0, 55.0, 86.0, 70.0),              # Werkstatt mit Vorplatz
          (24.0, 60.0, 33.0, 68.0))              # Sprengstoffhaeuschen


# ------------------------------------------------------------------ Hoehenfeld der Grube
def pit_z(x, y):
    """Hoehe des Grubenbodens in der Zelle mit Mittelpunkt (x, y): Rampe, Bucht am Rampenende, Baenke (3 m), Sohle (-9 m)."""
    if RAMPE[0] <= y < RAMPE[1]:
        zr = max(PIT_Z, -9.0 * (PIT[2] - x) / (PIT[2] - PIT[0]))
        return -0.25 * math.floor(-zr / 0.25)                 # Stufen von genau 0,25 m (Zellenmitte -0,125 -> 0; -0,375 -> -0,25; ...)
    if x < 36.0 and y < 32.0:
        return PIT_Z
    d = min(x - PIT[0], PIT[3] - y) + 3.0 * (T.noise(x / 10.0, y / 10.0, 91) - 0.5)
    k = 0 if d < 7.0 else 1 if d < 14.0 else 2 if d < 21.0 else 3
    return -3.0 * k


def zellen():
    ni, nj = int(round((PIT[2] - PIT[0]) / G)), int(round((PIT[3] - PIT[1]) / G))
    return ni, nj, {(i, j): pit_z(PIT[0] + (i + 0.5) * G, PIT[1] + (j + 0.5) * G) for i in range(ni) for j in range(nj)}


def _saeule(b, x0, y0, x1, y1, zlow, zhigh, top, tag):
    """Felssaeule von zlow bis zhigh in Scheiben von 1,5 m (Schichtung: abwechselnd hell/dunkel); oberste Scheibe mit Material top."""
    z1, k = zhigh, 0
    strata = ("Bruch Fels", "Bruch Fels dunkel", "Bruch Fels hell", "Bruch Fels")
    while z1 > zlow + 1e-6:
        z0 = max(zlow, z1 - 1.5)
        b.box(x0, y0, z0, x1, y1, z1, top if k == 0 else strata[(k + tag) % 4])
        z1, k = z0, k + 1


def _zlow(Z, i, j):
    z = Z[(i, j)]
    m = min([z] + [v for v in (Z.get((i + 1, j)), Z.get((i - 1, j)), Z.get((i, j + 1)), Z.get((i, j - 1))) if v is not None])
    return min(m, z - 0.3)


def _top(z, y):
    if z >= -0.01:
        return "Bruch Erde"
    if z <= PIT_Z + 0.01 or RAMPE[0] <= y < RAMPE[1]:
        return "Schotter"
    return "Bruch Fels hell"


def grube(b):
    """Baut Boden und Waende der Grube; Rueckgabe: Liste der Zaunsegmente (fuer Tests)."""
    ni, nj, Z = zellen()
    for j in range(nj):
        i = 0
        while i < ni:
            z, zl = Z[(i, j)], _zlow(Z, i, j)
            i1 = i + 1
            while i1 < ni and Z[(i1, j)] == z and abs(_zlow(Z, i1, j) - zl) < 1e-9:
                i1 += 1
            y0, y1 = PIT[1] + j * G, PIT[1] + (j + 1) * G
            _saeule(b, PIT[0] + i * G, y0, PIT[0] + i1 * G, y1, zl, z, _top(z, y0), i + 2 * j)
            i = i1
    # Randwand an der Wiesenkante (Aussenseite, oben bei -0,02 unter der Wiese)
    for j in range(nj):
        for (i, sx) in ((0, -1), (ni - 1, 1)):
            z = Z[(i, j)]
            if z < -0.01:
                x0 = PIT[0] - 1.0 if sx < 0 else PIT[2]
                _saeule(b, x0, PIT[1] + j * G, x0 + 1.0, PIT[1] + (j + 1) * G, z - 0.3, -0.02, "Bruch Fels", j)
    for i in range(ni):
        for (j, sy) in ((0, -1), (nj - 1, 1)):
            z = Z[(i, j)]
            if z < -0.01:
                y0 = PIT[1] - 1.0 if sy < 0 else PIT[3]
                _saeule(b, PIT[0] + i * G, y0, PIT[0] + (i + 1) * G, y0 + 1.0, z - 0.3, -0.02, "Bruch Fels", i + 3)
    return zaeune(b, Z, ni, nj)


def _zaun_segment(b, x0, y0, x1, y1, z, mat="Metall"):
    """Gelaender (Pfosten alle ~2,5 m, zwei Holme von 14 cm Staerke) entlang einer achsparallelen Strecke in Hoehe z."""
    ln = max(abs(x1 - x0), abs(y1 - y0))
    n = max(1, int(round(ln / 2.5)))
    for i in range(n + 1):
        px, py = x0 + (x1 - x0) * i / n, y0 + (y1 - y0) * i / n
        b.box(px - 0.06, py - 0.06, z, px + 0.06, py + 0.06, z + 1.1, mat)
    for (za, zb_) in ((0.5, 0.57), (1.0, 1.07)):
        b.box(min(x0, x1) - (0.07 if x0 == x1 else 0.0), min(y0, y1) - (0.07 if y0 == y1 else 0.0), z + za,
              max(x0, x1) + (0.07 if x0 == x1 else 0.0), max(y0, y1) + (0.07 if y0 == y1 else 0.0), z + zb_, mat)


def zaeune(b, Z, ni, nj):
    """Gelaender/Leitplanken: um jede begehbare Kante mit mehr als 0,3 m Absturz (Wiesenkante, Bankkanten) - ausser an der Rampeneinfahrt."""
    seg = []
    for j in range(nj):
        for i in range(ni):
            z = Z[(i, j)]
            x0, y0 = PIT[0] + i * G, PIT[1] + j * G
            for (di, dj, kante) in ((1, 0, (x0 + G, y0, x0 + G, y0 + G)), (-1, 0, (x0, y0, x0, y0 + G)), (0, 1, (x0, y0 + G, x0 + G, y0 + G)), (0, -1, (x0, y0, x0 + G, y0))):
                n = Z.get((i + di, j + dj))
                if n is None:                                                    # Kante zur Wiese: Zaun an der Aussenseite, wenn die Zelle tiefer liegt
                    if z < -0.3:
                        kx0, ky0, kx1, ky1 = kante
                        o = 0.0
                        if di:
                            kx0 = kx1 = kx0 + di * o
                        else:
                            ky0 = ky1 = ky0 + dj * o
                        # Einfahrt der Rampe (Ostkante, Zellen y 15..20) bleibt offen
                        if di == 1 and RAMPE[0] <= ky0 and ky1 <= RAMPE[1]:
                            continue
                        seg.append((kx0, ky0, kx1, ky1, 0.0))
                elif z - n > 0.3 and z > -0.01:                                      # begehbare Hoehe (Wiesenniveau) neben tieferer Zelle
                    kx0, ky0, kx1, ky1 = kante
                    o = 0.05
                    if di:
                        kx0 = kx1 = kx0 - di * o
                    else:
                        ky0 = ky1 = ky0 - dj * o
                        if dj == 1 and RAMPE[0] <= y0 < RAMPE[1] and i == ni - 1:                 # Rampenausgang: Zaun bis zum Randzaun verlaengern (kein Spalt)
                            kx1 += 0.3
                    seg.append((kx0, ky0, kx1, ky1, z))
                elif RAMPE[0] <= y0 < RAMPE[1] and dj == 1 and z - n > 0.3:           # Rampe: Leitplanke zur tieferen Nordseite
                    seg.append((x0 - (0.3 if i == 0 else 0.0), y0 + G - 0.08, x0 + G + (0.3 if i == ni - 1 else 0.0), y0 + G - 0.08, z, "platte"))
    for s in seg:
        if len(s) == 6:
            b.box(s[0], s[1] - 0.06, s[4], s[2], s[1] + 0.08, s[4] + 0.95, "Bruch Beton")
            b.box(s[0], s[1] - 0.08, s[4] + 0.95, s[2], s[1] + 0.1, s[4] + 1.02, "Metall")
        else:
            _zaun_segment(b, *s)
    return seg


# ------------------------------------------------------------------ Schraegaufzug, Brecherturm, Verladebunker
HOIST_Y = 32.5
HOIST_A = (38.5, -8.4)                           # unten (x, z)
HOIST_B = (62.3, 10.2)                           # oben am Brecher


def hoist_z(x):
    return HOIST_A[1] + (x - HOIST_A[0]) * (HOIST_B[1] - HOIST_A[1]) / (HOIST_B[0] - HOIST_A[0])


def schraegaufzug(b):
    """Kuebelbahn (Skip): zwei Schienen auf einem Holz-/Stahlbock von der Aufgabestelle in der Grube bis zum Brecherturm, Kuebel in der Mitte."""
    for sg in (-1, 1):
        yy = HOIST_Y + sg * 0.75
        b.beam((HOIST_A[0], yy, HOIST_A[1]), (HOIST_B[0], yy, HOIST_B[1]), 0.18, 0.22, "Metall")
    for x in (41.0, 45.0, 49.0, 53.0, 57.0):
        z = hoist_z(x) - 0.2
        for sg in (-1, 1):
            b.box(x - 0.12, HOIST_Y + sg * 1.05 - 0.12, PIT_Z, x + 0.12, HOIST_Y + sg * 1.05 + 0.12, z, "Holz alt")
        b.box(x - 0.1, HOIST_Y - 1.1, z - 0.3, x + 0.1, HOIST_Y + 1.1, z - 0.15, "Holz alt")
        for k in range(2):
            za = PIT_Z + 0.5 + k * (z - PIT_Z) / 2.0
            b.beam((x, HOIST_Y - 1.05, za), (x, HOIST_Y + 1.05, za + (z - PIT_Z) / 2.0 - 0.3), 0.08, 0.1, "Holz alt")
    for (xa, xb) in ((41.0, 45.0), (45.0, 49.0), (49.0, 53.0), (53.0, 57.0)):                      # Querstreben in x
        for sg in (-1, 1):
            b.beam((xa, HOIST_Y + sg * 1.05, PIT_Z + 1.0), (xb, HOIST_Y + sg * 1.05, hoist_z(xb) - 1.2), 0.08, 0.1, "Holz alt")
    xk = 50.0                                                                                    # Kuebel
    b.beam((xk - 1.0, HOIST_Y, hoist_z(xk - 1.0) + 0.55), (xk + 1.0, HOIST_Y, hoist_z(xk + 1.0) + 0.55), 1.5, 1.0, "Rost")
    b.beam((xk - 0.9, HOIST_Y, hoist_z(xk - 0.9) + 1.05), (xk + 0.9, HOIST_Y, hoist_z(xk + 0.9) + 1.05), 1.1, 0.3, "Bruch Fels")
    b.beam((xk, HOIST_Y, hoist_z(xk) + 1.2), (HOIST_B[0] - 1.0, HOIST_Y, HOIST_B[1] + 2.0), 0.04, 0.04, "Metall")      # Zugseil
    # Aufgabetrichter in der Grube (auf der Sohle, vor der Nordbank)
    ya, yb = HOIST_Y - 1.5, HOIST_Y + 1.2
    b.box(36.4, ya, PIT_Z, 40.6, yb, PIT_Z + 0.6, "Bruch Beton")
    for (x0, x1) in ((36.4, 36.7), (40.3, 40.6)):
        b.box(x0, ya, PIT_Z + 0.6, x1, yb, PIT_Z + 2.2, "Bruch Beton")
    for yy in (ya + 0.05, yb - 0.05):
        b.box(36.7, yy - 0.05, PIT_Z + 0.6, 40.3, yy + 0.05, PIT_Z + 2.2, "Bruch Beton")
    kegel(b, 38.5, HOIST_Y - 0.15, PIT_Z + 0.6, 1.3, 1.2, "Bruch Fels dunkel")


def kegel(b, *a, **kw):
    BA.kegel(b, *a, **kw)


def brecher(b):
    """Brecherturm (Stahlgeruest mit Wellblechverkleidung, 6 x 6 m, 11,5 m hoch): Aufgabe oben (Kuebel), Auslauf am Fuss mit Rutsche zum Bunker."""
    x0, y0, x1, y1 = BRECHER
    H = 11.5
    for (px, py) in ((x0, y0), (x1 - 0.3, y0), (x0, y1 - 0.3), (x1 - 0.3, y1 - 0.3)):
        b.box(px, py, 0.0, px + 0.3, py + 0.3, H + 0.4, "Metall")
    wallm = "Wellblech alt"
    zo = (0.0, H)
    # Waende mit Aufgabeoeffnung (West) und Auslauf (Ost)
    b.box(x0, y0 + 0.3, 1.0, x0 + 0.2, y1 - 0.3, 9.4, wallm)
    b.box(x0, y0 + 0.3, 9.4, x0 + 0.2, HOIST_Y - 1.4, H, wallm)
    b.box(x0, HOIST_Y + 1.4, 9.4, x0 + 0.2, y1 - 0.3, H, wallm)
    b.box(x0, HOIST_Y - 1.4, 11.0, x0 + 0.2, HOIST_Y + 1.4, H, wallm)
    b.box(x1 - 0.2, y0 + 0.3, 1.0, x1, y1 - 0.3, H, wallm)
    b.box(x0 + 0.3, y0, 1.0, x1 - 0.3, y0 + 0.2, H, wallm)
    b.box(x0 + 0.3, y1 - 0.2, 1.0, x1 - 0.3, y1, H, wallm)
    # Sockel aus Beton mit Auslaufoeffnung (Ost, unten)
    b.box(x0, y0, 0.0, x1, y1, 1.0, "Bruch Beton")
    b.box(x0 - 0.2, y0 - 0.2, H, x1 + 0.2, y1 + 0.2, H + 0.25, "Wellblech")                  # Dach
    b.box(x0 + 1.2, y0 + 1.2, H + 0.25, x1 - 1.2, y1 - 1.2, H + 0.9, "Metall")             # Windenhaus-Aufbau
    # Backenbrecher (sichtbar auf der Aussenseite): Schwungrad (Scheibe) an der Suedseite
    BA.scheibe_y(b, (x0 + x1) / 2, y0 - 0.15, 5.0, 1.6, 0.25, "Metall", n=12)
    b.box((x0 + x1) / 2 - 0.15, y0 - 0.25, 4.85, (x0 + x1) / 2 + 0.15, y0, 5.15, "Rost")
    # Rutsche zum Bunker
    b.beam((x1, HOIST_Y, 10.2), (73.8, 28.6, 9.7), 1.2, 0.2, "Metall")
    b.beam((x1, HOIST_Y - 0.55, 10.5), (73.8, 28.6 - 0.55, 10.0), 0.08, 0.35, "Metall")
    b.beam((x1, HOIST_Y + 0.55, 10.5), (73.8, 28.6 + 0.55, 10.0), 0.08, 0.35, "Metall")
    # Leiter an der Nordseite bis zur Aufgabebuehne (ohne Zugang zum Dach)
    for sg in (-0.3, 0.3):
        b.box(x0 + 2.8 + sg - 0.03, y1, 0.0, x0 + 2.8 + sg + 0.03, y1 + 0.1, 9.0, "Metall")
    for k in range(18):
        b.box(x0 + 2.5, y1, 0.4 + k * 0.5, x0 + 3.1, y1 + 0.1, 0.45 + k * 0.5, "Metall")
    # Schriftzug
    g = Lok(b, (x0 + x1) / 2, y0, 0.0, 0.0, 1)
    O.schrift(g, "STEINBRUCH", 0.0, 7.3, 0.0, 0.11, "Schrift weiss", 0.03)
    return g


def bunker(b):
    """Verladebunker (Beton) quer ueber dem Gleis y = 27: Durchfahrt 4,4 m breit / 5,4 m hoch, Trichter oben, Auslaufschuss ueber dem Wagen."""
    x0, y0, x1, y1 = BUNKER
    zdeck = 5.6
    for (ya, yb) in ((y0, 24.8), (29.2, y1)):
        b.box(x0, ya, 0.0, x1, yb, zdeck, "Bruch Beton")
        b.box(x0 - 0.15, ya, 0.0, x0, yb, 0.6, "Bruch Beton")
        b.box(x1, ya, 0.0, x1 + 0.15, yb, 0.6, "Bruch Beton")
    b.box(x0, y0, zdeck, x1, y1, zdeck + 0.7, "Bruch Beton")
    # Trichter: oben 7 x 9 m offen, unten 2 x 2 m; sichtbare Schraegen
    top = zdeck + 3.6
    bx0, bx1, by0, by1 = x0 + 0.5, x1 - 0.5, y0 + 0.5, y1 - 0.5
    ux0, ux1, uy0, uy1 = 75.0, 77.0, 26.0, 28.0
    zb = zdeck + 0.7
    quads = [
        [(bx0, by0, top), (bx1, by0, top), (ux1, uy0, zb), (ux0, uy0, zb)],
        [(bx1, by0, top), (bx1, by1, top), (ux1, uy1, zb), (ux1, uy0, zb)],
        [(bx1, by1, top), (bx0, by1, top), (ux0, uy1, zb), (ux1, uy1, zb)],
        [(bx0, by1, top), (bx0, by0, top), (ux0, uy0, zb), (ux0, uy1, zb)],
    ]
    for q in quads:
        b.add(q, [(0, 1, 2, 3)], "Rost")
        b.add(q[::-1], [(0, 1, 2, 3)], "Rost")
    for (xa, ya, xb, yb) in ((x0, y0, x1, y0 + 0.5), (x0, y1 - 0.5, x1, y1), (x0, y0 + 0.5, x0 + 0.5, y1 - 0.5), (x1 - 0.5, y0 + 0.5, x1, y1 - 0.5)):
        b.box(xa, ya, zdeck + 0.7, xb, yb, top, "Bruch Beton")
    b.box(x0 - 0.1, y0 - 0.1, top, x1 + 0.1, y0 + 0.5, top + 0.2, "Metall")
    b.box(x0 - 0.1, y1 - 0.5, top, x1 + 0.1, y1 + 0.1, top + 0.2, "Metall")
    kegel(b, 76.0, 27.0, zb + 0.2, 1.6, 1.0, "Bruch Fels")
    # Auslaufschuss und Schieber ueber dem Wagen
    b.box(75.0, 26.0, zdeck - 0.9, 77.0, 28.0, zdeck, "Metall")
    b.box(74.8, 25.8, zdeck - 1.0, 77.2, 28.2, zdeck - 0.9, "Rost")
    # Aufschrift
    g = Lok(b, (x0 + x1) / 2, y0, 0.0, 0.0, 1)
    O.schrift(g, "VERLADUNG", 0.0, 3.4, 0.0, 0.1, "Schrift weiss", 0.03)
    return g


# ------------------------------------------------------------------ Werkstatt
def werkstatt(b, lvl=1):
    """Werkstatt (16 x 10 m, Backstein, Wellblech-Satteldach mit Dachreiter, Tuer nach Sueden): Haupthalle mit Schiebetor, Drehbank, Bohrmaschine,
    Werkbank, Schmiede, Laufkran; Buero im Osten mit Schreibtisch, Ofen, Aktenschrank."""
    g = Lok(b, WERKSTATT[0], WERKSTATT[1], 0.0, 0.0, 1)
    w, d, H = 16.0, 10.0, 4.9
    hw, hd = w / 2, d / 2
    mat = "Klinker alt" if lvl else "Klinker"
    zf = F0
    oef_v = [(-5.8, -1.6, F0, F0 + 3.8), (1.0, 2.2, F0, F0 + 2.2), (4.0, 5.4, F0 + 1.1, F0 + 2.9), (6.0, 7.4, F0 + 1.1, F0 + 2.9)]
    oef_h = [(x - 0.7, x + 0.7, F0 + 1.3, F0 + 3.2) for x in (-6.0, -3.0, 0.0)] + [(3.6, 4.8, F0, F0 + 2.2)] + [(6.2, 7.4, F0 + 1.3, F0 + 3.2)]
    oef_w = [(y - 0.7, y + 0.7, F0 + 1.3, F0 + 3.2) for y in (-2.0, 2.0)]
    oef_o = [(-3.2, -1.8, F0 + 1.3, F0 + 3.0)]
    aussenwand(g, "x", -hd, -1, -hw, hw, H, mat, oef_v)
    aussenwand(g, "x", hd, 1, -hw, hw, H, mat, oef_h)
    aussenwand(g, "y", -hw, -1, -hd + WD, hd - WD, H, mat, oef_w)
    aussenwand(g, "y", hw, 1, -hd + WD, hd - WD, H, mat, oef_o)
    for x in (4.7, 6.7):
        fensterschmuck(g, "x", -hd, -1, x, F0 + 2.0, 1.4 if x == 4.7 else 1.4, 1.8, None)
    for x in (-6.0, -3.0, 0.0):
        fensterschmuck(g, "x", hd, 1, x, F0 + 2.25, 1.4, 1.9, None)
    fensterschmuck(g, "x", hd, 1, 6.8, F0 + 2.25, 1.2, 1.9, None)
    for y in (-2.0, 2.0):
        fensterschmuck(g, "y", -hw, -1, y, F0 + 2.25, 1.4, 1.9, None)
    fensterschmuck(g, "y", hw, 1, -2.5, F0 + 2.15, 1.4, 1.7, None)
    # Schiebetor (halb geoeffnet, Laufschiene darueber) und Mannschaftstuer
    g.box(-7.4, -hd - 0.12, F0 + 3.95, -0.0, -hd - 0.02, F0 + 4.1, "Metall")
    g.box(-5.8, -hd - 0.1, F0, -3.7, -hd - 0.03, F0 + 3.8, "Tor rot alt")
    for k in range(5):
        g.box(-5.8, -hd - 0.12, F0 + 0.2 + k * 0.7, -3.7, -hd - 0.1, F0 + 0.28 + k * 0.7, "Metall")
    tuerrahmen(g, "x", -hd - 0.07, -hd, 1.0, 2.2, F0, F0 + 2.2)
    g.box(0.8, -hd - 0.9, -0.6, 2.4, -hd - 0.07, F0, "Beton")
    g.box(-5.9, -hd - 1.5, -0.6, -1.5, -hd - 0.07, F0, "Beton")
    g.box(1.0, -hd + WD, F0, 1.05, -hd + WD + 0.9, F0 + 2.1, "Tuer grau")
    tuerrahmen(g, "x", hd, hd + 0.07, 3.6, 4.8, F0, F0 + 2.2)
    g.box(3.4, hd, -0.6, 5.0, hd + 1.0, F0, "Beton")
    # Schild
    g.box(-1.0, -hd - 0.1, F0 + 3.3, 4.2, -hd - 0.02, F0 + 4.1, "Schild gelb")
    O.schrift(g, "WERKSTATT", 1.6, F0 + 3.4, -hd - 0.1, 0.075, "Schrift schwarz", 0.03)
    # Boden, Decke
    ix0, ix1, iy0, iy1 = -hw + WD, hw - WD, -hd + WD, hd - WD
    g.box(ix0, iy0, -0.7, ix1, iy1, F0, "Beton")
    g.box(ix0, iy0, H - 0.2, ix1, iy1, H, "Decke")
    # Dach: Wellblech, Dachreiter (Lichtband) am First
    rz = dach(g, "x", w, d, H, 1.9, "Wellblech alt" if lvl else "Wellblech", mat, e=0.45)
    g.box(-6.0, -1.2, H + 1.9, 6.0, 1.2, H + 2.4, "Wellblech alt")
    g.box(-6.0, -1.2, H + 1.9, 6.0, -1.15, H + 2.35, "Glas")
    g.box(-6.0, 1.15, H + 1.9, 6.0, 1.2, H + 2.35, "Glas")
    # Schornstein (Schmiede)
    g.box(-7.3, 2.2, H - 0.1, -6.3, 3.2, rz(-6.8, 2.7) + 2.2, "Klinker alt")
    g.box(-7.4, 2.1, rz(-6.8, 2.7) + 2.2, -6.2, 3.3, rz(-6.8, 2.7) + 2.35, "Stein")
    # Buero (Ost): Trennwand bei x = 3.7, Tuer bei y = -3.6..-2.6
    g.box(3.7, iy0, F0, 3.9, -3.7, H - 0.2, "Innenwand")
    g.box(3.7, -2.5, F0, 3.9, -0.7, H - 0.2, "Innenwand")
    g.box(3.7, -3.7, F0 + 2.2, 3.9, -2.5, H - 0.2, "Innenwand")
    g.box(3.7, -0.7, F0, ix1, -0.5, H - 0.2, "Innenwand")
    tuerrahmen(g, "y", 3.7, 3.9, -3.7, -2.5, F0, F0 + 2.2)
    g.box(4.0, -1.0, F0, 4.9, -0.6, F0 + 1.8, "Metall")                                                    # Aktenschrank
    g.box(5.2, -4.45, F0, 7.2, -3.65, F0 + 0.78, "Holz")                                                    # Schreibtisch
    g.box(5.15, -4.5, F0 + 0.78, 7.25, -3.6, F0 + 0.84, "Holz alt")
    g.box(6.0, -3.5, F0, 6.5, -3.0, F0 + 0.45, "Holz")                                                      # Stuhl
    g.box(6.0, -3.0 - 0.0, F0 + 0.45, 6.5, -2.95, F0 + 1.0, "Holz")
    g.prism(7.3, -1.2, F0, 0.28, 1.0, 8, "Metall")                                                          # Ofen
    g.box(7.22, -1.28, F0 + 1.0, 7.38, -1.12, H - 0.2, "Metall")                                            # Ofenrohr
    g.box(ix1 - 0.05, -3.8, F0 + 1.3, ix1, -2.4, F0 + 2.2, "Schild gelb")                                   # Kalender/Karte
    g.box(4.0, iy0 + 0.05, F0 + 1.1, 4.7, iy0 + 0.3, F0 + 1.14, "Holz")                                    # Brett mit Schluesseln
    # Haupthalle: Werkbank (Nordwand), Drehbank, Bohrmaschine, Schmiede, Amboss, Fass, Kran
    g.box(-7.4, iy1 - 0.8, F0, -2.4, iy1 - 0.05, F0 + 0.9, "Holz")
    g.box(-7.4, iy1 - 0.8, F0 + 0.9, -2.4, iy1 - 0.05, F0 + 0.96, "Holz alt")
    for x in (-6.4, -4.2):
        g.box(x, iy1 - 0.45, F0 + 0.96, x + 0.18, iy1 - 0.25, F0 + 1.15, "Metall")                         # Schraubstock
        g.box(x + 0.05, iy1 - 0.4, F0 + 1.15, x + 0.13, iy1 - 0.3, F0 + 1.3, "Metall")
    g.box(-7.4, iy1 - 0.1, F0 + 1.3, -2.4, iy1 - 0.05, F0 + 2.4, "Regal")                                  # Werkzeugtafel
    for k in range(10):
        g.box(-7.3 + k * 0.5, iy1 - 0.2, F0 + 1.5 + (k % 3) * 0.3, -7.15 + k * 0.5, iy1 - 0.1, F0 + 2.0 + (k % 3) * 0.3, "Metall")
    g.box(-1.6, iy1 - 1.3, F0, 1.9, iy1 - 0.4, F0 + 0.35, "Gelb Maschine")                                  # Drehbank: Bett
    g.box(-1.6, iy1 - 1.2, F0 + 0.35, -0.8, iy1 - 0.5, F0 + 1.2, "Gelb Maschine")                         # Spindelstock
    g.box(1.2, iy1 - 1.1, F0 + 0.35, 1.9, iy1 - 0.6, F0 + 1.05, "Gelb Maschine")                          # Reitstock
    g.box(-0.8, iy1 - 1.0, F0 + 0.55, 1.2, iy1 - 0.8, F0 + 0.7, "Metall")
    g.box(-0.1, iy1 - 1.35, F0 + 0.5, 0.35, iy1 - 0.75, F0 + 0.62, "Gelb Maschine")
    g.prism(2.7, iy1 - 0.7, F0, 0.14, 1.6, 8, "Metall")                                                     # Standbohrmaschine
    g.box(2.35, iy1 - 0.95, F0 + 1.45, 3.1, iy1 - 0.45, F0 + 1.85, "Gelb Maschine")
    g.box(2.38, iy1 - 0.95, F0, 3.02, iy1 - 0.45, F0 + 0.1, "Metall")
    g.box(-7.4, -1.6, F0, -5.6, 0.4, F0 + 0.9, "Klinker alt")                                              # Schmiedeherd
    g.box(-7.4, -1.6, F0 + 0.9, -6.6, 0.4, F0 + 3.6, "Klinker alt")                                        # Esse (Rauchfang)
    g.box(-7.4, -1.5, F0 + 1.8, -6.0, 0.3, F0 + 1.95, "Metall")
    g.box(-5.0, -1.2, F0, -4.5, -0.7, F0 + 0.75, "Holz alt")                                                # Ambossstock
    g.box(-5.05, -1.25, F0 + 0.75, -4.45, -0.65, F0 + 0.95, "Metall")
    g.box(-5.0, -0.9, F0 + 0.95, -4.5, -0.8, F0 + 1.1, "Metall")
    for (x, y) in ((-6.5, 3.2), (-6.1, 3.2), (-6.3, 3.5)):
        g.prism(x, y, F0, 0.28, 0.9, 8, "Faesser rot")
    g.box(1.6, -3.0, F0, 3.4, -1.0, F0 + 0.12, "Holz alt")                                                  # Palette mit Ersatzteilen
    g.box(1.8, -2.8, F0 + 0.12, 2.8, -1.6, F0 + 0.9, "Regal")
    for k in range(3):
        g.prism(-2.6 + k * 0.55, 1.0, F0, 0.32, 0.25 + 0.0, 10, "Reifen")                                    # Reifenstapel
    g.prism(-2.05, 1.0, F0, 0.32, 0.6, 10, "Reifen")
    # Laufkran: zwei Kranbahnen an den Laengswaenden, Kranbruecke, Laufkatze mit Haken
    zk = H - 0.8
    for sy in (-1, 1):
        g.box(ix0 + 0.05, sy * 3.3 - 0.12, zk, ix1 - 0.05, sy * 3.3 + 0.12, zk + 0.3, "Metall")
    g.box(-2.5, -3.4, zk + 0.3, -2.1, 3.4, zk + 0.55, "Metall")
    g.box(-2.7, -0.4, zk - 0.35, -1.9, 0.4, zk + 0.3, "Gelb Maschine")
    g.box(-2.33, -0.04, zk - 1.4, -2.27, 0.04, zk - 0.35, "Metall")
    g.box(-2.45, -0.15, zk - 1.7, -2.15, 0.15, zk - 1.4, "Metall")
    # Lampen
    for x in (-5.0, 0.0):
        g.box(x - 0.02, -0.02, H - 1.1, x + 0.02, 0.02, H - 0.2, "Metall")
        g.box(x - 0.3, -0.3, H - 1.3, x + 0.3, 0.3, H - 1.1, "Schild gelb")
    return g


# ------------------------------------------------------------------ Sprengstoffhaeuschen
def sprengstoff(b):
    g = Lok(b, SPRENG[0], SPRENG[1], 0.0, 0.0, 1)
    w, d, H = 5.0, 3.6, 3.5
    hw, hd = w / 2, d / 2
    mat = "Bruch Beton"
    aussenwand(g, "x", -hd, -1, -hw, hw, H, mat, [(-0.6, 0.6, F0, F0 + 2.1)])
    aussenwand(g, "x", hd, 1, -hw, hw, H, mat, [])
    aussenwand(g, "y", -hw, -1, -hd + WD, hd - WD, H, mat, [])
    aussenwand(g, "y", hw, 1, -hd + WD, hd - WD, H, mat, [])
    g.box(-hw - 0.2, -hd - 0.2, H, hw + 0.2, hd + 0.2, H + 0.25, "Bruch Beton")
    tuerrahmen(g, "x", -hd - 0.07, -hd, -0.6, 0.6, F0, F0 + 2.1, "Metall")
    g.box(-0.6, -hd + WD, F0, -0.55, -hd + WD + 0.6, F0 + 2.05, "Tuer rot")                                # Stahltuer, aufgeschwenkt
    g.box(-0.9, -hd - 0.7, -0.6, 0.9, -hd - 0.07, F0, "Beton")
    g.box(-hw + WD, -hd + WD, -0.7, hw - WD, hd - WD, F0, "Beton")
    for k in range(3):                                                                                        # Kisten
        g.box(-1.9 + k * 1.2, hd - 1.0, F0, -1.0 + k * 1.2, hd - 0.3, F0 + 0.55, "Ware rot")
    g.box(-1.9, hd - 1.0, F0 + 0.55, -1.0, hd - 0.3, F0 + 1.1, "Ware rot")
    g.box(-1.0, -0.4 - 0.0, F0, -0.4, 0.6, F0 + 0.5, "Holz alt")
    g.box(hw - 0.9, -hd + 0.4, H - 0.2 - 0.0, hw - 0.4, hd - 0.4, H, "Decke")
    # Warnschild
    g.box(-1.9, -hd - 0.1, H - 1.0, 1.9, -hd - 0.02, H - 0.2, "Schild rot")
    O.schrift(g, "ACHTUNG", 0.0, H - 0.88, -hd - 0.1, 0.08, "Schrift weiss", 0.03)
    return g


# ------------------------------------------------------------------ Fahrzeuge
def kipper(b, cx, cy, theta, zb=0.0):
    """Muldenkipper (Lkw der 40er Jahre, 7,4 m lang): Fahrgestell, Fahrerhaus mit Scheibe, Kippmulde mit Felsladung, vier Raeder. Fahrtrichtung lokal +x."""
    g = Lok(b, cx, cy, zb, theta, 1)
    g.box(-3.4, -0.9, 0.55, 3.1, 0.9, 0.8, "Metall")
    g.box(1.5, -1.0, 0.8, 3.2, 1.0, 2.3, "Kipper blau")                                                      # Fahrerhaus
    g.box(2.55, -0.9, 1.5, 3.22, 0.9, 2.1, "Glas")
    g.box(1.5, -1.05, 2.3, 3.2, 1.05, 2.45, "Metall")
    g.box(3.2, -0.9, 0.8, 3.9, 0.9, 1.7, "Kipper blau")                                                      # Motorhaube
    g.box(3.9, -0.7, 0.9, 4.0, 0.7, 1.5, "Metall")                                                           # Kuehlergitter
    for sy in (-1, 1):
        g.box(3.8, sy * 0.6 - 0.15, 1.2, 4.0, sy * 0.6 + 0.15, 1.45, "Schild gelb")                          # Scheinwerfer
    g.box(-3.3, -1.1, 0.8, 1.3, 1.1, 1.0, "Metall")                                                          # Mulde: Boden
    for sy in (-1, 1):
        g.box(-3.3, sy * 1.1 - (0.0 if sy > 0 else 0.08), 1.0, 1.3, sy * 1.1 + (0.08 if sy > 0 else 0.0), 2.2, "Kipper blau")
    g.box(-3.3, -1.1, 1.0, -3.22, 1.1, 2.2, "Kipper blau")
    g.box(1.2, -1.1, 1.0, 1.3, 1.1, 2.6, "Kipper blau")
    BA.kegel(g.b, *g.P((-1.0, 0.0, 1.0))[:2], g.zb + 1.0, 1.0, 1.0, "Bruch Fels", n=8)
    for (x, y) in ((-2.4, 1.0), (-2.4, -1.0), (-1.6, 0.0)):
        BA.kegel(g.b, *g.P((x, y, 1.0))[:2], g.zb + 1.0, 0.45, 0.4, "Bruch Fels dunkel", n=6)
    for (x, sy) in ((2.6, -1), (2.6, 1), (-2.4, -1), (-2.4, 1), (-1.5, -1), (-1.5, 1)):
        px, py, pz = g.P((x, sy * 1.0, 0.0))
        scheibe_rot(g, x, sy * 1.0, 0.5, theta)
    return g


def scheibe_rot(g, x, y, r, theta, n=10):
    """Rad mit Achse quer zur Fahrtrichtung (lokal y), gedreht mit dem Fahrzeug."""
    c, s = math.cos(theta), math.sin(theta)
    ring = lambda dy: [(x + r * math.cos(2 * math.pi * k / n), y + dy, g.zb + r + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    a, d = ring(-0.15), ring(0.15)
    pts = [g.P((p[0], p[1], p[2] - g.zb)) for p in a + d]
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    g.b.add(pts, faces, "Reifen")


def bagger(b, cx, cy, theta, zb=PIT_Z):
    """Kettenbagger (Loeffelbagger): Raupenlaufwerke, Oberwagen mit Fuehrerhaus, Ausleger, Stiel und Loeffel. Blickrichtung lokal +x."""
    g = Lok(b, cx, cy, zb, theta, 1)
    for sy in (-1, 1):
        g.box(-1.9, sy * 1.35 - 0.4, 0.0, 1.9, sy * 1.35 + 0.4, 0.8, "Reifen")
        g.box(-1.7, sy * 1.35 - 0.45, 0.3, 1.7, sy * 1.35 + 0.45, 0.45, "Metall")
        for x in (-1.4, 0.0, 1.4):
            g.box(x - 0.3, sy * 1.35 - 0.45, 0.1, x + 0.3, sy * 1.35 + 0.45, 0.7, "Metall")
    g.box(-1.8, -1.0, 0.8, 1.8, 1.0, 1.1, "Metall")
    g.box(-2.0, -1.2, 1.1, 1.2, 1.2, 2.0, "Gelb Maschine")                                                    # Oberwagen
    g.box(-2.3, -1.0, 1.1, -2.0, 1.0, 1.9, "Gelb Maschine")                                                   # Gegengewicht
    g.box(0.1, -1.1, 2.0, 1.4, 0.1, 3.2, "Gelb Maschine")                                                      # Fuehrerhaus
    g.box(1.2, -1.0, 2.2, 1.4, 0.0, 3.0, "Glas")
    g.box(0.0, -1.2, 3.2, 1.5, 0.2, 3.3, "Metall")
    g.box(-1.5, 0.3, 2.0, -1.1, 0.7, 2.9, "Metall")                                                           # Auspuff
    b.beam(g.P((0.8, 0.7, 1.6)), g.P((3.0, 0.7, 3.8)), 0.4, 0.5, "Gelb Maschine")                            # Ausleger
    b.beam(g.P((3.0, 0.7, 3.8)), g.P((4.8, 0.7, 1.6)), 0.3, 0.35, "Gelb Maschine")                           # Stiel
    ax, ay, az = g.P((4.8, 0.7, 1.6))
    b.beam(g.P((4.6, 0.7, 1.9)), g.P((5.4, 0.7, 0.6)), 0.9, 0.5, "Rost")                                      # Loeffel
    b.beam(g.P((3.0, 0.3, 3.0)), g.P((1.6, 0.3, 1.6)), 0.12, 0.12, "Metall")                                  # Zylinder
    return g


# ------------------------------------------------------------------ Waechterhaus, Tor, Lager
TOR = (88.0, 62.0)                                # Einfahrt von der Werkstrasse (Mitte)
WAECHTER = (96.0, 59.5)


def waechterhaus(b):
    """Pfoertnerhaus (3,6 x 3 m, Pultdach, Tuer zur Einfahrt nach Westen): Schreibtisch, Ofen, Schluesselbrett, Fenster zur Einfahrt."""
    g = Lok(b, WAECHTER[0], WAECHTER[1], 0.0, -math.pi / 2, 1)
    hw, hd, H = 1.8, 1.5, 2.7
    mat = "Wellblech alt"
    oef_v = [(-0.5, 0.5, F0, F0 + 2.0), (0.9, 1.5, F0 + 0.9, F0 + 1.9)]
    aussenwand(g, "x", -hd, -1, -hw, hw, H, "Ziegel dunkel alt", oef_v)
    aussenwand(g, "x", hd, 1, -hw, hw, H, "Ziegel dunkel alt", [(-0.6, 0.6, F0 + 0.9, F0 + 1.9)])
    for sgn in (-1, 1):
        aussenwand(g, "y", sgn * hw, sgn, -hd + WD, hd - WD, H, "Ziegel dunkel alt", [])
    tuerrahmen(g, "x", -hd - 0.07, -hd, -0.5, 0.5, F0, F0 + 2.0)
    g.box(-0.5, -hd + WD, F0, -0.45, -hd + WD + 0.55, F0 + 1.95, "Tuer gruen")
    g.box(-0.9, -hd - 0.7, -0.6, 0.9, -hd - 0.07, F0, "Beton")
    g.box(-hw + WD, -hd + WD, -0.7, hw - WD, hd - WD, F0, "Beton")
    g.box(-hw + WD, -hd + WD, F0, hw - WD, hd - WD, F0 + 0.03, "Dielen")
    g.box(-hw + WD, -hd + WD, H - 0.25, hw - WD, hd - WD, H, "Decke")
    g.box(-hw - 0.3, -hd - 0.3, H, hw + 0.3, hd + 0.3, H + 0.15, "Wellblech alt")
    fensterschmuck(g, "x", -hd, -1, 1.2, F0 + 1.4, 0.6, 1.0, None)
    fensterschmuck(g, "x", hd, 1, 0.0, F0 + 1.4, 1.2, 1.0, None)
    g.box(-1.4, 0.4, F0, -0.4, 1.0, F0 + 0.75, "Holz")                                           # Schreibtisch
    g.box(-1.2, -0.3, F0, -0.8, 0.1, F0 + 0.45, "Holz alt")
    g.prism(1.1, 0.8, F0, 0.25, 1.1, 8, "Metall")                                                # Ofen
    g.box(0.2, hd - WD - 0.05, F0 + 1.3, 1.0, hd - WD, F0 + 1.8, "Holz")                        # Schluesselbrett
    return g


def tor(b):
    """Einfahrtstor des Steinbruchs: zwei Betonpfosten, Querbalken mit Schriftzug STEINBRUCH, Schranke (offen)."""
    g = Lok(b, TOR[0], TOR[1], 0.0, 0.0, 1)
    for sx in (-4.2, 4.2):
        g.box(sx - 0.3, -0.3, 0.0, sx + 0.3, 0.3, 4.6, "Bruch Beton")
        g.box(sx - 0.4, -0.4, 4.6, sx + 0.4, 0.4, 4.75, "Bruch Beton")
    g.box(-4.2, -0.12, 3.5, 4.2, 0.12, 4.5, "Schild gruen")
    g.box(-4.3, -0.14, 3.45, 4.3, 0.14, 3.5, "Rahmen weiss")
    g.box(-4.3, -0.14, 4.5, 4.3, 0.14, 4.55, "Rahmen weiss")
    O.schrift(g, "STEINBRUCH", 0.0, 3.62, -0.12, 0.1, "Schrift weiss", 0.03)
    g.box(-4.5, 1.0, 1.0, -3.0, 1.12, 1.1, "Signal rot")                                          # Schranke (hochgeklappt am Pfosten)
    g.box(-4.5, 1.0, 1.1, -4.4, 1.12, 3.2, "Signal weiss")
    return g


def lager(b):
    """Lagerplatz: Fasswand, Dieseltank auf Betonfuessen, Stapel behauener Steinbloecke, Schotterhaufen, Holzstapel, Lampen."""
    for k, (x, y) in enumerate(((83.0, 54.0), (83.9, 54.0), (84.8, 54.0), (83.45, 54.8), (84.35, 54.8), (83.9, 55.5))):
        b.prism(x, y, 0.0, 0.32, 0.95, 8, "Faesser rot" if k % 2 == 0 else "Rost")
    zyl = BA.zyl_x
    for xs in (82.0, 85.6):
        b.box(xs - 0.2, 47.2, 0.0, xs + 0.2, 48.8, 0.5, "Bruch Beton")
    zyl(b, 81.5, 86.1, 48.0, 1.4, 0.9, "Tank gruen", n=12)
    b.box(83.6, 47.9, 2.25, 84.0, 48.1, 2.45, "Metall")
    b.box(86.1, 47.3, 0.0, 87.0, 47.9, 1.2, "Metall")                                            # Zapfsaeule
    b.box(86.2, 47.35, 0.8, 86.9, 47.45, 1.1, "Schild gelb")
    for r_, (x0, y0) in enumerate(((64.0, 44.0), (64.0, 47.5), (64.0, 51.0))):                   # Steinstapel
        for k in range(4):
            for l_ in range(3 - (k // 2)):
                b.box(x0 + 1.5 * l_, y0, 0.08 + 0.7 * k, x0 + 1.4 + 1.5 * l_, y0 + 0.9, 0.7 + 0.7 * k, "Bruch Fels hell" if (k + l_ + r_) % 2 else "Stein")
    BA.kegel(b, 88.0, 34.0, 0.04, 3.6, 2.8, "Schotter", n=9)
    BA.kegel(b, 87.0, 21.5, 0.04, 3.0, 2.2, "Schotter dunkel", n=8, rot=0.2)
    BA.kegel(b, 66.0, 18.0, 0.04, 3.4, 2.4, "Bruch Fels", n=9, rot=0.4)
    BA.kegel(b, 68.5, 38.0, 0.04, 2.5, 1.7, "Schotter", n=7, rot=0.5)
    for k in range(6):                                                                           # Holzstapel (Stempel)
        for l_ in range(3):
            b.box(78.0, 44.0 + 0.45 * k, 0.04 + 0.35 * l_, 82.0, 44.4 + 0.45 * k, 0.4 + 0.35 * l_, "Holz alt") if l_ < 3 - k // 3 else None
    for (x, y) in ((70.0, 44.0), (76.0, 56.5), (66.0, 22.0), (88.0, 40.0)):
        b.box(x - 0.06, y - 0.06, 0.0, x + 0.06, y + 0.06, 5.0, "Metall")
        b.box(x - 0.3, y - 0.3, 5.0, x + 0.3, y + 0.3, 5.2, "Schild gelb")
        b.box(x - 0.35, y - 0.35, 5.2, x + 0.35, y + 0.35, 5.28, "Metall")


def hof(b):
    """Schotterplatz oestlich der Grube (YARD) als Flaeche knapp ueber der Wiese."""
    x0, y0, x1, y1 = YARD
    b.add([(x0, y0, 0.03), (x1, y0, 0.03), (x1, y1, 0.03), (x0, y1, 0.03)], [(0, 1, 2, 3)], "Schotter")
    for (x0, y0, x1, y1) in ((66.0, 56.0, 82.0, 60.0),                                              # Vorplatz der Werkstatt
                             (90.0, 56.5, 98.5, 62.5)):                                             # Platz vor dem Waechterhaus
        b.add([(x0, y0, 0.045), (x1, y0, 0.045), (x1, y1, 0.045), (x0, y1, 0.045)], [(0, 1, 2, 3)], "Schotter dunkel")


# ------------------------------------------------------------------ Zusammenbau
def bauen_bruch():
    """Alle Bauten des Steinbruchs als Bau-Objekte: Grube (Boden/Waende/Zaeune), Anlagen, Hallen, Fahrzeuge. Rueckgabe: Liste."""
    gr = Bau("bruch_grube")
    grube(gr)
    an = Bau("bruch_anlagen")
    hof(an)
    schraegaufzug(an)
    brecher(an)
    bunker(an)
    lager(an)
    tor(an)
    ge = Bau("bruch_gebaeude")
    werkstatt(ge)
    sprengstoff(ge)
    waechterhaus(ge)
    fz = Bau("bruch_fahrzeuge")
    bagger(fz, 42.0, 26.0, 0.5)
    kipper(fz, 53.0, 24.0, math.pi + 0.2, PIT_Z)
    BA.kegel(fz, 47.0, 30.0, PIT_Z, 3.2, 2.4, "Bruch Fels dunkel", n=9)
    BA.kegel(fz, 55.0, 30.5, PIT_Z, 2.2, 1.6, "Bruch Fels", n=8, rot=0.3)
    kipper(fz, 77.0, 37.5, 0.25, 0.0)                                                              # Kipper im Hof
    return [gr, an, ge, fz]
