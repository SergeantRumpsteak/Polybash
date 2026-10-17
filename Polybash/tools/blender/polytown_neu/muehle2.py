"""Polybash - zweite Muehle (gemauerte Hollaender-Turmmuehle) und Schaeferhuette am Nordrand (x 205..235, y 250..299).

Beide Bauten stehen auf ebenen Bauplaetzen (umgebung.PLATEAUS), sind mit keiner Strasse verbunden und sehen bewusst anders aus als die
Bockwindmuehle und die Blockhuetten weiter oestlich (muehle.py):
  * Turmmuehle (224, 286): runder, nach oben verjuengter weisser Putzturm (16 Segmente, Sockel aus Stein), drehbare Kappe mit schwarzer Haube
    und Steert (Schwanzbalken mit Windenrad), vier Gatterfluegel (Windbrett, Latten, Querrippen) nach Westen. Tuer im Sueden, davor Stufen; Kappe dreht die Fluegel nach Suedwesten (Steert nach Nordosten).
    Rundherum eine Galerie (Stellage, 1,1 m breit, Gelaender) in 3 m Hoehe mit gerader Treppe von Norden. Innen: Mehlboden mit Saecken und
    Mehlkasten, gerade Treppe (12 Stufen) in den Steinboden mit zwei Mahlgaengen (Zargen und Laeufer), mittig die Koenigswelle.
  * Schaeferhuette (211, 261): Schaeferwagen (Holzkasten mit Tonnendach aus Blech auf Eisenraedern, Treppe, Deichsel, Bett, Ofen mit Rohr),
    Pferch aus Hurden (5 Schafe, Futterraufe, Trog), Hundehuette, Wassertonne, Heuhaufen.
Hindernisse sind achsenparallele Quader (runde Waende: kleine Quader entlang des Kreises); Treppen haben max. 0,31 m Stufenhoehe."""
import math

import burg as B
import stadt as S
from stadt import Lok
import altbau
import umgebung as U
from burg import Bau

S.FARBEN.update({
    "Schaf Wolle": ((0.86, 0.84, 0.78), 1.0, 0.0), "Schaf Kopf": ((0.22, 0.19, 0.17), 1.0, 0.0),
    "Haube schwarz": ((0.07, 0.07, 0.08), 0.9, 0.0), "Windbrett": ((0.90, 0.89, 0.84), 0.8, 0.0),
    "Wagen gruen": ((0.14, 0.30, 0.22), 0.8, 0.0), "Wagen rot": ((0.52, 0.12, 0.10), 0.8, 0.0),
})
for _n in ("Stein alt", "Holz alt", "Holz dunkel", "Dielen", "Sack", "Heu", "Eisen", "Rahmen weiss", "Putz weiss", "Fenster", "Tuer", "Holz", "Stein", "Metall",
           "Brunnenwasser", "Dach grau", "Laden gruen", "Stroh", "Fell", "Teppich", "Regal"):
    S.FARBEN.setdefault(_n, ((0.5, 0.5, 0.5), 0.9, 0.0))

MUEHLE2 = (224.0, 286.0)                  # Mitte des Turms (Tuer nach Sueden, Fluegel nach Westen)
HUETTE = (216.0, 262.0)                   # Mitte des Bauplatzes Schaeferhuette
WAGEN = (210.5, 261.0)                    # Schaeferwagen (Tuer nach Westen)
PFERCH = (215.0, 258.0, 223.5, 265.0)     # Hurdengehege (x0, y0, x1, y1), Tor im Westen
PLATEAUS = ((224.0, 286.0, 9.5, 13.0), (216.0, 262.0, 8.5, 12.0))
BAUPLAETZE = ((224.0, 286.0, 16.0), (216.0, 262.0, 14.0))

R0, SCHRUMPF = 3.9, 0.14                  # Turmradius am Boden und Abnahme je Meter Hoehe
WD = 0.55                                 # Wandstaerke
HT = 11.0                                 # Turmhoehe bis zur Kappe (Fluegel bleiben ueber Kopfhoehe der Galerie)
Z_GAL, Z_OG = 3.0, 3.4                    # Galerie / Steinboden


def r_aus(z):
    return R0 - SCHRUMPF * z


def _z(x, y):
    return U.gelaende_hoehe(x, y)


def _belegt():
    mx, my = MUEHLE2
    out = [(mx - 5.6, my - 5.6, mx + 5.6, my + 5.6), (mx - 1.2, my + 4.4, mx + 1.2, my + 9.6), (mx - 1.6, my - 6.2, mx + 1.6, my - 3.4)]
    hx, hy = WAGEN
    out.append((hx - 3.8, hy - 1.6, hx + 5.0, hy + 1.6))
    out.append((PFERCH[0] - 0.6, PFERCH[1] - 0.6, PFERCH[2] + 0.6, PFERCH[3] + 0.6))
    out.append((hx - 1.2, hy + 2.0, hx + 1.2, hy + 4.2))                                                 # Wassertonne / Heu / Huette
    return out


