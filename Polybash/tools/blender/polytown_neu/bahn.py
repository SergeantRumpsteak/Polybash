"""Polybash - Eisenbahn: Gleisanlage vom Steinbruch (Suedwest) zum Bahnhof (ersetzt den suedlichen Kreisverkehr), Wagen, Signale.

Norden ist +y (die Richtung, in die man schaut, wenn man die Kirche betritt). Alle Koordinaten sind Weltkoordinaten in Metern.
Die Strecke laeuft von der Verladestelle im Steinbruch (Prellbock x = 63,2) geradeaus nach Osten ueber die Weiche bei x = 100 bis zum
Bahnhof (Gleis 1 am Hausbahnsteig, Gleis 2, Gleis 3 = durchgehendes Gueterbahngleis zum Gueterschuppen); Gleisende mit Prellboecken bei x = 184.
Wird von stadt.baue_alles() eingebunden."""
import math

import stadt as S
from stadt import Lok, pbox, wand, aussenwand, fensterschmuck, tuerrahmen, dach, F0, WD, TH
import oeffentlich as O
import talkessel as T
from burg import Bau

S.FARBEN.update({
    "Schiene":        ((0.33, 0.25, 0.20), 0.45, 0.5),
    "Schwelle":       ((0.20, 0.15, 0.11), 0.95, 0.0),
    "Schotterbett":   ((0.47, 0.45, 0.42), 1.0, 0.0),
    "Bahnsteig":      ((0.62, 0.60, 0.56), 0.95, 0.0),
    "Bahnsteigkante": ((0.86, 0.86, 0.80), 0.8, 0.0),
    "Wagen braun":    ((0.34, 0.19, 0.13), 0.9, 0.0),
    "Wagen grau":     ((0.38, 0.38, 0.36), 0.9, 0.0),
    "Rost":           ((0.42, 0.24, 0.15), 0.95, 0.2),
    "Wellblech":      ((0.46, 0.48, 0.47), 0.7, 0.3),
    "Wellblech alt":  ((0.40, 0.36, 0.31), 0.9, 0.2),
    "Signal rot":     ((0.60, 0.10, 0.08), 0.6, 0.0),
    "Signal weiss":   ((0.90, 0.90, 0.86), 0.6, 0.0),
    "Gelb Maschine":  ((0.78, 0.60, 0.12), 0.7, 0.1),
    "Kohle":          ((0.08, 0.08, 0.08), 1.0, 0.0),
    "Bruch Fels":        ((0.50, 0.46, 0.40), 0.95, 0.0),
    "Bruch Fels dunkel": ((0.36, 0.33, 0.30), 0.95, 0.0),
    "Bruch Fels hell":   ((0.64, 0.60, 0.52), 0.95, 0.0),
    "Bruch Erde":        ((0.42, 0.34, 0.24), 1.0, 0.0),
    "Schotter":          ((0.55, 0.52, 0.46), 1.0, 0.0),
    "Schotter dunkel":   ((0.46, 0.43, 0.38), 1.0, 0.0),
    "Bruch Beton":       ((0.55, 0.54, 0.50), 0.95, 0.0),
    "Wagen gruen":       ((0.14, 0.27, 0.17), 0.85, 0.0),
    "Sack":              ((0.62, 0.55, 0.40), 1.0, 0.0),
})

# ------------------------------------------------------------------ Lage der Anlage
GLEIS_Y = {1: 34.0, 2: 30.5, 3: 27.0}                 # Mittellinien der Gleise am Bahnhof / Steinbruch-Strecke
X_PRELL_W, X_PRELL_O = 63.2, 184.0                      # Gleisenden
SPUR = 1.435                                            # Spurweite
BAHNSTEIG = (132.0, 35.7, 168.0, 43.0)                  # Hausbahnsteig (Hoehe 0,28 m)
BST_H = 0.28
STATION = (150.0, 47.5)                                 # Mitte des Empfangsgebaeudes (24 x 9 m, Tuer nach Norden)
VORPLATZ = (134.0, 52.0, 166.0, 62.0)                   # Bahnhofsvorplatz, endet an der Suedstrasse
BALLAST_H = 0.18
UEBERGANG_X = 108.0                                     # Bahnuebergang der Gueterstrasse (Gleis 3 und Gleis 2)
BELEGT = ((184.0, 23.0, 300.0, 31.2),                     # Gleis 3 weiter zum Tunnel (Baeume freihalten)
          (130.0, 33.0, 188.0, 64.0),                   # Bahnhof: Bahnsteig, Empfangsgebaeude, Vorplatz, Wasserturm
          (60.0, 23.0, 190.0, 37.0),                    # Gleiskorridor Steinbruch -> Bahnhof
          (114.0, 13.0, 138.0, 26.5))                   # Gueterschuppen mit Rampe


