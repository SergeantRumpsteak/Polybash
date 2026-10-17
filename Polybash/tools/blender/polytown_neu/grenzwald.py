"""Polybash - Felsen- und Baumguertel direkt hinter dem Rand der Spielflaeche (0..300 m), der in das Gebirge uebergeht.

Das Bergland beginnt am Talrand mit sanften Auslaeufern (talkessel.hoehe_roh: nur wenige Meter in den ersten 15 m) - ohne diesen Guertel
koennte man einfach hinauslaufen. Deshalb:
  * Sperrriegel (Abstand d = 0,6 .. 5 m vom Rand): zwei gegeneinander versetzte Reihen grosser Felsbloecke (Radius 1,4 .. 2,2 m, Abstand 2,2 m);
    die Hindernisquader ueberlappen sich, es bleibt keine Luecke - auch nicht in den abgerundeten Ecken.
  * Dichter Nadel-/Mischwald dahinter (d = 4 .. 32 m, Reihen mit wachsendem Abstand) mit Stamm-Hindernissen,
  * zunehmend grosse Felsen und Felsgruppen (d bis 45 m), die in die Felswaende des Gebirges (talkessel.berg_netz) uebergehen,
  * steile Haenge bekommen statt Baeumen Felsbrocken.
Einzige Luecke: der Bahneinschnitt (y = 27, Gleis 3 Richtung Tunnel, talkessel.TUNNEL_*), der nach 52 m am Tunnelportal (Felsblock) endet.
Alle Teile stehen auf der Berggelaende-Hoehe (talkessel.hoehe)."""
import math

import burg as B
import stadt as S
import talkessel as T
from burg import Bau
from wald import tanne, laubbaum

S.FARBEN.update({"Fels Block": ((0.47, 0.44, 0.41), 0.95, 0.0), "Fels Block dunkel": ((0.33, 0.31, 0.31), 0.95, 0.0),
                 "Fels Block hell": ((0.58, 0.55, 0.50), 0.95, 0.0)})

TAL = T.TAL
SPERR_D = (1.3, 3.7)                 # Abstand der beiden Felsreihen vom Talrand
TIEF = 34.0                          # Tiefe des Waldguertels
SCHRITT = 2.2                        # Abstand der Sperrfelsen entlang des Rands


def _punkt(s, d):
    """Punkt im Abstand d vom Talquadrat (Randkurve mit abgerundeten Ecken), s = Laufstrecke ab (0, -d) gegen den Uhrzeigersinn."""
    a = math.pi / 2 * d
    seiten = [TAL, a, TAL, a, TAL, a, TAL, a]
    s %= (4 * TAL + 4 * a)
    for k, ln in enumerate(seiten):
        if s <= ln:
            break
        s -= ln
    if k == 0:
        return (s, -d)
    if k == 1:
        ang = -math.pi / 2 + s / d
        return (TAL + d * math.cos(ang), d * math.sin(ang))
    if k == 2:
        return (TAL + d, s)
    if k == 3:
        ang = s / d
        return (TAL + d * math.cos(ang), TAL + d * math.sin(ang))
    if k == 4:
        return (TAL - s, TAL + d)
    if k == 5:
        ang = math.pi / 2 + s / d
        return (d * math.cos(ang), TAL + d * math.sin(ang))
    if k == 6:
        return (-d, TAL - s)
    ang = math.pi + s / d
    return (d * math.cos(ang), d * math.sin(ang))


def _umfang(d):
    return 4 * TAL + 2 * math.pi * d


def _bahn_luecke(x, y, d):
    return x > TAL - 1.0 and abs(y - T.TUNNEL_Y) < 9.5 and d < 55.0