BELEGT = tuple(_belegt())


def _bm(g, a, b, w, h, mat):
    g.b.beam(g.P(a), g.P(b), w, h, mat)


def _prisma(g, a0, a1, z0, z1, mat, d=WD):
    """Wandsegment zwischen den Winkeln a0, a1 (Bogenmass) von z0 bis z1 (aussen verjuengt), Dicke d; kein Hindernis (nur Flaeche)."""
    ro0, ro1 = r_aus(z0), r_aus(z1)
    ca0, sa0, ca1, sa1 = math.cos(a0), math.sin(a0), math.cos(a1), math.sin(a1)
    v = []
    for (ro, z) in ((ro0, z0), (ro1, z1)):
        ri = ro - d
        v += [g.P((ro * ca0, ro * sa0, z)), g.P((ro * ca1, ro * sa1, z)), g.P((ri * ca1, ri * sa1, z)), g.P((ri * ca0, ri * sa0, z))]
    g.b.add(v, B.BOX_FACES, mat)


def turm(g, b):
    """Turmwand aus 16 Segmenten x 8 Baendern (Tuer im Sueden, drei Fenster je Seite) samt Hindernisquadern."""
    n, nb = 16, 11
    dz = HT / nb
    a_step = 2 * math.pi / n
    deko = altbau.Deko(g)
    for i in range(n):
        ac = -math.pi / 2 + i * a_step                       # Segmentmitte; i = 0: Tuer
        a0, a1 = ac - a_step / 2, ac + a_step / 2
        fenster = i in (4, 8, 12, 6, 10, 14)
        for k in range(nb):
            z0, z1 = k * dz, (k + 1) * dz
            if i == 0 and k < 2:
                continue                                      # Tuerloeffnung (Segmentbreite 1,5 m, 2,0 m hoch)
            mat = "Stein alt" if k == 0 else ("Putz weiss alt" if k < nb - 1 else "Putz weiss")
            if fenster and k in (3, 5, 7):
                t = a_step / 3
                _prisma(g, a0, a0 + t, z0, z1, mat)
                _prisma(g, a1 - t, a1, z0, z1, mat)
                _prisma(g, a0 + t, a1 - t, z0, z1, "Fenster", d=0.12)                 # Glas im Mauerloch
                _prisma(g, a0 + t, a1 - t, z0, z0 + 0.08, "Rahmen weiss", d=WD)       # Fensterbank
                _prisma(g, a0 + t, a1 - t, z1 - 0.08, z1, "Rahmen weiss", d=WD)
            else:
                _prisma(g, a0, a1, z0, z1, mat)
        # Hindernisse: je 2,1 m Hoehe drei kleine Quader entlang des Segments
        for kk in range(6):
            zlo = kk * 2.0
            zhi = min(zlo + 2.0, HT) if kk < 5 else HT
            if i == 0 and kk == 0:
                continue                                # Tuerseite: Hindernis erst ab der Tuersturzhoehe (2,0 m)
            zm = (zlo + zhi) / 2
            rm = r_aus(zm) - WD / 2
            for f in (0.17, 0.5, 0.83):
                a = a0 + (a1 - a0) * f
                px, py = rm * math.cos(a), rm * math.sin(a)
                g.b.bx.append((g.cx + px - 0.33, g.cy + py - 0.33, g.zb + zlo, g.cx + px + 0.33, g.cy + py + 0.33, g.zb + zhi))
    # Tuerrahmen und aufgeklapptes Tuerblatt (ohne Hindernis)
    ro = r_aus(0.0)
    deko.box(-0.78, -ro - 0.06, 0.0, -0.70, -ro + 0.1, 2.1, "Holz dunkel")
    deko.box(0.70, -ro - 0.06, 0.0, 0.78, -ro + 0.1, 2.1, "Holz dunkel")
    deko.box(-0.78, -ro - 0.06, 2.1, 0.78, -ro + 0.1, 2.2, "Holz dunkel")
    deko.box(0.86, -ro - 1.0, 0.0, 0.92, -ro - 0.05, 2.05, "Tuer")


