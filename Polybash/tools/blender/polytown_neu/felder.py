"""Getreidefelder westlich des Bauernhofs (x 3..33, y 66..95): vier Felder (reifer Weizen, Gerste, junger Weizen, Stoppelfeld mit Strohballen),
Feldweg, Vogelscheuche, Hecken. Die Halme sind einzeln modellierte Spitzen (je Buschel zwei Halme und eine Aehre) in Reihen mit Rauschen in der
Dichte und Hoehe; sie folgen der Wiesenhoehe und sind kein Hindernis (man laeuft durch das Korn). Wird von stadt.baue_alles() eingebunden."""
import math
import random

import burg as B
import stadt as S
import talkessel as T
import umgebung as U
import bahn as BA
from burg import Bau

S.FARBEN.update({"Acker": ((0.30, 0.21, 0.13), 1.0, 0.0), "Weizen reif": ((0.76, 0.64, 0.27), 1.0, 0.0), "Weizen hell": ((0.84, 0.74, 0.38), 1.0, 0.0),
                 "Gerste": ((0.70, 0.62, 0.32), 1.0, 0.0), "Aehre": ((0.88, 0.74, 0.34), 0.9, 0.0), "Weizen gruen": ((0.38, 0.55, 0.20), 1.0, 0.0),
                 "Weizen gruen hell": ((0.48, 0.64, 0.25), 1.0, 0.0), "Stoppel": ((0.62, 0.54, 0.30), 1.0, 0.0), "Hecke": ((0.18, 0.29, 0.12), 1.0, 0.0),
                 "Hecke hell": ((0.26, 0.38, 0.15), 1.0, 0.0)})
for _n, _c in (("Pfad", ((0.52, 0.46, 0.36), 0.95, 0.0)), ("Holz alt", ((0.40, 0.31, 0.22), 0.95, 0.0)), ("Holz dunkel", ((0.22, 0.15, 0.10), 0.95, 0.0)),
               ("Heu", ((0.74, 0.62, 0.28), 1.0, 0.0)), ("Stroh", ((0.80, 0.70, 0.35), 1.0, 0.0)), ("Stoff rot", ((0.55, 0.14, 0.12), 1.0, 0.0)), ("Stoff blau", ((0.22, 0.30, 0.45), 1.0, 0.0))):
    S.FARBEN.setdefault(_n, _c)

BELEGT = ((3.0, 68.5, 34.0, 95.0),)
WEG_Y = (74.4, 77.6)                                   # Feldweg (west-ost)
# (Mitte x, y, Halbe Laenge entlang der Reihen, halbe Breite, Reihenwinkel in Grad, Frucht)
FELDER = ((11.0, 85.6, 7.2, 7.4, 82.0, "weizen"), (25.6, 85.6, 6.6, 7.4, 8.0, "gerste"),
          (11.0, 71.6, 7.0, 2.6, 2.0, "jung"), (25.6, 71.6, 6.6, 2.6, -3.0, "stoppel"))


def _lokal(f):
    cx, cy, hu, hv, ang, _ = f
    a = math.radians(ang)
    return cx, cy, hu, hv, (math.cos(a), math.sin(a)), (-math.sin(a), math.cos(a))


def boden(f):
    cx, cy, hu, hv, d, p = _lokal(f)
    g = Bau("acker")
    nu, nv = max(2, int(2 * hu / 2.2)), max(2, int(2 * hv / 2.2))
    V = {}
    for i in range(nu + 1):
        for j in range(nv + 1):
            u, v = -hu + 2 * hu * i / nu, -hv + 2 * hv * j / nv
            x, y = cx + u * d[0] + v * p[0], cy + u * d[1] + v * p[1]
            V[(i, j)] = (x, y, U.gelaende_hoehe(x, y) + 0.03)
    for i in range(nu):
        for j in range(nv):
            g.add([V[(i, j)], V[(i + 1, j)], V[(i + 1, j + 1)], V[(i, j + 1)]], [(0, 1, 2, 3)], "Acker")
    return g


def _spitze(b, x, y, z0, hoehe, lean, r, mat):
    """Halm: dreiseitige Spitze mit leichter Neigung (lean = (dx, dy) am Gipfel)."""
    ph = (x * 12.9898 + y * 78.233) % 6.28
    base = [(x + r * math.cos(ph + 2.094 * k), y + r * math.sin(ph + 2.094 * k), z0) for k in range(3)]
    b.add(base + [(x + lean[0], y + lean[1], z0 + hoehe)], [(0, 1, 3), (1, 2, 3), (2, 0, 3)], mat)


