"""Polybash - Tunnelportal im Gebirge ausserhalb der Spielflaeche (Osten, x > 300).

Gleis 3 laeuft vom Bahnhof ueber den Talrand in einen Einschnitt (talkessel.hoehe schneidet den Berg entlang des Gleises bis zur Sohle aus) und
verschwindet bei x = TUNNEL_X in einem Portal aus Quadern. Hinter dem Portal fuellt ein Felsblock aus 2-m-Saeulen (Oberkante = urspruengliche
Berghoehe) den ausgeschnittenen Berg wieder auf; durch ihn fuehrt der gemauerte Tunnel ueber 14 m bis zu einer dunklen Wand (das Gleis laeuft weiter)."""
import math
import random

import stadt as S
import talkessel as T
from burg import Bau

S.FARBEN.update({"Tunnel schwarz": ((0.02, 0.02, 0.025), 1.0, 0.0)})
S.FARBEN.setdefault("Stein dunkel", ((0.40, 0.38, 0.35), 0.95, 0.0))

Y0 = T.TUNNEL_Y
TX = T.TUNNEL_X
TL = T.TUNNEL_L
R, ZS = 2.3, 3.6                                  # Tunnelhalbkreis: Radius, Kampferhoehe (Scheitel 5,9 m)


def _bogen(dy):
    return ZS + math.sqrt(max(0.0, R * R - dy * dy))


def bauen_tunnel():
    b = Bau("bahn_tunnel")
    rnd = random.Random(12)
    mats = ("Stein", "Stein alt", "Stein dunkel", "Stein alt")
    # Portal: Stirnwand aus Streifen (Quader), im Bogenbereich Wolbsteine, oben Gesims
    n = int(2 * 8.6 / 0.4)
    for i in range(n):
        ya, yb = Y0 - 8.6 + i * 0.4, Y0 - 8.6 + (i + 1) * 0.4
        dy = min(abs(ya - Y0), abs(yb - Y0))
        zb = _bogen(dy) if dy < R else 0.0
        top = 8.4 - 0.9 * max(0.0, (abs((ya + yb) / 2 - Y0) - 4.0) / 4.6) ** 1.5
        z = zb
        k = 0
        while z < top - 0.05:
            h = min(rnd.uniform(0.35, 0.7) if zb == 0.0 else 0.45, top - z)
            pr = rnd.uniform(0.0, 0.09)
            b.box(TX - 0.35 - pr, ya + 0.01, z, TX + 1.3, yb - 0.01, z + h - 0.02, mats[(i + k) % 4] if zb == 0.0 else "Stein")
            z += h
            k += 1
    b.box(TX - 0.6, Y0 - 3.4, 8.4, TX + 1.5, Y0 + 3.4, 8.7, "Stein alt")                        # Gesims
    for sg in (-1, 1):                                                                          # Sockel / Rampen links und rechts
        b.box(TX - 0.5, Y0 + sg * 7.4 - 1.3, -0.3, TX + 1.3, Y0 + sg * 7.4 + 1.3, 0.5, "Stein dunkel")
    # Felsblock hinter dem Portal
    cols = 2.0
    nxc, nyc = int(TL / cols), 19
    for ix in range(nxc):
        for iy in range(nyc):
            xa, ya = TX + ix * cols, Y0 - 19.0 + iy * cols
            xc, yc = xa + cols / 2, ya + cols / 2
            top = T.hoehe_roh(xc, yc) + rnd.uniform(-0.4, 0.4)
            if top < 0.4:
                continue
            dye = min(abs(ya - Y0), abs(ya + cols - Y0)) if not (ya < Y0 < ya + cols) else 0.0
            inn = ix < (TL - 2.0) / cols and dye < R + 0.6
            zb = (_bogen(min(dye, R)) + 0.5) if inn else -0.3
            if top <= zb + 0.2:
                continue
            z = top
            k = 0
            while z > zb + 1e-6:
                z0 = max(zb, z - rnd.uniform(1.4, 2.4))
                b.box(xa + 0.02, ya + 0.02, z0, xa + cols - 0.02, ya + cols - 0.02, z, ("Bruch Fels", "Bruch Fels dunkel", "Bruch Fels hell")[(ix + iy + k) % 3] if k else "Bruch Fels")
                z = z0
                k += 1
    # gemauerter Tunnel: Seitenwaende, Gewoelbe, Abschlusswand
    L = TL - 2.0
    for sg in (-1, 1):
        b.box(TX + 1.3, Y0 + sg * R - (0.0 if sg > 0 else 0.5), 0.0, TX + L, Y0 + sg * R + (0.5 if sg > 0 else 0.0), ZS, "Stein dunkel")
    nstr = int(2 * R / 0.3)
    for i in range(nstr):
        ya = Y0 - R + i * (2 * R / nstr)
        yb = ya + 2 * R / nstr
        dy = min(abs(ya - Y0), abs(yb - Y0))
        b.box(TX + 1.3, ya, _bogen(dy) - 0.02, TX + L, yb, _bogen(dy) + 0.4, "Stein dunkel" if i % 2 else "Stein alt")
        b.box(TX + 1.3, ya, ZS - 0.02, TX + L, yb, _bogen(max(0.0, dy)) , "Tunnel schwarz") if False else None
    b.box(TX + L, Y0 - R - 0.5, 0.0, TX + L + 0.3, Y0 + R + 0.5, 6.5, "Tunnel schwarz")
    # Portal-Ausstattung: Lampe, Notrufkasten, Steinschlag
    b.box(TX - 0.45, Y0 + R + 0.4, 2.2, TX - 0.35, Y0 + R + 0.9, 2.8, "Metall")
    b.box(TX - 0.5, Y0 - R - 0.9, 1.9, TX - 0.35, Y0 - R - 0.4, 2.7, "Signal rot")
    import bahn as BA
    for k in range(9):
        a = rnd.uniform(-9.0, 9.0)
        x = TX - rnd.uniform(1.0, 6.0)
        if abs(a) < 2.4:
            continue
        BA.kegel(b, x, Y0 + a, 0.0, rnd.uniform(0.5, 1.1), rnd.uniform(0.4, 0.8), "Bruch Fels dunkel", n=6)
    return b
