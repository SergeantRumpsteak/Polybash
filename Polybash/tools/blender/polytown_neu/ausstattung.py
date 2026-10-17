"""Polybash - Strassenausstattung: Trinkbrunnen, Bushaltestellen und Baenke (reine Geometrie, ohne bpy).

Alle Teile werden an Strassenraendern bzw. Plaetzen aufgestellt, ausgerichtet in 90-Grad-Schritten (th: 0 = Vorderseite nach Sueden,
90 = Osten, 180 = Norden, 270 = Westen), damit ihre Hindernisquader achsenparallel bleiben. Die Standorte werden aus Kandidatenlisten gewaehlt:
nur ebene Plaetze, die frei von Gebaeuden, Baeumen, Strassen und Zaeunen sind (alle bereits gebauten Gruppen werden geprueft).

  * Trinkbrunnen (Stein): Brunnenstock mit Inschrifttafel, Messing-Speier und Steintrog mit Wasser, Plinthe
  * Trinkbrunnen (Stahl): Standsaeule mit Druckknopf, gebogenem Strahlrohr, Schale und Hundenapf (Flugplatz, Zeltplatz, Bahnhof)
  * Bushaltestelle: Wartehaeuschen (Stahlrahmen, Glaswaende, Dach, Sitzbank, Fahrplanvitrine, Papierkorb) mit Haltestellenschild H
  * Bank: Gusseisenbeine, Holzlatten, Armlehnen
"""
import math

import stadt as S
import schilder as SC
import umgebung as U
from burg import Bau
from stadt import Lok

S.FARBEN.update(SC.FARBEN)
S.FARBEN.setdefault("Messing", ((0.70, 0.55, 0.20), 0.35, 0.0))
S.FARBEN.setdefault("Glas Halt", ((0.55, 0.70, 0.76), 0.1, 0.0))
S.FARBEN.setdefault("Halt Rahmen", ((0.10, 0.28, 0.20), 0.5, 0.0))
S.FARBEN.setdefault("Dach Halt", ((0.22, 0.24, 0.26), 0.7, 0.0))
S.FARBEN.setdefault("Fahrplan", ((0.93, 0.92, 0.80), 0.8, 0.0))
S.FARBEN.setdefault("Fenster", ((0.15, 0.2, 0.25), 0.2, 0.0))
S.FARBEN.setdefault("Eisen", ((0.14, 0.14, 0.15), 0.6, 0.0))
S.FARBEN.setdefault("Stein dunkel", ((0.42, 0.41, 0.40), 0.9, 0.0))
S.FARBEN.setdefault("Holz dunkel", ((0.30, 0.20, 0.12), 0.9, 0.0))

FRONT = {0: "S", 90: "E", 180: "N", 270: "W"}


def _dir(th):
    t = math.radians(th)
    return (math.sin(t), -math.cos(t))


def trinkbrunnen_stein(b, x, y, zb, th):
    g = Lok(b, x, y, zb, math.radians(th))
    g.box(-1.15, -0.95, 0.0, 1.15, 0.85, 0.10, "Pflaster")                                      # Plinthe
    g.box(-0.34, 0.15, 0.10, 0.34, 0.70, 1.40, "Stein")                                          # Brunnenstock
    g.box(-0.42, 0.10, 1.40, 0.42, 0.75, 1.52, "Stein dunkel")                                   # Deckplatte
    g.box(-0.30, 0.22, 1.52, 0.30, 0.65, 1.62, "Stein dunkel")                                   # Aufsatz
    g.box(-0.18, 0.14, 1.02, 0.18, 0.15, 1.30, "Eisen")                                          # Inschrifttafel
    for k in range(3):
        g.box(-0.12, 0.138, 1.07 + 0.07 * k, 0.12, 0.142, 1.09 + 0.07 * k, "Stein")              # Textzeilen
    g.box(-0.05, -0.12, 0.92, 0.05, 0.15, 1.00, "Messing")                                       # Speier
    g.box(-0.05, -0.12, 0.84, 0.05, -0.08, 1.00, "Messing")
    g.box(-0.016, -0.10, 0.50, 0.016, -0.07, 0.84, "Brunnenwasser")                              # Wasserstrahl
    g.box(-0.80, -0.62, 0.10, -0.70, 0.15, 0.62, "Stein")                                        # Trog (vier Waende, innen Wasser)
    g.box(0.70, -0.62, 0.10, 0.80, 0.15, 0.62, "Stein")
    g.box(-0.70, -0.62, 0.10, 0.70, -0.52, 0.62, "Stein")
    g.box(-0.70, 0.10, 0.10, 0.70, 0.15, 0.62, "Stein")
    g.box(-0.70, -0.52, 0.10, 0.70, 0.10, 0.50, "Brunnenwasser")
    g.box(-0.86, -0.68, 0.62, 0.86, -0.46, 0.68, "Stein dunkel")                                 # Randstein vorn
    g.box(-0.86, -0.68, 0.62, -0.64, 0.20, 0.68, "Stein dunkel")
    g.box(0.64, -0.68, 0.62, 0.86, 0.20, 0.68, "Stein dunkel")
    g.box(-0.25, -0.95, 0.10, 0.25, -0.70, 0.13, "Eisen")                                        # Ablaufgitter davor
    return b


