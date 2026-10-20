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
    fn = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[face]
    b.prism(sx_ - fn[0] * 0.14, sy_ - fn[1] * 0.14, zb, 0.05, 2.3, 6, "Schild Pfosten")                   # Pfosten hinter der Tafel
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


def _ort_ok(R, P, x, y, th, w, d, zb_tol=0.3, teich_ok=False):
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
        if math.hypot(x - tx, y - ty) < tr + (2.6 if teich_ok else 3.0):
            return False, 0.0
    return True, zb


# Kandidaten: (x, y, th)
# Trinkbrunnen: je Gebiet nur einer (erster passender Kandidat) - dort, wo Menschen sich aufhalten
BRUNNEN_STEIN = (("Marktplatz", ((68.4, 137.6, 270), (41.6, 137.6, 90), (68.4, 162.4, 270), (41.6, 162.4, 90))),
                 ("Dorf Nord", ((143.5, 230.0, 90), (156.5, 232.0, 270), (143.5, 214.0, 90))),
                 ("Bahnhofsvorplatz", ((136.5, 54.5, 90), (163.5, 54.5, 270), (141.0, 50.0, 90))))
BRUNNEN_STAHL = (("Flugplatz Tower", ((232.2, 156.0, 270), (232.2, 146.0, 270), (221.0, 156.0, 90))),
                 ("Zeltplatz", ((283.5, 281.0, 90), (284.0, 297.0, 0), (294.0, 281.0, 270))),
                 ("Steinbruch", ((86.0, 36.0, 180), (86.0, 66.0, 90), (90.0, 52.0, 270))))

HALT = (  # (Name, Kandidaten (x, y, th)) - Vorderseite zur Strasse; keine Haltestellen im Flughafen (x > 205)
    ("Nordstrasse O", [(154.7, y, 270) for y in (222.0, 214.0, 232.0, 208.0)]),
    ("Nordstrasse W", [(145.3, y, 90) for y in (232.0, 222.0, 214.0)]),
    ("Suedstrasse W", [(145.3, y, 90) for y in (82.0, 76.0, 88.0, 70.0)]),
    ("Suedstrasse O", [(154.7, y, 270) for y in (70.0, 76.0, 88.0)]),
    ("Markt Ost", [(x, 145.5, 180) for x in (74.5, 77.5, 72.0)]),
    ("Markt West", [(x, 154.5, 0) for x in (33.0, 35.5, 31.0)]),
    ("Hauptstrasse", [(x, 154.5, 0) for x in (88.0, 85.0, 90.5)]),
)

# Rastplaetze auf Gruenflaechen: Anker (x, y, Suchradius) - dort wird der naechste ebene, freie Grasplatz fuer Tisch + zwei Baenke gesucht
RASTPLAETZE = ((113.0, 192.0, 14.0), (30.0, 108.0, 16.0), (25.0, 205.0, 14.0), (172.0, 226.0, 16.0), (186.0, 118.0, 18.0),
               (118.0, 100.0, 14.0), (176.0, 74.0, 14.0), (208.0, 270.0, 14.0), (70.0, 255.0, 14.0))


def tisch(b, x, y, zb, th):
    """Picknicktisch 1,8 x 0,8 m (Tischlaenge lokal x) mit Beinpaaren."""
    g = Lok(b, x, y, zb, math.radians(th))
    g.box(-0.9, -0.4, 0.74, 0.9, 0.4, 0.78, "Holz")
    for sx in (-0.7, 0.7):
        g.box(sx - 0.05, -0.33, 0.0, sx + 0.05, 0.33, 0.74, "Holz dunkel")
    return b


def seerosen(b, tx, ty, tr, nr):
    """Seerosenblaetter (achteckige Scheiben mit Einschnitt, in Flecken) und Bluetenkelche auf dem Teich (Wasserspiegel U.TEICH_Z)."""
    import talkessel as T
    z = U.TEICH_Z + 0.03
    for k in range(70 + 14 * nr):
        a = T._h01(k, nr, 7001) * 6.2832
        r = (tr + 0.5) * math.sqrt(T._h01(k, nr, 7002)) * 0.93
        px, py = tx + r * math.cos(a), ty + r * math.sin(a)
        fl = T.fbm(px / 3.0, py / 3.0, T.SEED + 611, 2)
        if fl < 0.42 and T._h01(k, nr, 7003) > 0.12:
            continue
        rad = 0.22 + 0.30 * T._h01(k, nr, 7004)
        ph = T._h01(k, nr, 7005) * 6.2832
        n = 9
        ring = [(px + rad * math.cos(ph + 0.35 + (6.2832 - 0.7) * i / (n - 1)), py + rad * math.sin(ph + 0.35 + (6.2832 - 0.7) * i / (n - 1)), z) for i in range(n)]
        b.add([(px, py, z + 0.015)] + ring, [(0, 1 + i, 2 + i) for i in range(n - 1)], "Seerose Blatt" if T._h01(k, nr, 7006) > 0.3 else "Seerose Blatt hell")
        if T._h01(k, nr, 7007) < 0.28:                                              # Bluete: Kranz aus 6 Blaettern ueber einer gelben Mitte
            bx_, by_ = px + 0.1 * math.cos(ph), py + 0.1 * math.sin(ph)
            mat = "Seerose weiss" if T._h01(k, nr, 7008) < 0.6 else "Seerose rosa"
            for j in range(6):
                aj = ph + j * 1.0472
                tip = (bx_ + 0.16 * math.cos(aj), by_ + 0.16 * math.sin(aj), z + 0.13)
                l_ = (bx_ + 0.05 * math.cos(aj - 0.5), by_ + 0.05 * math.sin(aj - 0.5), z + 0.02)
                r_ = (bx_ + 0.05 * math.cos(aj + 0.5), by_ + 0.05 * math.sin(aj + 0.5), z + 0.02)
                b.add([l_, r_, tip], [(0, 1, 2), (2, 1, 0)], mat)
            b.prism(bx_, by_, z + 0.01, 0.04, 0.06, 5, "Seerose Mitte")


