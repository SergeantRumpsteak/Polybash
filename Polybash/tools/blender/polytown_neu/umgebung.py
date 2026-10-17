"""Polybash - Umgebung der Burg: Ringweg, Flughafen mit Landebahn, Vorfeld, Hangars, Tower, Zaun und Wegen.

Lage (Spielflaeche 0..300 m, Burgmitte C = 150/150, Tore der Burg im Norden und Sueden):
  * Die Ostmauer der Burg hat keinen Ausgang -> die Ostkante der Karte (x = 300) ist die Bezugskante.
  * Ringweg um die Burg (Mittelradius 52 m, ausserhalb des Wassergrabens) mit Zufahrten von den Bruecken.
  * Flughafen im Osten, Landebahn Nord-Sued (150 x 14 m) bei x = 256:
      - westlich der Bahn die Flughafenstrasse (x = 226): an ihr enden die beiden Abzweige vom Ring (45 Grad) und der Zubringer;
        Tower auf halber Bahnlaenge neben dem Zubringer, grosser Hangar am Suedende (offen zur Bahn);
      - oestlich der Bahn: Rollweg (parallel, ueber drei Anschluesse an die Bahn und an den Enden um die Bahn herum mit der
        Strasse verbunden), Vorfeld und davor die Hangarreihe: drei Tonnenhallen, die ohne Zwischenraum ineinander uebergehen
        und bis kurz vor die Berge reichen, zur Burg (nach Westen) ganz offen.
  * Das Gelaende ist eingezaeunt (Zaun x = 217 .. 299, y = 60 .. 240). Haupteingang ist der Zubringer (Checkpoint mit zwei
    Schranken); die beiden Abzweige vom Ring haben je ein Tor mit Schranke.
Gelbe Rollwegmittellinien laufen von den Bahnanschluessen ueber den Rollweg bis in alle Hangars; vor der Bahn stehen
Haltelinien (hold short: zwei Vollstriche auf der Wartseite, zwei Strichlinien zur Bahn hin).
Begehbar: Tower (Treppenhaus mit offener Feuerwehrtreppe bis in die Kanzel, Rundumplattform mit Gelaender) und der grosse
Hangar (Tuer im Westen, ganz offen nach Osten).
Noch ohne Texturen (nur Farben); die Bahn hat weisse Markierungen: Zebrastreifen an beiden Enden, je ein Touchdown-Paar in
beide Richtungen und durchgehend die Mittelstriche - sonst nichts.
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
RC = 12.0                                                             # Kurvenradius (Mittellinie) der Umfahrung der Bahnenden
UMFAHRUNG = ((SX, Y_SUED), (TAXI_X, Y_SUED), (TAXI_X, Y_NORD), (SX, Y_NORD))      # Mittellinie der Schleife (Ecken werden abgerundet)
ANSCHLUESSE = (80.0, 150.0, 220.0)                                    # Rollweg-Anschluesse an die Bahn (y)
# Hangarreihe: drei getrennte Tonnenhallen mit je eigenem Halbkreis-Dach (Radius = halbe Teilung REIHE_B = 1,3 x 16 m); wo ein Dach
# in den Boden geht, beginnt das naechste direkt wieder (die Halbkreise beruehren sich am Boden)
REIHE_N, REIHE_B = 3, 20.8
REIHE_R = REIHE_B / 2
REIHE_X0, REIHE_T = 279.0, 19.0                                       # offene Westkante, Tiefe: Rueckwand bei x = 298 (Talkante 300)
REIHE_YC = tuple(BY + (i - (REIHE_N - 1) / 2.0) * REIHE_B for i in range(REIHE_N))       # Achsen der drei Hallen
REIHE_Y0, REIHE_Y1 = REIHE_YC[0] - REIHE_R, REIHE_YC[-1] + REIHE_R                       # gesamte Breite 62,4 m
TANK_POS = (288.0, 108.0)                                             # Mitte der Abstellposition an der Tankstelle
RC_GELB = 4.5                                                         # Radius der gelben Abbiegelinien
TANK = (REIHE_X0, 88.0, 297.0, 116.0)                                 # Tankstelle (Asphaltflaeche) suedlich der Hallen, an Vorfeld/Rollweg
VORFELD = (TAXI_X + TAXI_B / 2, TANK[1], REIHE_X0, REIHE_Y1)         # Vorfeld zwischen Rollweg und Hallen (reicht bis zur Tankstelle)
HELI = (240.0, 184.0, 8.0)                                            # Helipad nordlich vom Tower auf der Gruenflaeche: Mitte, Radius
# Grosser Hangar am Suedende westlich der Bahn, offen nach Osten (zur Bahn), Tuer im Westen
HX, HY, HW, HD, HH = 237.5, 90.0, 12.0, 28.0, 6.0                    # Mitte, Breite (x), Tiefe (y), Hoehe
HANGAR = (HX - HW / 2, HY - HD / 2, HX + HW / 2, HY + HD / 2)       # (231.5, 76, 243.5, 104): 28 m lang in Bahnrichtung
# Tower westlich der Bahn auf halber Bahnlaenge: Sockelgebaeude (12 x 10 m) mit dem Treppenschacht (6 x 6 m) in der Nordhaelfte
TX, TY = 240.0, 162.0
TOWER_ANNEX = (TX - 6.0, TY - 5.0, TX + 6.0, TY + 5.0)
SCY = TY + 1.6                                                        # Mitte des Schachts (y); Schachtnordwand sitzt an der Sockelnordwand
Z_BODEN, Z_KAB = 0.07, 13.3
RADAR_Z = 17.0                                                        # Drehpunkt der Radaranlage auf dem Kanzeldach                                           # Hallenboden, Kanzelboden
# Stadt (siehe stadt.py): ebene Zonen fuer Staedte/Doerfer (x0, y0, x1, y1) und Teiche (x, y, Radius) - das Gelaende richtet sich danach
STADT_ZONEN = ((10.0, 80.0, 100.0, 220.0),        # Stadt im Westen (Marktplatz, Rathaus, Wohnviertel)
               (120.0, 216.0, 182.0, 280.0),      # Dorf im Norden
               (120.0, 20.0, 182.0, 84.0),        # Bahnhof im Sueden (Empfangsgebaeude, Bahnsteig, Vorplatz; frueher Dorf mit Kreisverkehr)
               (8.0, 3.0, 100.0, 80.0),           # Steinbruch im Suedwesten (Grube, Hof, Werkstatt) - die Grube selbst ist ein Loch in der Wiese
               (84.0, 8.0, 196.0, 40.0),          # Gleiskorridor Steinbruch -> Bahnhof mit Gueterschuppen und Gueterstrasse
               (190.0, 22.0, 300.0, 32.0, 12.0))   # Gleiskorridor Bahnhof -> Gebirge (Tunnel hinter dem Talrand); schmal, Huegel duerfen direkt daneben beginnen
TEICHE = ((16.0, 236.0, 9.0), (110.0, 60.0, 8.0), (190.0, 246.0, 9.0), (192.0, 50.0, 8.0))
# Burgberg nordlich der Stadt (hinter der Kirche): ebener Gipfel (Radius RUINE_R0) in Hoehe RUINE_Z, Flanken bis RUINE_R1 (siehe ruine.py)
RUINE = (54.0, 261.0)
RUINE_Z = 16.0
RUINE_R0, RUINE_R1 = 14.0, 40.0
TEICH_Z = -0.4                                    # Wasserspiegel
# Zaun und Eingang
GATE_X = 217.0                                                        # Zaunlinie im Westen (zwischen Ring und Flughafenstrasse)
ZAUN = (GATE_X, 60.0, 299.0, 240.0)
GELB_B, Z_GELB0, Z_GELB1 = 0.4, 0.07, 0.10
HOLD_D = (1.5, 2.1, 2.7, 3.3)                                         # Abstand der Haltelinien von der Bahnkante (Strich, Strich, voll, voll)

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
    "Markierung gelb": ((0.95, 0.76, 0.08), 0.7, 0.0),
    "Tower Stufen":    ((0.36, 0.38, 0.38), 0.5, 0.0),
    "Schranke rot":    ((0.75, 0.10, 0.08), 0.6, 0.0),
    "Schranke weiss":  ((0.93, 0.93, 0.90), 0.6, 0.0),
    "Windsack orange": ((0.95, 0.45, 0.08), 0.7, 0.0),
    "Zapfsaeule":      ((0.78, 0.14, 0.10), 0.5, 0.0),
    "Tank":            ((0.78, 0.80, 0.80), 0.5, 0.2),
    "Insel":           ((0.55, 0.55, 0.53), 0.95, 0.0),
}


# ------------------------------------------------------------------ Gelaende: Huegel und Senken, Ringweg
# Der Ringweg ist nicht exakt kreisfoermig: sein Mittelradius schwankt natuerlich zwischen RING_R und RING_R + 5,5 m
# (nach innen darf er nicht, dort liegt der Wassergraben). Festgelegte Phasen -> reproduzierbar.
_RING_OBERWELLEN = ((2, 0.55, 0.9), (3, 0.30, 4.1), (5, 0.17, 2.2), (7, 0.09, 5.3))


def ring_r(a):
    """Mittelradius des Ringwegs in Richtung a (Bogenmass, 0 = Osten)."""
    s = sum(am * math.sin(k * a + ph) for k, am, ph in _RING_OBERWELLEN)
    s /= sum(am for _, am, _ in _RING_OBERWELLEN)                     # -1..1
    return RING_R + 2.75 + 2.75 * s


def ring_punkt(a, versatz=0.0):
    r = ring_r(a) + versatz
    return (C + r * math.cos(a), C + r * math.sin(a))


def abzweig(s):
    """Gerader Abzweig vom Ring (Richtung +-45 Grad) bis zur Flughafenstrasse: Anfang (auf dem Ring), Ende (x = SX)."""
    u = (math.sqrt(0.5), s * math.sqrt(0.5))
    a0 = ring_punkt(s * math.pi / 4)
    d_end = (SX - a0[0]) / u[0]
    return a0, (a0[0] + u[0] * d_end, a0[1] + u[1] * d_end)


def strassen_achsen():
    """Mittellinien der Wege im Huegelland (Strecken), fuer die Abflachung der Huegel entlang der Wege."""
    ach = []
    for s in (-1, 1):
        ach.append(((C, C + s * (B.A + 11.0)), ring_punkt(s * math.pi / 2)))
        ach.append(abzweig(s))
    ach.append((ring_punkt(0.0), (BAHN[0], C)))
    return ach


def _seg_abstand(x, y, p, q):
    dx, dy = q[0] - p[0], q[1] - p[1]
    t = max(0.0, min(1.0, ((x - p[0]) * dx + (y - p[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - p[0] - t * dx, y - p[1] - t * dy)


_ACHSEN = None


KUPPEN = ((255.0, 10.0, 22.0, 9.0), (232.0, 12.0, 14.0, 5.0), (285.0, 14.0, 16.0, 7.0), (100.0, 288.0, 16.0, 6.0),
          (22.0, 268.0, 16.0, 7.0), (236.0, 272.0, 16.0, 7.0), (276.0, 284.0, 14.0, 6.0), (196.0, 290.0, 12.0, 5.0),
          (213.0, 7.0, 11.0, 6.0), (268.0, 6.0, 13.0, 8.0), (244.0, 41.0, 11.0, 6.0), (272.0, 42.0, 12.0, 7.0), (214.0, 40.0, 9.0, 4.0))   # Waldhuegel an der Bahnstrecke


def huegel_roh(x, y):
    """Huegel (bis etwa 12 m) und flache Senken (bis etwa -4 m) als weiche Landschaft: grosse Wellen (Wellenlaenge ~110 m), dazu
    kleinere Kuppen (~55 m) und feine Bodenwellen (~26 m)."""
    n = T.fbm(x / 110.0, y / 110.0, T.SEED + 21, 3)
    v = (n - 0.5) * 4.5 + 0.12
    h = 15.0 * v if v > 0 else 5.5 * v
    h += 5.0 * (T.fbm(x / 55.0, y / 55.0, T.SEED + 25, 2) - 0.5) * 2.0
    for kx, ky, kr, kh in KUPPEN:                                                                # einzelne markante Huegel mit Gesteinsrippen
        d2 = ((x - kx) ** 2 + (y - ky) ** 2) / (kr * kr)
        if d2 < 6.0:
            h += kh * math.exp(-d2) * (0.85 + 0.3 * T.noise(x / 9.0, y / 9.0, T.SEED + 41))
    return h + 1.4 * (T.fbm(x / 26.0, y / 26.0, T.SEED + 23, 2) - 0.5) * 2.0


def _flach(x, y):
    """Gemeinsame Maske (0..1) ausser der Wegabflachung: Burggelaende, Flugplatz mit Zaun, Talrand."""
    m = B.smoothstep(0.0, 1.0, math.hypot(max(205.0 - x, 0.0) / 26.0, max(52.0 - y, 0.0) / 14.0, max(y - 248.0, 0.0) / 26.0))   # Flugplatz: x >= 205, y 52..248
    m *= B.smoothstep(0.0, 14.0, min(x, T.TAL - x, y, T.TAL - y))                                # Talrand (dort schliessen die Berge an, z = 0)
    for zz in STADT_ZONEN:                                                                       # Stadt und Doerfer: ebener Baugrund
        x0, y0, x1, y1 = zz[:4]
        m *= B.smoothstep(0.0, zz[4] if len(zz) > 4 else 20.0, math.hypot(max(x0 - x, 0.0, x - x1), max(y0 - y, 0.0, y - y1)))
    for tx, ty, tr in TEICHE:                                                                    # rund um Teiche flaches Ufer
        m *= B.smoothstep(tr + 2.0, tr + 20.0, math.hypot(x - tx, y - ty))
    return m


def gelaende_maske(x, y):
    """0 = eben, 1 = volle Huegel. Eben: Burggelaende (Quadrat), Flughafengelaende (mit Zaun) und Talrand; entlang der Wege
    (Ring, Abzweige, Zubringer) nur schwache Bodenwellen."""
    global _ACHSEN
    if _ACHSEN is None:
        _ACHSEN = strassen_achsen()
    c = max(abs(x - C), abs(y - C))
    m = B.smoothstep(42.0, 62.0, c) * _flach(x, y)                     # Burg: Chebyshev-Abstand 42 m (Patch endet bei 40 m)
    d = abs(math.hypot(x - C, y - C) - ring_r(math.atan2(y - C, x - C)))
    for p, q in _ACHSEN:
        d = min(d, _seg_abstand(x, y, p, q))
    return m * (0.18 + 0.82 * B.smoothstep(7.0, 22.0, d))              # Wege: nur kleine Unebenheiten


def gelaende_hoehe(x, y):
    """Hoehe der Wiese im Tal bei (x, y)."""
    m = gelaende_maske(x, y)
    c = max(abs(x - C), abs(y - C))
    ms = B.smoothstep(44.0, 54.0, c) * _flach(x, y)                    # kleine Bodenwellen auch entlang der Wege (nicht auf dem Burgplatz)
    h = (huegel_roh(x, y) * m if m > 1e-6 else 0.0) + (1.6 * (T.fbm(x / 30.0, y / 30.0, T.SEED + 31, 2) - 0.5) * ms if ms > 1e-6 else 0.0)
    dr = math.hypot(x - RUINE[0], y - RUINE[1])                                                  # Burgberg: ebener Gipfel, Flanken mit Felsrippen
    if dr < RUINE_R1 + 22.0:
        h *= 0.35 + 0.65 * B.smoothstep(RUINE_R1, RUINE_R1 + 22.0, dr)                       # rund um den Burgberg flacheres Land: er ragt heraus
    for tx, ty, tr in TEICHE:                                                                    # Teichmulden
        d = math.hypot(x - tx, y - ty)
        if d < tr + 3.5:
            h -= 2.4 * (1.0 - B.smoothstep(tr - 2.0, tr + 3.5, d))
    if dr < RUINE_R1:
        w = (1.0 - B.smoothstep(RUINE_R0, RUINE_R1, dr)) * B.smoothstep(0.0, 14.0, min(x, T.TAL - x, y, T.TAL - y))
        h = h * (1.0 - w) + (RUINE_Z + 3.2 * (T.fbm(x / 9.0, y / 9.0, T.SEED + 51, 2) - 0.5) * 4.0 * w * (1.0 - w)) * w
    return 0.0 if abs(h) < 1e-9 else h


def _z_auf(x, y, z0, hf):
    h = hf(x, y) if hf else 0.0
    return h + z0 + 0.03 * min(1.0, abs(h) / 0.05)                     # kleiner Zuschlag, damit die Wiese nicht durchsticht


# ------------------------------------------------------------------ flache Wegstuecke (Oberflaechen)
def streifen(b, p0, p1, w, z, mat, hf=gelaende_hoehe, schritt=3.0):
    """Gerades Wegstueck von p0 nach p1 (Breite w), dem Gelaende folgend (Hoehe z ueber der Wiese), Normale nach oben."""
    dx, dy = p1[0] - p0[0], p1[1] - p0[1]
    ln = math.hypot(dx, dy)
    nx, ny = -dy / ln * w / 2, dx / ln * w / 2
    n = max(1, int(math.ceil(ln / schritt)))
    v = []
    for i in range(n + 1):
        cx, cy = p0[0] + dx * i / n, p0[1] + dy * i / n
        for sg in (1, -1):
            x, y = cx + sg * nx, cy + sg * ny
            v.append((x, y, _z_auf(x, y, z, hf)))
    f = [(2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2) for i in range(n)]
    b.add(v, f, mat)


def rund(pts, r, geschlossen=False, n=8):
    """Ersetzt die Ecken eines Linienzugs durch Kreisbogen (Radius r, je n Teilstuecke); bei zu kurzen Seiten wird r verkleinert."""
    m = len(pts)
    out = []
    for i in range(m):
        if not geschlossen and i in (0, m - 1):
            out.append(tuple(pts[i]))
            continue
        P, A, Cc = pts[i], pts[i - 1], pts[(i + 1) % m]
        u1 = (A[0] - P[0], A[1] - P[1]); l1 = math.hypot(*u1); u1 = (u1[0] / l1, u1[1] / l1)
        u2 = (Cc[0] - P[0], Cc[1] - P[1]); l2 = math.hypot(*u2); u2 = (u2[0] / l2, u2[1] / l2)
        th = math.acos(max(-1.0, min(1.0, u1[0] * u2[0] + u1[1] * u2[1])))
        if th > math.pi - 1e-3:
            out.append(tuple(P))
            continue
        t = r / math.tan(th / 2)
        t = min(t, l1 / 2 if (geschlossen or i > 1) else l1 - 0.01, l2 / 2 if (geschlossen or i < m - 2) else l2 - 0.01)
        rr = t * math.tan(th / 2)
        T1 = (P[0] + u1[0] * t, P[1] + u1[1] * t)
        T2 = (P[0] + u2[0] * t, P[1] + u2[1] * t)
        bis = (u1[0] + u2[0], u1[1] + u2[1]); lb = math.hypot(*bis); bis = (bis[0] / lb, bis[1] / lb)
        M = (P[0] + bis[0] * rr / math.sin(th / 2), P[1] + bis[1] * rr / math.sin(th / 2))
        a1 = math.atan2(T1[1] - M[1], T1[0] - M[0]); a2 = math.atan2(T2[1] - M[1], T2[0] - M[0])
        da = (a2 - a1 + math.pi) % (2 * math.pi) - math.pi
        for k in range(n + 1):
            aa = a1 + da * k / n
            out.append((M[0] + rr * math.cos(aa), M[1] + rr * math.sin(aa)))
    return out


def pfad(b, pts, w, z, mat, geschlossen=False, hf=gelaende_hoehe, schritt=3.0):
    """Weg (Breite w) entlang eines Linienzugs, dem Gelaende folgend; zu lange Stuecke werden unterteilt. Normale nach oben."""
    q = []
    m = len(pts)
    for i in range(m if geschlossen else m - 1):
        p0, p1 = pts[i], pts[(i + 1) % m]
        ln = math.hypot(p1[0] - p0[0], p1[1] - p0[1])
        n = max(1, int(math.ceil(ln / schritt)))
        q += [(p0[0] + (p1[0] - p0[0]) * k / n, p0[1] + (p1[1] - p0[1]) * k / n) for k in range(n)]
    if not geschlossen:
        q.append(tuple(pts[-1]))
    v = []
    M = len(q)
    for i in range(M):
        a = q[(i - 1) % M] if (geschlossen or i > 0) else q[i]
        c = q[(i + 1) % M] if (geschlossen or i < M - 1) else q[i]
        dx, dy = c[0] - a[0], c[1] - a[1]
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln * w / 2, dx / ln * w / 2
        for sg in (1, -1):
            x, y = q[i][0] + sg * nx, q[i][1] + sg * ny
            v.append((x, y, _z_auf(x, y, z, hf)))
    f = [(2 * i, 2 * i + 1, 2 * ((i + 1) % M) + 1, 2 * ((i + 1) % M)) for i in range(M if geschlossen else M - 1)]
    b.add(v, f, mat)


def ring(b, w, z, mat, n=180, hf=gelaende_hoehe):
    """Ringweg (Breite w) um die Burgmitte mit schwankendem Mittelradius ring_r(a), dem Gelaende folgend; n Vierecke."""
    v = []
    for i in range(n):
        a = 2 * math.pi * i / n
        r = ring_r(a)
        for rr in (r - w / 2, r + w / 2):
            x, y = C + rr * math.cos(a), C + rr * math.sin(a)
            v.append((x, y, _z_auf(x, y, z, hf)))
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
    ring(b, BREITE_WEG, Z_RING, "Weg")
    # Zufahrten von den beiden Bruecken (Bruecken enden bei C +- 36,5) bis zur Mitte des Rings
    for s in (-1, 1):
        streifen(b, (C, C + s * (B.A + 11.0)), ring_punkt(s * math.pi / 2), BREITE_WEG, Z_WEG, "Weg")
    # Flughafenstrasse (Nord-Sued) westlich der Bahn, mit runder Umfahrung der Bahnenden zum Rollweg: geschlossene Schleife um die Bahn
    pfad(b, rund(UMFAHRUNG, RC, geschlossen=True), BREITE_WEG, Z_WEG, "Weg", geschlossen=True)
    # zwei gerade Abzweige vom Ring (bei +-45 Grad); sie enden dort, wo sie auf die Flughafenstrasse treffen
    for s in (-1, 1):
        a0, a1 = abzweig(s)
        streifen(b, a0, a1, BREITE_WEG, Z_WEG, "Weg")
    # Zubringer vom Ring nach Osten: ueber die Strasse bis zur Bahnmitte (Rollweg-Anschluss von Westen)
    streifen(b, ring_punkt(0.0), (BAHN[0], C), BREITE_WEG, Z_WEG, "Weg")
    # Zugang zum Tower (Westtuer) und zum Hangar (Westtuer) von der Strasse
    streifen(b, (TX, C + BREITE_WEG / 2 - 0.5), (TX, TOWER_ANNEX[1]), 3.0, Z_WEG, "Weg")
    streifen(b, (SX + BREITE_WEG / 2 - 0.5, HY), (HANGAR[0], HY), 3.0, Z_WEG, "Weg")
    return b


# ------------------------------------------------------------------ gelbe Rollwegmarkierung, Haltelinien
def gelbe_linie_x(b, xa, xb, y, sperr=()):
    """Gelbe Mittellinie (Breite GELB_B) entlang x bei y; die x-Intervalle in 'sperr' (Vollstriche der Haltelinie) bleiben frei."""
    segs = [(min(xa, xb), max(xa, xb))]
    for (s0, s1) in sperr:
        neu = []
        for a, c in segs:
            if s1 <= a or s0 >= c:
                neu.append((a, c))
                continue
            if s0 > a:
                neu.append((a, s0))
            if s1 < c:
                neu.append((s1, c))
        segs = neu
    for a, c in segs:
        if c - a > 0.05:
            b.box(a, y - GELB_B / 2, Z_GELB0, c, y + GELB_B / 2, Z_GELB1, "Markierung gelb")


def gelb_bogen(b, cx, cy, r, a0, a1, n=10):
    """Gelber Kreisbogen (Mittellinie, Breite GELB_B) um (cx, cy) von Winkel a0 bis a1 (Grad), flach auf Z_GELB1."""
    ri, ra = r - GELB_B / 2, r + GELB_B / 2
    v, f = [], []
    for i in range(n + 1):
        a = math.radians(a0 + (a1 - a0) * i / n)
        v += [(cx + ri * math.cos(a), cy + ri * math.sin(a), Z_GELB1), (cx + ra * math.cos(a), cy + ra * math.sin(a), Z_GELB1)]
    for i in range(n):
        q = (2 * i, 2 * i + 1, 2 * i + 3, 2 * i + 2)
        f.append(q if a1 > a0 else q[::-1])
    b.add(v, f, "Markierung gelb")


def haltelinie(b, x_bahn, rich, yc, halb):
    """Hold-short-Markierung quer zum Rollweg vor der Bahnkante x_bahn (rich = +1: Rollweg liegt oestlich, -1: westlich).

    Zur Bahn hin zwei Strichlinien (Flugzeuge duerfen von der Bahn her kreuzen), auf der Wartseite zwei Vollstriche.
    Die Strichlinien haben eine gerade Zahl Striche, damit die Mittellinie durch die Luecke in der Mitte laeuft.
    Rueckgabe: x-Intervalle der Vollstriche (die Mittellinie wird dort unterbrochen)."""
    m = "Markierung gelb"
    n = int((2 * halb - 0.4 + 0.5) // 1.3)
    n -= n % 2
    gesamt = n * 0.8 + (n - 1) * 0.5
    ys = yc - gesamt / 2
    for d in HOLD_D[:2]:
        xm = x_bahn + rich * d
        for k in range(n):
            ya = ys + 1.3 * k
            b.box(xm - 0.125, ya, Z_GELB0, xm + 0.125, ya + 0.8, Z_GELB1, m)
    sperr = []
    for d in HOLD_D[2:]:
        xm = x_bahn + rich * d
        b.box(xm - 0.125, yc - gesamt / 2, Z_GELB0, xm + 0.125, yc + gesamt / 2, Z_GELB1, m)
        sperr.append((xm - 0.125, xm + 0.125))
    return sperr



# ------------------------------------------------------------------ Landebahn, Rollweg, Vorfeld
def landebahn():
    b = Bau("umgebung_landebahn")
    x0, y0, x1, y1 = BAHN
    b.box(x0, y0, -0.12, x1, y1, Z_BAHN, "Piste")
    # Rollweg (parallel zur Bahn, oestlich) mit den Anschluessen an die Bahn
    b.box(TAXI_X - TAXI_B / 2, Y_SUED + RC, -0.12, TAXI_X + TAXI_B / 2, Y_NORD - RC, Z_VORFELD, "Vorfeld")          # gerader Teil; die Kurven sind Teil der Schleife
    for yc in ANSCHLUESSE:
        b.box(x1, yc - TAXI_B / 2, -0.12, TAXI_X - TAXI_B / 2, yc + TAXI_B / 2, Z_VORFELD, "Vorfeld")
    # Vorfeld vor der Hangarreihe (zwischen Rollweg und Hallen)
    vx0, vy0, vx1, vy1 = VORFELD
    b.box(vx0, vy0, -0.12, vx1, vy1, Z_VORFELD, "Vorfeld")
    # Vorfeld vor dem grossen Hangar (verbindet ihn mit der Bahn) und Einmuendung der Zufahrt von Westen (breiter Rollweg)
    b.box(HANGAR[2], HANGAR[1] - 1.0, -0.12, x0, HANGAR[3] + 1.0, Z_VORFELD, "Vorfeld")
    b.box(x0 - 12.0, C - 6.0, -0.12, x0, C + 6.0, Z_VORFELD, "Vorfeld")
    # ---- gelbe Rollwegmittellinien und Haltelinien (Oberkante Z_GELB1) ----
    # Rollweg parallel zur Bahn: die Linie beginnt am ersten Anschluss und endet am letzten (dort biegt sie ab)
    rg = RC_GELB
    b.box(TAXI_X - GELB_B / 2, ANSCHLUESSE[0] + rg, Z_GELB0, TAXI_X + GELB_B / 2, ANSCHLUESSE[-1] - rg, Z_GELB1, "Markierung gelb")
    for yc in ANSCHLUESSE:                                       # Rollweg -> runder Bogen -> Haltelinie: die Linie endet am aeusseren Vollstrich
        sp = haltelinie(b, x1, +1, yc, TAXI_B / 2)
        if yc > ANSCHLUESSE[0]:
            gelb_bogen(b, TAXI_X - rg, yc - rg, rg, 0.0, 90.0)       # von Sueden kommend nach Westen
        if yc < ANSCHLUESSE[-1]:
            gelb_bogen(b, TAXI_X - rg, yc + rg, rg, 0.0, -90.0)      # von Norden kommend nach Westen
        gelbe_linie_x(b, x1 + HOLD_D[3] + 0.125, TAXI_X - rg, yc)
    for yc in REIHE_YC:                                          # Rollweg -> Bogen -> Vorfeld -> bis hinten in jede Halle
        gelb_bogen(b, TAXI_X + rg, yc + rg, rg, 180.0, 270.0)
        gelb_bogen(b, TAXI_X + rg, yc - rg, rg, 180.0, 90.0)
        gelbe_linie_x(b, TAXI_X + rg, REIHE_X0 + REIHE_T - 3.0, yc)
    gelbe_linie_x(b, HANGAR[0] + 2.5, x0 - 3.0, HY)              # grosser Hangar: von der Halle bis zur Vorfeldkante (keine Haltelinie)
    # ---- weisse Markierungen (Oberkante Z_MARK) ----
    m = "Markierung weiss"

    def mk(xa, ya, xb, yb):
        b.box(xa, ya, Z_BAHN, xb, yb, Z_MARK, m)

    # Mittellinie durchgehend: Striche 4 m lang, alle 8 m, symmetrisch zur Bahnmitte (16 Striche, erster 13 m vom Bahnende)
    for k in range(16):
        ya = BY - 62.0 + 8.0 * k
        mk(BX - 0.2, ya, BX + 0.2, ya + 4.0)
    for ende in (-1, 1):                                          # -1 = Suedende, +1 = Nordende; jede Richtung gleich
        def y_ab(d0, d1):
            """Abstand d0..d1 (m) von der Schwelle am Ende -> (ya, yb)"""
            return (y0 + d0, y0 + d1) if ende < 0 else (y1 - d1, y1 - d0)
        # Zebrastreifen an der Schwelle: 5 Streifen je Seite, 9 m lang, 3 m hinter dem Bahnende
        ya, yb = y_ab(3.0, 12.0)
        for k in range(5):
            off = 0.9 + 1.2 * k
            for sgn in (-1, 1):
                mk(BX + sgn * off - 0.4, ya, BX + sgn * off + 0.4, yb)
        # Touchdown-Markierung: zwei breite Balken beiderseits der Mittellinie, 42..54 m hinter der Schwelle
        ya, yb = y_ab(42.0, 54.0)
        for sgn in (-1, 1):
            mk(BX + sgn * 4.4 - 0.9, ya, BX + sgn * 4.4 + 0.9, yb)
    return b


# ------------------------------------------------------------------ Hangars
def halle(b, x0, y0, x1, y1, offen, h=6.0, kisten=False, tuer_y=None):
    """Halle mit Boden, Waenden und Dach; 'offen' = Seite ohne Wand ('W' oder 'O'); das Dach ragt dort 1,2 m ueber.

    tuer_y: Mitte einer Tuer (1,4 m breit, 2,3 m hoch) in der geschlossenen Stirnwand (nur bei offen = 'O', Wand im Westen)."""
    t = 0.4
    b.box(x0, y0, -0.12, x1, y1, 0.07, "Hangar Boden")
    b.box(x0, y0, 0.07, x1, y0 + t, h, "Hangar Wand")                                    # Suedwand
    b.box(x0, y1 - t, 0.07, x1, y1, h, "Hangar Wand")                                    # Nordwand
    if offen == "W":
        b.box(x1 - t, y0, 0.07, x1, y1, h, "Hangar Wand")                                # Rueckwand Ost
        b.box(x0 - 1.2, y0 - 0.3, h, x1 + 0.3, y1 + 0.3, h + 0.45, "Hangar Dach")
    else:
        if tuer_y is None:
            b.box(x0, y0, 0.07, x0 + t, y1, h, "Hangar Wand")                            # Rueckwand West
        else:                                                                            # Rueckwand mit Tuerloch
            b.box(x0, y0 + t, 0.07, x0 + t, tuer_y - 0.7, h, "Hangar Wand")
            b.box(x0, tuer_y + 0.7, 0.07, x0 + t, y1 - t, h, "Hangar Wand")
            b.box(x0, tuer_y - 0.7, 2.3, x0 + t, tuer_y + 0.7, h, "Hangar Wand")         # Sturz
            b.box(x0 - 0.05, tuer_y - 0.8, 2.3, x0 + t + 0.05, tuer_y + 0.8, 2.4, "Rahmen")
            b.box(x0 - 0.05, tuer_y - 0.8, 0.07, x0 + t + 0.05, tuer_y - 0.7, 2.3, "Rahmen")        # Zargen
            b.box(x0 - 0.05, tuer_y + 0.7, 0.07, x0 + t + 0.05, tuer_y + 0.8, 2.3, "Rahmen")
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
    """Grosser Hangar am Suedende westlich der Bahn, offen nach Osten; begehbar durch die Westtuer (von der Strasse) und das Osttor."""
    b = Bau("umgebung_hangar")
    x0, y0, x1, y1 = HANGAR
    halle(b, x0, y0, x1, y1, "O", HH, kisten=True, tuer_y=HY)
    for dx in (-3.0, 3.0):
        B.fenster(b, HX + dx, y1, 3.0, 1.6, 1.1, 0, 1)
        B.fenster(b, HX + dx, y0, 3.0, 1.6, 1.1, 0, -1)
    for dy in (-9.5, -3.5, 3.5, 9.5):
        B.fenster(b, x0, HY + dy, 3.0, 1.6, 1.1, -1, 0)
    return b


def _quad_orient(b, verts, richtung, mat):
    """Fuegt ein Vieleck so ein, dass seine Normale in 'richtung' zeigt (Newell-Verfahren)."""
    nx = ny = nz = 0.0
    for k in range(len(verts)):
        a, c = verts[k], verts[(k + 1) % len(verts)]
        nx += (a[1] - c[1]) * (a[2] + c[2])
        ny += (a[2] - c[2]) * (a[0] + c[0])
        nz += (a[0] - c[0]) * (a[1] + c[1])
    if nx * richtung[0] + ny * richtung[1] + nz * richtung[2] < 0:
        verts = verts[::-1]
    b.add(verts, [tuple(range(len(verts)))], mat)


def _profil(ycs, r, n):
    """Querschnitt (y, z) der Hallenreihe von links nach rechts: Halbkreise vom Radius r um die Achsen ycs; wo benachbarte
    Kreise sich schneiden, geht der eine Bogen in den naechsten ueber (Kehle), nur die aeusseren Enden laufen bis zum Boden."""
    s = ycs[1] - ycs[0] if len(ycs) > 1 else 0.0
    ak = math.acos(s / (2.0 * r)) if s > 0 else 0.0
    pts = []
    for i, yc in enumerate(ycs):
        tl = math.pi if i == 0 else math.pi - ak
        tr = 0.0 if i == len(ycs) - 1 else ak
        for k in range(n + 1):
            if i > 0 and k == 0:
                continue                                                  # Schnittpunkt gehoert schon zum vorigen Bogen
            th = tl + (tr - tl) * k / n
            pts.append((yc + r * math.cos(th), max(0.0, round(r * math.sin(th), 9))))
    return pts


def tonnenreihe(b, x0, x1, ycs, R, dicke=0.4, n=12, mat="Hangar Dach", mat_boden="Hangar Boden"):
    """Reihe runder Hangars (Tonnengewoelbe) ohne Zwischenraum: eine zusammenhaengende Halle mit gewelltem Dach.
    Achse in x-Richtung, Westseite (x0) komplett offen, im Osten (x1) schliesst eine Rueckwand ab."""
    t = dicke
    ao, ai = _profil(ycs, R, n), _profil(ycs, R - t, n)
    b.box(x0, ao[0][0], -0.12, x1, ao[-1][0], 0.07, mat_boden)                  # Boden
    for k in range(len(ao) - 1):
        (y0, z0), (y1, z1) = ao[k], ao[k + 1]
        (iy0, iz0), (iy1, iz1) = ai[k], ai[k + 1]
        _quad_orient(b, [(x0, y0, z0), (x1, y0, z0), (x1, y1, z1), (x0, y1, z1)], (0.0, -(z1 - z0), y1 - y0), mat)                 # aussen
        _quad_orient(b, [(x0, iy0, iz0), (x1 - t, iy0, iz0), (x1 - t, iy1, iz1), (x0, iy1, iz1)], (0.0, iz1 - iz0, -(iy1 - iy0)), mat)  # innen
        _quad_orient(b, [(x0, y0, z0), (x0, y1, z1), (x0, iy1, iz1), (x0, iy0, iz0)], (-1.0, 0.0, 0.0), mat)                       # Stirnkante offen
    for xx, prof, d in ((x1, ao, (1.0, 0.0, 0.0)), (x1 - t, ai, (-1.0, 0.0, 0.0))):                                                  # Rueckwand
        for k in range(len(prof) - 1):
            (y0, z0), (y1, z1) = prof[k], prof[k + 1]
            pts = [(xx, y0, 0.0), (xx, y1, 0.0), (xx, y1, z1), (xx, y0, z0)]
            pts = [p for i, p in enumerate(pts) if i == 0 or max(abs(p[j] - pts[i - 1][j]) for j in range(3)) > 1e-9]
            if len(pts) > 2 and max(abs(pts[0][j] - pts[-1][j]) for j in range(3)) < 1e-9:
                pts = pts[:-1]
            if len(pts) >= 3:
                _quad_orient(b, pts, d, mat)
    for xr in (x0 + 0.3, x0 + (x1 - x0) / 2, x1 - t - 0.2):                      # Dachrippen innen (sichtbare Bogenbinder)
        for k in range(len(ai) - 1):
            a = (xr, ai[k][0], max(0.0, ai[k][1] - 0.15))
            c = (xr, ai[k + 1][0], max(0.0, ai[k + 1][1] - 0.15))
            b.beam(a, c, 0.25, 0.25, "Metall", up=(1.0, 0.0, 0.0))


def hangarreihe():
    """Drei runde Hangars nebeneinander (getrennt, Daecher beruehren sich am Boden) zwischen Vorfeld und Bergen, nach Westen (zur Burg) ganz offen."""
    b = Bau("umgebung_hangarreihe")
    x0, x1 = REIHE_X0, REIHE_X0 + REIHE_T
    for yc in REIHE_YC:                                                           # jede Halle mit eigenem Rundbogen
        tonnenreihe(b, x0, x1, [yc], REIHE_R, n=16)
    for i, yc in enumerate(REIHE_YC):
        if i != 1:                                                                # Kisten in zwei der Hallen
            b.box(x1 - 4.4, yc - 3.0, 0.07, x1 - 2.0, yc - 0.6, 1.3, "Kiste")
            b.box(x1 - 4.4, yc - 3.0, 1.3, x1 - 3.2, yc - 1.8, 2.6, "Kiste")
    return b



# ------------------------------------------------------------------ Tower
def _lauf(b, d, x, y, n, w, base, sh, sd, panel_bis=None):
    """Treppenlauf der Feuerwehrtreppe im Tower: n Trittbleche (0,1 m dick) ab Hoehe base, Stufenhoehe sh, Tiefe sd, Breite w.
    (x, y) = Ecke der untersten Stufe, d = Steigrichtung. Auf der Schachtseite (zur Mitte) steht eine Blechbruestung, die mit den
    Stufen mitwaechst (1,0 m ueber der Stufe oder bis panel_bis) - so kann man nicht in den Schacht fallen."""
    rects = []
    for i in range(n):
        top = base + (i + 1) * sh
        if d == "N":
            r = (x, y + i * sd, x + w, y + (i + 1) * sd)
            p = (x - 0.1, r[1], x, r[3])
        elif d == "S":
            r = (x, y - (i + 1) * sd, x + w, y - i * sd)
            p = (x + w, r[1], x + w + 0.1, r[3])
        elif d == "E":
            r = (x + i * sd, y, x + (i + 1) * sd, y + w)
            p = (r[0], y + w, r[2], y + w + 0.1)
        else:
            r = (x - (i + 1) * sd, y, x - i * sd, y + w)
            p = (r[0], y - 0.1, r[2], y)
        b.box(r[0], r[1], top - 0.1, r[2], r[3], top, "Tower Stufen")                      # Trittblech
        b.box(p[0], p[1], top - 0.1, p[2], p[3], panel_bis if panel_bis else top + 1.0, "Tower Stufen")   # Bruestung
        rects.append((r, top))
    (r0, t0), (r1, t1) = rects[0], rects[-1]
    c0 = ((r0[0] + r0[2]) / 2, (r0[1] + r0[3]) / 2)
    c1 = ((r1[0] + r1[2]) / 2, (r1[1] + r1[3]) / 2)
    for off in (0.1, w - 0.1):                                                              # zwei Wangen unter den Seitenkanten
        if d in "NS":
            a, e = (x + off, c0[1], t0 - 0.16), (x + off, c1[1], t1 - 0.16)
        else:
            a, e = (c0[0], y + off, t0 - 0.16), (c1[0], y + off, t1 - 0.16)
        b.beam(a, e, 0.1, 0.22, "Tower Stufen")


def _wand_x(b, xa, xb, y0, y1, z0, z1, mat, tuer_x=None, tuer_b=1.4, tuer_h=2.3):
    """Wand entlang x (Dicke y0..y1) mit optionalem Tuerloch bei tuer_x (Mitte)."""
    if tuer_x is None:
        b.box(xa, y0, z0, xb, y1, z1, mat)
        return
    b.box(xa, y0, z0, tuer_x - tuer_b / 2, y1, z1, mat)
    b.box(tuer_x + tuer_b / 2, y0, z0, xb, y1, z1, mat)
    b.box(tuer_x - tuer_b / 2, y0, z0 + tuer_h, tuer_x + tuer_b / 2, y1, z1, mat)


def _wand_y(b, ya, yb, x0, x1, z0, z1, mat, tuer_y=None, tuer_b=1.4, tuer_h=2.3):
    """Wand entlang y (Dicke x0..x1) mit optionalem Tuerloch bei tuer_y (Mitte)."""
    if tuer_y is None:
        b.box(x0, ya, z0, x1, yb, z1, mat)
        return
    b.box(x0, ya, z0, x1, tuer_y - tuer_b / 2, z1, mat)
    b.box(x0, tuer_y + tuer_b / 2, z0, x1, yb, z1, mat)
    b.box(x0, tuer_y - tuer_b / 2, z0 + tuer_h, x1, tuer_y + tuer_b / 2, z1, mat)


def tower():
    """Begehbarer Tower: Sockelgebaeude (Tuer im Sueden) mit dem Treppenschacht; darin eine offene Feuerwehrtreppe (rechteckige
    Spirale um den freien Schacht, 6 Laeufe zu je 4 Stufen und je ein Eckpodest) bis in die Kanzel; Kanzel mit Tuer zur
    Rundumplattform (1,5 m breit, Gelaender)."""
    b = Bau("umgebung_tower")
    t = 0.4
    ax0, ay0, ax1, ay1 = TOWER_ANNEX
    sx0, sx1, sy0, sy1 = TX - 3.0, TX + 3.0, SCY - 3.0, SCY + 3.0                    # Schacht aussen (6 x 6)
    ix0, ix1, iy0, iy1 = sx0 + t, sx1 - t, sy0 + t, sy1 - t                          # Schacht innen (5,2 x 5,2)
    # ---- Sockelgebaeude: Boden, Waende (Tuer im Sueden bei x = TX), Flachdach mit Schachtloch
    b.box(ax0, ay0, -0.12, ax1, ay1, Z_BODEN, "Tower Beton")
    _wand_x(b, ax0, ax1, ay0, ay0 + t, Z_BODEN, 3.4, "Tower Beton", tuer_x=TX)
    _wand_x(b, ax0, ax1, ay1 - t, ay1, Z_BODEN, 3.4, "Tower Beton")
    b.box(ax0, ay0 + t, Z_BODEN, ax0 + t, ay1 - t, 3.4, "Tower Beton")
    b.box(ax1 - t, ay0 + t, Z_BODEN, ax1, ay1 - t, 3.4, "Tower Beton")
    b.box(TX - 0.8, ay0 - 0.05, 2.3, TX + 0.8, ay0 + t + 0.05, 2.4, "Rahmen")                    # Tuerrahmen
    b.box(TX - 0.8, ay0 - 0.05, Z_BODEN, TX - 0.7, ay0 + t + 0.05, 2.3, "Rahmen")
    b.box(TX + 0.7, ay0 - 0.05, Z_BODEN, TX + 0.8, ay0 + t + 0.05, 2.3, "Rahmen")
    ox0, oy0, ox1, oy1 = ax0 - 0.2, ay0 - 0.2, ax1 + 0.2, ay1 + 0.2                          # Dach mit 0,2 m Rand
    b.box(ox0, oy0, 3.4, ox1, sy0, 3.7, "Tower Dach")                                         # Dach um den Schacht herum
    b.box(ox0, sy1, 3.4, ox1, oy1, 3.7, "Tower Dach")
    b.box(ox0, sy0, 3.4, sx0, sy1, 3.7, "Tower Dach")
    b.box(sx1, sy0, 3.4, ox1, sy1, 3.7, "Tower Dach")
    # ---- Schacht: Waende bis unter den Kanzelboden, Tuer im Sueden (x = TX - 0.6, 1,2 m breit)
    _wand_x(b, sx0, sx1, sy0, sy0 + t, Z_BODEN, 13.0, "Tower Beton", tuer_x=TX - 0.6, tuer_b=1.2)
    _wand_x(b, sx0, sx1, sy1 - t, sy1, Z_BODEN, 13.0, "Tower Beton")
    b.box(sx0, sy0 + t, Z_BODEN, sx0 + t, sy1 - t, 13.0, "Tower Beton")
    b.box(sx1 - t, sy0 + t, Z_BODEN, sx1, sy1 - t, 13.0, "Tower Beton")
    for zz in (6.5, 9.5):                                                                    # Fensterschlitze am Schaft
        for sx in (-1, 1):
            b.box(TX + sx * 3.0, SCY - 0.6, zz, TX + sx * 3.05, SCY + 0.6, zz + 0.7, "Fenster")
        for sy in (-1, 1):
            b.box(TX - 0.6, SCY + sy * 3.0, zz, TX + 0.6, SCY + sy * 3.05, zz + 0.7, "Fenster")
    # ---- Feuerwehrtreppe: gegen den Uhrzeigersinn, Start im Suedostzipfel am Boden
    stu = (Z_KAB - Z_BODEN) / 30.0
    laeufe = [("N", ix1 - 1.0, iy0 + 1.0), ("W", ix1 - 1.0, iy1 - 1.0), ("S", ix0, iy1 - 1.0), ("E", ix0 + 1.0, iy0)]
    podeste = [(ix1 - 1.0, iy1 - 1.0), (ix0, iy1 - 1.0), (ix0, iy0), (ix1 - 1.0, iy0)]      # NO, NW, SW, SO (Ecke unten links)
    z = Z_BODEN
    hoechstes = {}
    for k in range(6):
        d, x, y = laeufe[k % 4]
        _lauf(b, d, x, y, 4, 1.0, z, stu, 0.8, panel_bis=13.0 if k == 5 else None)
        z += 5 * stu
        px, py = podeste[k % 4]
        b.box(px, py, z - 0.1, px + 1.0, py + 1.0, z, "Tower Stufen")                      # Eckpodest
        hoechstes[k % 4] = z
    for j, (px, py) in enumerate(podeste):                                                  # eine Saeule je Ecke bis zum hoechsten Podest
        cx = px + 0.9 if px > TX else px + 0.1
        cy = py + 0.9 if py > SCY else py + 0.1
        b.prism(cx, cy, Z_BODEN, 0.13, hoechstes[j] - 0.1 - Z_BODEN, 8, "Tower Stufen")
    # ---- Kanzel (7 x 7 m) auf Plattform (10 x 10 m): Boden mit Treppenloch ueber dem Nordlauf
    px0, py0, px1, py1 = TX - 5.0, SCY - 5.0, TX + 5.0, SCY + 5.0
    h0, h1 = iy1 - 1.0, iy1                                                                 # Loch: y-Streifen ueber dem letzten Lauf
    b.box(px0, py0, 13.0, px1, h0, Z_KAB, "Tower Dach")
    b.box(px0, h1, 13.0, px1, py1, Z_KAB, "Tower Dach")
    b.box(px0, h0, 13.0, ix0, h1, Z_KAB, "Tower Dach")
    b.box(ix1, h0, 13.0, px1, h1, Z_KAB, "Tower Dach")
    for sgn in (-1, 1):                                                                      # Stuetzstreben unter der Plattform
        b.beam((TX + sgn * 3.0, SCY, 10.8), (TX + sgn * 4.7, SCY, 12.95), 0.2, 0.2, "Metall")
        b.beam((TX, SCY + sgn * 3.0, 10.8), (TX, SCY + sgn * 4.7, 12.95), 0.2, 0.2, "Metall")
    kx0, kx1, ky0, ky1 = TX - 3.5, TX + 3.5, SCY - 3.5, SCY + 3.5
    kt = 0.3
    for mat, z0, z1 in (("Tower Beton", Z_KAB, 14.2), ("Glas", 14.2, 15.2)):                # Bruestung, Glasband; Tuer im Westen
        b.box(kx0, ky0, z0, kx1, ky0 + kt, z1, mat)
        b.box(kx0, ky1 - kt, z0, kx1, ky1, z1, mat)
        b.box(kx1 - kt, ky0 + kt, z0, kx1, ky1 - kt, z1, mat)
        b.box(kx0, ky0 + kt, z0, kx0 + kt, SCY - 0.6, z1, mat)
        b.box(kx0, SCY + 0.6, z0, kx0 + kt, ky1 - kt, z1, mat)
    for sx in (-1, 1):                                                                       # Eckpfosten
        for sy in (-1, 1):
            b.box(TX + sx * 3.5 - 0.15, SCY + sy * 3.5 - 0.15, Z_KAB, TX + sx * 3.5 + 0.15, SCY + sy * 3.5 + 0.15, 15.2, "Tower Beton")
    b.box(kx1 - 0.9, SCY - 1.5, Z_KAB, kx1 - kt, SCY + 1.5, 14.3, "Metall")                 # Lotsenpult an der Ostwand
    b.box(kx0 - 0.5, ky0 - 0.5, 15.2, kx1 + 0.5, ky1 + 0.5, 15.6, "Tower Dach")             # Kanzeldach
    b.box(TX - 0.5, SCY - 0.5, 15.6, TX + 0.5, SCY + 0.5, 16.2, "Tower Beton")              # Sockel der Radaranlage
    b.box(TX - 0.12, SCY - 0.12, 16.2, TX + 0.12, SCY + 0.12, RADAR_Z, "Metall")             # Stuetze (dreht nicht)
    b.box(TX + 1.6, SCY + 1.6, 15.6, TX + 2.4, SCY + 2.4, 16.4, "Metall")                   # Geraetekasten
    # ---- Gelaender der Rundumplattform: Fussleiste, Mittel- und Handlauf, Pfosten alle ~1,6 m
    g = 4.85
    for sgn in (-1, 1):
        for (a0, a1, a2, a3) in ((TX - g, SCY + sgn * g - 0.04, TX + g, SCY + sgn * g + 0.04),
                                 (TX + sgn * g - 0.04, SCY - g, TX + sgn * g + 0.04, SCY + g)):
            for (zr0, zr1) in ((Z_KAB, 13.45), (13.8, 13.88), (14.32, 14.4)):
                b.box(a0, a1, zr0, a2, a3, zr1, "Metall")
    for i in range(7):
        o = -g + i * (2 * g / 6.0)
        for sgn in (-1, 1):
            b.box(TX + o - 0.05, SCY + sgn * g - 0.05, Z_KAB, TX + o + 0.05, SCY + sgn * g + 0.05, 14.4, "Metall")
            b.box(TX + sgn * g - 0.05, SCY + o - 0.05, Z_KAB, TX + sgn * g + 0.05, SCY + o + 0.05, 14.4, "Metall")
    # ---- Gelaender um das Treppenloch im Kanzelboden (offen nur am obersten Podest, wo man aus der Treppe in die Kanzel tritt)
    for (a0, a1, a2, a3) in ((ix0 + 1.0, h0 - 0.1, ix1 + 0.1, h0), (ix0 + 1.0, h1, ix1 + 0.1, h1 + 0.1), (ix1, h0, ix1 + 0.1, h1)):
        for (zr0, zr1) in ((Z_KAB, 13.45), (13.8, 13.88), (14.32, 14.4)):
            b.box(a0, a1, zr0, a2, a3, zr1, "Metall")
    # ---- fenster am Sockelgebaeude
    for dx in (-3.2, 3.2):
        B.fenster(b, TX + dx, ay0, 1.9, 1.5, 1.0, 0, -1)
    for dx in (-3.2, 0.0, 3.2):
        B.fenster(b, TX + dx, ay1, 1.9, 1.5, 1.0, 0, 1)
    for dy in (-2.4, 2.4):
        B.fenster(b, ax1, TY + dy, 1.9, 1.5, 1.0, 1, 0)
        B.fenster(b, ax0, TY + dy, 1.9, 1.5, 1.0, -1, 0)
    return b


# ------------------------------------------------------------------ Zaun, Tore, Checkpoint
def zaunstrecke(b, achse, fest, t0, t1, luecken=(), abstand=3.0):
    """Zaun entlang einer Achse ('x': y = fest, von x = t0 bis t1; 'y': x = fest); in den 'luecken' (a, c) steht kein Zaun.
    Pfosten (0,12 m) alle <= 3 m, zwei Querholme; an den Luecken ein Endpfosten."""
    spans = [(t0, t1)]
    for (a, c) in sorted(luecken):
        neu = []
        for s0, s1 in spans:
            if c <= s0 or a >= s1:
                neu.append((s0, s1))
                continue
            if a > s0:
                neu.append((s0, a))
            if c < s1:
                neu.append((c, s1))
        spans = neu
    for s0, s1 in spans:
        n = max(1, int(math.ceil((s1 - s0) / abstand)))
        for i in range(n + 1):
            p = s0 + (s1 - s0) * i / n
            if achse == "x":
                b.box(p - 0.06, fest - 0.06, 0.0, p + 0.06, fest + 0.06, 2.0, "Metall")
            else:
                b.box(fest - 0.06, p - 0.06, 0.0, fest + 0.06, p + 0.06, 2.0, "Metall")
        for (zr0, zr1) in ((0.3, 0.36), (1.0, 1.06), (1.9, 1.96)):
            if achse == "x":
                b.box(s0, fest - 0.03, zr0, s1, fest + 0.03, zr1, "Metall")
            else:
                b.box(fest - 0.03, s0, zr0, fest + 0.03, s1, zr1, "Metall")


def schranke(b, px, py, hx, hy, laenge, winkel=80.0):
    """Offene Schranke: Pfosten bei (px, py), der Baum (rot-weiss, Laenge 'laenge') steht um 'winkel' Grad aufgerichtet und neigt
    sich in Richtung (hx, hy) ueber die Fahrbahn; am anderen Ende ein Auflager."""
    n = math.hypot(hx, hy)
    hx, hy = hx / n, hy / n
    b.box(px - 0.2, py - 0.2, 0.0, px + 0.2, py + 0.2, 1.1, "Metall")
    b.box(px + hx * laenge - 0.1, py + hy * laenge - 0.1, 0.0, px + hx * laenge + 0.1, py + hy * laenge + 0.1, 1.0, "Metall")
    w = math.radians(winkel)
    z0 = 1.05
    for k in range(6):
        a0, a1 = laenge * k / 6.0, laenge * (k + 1) / 6.0
        pa = (px + hx * a0 * math.cos(w), py + hy * a0 * math.cos(w), z0 + a0 * math.sin(w))
        pb = (px + hx * a1 * math.cos(w), py + hy * a1 * math.cos(w), z0 + a1 * math.sin(w))
        b.beam(pa, pb, 0.14, 0.14, "Schranke rot" if k % 2 == 0 else "Schranke weiss")


def zaun():
    """Zaun um das Flugplatzgelaende mit Haupteingang (Checkpoint) am Zubringer und je einem Tor an den beiden Ring-Abzweigen."""
    b = Bau("umgebung_zaun")
    x0, y0, x1, y1 = ZAUN
    yz = (C - 4.8, C + 4.8)                                                                  # Haupteingang (Zubringer, Fahrbahn 146..154)
    yb = []                                                                                  # Abzweige kreuzen den Zaun hier (45 Grad)
    for s in (-1, 1):
        a0, _ = abzweig(s)
        yb.append(a0[1] + s * (GATE_X - a0[0]))
    lw = BREITE_WEG / math.sqrt(0.5) / 2.0 + 0.9                                             # halbe Torbreite entlang des Zauns
    luecken = [yz] + [(y - lw, y + lw) for y in yb]
    zaunstrecke(b, "y", x0, y0, y1, luecken)                                                 # Westzaun mit den drei Toren
    zaunstrecke(b, "x", y0, x0, x1)                                                          # Suedzaun
    zaunstrecke(b, "x", y1, x0, x1)                                                          # Nordzaun
    zaunstrecke(b, "y", x1, y0, y1)                                                          # Ostzaun (an den Bergen)
    # ---- Checkpoint am Zubringer: Mittelinsel mit Wachhaus, Vordach ueber beide Fahrstreifen, je Richtung eine Schranke
    gx = GATE_X
    b.box(gx - 2.4, C - 1.3, 0.0, gx + 2.4, C + 1.3, 0.15, "Insel")
    b.box(gx - 1.6, C - 1.1, 0.15, gx + 1.6, C + 1.1, 2.7, "Tower Beton")                    # Wachhaus 3,2 x 2,2 m
    for sy in (-1, 1):
        B.fenster(b, gx, C + sy * 1.1, 1.7, 2.0, 1.0, 0, sy)
    for sx in (-1, 1):
        B.fenster(b, gx + sx * 1.6, C, 1.7, 1.2, 1.0, sx, 0)
    b.box(gx - 2.6, C - 4.8, 3.6, gx + 2.6, C + 4.8, 3.9, "Tower Dach")                     # Vordach
    b.box(gx - 1.6, C - 1.1, 2.7, gx + 1.6, C + 1.1, 3.6, "Tower Beton")                    # Aufsatz zwischen Haus und Dach
    for sy in (-1, 1):
        b.box(gx - 0.15, C + sy * 4.55 - 0.15, 0.0, gx + 0.15, C + sy * 4.55 + 0.15, 3.6, "Tower Beton")      # Stuetzen am Fahrbahnrand
    # Einfahrt (nach Osten): Fahrstreifen y 146..148,7; Schranke vor dem Dach, Baum neigt sich zum Fahrbahnrand
    schranke(b, gx - 3.4, C - 1.5, 0.0, -1.0, 2.9)
    # Ausfahrt (nach Westen): Fahrstreifen y 151,3..154; Schranke hinter dem Dach
    schranke(b, gx + 3.4, C + 1.5, 0.0, 1.0, 2.9)
    # ---- Tore an den beiden Abzweigen: zwei Schrankenbaeume von beiden Fahrbahnraendern
    for s, y in zip((-1, 1), yb):
        u = (math.sqrt(0.5), s * math.sqrt(0.5))
        v = (-u[1], u[0])                                                                    # quer zur Fahrbahn
        for sg in (-1, 1):
            schranke(b, gx + sg * v[0] * 4.5, y + sg * v[1] * 4.5, -sg * v[0], -sg * v[1], 4.0)
    return b


def tankstelle():
    """Asphaltierte Flugzeug-Tankstelle suedlich der Hangarreihe (auf der dem Tower abgewandten Seite), an Vorfeld und Rollweg.

    Ohne Dach: Abstellposition (14 x 14 m, Platz fuer ein Kleinflugzeug mit ~11 m Spannweite) mit gelber Zufahrtslinie, Haltebalken
    und Verzurrringen; die Zapfsaeulen stehen auf Inseln am Rand der Position (Schlauchlaenge reicht zum Tank, die Fluegel bleiben frei).
    Dazu Shop, zwei stehende Tanks und ein Preisschild neben der Zufahrt."""
    b = Bau("umgebung_tankstelle")
    x0, y0, x1, y1 = TANK
    b.box(x0, y0, -0.12, x1, y1, Z_VORFELD, "Vorfeld")
    # Zapfinseln mit je einer Saeule (Avgas / Jet A1) suedlich der Abstellposition
    for xx in (TANK_POS[0] - 2.5, TANK_POS[0] + 2.5):
        b.box(xx - 0.7, TANK_POS[1] - 8.0, Z_VORFELD, xx + 0.7, TANK_POS[1] - 6.9, Z_VORFELD + 0.2, "Insel")
        b.box(xx - 0.35, TANK_POS[1] - 7.75, Z_VORFELD + 0.2, xx + 0.35, TANK_POS[1] - 7.25, 1.8, "Zapfsaeule")
        b.box(xx - 0.25, TANK_POS[1] - 7.2, 0.9, xx + 0.25, TANK_POS[1] - 7.1, 1.3, "Metall")             # Schlauchhalter
    # Verzurrringe unter den Tragflaechen (flache Ringe im Boden) und Haltebalken am Bugradpunkt
    for dx in (-3.0, 3.0):
        for dy in (-4.5, 4.5):
            b.box(TANK_POS[0] + dx - 0.15, TANK_POS[1] + dy - 0.15, Z_VORFELD, TANK_POS[0] + dx + 0.15, TANK_POS[1] + dy + 0.15, Z_VORFELD + 0.06, "Metall")
    # Shop (Flachdach, Tuer zur Zapfseite)
    sx0, sy0, sx1, sy1 = 281.0, 91.0, 291.0, 97.0
    b.box(sx0, sy0, Z_VORFELD, sx1, sy1, 3.4, "Tower Beton")
    b.box(sx0 - 0.3, sy0 - 0.3, 3.4, sx1 + 0.3, sy1 + 0.3, 3.7, "Tower Dach")
    b.box(286.0 - 0.6, sy1, Z_VORFELD, 286.0 + 0.6, sy1 + 0.06, 2.2, "Tuer")
    for dx in (-3.0, 3.0):
        B.fenster(b, 286.0 + dx, sy1, 1.6, 1.8, 1.2, 0, 1)
        B.fenster(b, 286.0 + dx, sy0, 1.6, 1.8, 1.2, 0, -1)
    # Tanks (stehend) und Preisschild (am Rand, ausserhalb der Flaechen der Tragflaechen)
    for yy in (92.0, 97.5):
        b.prism(294.3, yy, Z_VORFELD, 1.8, 4.2, 12, "Tank")
    b.box(280.5 - 0.1, 89.6 - 0.1, Z_VORFELD, 280.5 + 0.1, 89.6 + 0.1, 6.0, "Metall")
    b.box(280.5 - 1.0, 89.6 - 0.15, 5.0, 280.5 + 1.0, 89.6 + 0.15, 6.4, "Rahmen")
    # gelbe Zufahrtslinie (Bogen vom Rollweg) in die Position und Haltebalken; Position als weisses Rechteck
    px, py = TANK_POS
    for (a0, a1, sg) in ((180.0, 270.0, 1), (90.0, 180.0, -1)):
        gelb_bogen(b, TAXI_X + RC_GELB, py + sg * RC_GELB, RC_GELB, a0, a1)
    gelbe_linie_x(b, TAXI_X + RC_GELB, px + 4.0, py)
    b.box(px + 4.0, py - 1.8, Z_GELB0, px + 4.4, py + 1.8, Z_GELB1, "Markierung gelb")
    m = "Markierung weiss"
    for (xa, ya, xb, yb) in ((px - 6.8, py - 6.8, px + 6.8, py - 6.6), (px - 6.8, py + 6.6, px + 6.8, py + 6.8),
                             (px - 6.8, py - 6.8, px - 6.6, py + 6.8), (px + 6.6, py - 6.8, px + 6.8, py + 6.8)):
        b.box(xa, ya, Z_GELB0, xb, yb, Z_GELB1, m)
    return b


def helipad():
    """Helipad auf der Gruenflaeche nordlich des Towers: runde Betonflaeche mit Ring und H, Zufahrtsweg zur Flughafenstrasse."""
    b = Bau("umgebung_helipad")
    hx, hy, hr = HELI
    b.prism(hx, hy, 0.0, hr, 0.09, 24, "Vorfeld")
    n = 48
    ri, ra = hr - 1.6, hr - 1.1
    v, f = [], []
    for i in range(n):
        a = 2 * math.pi * i / n
        v += [(hx + ri * math.cos(a), hy + ri * math.sin(a), 0.11), (hx + ra * math.cos(a), hy + ra * math.sin(a), 0.11)]
        j = (i + 1) % n
        f.append((2 * i, 2 * i + 1, 2 * j + 1, 2 * j))
    b.add(v, f, "Markierung weiss")
    for sx in (-1, 1):                                                          # H: zwei Balken und Quersteg
        b.box(hx + sx * 1.8 - 0.4, hy - 2.6, 0.09, hx + sx * 1.8 + 0.4, hy + 2.6, 0.11, "Markierung weiss")
    b.box(hx - 1.4, hy - 0.4, 0.09, hx + 1.4, hy + 0.4, 0.11, "Markierung weiss")
    streifen(b, (SX + BREITE_WEG / 2 - 1.0, hy), (hx - hr + 0.5, hy), 5.0, Z_WEG, "Weg")
    return b


def windsaecke():
    """Je ein Windsack an beiden Enden der Landebahn (westlich neben der Bahn, ausserhalb der Rollwege): Mast, Auslegerring, Sack."""
    b = Bau("umgebung_windsaecke")
    for yy in (BAHN[1] - 2.5, BAHN[3] + 2.5):
        x = BAHN[0] - 2.5
        b.box(x - 0.4, yy - 0.4, 0.0, x + 0.4, yy + 0.4, 0.3, "Insel")
        b.prism(x, yy, 0.3, 0.12, 6.2, 8, "Metall")
        ringe = [(0.62, 0.62), (0.55, 0.50), (0.46, 0.38), (0.36, 0.30), (0.26, 0.24)]      # (Radius vorn, hinten) je Segment
        x0 = x + 0.3
        b.beam((x, yy, 6.5), (x0, yy, 6.5), 0.1, 0.1, "Metall")
        for k, (r0, r1) in enumerate(ringe):
            xa, xb = x0 + 0.75 * k, x0 + 0.75 * (k + 1)
            mat = "Windsack orange" if k % 2 == 0 else "Markierung weiss"
            n = 8
            for i in range(n):
                a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
                am = (a0 + a1) / 2
                _quad_orient(b, [(xa, yy + r0 * math.cos(a0), 6.5 + r0 * math.sin(a0)), (xb, yy + r1 * math.cos(a0), 6.5 + r1 * math.sin(a0)),
                                 (xb, yy + r1 * math.cos(a1), 6.5 + r1 * math.sin(a1)), (xa, yy + r0 * math.cos(a1), 6.5 + r0 * math.sin(a1))],
                             (0.0, math.cos(am), math.sin(am)), mat)
    return b


def radar_tower():
    """Drehende Radaranlage auf dem Kanzeldach des Towers (Ortskoordinaten um den Drehpunkt; Antenne blickt nach +y)."""
    g = Bau("tower_radar")
    g.prism(0.0, 0.0, 0.0, 0.25, 0.5, 8, "Metall")                                  # Drehkranz
    g.box(-0.9, -0.12, 0.5, 0.9, 0.12, 0.7, "Metall")                              # Ausleger/Tragbalken
    W, Hh = 4.4, 1.3                                                                # Reflektor: Gitterrahmen mit Querstreben
    for sx in (-1, 1):
        g.box(sx * W / 2 - 0.05, 0.35, 0.7, sx * W / 2 + 0.05, 0.45, 0.7 + Hh + 0.1, "Rahmen")
    for zz in (0.7, 0.7 + Hh + 0.05):
        g.box(-W / 2, 0.35, zz, W / 2, 0.45, zz + 0.05, "Rahmen")
    for k in range(1, 5):
        g.box(-W / 2, 0.37, 0.7 + Hh * k / 5, W / 2, 0.43, 0.7 + Hh * k / 5 + 0.04, "Rahmen")
    for k in range(1, 10):
        g.box(-W / 2 + W * k / 10 - 0.02, 0.37, 0.7, -W / 2 + W * k / 10 + 0.02, 0.43, 0.7 + Hh + 0.05, "Rahmen")
    for sx in (-1, 1):
        g.beam((sx * 0.6, 0.0, 0.6), (sx * W / 2 - 0.02, 0.38, 0.7 + Hh * 0.5), 0.07, 0.07, "Metall")
    g.box(-0.15, 0.45, 0.7 + Hh + 0.05, 0.15, 0.95, 0.7 + Hh + 0.3, "Metall")      # Speisehorn oben
    return g


def drehteile():
    """Drehbare Teile als eigene Objekte: Liste (Name, Bau in Ortskoordinaten, Drehpunkt, Anfangsdrehung um z in Grad, Grad pro Bild)."""
    return [("tower_radar", radar_tower(), (TX, SCY, RADAR_Z), 0.0, 6.0)]


def baue_alles():
    """Gibt die Baugruppen zurueck (ohne bpy aufrufbar)."""
    return [wege(), landebahn(), hangar(), hangarreihe(), tower(), zaun(), windsaecke(), tankstelle(), helipad()]


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
    for name, g, (px, py, pz), rot, grad_je_bild in drehteile():                # drehbar: Objektursprung = Drehpunkt
        namen = []
        for mname in g.m:
            if mname not in namen:
                namen.append(mname)
        mats = [T.material(n, *FARBEN[n]) for n in namen]
        ob = T.add_mesh(coll, name, g.v, g.f, mats, [namen.index(mname) for mname in g.m])
        ob.location = (px, py, pz)
        ob.rotation_euler = (0.0, 0.0, math.radians(rot))
        try:                                                                     # Dauerdrehung ueber einen Treiber (kein Keyframe noetig)
            fc = ob.driver_add("rotation_euler", 2)
            fc.driver.type = 'SCRIPTED'
            fc.driver.expression = "%.6f + frame * %.6f" % (math.radians(rot), math.radians(grad_je_bild))
        except Exception:
            pass
        nf += len(g.f)
    return nf