def fels(b, x, y, zb, r, hs, rnd, mat=None, bx=True):
    """Felsblock: unregelmaessiges Ikosaeder (12 Ecken), unten eingesunken; Radius r, Hoehenfaktor hs."""
    g = (1 + 5 ** 0.5) / 2
    ecken = [(-1, g, 0), (1, g, 0), (-1, -g, 0), (1, -g, 0), (0, -1, g), (0, 1, g), (0, -1, -g), (0, 1, -g), (g, 0, -1), (g, 0, 1), (-g, 0, -1), (-g, 0, 1)]
    flaechen = [(0, 11, 5), (0, 5, 1), (0, 1, 7), (0, 7, 10), (0, 10, 11), (1, 5, 9), (5, 11, 4), (11, 10, 2), (10, 7, 6), (7, 1, 8),
                (3, 9, 4), (3, 4, 2), (3, 2, 6), (3, 6, 8), (3, 8, 9), (4, 9, 5), (2, 4, 11), (6, 2, 10), (8, 6, 7), (9, 8, 1)]
    ph = rnd(1) * 6.283
    c, s = math.cos(ph), math.sin(ph)
    v = []
    for i, (ex, ey, ez) in enumerate(ecken):
        n = math.sqrt(ex * ex + ey * ey + ez * ez)
        k = 0.72 + 0.5 * rnd(10 + i)
        px, py, pz = ex / n * k, ey / n * k, ez / n * k
        v.append((x + r * (px * c - py * s) * (1.0 + 0.25 * (rnd(3) - 0.5)), y + r * (px * s + py * c) * (1.0 + 0.25 * (rnd(4) - 0.5)),
                  zb + r * hs * pz * 0.92 + r * hs * 0.30))
    v = [(px, py, max(pz, zb - 0.6 * r * hs)) for (px, py, pz) in v]
    m = mat or ("Fels Block" if rnd(5) < 0.55 else ("Fels Block dunkel" if rnd(5) < 0.85 else "Fels Block hell"))
    b.add(v, flaechen, m)
    if bx:
        e = r * 0.72
        b.bx.append((x - e, y - e, zb, x + e, y + e, zb + max(1.2, r * hs * 1.25)))


def _kleiner_baum(b, x, y, zb, rnd):
    """Nadelbaum mit nur zwei Kronenstufen (spart Flaechen im dichten Guertel); Stamm blockiert."""
    hs = 0.85 + 0.9 * rnd(1)
    b.prism(x, y, zb - 0.25, 0.26, 2.8 * hs + 0.25, 5, "Stamm")
    mat = "Tanne" if rnd(2) < 0.65 else "Tanne hell"
    for k, (r, z0, hh) in enumerate(((2.1, 1.9, 3.0), (1.3, 3.8, 2.8))):
        z0 *= hs
        hh *= hs
        n = 6
        ph = rnd(3 + k) * 2.0
        ring = [(x + r * hs ** 0.5 * (0.85 + 0.3 * rnd(10 + i + 7 * k)) * math.cos(2 * math.pi * i / n + ph),
                 y + r * hs ** 0.5 * (0.85 + 0.3 * rnd(10 + i + 7 * k)) * math.sin(2 * math.pi * i / n + ph), zb + z0) for i in range(n)]
        b.add(ring + [(x, y, zb + z0 + hh)], [tuple(range(n - 1, -1, -1))] + [(i, (i + 1) % n, n) for i in range(n)], mat)
    b.bx.append((x - 0.27, y - 0.27, zb, x + 0.27, y + 0.27, zb + 2.8 * hs))


def _rnd_fn(seed):
    return lambda i, s=seed: T._h01(s, i, 4711)