# ------------------------------------------------------------------ kleine Bauteile
def scheibe_y(b, cx, cy, cz, r, dy, mat, n=10):
    """Liegende Scheibe (Rad) mit Achse in y-Richtung: Mitte (cx, cy, cz), Dicke dy."""
    ring = lambda y: [(cx + r * math.cos(2 * math.pi * k / n), y, cz + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    a, c = ring(cy - dy / 2), ring(cy + dy / 2)
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    b.add(a + c, faces, mat)


def kegel(b, cx, cy, z0, r, h, mat, n=8, rot=0.0):
    """Schuettkegel (Schotterhaufen): n-Eck-Pyramide."""
    ring = [(cx + r * math.cos(rot + 2 * math.pi * k / n), cy + r * math.sin(rot + 2 * math.pi * k / n), z0) for k in range(n)]
    verts = ring + [(cx, cy, z0 + h)]
    faces = [tuple(range(n - 1, -1, -1))] + [(k, (k + 1) % n, n) for k in range(n)]
    b.add(verts, faces, mat)


def gleis_gerade(b, y, x0, x1, ballast=True, sleeper_dx=0.7, bett_breite=3.4):
    """Gerades Gleis in x-Richtung bei y von x0 bis x1: Schotterbett, Schwellen (alle 0,7 m), zwei Schienen."""
    if ballast:
        b.box(x0, y - bett_breite / 2, 0.0, x1, y + bett_breite / 2, BALLAST_H, "Schotterbett")
    n = int((x1 - x0) / sleeper_dx)
    for i in range(n):
        xs = x0 + 0.35 + i * sleeper_dx
        b.box(xs - 0.13, y - 1.3, BALLAST_H, xs + 0.13, y + 1.3, BALLAST_H + 0.1, "Schwelle")
    for sg in (-1, 1):
        yy = y + sg * SPUR / 2
        b.box(x0, yy - 0.035, BALLAST_H + 0.1, x1, yy + 0.035, BALLAST_H + 0.24, "Schiene")


def gleis_kurve(b, pts, bett_breite=3.4):
    """Gleis entlang eines Linienzugs (Weichenstrasse, S-Kurve) aus schraegen Balken: Bett, Schwellen, Schienen."""
    for p, q in zip(pts, pts[1:]):
        dx, dy = q[0] - p[0], q[1] - p[1]
        ln = math.hypot(dx, dy)
        ux, uy = dx / ln, dy / ln
        nx, ny = -uy, ux
        b.beam((p[0], p[1], BALLAST_H / 2), (q[0], q[1], BALLAST_H / 2), bett_breite, BALLAST_H, "Schotterbett")
        k = int(ln / 0.7) + 1
        for i in range(k):
            cx, cy = p[0] + ux * (0.35 + i * 0.7), p[1] + uy * (0.35 + i * 0.7)
            if math.hypot(cx - p[0], cy - p[1]) > ln:
                break
            b.beam((cx - nx * 1.3, cy - ny * 1.3, BALLAST_H + 0.05), (cx + nx * 1.3, cy + ny * 1.3, BALLAST_H + 0.05), 0.26, 0.1, "Schwelle")
        for sg in (-1, 1):
            o = sg * SPUR / 2
            b.beam((p[0] + nx * o, p[1] + ny * o, BALLAST_H + 0.17), (q[0] + nx * o, q[1] + ny * o, BALLAST_H + 0.17), 0.07, 0.14, "Schiene")


def s_kurve(x0, y0, x1, y1, n=8):
    """Weicher Uebergang (S-Kurve) von (x0, y0) nach (x1, y1): Punkte mit Glaettung (smoothstep)."""
    out = []
    for i in range(n + 1):
        t = i / n
        s = t * t * (3 - 2 * t)
        out.append((x0 + (x1 - x0) * t, y0 + (y1 - y0) * s))
    return out


def prellbock(b, x, y, richtung=1):
    """Prellbock am Gleisende (x, y): Querbalken auf zwei Staendern mit Puffern; richtung = +1: das Gleis liegt im +x (Ende im Westen)."""
    for sg in (-1, 1):
        b.box(x - 0.2, y + sg * 0.75 - 0.15, 0.0, x + 0.2, y + sg * 0.75 + 0.15, 1.15, "Schwelle")
    b.box(x - 0.25, y - 1.25, 0.95, x + 0.25, y + 1.25, 1.15, "Signal rot")
    for sg in (-1, 1):
        b.box(x + richtung * 0.25, y + sg * 0.75 - 0.1, 0.85, x + richtung * 0.5, y + sg * 0.75 + 0.1, 1.0, "Schiene")


def formsignal(b, x, y, hoehe=5.0, ausrichtung=1):
    """Formsignal (Fluegelsignal): Gittermast, Arm auf 'Halt' (waagerecht, rot-weiss) und Laterne; steht neben dem Gleis bei (x, y)."""
    b.box(x - 0.08, y - 0.08, 0.0, x + 0.08, y + 0.08, hoehe, "Metall")
    b.box(x - 0.15, y - 0.15, 0.0, x + 0.15, y + 0.15, 0.35, "Schwelle")
    b.box(x - 0.03, y - 0.03 + ausrichtung * 0.0, hoehe - 0.9, x + 0.03, y + 0.03, hoehe - 0.3, "Metall")
    for k in range(4):                                           # Signalfluegel: rot-weisse Streifen quer zur Gleisachse
        y0 = y + ausrichtung * (0.1 + 0.28 * k)
        b.box(x - 0.04, min(y0, y0 + ausrichtung * 0.28), hoehe - 0.45, x + 0.04, max(y0, y0 + ausrichtung * 0.28), hoehe - 0.15,
              "Signal rot" if k % 2 == 0 else "Signal weiss")
    b.box(x - 0.2, y - 0.2, hoehe - 1.9, x + 0.2, y + 0.2, hoehe - 1.3, "Metall")           # Laterne
    b.box(x - 0.22, y - 0.05, hoehe - 1.75, x - 0.18, y + 0.05, hoehe - 1.45, "Signal rot")


def offener_wagen(b, x0, y, laenge=8.6, beladen=True, mat="Wagen braun", z0=BALLAST_H + 0.24):
    """Offener Gueterwagen (Muldenwagen) auf dem Gleis y, von x0 bis x0 + laenge: Untergestell, vier Raeder (Scheiben), Bordwaende, Puffer, Ladung."""
    x1 = x0 + laenge
    zr = 0.45                                                    # Radradius
    zb = z0 + 0.35
    b.box(x0, y - 1.15, zb, x1, y + 1.15, zb + 0.18, "Metall")                                 # Rahmen
    for sg in (-1, 1):
        for xx in (x0 + 1.4, x1 - 1.4):
            scheibe_y(b, xx, y + sg * 0.74, z0 + zr - 0.02, zr, 0.1, "Metall")
            b.box(xx - 0.25, y + sg * 0.74 - 0.1, zb - 0.28, xx + 0.25, y + sg * 0.74 + 0.1, zb, "Schwelle")   # Achslager
    for sg in (-1, 1):
        for yy in (y - 0.6, y + 0.6):
            b.box(x0 - 0.3, yy - 0.1, zb + 0.05, x0, yy + 0.1, zb + 0.2, "Metall")
            b.box(x1, yy - 0.1, zb + 0.05, x1 + 0.3, yy + 0.1, zb + 0.2, "Metall")
        break
    hw = 1.1
    b.box(x0, y - hw, zb + 0.18, x1, y - hw + 0.08, zb + 1.7, mat)                              # Seitenwaende
    b.box(x0, y + hw - 0.08, zb + 0.18, x1, y + hw, zb + 1.7, mat)
    b.box(x0, y - hw, zb + 0.18, x0 + 0.08, y + hw, zb + 1.7, mat)
    b.box(x1 - 0.08, y - hw, zb + 0.18, x1, y + hw, zb + 1.7, mat)
    for k in range(1, 5):                                                                       # Bretterfugen
        xx = x0 + laenge * k / 5.0
        for yy in (y - hw - 0.02, y + hw):
            b.box(xx - 0.05, yy, zb + 0.2, xx + 0.05, yy + 0.02, zb + 1.68, "Schwelle")
    b.box(x0 + 0.1, y - hw + 0.08, zb + 0.18, x1 - 0.1, y + hw - 0.08, zb + 0.28, "Rost")        # Boden
    if beladen:
        kegel(b, (x0 + x1) / 2, y, zb + 0.28, 1.0, 1.3, "Bruch Fels", n=8)
        kegel(b, x0 + laenge * 0.25, y, zb + 0.28, 0.85, 1.0, "Bruch Fels dunkel", n=7, rot=0.3)
        kegel(b, x0 + laenge * 0.75, y, zb + 0.28, 0.85, 1.0, "Bruch Fels hell", n=7, rot=0.6)
    b.box(x0 + 1.0, y - 0.05, zb - 0.1, x1 - 1.0, y + 0.05, zb, "Metall")


# ------------------------------------------------------------------ Empfangsgebaeude
def empfangsgebaeude(b, cx, cy, lvl=1):
    """Bahnhofsgebaeude (24 x 9 m, Tuer nach Norden zum Vorplatz, Bahnsteigseite nach Sueden): hohe Schalterhalle in der Mitte mit Giebel, Uhr und Schriftzug
    BAHNHOF, zwei niedrigere Fluegel (Wartesaal, Gepaeck/Vorsteher). Innen alles begehbar: Schalter, Baenke, Ofen, Fahrplan; Bahnsteigtueren auf der Suedseite."""
    g = Lok(b, cx, cy, 0.0, math.pi, 1)
    mat = "Putz gelb alt" if lvl else "Putz gelb"
    ziegel = "Ziegel dunkel alt" if lvl and "Ziegel dunkel alt" in S.FARBEN else "Ziegel dunkel"
    hd = 4.5
    HM, HF = F0 + 5.6, F0 + 4.0                                       # Traufhoehen Mittelbau / Fluegel
    # ---- Mittelbau (x -6..6)
    oef_v = [(-1.3, 1.3, F0, F0 + 3.2), (-1.1, 1.1, F0 + 3.2, F0 + 3.9)]
    oef_v += [(x - 0.8, x + 0.8, F0 + 0.9, F0 + 3.6) for x in (-4.2, 4.2)]
    oef_h = [(-1.3, 1.3, F0, F0 + 2.6)] + [(x - 0.8, x + 0.8, F0 + 0.9, F0 + 3.6) for x in (-4.2, 4.2)]
    aussenwand(g, "x", -hd, -1, -6.0, 6.0, HM, mat, oef_v)
    aussenwand(g, "x", hd, 1, -6.0, 6.0, HM, mat, oef_h)
    # ---- Fluegel: Westfluegel (x -12..-6) Wartesaal, Ostfluegel (x 6..12) Gepaeck/Vorsteher
    for sgn in (-1, 1):
        xa, xb = (-12.0, -6.0) if sgn < 0 else (6.0, 12.0)
        oef_f = [(min(sgn * 7.4, sgn * 8.6) - 0.0, max(sgn * 7.4, sgn * 8.6), F0 + 0.9, F0 + 2.7), (min(sgn * 9.6, sgn * 10.8), max(sgn * 9.6, sgn * 10.8), F0 + 0.9, F0 + 2.7)]
        oef_hf = [(min(sgn * 8.0, sgn * 10.0), max(sgn * 8.0, sgn * 10.0), F0, F0 + 2.5)] + [(min(sgn * 10.9, sgn * 11.5), max(sgn * 10.9, sgn * 11.5), F0 + 0.9, F0 + 2.7)]
        aussenwand(g, "x", -hd, -1, xa, xb, HF, mat, [(o[0], o[1], o[2], o[3]) for o in oef_f])
        aussenwand(g, "x", hd, 1, xa, xb, HF, mat, oef_hf)
        aussenwand(g, "y", sgn * 12.0, sgn, -hd + WD, hd - WD, HF, mat, [(-0.8, 0.8, F0 + 0.9, F0 + 2.7)])
        for x in ((7.4 + 8.6) / 2, (9.6 + 10.8) / 2):
            fensterschmuck(g, "x", -hd, -1, sgn * x, F0 + 1.8, 1.2, 1.8, "Laden gruen alt" if lvl else "Laden gruen")
        fensterschmuck(g, "x", hd, 1, sgn * 11.2, F0 + 1.8, 0.6, 1.8, None)
        fensterschmuck(g, "y", sgn * 12.0, sgn, 0.0, F0 + 1.8, 1.6, 1.8, None)
        # Querwand zum Mittelbau mit Tuer (y -1.6..-0.4)
        wand(g, "y", sgn * 6.0 - 0.15 if sgn > 0 else sgn * 6.0 - 0.15, sgn * 6.0 + 0.15, -hd + WD, hd - WD, -1.0, HM, "Innenwand", [(-1.8, -0.6, F0, F0 + TH)])
        tuerrahmen(g, "y", sgn * 6.0 - 0.15, sgn * 6.0 + 0.15, -1.8, -0.6, F0, F0 + TH)
        # Bahnsteigtuer (Westfluegel: Wartesaal; Ostfluegel: Gepaeck, zweiflueglig)
        tuerrahmen(g, "x", hd, hd + 0.07, min(sgn * 8.0, sgn * 10.0), max(sgn * 8.0, sgn * 10.0), F0, F0 + 2.5)
        g.box(min(sgn * 8.0, sgn * 10.0) - 0.4, hd, -0.6, max(sgn * 8.0, sgn * 10.0) + 0.4, hd + 1.0, F0, "Beton")
    # Dach Mittelbau (Giebel zur Strasse: First laengs y) und Fluegel (Walm)
    rz = dach(g, "y", 12.0, 2 * hd, HM, 2.9, ziegel, mat, e=0.55)
    for sgn in (-1, 1):
        gf = Lok(b, *g.P((sgn * 9.0, 0.0, 0.0))[:2], 0.0, math.pi, 1)
        dach(gf, "walm", 6.0, 2 * hd, HF, 1.4, ziegel, mat, e=0.5)
        g.box(sgn * 9.0 - 0.4, -0.4, HF - 0.1, sgn * 9.0 + 0.4, 0.4, HF + 2.5, "Klinker alt" if lvl else "Klinker")                      # Schornstein
        g.box(sgn * 9.0 - 0.5, -0.5, HF + 2.5, sgn * 9.0 + 0.5, 0.5, HF + 2.65, "Stein")
    # ---- Portal, Uhr, Schriftzug
    for sx in (-1, 1):
        g.box(sx * 1.3 - (0.0 if sx > 0 else 0.35), -hd - 0.3, F0, sx * 1.3 + (0.35 if sx > 0 else 0.0), -hd, F0 + 3.4, "Stein alt")
    g.box(-1.9, -hd - 0.35, F0 + 3.4, 1.9, -hd, F0 + 3.7, "Stein alt")
    tuerrahmen(g, "x", -hd - 0.07, -hd, -1.3, 1.3, F0, F0 + 3.2, "Rahmen weiss")
    g.box(-1.1, -hd + 0.05, F0 + 3.2, 1.1, -hd + 0.1, F0 + 3.9, "Glas")
    g.box(-1.3, -hd - 0.9, -0.6, 1.3, -hd - 0.07, F0, "Beton")
    g.box(-1.3, -hd - 1.5, -0.6, 1.3, -hd - 0.9, 0.1, "Beton")
    g.box(-1.3, -hd + WD, F0, -1.25, -hd + WD + 0.65, F0 + 3.1, "Tuer gruen")
    g.box(1.25, -hd + WD, F0, 1.3, -hd + WD + 0.65, F0 + 3.1, "Tuer gruen")
    zu = F0 + 6.4                                                       # Uhr auf dem Giebeldreieck (Dachrand), ueber dem Portal: dort verdeckt sie nichts
    yu = -hd - 0.55                                                     # Vorderkante des Daches (Dachueberstand e = 0,55 m)
    n = 16
    P = [(1.0 * math.cos(2 * math.pi * k / n), yu - 0.09, zu + 1.0 * math.sin(2 * math.pi * k / n)) for k in range(n)]
    g.poly(P, (0.0, -1.0, 0.0), "Uhr")
    for hh in range(12):
        a = 2 * math.pi * hh / 12
        g.box(0.82 * math.cos(a) - 0.04, yu - 0.11, zu + 0.82 * math.sin(a) - 0.04, 0.82 * math.cos(a) + 0.04, yu - 0.09, zu + 0.82 * math.sin(a) + 0.04, "Schrift schwarz")
    g.box(-0.04, yu - 0.12, zu, 0.04, yu - 0.09, zu + 0.65, "Schrift schwarz")
    g.box(0.0, yu - 0.12, zu - 0.04, 0.48, yu - 0.09, zu + 0.04, "Schrift schwarz")
    fensterschmuck(g, "x", -hd, -1, -4.2, F0 + 2.25, 1.6, 2.7, "Laden gruen alt" if lvl else "Laden gruen")
    fensterschmuck(g, "x", -hd, -1, 4.2, F0 + 2.25, 1.6, 2.7, "Laden gruen alt" if lvl else "Laden gruen")
    fensterschmuck(g, "x", hd, 1, -4.2, F0 + 2.25, 1.6, 2.7, None)
    fensterschmuck(g, "x", hd, 1, 4.2, F0 + 2.25, 1.6, 2.7, None)
    tuerrahmen(g, "x", hd, hd + 0.07, -1.3, 1.3, F0, F0 + 2.6)
    g.box(-1.4, hd, -0.6, 1.4, hd + 1.0, F0, "Beton")
    # ---- Boden, Decken
    ix0, ix1, iy0, iy1 = -12.0 + WD, 12.0 - WD, -hd + WD, hd - WD
    g.box(ix0, iy0, -0.7, ix1, iy1, F0, "Beton")
    g.box(-6.0 + 0.15, iy0, F0, 6.0 - 0.15, iy1, F0 + 0.03, "Linoleum")
    for sgn in (-1, 1):
        g.box(min(sgn * 6.15, sgn * 11.7), iy0, F0, max(sgn * 6.15, sgn * 11.7), iy1, F0 + 0.03, "Dielen")
        g.box(min(sgn * 6.15, sgn * 11.7), iy0, HF - 0.25, max(sgn * 6.15, sgn * 11.7), iy1, HF, "Decke")
    g.box(-6.0 + 0.15, iy0, HM - 0.25, 6.0 - 0.15, iy1, HM, "Decke")
    # ---- Schalterhalle: Fahrkartenschalter (Ostwand), Baenke, Ofen, Fahrplaene
    g.box(3.0, -2.6, F0, 5.7, -2.2, F0 + 1.15, "Holz")                                                     # Schaltertheke (quer)
    g.box(3.0, -2.65, F0 + 1.15, 5.7, -2.15, F0 + 1.22, "Holz alt")
    wand(g, "x", -2.5, -2.3, 3.0, 5.7, F0 + 1.22, F0 + 2.6, "Glas", [(3.5, 4.3, F0 + 1.5, F0 + 2.1), (4.7, 5.5, F0 + 1.5, F0 + 2.1)])
    g.box(3.0, -2.65, F0 + 2.6, 5.7, -2.15, F0 + 2.75, "Holz")
    g.box(3.0, -2.2, F0, 5.7, 1.0, F0 + 0.8, "Holz")                                                         # Rueckraum des Schalters (Tresen)
    g.box(3.1, -2.1, F0 + 0.8, 5.6, 0.9, F0 + 0.86, "Holz alt")
    g.box(4.2, -1.2, F0 + 0.86, 4.9, -0.5, F0 + 1.15, "Metall")                                              # Kasse / Stempelmaschine
    for k in range(3):
        g.box(-5.0, -3.4 + k * 1.1, F0, -3.9, -2.9 + k * 1.1, F0 + 0.45, "Bank")                           # Wartebaenke
        g.box(-5.0, -3.4 + k * 1.1, F0 + 0.45, -4.9, -2.9 + k * 1.1, F0 + 1.0, "Bank")
    g.box(-3.0, 1.6, F0, -1.2, 2.1, F0 + 0.8, "Holz")                                                        # Auskunftstisch
    g.prism(-5.2, 2.6, F0, 0.45, 2.0, 8, "Kachel")                                                           # Kachelofen
    g.box(-5.45, 2.35, F0 + 2.0, -4.95, 2.85, F0 + 2.1, "Metall")
    for k in range(3):                                                                                       # Fahrplanaushaenge
        g.box(-5.8 + k * 1.3, 3.95, F0 + 1.6, -4.7 + k * 1.3, 4.0, F0 + 3.0, "Schild gelb")
    g.box(1.6, -3.9, F0, 2.9, -3.5, F0 + 0.5, "Ware")                                                        # Gepaeckkarre
    # ---- Westfluegel: Wartesaal (Baenke, Tisch, Kachelofen)
    for k in range(3):
        g.box(-11.6, -3.4 + k * 1.2, F0, -10.8, -2.8 + k * 1.2, F0 + 0.45, "Bank")
        g.box(-11.6, -3.4 + k * 1.2, F0 + 0.45, -11.5, -2.8 + k * 1.2, F0 + 1.0, "Bank")
    g.box(-9.6, -1.5, F0, -8.2, -0.4, F0 + 0.78, "Holz")
    g.prism(-7.0, 2.7, F0, 0.4, 1.8, 8, "Kachel")
    g.box(-8.8, 3.6, F0 + 1.4, -7.4, 3.65, F0 + 2.2, "Schild rot")
    # ---- Ostfluegel: Gepaeck (Waage, Kisten) und Vorsteherbuero
    g.box(7.2, -3.8, F0, 8.6, -2.2, F0 + 0.8, "Holz")
    g.box(7.1, -3.9, F0 + 0.8, 8.7, -2.1, F0 + 0.85, "Holz alt")
    g.box(9.6, 2.8, F0, 11.6, 3.7, F0 + 0.8, "Holz")                                                        # Schreibtisch Vorsteher
    g.box(10.2, 2.0, F0, 10.6, 2.4, F0 + 0.45, "Holz")
    g.box(11.4, -3.5, F0, 11.7, -1.5, F0 + 1.9, "Metall")                                                    # Aktenschrank
    for k, (x, y) in enumerate(((7.8, 2.8), (8.6, 3.3), (9.0, 0.6), (9.0, 1.4))):
        g.box(x - 0.4, y - 0.4, F0, x + 0.4, y + 0.4, F0 + 0.55, "Ware" if k % 2 else "Ware rot")
    g.box(7.0, 3.9, F0 + 1.2, 8.4, 4.0, F0 + 2.0, "Schild gelb")
    return g


# ------------------------------------------------------------------ Bahnsteig mit Dach
def bahnsteig(b):
    """Hausbahnsteig (36 x 7,3 m, 0,28 m hoch) mit weisser Kante und Warnstreifen, Bahnsteigdach (Pultdach auf Staendern), Namensschildern, Baenken, Lampen, Gepaeckkarren."""
    x0, y0, x1, y1 = BAHNSTEIG
    b.box(x0, y0, -0.4, x1, y1, BST_H, "Bahnsteig")
    b.box(x0, y0, BST_H - 0.01, x1, y0 + 0.3, BST_H + 0.01, "Bahnsteigkante")
    b.box(x0, y0 + 0.9, BST_H - 0.01, x1, y0 + 1.0, BST_H + 0.012, "Bahnsteigkante")
    # Dach: Pult von y = 36,3 (3,4 m) nach y = 43 (3,85 m) an der Gebaeudewand; Staender am Gleisrand
    ya, yb, za, zb_ = 36.3, 43.0, 3.4, 3.85
    xa, xb = x0 + 1.0, x1 - 1.0
    q = [(xa, ya, za), (xb, ya, za), (xb, yb, zb_), (xa, yb, zb_)]
    b.add(q, [(0, 1, 2, 3)], "Wellblech alt")
    b.add([(xa, ya, za - 0.12), (xa, yb, zb_ - 0.12), (xb, yb, zb_ - 0.12), (xb, ya, za - 0.12)], [(0, 1, 2, 3)], "Holz alt")
    b.box(xa, ya - 0.05, za - 0.35, xb, ya + 0.08, za + 0.04, "Rahmen weiss")
    xs = [xa + 1.0 + 6.0 * k for k in range(6)]
    for x in xs:
        b.box(x - 0.11, 37.2 - 0.11, BST_H, x + 0.11, 37.2 + 0.11, za - 0.1, "Metall")
        b.box(x - 0.2, 37.2 - 0.2, BST_H, x + 0.2, 37.2 + 0.2, BST_H + 0.25, "Metall")
        b.beam((x, 37.2, za - 0.2), (x, yb, zb_ - 0.2), 0.16, 0.28, "Holz alt")
        for sg in (-1, 1):
            b.beam((x, 37.2 + 0.0, za - 0.9), (x, 37.2 + sg * 0.9 + 0.0, za - 0.2), 0.08, 0.1, "Metall") if sg > 0 else None
    # Namensschilder zwischen den Staendern
    for xc in (xs[1] + 3.0, xs[3] + 3.0):
        g = Lok(b, xc, 37.2, 0.0, 0.0, 1)
        g.box(-1.6, -0.05, 2.45, 1.6, 0.05, 3.2, "Schild gruen")
        g.box(-1.6, -0.06, 2.42, 1.6, 0.06, 2.45, "Rahmen weiss")
        g.box(-1.6, -0.06, 3.2, 1.6, 0.06, 3.23, "Rahmen weiss")
        for sx in (-1.4, 1.4):
            g.box(sx - 0.02, -0.02, 3.23, sx + 0.02, 0.02, za - 0.08, "Metall")
        O.schrift(g, "POLYTOWN", 0.0, 2.6, -0.05, 0.058, "Schrift weiss", 0.02)
    # Lampen am Dach
    for x in xs[:-1]:
        xl = x + 3.0
        b.box(xl - 0.02, 39.5 - 0.02, 3.0, xl + 0.02, 39.5 + 0.02, 3.6, "Metall")
        b.box(xl - 0.18, 39.5 - 0.18, 2.8, xl + 0.18, 39.5 + 0.18, 3.0, "Schild gelb")
    # Baenke und Karren
    for xc in (143.5, 156.5):
        for dy, (zl, zh) in ((0.0, (0.28 + 0.42, 0.28 + 0.47)),):
            b.box(xc - 0.9, 38.9, BST_H + 0.42, xc + 0.9, 39.4, BST_H + 0.47, "Bank")
        b.box(xc - 0.9, 39.35, BST_H + 0.47, xc + 0.9, 39.4, BST_H + 0.95, "Bank")
        for sx in (-0.8, 0.8):
            b.box(xc + sx - 0.04, 38.95, BST_H, xc + sx + 0.04, 39.35, BST_H + 0.42, "Metall")
    xk = 162.2
    b.box(xk, 41.0, BST_H + 0.35, xk + 1.6, 41.9, BST_H + 0.42, "Holz")                                        # Gepaeckkarre
    for sx in (0.2, 1.4):
        b.box(xk + sx - 0.3, 41.9, BST_H, xk + sx + 0.3, 41.95, BST_H + 0.6, "Metall")
    b.box(xk + 0.2, 41.2, BST_H + 0.42, xk + 1.0, 41.8, BST_H + 0.9, "Ware")
    b.box(xk + 0.9, 41.3, BST_H + 0.42, xk + 1.4, 41.8, BST_H + 0.75, "Ware rot")
    for k in range(3):                                                                                       # Milchkannen
        b.prism(135.2 + 0.4 * k, 42.2, BST_H, 0.17, 0.7, 8, "Metall")
    # Rampen (Enden des Bahnsteigs)
    for (xe, sgn) in ((x0, -1), (x1, 1)):
        b.add([(xe, y0, BST_H), (xe, y1, BST_H), (xe + sgn * 0.9, y1, 0.0), (xe + sgn * 0.9, y0, 0.0)], [(0, 1, 2, 3), (3, 2, 1, 0)], "Bahnsteig")


# ------------------------------------------------------------------ Stellwerk (Bahnsteig, Westende)
STELLWERK = (135.0, 40.0)


def stellwerk(b, lvl=1):
    """Stellwerk (6,4 x 4,4 m) am Westende des Bahnsteigs: unten Backstein (Relaisraum, Tuer zum Bahnsteig, Innentreppe), oben verglaster Stellwerksraum mit
    Hebelbank, Schreibtisch und Fahrplantafel. Tuer nach Osten (Lok theta = pi/2)."""
    g = Lok(b, STELLWERK[0], STELLWERK[1], 0.0, math.pi / 2, 1)
    hw, hd = 3.2, 2.2
    zf2 = F0 + 2.7                                     # Oberkante Zwischendecke
    zt = zf2 + 2.5                                     # Traufe
    ziegel = "Ziegel alt" if lvl else "Ziegel"
    # unten
    oef_v = [(-2.0, -1.0, F0, F0 + 2.1), (0.4, 1.6, F0 + 0.9, F0 + 2.0), (2.0, 3.0, F0 + 0.9, F0 + 2.0)]
    aussenwand(g, "x", -hd, -1, -hw, hw, zf2, ziegel, oef_v)
    aussenwand(g, "x", hd, 1, -hw, hw, zf2, ziegel, [(-1.0, 0.0, F0 + 0.9, F0 + 2.0)])
    for sgn in (-1, 1):
        aussenwand(g, "y", sgn * hw, sgn, -hd + WD, hd - WD, zf2, ziegel, [(-0.5, 0.5, F0 + 0.9, F0 + 2.0)])
    tuerrahmen(g, "x", -hd - 0.07, -hd, -2.0, -1.0, F0, F0 + 2.1)
    g.box(-1.95, -hd + WD, F0, -1.9, -hd + WD + 0.9, F0 + 2.05, "Tuer gruen")
    g.box(-2.3, -hd - 0.8, -0.6, -0.7, -hd - 0.07, F0, "Beton")
    g.box(-hw + WD, -hd + WD, -0.7, hw - WD, hd - WD, F0, "Beton")
    g.box(-hw + WD, -hd + WD, F0, hw - WD, hd - WD, F0 + 0.03, "Dielen")
    # Innentreppe (Rueckwand, steigt nach +x), Oeffnung in der Decke
    n = 13
    rise = (zf2 - F0) / n
    for k in range(n):
        xk = -2.6 + 0.26 * k
        g.box(xk, 1.0, F0, xk + 0.26, hd - WD, F0 + rise * (k + 1), "Holz")
    for k in range(n):                                                                           # Treppengelaender zur Raumseite (Fuellung)
        xk = -2.6 + 0.26 * k
        g.box(xk, 0.93, F0 + rise * (k + 1), xk + 0.26, 1.07, max(F0 + rise * (k + 1) + 1.0, zf2 + 1.0 if xk >= -1.9 else 0.0), "Holz")
    ox0, ox1, oy0, oy1 = -1.9, 0.5, 1.0, hd - WD
    sl = [(-hw + WD, -hd + WD, ox0, hd - WD), (ox0, -hd + WD, ox1, oy0), (ox1, -hd + WD, hw - WD, hd - WD)]
    for (a, c, d, e) in sl:
        g.box(a, c, zf2 - 0.25, d, e, zf2, "Decke")
    g.box(ox0 - 0.07, oy0 - 0.07, zf2, ox1, oy0 + 0.07, zf2 + 1.0, "Metall")                      # Gelaender (offene Seite)
    g.box(ox0 - 0.07, oy0, zf2, ox0 + 0.07, hd - WD, zf2 + 1.0, "Metall")                          # Gelaender (Stirnseite)
    g.box(-hw + WD, -hd + WD, F0, -hw + WD + 0.5, -hd + WD + 0.5, F0 + 1.0, "Holz")             # Relaiskasten
    g.box(2.0, -hd + WD, F0, hw - WD, -hd + WD + 0.6, F0 + 1.9, "Metall")
    g.box(1.0, hd - WD - 0.35, F0 + 0.6, 2.4, hd - WD, F0 + 1.7, "Metall")
    # oben: Fensterband
    zb_ = zf2 + 1.0
    # obere Waende: Brustung (Holz) + Glas
    for (aus, sg) in ((-hd, -1), (hd, 1)):
        pbox(g, "x", -hw, hw, min(aus, aus - sg * WD), max(aus, aus - sg * WD), zf2, zb_, "Holz" if lvl == 0 else "Holz alt")
        pbox(g, "x", -hw, hw, min(aus, aus - sg * WD), max(aus, aus - sg * WD), zt - 0.4, zt, "Holz alt")
        pbox(g, "x", -hw, hw, min(aus, aus - sg * 0.05) - (0.0), max(aus, aus - sg * 0.05), zb_, zt - 0.4, "Glas")
        for xp in (-hw, -1.6, 0.0, 1.6, hw - 0.1):
            pbox(g, "x", xp, xp + 0.1, min(aus, aus - sg * WD), max(aus, aus - sg * WD), zb_, zt - 0.4, "Holz alt")
    for sgn in (-1, 1):
        pbox(g, "y", -hd, hd, sgn * hw - (WD if sgn > 0 else 0), sgn * hw + (0 if sgn > 0 else WD), zf2, zb_, "Holz alt")
        pbox(g, "y", -hd, hd, sgn * hw - (WD if sgn > 0 else 0), sgn * hw + (0 if sgn > 0 else WD), zb_, zt, "Holz alt")
    g.box(-hw - 0.2, -hd - 0.2, zt, hw + 0.2, hd + 0.2, zt + 0.2, "Dach grau alt")
    g.box(-hw - 0.2, -hd - 0.2, zt + 0.2, hw + 0.2, hd + 0.2, zt + 0.28, "Wellblech alt")
    g.box(1.5, 0.4, zt + 0.28, 2.0, 0.9, zt + 1.3, "Klinker alt")                                  # Schornstein
    # Einrichtung oben
    for k in range(8):                                                                           # Hebelbank (Hebel + Rahmen)
        xk = -1.8 + 0.28 * k
        g.box(xk - 0.04, -1.1, zf2, xk + 0.04, -0.9, zf2 + 0.9, "Metall")
        g.box(xk - 0.02, -1.05, zf2 + 0.9, xk + 0.02, -0.95, zf2 + 1.1, "Signal rot" if k % 3 == 0 else "Signal weiss")
    g.box(-2.1, -1.2, zf2, 0.5, -0.8, zf2 + 0.3, "Holz")
    g.box(1.2, 0.3, zf2, 2.8, 1.0, zf2 + 0.78, "Holz")
    g.box(1.6, 1.0, zf2, 2.0, 1.4, zf2 + 0.45, "Holz alt")
    g.box(1.4, 0.5, zf2 + 0.78, 1.8, 0.8, zf2 + 0.92, "Metall")                                  # Fernsprecher
    g.box(2.9, 1.0, zf2 + 1.2, 3.0, 1.9, zf2 + 2.0, "Schild gelb")                               # Fahrplantafel
    return g


# ------------------------------------------------------------------ Gueterschuppen
SCHUPPEN = (126.0, 19.2)
FG = 0.95                                              # Hoehe des Ladebodens (unter 1 m: offene Rampenkante ist kein Absturz)


def gueterschuppen(b, lvl=1):
    """Gueterschuppen (16 x 7 m) am Gleis 3 mit Laderampe (1,1 m hoch, Vordach, Treppe) zum Gleis, drei Schiebetueren zur Rampe, Hintertuer zur Gueterstrasse (Treppe).
    Innen Kisten, Saecke, Waage und kleines Buero. Fassade zum Gleis (Norden): Lok theta = pi."""
    g = Lok(b, SCHUPPEN[0], SCHUPPEN[1], 0.0, math.pi, 1)
    hw, hd = 8.0, 3.5
    mat = "Wellblech alt" if lvl else "Wellblech"
    holz = "Holz alt"
    H = FG + 3.4
    oef_v = [(x - 1.2, x + 1.2, FG, FG + 2.7) for x in (-5.0, 0.0, 5.0)]
    oef_h = [(-0.6, 0.6, FG, FG + 2.1), (4.5, 5.5, FG + 0.9, FG + 2.0), (-5.5, -4.5, FG + 0.9, FG + 2.0)]
    ziegel = "Ziegel dunkel alt" if lvl else "Ziegel dunkel"
    for (aus, sg, oef) in ((-hd, -1, oef_v), (hd, 1, oef_h)):
        pb = lambda p0, p1, z0, z1, m: wand(g, "x", p0, p1, -hw, hw, z0, z1, m, oef)
        p0, p1 = sorted((aus, aus - sg * WD))
        pb(p0, p1, -1.0, FG + 1.0, ziegel)
        pb(p0, p1, FG + 1.0, H, mat if lvl >= 0 else mat)
    for sgn in (-1, 1):
        p0, p1 = sorted((sgn * hw, sgn * hw - sgn * WD))
        wand(g, "y", p0, p1, -hd + WD, hd - WD, -1.0, FG + 1.0, ziegel, [])
        wand(g, "y", p0, p1, -hd + WD, hd - WD, FG + 1.0, H, mat, [(-0.7, 0.7, FG + 0.9, FG + 1.9)])
    g.box(-hw + WD, -hd + WD, -0.7, hw - WD, hd - WD, FG, "Beton")
    g.box(-hw + WD, -hd + WD, FG, hw - WD, hd - WD, FG + 0.03, "Dielen")
    # Rampe
    rd = 2.5
    g.box(-hw - 0.5, -hd - rd, -0.7, hw + 0.5, -hd, FG, "Bruch Beton")
    g.box(-hw - 0.5, -hd - rd, FG - 0.01, hw + 0.5, -hd - rd + 0.12, FG + 0.02, "Bahnsteigkante")
    for k in range(3):                                                                              # Treppe am Rampenende (vier gleiche Stufen)
        g.box(hw + 0.5 + 0.3 * k, -hd - rd, -0.7, hw + 0.5 + 0.3 * (k + 1), -hd - rd + 1.2, FG - FG / 4 * (k + 1), "Bruch Beton")
    # Vordach ueber der Rampe
    for xp in (-7.5, -2.5, 2.5, 7.5):
        g.box(xp - 0.1, -hd - rd + 0.2 - 0.1, FG, xp + 0.1, -hd - rd + 0.2 + 0.1, FG + 3.3, "Metall")
    g.box(-hw - 0.5, -hd - rd, FG + 3.3, hw + 0.5, -hd, FG + 3.45, "Holz alt")
    g.box(-hw - 0.5, -hd - rd, FG + 3.45, hw + 0.5, -hd - rd + 0.1, FG + 3.6, "Rahmen weiss")
    # Schiebetueren (halb geoeffnet), Tuerschienen
    for x in (-5.0, 0.0, 5.0):
        g.box(x + 0.2, -hd - 0.12, FG, x + 1.35, -hd - 0.04, FG + 2.7, "Tuer gruen")
        g.box(x - 1.3, -hd - 0.14, FG + 2.75, x + 1.4, -hd - 0.08, FG + 2.82, "Metall")
    # Dach
    rz = dach(g, "x", 2 * hw, 2 * hd, H, 1.3, "Wellblech alt" if lvl else "Wellblech", mat, e=0.45)
    g.box(-hw - 0.5, -0.1, H + 1.25, hw + 0.5, 0.1, H + 1.4, "Rost")
    # Hintertuer (Suedwand, +y) mit Treppe
    tuerrahmen(g, "x", hd, hd + 0.07, -0.6, 0.6, FG, FG + 2.1)
    for k in range(3):                                                                              # Treppe an der Hintertuer
        g.box(-0.9, hd + 0.3 * k, -0.7, 0.9, hd + 0.3 * (k + 1), FG - FG / 4 * (k + 1), "Bruch Beton")
    # Fenster
    for x in (-5.0, 5.0):
        fensterschmuck(g, "x", hd, 1, x, FG + 1.45, 1.0, 1.1, None)
    fensterschmuck(g, "y", hw, 1, 0.0, FG + 1.45, 1.0, 1.1, None)
    fensterschmuck(g, "y", -hw, -1, 0.0, FG + 1.45, 1.0, 1.1, None)
    # Aufschrift
    # Einrichtung innen
    for k in range(4):
        g.box(-7.4 + 1.0 * k, hd - 1.4, FG, -6.6 + 1.0 * k, hd - 0.6, FG + 0.7, "Ware")
    g.box(-7.4, hd - 1.4, FG + 0.7, -6.6, hd - 0.6, FG + 1.3, "Ware rot")
    g.box(-6.4, hd - 1.4, FG + 0.7, -5.6, hd - 0.6, FG + 1.3, "Ware")
    for k in range(5):
        g.box(2.2 + 0.7 * k, hd - 1.2, FG, 2.8 + 0.7 * k, hd - 0.6, FG + 0.45, "Sack")
    g.box(2.4, hd - 1.2, FG + 0.45, 3.0, hd - 0.6, FG + 0.9, "Sack")
    g.box(-3.3, 0.2, FG, -1.9, 1.4, FG + 0.25, "Metall")                                         # Plattformwaage
    g.box(-3.1, 1.2, FG + 0.25, -2.9, 1.4, FG + 1.3, "Metall")
    g.box(-3.1, 1.2, FG + 1.3, -2.9, 1.4, FG + 1.5, "Schild gelb")
    g.box(5.4, hd - 2.2, FG, 7.6, hd - 0.3, FG + 0.1, "Holz alt")                                  # Buerokoje
    g.box(6.6, hd - 1.5, FG, 7.6, hd - 0.5, FG + 0.78, "Holz")
    g.box(5.5, hd - 0.9, FG, 5.9, hd - 0.5, FG + 0.45, "Holz alt")
    # Gueter auf der Rampe
    for k, (x, ww) in enumerate(((-6.5, 0.9), (-3.0, 0.7), (3.5, 1.0), (6.8, 0.8))):
        g.box(x, -hd - 1.9, FG, x + ww, -hd - 1.2, FG + 0.5 + 0.2 * (k % 2), "Ware" if k % 2 else "Ware rot")
    return g


# ------------------------------------------------------------------ Wasserturm und Wasserkran
WASSERTURM = (178.0, 40.5)


def wasserturm(b, lvl=1):
    """Wasserturm (Backstein, 3,6 x 3,6 m, 7 m hoch) mit Stahlbehaelter und Kegeldach, Leiter und Tuer; daneben ein Wasserkran, dessen Ausleger ueber Gleis 1 schwenkt."""
    g = Lok(b, WASSERTURM[0], WASSERTURM[1], 0.0, 0.0, 1)
    ziegel = "Ziegel dunkel alt" if lvl else "Ziegel dunkel"
    hw = 1.8
    aussenwand(g, "x", -hw, -1, -hw, hw, 6.6, ziegel, [(-0.5, 0.5, F0, F0 + 2.0), (-0.3, 0.3, 4.2, 5.2)])
    aussenwand(g, "x", hw, 1, -hw, hw, 6.6, ziegel, [(-0.3, 0.3, 4.2, 5.2)])
    for sgn in (-1, 1):
        aussenwand(g, "y", sgn * hw, sgn, -hw + WD, hw - WD, 6.6, ziegel, [])
    tuerrahmen(g, "x", -hw - 0.07, -hw, -0.5, 0.5, F0, F0 + 2.0)
    g.box(-0.5, -hw + WD, F0, -0.45, -hw + WD + 0.5, F0 + 1.95, "Tuer gruen")
    g.box(-hw + WD, -hw + WD, -0.7, hw - WD, hw - WD, F0, "Beton")
    g.box(-hw + WD, -hw + WD, 6.4, hw - WD, hw - WD, 6.6, "Decke")
    g.box(-hw - 0.2, -hw - 0.2, 6.6, hw + 0.2, hw + 0.2, 6.8, "Stein alt")
    g.prism(0.0, 0.0, 6.8, 2.0, 2.8, 14, "Rost")
    for zz in (7.3, 8.1, 8.9):
        g.prism(0.0, 0.0, zz, 2.06, 0.08, 14, "Metall")
    g.prism(0.0, 0.0, 9.6, 2.1, 0.12, 14, "Metall")
    # Kegeldach
    n = 14
    ring = [(2.2 * math.cos(2 * math.pi * k / n), 2.2 * math.sin(2 * math.pi * k / n), 9.7) for k in range(n)]
    wv = [g.P(p) for p in ring] + [g.P((0.0, 0.0, 11.2))]
    b.add(wv, [tuple(range(n - 1, -1, -1))] + [(k, (k + 1) % n, n) for k in range(n)], "Dach grau alt")
    # Leiter an der Westwand
    for zz in [0.4 + 0.3 * k for k in range(1, 22)]:
        g.box(-hw - 0.2, 0.55, zz, -hw, 0.95, zz + 0.04, "Metall")
    g.box(-hw - 0.22, 0.5, 0.4, -hw - 0.16, 0.56, 6.7, "Metall")
    g.box(-hw - 0.22, 0.94, 0.4, -hw - 0.16, 1.0, 6.7, "Metall")
    # Wasserkran (Standrohr + Ausleger ueber Gleis 1)
    kx, ky = 181.0, 36.9
    b.box(kx - 0.2, ky - 0.2, 0.0, kx + 0.2, ky + 0.2, 0.5, "Stein alt")
    b.box(kx - 0.1, ky - 0.1, 0.5, kx + 0.1, ky + 0.1, 3.9, "Metall")
    b.prism(kx, ky, 3.9, 0.2, 0.25, 8, "Metall")
    b.beam((kx, ky, 4.0), (kx, GLEIS_Y[1] + 0.9, 3.6), 0.2, 0.2, "Metall")
    b.beam((kx, GLEIS_Y[1] + 0.9, 3.6), (kx, GLEIS_Y[1] + 0.9, 2.8), 0.12, 0.12, "Metall")
    b.beam((kx, ky - 0.1, 0.9), (WASSERTURM[0] - 1.8, WASSERTURM[1] - 1.0, 0.2), 0.12, 0.12, "Metall")        # Rohr zum Turm
    return g


# ------------------------------------------------------------------ Dampflok, Personenwagen
def zyl_x(b, x0, x1, y, z, r, mat, n=12):
    """Liegender Zylinder (Kessel) mit Achse in x-Richtung."""
    ring = lambda x: [(x, y + r * math.cos(2 * math.pi * k / n), z + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    a, c = ring(x0), ring(x1)
    faces = [tuple(range(n - 1, -1, -1)), tuple(range(n, 2 * n))] + [(k, (k + 1) % n, n + (k + 1) % n, n + k) for k in range(n)]
    b.add(a + c, faces, mat)


def dampflok(b, x0, y, z0=BALLAST_H + 0.24):
    """Schlepptenderlok der 40er (Rauchfang, Kessel, Dampfdom, Fuehrerhaus, Treib-/Kuppelstangen) mit Tender (Kohle), 13 m lang; Front zeigt nach +x. x0 = Tenderende."""
    zr = 0.42
    # Tender
    b.box(x0, y - 1.2, z0 + 0.35, x0 + 5.0, y + 1.2, z0 + 0.6, "Metall")
    b.box(x0 + 0.1, y - 1.25, z0 + 0.6, x0 + 4.9, y + 1.25, z0 + 1.9, "Schwelle")
    b.box(x0 + 0.3, y - 1.1, z0 + 1.9, x0 + 4.7, y + 1.1, z0 + 2.15, "Kohle")
    kegel(b, x0 + 2.5, y, z0 + 2.1, 1.0, 0.5, "Kohle", n=8)
    for sg in (-1, 1):
        for xx in (x0 + 0.9, x0 + 1.9, x0 + 3.1, x0 + 4.1):
            scheibe_y(b, xx, y + sg * 0.74, z0 + zr, zr, 0.1, "Metall", n=12)
    # Lok
    xl = x0 + 5.4
    b.box(xl, y - 1.15, z0 + 0.75, xl + 7.6, y + 1.15, z0 + 1.0, "Metall")
    zyl_x(b, xl + 2.2, xl + 7.4, y, z0 + 2.1, 1.0, "Schwelle", n=12)
    b.box(xl + 7.4, y - 1.0, z0 + 1.1, xl + 7.6, y + 1.0, z0 + 3.1, "Metall")                       # Rauchkammertuer
    b.prism(xl + 7.0, y, z0 + 3.05, 0.3, 0.9, 8, "Metall")                                          # Schornstein
    b.prism(xl + 7.0, y, z0 + 3.95, 0.42, 0.18, 8, "Metall")
    b.prism(xl + 5.2, y, z0 + 3.05, 0.55, 0.45, 8, "Metall")                                        # Dampfdom
    b.prism(xl + 3.6, y, z0 + 3.05, 0.4, 0.3, 8, "Rost")                                            # Sandkasten
    b.box(xl, y - 1.25, z0 + 1.0, xl + 2.3, y + 1.25, z0 + 3.4, "Schwelle")                         # Fuehrerhaus
    b.box(xl - 0.1, y - 1.35, z0 + 3.4, xl + 2.5, y + 1.35, z0 + 3.55, "Metall")
    for sg in (-1, 1):
        b.box(xl + 0.6, y + sg * 1.25 - (0.0 if sg > 0 else 0.03), z0 + 2.0, xl + 1.7, y + sg * 1.25 + (0.03 if sg > 0 else 0.0), z0 + 2.9, "Glas")
    for sg in (-1, 1):
        for xx in (xl + 3.0, xl + 4.6, xl + 6.2):
            scheibe_y(b, xx, y + sg * 0.74, z0 + 0.72, 0.72, 0.1, "Metall", n=14)
        b.box(xl + 3.0, y + sg * 0.80 - 0.03, z0 + 0.55, xl + 6.2, y + sg * 0.80 + 0.03, z0 + 0.7, "Metall")       # Kuppelstange
        b.box(xl + 6.2, y + sg * 1.0 - 0.15, z0 + 0.95, xl + 7.2, y + sg * 1.0 + 0.15, z0 + 1.35, "Metall")      # Zylinder
    for sg in (-1, 1):
        scheibe_y(b, xl + 6.9, y + sg * 0.74, z0 + 0.3, 0.3, 0.1, "Metall", n=10)
    b.box(xl + 7.6, y - 0.9, z0 + 0.5, xl + 7.9, y + 0.9, z0 + 0.7, "Signal rot")                     # Pufferbohle
    b.box(xl + 7.6, y - 0.25, z0 + 2.4, xl + 7.7, y + 0.25, z0 + 2.9, "Schild gelb")              # Laterne
    b.box(x0 + 5.0, y - 0.1, z0 + 0.5, x0 + 5.4, y + 0.1, z0 + 0.7, "Metall")                       # Kupplung


def personenwagen(b, x0, y, laenge=14.0, z0=BALLAST_H + 0.24):
    """Personenwagen (3. Klasse, 40er): gruener Kasten mit Fensterband, Plattformen an den Enden, Dach; x0 = Westende."""
    x1 = x0 + laenge
    b.box(x0, y - 1.2, z0 + 0.4, x1, y + 1.2, z0 + 0.6, "Metall")
    b.box(x0 + 0.4, y - 1.4, z0 + 0.6, x1 - 0.4, y + 1.4, z0 + 3.0, "Wagen gruen")
    b.box(x0 + 0.4, y - 1.45, z0 + 1.3, x1 - 0.4, y + 1.45, z0 + 1.38, "Rahmen weiss")
    for sg in (-1, 1):
        n = 10
        for k in range(n):
            xk = x0 + 1.4 + k * (laenge - 2.8) / n
            yy = y + sg * 1.405
            b.box(xk, min(yy, yy + sg * 0.02), z0 + 1.6, xk + 0.8, max(yy, yy + sg * 0.02), z0 + 2.5, "Glas")
        for xx in (x0 + 2.2, x1 - 2.2):
            for dx in (-0.5, 0.5):
                scheibe_y(b, xx + dx, y + sg * 0.74, z0 + 0.42, 0.42, 0.1, "Metall", n=12)
    b.box(x0 + 0.4, y - 1.3, z0 + 3.0, x1 - 0.4, y + 1.3, z0 + 3.12, "Dach grau")
    b.box(x0 + 0.6, y - 0.9, z0 + 3.12, x1 - 0.6, y + 0.9, z0 + 3.28, "Dach grau")
    for xe in (x0, x1 - 0.4):                                                                         # Endbuehnen
        b.box(xe, y - 1.0, z0 + 0.6, xe + 0.4, y + 1.0, z0 + 0.7, "Metall")
        b.box(xe + (0.0 if xe == x0 else 0.4) - 0.0, y - 0.1, z0 + 0.5, xe + (-0.3 if xe == x0 else 0.7), y + 0.1, z0 + 0.7, "Metall")


# ------------------------------------------------------------------ Gleisanlage
X_WEICHE = 100.0                                         # hier zweigt Gleis 2 von Gleis 3 ab (Gleis 1 folgt bei x = 112)
WEICHE = {2: (X_WEICHE, X_WEICHE + 12.0), 1: (X_WEICHE + 12.0, X_WEICHE + 24.0)}


def gleise(b):
    """Gleis 3 (durchgehend vom Steinbruch-Prellbock bis zum Gleisende am Bahnhof), Gleis 2 und 1 ueber S-Kurven (Weichenstrassen) mit Prellboecken, Signalen."""
    gleis_gerade(b, GLEIS_Y[3], X_PRELL_W, T.TUNNEL_X + 8.0)                          # Gleis 3 laeuft weiter bis in den Tunnel (tunnel.py)
    a0, a1 = WEICHE[2]
    gleis_kurve(b, s_kurve(a0, GLEIS_Y[3], a1, GLEIS_Y[2], 8))
    gleis_gerade(b, GLEIS_Y[2], a1, X_PRELL_O)
    c0, c1 = WEICHE[1]
    gleis_kurve(b, s_kurve(c0, GLEIS_Y[2], c1, GLEIS_Y[1], 8))
    gleis_gerade(b, GLEIS_Y[1], c1, X_PRELL_O)
    prellbock(b, X_PRELL_W, GLEIS_Y[3], 1)
    for k in (1, 2):
        prellbock(b, X_PRELL_O, GLEIS_Y[k], -1)
    # Weichenlaterne, Signale
    b.box(a0 + 0.5, GLEIS_Y[3] - 1.75, 0.0, a0 + 0.6, GLEIS_Y[3] - 1.65, 0.7, "Metall")
    b.box(a0 + 0.4, GLEIS_Y[3] - 1.9, 0.7, a0 + 0.7, GLEIS_Y[3] - 1.6, 1.0, "Signal rot")
    formsignal(b, 94.0, GLEIS_Y[3] - 2.1, 5.0, -1)
    formsignal(b, 128.0, (GLEIS_Y[1] + GLEIS_Y[2]) / 2, 5.5, 1)
    formsignal(b, 126.0, GLEIS_Y[3] + 1.9, 4.5, 1)
    bahnuebergang(b)


def _kreuzbrett(b, x, y, z, ys, mat):
    """Schraeges Brett des Andreaskreuzes (Ebene x-z bei y), 0,9 m lang."""
    d = 0.45
    for sgn in (-1, 1):
        q = [(x - d, y, z - sgn * d), (x + d, y, z + sgn * d), (x + d, y + ys * 0.04, z + sgn * d), (x - d, y + ys * 0.04, z - sgn * d)]
        # Brett als schmales Parallelogramm (Breite 0,12 in z-Richtung)
        p = [(x - d, y, z - sgn * d - 0.06), (x - d, y, z - sgn * d + 0.06), (x + d, y, z + sgn * d + 0.06), (x + d, y, z + sgn * d - 0.06)]
        b.add(p, [(0, 1, 2, 3), (3, 2, 1, 0)], mat)


def bahnuebergang(b):
    """Bahnuebergang der Gueterstrasse: Holzbohlen zwischen/neben den Schienen und beidseitig ein Andreaskreuz mit Pfosten."""
    x = UEBERGANG_X
    b.box(x - 3.0, 24.6, 0.0, x + 3.0, 32.4, 0.27, "Holz alt")
    for (px, py) in ((x - 3.6, 33.0), (x + 3.6, 24.0)):
        b.box(px - 0.06, py - 0.06, 0.0, px + 0.06, py + 0.06, 2.6, "Metall")
        b.box(px - 0.5, py - 0.03, 2.1, px + 0.5, py + 0.03, 2.9, "Signal weiss")
        _kreuzbrett(b, px, py - 0.04, 2.5, -1, "Signal rot")


def zuege(b):
    """Rollendes Material: beladene Muldenwagen unter dem Verladebunker (Gleis 3) und weiter ostwaerts, Zug am Bahnsteig (Gleis 1), Wagen auf Gleis 2."""
    for i, x0 in enumerate((71.7, 81.0, 90.3, 99.6)):
        offener_wagen(b, x0, GLEIS_Y[3], beladen=i != 3, mat="Wagen braun" if i % 2 == 0 else "Wagen grau")
    offener_wagen(b, 118.0, GLEIS_Y[2], beladen=True, mat="Wagen grau")
    offener_wagen(b, 127.6, GLEIS_Y[2], beladen=False, mat="Wagen braun")
    personenwagen(b, 134.5, GLEIS_Y[1])
    personenwagen(b, 149.0, GLEIS_Y[1])
    dampflok(b, 163.5, GLEIS_Y[1])


# ------------------------------------------------------------------ Bahnhofsvorplatz
def vorplatz(b):
    """Gepflasterter Vorplatz (32 x 10 m) zwischen Suedstrasse und Empfangsgebaeude: Beete, Baenke, Laternen, Fahrradstaender, Telefonzelle, Gepaeckkarren."""
    x0, y0, x1, y1 = VORPLATZ
    z = S.Z_PLATZ
    b.add([(x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z)], [(0, 1, 2, 3)], "Pflaster")
    for xc in (140.0, 160.0):                                                                  # Beete
        b.box(xc - 2.2, 56.5 - 1.2, 0.0, xc + 2.2, 56.5 + 1.2, 0.35, "Stein alt")
        b.box(xc - 2.0, 56.5 - 1.0, 0.3, xc + 2.0, 56.5 + 1.0, 0.38, "Bruch Erde")
        for k in range(5):
            b.box(xc - 1.6 + 0.8 * k, 56.5 - 0.4 + 0.3 * (k % 2), 0.38, xc - 1.2 + 0.8 * k, 56.5 + 0.1 + 0.3 * (k % 2), 0.8 + 0.1 * (k % 3), "Laub hell")
    for xc, th in ((144.0, 0.0), (156.0, 0.0)):                                                # Baenke
        g = Lok(b, xc, 53.6, 0.0, th, 1)
        g.box(-0.9, -0.25, 0.42, 0.9, 0.25, 0.47, "Bank")
        g.box(-0.9, 0.2, 0.47, 0.9, 0.25, 0.95, "Bank")
        for sx in (-0.8, 0.8):
            g.box(sx - 0.04, -0.2, 0.0, sx + 0.04, 0.2, 0.42, "Metall")
    for xc in (136.0, 146.0, 154.0, 164.0):                                                    # Laternen
        b.box(xc - 0.06, 58.0 - 0.06, 0.0, xc + 0.06, 58.0 + 0.06, 4.2, "Metall")
        b.box(xc - 0.22, 58.0 - 0.22, 4.2, xc + 0.22, 58.0 + 0.22, 4.55, "Schild gelb")
        b.box(xc - 0.28, 58.0 - 0.28, 4.55, xc + 0.28, 58.0 + 0.28, 4.62, "Metall")
    for k in range(6):                                                                         # Fahrradstaender
        xk = 164.0 - 0.0 + 0.0
        b.box(135.0 + 0.7 * k - 0.02, 61.0, 0.0, 135.0 + 0.7 * k + 0.02, 61.0 + 1.6, 0.05, "Metall")
        b.box(135.0 + 0.7 * k - 0.02, 61.0, 0.0, 135.0 + 0.7 * k + 0.02, 61.04, 0.7, "Metall")
        b.box(135.0 + 0.7 * k - 0.02, 62.56, 0.0, 135.0 + 0.7 * k + 0.02, 62.6, 0.7, "Metall")
        b.box(135.0 + 0.7 * k - 0.02, 61.0, 0.68, 135.0 + 0.7 * k + 0.02, 62.6, 0.72, "Metall")
    g = Lok(b, 163.0, 62.0 - 3.0, 0.0, 0.0, 1)                                                # Telefonzelle
    g.box(-0.5, -0.5, 0.0, 0.5, 0.5, 0.1, "Beton")
    for (x0_, y0_, x1_, y1_) in ((-0.5, -0.5, -0.42, 0.5), (0.42, -0.5, 0.5, 0.5), (-0.5, 0.42, 0.5, 0.5), (-0.5, -0.5, -0.1, -0.42), (0.1, -0.5, 0.5, -0.42)):
        g.box(x0_, y0_, 0.1, x1_, y1_, 2.4, "Schild rot")
    g.box(-0.42, 0.40, 0.9, 0.42, 0.42, 2.2, "Glas")
    g.box(-0.5, -0.5, 2.4, 0.5, 0.5, 2.5, "Schild rot")
    g.box(-0.1, -0.5, 0.1, 0.1, -0.46, 2.2, "Glas")
    for (x, y) in ((139.0, 60.0), (141.0, 60.6)):                                              # Gepaeck
        b.box(x, y, 0.0, x + 0.8, y + 0.5, 0.45, "Ware")


# ------------------------------------------------------------------ Zusammenbau
def bauen_bahn():
    """Alle Bauten der Bahnanlage als Bau-Objekte: Gleise, Bahnhofsgebaeude, Rollmaterial."""
    gl = Bau("bahn_gleise")
    gleise(gl)
    ge = Bau("bahn_bahnhof")
    empfangsgebaeude(ge, *STATION)
    bahnsteig(ge)
    stellwerk(ge)
    gueterschuppen(ge)
    wasserturm(ge)
    vorplatz(ge)
    zg = Bau("bahn_zuege")
    zuege(zg)
    import tunnel
    return [gl, ge, zg, tunnel.bauen_tunnel()]
