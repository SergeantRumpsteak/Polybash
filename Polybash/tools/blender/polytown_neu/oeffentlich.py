"""Polybash - oeffentliche Gebaeude der Stadt (40er-Jahre-Stil, verwittert): Feuerwehr, Supermarkt (Konsum), Post, Kirche.

Alle Gebaeude sind im lokalen Koordinatensystem gebaut (Tuer/Fassade zur -y-Seite) und werden ueber stadt.Lok gedreht; Waende haben echte
Oeffnungen, die Innenraeume sind begehbar (Raster-Test in der Entwicklung). Wird von stadt.baue_alles() eingebunden."""
import math

import stadt as S
from stadt import Lok, pbox, wand, aussenwand, fensterschmuck, tuerrahmen, dach, F0, WD, TH
from burg import Bau

S.FARBEN.update({
    "Tor rot":        ((0.46, 0.10, 0.08), 0.75, 0.0),
    "Tor rot alt":    ((0.38, 0.12, 0.10), 0.9, 0.0),
    "Beton":          ((0.52, 0.51, 0.48), 0.95, 0.0),
    "Schrift weiss":  ((0.88, 0.87, 0.80), 0.7, 0.0),
    "Schrift schwarz": ((0.07, 0.07, 0.07), 0.7, 0.0),
    "Schild rot":     ((0.50, 0.10, 0.08), 0.7, 0.0),
    "Schild gelb":    ((0.82, 0.66, 0.10), 0.7, 0.0),
    "Schild gruen":   ((0.14, 0.30, 0.20), 0.7, 0.0),
    "Kachel":         ((0.80, 0.80, 0.76), 0.5, 0.0),
    "Linoleum":       ((0.46, 0.40, 0.28), 0.8, 0.0),
    "Regal":          ((0.55, 0.43, 0.28), 0.9, 0.0),
    "Ware":           ((0.70, 0.55, 0.22), 0.9, 0.0),
    "Ware rot":       ((0.62, 0.18, 0.12), 0.9, 0.0),
    "Ware blau":      ((0.22, 0.32, 0.52), 0.9, 0.0),
    "Glas":           ((0.30, 0.42, 0.46), 0.1, 0.0),
    "Dach Schiefer":  ((0.22, 0.24, 0.27), 0.8, 0.0),
    "Kreuz":          ((0.70, 0.60, 0.25), 0.4, 0.3),
    "Altar":          ((0.60, 0.58, 0.52), 0.8, 0.0),
    "Bank":           ((0.34, 0.22, 0.13), 0.9, 0.0),
    "Teppich":        ((0.45, 0.12, 0.12), 0.95, 0.0),
    "Glas bunt blau": ((0.18, 0.28, 0.62), 0.2, 0.2),
    "Glas bunt rot":  ((0.62, 0.16, 0.14), 0.2, 0.2),
    "Glas bunt gelb": ((0.80, 0.68, 0.20), 0.2, 0.2),
})
for _n in ("Dach Schiefer", "Beton", "Tor rot"):
    pass

# ------------------------------------------------------------------ Schrift (5 x 7 Pixel, aus Quadern)
FONT = {
    "A": ("01110", "10001", "10001", "11111", "10001", "10001", "10001"),
    "E": ("11111", "10000", "11110", "10000", "10000", "10000", "11111"),
    "F": ("11111", "10000", "11110", "10000", "10000", "10000", "10000"),
    "H": ("10001", "10001", "10001", "11111", "10001", "10001", "10001"),
    "K": ("10001", "10010", "10100", "11000", "10100", "10010", "10001"),
    "M": ("10001", "11011", "10101", "10101", "10001", "10001", "10001"),
    "N": ("10001", "11001", "10101", "10011", "10001", "10001", "10001"),
    "O": ("01110", "10001", "10001", "10001", "10001", "10001", "01110"),
    "P": ("11110", "10001", "10001", "11110", "10000", "10000", "10000"),
    "R": ("11110", "10001", "10001", "11110", "10100", "10010", "10001"),
    "S": ("01111", "10000", "10000", "01110", "00001", "00001", "11110"),
    "T": ("11111", "00100", "00100", "00100", "00100", "00100", "00100"),
    "U": ("10001", "10001", "10001", "10001", "10001", "10001", "01110"),
    "W": ("10001", "10001", "10001", "10101", "10101", "11011", "10001"),
    " ": ("00000",) * 7,
}


def schrift_breite(text, px):
    return (len(text) * 6 - 1) * px


def schrift(g, text, xc, z0, yface, px, mat, tiefe=0.05):
    """Schrift aus Quadern auf einer nach -y zeigenden Wand (Flaeche bei y = yface), zentriert auf x = xc, Unterkante z0."""
    x = xc - schrift_breite(text, px) / 2
    for ch in text:
        bm = FONT[ch]
        for r, row in enumerate(bm):
            for c, v in enumerate(row):
                if v == "1":
                    g.box(x + c * px, yface - tiefe, z0 + (6 - r) * px, x + (c + 1) * px, yface, z0 + (7 - r) * px, mat)
        x += 6 * px


def _tor(g, xa, xb, y_wand, hoehe, mat, glas=True):
    """Tuerfluegel (aufgeschwenkt, flach an der Fassade) von x = xa bis xb: Rahmen, gefuellte Felder, Scheiben im oberen Teil."""
    w = abs(xb - xa)
    x0, x1 = min(xa, xb), max(xa, xb)
    y0, y1 = y_wand - 0.16, y_wand - 0.07
    g.box(x0, y0, F0, x1, y1, F0 + hoehe, mat)
    rh = "Holz alt"
    g.box(x0, y0 - 0.03, F0, x0 + 0.1, y1, F0 + hoehe, rh)
    g.box(x1 - 0.1, y0 - 0.03, F0, x1, y1, F0 + hoehe, rh)
    for zz in (F0, F0 + hoehe / 2 - 0.05, F0 + hoehe - 0.1):
        g.box(x0, y0 - 0.03, zz, x1, y1, zz + 0.1, rh)
    if glas:
        for k in range(2):
            za = F0 + hoehe / 2 + 0.25 + k * 0.0
            for (ca, cb) in ((x0 + 0.2, x0 + w / 2 - 0.05), (x0 + w / 2 + 0.05, x1 - 0.2)):
                g.box(ca, y0 - 0.04, za, cb, y0, za + hoehe / 2 - 0.55, "Fenster")
            break
    for zz in (F0 + 0.6, F0 + hoehe - 0.7):                           # Beschlaege
        g.box(x0 if xa < xb else x1 - 0.25, y0 - 0.05, zz, (x0 + 0.25) if xa < xb else x1, y0, zz + 0.1, "Metall")


# ------------------------------------------------------------------ Feuerwehr
HALL = (-20.0, 14.4)               # Hallenlaenge (lokales x)
TURM_X = (14.4, 20.0)              # Turm (5,6 m) am Nordende, buendig mit der Fassade
D = 8.4
HH = 7.4                           # Traufhoehe der Halle
HT = 11.7                          # Oberkante Turmwand (Wachraum-Decke)
ZW = F0 + 8.8                      # Wachraum-Fussboden (9,0 m)
TOR_B, TOR_H = 5.6, 4.2