def objekte():
    """Liste (x, y, art, r, d): 'fels' mit Radius r, 'baum', 'laub'; deterministisch."""
    out = []
    # --- Sperriegel: zwei versetzte Felsreihen
    for ri, d in enumerate(SPERR_D):
        n = int(_umfang(d) / SCHRITT)
        for k in range(n):
            s = (k + 0.5 * ri) * _umfang(d) / n
            x, y = _punkt(s, d)
            h = T._h01(k, ri, 91)
            if _bahn_luecke(x, y, d):
                continue
            x += (T._h01(k, ri, 92) - 0.5) * 0.5
            y += (T._h01(k, ri, 93) - 0.5) * 0.5
            out.append((x, y, "fels", 1.5 + 0.7 * h, d))
    # --- Bahneinschnitt: Felsen beidseits der Schlucht (Gleis 3) bis zum Tunnelportal, damit man nicht seitlich hinter den Riegel gelangt
    for sg in (-1, 1):
        for ri in range(2):
            yy = T.TUNNEL_Y + sg * (10.4 + 2.3 * ri)
            k = 0
            xx = TAL + 0.5 + 1.1 * ri
            while xx < T.TUNNEL_X + T.TUNNEL_L + 4.0:
                h = T._h01(k, ri + 5 * (sg + 1), 95)
                out.append((xx, yy + (T._h01(k, ri, 96) - 0.5) * 0.5, "fels", 1.5 + 0.7 * h, 5.0))
                xx += SCHRITT
                k += 1
    # --- Waldguertel in Reihen, nach aussen lockerer; Haenge steil -> Fels
    d = 4.6
    reihe = 0
    while d < TIEF:
        sp = 2.3 + d * 0.085
        n = int(_umfang(d) / sp)
        pr = 0.95 - 0.55 * B.smoothstep(12.0, TIEF, d)
        for k in range(n):
            u = T._h01(k, reihe, 301)
            if u > pr:
                continue
            s = (k + 0.5 * (reihe % 2) + (T._h01(k, reihe, 302) - 0.5) * 0.7) * _umfang(d) / n
            dd = d + (T._h01(k, reihe, 303) - 0.5) * 1.8
            x, y = _punkt(s, dd)
            if _bahn_luecke(x, y, dd):
                continue
            q = T._h01(k, reihe, 304)
            art = "baum" if q < 0.72 else ("laub" if q < 0.88 else "fels")
            if art == "fels":
                out.append((x, y, "fels", 1.2 + 1.2 * T._h01(k, reihe, 305), dd))
            else:
                out.append((x, y, art, 0.0, dd))
        d += 2.6
        reihe += 1
    # --- grosse Felsgruppen, die zum Gebirge ueberleiten (je weiter aussen, desto groesser)
    d = 8.0
    reihe = 0
    while d < 46.0:
        sp = 15.0 - 5.0 * B.smoothstep(8.0, 46.0, d)
        n = int(_umfang(d) / sp)
        for k in range(n):
            if T._h01(k, reihe, 401) > 0.7:
                continue
            s = (k + T._h01(k, reihe, 402)) * _umfang(d) / n
            dd = d + (T._h01(k, reihe, 403) - 0.5) * 4.0
            x, y = _punkt(s, dd)
            if _bahn_luecke(x, y, dd):
                continue
            r = (2.2 + 2.6 * B.smoothstep(8.0, 46.0, dd)) * (0.8 + 0.5 * T._h01(k, reihe, 404))
            out.append((x, y, "fels", r, dd))
            if T._h01(k, reihe, 405) < 0.6:                                   # Begleitbloecke
                a = T._h01(k, reihe, 406) * 6.283
                out.append((x + 0.9 * r * math.cos(a), y + 0.9 * r * math.sin(a), "fels", r * 0.55, dd))
        d += 6.0
        reihe += 1
    return out


def bauen_guertel():
    """Baugruppen des Randguertels: Felsen und Baeume in zwei Gruppen."""
    bf, bw = Bau("grenze_felsen"), Bau("grenze_wald")
    for i, (x, y, art, r, d) in enumerate(objekte()):
        zb = T.hoehe(x, y)
        rnd = _rnd_fn(i * 37 + int(x) * 3 + int(y) * 5)
        if art == "fels":
            hs = 0.85 + 0.55 * rnd(2) + (0.35 if d < 6.0 else 0.0)
            fels(bf, x, y, zb, r, hs, rnd)
        elif art == "baum":
            if T.glatte_neigung(x, y, 3.0) < 0.62:
                fels(bf, x, y, zb, 1.1 + 0.9 * rnd(2), 1.1, rnd)
            else:
                _kleiner_baum(bw, x, y, zb, rnd)
        else:
            laubbaum(bw, x, y, zb, rnd)
    return [bf, bw]