def trinkbrunnen_stahl(b, x, y, zb, th):
    g = Lok(b, x, y, zb, math.radians(th))
    g.box(-0.62, -0.62, 0.0, 0.62, 0.62, 0.08, "Pflaster")
    g.box(-0.16, -0.16, 0.08, 0.16, 0.16, 1.02, "Eisen")                                         # Saeule
    g.box(-0.20, -0.20, 1.02, 0.20, 0.20, 1.08, "Metall")                                        # Kappe
    g.box(-0.20, -0.20, 0.08, 0.20, 0.20, 0.16, "Metall")                                        # Fuss
    g.box(-0.04, -0.30, 0.88, 0.04, -0.14, 0.94, "Metall")                                       # Strahlrohr
    g.box(-0.04, -0.30, 0.82, 0.04, -0.26, 0.94, "Metall")
    g.box(-0.012, -0.29, 0.66, 0.012, -0.27, 0.82, "Brunnenwasser")
    g.box(-0.30, -0.52, 0.60, 0.30, -0.14, 0.66, "Metall")                                       # Schale
    g.box(-0.30, -0.52, 0.66, 0.30, -0.49, 0.70, "Metall")
    g.box(-0.30, -0.17, 0.66, 0.30, -0.14, 0.70, "Metall")
    g.box(-0.30, -0.49, 0.66, -0.27, -0.17, 0.70, "Metall")
    g.box(0.27, -0.49, 0.66, 0.30, -0.17, 0.70, "Metall")
    g.box(0.07, -0.18, 0.78, 0.13, -0.16, 0.84, "Messing")                                       # Druckknopf
    g.box(-0.22, -0.60, 0.08, 0.22, -0.30, 0.16, "Metall")                                       # niedriger Napf fuer Hunde
    g.box(-0.18, -0.56, 0.16, 0.18, -0.34, 0.17, "Brunnenwasser")
    return b


def bank(b, x, y, zb, th, laenge=1.8):
    g = Lok(b, x, y, zb, math.radians(th))
    h = laenge / 2
    for sx in (-1, 1):
        g.box(sx * (h - 0.12) - 0.05, -0.24, 0.0, sx * (h - 0.12) + 0.05, 0.26, 0.05, "Eisen")        # Fuss
        g.box(sx * (h - 0.12) - 0.04, -0.20, 0.05, sx * (h - 0.12) + 0.04, 0.22, 0.44, "Eisen")      # Bein/Sitzwange
        g.box(sx * (h - 0.12) - 0.04, 0.18, 0.44, sx * (h - 0.12) + 0.04, 0.24, 0.88, "Eisen")       # Ruecklehnenstuetze
        g.box(sx * (h - 0.12) - 0.05, -0.22, 0.60, sx * (h - 0.12) + 0.05, 0.10, 0.65, "Eisen")      # Armlehne
    for k in range(3):                                                                              # Sitzlatten
        g.box(-h, -0.22 + 0.14 * k, 0.44, h, -0.12 + 0.14 * k, 0.48, "Holz")
    for k in range(2):                                                                              # Ruecklehnenlatten
        g.box(-h, 0.18, 0.56 + 0.17 * k, h, 0.22, 0.68 + 0.17 * k, "Holz")
    return b