def bestellen(f, rnd):
    """Halme in Reihen. Rueckgabe: Bau."""
    cx, cy, hu, hv, d, p = _lokal(f)
    kind = f[5]
    g = Bau("korn_" + kind)
    sp_v, sp_u = (0.52, 0.40) if kind in ("weizen", "gerste") else (0.55, 0.42)
    k = 0
    v = -hv + 0.5
    while v < hv - 0.4:
        u = -hu + 0.5
        while u < hu - 0.4:
            n = T.fbm((cx + u) / 5.0 + v * 0.02, (cy + v) / 5.0, T.SEED + 301, 2)           # Dichte und Hoehe als Rauschen
            if rnd.random() < (0.97 if kind != "stoppel" else 0.9) * min(1.0, 0.45 + 1.1 * n):
                uu = u + rnd.uniform(-0.22, 0.22)
                vv = v + rnd.uniform(-0.18, 0.18)
                x, y = cx + uu * d[0] + vv * p[0], cy + uu * d[1] + vv * p[1]
                z0 = U.gelaende_hoehe(x, y) + 0.03
                wind = (0.10 * math.sin(x / 7.0 + y / 11.0), 0.07 * math.cos(y / 6.0))
                if kind == "stoppel":
                    _spitze(g, x, y, z0, rnd.uniform(0.10, 0.2), (0.0, 0.0), 0.035, "Stoppel")
                elif kind == "jung":
                    for j in range(2):
                        _spitze(g, x + 0.05 * j, y, z0, rnd.uniform(0.25, 0.4) * (0.7 + 0.5 * n), (rnd.uniform(-0.05, 0.05) + wind[0] * 0.3, rnd.uniform(-0.05, 0.05)), 0.04,
                                "Weizen gruen" if rnd.random() < 0.6 else "Weizen gruen hell")
                else:
                    h = (0.95 if kind == "weizen" else 0.80) * (0.75 + 0.5 * n) * rnd.uniform(0.9, 1.1)
                    mat = ("Weizen reif" if rnd.random() < 0.6 else "Weizen hell") if kind == "weizen" else ("Gerste" if rnd.random() < 0.7 else "Weizen hell")
                    for j in range(2):
                        hh = h * (1.0 if j == 0 else 0.82)
                        lx, ly = wind[0] + rnd.uniform(-0.08, 0.08), wind[1] + rnd.uniform(-0.08, 0.08)
                        ox = 0.05 * j
                        _spitze(g, x + ox, y, z0, hh * 0.86, (lx * 0.85, ly * 0.85), 0.04, mat)
                        # Aehre: kleiner, dickerer Kegel auf dem Halm
                        zt = z0 + hh * 0.78
                        ph = rnd.uniform(0, 6.28)
                        ring = [(x + ox + lx * 0.74 + 0.055 * math.cos(ph + 2.094 * q), y + ly * 0.74 + 0.055 * math.sin(ph + 2.094 * q), zt) for q in range(3)]
                        g.add(ring + [(x + ox + lx, y + ly, zt + hh * 0.28)], [(0, 1, 3), (1, 2, 3), (2, 0, 3)], "Aehre")
                k += 1
            u += sp_u
        v += sp_v
    return g


def hecke(b, x0, y0, x1, y1, rnd):
    ln = math.hypot(x1 - x0, y1 - y0)
    n = int(ln / 1.7)
    for i in range(n + 1):
        t = i / max(n, 1)
        x, y = x0 + (x1 - x0) * t + rnd.uniform(-0.2, 0.2), y0 + (y1 - y0) * t + rnd.uniform(-0.2, 0.2)
        r = rnd.uniform(0.8, 1.15)
        z0 = U.gelaende_hoehe(x, y)
        m = 7
        ph = rnd.uniform(0, 6.28)
        ring = [(x + r * rnd.uniform(0.85, 1.15) * math.cos(ph + 2 * math.pi * k / m), y + r * rnd.uniform(0.85, 1.15) * math.sin(ph + 2 * math.pi * k / m), z0 + 0.35) for k in range(m)]
        b.add(ring + [(x, y, z0 + r * 1.35 + 0.35), (x, y, z0 - 0.1)], [(k, (k + 1) % m, m) for k in range(m)] + [((k + 1) % m, k, m + 1) for k in range(m)],
              "Hecke" if rnd.random() < 0.65 else "Hecke hell")