def innen(g):
    """Mehlboden (unten), Steinboden mit Mahlgaengen (3,4 m), Treppe, Koenigswelle."""
    deko = altbau.Deko(g)
    g.b.add([g.P((2.95 * math.cos(2 * math.pi * k / 16), 2.95 * math.sin(2 * math.pi * k / 16), 0.02)) for k in range(16)], [tuple(range(15, -1, -1))], "Dielen")
    rin = r_aus(Z_OG) - WD - 0.04
    ys = [-2.8, -2.2, -1.6, -1.2, -0.6, 0.0, 0.6, 1.2, 1.8, 2.4, 2.8]
    for y0, y1 in zip(ys, ys[1:]):
        yh = max(abs(y0), abs(y1))
        if yh >= rin:
            continue
        half = math.sqrt(max(0.01, rin * rin - yh * yh))
        if y1 <= -1.2 + 1e-9:                                                              # Treppenaussparung x -1.9 .. 1.7
            if half > 1.7:
                g.box(1.7, y0, Z_OG - 0.2, half, y1, Z_OG, "Dielen")
            if half > 1.9:
                g.box(-half, y0, Z_OG - 0.2, -1.9, y1, Z_OG, "Dielen")
        else:
            g.box(-half, y0, Z_OG - 0.2, half, y1, Z_OG, "Dielen")
    # Balken unter dem Steinboden
    for k in range(-4, 5):
        deko.box(-2.7, k * 0.6 - 0.05, Z_OG - 0.35, 2.7, k * 0.6 + 0.05, Z_OG - 0.2, "Holz dunkel")
    # gerade Treppe: 12 Stufen von x = -1.9 (unten) nach +1.7 (oben), y -2.2 .. -1.3
    n = 12
    for i in range(n):
        g.box(-1.9 + 0.3 * i, -2.2, 0.0, -1.9 + 0.3 * (i + 1), -1.2, Z_OG * (i + 1) / n, "Holz" if i % 2 else "Holz alt")
    for sy in (-2.25, -1.25):
        _bm(g, (-1.9, sy, 0.9), (1.7, sy, Z_OG + 0.9), 0.07, 0.07, "Holz dunkel")
    # Koenigswelle (Mitte) mit grossem Kammrad (hoch oben, ohne Hindernis)
    g.box(-0.2, -0.2, 0.0, 0.2, 0.2, HT + 0.4, "Holz dunkel")
    deko.box(-0.9, -0.9, 6.0, 0.9, 0.9, 6.3, "Holz")
    for k in range(12):
        a = k * math.pi / 6
        deko.box(1.3 * math.cos(a) - 0.1, 1.3 * math.sin(a) - 0.1, 5.9, 1.3 * math.cos(a) + 0.1, 1.3 * math.sin(a) + 0.1, 6.4, "Holz alt")
    for sx in (-1, 1):
        _bm(g, (0.0, 0.0, 6.15), (sx * 1.3, 0.0, 6.15), 0.2, 0.2, "Holz dunkel")
        _bm(g, (0.0, 0.0, 6.15), (0.0, sx * 1.3, 6.15), 0.2, 0.2, "Holz dunkel")
    # Mahlgaenge: Zarge (Holzring), Laeufer, Trichter - als Hindernisse 1,5 x 1,5 m
    for (px, py) in ((-1.35, 1.1), (1.35, 1.1)):
        g.box(px - 0.75, py - 0.75, Z_OG, px + 0.75, py + 0.75, Z_OG + 0.55, "Holz")
        deko.box(px - 0.65, py - 0.65, Z_OG + 0.55, px + 0.65, py + 0.65, Z_OG + 0.62, "Stein")
        g.b.prism(*g.P((px, py, 0.0))[:2], g.zb + Z_OG + 0.62, 0.55, 0.14, 10, "Stein")
        for k in range(4):
            a = k * math.pi / 2 + 0.4
            _bm(g, (px + 0.5 * math.cos(a), py + 0.5 * math.sin(a), Z_OG + 0.62), (px + 0.2 * math.cos(a), py + 0.2 * math.sin(a), Z_OG + 1.9), 0.06, 0.06, "Holz dunkel")
        ring = [g.P((px + 0.5 * math.cos(2 * math.pi * k / 8), py + 0.5 * math.sin(2 * math.pi * k / 8), Z_OG + 1.9)) for k in range(8)]
        g.b.add(ring + [g.P((px, py, Z_OG + 1.2))], [tuple(range(7, -1, -1))] + [(k, (k + 1) % 8, 8) for k in range(8)], "Holz alt")
    g.box(-0.5, 2.0, Z_OG, 0.5, 2.55, Z_OG + 0.8, "Holz")                                  # Mehlschurre
    # Mehlboden unten: Saecke, Mehlkasten, Fass, Hebezeug
    for k, (px, py) in enumerate(((-2.5, -0.3), (-2.5, 0.5), (-2.0, 1.0), (2.45, -0.3), (2.45, 0.5), (2.0, 1.2))):
        g.box(px - 0.3, py - 0.28, 0.0, px + 0.3, py + 0.28, 0.55, "Sack")
        if k % 2 == 0:
            g.box(px - 0.28, py - 0.26, 0.55, px + 0.28, py + 0.26, 1.05, "Sack")
    g.box(-0.9, 2.1, 0.0, 0.9, 2.9, 0.9, "Holz")                                           # Mehlkasten
    deko.box(-0.8, 2.15, 0.9, 0.8, 2.85, 0.95, "Holz dunkel")
    g.b.prism(*g.P((1.7, 2.3, 0.0))[:2], g.zb, 0.38, 0.9, 8, "Holz alt")                    # Fass
    deko.box(-0.9, 0.05, 2.7, 0.9, 0.12, 2.8, "Holz dunkel")                                # Lastbalken
    # Fenster-Bruestungen sind Mauerwerk; Eisenanker am Turm
    return g