S.FARBEN.update({"Seerose Blatt": ((0.12, 0.34, 0.14), 0.7, 0.0), "Seerose Blatt hell": ((0.22, 0.45, 0.18), 0.7, 0.0),
                 "Seerose weiss": ((0.95, 0.94, 0.88), 0.6, 0.0), "Seerose rosa": ((0.93, 0.60, 0.72), 0.6, 0.0), "Seerose Mitte": ((0.95, 0.78, 0.15), 0.6, 0.0)})
for _k in ("Seerose Blatt", "Seerose Blatt hell", "Seerose weiss", "Seerose rosa", "Seerose Mitte"):
    U.FARBEN.setdefault(_k, S.FARBEN[_k])


def wegweiser(b, x, y, zb, face, eintraege):
    """Wegweiser: Mittelpfosten mit uebereinander gestapelten Richtungstafeln (gelb, schwarze Schrift, Pfeil); eintraege = [(Text, Pfeil)] von oben nach unten."""
    n = len(eintraege)
    for i, (text, pfeil) in enumerate(eintraege):
        SC.schild(b, x, y, face, [("richtung", text, pfeil)], pfosten=False, unten=1.15 + 0.95 * (n - 1 - i), zb=zb)
    k = SC.SCHILD_SKALA
    h = (1.15 + 0.95 * (n - 1) + SC.TAFEL_H - 0.1) * k
    nx, ny = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[face]
    px, py = x - nx * 0.16 * k, y - ny * 0.16 * k                          # Pfosten hinter den Tafeln (Tafeldicke 0,08 m, Pfosten dahinter)
    b.prism(px, py, zb - 0.5, 0.06, h + 0.5, 6, "Schild Pfosten")
    b.bx.append((px - 0.06, py - 0.06, zb - 0.5, px + 0.06, py + 0.06, zb + h))


def _wegweiser_orte():
    """(Name, Winkel/Position, Blickrichtung, Eintraege): an den Ringabzweigen jeweils vor der Einmuendung auf der Aussenseite (Fahrer sehen die Vorderseite)."""
    pi = math.pi
    return (("Ring W nord", pi + 0.22, "S", [("RATHAUS", "links"), ("KREISEL", "oben")]),
            ("Ring W sued", pi - 0.22, "N", [("RATHAUS", "rechts"), ("BAHNHOF", "oben")]),
            ("Ring S west", -pi / 2 - 0.22, "W", [("FLUGPLATZ", "oben"), ("BAHNHOF", "rechts")]),
            ("Ring S ost", -pi / 2 + 0.22, "E", [("BAHNHOF", "links")]),
            ("Ring N west", pi / 2 + 0.22, "W", [("KREISEL", "links")]),
            ("Ring N ost", pi / 2 - 0.22, "E", [("KREISEL", "rechts")]),
            ("Ring O sued", -0.45, "S", [("FLUGPLATZ", "rechts")]),
            ("Ring O nord", 0.45, "N", [("FLUGPLATZ", "links")]))