def vogelscheuche(b, x, y):
    z = U.gelaende_hoehe(x, y)
    b.box(x - 0.04, y - 0.04, z, x + 0.04, y + 0.04, z + 2.0, "Holz alt")
    b.box(x - 0.7, y - 0.03, z + 1.45, x + 0.7, y + 0.03, z + 1.52, "Holz alt")
    b.box(x - 0.28, y - 0.12, z + 0.85, x + 0.28, y + 0.12, z + 1.5, "Stoff blau")        # Hemd
    b.box(x - 0.66, y - 0.05, z + 1.12, x - 0.27, y + 0.05, z + 1.46, "Stoff blau")
    b.box(x + 0.27, y - 0.05, z + 1.12, x + 0.66, y + 0.05, z + 1.46, "Stoff blau")
    b.prism(x, y, z + 1.52, 0.17, 0.26, 7, "Stroh")                                      # Kopf
    b.prism(x, y, z + 1.78, 0.28, 0.04, 8, "Holz dunkel")                                  # Hut
    b.prism(x, y, z + 1.8, 0.15, 0.22, 8, "Holz dunkel")
    for sx in (-1, 1):                                                                    # Stroh an Armen und Saum
        b.box(x + sx * 0.66 - 0.04, y - 0.04, z + 1.02, x + sx * 0.66 + 0.04, y + 0.04, z + 1.14, "Stroh")
    b.box(x - 0.2, y - 0.1, z + 0.7, x + 0.2, y + 0.1, z + 0.86, "Stroh")
    b.bx.append((x - 0.1, y - 0.1, z, x + 0.1, y + 0.1, z + 2.0))


def bauen_felder():
    rnd = random.Random(2468)
    out = []
    boeden = Bau("acker")
    for f in FELDER:
        boeden.merge(boden(f))
        out.append(bestellen(f, rnd))
    deko = Bau("feld_deko")
    # Feldweg (folgt dem Gelaende), Zufahrt vom Hof
    U.pfad(deko, [(3.0, sum(WEG_Y) / 2), (35.5, sum(WEG_Y) / 2)], WEG_Y[1] - WEG_Y[0], 0.035, "Pfad", hf=U.gelaende_hoehe, schritt=2.5)
    # Hecken: Westrand, Nordrand, zwischen den Feldern
    hecke(deko, 3.6, 94.0, 33.0, 94.4, rnd)
    hecke(deko, 3.4, 68.8, 3.5, 74.0, rnd)
    hecke(deko, 3.4, 78.0, 3.5, 94.0, rnd)
    hecke(deko, 18.4, 78.2, 18.4, 93.4, rnd)
    hecke(deko, 33.4, 69.0, 33.4, 74.0, rnd)
    hecke(deko, 18.4, 69.0, 18.4, 74.0, rnd)
    vogelscheuche(deko, 11.5, 86.0)
    z = U.gelaende_hoehe
    for (x, y, n) in ((22.0, 71.2, 2), (24.6, 72.4, 1), (27.4, 70.6, 2), (29.6, 72.0, 1)):    # Strohballen auf dem Stoppelfeld
        for k in range(n):
            BA.zyl_x(deko, x - 0.6, x + 0.6, y, z(x, y) + 0.6 + k * 1.2, 0.6, "Stroh" if k % 2 else "Heu", n=10)
        deko.bx.append((x - 0.6, y - 0.6, z(x, y), x + 0.6, y + 0.6, z(x, y) + 1.2 * n))
    # Feldscheune fuer Geraete: Holzunterstand am Weg
    ux, uy = 31.0, 79.6
    for sx in (0, 1):
        for sy in (0, 1):
            deko.box(ux + sx * 3.0 - 0.1, uy + sy * 2.4 - 0.1, 0.0, ux + sx * 3.0 + 0.1, uy + sy * 2.4 + 0.1, 2.3 - 0.35 * sy, "Holz alt")
    deko.add([(ux - 0.5, uy - 0.3, 2.3), (ux + 3.5, uy - 0.3, 2.3), (ux + 3.5, uy + 2.7, 1.95), (ux - 0.5, uy + 2.7, 1.95)], [(0, 1, 2, 3)], "Dach rot alt")
    deko.add([(ux - 0.5, uy + 2.7, 1.95), (ux + 3.5, uy + 2.7, 1.95), (ux + 3.5, uy - 0.3, 2.3), (ux - 0.5, uy - 0.3, 2.3)], [(0, 1, 2, 3)], "Holz dunkel")
    heuballen_(deko, ux + 1.5, uy + 1.2)
    return [boeden] + out + [deko]


def heuballen_(b, x, y):
    BA.zyl_x(b, x - 0.6, x + 0.6, y, 0.6, 0.6, "Heu", n=10)
    b.bx.append((x - 0.6, y - 0.6, 0.0, x + 0.6, y + 0.6, 1.2))