def galerie(g):
    """Umlaufende Galerie in Z_GAL Hoehe, Gelaender, Treppe von Norden (12 Stufen)."""
    deko = altbau.Deko(g)
    for rr in (3.65, 4.1):
        n = int(2 * math.pi * rr / 0.5)
        for k in range(n):
            a = 2 * math.pi * k / n
            px, py = rr * math.cos(a), rr * math.sin(a)
            g.box(px - 0.3, py - 0.3, Z_GAL - 0.2, px + 0.3, py + 0.3, Z_GAL, "Dielen")
    for a in range(24):                                                                      # Konsolen unter der Galerie
        a_ = a * math.pi / 12
        _bm(g, (3.4 * math.cos(a_), 3.4 * math.sin(a_), Z_GAL - 1.0), (4.35 * math.cos(a_), 4.35 * math.sin(a_), Z_GAL - 0.2), 0.12, 0.12, "Holz dunkel")
    nposts = 36
    rr = 4.5
    posts = []
    for k in range(nposts):
        a = 2 * math.pi * k / nposts
        if abs(a - math.pi / 2) < 0.25:
            continue                                                                         # Zugang der Treppe
        px, py = rr * math.cos(a), rr * math.sin(a)
        g.box(px - 0.05, py - 0.05, Z_GAL, px + 0.05, py + 0.05, Z_GAL + 1.05, "Holz dunkel")
        posts.append((k, px, py))
    for (k, px, py) in posts:
        k2 = (k + 1) % nposts
        if any(p[0] == k2 for p in posts):
            a2 = 2 * math.pi * k2 / nposts
            for hz in (0.55, 1.05):
                _bm(g, (px, py, Z_GAL + hz), (rr * math.cos(a2), rr * math.sin(a2), Z_GAL + hz), 0.06, 0.06, "Holz")
    # Treppe von Norden: Stufe i hat die Oberkante 0,25 (i + 1); Absatz oben an der Galerie
    n = 12
    for i in range(n):
        y0 = 4.5 + 0.4 * (n - 1 - i)
        g.box(-0.5, y0 - (0.4 if i == n - 1 else 0.0), 0.0, 0.5, y0 + 0.4, Z_GAL * (i + 1) / n, "Holz" if i % 2 else "Holz alt")
    for sx in (-0.56, 0.56):
        _bm(g, (sx, 9.2, 0.9), (sx, 4.5, Z_GAL + 0.9), 0.07, 0.07, "Holz dunkel")
        for k in range(0, n, 3):
            yy = 4.5 + 0.4 * (n - 1 - k) + 0.2
            _bm(g, (sx, yy, Z_GAL * (k + 1) / n), (sx, yy, Z_GAL * (k + 1) / n + 0.9), 0.06, 0.06, "Holz dunkel")