def feuerwehr(b, cx, cy, zb, theta, lvl=1, seed=3):
    """Feuerwehrhaus 40 x 8,4 m: grosse Halle mit drei Fluegeltoren (aufgeschwenkt), Aufschrift, Mannschafts-/Geraeteecke; am Nordende der
    Wachturm (Schlauchturm) mit gegenlaeufiger Treppe, Wachraum mit Rundumfenstern, Walmdach und Sirene. Gebaeude ueber lokale x-Achse laenger."""
    g = Lok(b, cx, cy, zb, theta, 1)
    mat = "Putz gelb alt" if lvl else "Putz gelb"
    ziegel = "Ziegel alt" if lvl else "Ziegel"
    tor = "Tor rot alt" if lvl else "Tor rot"
    xa, xb = HALL
    hl = xb - xa                                           # 34,4
    bay = hl / 3.0
    xs = [xa + bay * (k + 0.5) for k in range(3)]         # Torachsen
    # --- Halle: Aussenwaende
    oef_v = [(x - TOR_B / 2, x + TOR_B / 2, F0, F0 + TOR_H) for x in xs]
    fz_zc, fz_h = 6.45, 1.0
    win_v = [(x + dx, fz_zc) for x in xs for dx in (-1.9, 1.9)]
    oef_v += [(x - 0.55, x + 0.55, fz_zc - fz_h / 2, fz_zc + fz_h / 2) for x, _ in win_v]
    hint = [-17.0, -12.5, -8.0, -3.5, 1.0, 5.5, 10.0]
    oef_h = [(x - 0.65, x + 0.65, 3.2 - 0.7, 3.2 + 0.7) for x in hint]
    aussenwand(g, "x", -D / 2, -1, xa, xb, HH, mat, oef_v)
    aussenwand(g, "x", D / 2, 1, xa, xb, HH, mat, oef_h)
    oef_w = [(-0.55, 0.55, F0, F0 + TH), (-3.0 - 0.55, -3.0 + 0.55, 3.0, 4.2), (3.0 - 0.55, 3.0 + 0.55, 3.0, 4.2)]
    aussenwand(g, "y", xa, -1, -D / 2 + WD, D / 2 - WD, HH, mat, oef_w)                    # Westgiebel: Tuer + 2 Fenster
    oef_o = [(-1.6, -0.5, F0, F0 + TH)]
    wand(g, "y", xb - WD, xb, -D / 2 + WD, D / 2 - WD, -1.0, HH, mat, oef_o)       # Wand Halle | Turm (Durchgang)
    tuerrahmen(g, "y", xb - WD, xb, oef_o[0][0], oef_o[0][1], F0, F0 + TH)
    # Fenster mit Schmuck
    for x, zc in win_v:
        fensterschmuck(g, "x", -D / 2, -1, x, zc, 1.1, fz_h, None)
    for x in hint:
        fensterschmuck(g, "x", D / 2, 1, x, 3.2, 1.3, 1.4, None)
    for (a, _lo, zl, zh) in ((-3.0, 0, 3.0, 4.2), (3.0, 0, 3.0, 4.2)):
        fensterschmuck(g, "y", xa, -1, a, (zl + zh) / 2, 1.1, zh - zl, None)
    # Tuer im Westgiebel
    tuerrahmen(g, "y", xa - 0.07, xa, -0.55, 0.55, F0, F0 + TH)
    g.box(xa - 0.7, -0.75, -0.6, xa, 0.75, F0, "Beton")
    # --- Tore: Torrahmen aus Naturstein, Fluegel flach an der Fassade
    for x in xs:
        tuerrahmen(g, "x", -D / 2 - 0.05, -D / 2 + 0.0, x - TOR_B / 2, x + TOR_B / 2, F0, F0 + TOR_H, "Stein alt", t=0.25, v=0.02)
        g.box(x - TOR_B / 2, -D / 2 - 0.05, F0 - 0.04, x + TOR_B / 2, -D / 2 + WD, F0, "Beton")                   # Schwelle
        _tor(g, x - TOR_B / 2, x - TOR_B / 2 - TOR_B / 2, -D / 2, TOR_H, tor)
        _tor(g, x + TOR_B / 2, x + TOR_B / 2 + TOR_B / 2, -D / 2, TOR_H, tor)
    # --- Aufschrift
    sx0 = xs[1]
    g.box(sx0 - 3.9, -D / 2 - 0.06, 4.75, sx0 + 3.9, -D / 2, 5.85, "Schild rot")
    schrift(g, "FEUERWEHR", sx0, 4.95, -D / 2 - 0.06, 0.125, "Schrift weiss", 0.04)
    # --- Boden, Decke, Innenausbau
    ix0, ix1, iy0, iy1 = xa + WD, xb - WD, -D / 2 + WD, D / 2 - WD
    g.box(ix0, iy0, -0.7, ix1, iy1, F0, "Beton")
    g.box(ix0, iy0, HH - 0.25, ix1, iy1, HH, "Decke")
    for k in range(4):                                       # Spinde an der Westwand (Rueckseite)
        g.box(ix0 + 0.1 + k * 0.55, iy1 - 0.55, F0, ix0 + 0.6 + k * 0.55, iy1 - 0.05, F0 + 1.9, "Metall")
    g.box(xs[1] - 2.0, iy1 - 0.8, F0, xs[1] + 1.0, iy1 - 0.05, F0 + 0.9, "Holz")                              # Werkbank
    g.box(xs[1] - 2.0, iy1 - 0.1, F0 + 0.9, xs[1] + 1.0, iy1 - 0.05, F0 + 2.2, "Regal")                       # Werkzeugwand
    g.box(xs[2] - 1.0, iy1 - 0.9, F0, xs[2] + 1.0, iy1 - 0.05, F0 + 0.3, "Regal")                              # Schlauchpritsche
    for k in range(5):
        g.prism(xs[2] - 0.8 + 0.4 * k, iy1 - 0.45, F0 + 0.3, 0.17, 0.5, 8, "Ware rot")                       # aufgerollte Schlaeuche
    g.box(xs[0] - 1.5, iy1 - 0.35, F0 + 2.0, xs[0] + 1.5, iy1 - 0.05, F0 + 2.1, "Metall")                       # Leiterhalter
    g.box(xs[0] - 1.5, iy1 - 0.3, F0 + 2.1, xs[0] + 1.5, iy1 - 0.15, F0 + 2.2, "Holz alt")                      # Steckleiter
    # --- Dach der Halle
    gh = Lok(b, cx + (xa + hl / 2) * math.cos(theta), cy + (xa + hl / 2) * math.sin(theta), zb, theta, 1)
    dach(gh, "x", hl, D, HH, 2.5, ziegel, mat, e=0.5)
    # --- Turm (Wachturm): lokale Mitte (tx, ty)
    tx = (TURM_X[0] + TURM_X[1]) / 2
    ty = -D / 2 + 2.8
    t0, t1 = TURM_X
    y0t, y1t = -D / 2, -D / 2 + 5.6
    ti0, ti1, tj0, tj1 = t0 + WD, t1 - WD, y0t + WD, y1t - WD
    win_t = []
    for (ach, aussen, sg, a_c) in (("x", y0t, -1, (tx - 1.15, tx + 1.15)), ("x", y1t, 1, (tx - 1.15, tx + 1.15)), ("y", t1, 1, (ty - 1.15, ty + 1.15)),
                                   ("y", t0, -1, (ty - 1.15, ty + 1.15))):
        for a in a_c:
            win_t.append((ach, aussen, sg, a, ZW + 1.65))
    schlitz = [(ty, 3.4), (ty, 5.6), (ty, 7.8)]
    ot_v = [(tx - 2.15 + 0.0, tx - 1.05, F0, F0 + TH)] + [(a - 0.8, a + 0.8, ZW + 1.0, ZW + 2.3) for a in (tx - 1.15, tx + 1.15)]
    ot_h = [(a - 0.8, a + 0.8, ZW + 1.0, ZW + 2.3) for a in (tx - 1.15, tx + 1.15)]
    ot_e = [(a - 0.8, a + 0.8, ZW + 1.0, ZW + 2.3) for a in (ty - 1.15, ty + 1.15)] + [(ty - 0.35, ty + 0.35, zc - 0.5, zc + 0.5) for _, zc in schlitz]
    ot_w = [(a - 0.8, a + 0.8, ZW + 1.0, ZW + 2.3) for a in (ty - 1.15, ty + 1.15)] + [(-1.6, -0.5, F0, F0 + TH)]
    aussenwand(g, "x", y0t, -1, t0, t1, HT, mat, ot_v)
    aussenwand(g, "x", y1t, 1, t0, t1, HT, mat, ot_h)
    aussenwand(g, "y", t1, 1, y0t + WD, y1t - WD, HT, mat, ot_e)
    aussenwand(g, "y", t0 + 0.3, -1, y0t + WD, y1t - WD, HT, mat, ot_w, sockel=False)
    for a in (tx - 1.15, tx + 1.15):
        fensterschmuck(g, "x", y0t, -1, a, ZW + 1.65, 1.6, 1.3, None)
        fensterschmuck(g, "x", y1t, 1, a, ZW + 1.65, 1.6, 1.3, None)
    for a in (ty - 1.15, ty + 1.15):
        fensterschmuck(g, "y", t1, 1, a, ZW + 1.65, 1.6, 1.3, None)
        fensterschmuck(g, "y", t0 + 0.3, -1, a, ZW + 1.65, 1.6, 1.3, None)
    for _, zc in schlitz:
        fensterschmuck(g, "y", t1, 1, ty, zc, 0.7, 1.0, None)
    tuerrahmen(g, "x", y0t - 0.07, y0t, ot_v[0][0], ot_v[0][1], F0, F0 + TH)                   # Turmtuer (Personal)
    g.box(ot_v[0][0], y0t - 0.05, F0 - 0.04, ot_v[0][1], y0t + WD, F0, "Beton")
    g.box(ot_v[0][0] - 0.3, y0t - 0.8, -0.6, ot_v[0][1] + 0.3, y0t - 0.07, F0, "Beton")
    g.box(ot_v[0][0] - 0.1, y0t - 0.12, 2.75, ot_v[0][1] + 0.1, y0t, 2.87, "Dach grau alt")
    # Durchgang Turm <-> Halle (Turmseite)
    wand(g, "y", t0, t0 + 0.3, tj0, tj1, -1.0, HT, mat, [(-1.6, -0.5, F0, F0 + TH)])
    # Turmboden, Zwischenboeden (nur der Wachraum-Boden), Wachraumdecke
    g.box(ti0 + 0.3, tj0, -0.7, ti1, tj1, F0, "Beton")
    ti0 += 0.3
    # Wachraum-Boden: y > -1.6 durchgehend, Westlandung (x < ti0 + 1.0)
    ylane0, ylane1 = tj0, tj0 + 2.3                              # Treppenbereich y: tj0 .. tj0+2.3 (Spur A, Spur B)
    def platte(x0, y0, x1, y1, z, mat1="Dielen"):
        g.box(x0, y0, z - 0.25, x1, y1, z - 0.05, "Decke")
        g.box(x0, y0, z - 0.05, x1, y1, z, mat1)
    platte(ti0, ylane1, ti1, tj1, ZW)
    platte(ti0, tj0, ti0 + 1.0, ylane1, ZW)
    g.box(ti0, tj0, HT - 0.25, ti1, tj1, HT, "Decke")
    # Treppe: Spur A (y tj0 .. tj0+1.1), Spur B (y tj0+1.2 .. tj0+2.3); 11 Stufen je 0,27 m, Steigung 0,2
    la, lb = (tj0, tj0 + 1.1), (tj0 + 1.2, ylane1)
    xw = ti0 + 1.0                                               # westliches Ende der Laeufe
    xe = xw + 11 * 0.27                                           # oestliches Ende (Landung dahinter)
    z = F0
    for fl in range(4):
        lane = la if fl % 2 == 0 else lb
        for k in range(11):
            zt = z + 0.2 * (k + 1)
            if fl % 2 == 0:
                xx0 = xw + 0.27 * k
            else:
                xx0 = xe - 0.27 * (k + 1)
            g.box(xx0, lane[0], zt - 0.1, xx0 + 0.27, lane[1], zt, "Holz")
            # Gelaender: zwischen den Spuren (y = tj0+1.1 .. 1.2) und zur Schachtseite (y = ylane1)
            for yy in (tj0 + 1.1, ylane1 - 0.06):
                if yy == ylane1 - 0.06 and fl % 2 == 0:
                    continue
                if yy == tj0 + 1.1:
                    g.box(xx0, yy, zt + 0.45, xx0 + 0.27, yy + 0.1, zt + 0.5, "Holz")
                    g.box(xx0, yy, zt + 0.92, xx0 + 0.27, yy + 0.1, zt + 0.97, "Holz")
                else:
                    g.box(xx0, yy, zt + 0.45, xx0 + 0.27, yy + 0.05, zt + 0.5, "Holz")
                    g.box(xx0, yy, zt + 0.92, xx0 + 0.27, yy + 0.05, zt + 0.97, "Holz")
            if fl % 2 == 0 and k % 3 == 0:
                g.box(xx0 + 0.1, tj0 + 1.1, zt, xx0 + 0.17, tj0 + 1.17, zt + 0.97, "Holz")
        z += 2.2
        # Landung am Ende des Laufs
        if fl % 2 == 0:
            platte(xe, tj0, ti1, ylane1, z, "Holz")                                  # Ostlandung
            g.box(xe, ylane1 - 0.06, z + 0.45, ti1, ylane1 - 0.01, z + 0.5, "Holz")
            g.box(xe, ylane1 - 0.06, z + 0.92, ti1, ylane1 - 0.01, z + 0.97, "Holz")
        elif fl == 1:
            platte(ti0, tj0, xw, ylane1, z, "Holz")                                  # Westlandung auf 4,6 m
            g.box(ti0, ylane1 - 0.06, z + 0.45, xw, ylane1 - 0.01, z + 0.5, "Holz")
            g.box(ti0, ylane1 - 0.06, z + 0.92, xw, ylane1 - 0.01, z + 0.97, "Holz")
    # Gelaender am Schacht des Wachraums (Nordkante der Spuren) und quer ueber Spur A am Westende
    for (x0, y0, x1, y1) in ((xw, ylane1 - 0.06, ti1, ylane1 - 0.01), (xw - 0.06, tj0, xw - 0.01, tj0 + 1.1)):
        g.box(x0, y0, ZW + 0.45, x1, y1, ZW + 0.5, "Holz")
        g.box(x0, y0, ZW + 0.92, x1, y1, ZW + 0.97, "Holz")
    # Wachraum-Moebel
    g.box(ti1 - 0.8, ylane1 + 0.3, ZW, ti1 - 0.1, ylane1 + 1.4, ZW + 0.8, "Holz")                       # Tisch mit Funkgeraet
    g.box(ti1 - 0.7, ylane1 + 0.4, ZW + 0.8, ti1 - 0.3, ylane1 + 0.9, ZW + 1.0, "Metall")
    g.box(ti0 + 0.2, tj1 - 0.5, ZW, ti0 + 1.6, tj1 - 0.1, ZW + 0.45, "Holz")                            # Bank
    # Dach des Turms (Zeltdach) + Sirene
    gt = Lok(b, *g.P((tx, ty, 0.0))[:2], zb, theta, 1)
    gt.zb = zb
    rz = dach(gt, "walm", 5.6, 5.6, HT, 3.4, ziegel, mat, e=0.55)
    za = HT + 3.4
    g.box(tx - 0.05, ty - 0.05, za, tx + 0.05, ty + 0.05, za + 0.8, "Metall")
    g.box(tx - 0.4, ty - 0.4, za + 0.8, tx + 0.4, ty + 0.4, za + 1.3, "Metall")                         # Sirenenmotor
    for k in range(4):                                                                              # Sirenenhorn
        a = k * math.pi / 2
        g.box(tx + math.cos(a) * 0.55 - 0.15, ty + math.sin(a) * 0.55 - 0.15, za + 0.95, tx + math.cos(a) * 0.55 + 0.15, ty + math.sin(a) * 0.55 + 0.15, za + 1.2, "Metall")
    # Anbau hinter dem Turm (massiver Block mit Flachdach, Geraeteschuppen)
    g.box(t0, y1t, -1.0, t1, D / 2, 3.4, mat)
    g.box(t0 - 0.1, y1t, 3.4, t1 + 0.1, D / 2 + 0.1, 3.6, "Dach grau alt")
    return g