def papierkorb(b, x, y, zb):
    b.prism(x, y, zb, 0.2, 0.7, 8, "Eisen")
    b.prism(x, y, zb + 0.7, 0.22, 0.04, 8, "Metall")


def bushaltestelle(b, x, y, zb, th):
    """Wartehaeuschen 4,2 x 2,1 m, Vorderseite offen zur Strasse (lokal -y); Schild H neben dem Haeuschen."""
    g = Lok(b, x, y, zb, math.radians(th))
    g.box(-2.3, -1.25, 0.0, 2.5, 1.15, 0.06, "Pflaster")                                         # Fundamentplatte
    for sx in (-1.9, 1.9):                                                                       # Stahlstuetzen vorn und hinten
        for sy in (-0.85, 0.85):
            g.box(sx - 0.05, sy - 0.05, 0.06, sx + 0.05, sy + 0.05, 2.45, "Halt Rahmen")
    g.box(-2.15, -1.05, 2.45, 2.15, 1.05, 2.55, "Dach Halt")                                     # Dach
    g.box(-2.2, -1.1, 2.55, 2.2, -1.0, 2.62, "Halt Rahmen")                                      # Dachkante
    g.box(-2.2, 1.0, 2.55, 2.2, 1.1, 2.62, "Halt Rahmen")
    g.box(-2.2, -1.1, 2.55, -2.1, 1.1, 2.62, "Halt Rahmen")
    g.box(2.1, -1.1, 2.55, 2.2, 1.1, 2.62, "Halt Rahmen")
    for k in range(3):                                                                           # Rueckwand: drei Glasscheiben mit Rahmen
        x0 = -1.9 + k * 1.267
        g.box(x0 + 0.03, 0.82, 0.25, x0 + 1.237, 0.88, 2.35, "Glas Halt")
        g.box(x0, 0.80, 0.20, x0 + 1.267, 0.90, 0.25, "Halt Rahmen")
    g.box(1.85, -0.85, 0.25, 1.92, 0.85, 2.35, "Glas Halt")                                      # Seitenwand rechts
    g.box(-1.9, 0.80, 2.35, 1.9, 0.90, 2.45, "Halt Rahmen")
    g.box(-0.6, 0.78, 0.9, 0.6, 0.80, 1.7, "Fahrplan")                                           # Fahrplanvitrine auf der Glasscheibe
    g.box(-0.62, 0.77, 0.88, 0.62, 0.79, 0.9, "Halt Rahmen")
    g.box(-0.62, 0.77, 1.7, 0.62, 0.79, 1.72, "Halt Rahmen")
    for k in range(6):
        g.box(-0.5, 0.775, 1.0 + 0.1 * k, 0.5, 0.78, 1.04 + 0.1 * k, "Metall")                  # Fahrplanzeilen
    g.box(-1.5, 0.35, 0.0, 0.9, 0.75, 0.05, "Metall")                                           # Sitzbank (Metallsitz auf zwei Fuessen)
    g.box(-1.45, 0.35, 0.40, 0.85, 0.72, 0.45, "Holz")
    g.box(-1.45, 0.68, 0.45, 0.85, 0.72, 0.90, "Holz")
    for sx in (-1.35, 0.75):
        g.box(sx - 0.04, 0.38, 0.0, sx + 0.04, 0.70, 0.40, "Metall")
    # Papierkorb und Haltestellenschild neben dem Haeuschen
    px, py, _ = g.P((2.9, -0.4, 0.0))
    papierkorb(b, px, py, zb)
    sx_, sy_, _ = g.P((-2.9, -0.7, 0.0))
    fx, fy = _dir(th)
    face = FRONT[th % 360]
    b.prism(sx_, sy_, zb, 0.05, 2.3, 6, "Schild Pfosten")
    SC.schild(b, sx_, sy_ + 0.0, face, [("bus", "H", None)], pfosten=False, unten=1.75)
    return b