def kappe(g):
    """Drehbare Kappe mit Haube, Windwelle, vier Gatterfluegeln und Steert."""
    deko = altbau.Deko(g)
    n = 16
    ring = lambda r, z: [g.P((r * math.cos(2 * math.pi * k / n), r * math.sin(2 * math.pi * k / n), z)) for k in range(n)]
    rc = r_aus(HT) + 0.5
    ringe = [(rc, HT), (rc, HT + 0.35), (rc - 0.25, HT + 0.45), (rc - 0.25, HT + 1.1), (rc - 0.7, HT + 1.9), (rc - 1.45, HT + 2.5), (0.5, HT + 2.8)]
    for (r0, z0), (r1, z1) in zip(ringe, ringe[1:]):
        a, c = ring(r0, z0), ring(r1, z1)
        for k in range(n):
            g.b.add([a[k], a[(k + 1) % n], c[(k + 1) % n], c[k]], [(0, 1, 2, 3)], "Haube schwarz" if r0 > 1.4 else "Dach grau")
    g.b.add(ring(0.5, HT + 2.8) + [g.P((0.0, 0.0, HT + 3.1))], [(k, (k + 1) % n, n) for k in range(n)], "Dach grau")
    g.b.add(ring(rc, HT)[::-1], [tuple(range(n))], "Holz dunkel")
    deko.box(-0.03, -0.03, HT + 3.1, 0.03, 0.03, HT + 3.9, "Eisen")                         # Wetterfahne
    deko.box(0.0, -0.01, HT + 3.55, 0.7, 0.01, HT + 3.9, "Eisen")
    # Windwelle nach Westen auf z = HT + 1.0
    hz, hx = HT + 1.3, -3.45
    _bm(g, (1.2, 0.0, hz), (hx, 0.0, hz), 0.42, 0.42, "Holz dunkel")
    deko.box(hx - 0.55, -0.4, hz - 0.4, hx + 0.1, 0.4, hz + 0.4, "Eisen")                     # Fluegelkopf
    ph = math.radians(20.0)
    for k in range(4):
        a = ph + k * math.pi / 2
        ur, uz = math.cos(a), math.sin(a)                                                    # radial in (y, z)
        wr, wz = -math.sin(a), math.cos(a)                                                   # quer
        P = lambda r, o, dx=0.0: (hx + dx, ur * r + wr * o, hz + uz * r + wz * o)
        _bm(g, P(0.3, 0.0), P(7.4, 0.0), 0.26, 0.2, "Holz dunkel")                           # Rute
        _bm(g, P(1.2, 0.18, -0.12), P(7.3, 0.18, -0.12), 0.1, 0.045, "Windbrett")           # Windbrett (Vorderseite)
        _bm(g, P(1.2, 1.7, 0.0), P(7.3, 1.7, 0.0), 0.08, 0.08, "Rahmen weiss")              # hintere Latte
        _bm(g, P(1.2, 0.5, 0.0), P(1.2, 1.7, 0.0), 0.08, 0.08, "Rahmen weiss")
        _bm(g, P(7.3, 0.18, 0.0), P(7.3, 1.7, 0.0), 0.08, 0.08, "Rahmen weiss")
        r = 1.6
        while r < 7.3:
            _bm(g, P(r, 0.18), P(r, 1.7), 0.05, 0.05, "Rahmen weiss")                        # Querrippen (Gatter)
            r += 0.5
        for oo in (0.9, 1.3):
            _bm(g, P(1.2, oo), P(7.6, oo), 0.04, 0.04, "Rahmen weiss")                       # Laengslatten
    # Steert (Schwanzbalken) nach Osten, schraeg zum Boden mit Windenrad
    _bm(g, (2.7, 0.0, HT + 0.6), (7.4, 0.0, 2.2), 0.28, 0.2, "Holz dunkel")
    _bm(g, (7.4, 0.0, 2.2), (7.6, 0.0, 0.0), 0.22, 0.22, "Holz")
    for k in range(8):                                                                       # Windenrad am Fuss
        a = k * math.pi / 4
        _bm(g, (7.6, 0.0, 1.0), (7.6 + 0.0, 0.8 * math.cos(a), 1.0 + 0.8 * math.sin(a)), 0.05, 0.05, "Holz alt")
    g.box(7.45, -0.1, 0.0, 7.75, 0.1, 0.6, "Holz dunkel")                                    # Steertpfosten (Hindernis)


def muehle(b):
    cx, cy = MUEHLE2
    zb = _z(cx, cy)
    g = Lok(b, cx, cy, zb, 0.0)
    turm(g, b)
    innen(g)
    galerie(g)
    kappe(Lok(b, cx, cy, zb, math.radians(45.0)))                                          # Kappe samt Fluegeln nach Suedwesten, Steert nach Nordosten
    # Zubehoer vor der Muehle: Sackkarre-artige Karre, Saecke, Holzblock mit Beil
    g.box(-2.7, -5.2, 0.0, -2.1, -4.6, 0.55, "Sack")
    g.box(-2.6, -5.0, 0.55, -2.2, -4.7, 1.05, "Sack")
    g.box(-1.9, -5.4, 0.0, -1.3, -4.8, 0.45, "Sack")
    g.b.prism(*g.P((2.6, -5.0, 0.0))[:2], g.zb, 0.3, 0.5, 8, "Holz alt")
    return b