# ------------------------------------------------------------------ Supermarkt (Konsum)
def _flaeche_quad(g, pts, richtung, mat):
    g.poly(pts, richtung, mat)
    g.poly(pts[::-1], tuple(-v for v in richtung), mat)


def supermarkt(b, cx, cy, zb, theta, lvl=1):
    """Konsum-Laden 12 x 9 m: Flachdach mit Attika, drei Schaufenster, Doppeltuer (nach innen aufgeschwenkt), gestreifte Markise, Schriftzug KONSUM,
    Lieferanten- und Seitentuer. Innen: Regalwaende, zwei Regalinseln, Kasse, Kuehltruhe - alles begehbar. Tuer bei lokalem x = +3,8."""
    g = Lok(b, cx, cy, zb, theta, 1)
    w, d, H = 12.0, 9.0, 4.8
    hw, hd = w / 2, d / 2
    mat = "Putz sand alt" if lvl else "Putz sand"
    sch = [-4.2, -1.6, 1.0]
    oef_v = [(x - 1.2, x + 1.2, F0 + 0.55, F0 + 2.75) for x in sch] + [(2.9, 4.7, F0, F0 + 2.5)]
    oef_h = [(-4.2, -2.8, F0, F0 + 2.4)] + [(x - 0.6, x + 0.6, F0 + 2.0, F0 + 3.0) for x in (0.0, 3.5)]
    oef_w = [(y - 0.6, y + 0.6, F0 + 1.0, F0 + 2.4) for y in (-1.5, 1.5)]
    oef_o = [(1.9, 3.0, F0, F0 + 2.3), (-2.1, -0.9, F0 + 1.0, F0 + 2.4)]
    aussenwand(g, "x", -hd, -1, -hw, hw, H, mat, oef_v)
    aussenwand(g, "x", hd, 1, -hw, hw, H, mat, oef_h)
    aussenwand(g, "y", -hw, -1, -hd + WD, hd - WD, H, mat, oef_w)
    aussenwand(g, "y", hw, 1, -hd + WD, hd - WD, H, mat, oef_o)
    for x in sch:
        fensterschmuck(g, "x", -hd, -1, x, F0 + 1.65, 2.4, 2.2, None)
    for a in (0.0, 3.5):
        fensterschmuck(g, "x", hd, 1, a, F0 + 2.5, 1.2, 1.0, None)
    for y in (-1.5, 1.5):
        fensterschmuck(g, "y", -hw, -1, y, F0 + 1.7, 1.2, 1.4, None)
    fensterschmuck(g, "y", hw, 1, -1.5, F0 + 1.7, 1.2, 1.4, None)
    # Tueren: Eingang (Doppeltuer, Fluegel innen), Lieferanten-Tuer hinten, Seitentuer Ost
    tuerrahmen(g, "x", -hd - 0.07, -hd, 2.9, 4.7, F0, F0 + 2.5)
    g.box(2.9, -hd - 0.05, F0 - 0.04, 4.7, -hd + WD, F0, "Beton")
    g.box(2.9, -hd + WD, F0, 2.95, -hd + WD + 0.85, F0 + 2.4, "Tuer gruen")
    g.box(4.65, -hd + WD, F0, 4.7, -hd + WD + 0.85, F0 + 2.4, "Tuer gruen")
    g.box(2.95, -hd - 0.02, F0 + 1.0, 4.65, -hd, F0 + 2.4, "Glas")
    g.box(2.7, -hd - 1.6, -0.6, 4.9, -hd - 0.07, F0, "Beton")
    tuerrahmen(g, "x", hd, hd + 0.07, -4.2, -2.8, F0, F0 + 2.4)
    g.box(-4.4, hd, -0.6, -2.6, hd + 1.2, F0 + 0.1, "Beton")                                                       # Laderampe
    g.box(-4.2, hd - 0.06, F0, -3.5, hd, F0 + 2.3, "Tuer grau")                                                    # Lieferantentuer (halb offen)
    tuerrahmen(g, "y", hw, hw + 0.07, 1.9, 3.0, F0, F0 + 2.3)
    g.box(hw, 1.9, -0.6, hw + 0.9, 3.0, F0, "Beton")
    # Schild und Markise
    g.box(-5.6, -hd - 0.12, 3.5, 2.8, -hd, 4.55, "Schild gruen")
    schrift(g, "KONSUM", -1.4, 3.62, -hd - 0.12, 0.12, "Schrift weiss", 0.04)
    for k in range(10):
        xa = -5.7 + 0.86 * k
        pts = [(xa, -hd - 0.1, 3.35), (xa + 0.86, -hd - 0.1, 3.35), (xa + 0.86, -hd - 1.5, 2.85), (xa, -hd - 1.5, 2.85)]
        _flaeche_quad(g, pts, (0.0, -0.5, 1.0), "Markt rot" if k % 2 == 0 else "Markt weiss")
        g.box(xa, -hd - 1.52, 2.62, xa + 0.86, -hd - 1.48, 2.88, "Markt rot" if k % 2 == 0 else "Markt weiss")
    for xx in (-5.7, 2.9):
        g.box(xx, -hd - 1.4, 2.8, xx + 0.05, -hd - 0.1, 2.85, "Metall")
    # Flachdach mit Attika, Lichtkuppel, Lueftung
    g.box(-hw - 0.15, -hd - 0.15, H, hw + 0.15, hd + 0.15, H + 0.18, "Dach Schiefer")
    for (x0, y0, x1, y1) in ((-hw - 0.15, -hd - 0.15, hw + 0.15, -hd + 0.1), (-hw - 0.15, hd - 0.1, hw + 0.15, hd + 0.15),
                             (-hw - 0.15, -hd - 0.15, -hw + 0.1, hd + 0.15), (hw - 0.1, -hd - 0.15, hw + 0.15, hd + 0.15)):
        g.box(x0, y0, H + 0.18, x1, y1, H + 0.85, mat)
        g.box(x0 - 0.04, y0 - 0.04, H + 0.85, x1 + 0.04, y1 + 0.04, H + 0.95, "Stein alt")
    g.box(-1.5, -1.0, H + 0.18, 1.5, 1.0, H + 0.7, "Glas")
    g.box(3.0, 1.5, H + 0.18, 3.6, 2.1, H + 1.2, "Metall")
    if lvl:
        for (xa, ya, xb, yb) in ((-4.0, 1.0, -2.6, 2.2), (2.0, -2.5, 3.5, -1.4)):
            g.poly([(xa, ya, H + 0.2), (xb, ya, H + 0.2), (xb, yb, H + 0.2), (xa, yb, H + 0.2)], (0, 0, 1), "Pappe")
    # Innenraum: Boden, Decke, Regale, Kasse
    ix0, ix1, iy0, iy1 = -hw + WD, hw - WD, -hd + WD, hd - WD
    g.box(ix0, iy0, -0.7, ix1, iy1, F0, "Linoleum")
    g.box(ix0, iy0, H - 0.25, ix1, iy1, H, "Decke")
    goods = ("Ware", "Ware rot", "Ware blau", "Ware")

    def regal(x0, y0, x1, y1, h=1.9):
        g.box(x0, y0, F0, x1, y1, F0 + 0.12, "Regal")
        for k in range(1, 5):
            g.box(x0, y0, F0 + 0.12 + k * (h - 0.12) / 4 - 0.04, x1, y1, F0 + 0.12 + k * (h - 0.12) / 4, "Regal")
        lang = max(x1 - x0, y1 - y0)
        n = int(lang / 0.45)
        for k in range(n):
            for lv in range(4):
                za = F0 + 0.12 + lv * (h - 0.12) / 4
                zz = za + 0.08 + 0.18 * ((k + lv) % 3) / 2
                if x1 - x0 > y1 - y0:
                    g.box(x0 + 0.05 + k * 0.45, y0 + 0.05, za, x0 + 0.40 + k * 0.45, y1 - 0.05, zz, goods[(k + lv) % 4])
                else:
                    g.box(x0 + 0.05, y0 + 0.05 + k * 0.45, za, x1 - 0.05, y0 + 0.40 + k * 0.45, zz, goods[(k + lv) % 4])
    regal(-2.0, iy1 - 0.5, ix1 - 0.2, iy1 - 0.02, 2.1)                 # Rueckwand
    regal(ix0 + 0.02, -3.0, ix0 + 0.5, 2.4, 2.1)                       # Westwand
    regal(-3.4, 1.5, 0.4, 2.0, 1.6)                                    # Inseln
    regal(-3.4, -0.1, 0.4, 0.4, 1.6)
    g.box(0.6, -2.6, F0, 3.2, -1.8, F0 + 1.0, "Holz")                  # Kasse
    g.box(0.8, -2.4, F0 + 1.0, 1.4, -2.0, F0 + 1.35, "Metall")
    g.box(ix1 - 0.9, -1.2, F0, ix1 - 0.05, 1.8, F0 + 0.9, "Kachel")    # Kuehltruhe
    g.box(ix1 - 0.85, -1.15, F0 + 0.9, ix1 - 0.1, 1.75, F0 + 0.98, "Glas")
    g.box(3.6, 1.2, F0, 4.0, 1.6, F0 + 0.7, "Metall")                  # Einkaufskorb-Staender
    for k in range(3):
        g.box(-0.9 + k * 0.25, iy1 - 1.1, H - 0.45, -0.7 + k * 0.25, iy1 - 0.9, H - 0.25, "Metall")
    return g