# ------------------------------------------------------------------ Standortwahl
class _Raster:
    """Hindernisquader (nur oberhalb 0,2 m) in einem 8-m-Raster fuer schnelle Freiheitspruefung."""

    def __init__(self, gruppen):
        self.z = {}
        for g in gruppen:
            for bx in g.bx:
                if bx[5] - bx[2] < 0.12:
                    continue
                for ix in range(int(bx[0] // 8) - 0, int(bx[3] // 8) + 1):
                    for iy in range(int(bx[1] // 8) - 0, int(bx[4] // 8) + 1):
                        self.z.setdefault((ix, iy), []).append(bx)

    def frei(self, x0, y0, x1, y1, zb):
        for ix in range(int((x0 - 0.1) // 8), int((x1 + 0.1) // 8) + 1):
            for iy in range(int((y0 - 0.1) // 8), int((y1 + 0.1) // 8) + 1):
                for bx in self.z.get((ix, iy), ()):
                    if bx[0] < x1 and bx[3] > x0 and bx[1] < y1 and bx[4] > y0 and bx[5] > zb + 0.12 and bx[2] < zb + 2.6:
                        return False
        return True


def _footprint(x, y, th, w, d):
    """Achsenparalleles Rechteck um (x, y): w entlang der lokalen x-Achse, d entlang lokal y (th Vielfache von 90)."""
    if th % 180 == 90:
        w, d = d, w
    return (x - w / 2, y - d / 2, x + w / 2, y + d / 2)


def _ort_ok(R, P, x, y, th, w, d, zb_tol=0.3):
    x0, y0, x1, y1 = _footprint(x, y, th, w, d)
    if x0 < 6 or y0 < 6 or x1 > 294 or y1 > 294:
        return False, 0.0
    zs = [U.gelaende_hoehe(px, py) for px in (x0, x1, x) for py in (y0, y1, y)]
    if max(zs) - min(zs) > zb_tol:
        return False, 0.0
    zb = sum(zs) / len(zs)
    if not R.frei(x0, y0, x1, y1, zb):
        return False, 0.0
    strs = P["strs"]
    for px in (x0, (x0 + x1) / 2, x1):
        for py in (y0, (y0 + y1) / 2, y1):
            if S.strassenabstand(px, py, strs) < 0.15:
                return False, 0.0
    for tx, ty, tr in U.TEICHE:
        if math.hypot(x - tx, y - ty) < tr + 3.0:
            return False, 0.0
    return True, zb


# Kandidaten: (x, y, th)
BRUNNEN_STEIN = ((41.6, 137.6, 90), (68.4, 137.6, 270), (41.6, 162.4, 90), (68.4, 162.4, 270),            # Marktplatz (Ecken)
                 (207.5, 137.0, 270), (207.5, 163.0, 270), (92.0, 144.0, 0),                              # Burgring, Hauptstrasse
                 (143.5, 230.0, 90), (156.5, 232.0, 270), (143.5, 214.0, 90),                             # Dorf Nord
                 (136.5, 54.5, 90), (163.5, 54.5, 270), (141.0, 50.0, 90),                                # Bahnhofsvorplatz
                 (53.0, 80.2, 180), (47.0, 80.2, 180))                                                    # Bauernhof Zufahrt
BRUNNEN_STAHL = ((232.2, 146.0, 270), (232.2, 156.0, 270), (221.0, 146.0, 90), (221.0, 156.0, 90),        # Flugplatz (Strasse x = 226)
                 (283.5, 281.0, 90), (284.0, 297.0, 0), (294.0, 281.0, 270),                             # Zeltplatz
                 (86.0, 36.0, 180), (86.0, 66.0, 90), (90.0, 52.0, 270),                                  # Steinbruch
                 (262.5, 36.0, 0), (196.0, 36.0, 0), (210.0, 40.0, 0))                                    # an der Bahn

HALT = (  # (Name, Kandidaten (x, y, th)) - Vorderseite zur Strasse
    ("Nordstrasse O", [(154.7, y, 270) for y in (222.0, 214.0, 232.0, 208.0)]),
    ("Nordstrasse W", [(145.3, y, 90) for y in (232.0, 222.0, 214.0)]),
    ("Suedstrasse W", [(145.3, y, 90) for y in (82.0, 76.0, 88.0, 70.0)]),
    ("Suedstrasse O", [(154.7, y, 270) for y in (70.0, 76.0, 88.0)]),
    ("Markt Ost", [(x, 145.5, 180) for x in (74.5, 77.5, 72.0)]),
    ("Markt West", [(x, 154.5, 0) for x in (33.0, 35.5, 31.0)]),
    ("Hauptstrasse", [(x, 154.5, 0) for x in (88.0, 85.0, 90.5)]),
    ("Flughafenstrasse O", [(231.9, y, 270) for y in (120.0, 112.0, 128.0, 135.0, 120.0)]),
    ("Flughafenstrasse W", [(220.1, y, 90) for y in (190.0, 200.0, 125.0, 105.0, 175.0)]),
    ("Flughafenstrasse W2", [(220.1, y, 90) for y in (95.0, 85.0, 135.0, 210.0)]),
)

BAENKE_PLATZ = ((55.0, 144.2, 180), (55.0, 155.8, 0), (49.2, 150.0, 90), (60.8, 150.0, 270))              # um den Marktbrunnen, Blick zur Mitte
# Strassenbaenke: Strassenmitten (achsenparallel), Seite, Bereich, Abstand
STRASSEN = (("x", 150.0, 207.0, 238.0, 3.9), ("x", 150.0, 66.0, 94.0, 3.9),                              # Nord-/Suedstrasse (x = const)
            ("y", 150.0, 29.0, 39.0, 3.9), ("y", 150.0, 71.0, 81.0, 3.9), ("y", 150.0, 83.0, 93.0, 3.9),  # Markt West/Ost, Hauptstrasse
            ("x", 226.0, 70.0, 230.0, 5.2), ("y", 150.0, 150.0, 220.0, 5.2))                             # Flughafenstrasse, Zubringer


def _kandidaten_baenke():
    out = []
    for (ach, c, a0, a1, off) in STRASSEN:
        pos = a0 + 3.0
        k = 0
        while pos < a1 - 2.0:
            for sg in (-1, 1):
                if (k + (1 if sg > 0 else 0)) % 2:
                    continue
                if ach == "x":                                  # Strasse laeuft in y, Bank neben ihr, Blick zur Strasse
                    out.append((c + sg * off, pos, 90 if sg < 0 else 270))
                else:
                    out.append((pos, c + sg * off, 180 if sg < 0 else 0))
            pos += 14.0
            k += 1
    return out


def bauen(gruppen, P):
    """Gruppe 'ausstattung': Trinkbrunnen, Bushaltestellen und Baenke (nach allen anderen Gruppen aufrufen)."""
    R = _Raster(gruppen)
    del PLATZIERT[:]
    b = Bau("ausstattung")
    belegt = []

    def setze(fn, x, y, th, w, d):
        ok, zb = _ort_ok(R, P, x, y, th, w, d)
        if not ok:
            return False
        for (bx0, by0, bx1, by1) in belegt:
            fx0, fy0, fx1, fy1 = _footprint(x, y, th, w, d)
            if bx0 < fx1 and bx1 > fx0 and by0 < fy1 and by1 > fy0:
                return False
        fn(b, x, y, zb, th)
        PLATZIERT.append((fn.__name__, round(x, 1), round(y, 1), th))
        belegt.append(_footprint(x, y, th, w, d))
        return True

    for kand in (BRUNNEN_STEIN, BRUNNEN_STAHL):
        fn = trinkbrunnen_stein if kand is BRUNNEN_STEIN else trinkbrunnen_stahl
        w, d = (2.6, 2.0) if kand is BRUNNEN_STEIN else (1.4, 1.4)
        gesetzt = 0
        for (x, y, th) in kand:
            if gesetzt >= (4 if kand is BRUNNEN_STEIN else 4):
                break
            # nur ein Brunnen je Gebiet (Abstand > 25 m zu bereits gesetzten gleicher Art)
            if any(math.hypot(x - bx, y - by) < 25.0 for (bx, by) in ABGESETZT.get(fn.__name__, [])):
                continue
            if setze(fn, x, y, th, w, d):
                ABGESETZT.setdefault(fn.__name__, []).append((x, y))
                gesetzt += 1
    for (name, kand) in HALT:
        for (x, y, th) in kand:
            if setze(bushaltestelle, x, y, th, 5.8, 2.6):
                break
    for (x, y, th) in BAENKE_PLATZ:
        setze(bank, x, y, th, 1.8, 0.7)
    for (x, y, th) in _kandidaten_baenke():
        setze(bank, x, y, th, 1.8, 0.7)
    ABGESETZT.clear()
    return [b]


ABGESETZT = {}
PLATZIERT = []                      # (Art, x, y, th) der zuletzt gesetzten Teile (Pruefung/Debug)