# ------------------------------------------------------------------ Schaeferhuette
def _rad(g, cx, cy, cz, r, w, n=12):
    """Eisenrad mit Achse in y (lokal): Reifen als Ring aus n Quadern-Flaechen, Speichen; Hindernis: ein schmaler Quader."""
    ring = lambda y, rr: [g.P((cx + rr * math.cos(2 * math.pi * k / n), y, cz + rr * math.sin(2 * math.pi * k / n))) for k in range(n)]
    for (ra, rb, mat) in ((r, r - 0.07, "Eisen"),):
        a0, a1, b0, b1 = ring(cy - w / 2, ra), ring(cy + w / 2, ra), ring(cy - w / 2, rb), ring(cy + w / 2, rb)
        for k in range(n):
            j = (k + 1) % n
            g.b.add([a0[k], a0[j], a1[j], a1[k]], [(0, 1, 2, 3)], mat)
            g.b.add([b0[j], b0[k], b1[k], b1[j]], [(0, 1, 2, 3)], mat)
            g.b.add([a0[j], a0[k], b0[k], b0[j]], [(0, 1, 2, 3)], mat)
            g.b.add([a1[k], a1[j], b1[j], b1[k]], [(0, 1, 2, 3)], mat)
    for k in range(6):
        a = k * math.pi / 3
        _bm(g, (cx, cy, cz), (cx + (r - 0.05) * math.cos(a), cy, cz + (r - 0.05) * math.sin(a)), 0.06, 0.06, "Holz alt")
    deko = altbau.Deko(g)
    g.box(cx - r * 0.7, cy - w / 2, 0.0, cx + r * 0.7, cy + w / 2, 2 * r, "Eisen")


def schaf(g, x, y, ach, wolle=True):
    """Schaf in lokalen Koordinaten (ach 'x': Kopf nach +x, 'y': Kopf nach +y); Hindernis: Koerperquader."""
    if ach == "x":
        g.box(x - 0.45, y - 0.25, 0.32, x + 0.45, y + 0.25, 0.80, "Schaf Wolle")
        g.box(x + 0.45, y - 0.12, 0.55, x + 0.78, y + 0.12, 0.88, "Schaf Kopf")
        for sx in (-0.32, 0.32):
            for sy in (-0.15, 0.15):
                g.box(x + sx - 0.04, y + sy - 0.04, 0.0, x + sx + 0.04, y + sy + 0.04, 0.32, "Schaf Kopf")
        g.box(x + 0.5, y - 0.18, 0.78, x + 0.56, y - 0.12, 0.88, "Schaf Kopf")
        g.box(x + 0.5, y + 0.12, 0.78, x + 0.56, y + 0.18, 0.88, "Schaf Kopf")
    else:
        g.box(x - 0.25, y - 0.45, 0.32, x + 0.25, y + 0.45, 0.80, "Schaf Wolle")
        g.box(x - 0.12, y + 0.45, 0.55, x + 0.12, y + 0.78, 0.88, "Schaf Kopf")
        for sx in (-0.15, 0.15):
            for sy in (-0.32, 0.32):
                g.box(x + sx - 0.04, y + sy - 0.04, 0.0, x + sx + 0.04, y + sy + 0.04, 0.32, "Schaf Kopf")