# ------------------------------------------------------------------ Post
def post(b, cx, cy, zb, theta, lvl=1):
    """Postamt 11 x 9 m, zwei Geschosse (EG begehbar): Portal mit Schriftzug POST, Posthorn-Schild, gelber Briefkasten, Walmdach mit Kamin.
    Innen: Schalterhalle mit Wartebaenken und Schreibpult, Schalterwand mit drei Schaltern, Dienstraum mit Paketregal. Tuer in der Mitte (x = 0)."""
    g = Lok(b, cx, cy, zb, theta, 1)
    w, d = 11.0, 9.0
    hw, hd = w / 2, d / 2
    ZE = F0 + 3.6                                              # Decke EG
    H = ZE + 0.25 + 3.0                                        # Traufe
    mat = "Putz gelb alt" if lvl else "Putz gelb"
    ziegel = "Ziegel alt" if lvl else "Ziegel"
    zc_u = ZE + 0.25 + 1.6
    oef_v = [(-0.95, 0.95, F0, F0 + 2.9)] + [(x - 0.7, x + 0.7, F0 + 0.8, F0 + 2.7) for x in (-3.5, 3.5, -1.0 - 3.0 * 0, 0)][:2]
    oef_v += [(x - 0.55, x + 0.55, zc_u - 0.8, zc_u + 0.8) for x in (-4.0, -2.0, 0.0, 2.0, 4.0)]
    oef_h = [(x - 0.65, x + 0.65, F0 + 0.9, F0 + 2.7) for x in (-4.0, -1.8, 0.4)] + [(3.0, 4.1, F0, F0 + 2.3)]
    oef_h += [(x - 0.55, x + 0.55, zc_u - 0.8, zc_u + 0.8) for x in (-4.0, -2.0, 0.0, 2.0, 4.0)]
    oef_w = [(y - 0.6, y + 0.6, F0 + 0.9, F0 + 2.7) for y in (-1.8, 1.8)] + [(y - 0.55, y + 0.55, zc_u - 0.8, zc_u + 0.8) for y in (-1.8, 1.8)]
    oef_o = [(-0.55, 0.55, F0, F0 + 2.3)] + [(y - 0.55, y + 0.55, zc_u - 0.8, zc_u + 0.8) for y in (-1.8, 1.8)]
    aussenwand(g, "x", -hd, -1, -hw, hw, H, mat, oef_v)
    aussenwand(g, "x", hd, 1, -hw, hw, H, mat, oef_h)
    aussenwand(g, "y", -hw, -1, -hd + WD, hd - WD, H, mat, oef_w)
    aussenwand(g, "y", hw, 1, -hd + WD, hd - WD, H, mat, oef_o)
    for x in (-3.5, 3.5):
        fensterschmuck(g, "x", -hd, -1, x, F0 + 1.75, 1.4, 1.9, "Laden gruen alt" if lvl else "Laden gruen")
    for x in (-4.0, -2.0, 0.0, 2.0, 4.0):
        fensterschmuck(g, "x", -hd, -1, x, zc_u, 1.1, 1.6, None)
        fensterschmuck(g, "x", hd, 1, x, zc_u, 1.1, 1.6, None)
    for x in (-4.0, -1.8, 0.4):
        fensterschmuck(g, "x", hd, 1, x, F0 + 1.8, 1.3, 1.8, None)
    for y in (-1.8, 1.8):
        fensterschmuck(g, "y", -hw, -1, y, F0 + 1.8, 1.2, 1.8, None)
        fensterschmuck(g, "y", -hw, -1, y, zc_u, 1.1, 1.6, None)
        fensterschmuck(g, "y", hw, 1, y, zc_u, 1.1, 1.6, None)
    # Portal: Pilaster, Gebaelk, Schild POST, Doppeltuer aufgeschwenkt, zwei Stufen
    tuerrahmen(g, "x", -hd - 0.07, -hd, -0.95, 0.95, F0, F0 + 2.9, "Stein alt", t=0.15)
    g.box(-0.95, -hd - 0.05, F0 - 0.04, 0.95, -hd + WD, F0, "Beton")
    for sx in (-1, 1):
        g.box(sx * 1.4 - 0.2, -hd - 0.3, F0, sx * 1.4 + 0.2, -hd, F0 + 3.2, "Stein alt")
        g.box(sx * 1.4 - 0.27, -hd - 0.36, F0, sx * 1.4 + 0.27, -hd, F0 + 0.3, "Stein alt")
        g.box(sx * 1.4 - 0.27, -hd - 0.36, F0 + 2.9, sx * 1.4 + 0.27, -hd, F0 + 3.2, "Stein alt")
        g.box(sx * 0.95 - (0.0 if sx < 0 else 0.05), -hd + WD, F0, sx * 0.95 + (0.05 if sx < 0 else 0.0), -hd + WD + 0.9, F0 + 2.8, "Tuer")
    g.box(-1.9, -hd - 0.4, F0 + 3.2, 1.9, -hd, F0 + 3.55, "Stein alt")
    g.box(-1.8, -hd - 0.1, F0 + 3.6, 1.8, -hd, F0 + 4.5, "Schild gelb")
    schrift(g, "POST", 0.0, F0 + 3.78, -hd - 0.1, 0.12, "Schrift schwarz", 0.04)
    g.box(-1.9, -hd - 1.5, -0.6, 1.9, -hd - 0.7, 0.1, "Beton")
    g.box(-1.9, -hd - 0.7, -0.6, 1.9, -hd - 0.07, F0, "Beton")
    # Posthorn-Schild (rund) neben dem Portal und gelber Briefkasten
    n = 14
    P = [(-4.9 + 0.5 * math.cos(2 * math.pi * k / n), -hd - 0.08, F0 + 2.6 + 0.5 * math.sin(2 * math.pi * k / n)) for k in range(n)]
    g.poly(P, (0.0, -1.0, 0.0), "Schild gelb")
    g.box(-5.1, -hd - 0.12, F0 + 2.45, -4.7, -hd - 0.08, F0 + 2.75, "Schrift schwarz")
    g.box(-4.95, -hd - 0.12, F0 + 2.2, -4.85, -hd - 0.08, F0 + 2.6, "Schrift schwarz")
    g.box(2.3, -hd - 0.9, 0.0, 2.8, -hd - 0.5, 1.1, "Schild gelb")
    g.prism(2.55, -hd - 0.7, 1.1, 0.24, 0.12, 10, "Schild gelb")
    g.box(2.35, -hd - 0.92, 0.55, 2.75, -hd - 0.9, 0.65, "Schrift schwarz")
    # Seitentuer + Dienstzugang hinten
    tuerrahmen(g, "x", hd, hd + 0.07, 3.0, 4.1, F0, F0 + 2.3)
    g.box(2.8, hd, -0.6, 4.3, hd + 1.0, F0, "Beton")
    tuerrahmen(g, "y", hw, hw + 0.07, -0.55, 0.55, F0, F0 + 2.3)
    g.box(hw, -0.7, -0.6, hw + 0.9, 0.7, F0, "Beton")
    # Boden, Decke EG, Decke OG
    ix0, ix1, iy0, iy1 = -hw + WD, hw - WD, -hd + WD, hd - WD
    g.box(ix0, iy0, -0.7, ix1, iy1, F0, "Linoleum")
    g.box(ix0, iy0, ZE, ix1, iy1, ZE + 0.25, "Decke")
    g.box(ix0, iy0, H - 0.25, ix1, iy1, H, "Decke")
    # Schalterwand bei y = 0.8: Theke, Glasaufsatz mit drei Schalteroeffnungen, Durchgang (Klappe) bei x 4.0 .. 5.0
    g.box(ix0, 0.6, F0, 3.95, 1.0, F0 + 1.15, "Holz")
    g.box(ix0, 0.55, F0 + 1.15, 3.95, 1.05, F0 + 1.22, "Holz alt")
    sal = [(x - 0.4, x + 0.4, F0 + 1.45, F0 + 2.1) for x in (-3.4, -0.9, 1.6)]
    wand(g, "x", 0.74, 0.86, ix0, 3.95, F0 + 1.22, F0 + 2.6, "Glas", sal)
    g.box(ix0, 0.68, F0 + 2.6, 3.95, 0.92, F0 + 2.75, "Holz")
    for xx in (ix0, -2.1, 0.4, 2.8, 3.8):
        g.box(xx, 0.68, F0 + 1.22, xx + 0.12, 0.92, F0 + 2.75, "Holz")
    # Schalterhalle: Wartebaenke, Schreibpult, Briefkastenwand, Aushaenge
    for yy in (-3.2, -1.6):
        g.box(ix0 + 0.1, yy - 0.25, F0, ix0 + 0.6, yy + 0.25, F0 + 0.45, "Bank")
        g.box(ix0 + 0.1, yy - 0.25, F0 + 0.45, ix0 + 0.18, yy + 0.25, F0 + 0.95, "Bank")
    g.box(-1.5, -2.9, F0, 0.3, -2.4, F0 + 1.05, "Holz")
    g.box(-1.5, -2.9, F0 + 1.05, 0.3, -2.4, F0 + 1.15, "Holz alt")
    for k in range(6):
        g.box(ix1 - 0.4, -3.6 + k * 0.5, F0 + 0.4, ix1 - 0.02, -3.2 + k * 0.5, F0 + 2.0, "Schild gelb" if k % 2 == 0 else "Metall")
    g.box(ix0 + 0.02, -0.9, F0 + 1.2, ix0 + 0.1, 0.3, F0 + 2.2, "Schild rot")
    # Dienstraum: Schreibtische, Paketregal, Postsaecke
    g.box(-4.6, 2.4, F0, -2.8, 3.1, F0 + 0.8, "Holz")
    g.box(0.0, 2.4, F0, 1.8, 3.1, F0 + 0.8, "Holz")
    g.box(ix0 + 0.1, iy1 - 0.5, F0, 2.8, iy1 - 0.05, F0 + 2.0, "Regal")
    for k in range(7):
        g.box(ix0 + 0.15 + k * 0.5, iy1 - 0.45, F0 + 0.1 + (k % 3) * 0.6, ix0 + 0.55 + k * 0.5, iy1 - 0.1, F0 + 0.6 + (k % 3) * 0.6, ("Ware", "Ware rot", "Ware blau")[k % 3])
    g.prism(4.3, 3.0, F0, 0.35, 0.9, 8, "Ware blau")
    g.prism(3.7, 2.2, F0, 0.3, 0.8, 8, "Ware blau")
    # Dach (Walmdach) + Kamin
    rz = dach(g, "walm", w, d, H, 3.2, ziegel, mat, e=0.55)
    g.box(-2.6, -0.4, H - 0.1, -1.9, 0.4, rz(-2.2, 0) + 0.9, "Klinker alt" if lvl else "Klinker")
    g.box(-2.7, -0.5, rz(-2.2, 0) + 0.9, -1.8, 0.5, rz(-2.2, 0) + 1.02, "Stein")
    return g