def bauen(gruppen, P):
    """Gruppen 'ausstattung' (Brunnen, Haltestellen, Rastplaetze mit Tisch und Baenken, Teichbaenke) und 'seerosen'."""
    import gras as GR
    R = _Raster(gruppen)
    M = GR.maske(P)
    del PLATZIERT[:]
    b = Bau("ausstattung")
    belegt = []

    def setze(fn, x, y, th, w, d, **kw):
        ok, zb = _ort_ok(R, P, x, y, th, w, d, **kw)
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

    def gras_ok(x0, y0, x1, y1, flug=False):
        """Alle Stichproben des Rechtecks sind Grasflaeche (nicht Strasse, Wasser, Graben, Hof, Flugplatz)."""
        for k in range(5):
            for m in range(5):
                px, py = x0 + (x1 - x0) * k / 4, y0 + (y1 - y0) * m / 4
                if (M.im_flug(px, py) and not flug) or not M.ok(px, py, flug_gras=flug):
                    return False
        return True

    for kand, fn, (w, d) in ((BRUNNEN_STEIN, trinkbrunnen_stein, (2.6, 2.0)), (BRUNNEN_STAHL, trinkbrunnen_stahl, (1.4, 1.4))):
        for (_name, liste) in kand:
            for (x, y, th) in liste:
                if setze(fn, x, y, th, w, d):
                    break
    for (name, kand) in HALT:
        for (x, y, th) in kand:
            if x < 205.0 and setze(bushaltestelle, x, y, th, 5.8, 2.6):
                break
    # Rastplaetze: Tisch (Laenge entlang u) mit zwei einander gegenueberstehenden Baenken, nur auf Gras, nicht im Flughafen
    for si, (ax, ay, rad) in enumerate(RASTPLAETZE):
        gefunden = False
        for ring in range(0, int(rad // 2) + 1):
            if gefunden:
                break
            for k in range(max(1, 8 * ring)):
                a = 6.2832 * k / max(1, 8 * ring) + si
                x, y = ax + 2.0 * ring * math.cos(a), ay + 2.0 * ring * math.sin(a)
                for rot in ((0, 90) if si % 2 == 0 else (90, 0)):
                    w, d = 2.2, 3.7
                    x0, y0, x1, y1 = _footprint(x, y, rot, w, d)
                    if not gras_ok(x0 - 1.0, y0 - 1.0, x1 + 1.0, y1 + 1.0):
                        continue
                    ok0, _zb = _ort_ok(R, P, x, y, rot, w + 0.6, d + 0.6)
                    if not ok0:
                        continue
                    c, sn = math.cos(math.radians(rot)), math.sin(math.radians(rot))
                    ok1 = setze(tisch, x, y, rot, 1.8, 0.8)
                    if not ok1:
                        continue
                    for v, th in ((1.15, rot), (-1.15, rot + 180)):
                        setze(bank, x - v * sn, y + v * c, th % 360, 1.8, 0.7)
                    gefunden = True
                    break
                if gefunden:
                    break
    # Teiche: Einzelbaenke am Ufer mit Blick zum Wasser (Achsenrichtungen; hoechstens zwei je Teich, auf Gras)
    for ti, (tx, ty, tr) in enumerate(U.TEICHE):
        d = tr + 3.6
        n = 0
        for (dx, dy, th) in ((0, -1, 180), (-1, 0, 90), (1, 0, 270), (0, 1, 0)):     # Bank steht in Richtung (dx, dy) vom Teich, schaut zur Mitte
            if n >= 2:
                break
            x, y = tx + dx * d, ty + dy * d
            w, dd = 1.8, 0.7
            x0, y0, x1, y1 = _footprint(x, y, th, w, dd)
            if not gras_ok(x0, y0, x1, y1):
                continue
            if setze(bank, x, y, th, w, dd, zb_tol=0.5, teich_ok=True):
                n += 1
    # Wegweiser an den Ringabzweigen (Rathaus, Bahnhof, Flugplatz, Kreisel = Nordkreisel) und am Abzweig zum Steinbruch
    def wegweiser_setzen(anker, face, eintraege):
        th = 0 if face in ("N", "S") else 90
        w = max(SC._tafel_breite(t, p) for t, p in eintraege) + 0.2
        kand = sorted(((dx, dy) for dx in range(-12, 13) for dy in range(-12, 13)), key=lambda q: q[0] ** 2 + q[1] ** 2)
        for dx, dy in kand:
            x, y = anker[0] + dx * 0.75, anker[1] + dy * 0.75
            x0, y0, x1, y1 = _footprint(x, y, th, w, 0.4)
            if not gras_ok(x0 - 0.3, y0 - 0.3, x1 + 0.3, y1 + 0.3, flug=True):
                continue
            if any(bx0 < x1 and bx1 > x0 and by0 < y1 and by1 > y0 for (bx0, by0, bx1, by1) in belegt):
                continue
            ok, zb = _ort_ok(R, P, x, y, th, w, 0.4, zb_tol=0.9)
            if ok:
                wegweiser(b, x, y, zb, face, eintraege)
                PLATZIERT.append(("wegweiser:" + eintraege[0][0], round(x, 1), round(y, 1), face))
                belegt.append((x0, y0, x1, y1))
                return True
        print("Hinweis: Wegweiser %s nicht platzierbar" % eintraege[0][0])
        return False

    for (_n, a, face, eintr) in _wegweiser_orte():
        wegweiser_setzen(U.ring_punkt(a, U.BREITE_WEG / 2 + 1.5), face, eintr)
    wegweiser_setzen((86.3, 108.0), "N", [("STEINBRUCH", "rechts")])
    ABGESETZT.clear()
    # Seerosen auf allen Teichen
    sr = Bau("seerosen")
    for ti, (tx, ty, tr) in enumerate(U.TEICHE):
        seerosen(sr, tx, ty, tr, ti)
    return [b, sr]


ABGESETZT = {}
PLATZIERT = []                      # (Art, x, y, th) der zuletzt gesetzten Teile (Pruefung/Debug)