def wagen(b):
    wx, wy = WAGEN
    zb = _z(wx, wy)
    g = Lok(b, wx, wy, zb, 0.0)
    deko = altbau.Deko(g)
    FZ, H, t = 0.85, 2.15, 0.08
    x0, x1, y0, y1 = -1.9, 1.9, -1.0, 1.0
    g.box(x0, y0, FZ - 0.18, x1, y1, FZ, "Holz dunkel")                                           # Boden mit Raehmchen
    deko.box(x0 + t, y0 + t, FZ, x1 - t, y1 - t, FZ + 0.02, "Dielen")
    wand(g, "x", y0, y0 + t, x0, x1, FZ, H, "Wagen gruen", [(0.15, 0.95, FZ + 0.55, FZ + 1.15)])
    wand(g, "x", y1 - t, y1, x0, x1, FZ, H, "Wagen gruen", [(0.15, 0.95, FZ + 0.55, FZ + 1.15)])
    wand(g, "y", x0, x0 + t, y0 + t, y1 - t, FZ, H, "Wagen gruen", [(-0.4, 0.4, FZ, FZ + 1.95)])     # Tuer im Westen
    wand(g, "y", x1 - t, x1, y0 + t, y1 - t, FZ, H, "Wagen gruen", [])
    for (yy, nn) in ((y0, -1), (y1, 1)):
        deko.box(0.15, yy, FZ + 0.55, 0.95, yy + nn * 0.03, FZ + 1.15, "Fenster")
        for (a, c, z0_, z1_) in ((0.1, 0.15, FZ + 0.5, FZ + 1.2), (0.95, 1.0, FZ + 0.5, FZ + 1.2)):
            deko.box(a, yy, z0_, c, yy + nn * 0.05, z1_, "Wagen rot")
        deko.box(0.1, yy, FZ + 0.5, 1.0, yy + nn * 0.05, FZ + 0.55, "Wagen rot")
        deko.box(0.1, yy, FZ + 1.15, 1.0, yy + nn * 0.05, FZ + 1.2, "Wagen rot")
    for xx in (x0 + 0.05, x1 - 0.13):                                                             # Eckleisten
        for yy in (y0, y1 - 0.08):
            deko.box(xx, yy, FZ, xx + 0.08, yy + 0.08, H, "Wagen rot")
    # Tonnendach aus Blech: Bogen ueber y, 9 Segmente (kein Hindernis)
    prof = [(y0 - 0.12 + (y1 - y0 + 0.24) * k / 8, H + 0.55 * (1 - ((k - 4) / 4.0) ** 2)) for k in range(9)]
    for (ya, za), (yb, zb_) in zip(prof, prof[1:]):
        g.poly([(x0 - 0.25, ya, za), (x1 + 0.25, ya, za), (x1 + 0.25, yb, zb_), (x0 - 0.25, yb, zb_)], (0.0, 0.0, 1.0), "Metall")
    for xx in (x0 + 0.1, 0.0, x1 - 0.1):
        for (ya, za), (yb, zb_) in zip(prof, prof[1:]):
            _bm(g, (xx, ya, za - 0.02), (xx, yb, zb_ - 0.02), 0.06, 0.04, "Holz dunkel")
    # Giebelwand oben: Segment ueber den Seitenwaenden (West/Ost)
    for sx, nx in ((x0, -1.0), (x1, 1.0)):
        g.poly([(sx, y0, H), (sx, y1, H)] + [(sx, p[0], p[1] - 0.02) for p in prof[::-1]], (nx, 0.0, 0.0), "Wagen gruen")
    # Ofen mit Rohr, Bett, Tisch, Regal, Laterne
    g.box(1.15, -0.85, FZ, 1.75, -0.35, FZ + 0.5, "Eisen")
    g.b.prism(*g.P((1.45, -0.6, 0.0))[:2], g.zb + FZ + 0.5, 0.05, 2.4, 8, "Eisen")
    g.box(-0.2, 0.3, FZ, 1.1, 0.95, FZ + 0.45, "Holz")                                           # Bettkasten
    deko.box(-0.15, 0.35, FZ + 0.45, 1.05, 0.9, FZ + 0.58, "Teppich")
    g.box(-1.7, 0.55, FZ + 0.3, -1.25, 0.95, FZ + 0.32, "Holz")                                  # Klapptisch
    g.box(-1.5, 0.74, FZ, -1.45, 0.76, FZ + 0.3, "Holz dunkel")
    g.box(1.2, 0.6, FZ + 1.3, 1.85, 0.95, FZ + 1.35, "Holz")                                     # Regalbrett
    # Treppe (3 Stufen), Deichsel mit Stuetzrad, Raeder
    for i in range(2):                                                                            # 3 Steigungen: 0,283 / 0,567 / Boden 0,85
        g.box(x0 - 0.35 * (i + 1), -0.5, 0.0, x0 - 0.35 * i, 0.5, FZ - 0.283 * (i + 1), "Holz" if i % 2 else "Holz alt")
    _bm(g, (x1 + 0.1, 0.0, 0.55), (x1 + 2.4, 0.0, 0.5), 0.12, 0.12, "Holz dunkel")
    g.box(x1 + 2.3, -0.08, 0.0, x1 + 2.5, 0.08, 0.55, "Holz")
    for xc in (-1.0, 1.0):
        for sy in (-1, 1):
            _rad(g, xc, sy * 1.12, 0.62, 0.62, 0.1)
    # Pferch: Hurden (Pfosten, zwei Querbalken, Stehbretter), Tor im Westen (offen nach innen), Trog, Raufe, Schafe
    px0, py0, px1, py1 = PFERCH
    gx, gy = px0 - wx, py0 - wy
    lx0, ly0, lx1, ly1 = px0 - wx, py0 - wy, px1 - wx, py1 - wy

    def hurde_x(xa, xb, y):
        xx = xa
        while xx < xb - 1e-6:
            xn = min(xx + 1.5, xb)
            g.box(xx - 0.05, y - 0.05, 0.0, xx + 0.05, y + 0.05, 1.05, "Holz dunkel")
            g.box(xx + 0.05, y - 0.03, 0.30, xn - 0.05, y + 0.03, 0.40, "Holz")
            g.box(xx + 0.05, y - 0.03, 0.70, xn - 0.05, y + 0.03, 0.80, "Holz")
            kx = xx + 0.3
            while kx < xn - 0.1:
                g.box(kx - 0.02, y - 0.02, 0.0, kx + 0.02, y + 0.02, 0.95, "Holz alt")
                kx += 0.3
            xx = xn
        g.box(xb - 0.05, y - 0.05, 0.0, xb + 0.05, y + 0.05, 1.05, "Holz dunkel")

    def hurde_y(x, ya, yb):
        yy = ya
        while yy < yb - 1e-6:
            yn = min(yy + 1.5, yb)
            g.box(x - 0.05, yy - 0.05, 0.0, x + 0.05, yy + 0.05, 1.05, "Holz dunkel")
            g.box(x - 0.03, yy + 0.05, 0.30, x + 0.03, yn - 0.05, 0.40, "Holz")
            g.box(x - 0.03, yy + 0.05, 0.70, x + 0.03, yn - 0.05, 0.80, "Holz")
            ky = yy + 0.3
            while ky < yn - 0.1:
                g.box(x - 0.02, ky - 0.02, 0.0, x + 0.02, ky + 0.02, 0.95, "Holz alt")
                ky += 0.3
            yy = yn
        g.box(x - 0.05, yb - 0.05, 0.0, x + 0.05, yb + 0.05, 1.05, "Holz dunkel")

    hurde_x(lx0, lx1, ly0)
    hurde_x(lx0, lx1, ly1)
    hurde_y(lx1, ly0, ly1)
    gate = (ly0 + ly1) / 2
    hurde_y(lx0, ly0, gate - 0.8)
    hurde_y(lx0, gate + 0.8, ly1)
    g.box(lx0 + 0.05, gate - 0.8, 0.0, lx0 + 1.65, gate - 0.74, 1.0, "Holz")                       # offenes Tor, nach innen geschwungen
    g.box(lx0 + 0.05, gate - 0.8, 0.35, lx0 + 1.65, gate - 0.74, 0.45, "Holz alt")
    # Trog und Raufe im Pferch
    g.box(lx1 - 1.0, ly0 + 1.0, 0.0, lx1 - 0.4, ly0 + 3.0, 0.45, "Holz")
    g.box(lx1 - 0.92, ly0 + 1.08, 0.3, lx1 - 0.48, ly0 + 2.92, 0.4, "Brunnenwasser")
    g.box(lx0 + 3.0, ly1 - 0.9, 0.0, lx0 + 5.0, ly1 - 0.4, 0.55, "Holz")                          # Futterraufe mit Heu
    deko.box(lx0 + 3.1, ly1 - 0.85, 0.55, lx0 + 4.9, ly1 - 0.45, 0.85, "Heu")
    for (sx, sy, a) in ((2.7, 2.0, "x"), (4.3, 3.4, "y"), (5.4, 1.8, "x"), (3.4, 4.5, "x"), (6.4, 4.2, "y")):
        schaf(g, lx0 + sx, ly0 + sy, a)
    # Hundehuette, Wassertonne, Heuhaufen, Hirtenstab am Wagen
    g.box(-0.6, 2.4, 0.0, 0.5, 3.3, 0.7, "Holz")
    g.box(-0.7, 2.3, 0.7, 0.6, 3.4, 0.82, "Dach grau")
    g.box(-0.2, 2.38, 0.0, 0.1, 2.4, 0.45, "Fenster")
    g.b.prism(*g.P((1.9, 2.8, 0.0))[:2], g.zb, 0.4, 0.85, 10, "Holz alt")
    g.b.prism(*g.P((1.9, 2.8, 0.0))[:2], g.zb + 0.8, 0.34, 0.04, 10, "Brunnenwasser")
    for (hx_, hy_, r_) in ((3.2, 2.4, 0.9), (4.2, 2.7, 0.7)):
        g.box(hx_ - r_, hy_ - r_, 0.0, hx_ + r_, hy_ + r_, 1.1 * r_, "Heu")
    _bm(g, (x0 - 0.15, -1.3, 0.0), (x0 - 0.15, -1.3, 1.7), 0.05, 0.05, "Holz dunkel")             # Hirtenstab (Krummstab)
    _bm(g, (x0 - 0.15, -1.3, 1.7), (x0 - 0.3, -1.3, 1.8), 0.05, 0.05, "Holz dunkel")
    return b


def bauen_ne():
    """Liefert [Muehle, Schaeferhuette] als Baugruppen."""
    a, c = Bau("nord2_muehle"), Bau("nord2_schaefer")
    muehle(a)
    wagen(c)
    return [a, c]


from stadt import wand  # noqa: E402