# ------------------------------------------------------------------ Kirche
def _spitzbogen(a, br, z0):
    """Gestufte Spitzbogen-Oeffnung um die Achse a: Liste (alo, ahi, zlo, zhi) mit drei Stufen (br = Breite unten, z0 = Kaempfer)."""
    return [(a - br / 2, a + br / 2, z0[0], z0[1]), (a - br * 0.38, a + br * 0.38, z0[1], z0[1] + 0.8), (a - br * 0.2, a + br * 0.2, z0[1] + 0.8, z0[1] + 1.3)]


def kirche(b, cx, cy, zb, theta, lvl=1):
    """Kirche 10,6 x 26 m: Turm mit Vorhalle/Hauptportal an der Strassenseite (lokal y = -13), Kirchenschiff mit vier Spitzbogenfenstern je Seite
    (Buntglas), Strebepfeiler, Chor mit Dreifachlanzette, Satteldaecher aus Schiefer, Turm mit Uhr, Schallluken und Spitzhelm mit Kreuz.
    Innen begehbar: Vorhalle, Schiff mit Kirchenbaenken und Mittelgang, Chorstufen, Altar, Kanzel, Taufstein. Turm oben geschlossen."""
    g = Lok(b, cx, cy, zb, theta, 1)
    mat = "Putz weiss alt" if lvl else "Putz weiss"
    stein = "Stein alt" if lvl else "Stein"
    H, H2, HT_ = F0 + 6.6, F0 + 5.6, F0 + 13.8
    nx = 5.3                       # halbe Schiffbreite
    yv, yn, yc = -13.0, -7.0, 8.0  # Turmfront, Schiffsbeginn, Chorbeginn
    ye = 13.0
    tw = 3.0                       # halbe Turmbreite
    cw = 3.3                       # halbe Chorbreite
    buntg = ("Glas bunt blau", "Glas bunt rot", "Glas bunt gelb")
    # ---- Schiff: Seitenwaende mit je 4 Spitzbogenfenstern
    fy = [-4.4, -1.5, 1.4, 4.3]
    oef_s = [o for a in fy for o in _spitzbogen(a, 1.4, (F0 + 1.9, F0 + 4.3))]
    aussenwand(g, "y", nx, 1, yn, yc, H, mat, oef_s)
    aussenwand(g, "y", -nx, -1, yn, yc, H, mat, oef_s)
    for sg in (1, -1):
        for a in fy:
            for k, (lo, hi, zl, zh) in enumerate(_spitzbogen(a, 1.4, (F0 + 1.9, F0 + 4.3))):
                p0, p1 = sorted((sg * (nx - 0.17), sg * (nx - 0.13)))
                pbox(g, "y", lo, hi, p0, p1, zl, zh, buntg[(fy.index(a) + k + (sg > 0)) % 3])
                if k == 0:
                    pbox(g, "y", lo - 0.08, lo, sorted((sg * nx, sg * (nx + 0.05)))[0], sorted((sg * nx, sg * (nx + 0.05)))[1], zl - 0.06, zh + 0.5, stein)
                    pbox(g, "y", hi, hi + 0.08, sorted((sg * nx, sg * (nx + 0.05)))[0], sorted((sg * nx, sg * (nx + 0.05)))[1], zl - 0.06, zh + 0.5, stein)
            pbox(g, "y", a - 0.8, a + 0.8, *sorted((sg * nx, sg * (nx + 0.18))), F0 + 1.8, F0 + 1.9, stein)             # Fensterbank
        for ys in (-6.0, -3.0, 0.0, 3.0, 6.0):                                                                          # Strebepfeiler
            pbox(g, "y", ys - 0.3, ys + 0.3, *sorted((sg * nx, sg * (nx + 0.5))), -0.6, F0 + 3.4, stein)
            pbox(g, "y", ys - 0.22, ys + 0.22, *sorted((sg * nx, sg * (nx + 0.3))), F0 + 3.4, F0 + 5.4, stein)
            pbox(g, "y", ys - 0.26, ys + 0.26, *sorted((sg * (nx + 0.05), sg * (nx + 0.34))), F0 + 5.4, F0 + 5.55, stein)
    # ---- Rueckwand Schiff mit Chorbogen, Frontwand Schiff mit Bogen zur Vorhalle
    bog_c = _spitzbogen(0.0, 3.6, (F0, F0 + 3.6))
    wand(g, "x", yc, yc + WD, -nx + WD, nx - WD, -1.0, H, mat, bog_c)
    bog_v = _spitzbogen(0.0, 2.8, (F0, F0 + 3.0))
    wand(g, "x", yn, yn + WD, -nx + WD, nx - WD, -1.0, H, mat, bog_v)
    # ---- Chor
    oef_c = [o for a in (10.5,) for o in _spitzbogen(a, 1.0, (F0 + 1.8, F0 + 3.6))]
    aussenwand(g, "y", cw, 1, yc, ye, H2, mat, oef_c)
    aussenwand(g, "y", -cw, -1, yc, ye, H2, mat, oef_c)
    lanz = [o for a in (-1.8, 0.0, 1.8) for o in _spitzbogen(a, 0.9, (F0 + 1.8, F0 + 3.7))]
    aussenwand(g, "x", ye, 1, -cw, cw, H2, mat, lanz)
    for sg in (1, -1):
        for k, (lo, hi, zl, zh) in enumerate(_spitzbogen(10.5, 1.0, (F0 + 1.8, F0 + 3.6))):
            pbox(g, "y", lo, hi, *sorted((sg * (cw - 0.17), sg * (cw - 0.13))), zl, zh, buntg[(k + 1) % 3])
    for ai, a in enumerate((-1.8, 0.0, 1.8)):
        for k, (lo, hi, zl, zh) in enumerate(_spitzbogen(a, 0.9, (F0 + 1.8, F0 + 3.7))):
            pbox(g, "x", lo, hi, ye - 0.17, ye - 0.13, zl, zh, buntg[(ai + k) % 3])
    for sg in (1, -1):
        for ys in (yc + 0.3, ye - 0.3):                                                                                 # Chor-Strebepfeiler
            pbox(g, "y", ys - 0.25, ys + 0.25, *sorted((sg * cw, sg * (cw + 0.45))), -0.6, F0 + 4.2, stein)
    g.box(-cw - 0.45, ye - 0.15, -0.6, -cw + 0.1, ye + 0.45, F0 + 4.2, stein)
    g.box(cw - 0.1, ye - 0.15, -0.6, cw + 0.45, ye + 0.45, F0 + 4.2, stein)
    # ---- Boden, Decken
    g.box(-nx + WD, yn + WD, -0.7, nx - WD, yc + WD, F0, "Beton")
    g.box(-cw + WD, yc, -0.7, cw - WD, ye - WD, F0, "Beton")
    g.box(-nx + WD, yn + WD, H - 0.2, nx - WD, yc, H, "Decke")
    g.box(-cw + WD, yc, H2 - 0.2, cw - WD, ye - WD, H2, "Decke")
    for ys in (-5.5, -3.0, -0.5, 2.0, 4.5, 7.0):
        g.box(-nx + WD, ys - 0.12, H - 0.5, nx - WD, ys + 0.12, H - 0.2, "Holz alt")                                  # Balken
    # Chorstufen (je 0.2 m)
    g.box(-nx + WD, 5.6, F0, nx - WD, yc, F0 + 0.2, "Beton")
    g.box(-cw + WD, yc, F0, cw - WD, ye - WD, F0 + 0.4, "Beton")
    zc_ = F0 + 0.4
    # ---- Vorhalle (Turmerdgeschoss) + Turm
    oef_front = [(-1.3, 1.3, F0, F0 + 3.2), (-1.1, 1.1, F0 + 3.2, F0 + 3.9), (-0.7, 0.7, F0 + 3.9, F0 + 4.4)]
    aussenwand(g, "x", yv, -1, -tw, tw, HT_, mat, oef_front)
    schall = [(-0.8, 0.8, F0 + 10.0, F0 + 12.0), (-0.55, 0.55, F0 + 12.0, F0 + 12.7)]
    ym = (yv + yn) / 2
    oef_t = [(ym - 0.8, ym + 0.8, F0 + 10.0, F0 + 12.0), (ym - 0.55, ym + 0.55, F0 + 12.0, F0 + 12.7)]
    aussenwand(g, "y", tw, 1, yv + WD, yn, HT_, mat, oef_t)
    aussenwand(g, "y", -tw, -1, yv + WD, yn, HT_, mat, oef_t)
    # ---- Innere Verfuellung des Turms (oberhalb der Vorhalle massiv) + Lamellen in den Schallluken
    g.box(-tw + WD, yv + WD, F0 + 4.4, tw - WD, yn - WD, HT_ - 0.2, "Innenwand")
    g.box(-tw + WD, yv + WD, F0 + 4.2, tw - WD, yn - WD, F0 + 4.4, "Decke")
    for zz in [F0 + 10.1 + 0.3 * k for k in range(8)]:
        for sg in (1, -1):
            g.box(sg * (tw - 0.2) - 0.0, yv + 1.4, zz, sg * (tw - 0.12), yn - 1.4, zz + 0.1, "Holz alt")
    g.box(-0.6, yv + 0.25, F0 + 10.0, 0.6, yv + 0.3, F0 + 12.7, "Holz alt")                                         # Front-Luke (geschlossen/Holz)
    for zz in [F0 + 10.1 + 0.3 * k for k in range(8)]:
        g.box(-0.8, yv - 0.02, zz, 0.8, yv + 0.05, zz + 0.1, "Holz alt")
    # Gesimse am Turm
    for zz, ex in ((F0 + 4.6, 0.12), (F0 + 9.3, 0.12), (HT_ - 0.25, 0.25)):
        g.box(-tw - ex, yv - ex, zz, tw + ex, yn + ex, zz + 0.2, stein)
    for k in range(12):
        zz = -0.0 + k * 1.15
        q = 0.38 if k % 2 == 0 else 0.55
        for sx in (-1, 1):
            g.box(sx * tw - sx * q, yv - 0.04, zz, sx * tw + sx * 0.04, yv + 0.55, zz + 0.5, stein)
    # Uhr (Front)
    zu = F0 + 7.2
    n = 16
    P = [(1.0 * math.cos(2 * math.pi * k / n), yv - 0.09, zu + 1.0 * math.sin(2 * math.pi * k / n)) for k in range(n)]
    g.poly(P, (0.0, -1.0, 0.0), "Schrift weiss")
    for hh in range(12):
        a = 2 * math.pi * hh / 12
        g.box(0.82 * math.cos(a) - 0.04, yv - 0.11, zu + 0.82 * math.sin(a) - 0.04, 0.82 * math.cos(a) + 0.04, yv - 0.09, zu + 0.82 * math.sin(a) + 0.04, "Schrift schwarz")
    g.box(-0.04, yv - 0.12, zu, 0.04, yv - 0.09, zu + 0.7, "Schrift schwarz")
    g.box(0.0, yv - 0.12, zu - 0.04, 0.5, yv - 0.09, zu + 0.04, "Schrift schwarz")
    # Portal: Stein-Gewaende, Tuerfluegel offen (nach innen an die Seitenwaende), Glas im Bogenfeld, Stufen
    for sx in (-1, 1):
        g.box(sx * 1.3 - (0.0 if sx > 0 else 0.4), yv - 0.35, F0, sx * 1.3 + (0.4 if sx > 0 else 0.0), yv, F0 + 3.2, stein)
        g.box(sx * 1.1 - (0.0 if sx > 0 else 0.3), yv - 0.25, F0 + 3.2, sx * 1.1 + (0.3 if sx > 0 else 0.0), yv, F0 + 3.9, stein)
        g.box(sx * 0.7 - (0.0 if sx > 0 else 0.25), yv - 0.2, F0 + 3.9, sx * 0.7 + (0.25 if sx > 0 else 0.0), yv, F0 + 4.4, stein)
        g.box(sx * 1.3 - 0.0, yv + WD, F0, sx * 1.3 + sx * 0.07, yv + WD + 1.3, F0 + 3.0, "Tuer")                                # aufgeschwenkter Fluegel
    g.box(-0.7, yv - 0.2, F0 + 4.4, 0.7, yv, F0 + 4.7, stein)
    g.box(-0.7, yv + 0.1, F0 + 3.2, 0.7, yv + 0.14, F0 + 4.4, "Glas bunt gelb")
    g.box(-2.2, yv - 1.5, -0.6, 2.2, yv - 0.7, 0.1, "Beton")
    g.box(-2.2, yv - 0.7, -0.6, 2.2, yv, F0, "Beton")
    g.box(-1.3, yv - 0.05, F0 - 0.04, 1.3, yv + WD, F0, "Beton")
    # Vorhalle innen
    g.box(-tw + WD, yv + WD, -0.7, tw - WD, yn, F0, "Beton")
    g.box(-tw + WD + 0.05, yv + WD + 0.05, F0, -tw + WD + 0.35, yv + WD + 0.9, F0 + 1.3, "Holz")                       # Opferstock/Schriftentisch
    g.box(tw - WD - 0.3, yv + 2.0, F0 + 1.2, tw - WD - 0.04, yv + 3.6, F0 + 2.0, "Schild gelb")                         # Aushang
    g.prism(-tw + 0.7, yn - 0.7, F0, 0.2, 1.0, 8, "Stein")                                                              # Weihwasserbecken
    # ---- Daecher: Schiff, Chor, Turmhelm
    gn = Lok(b, cx + 0.5 * (-math.sin(theta)) * 1.0 + 0.0, cy + 0.5 * math.cos(theta), zb, theta, 1)
    dach(gn, "y", 2 * nx, yc - yn, H, 4.4, "Dach Schiefer", mat, e=0.45)
    gc = Lok(b, cx + (-math.sin(theta)) * (yc + ye) / 2, cy + math.cos(theta) * (yc + ye) / 2, zb, theta, 1)
    dach(gc, "y", 2 * cw, ye - yc, H2, 2.6, "Dach Schiefer", mat, e=0.4)
    gt = Lok(b, cx + (-math.sin(theta)) * (yv + yn) / 2, cy + math.cos(theta) * (yv + yn) / 2, zb, theta, 1)
    dach(gt, "walm", 2 * tw, yn - yv, HT_, 8.0, "Dach Schiefer", mat, e=0.3)
    top = HT_ + 8.0
    g.box(-0.08, (yv + yn) / 2 - 0.08, top, 0.08, (yv + yn) / 2 + 0.08, top + 1.8, "Kreuz")
    g.box(-0.5, (yv + yn) / 2 - 0.06, top + 1.1, 0.5, (yv + yn) / 2 + 0.06, top + 1.25, "Kreuz")
    g.box(-0.06, (yv + yn) / 2 - 0.5, top + 1.1, 0.06, (yv + yn) / 2 + 0.5, top + 1.25, "Kreuz")
    for sx in (-1, 1):                                                                                                  # Wasserspeier-Zierspitzen an den Turmecken
        for sy in (yv, yn):
            g.box(sx * tw - 0.15, sy - 0.15 if sy == yv else sy - 0.15, HT_, sx * tw + 0.15, sy + 0.15, HT_ + 0.9, stein)
    # Kreuz auf dem Schiffgiebel (Ostende) und Chor
    g.box(-0.06, ye - 0.1, H2 + 2.6, 0.06, ye + 0.1, H2 + 3.6, "Kreuz")
    g.box(-0.4, ye - 0.06, H2 + 3.0, 0.4, ye + 0.06, H2 + 3.15, "Kreuz")
    # ---- Innenausstattung
    g.box(-0.6, yn + WD, F0, 0.6, yc - 0.5, F0 + 0.03, "Teppich")                                                       # Laeufer im Mittelgang
    for side in (-1, 1):
        for k in range(9):
            ys = -5.2 + k * 1.1
            x0, x1 = (1.3, 4.4) if side > 0 else (-4.4, -1.3)
            g.box(x0, ys, F0, x1, ys + 0.38, F0 + 0.45, "Bank")
            g.box(x0, ys + 0.38, F0, x1, ys + 0.48, F0 + 1.0, "Bank")
    g.box(-4.9, 3.5, F0, -3.9, 4.6, F0 + 1.3, "Holz")                                                                   # Kanzel
    g.box(-5.0, 3.4, F0 + 1.3, -3.8, 4.7, F0 + 1.45, "Holz alt")
    g.box(-4.9, 3.5, F0 + 1.45, -3.9, 3.6, F0 + 2.6, "Holz")
    g.box(-4.9, 4.5, F0 + 1.45, -3.9, 4.6, F0 + 2.6, "Holz")
    g.box(-4.5, 3.3, F0 + 2.6, -4.3, 4.7, F0 + 2.75, "Holz alt")
    g.prism(3.6, 4.8, F0, 0.4, 0.95, 8, "Stein")                                                                        # Taufstein
    g.prism(3.6, 4.8, F0 + 0.95, 0.5, 0.08, 8, "Stein")
    g.box(-1.3, 10.9, zc_, 1.3, 11.8, zc_ + 1.0, "Altar")                                                               # Altar
    g.box(-1.45, 10.8, zc_ + 1.0, 1.45, 11.9, zc_ + 1.1, "Stein")
    g.box(-0.6, 10.95, zc_ + 1.1, 0.6, 11.75, zc_ + 1.12, "Teppich")
    for sx in (-0.9, 0.9):
        g.prism(sx, 11.35, zc_ + 1.1, 0.07, 0.4, 6, "Schild gelb")
    g.box(-0.07, ye - WD - 0.05, zc_ + 1.8, 0.07, ye - WD + 0.0, zc_ + 3.6, "Kreuz")                                  # Altarkreuz an der Ostwand
    g.box(-0.5, ye - WD - 0.05, zc_ + 3.0, 0.5, ye - WD + 0.0, zc_ + 3.14, "Kreuz")
    g.box(cw - 0.9, 9.0, zc_, cw - WD - 0.0, 9.5, zc_ + 1.2, "Holz")                                                    # Chorgestuehl
    g.box(-cw + WD, 9.0, zc_, -cw + 0.9, 9.5, zc_ + 1.2, "Holz")
    for sg in (-1, 1):
        for ys in (-2.5, 1.0):                                                                                          # Haengeleuchter
            g.box(sg * 2.0 - 0.02, ys - 0.02, H - 1.7, sg * 2.0 + 0.02, ys + 0.02, H - 0.5, "Metall")
            g.prism(sg * 2.0, ys, H - 2.0, 0.28, 0.3, 8, "Schild gelb")
    for sg in (-1, 1):
        g.box(sg * (nx - 0.9) - 0.15, 6.4, F0, sg * (nx - 0.9) + 0.15, 6.7, F0 + 0.1, "Metall")
        g.prism(sg * (nx - 0.9), 6.55, F0 + 0.1, 0.1, 1.2, 6, "Metall")                                                 # Kerzenstaender
    return g


