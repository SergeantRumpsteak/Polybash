"""Polybash - Rathaus und Gasthaus am Marktplatz im rustikalen, alten Stil (viele kleine Polygone, kein glatter Spielzeuglook).

Bruchsteinsockel aus unregelmaessigen Quadern, Obergeschoss in Fachwerk mit Ueberhang (Kopfbaender), steiles Dach mit einzeln gesetzten, verschieden
verwitterten Ziegelreihen, Fehlstellen, Moos, Gauben, schiefe Laeden, Putzschaeden. Aufbau lokal wie in stadt.py (Fassade -y), Gebaeude sind massiv.
Wird von stadt.rathaus / stadt.gasthaus aufgerufen (lazy Import)."""
import math
import random

import stadt as S
from stadt import Lok, pbox, wand, fensterschmuck, _lok

S.FARBEN.update({
    "Dach rot alt":    ((0.46, 0.21, 0.15), 0.9, 0.0),
    "Dach rot dunkel": ((0.33, 0.15, 0.12), 0.95, 0.0),
    "Dach rot hell":   ((0.60, 0.30, 0.20), 0.85, 0.0),
    "Rathaus alt":     (S._verwittert(S.FARBEN["Rathaus"][0]), 0.95, 0.0),
    "Stein dunkel":    ((0.40, 0.38, 0.35), 0.95, 0.0),
    "Kupfer alt":      ((0.26, 0.44, 0.38), 0.7, 0.2),
    "Eisen":           ((0.12, 0.12, 0.13), 0.6, 0.5),
})
S.FARBEN.setdefault("Holz dunkel", ((0.22, 0.15, 0.10), 0.95, 0.0))


# ------------------------------------------------------------------ Bausteine
def mauerwerk(g, ach, aussen, sg, a0, a1, z0, z1, rnd, oeff=(), mats=("Stein", "Stein alt", "Stein dunkel", "Stein alt")):
    """Bruchsteinmauer: Reihen unterschiedlicher Hoehe aus Quadern verschiedener Laenge, die unregelmaessig (1..7 cm) aus der Wand ragen."""
    z = z0
    while z < z1 - 0.1:
        h = min(rnd.uniform(0.26, 0.52), z1 - z)
        a = a0 + rnd.uniform(0.0, 0.5)
        while a < a1 - 0.2:
            w = min(rnd.uniform(0.45, 1.3), a1 - a)
            hit = any(o[0] - 0.02 < a + w and o[1] + 0.02 > a and o[2] - 0.02 < z + h and o[3] + 0.02 > z for o in oeff)
            if not hit and w > 0.2:
                pr = rnd.uniform(0.012, 0.075)
                p0, p1 = sorted((aussen, aussen + sg * pr))
                pbox(g, ach, a + 0.02, a + w - 0.02, p0, p1, z + 0.015, z + h - 0.015, rnd.choice(mats))
            a += w
        z += h


def fachwerk_z(g, ach, aussen, sg, a0, a1, z0, z1, oeff, rnd, holz="Holz dunkel"):
    """Fachwerk zwischen z0 und z1: Schwelle, Rahmen, unregelmaessige Staender, Streben und Kopfbaender; spart Oeffnungen aus."""
    def pb(aa0, aa1, zz0, zz1, tief=0.09):
        p0, p1 = sorted((aussen, aussen + sg * tief))
        wand(g, ach, p0, p1, aa0, aa1, zz0, zz1, holz, oeff)
    pb(a0, a1, z0, z0 + 0.28)
    pb(a0, a1, z1 - 0.26, z1)
    zm = z0 + (z1 - z0) * rnd.uniform(0.45, 0.58)
    pb(a0, a1, zm, zm + 0.15, 0.07)
    pos = [a0]
    while pos[-1] < a1 - 1.3:
        pos.append(pos[-1] + rnd.uniform(1.1, 1.8))
    pos[-1] = a1 if a1 - pos[-2] < 2.2 else pos[-1]
    if pos[-1] < a1 - 0.3:
        pos.append(a1)
    for k, a in enumerate(pos):
        xa = a0 if k == 0 else (a1 - 0.24 if k == len(pos) - 1 else a - 0.1)
        xb = a0 + 0.24 if k == 0 else (a1 if k == len(pos) - 1 else a + 0.1)
        pb(xa, xb, z0, z1)
    for k in range(len(pos) - 1):                                                       # Streben (fallend) in freien Feldern
        pa, pc = pos[k] + 0.12, pos[k + 1] - 0.12
        if pc - pa < 0.6:
            continue
        for (za, zb) in ((z0 + 0.3, zm), (zm + 0.15, z1 - 0.26)):
            if any(o[0] < pc and o[1] > pa and o[2] < zb and o[3] > za for o in oeff):
                continue
            if rnd.random() < 0.28:
                continue
            up = rnd.random() < 0.5
            lo, hi = (za + 0.05, zb - 0.05)
            pts = [(pa, lo if up else hi), (pa + 0.16, lo if up else hi), (pc, hi if up else lo), (pc - 0.16, hi if up else lo)]
            P = [_lok(ach, aussen, sg, a, 0.1, z) for a, z in pts]
            rv = (0.0, sg, 0.0) if ach == "x" else (sg, 0.0, 0.0)
            g.poly(P, rv, holz)


def putzschaeden(g, ach, aussen, sg, a0, a1, z0, z1, oeff, rnd, n, mat="Klinker alt"):
    """Abgeplatzter Putz: unregelmaessige Flecken, durch die das Mauerwerk scheint (jeweils ein Vieleck mit 5-6 Ecken), dazu Risse und Schmutzstreifen."""
    for _ in range(n):
        bw, bh = rnd.uniform(0.4, 1.2), rnd.uniform(0.35, 1.0)
        ac = rnd.uniform(a0 + 0.5 + bw / 2, a1 - 0.5 - bw / 2) if a1 - a0 > bw + 1.2 else (a0 + a1) / 2
        zc = rnd.uniform(z0 + 0.4 + bh / 2, z1 - 0.4 - bh / 2)
        if any(o[0] - 0.15 < ac + bw / 2 and o[1] + 0.15 > ac - bw / 2 and o[2] - 0.15 < zc + bh / 2 and o[3] + 0.15 > zc - bh / 2 for o in oeff):
            continue
        k = rnd.randint(5, 7)
        pts = []
        for i in range(k):
            ang = 2 * math.pi * i / k + rnd.uniform(-0.25, 0.25)
            rr = rnd.uniform(0.7, 1.15)
            pts.append((ac + math.cos(ang) * bw / 2 * rr, zc + math.sin(ang) * bh / 2 * rr))
        P = [_lok(ach, aussen, sg, a, 0.02, z) for a, z in pts]
        rv = (0.0, sg, 0.0) if ach == "x" else (sg, 0.0, 0.0)
        g.poly(P, rv, mat)
    for _ in range(max(1, n // 2)):                                                      # Regenstreifen / Risse
        ac = rnd.uniform(a0 + 0.4, a1 - 0.4)
        zt = rnd.uniform(z1 - 1.2, z1 - 0.3)
        zb = zt - rnd.uniform(0.8, 1.8)
        if any(o[0] - 0.1 < ac + 0.1 and o[1] + 0.1 > ac - 0.1 and o[2] < zt and o[3] > zb for o in oeff):
            continue
        pts = [(ac - 0.07, zt), (ac + 0.07, zt), (ac + 0.03 + rnd.uniform(-0.06, 0.1), zb), (ac - 0.03 + rnd.uniform(-0.1, 0.06), zb)]
        P = [_lok(ach, aussen, sg, a, 0.015, z) for a, z in pts]
        rv = (0.0, sg, 0.0) if ach == "x" else (sg, 0.0, 0.0)
        g.poly(P, rv, "Schmutz")


def ziegelreihen(g, x0, x1, ye, ze, yr, zr, nrm, rnd, mats=None):
    """Dachflaeche von der Traufe (ye, ze) zum First (yr, zr), von x0 bis x1: Grundflaeche (Dachlatten) plus einzeln gesetzte Ziegelreihen, jede in
    Stuecken von 0,8..2,6 m aus verschieden stark verwitterten Ziegeln, mit leicht verschiedener Dicke; gelegentlich Fehlstellen und Moosflecken."""
    mats = mats or (("Dach rot", 4), ("Dach rot alt", 4), ("Dach rot dunkel", 2), ("Dach rot hell", 1), ("Moos", 1))
    pool = [m for m, wgt in mats for _ in range(wgt)]
    g.poly([(x0, ye, ze), (x1, ye, ze), (x1, yr, zr), (x0, yr, zr)], nrm, "Holz dunkel")
    ln = math.hypot(yr - ye, zr - ze)
    n = max(4, int(ln / 0.42))
    nl = math.hypot(nrm[1], nrm[2])
    ny, nz = nrm[1] / nl, nrm[2] / nl
    for k in range(n):
        t0, t1 = k / n, (k + 1) / n
        ya, za, yb, zb = ye + (yr - ye) * t0, ze + (zr - ze) * t0, ye + (yr - ye) * t1, ze + (zr - ze) * t1
        a = x0 + rnd.uniform(0.0, 0.8) * (k % 2)
        while a < x1 - 0.1:
            w = min(rnd.uniform(0.8, 2.6), x1 - a)
            if rnd.random() < 0.035:                                                     # Fehlstelle: Latten sichtbar
                a += w
                continue
            o = rnd.uniform(0.02, 0.07)
            m = rnd.choice(pool)
            g.poly([(a, ya + ny * o, za + nz * o), (a + w, ya + ny * o, za + nz * o), (a + w, yb + ny * (o + 0.015), zb + nz * (o + 0.015)),
                    (a, yb + ny * (o + 0.015), zb + nz * (o + 0.015))], nrm, m)
            a += w


def kamin(g, x, y, z0, z1, rnd, breit=0.9):
    """Ziegelkamin mit Absatz, ausgebrochener Krone und Kappe."""
    g.box(x - breit / 2, y - breit / 2, z0, x + breit / 2, y + breit / 2, z1, "Ziegel dunkel alt")
    g.box(x - breit / 2 - 0.08, y - breit / 2 - 0.08, z1 - 0.2, x + breit / 2 + 0.08, y + breit / 2 + 0.08, z1, "Stein alt")
    for (dx, dy) in ((-1, -1), (1, -1), (1, 1), (-1, 1)):
        h = rnd.uniform(0.0, 0.25)
        g.box(x + dx * breit / 2 - (0.15 if dx > 0 else 0), y + dy * breit / 2 - (0.15 if dy > 0 else 0), z1, x + dx * breit / 2 + (0 if dx > 0 else 0.15),
              y + dy * breit / 2 + (0 if dy > 0 else 0.15), z1 + 0.05 + h, "Ziegel dunkel alt")
    g.box(x - breit / 2 + 0.2, y - breit / 2 + 0.2, z1 - 0.3, x + breit / 2 - 0.2, y + breit / 2 - 0.2, z1 + 0.02, "Schmutz")


def giebelwand(g, sx, hd, h, rh, mat, rnd, holz="Holz dunkel"):
    """Giebeldreieck bei x = sx*w/2 (sx als Absolutkoordinate): Putz mit Fachwerk-Staendern, Spannriegel, Strebe und rundem Bodenloch."""
    xx = sx
    n = 1 if xx > 0 else -1
    g.poly([(xx, -hd, h), (xx, hd, h), (xx, 0.0, h + rh)], (n, 0.0, 0.0), mat)
    o = 0.07 * n
    for yy in (-hd * 0.66, -hd * 0.33, hd * 0.33, hd * 0.66):
        top = h + rh * (1 - abs(yy) / hd) - 0.15
        g.box(xx, yy - 0.07, h, xx + o, yy + 0.07, top, holz)
    g.box(xx, -hd * 0.6, h + rh * 0.38, xx + o, hd * 0.6, h + rh * 0.38 + 0.14, holz)
    for sgn in (-1, 1):
        g.poly([(xx + o * 0.5, sgn * hd * 0.1, h + 0.05), (xx + o * 0.5, sgn * hd * 0.1 + sgn * 0.17, h + 0.05),
                (xx + o * 0.5, sgn * hd * 0.55 + sgn * 0.17, h + rh * 0.38), (xx + o * 0.5, sgn * hd * 0.55, h + rh * 0.38)], (n, 0.0, 0.0), holz)
    kreis = [(xx + 0.03 * n, 0.45 * math.cos(2 * math.pi * k / 10), h + rh * 0.62 + 0.45 * math.sin(2 * math.pi * k / 10)) for k in range(10)]
    g.poly(kreis, (n, 0.0, 0.0), "Fenster")
    for k in range(10):
        a, c = kreis[k], kreis[(k + 1) % 10]
        g.box(min(a[0], c[0]), min(a[1], c[1]) - 0.04, min(a[2], c[2]) - 0.04, max(a[0], c[0]) + 0.05 * n, max(a[1], c[1]) + 0.04, max(a[2], c[2]) + 0.04, "Stein alt") if False else None


def steilgiebel_dach(g, w, d, h, rh, ue, rnd, mat_g="Rathaus alt"):
    """Satteldach mit Firstrichtung x: beide Flaechen mit Ziegelreihen, Ortgang- und Traufbrett, durchhaengender First, Giebelwaende mit Fachwerk."""
    hd = d / 2
    x0, x1 = -w / 2 - ue, w / 2 + ue
    s = rh / hd
    ye, ze = hd + ue, h - s * ue
    ziegelreihen(g, x0, x1, -ye, ze, 0.0, h + rh, (0.0, -rh, hd), rnd)
    ziegelreihen(g, x0, x1, ye, ze, 0.0, h + rh, (0.0, rh, hd), rnd)
    g.poly([(x0, -ye, ze), (x0, ye, ze), (x1, ye, ze), (x1, -ye, ze)], (0.0, 0.0, -1.0), "Holz dunkel")
    for sx in (-1, 1):
        giebelwand(g, sx * w / 2, hd, h, rh, mat_g, rnd)
        for sy in (-1, 1):                                                                # Ortgangbretter
            g.poly([(sx * (w / 2 + ue), sy * ye, ze), (sx * (w / 2 + ue), sy * ye, ze - 0.2), (sx * (w / 2 + ue), 0.0, h + rh - 0.2), (sx * (w / 2 + ue), 0.0, h + rh)],
                   (sx, 0.0, 0.0), "Holz dunkel")
    for sy in (-1, 1):                                                                    # Traufbretter
        g.box(x0, sy * ye - 0.05, ze - 0.2, x1, sy * ye + 0.05, ze + 0.02, "Holz dunkel")
    nseg = 6                                                                                 # First: Reihe leicht versetzter Firstziegel
    for k in range(nseg):
        xa, xb = x0 + (x1 - x0) * k / nseg, x0 + (x1 - x0) * (k + 1) / nseg
        dz = rnd.uniform(-0.04, 0.06)
        g.box(xa, -0.17, h + rh - 0.04 + dz, xb - 0.03, 0.17, h + rh + 0.2 + dz, "Dach rot dunkel" if k % 3 else "Dach rot alt")
    return lambda y: h + rh * max(0.0, 1 - abs(y) / hd)


def gaube_alt(g, ax, yf, zf, rz, rh_main, h_main, hd, rnd, br=1.25, eh=1.9, laden="Laden braun alt"):
    """Zwerchgaube (kleines Giebelhaus im Dach) auf der Vorderseite (y < 0): Putzwand mit Fachwerk, Fenster mit Laden, Satteldach, Holzbrett."""
    s = rh_main / hd
    zr = zf + eh + br * 0.75
    ze = zf + eh
    yb = lambda z: -hd * (1 - (z - h_main) / rh_main)
    g.box(ax - br, yf, zf - 0.6, ax + br, yf + 0.25, ze, "Rathaus alt")
    g.poly([(ax - br, yf, ze), (ax + br, yf, ze), (ax, yf, zr)], (0, -1, 0), "Rathaus alt")
    for sx in (-1, 1):
        g.poly([(ax + sx * br, yf, ze), (ax + sx * br, yb(ze), ze), (ax + sx * br, yb(zr), zr), (ax + sx * br, yf, ze)], (sx, 0, 0), "Rathaus alt")
    g.box(ax - br, yf - 0.02, zf - 0.6, ax - br + 0.2, yf + 0.1, ze, "Holz dunkel")
    g.box(ax + br - 0.2, yf - 0.02, zf - 0.6, ax + br, yf + 0.1, ze, "Holz dunkel")
    g.box(ax - br, yf - 0.02, ze - 0.2, ax + br, yf + 0.1, ze, "Holz dunkel")
    for sx in (-1, 1):
        g.poly([(ax + sx * (br + 0.35), yf - 0.35, ze - 0.2), (ax, yf - 0.35, zr + 0.28), (ax, yb(zr) , zr + 0.28), (ax + sx * (br + 0.35), yb(ze), ze - 0.2)],
               (sx * s, -1.0, 1.5), rnd.choice(("Dach rot", "Dach rot alt", "Dach rot dunkel")))
    fensterschmuck(g, "x", yf, -1, ax, zf + 0.7 + 0.25, 0.8, 1.1, laden, "ok" if rnd.random() < 0.7 else "kaputt", (rnd.choice(("ok", "schief")), "ok"))
    g.box(ax - 0.12, yf - 0.28, zr - 0.2, ax + 0.12, yf - 0.05, zr + 0.5, "Holz dunkel")     # Giebelspitze


# ------------------------------------------------------------------ Rathaus
def rathaus(b, cx, cy, theta):
    """Altes Rathaus (22 x 12 m): Bruchsteinerdgeschoss, ueberkragendes Fachwerkobergeschoss, steiles Ziegeldach mit Gauben und Kaminen, Uhrturm mit
    Holzglockenstube und Kupferhelm, Laube mit Rundbogenportal, Erker, Anschlagtafel, Bank, verwitterte Laeden. Fassade zum Platz (lokal -y)."""
    rnd = random.Random(31)
    g = Lok(b, cx, cy, 0.0, theta)
    hw, hd = 11.0, 6.0
    z1, z2, rh, ue = 3.6, 7.2, 5.8, 0.65
    ty0, ty1 = -hd - 1.6, -hd + 3.4                      # Turm: y-Ausdehnung, x -2.6..2.6
    ov = 0.42                                            # Ueberhang des Obergeschosses vorn
    # Kern
    g.box(-hw, -hd, -1.0, hw, hd, z1, "Stein dunkel")
    g.box(-hw - 0.15, -hd - 0.15, -0.5, hw + 0.15, hd + 0.15, 0.55, "Stein dunkel")                # Sockelvorsprung
    g.box(-hw, -hd - ov, z1, hw, hd, z2, "Rathaus alt")
    g.box(-hw - 0.1, -hd - ov, z1 - 0.1, hw + 0.1, hd + 0.1, z1 + 0.06, "Holz dunkel")             # Deckenbalken-Schwelle
    for x in [-10.4 + 1.6 * k for k in range(14)]:                                                 # Balkenkoepfe + Kopfbaender unter dem Ueberhang
        if abs(x) < 2.9:
            continue
        g.box(x - 0.11, -hd - ov, z1 - 0.5, x + 0.11, -hd, z1 - 0.1, "Holz dunkel")
        g.poly([(x - 0.1, -hd, z1 - 0.1), (x + 0.1, -hd, z1 - 0.1), (x + 0.1, -hd - ov, z1 - 0.05), (x - 0.1, -hd - ov, z1 - 0.05)], (0, 0, -1), "Holz dunkel")
    # Fenster-Lage
    xs_f = [-9.4, -6.8, -4.2, 4.2, 6.8, 9.4]
    ze = 1.9
    zo = 5.35
    oeff_eg = [(x - 0.55, x + 0.55, ze - 0.8, ze + 0.8) for x in xs_f] + [(-2.6, 2.6, -1, z2)]
    oeff_og = [(x - 0.6, x + 0.6, zo - 0.85, zo + 0.85) for x in xs_f] + [(-2.6, 2.6, -1, z2)]
    mauerwerk(g, "x", -hd, -1, -hw, hw, -0.3, z1, rnd, oeff_eg)
    mauerwerk(g, "x", hd, 1, -hw, hw, -0.3, z1, rnd, [(x - 0.55, x + 0.55, ze - 0.8, ze + 0.8) for x in (-7.5, -2.5, 2.5, 7.5)])
    mauerwerk(g, "y", -hw, -1, -hd, hd, -0.3, z1, rnd, [(y - 0.55, y + 0.55, ze - 0.8, ze + 0.8) for y in (-2.5, 2.5)])
    mauerwerk(g, "y", hw, 1, -hd, hd, -0.3, z1, rnd, [(y - 0.55, y + 0.55, ze - 0.8, ze + 0.8) for y in (-2.5, 2.5)])
    fachwerk_z(g, "x", -hd - ov, -1, -hw, hw, z1, z2, oeff_og, rnd)
    fachwerk_z(g, "x", hd, 1, -hw, hw, z1, z2, [(x - 0.55, x + 0.55, zo - 0.85, zo + 0.85) for x in (-7.5, -2.5, 2.5, 7.5)], rnd)
    for sx in (-1, 1):
        fachwerk_z(g, "y", sx * hw, sx, -hd, hd, z1, z2, [(y - 0.6, y + 0.6, zo - 0.85, zo + 0.85) for y in (-2.5, 2.5)], rnd)
    for x in xs_f:
        fensterschmuck(g, "x", -hd, -1, x, ze, 1.0, 1.5, "Laden braun alt", rnd.choice(("ok", "ok", "ok", "kaputt", "bretter")), (rnd.choice(("ok", "ok", "schief", "fehlt")), rnd.choice(("ok", "ok", "schief"))))
        fensterschmuck(g, "x", -hd - ov, -1, x, zo, 1.1, 1.7, "Laden braun alt", rnd.choice(("ok", "ok", "ok", "kaputt")), (rnd.choice(("ok", "ok", "schief")), rnd.choice(("ok", "fehlt", "ok"))))
    for x in (-7.5, -2.5, 2.5, 7.5):
        fensterschmuck(g, "x", hd, 1, x, ze, 1.0, 1.5, "Laden braun alt", rnd.choice(("ok", "kaputt", "bretter")), ("ok", rnd.choice(("ok", "fehlt"))))
        fensterschmuck(g, "x", hd, 1, x, zo, 1.1, 1.7, "Laden braun alt", rnd.choice(("ok", "kaputt")), (rnd.choice(("ok", "schief")), "ok"))
    for sx in (-1, 1):
        for y in (-2.5, 2.5):
            fensterschmuck(g, "y", sx * hw, sx, y, ze, 1.0, 1.5, "Laden braun alt", rnd.choice(("ok", "bretter")), ("ok", "ok"))
            fensterschmuck(g, "y", sx * hw, sx, y, zo, 1.1, 1.7, "Laden braun alt", "ok", (rnd.choice(("ok", "schief")), "ok"))
    putzschaeden(g, "x", -hd - ov, -1, -hw, hw, z1 + 0.3, z2, oeff_og, rnd, 7, "Ziegel dunkel alt")
    putzschaeden(g, "x", hd, 1, -hw, hw, z1 + 0.3, z2, [], rnd, 6, "Ziegel dunkel alt")
    putzschaeden(g, "y", hw, 1, -hd, hd, z1 + 0.3, z2, [], rnd, 4, "Ziegel dunkel alt")
    putzschaeden(g, "y", -hw, -1, -hd, hd, z1 + 0.3, z2, [], rnd, 4, "Ziegel dunkel alt")
    # Sockel-Schmutz und Moos
    for (ach, aus, sg, a0, a1) in (("x", -hd, -1, -hw, hw), ("x", hd, 1, -hw, hw), ("y", -hw, -1, -hd, hd), ("y", hw, 1, -hd, hd)):
        p0, p1 = sorted((aus + sg * 0.08, aus + sg * 0.1))
        pbox(g, ach, a0, a1, p0, p1, -0.1, 0.5, "Schmutz")
        for _ in range(5):
            a = rnd.uniform(a0 + 1, a1 - 1)
            p0, p1 = sorted((aus + sg * 0.08, aus + sg * 0.12))
            pbox(g, ach, a, a + rnd.uniform(0.4, 1.2), p0, p1, 0.0, rnd.uniform(0.3, 0.8), "Moos")
    # Dach
    rzf = steilgiebel_dach(g, 2 * hw, 2 * hd, z2, rh, ue, rnd)
    for ax in (-7.0, 7.0):
        yf = -hd + 0.5
        gaube_alt(g, ax, yf, rzf(yf), rzf, rh, z2, hd, rnd)
    kamin(g, -7.5, 1.5, z2 + rh * 0.55, z2 + rh + 2.4, rnd)
    kamin(g, 6.5, 2.0, z2 + rh * 0.55, z2 + rh + 2.1, rnd, 1.0)
    # Erker (Ostecke vorn, Obergeschoss)
    ex, ey = hw - 2.3, -hd - ov
    g.box(ex - 1.1, ey - 0.9, z1 + 0.3, ex + 1.1, ey, z2 - 0.4, "Rathaus alt")
    g.box(ex - 1.1, ey - 0.9, z1 + 0.05, ex + 1.1, ey, z1 + 0.35, "Holz dunkel")
    for k in range(3):
        g.box(ex - 1.0 + k * 0.75, ey - 0.88, z1 - 0.45, ex - 0.8 + k * 0.75, ey - 0.1, z1 + 0.05, "Holz dunkel")
    fensterschmuck(g, "x", ey - 0.9, -1, ex, zo, 1.2, 1.4, "Laden braun alt", "ok", ("ok", "schief"))
    g.poly([(ex - 1.3, ey - 1.1, z2 - 0.4), (ex + 1.3, ey - 1.1, z2 - 0.4), (ex, ey - 0.95, z2 + 0.9), (ex, ey, z2 + 0.9)], (0, -1, 1), "Kupfer alt")
    # Turm
    tc = (ty0 + ty1) / 2
    tw = 2.6
    g.box(-tw, ty0, -1.0, tw, ty1, 8.2, "Stein dunkel")
    mauerwerk(g, "x", ty0, -1, -tw, tw, -0.3, 8.2, rnd, [(-1.4, 1.4, -1, 3.8)])
    mauerwerk(g, "y", -tw, -1, ty0, -hd - ov, -0.3, 8.2, rnd)
    mauerwerk(g, "y", tw, 1, ty0, -hd - ov, -0.3, 8.2, rnd)
    for k in range(3):
        g.box(-tw - 0.12, ty0 - 0.12, 5.0 + k * 0.0, tw + 0.12, ty1, 5.0, "Stein") if False else None
    g.box(-tw - 0.15, ty0 - 0.15, 8.2, tw + 0.15, ty1 + 0.15, 8.5, "Stein alt")                    # Gesims
    for sx in (-1, 1):
        for sy in (ty0 - 0.15, ty1 + 0.15):
            g.box(sx * tw - 0.18 - (0.15 if sx > 0 else 0), sy - 0.18, 8.5, sx * tw + 0.18 - (0 if sx > 0 else -0.15), sy + 0.18, 8.9, "Stein alt")
    # Portal mit Rundbogen
    bx0, bx1 = -1.25, 1.25
    g.box(bx0 - 0.4, ty0 - 0.2, -0.2, bx0, ty0, 3.6, "Stein")
    g.box(bx1, ty0 - 0.2, -0.2, bx1 + 0.4, ty0, 3.6, "Stein")
    arc = [(math.cos(math.pi * k / 10) * (-1.25 if False else 1.25), ty0 - 0.2, 3.6 + math.sin(math.pi * k / 10) * 1.25) for k in range(11)]
    for k in range(10):
        a, c = arc[k], arc[k + 1]
        g.poly([(a[0], ty0 - 0.22, a[2]), (c[0], ty0 - 0.22, c[2]), (c[0] * 1.3, ty0 - 0.22, 3.6 + (c[2] - 3.6) * 1.3), (a[0] * 1.3, ty0 - 0.22, 3.6 + (a[2] - 3.6) * 1.3)], (0, -1, 0), "Stein alt")
    tor = [(bx0, ty0 + 0.02, 0.0), (bx1, ty0 + 0.02, 0.0)] + [(c[0], ty0 + 0.02, c[2]) for c in arc[:0:-1]][:0] + [(c[0], ty0 + 0.02, c[2]) for c in arc]
    g.poly([(bx0, ty0 + 0.02, 0.0), (bx1, ty0 + 0.02, 0.0)] + [(a[0], ty0 + 0.02, a[2]) for a in arc[1:-1]], (0, -1, 0), "Tuer")
    for k in range(5):                                                                              # Eisenbaender
        g.box(bx0, ty0 - 0.03, 0.4 + k * 0.7, bx1, ty0 + 0.0, 0.5 + k * 0.7, "Eisen")
    g.box(-0.04, ty0 - 0.05, 0.0, 0.04, ty0, 3.5, "Eisen")
    for k, wdt in enumerate((0.55, 0.5, 0.58)):                                                     # unregelmaessige Treppe
        g.box(-2.3 + rnd.uniform(-0.1, 0.1), ty0 - 0.45 * (k + 1), -0.4, 2.3 + rnd.uniform(-0.1, 0.1), ty0, 0.5 - 0.17 * (k + 1) + 0.17, rnd.choice(("Stein", "Stein alt")))
    # Uhren
    for (nx, ny, px, py) in ((0, -1, 0.0, ty0), (0, 1, 0.0, ty1), (-1, 0, -tw, tc), (1, 0, tw, tc)):
        zc, rr = 6.0, 1.05
        ring = [(rr * math.cos(2 * math.pi * k / 14), rr * math.sin(2 * math.pi * k / 14)) for k in range(14)]
        if nx:
            g.poly([(px + nx * 0.07, tc + a, zc + c) for a, c in ring], (nx, 0, 0), "Uhr")
            g.box(px, tc - rr - 0.1, zc - rr - 0.1, px + nx * 0.12, tc + rr + 0.1, zc - rr, "Stein alt")
            g.box(px, tc - rr - 0.1, zc + rr, px + nx * 0.12, tc + rr + 0.1, zc + rr + 0.1, "Stein alt")
            g.box(px, tc - rr - 0.1, zc - rr, px + nx * 0.12, tc - rr, zc + rr, "Stein alt")
            g.box(px, tc + rr, zc - rr, px + nx * 0.12, tc + rr + 0.1, zc + rr, "Stein alt")
            g.box(px + nx * 0.07, tc - 0.04, zc, px + nx * 0.1, tc + 0.04, zc + 0.8, "Eisen")
            g.box(px + nx * 0.07, tc, zc - 0.04, px + nx * 0.1, tc + 0.55, zc + 0.04, "Eisen")
        else:
            g.poly([(a, py + ny * 0.07, zc + c) for a, c in ring], (0, ny, 0), "Uhr")
            g.box(-rr - 0.1, py, zc - rr - 0.1, rr + 0.1, py + ny * 0.12, zc - rr, "Stein alt")
            g.box(-rr - 0.1, py, zc + rr, rr + 0.1, py + ny * 0.12, zc + rr + 0.1, "Stein alt")
            g.box(-rr - 0.1, py, zc - rr, -rr, py + ny * 0.12, zc + rr, "Stein alt")
            g.box(rr, py, zc - rr, rr + 0.1, py + ny * 0.12, zc + rr, "Stein alt")
            g.box(-0.04, py + ny * 0.07, zc, 0.04, py + ny * 0.1, zc + 0.8, "Eisen")
            g.box(0.0, py + ny * 0.07, zc - 0.04, 0.55, py + ny * 0.1, zc + 0.04, "Eisen")
    # Holzglockenstube (Fachwerk, offene Schallarkaden mit Glocke) 8.9 .. 12.6
    zb0, zb1 = 8.9, 12.4
    hh = 2.1
    for sx in (-1, 1):
        for sy in (-1, 1):
            px = sx * (tw - 0.3)
            py = tc + sy * (tw - 0.3)
            g.box(px - 0.18, py - 0.18, zb0, px + 0.18, py + 0.18, zb1, "Holz dunkel")
    for (lo, hi, mid) in ((-tw + 0.1, tw - 0.1, None),):
        for sy in (-1, 1):
            py = tc + sy * (tw - 0.3)
            g.box(lo, py - 0.12, zb0, hi, py + 0.12, zb0 + 0.9, "Holz alt")
            g.box(lo, py - 0.12, zb1 - 0.35, hi, py + 0.12, zb1, "Holz dunkel")
        for sx in (-1, 1):
            px = sx * (tw - 0.3)
            g.box(px - 0.12, tc - tw + 0.1, zb0, px + 0.12, tc + tw - 0.1, zb0 + 0.9, "Holz alt")
            g.box(px - 0.12, tc - tw + 0.1, zb1 - 0.35, px + 0.12, tc + tw - 0.1, zb1, "Holz dunkel")
    for sy in (-1, 1):
        py = tc + sy * (tw - 0.3)
        g.poly([(-0.9, py, zb0 + 0.9), (-0.9, py, zb0 + 2.2), (0.0, py, zb0 + 2.8), (0.9, py, zb0 + 2.2), (0.9, py, zb0 + 0.9)], (0, sy, 0), "Fenster")
    g.prism(0.0, tc, zb0 + 1.1, 0.5, 0.6, 10, "Kupfer alt")                                       # Glocke
    g.box(-0.1, tc - 0.1, zb0 + 1.6, 0.1, tc + 0.1, zb1 - 0.35, "Eisen")
    g.box(-tw - 0.2, ty0 - 0.2, zb1, tw + 0.2, ty1 + 0.2, zb1 + 0.2, "Holz dunkel")
    # steiler Helm
    apex = (0.0, tc, 21.0)
    ecken = [(-tw - 0.6, ty0 - 0.6, zb1 + 0.2), (tw + 0.6, ty0 - 0.6, zb1 + 0.2), (tw + 0.6, ty1 + 0.6, zb1 + 0.2), (-tw - 0.6, ty1 + 0.6, zb1 + 0.2)]
    for k in range(4):
        a, c = ecken[k], ecken[(k + 1) % 4]
        mx, my = (a[0] + c[0]) / 2, (a[1] + c[1]) / 2
        for j in range(6):
            t0, t1 = j / 6, (j + 1) / 6
            pa = (a[0] + (apex[0] - a[0]) * t0, a[1] + (apex[1] - a[1]) * t0, a[2] + (apex[2] - a[2]) * t0)
            pb_ = (c[0] + (apex[0] - c[0]) * t0, c[1] + (apex[1] - c[1]) * t0, c[2] + (apex[2] - c[2]) * t0)
            pc = (c[0] + (apex[0] - c[0]) * t1, c[1] + (apex[1] - c[1]) * t1, c[2] + (apex[2] - c[2]) * t1)
            pd = (a[0] + (apex[0] - a[0]) * t1, a[1] + (apex[1] - a[1]) * t1, a[2] + (apex[2] - a[2]) * t1)
            g.poly([pa, pb_, pc, pd], (mx - apex[0], my - apex[1], 4.0), rnd.choice(("Kupfer alt", "Dach Kupfer", "Kupfer alt", "Moos")))
    g.poly(ecken[::-1], (0, 0, -1), "Holz dunkel")
    g.box(-0.05, tc - 0.05, 21.0, 0.05, tc + 0.05, 22.4, "Eisen")                                  # Spitze: Kugel und Wetterfahne
    g.prism(0.0, tc, 21.5, 0.22, 0.4, 8, "Kupfer alt")
    g.box(0.05, tc - 0.02, 22.0, 0.9, tc + 0.02, 22.5, "Eisen")
    # Anschlagtafel, Bank, Laterne, Fass
    g.box(-5.8, -hd - 0.1, 1.2, -4.3, -hd, 2.5, "Holz alt")
    for k in range(4):
        g.box(-5.7 + 0.35 * k, -hd - 0.14, 1.4 + 0.2 * (k % 2), -5.45 + 0.35 * k, -hd - 0.1, 2.2 - 0.1 * (k % 3), "Pappe" if k % 2 else "Putz weiss alt")
    g.box(4.0, -hd - 0.9, 0.0, 6.4, -hd - 0.4, 0.45, "Holz alt")
    g.box(4.0, -hd - 0.5, 0.45, 6.4, -hd - 0.4, 0.95, "Holz alt")
    for sx in (4.2, 6.2):
        g.box(sx - 0.06, -hd - 0.85, 0.0, sx + 0.06, -hd - 0.45, 0.45, "Holz dunkel")
    g.box(-3.2, -hd - 0.12, 2.6, -3.1, -hd - 1.0, 2.7, "Eisen")
    g.box(-3.3, -hd - 1.05, 2.1, -3.0, -hd - 0.75, 2.6, "Schild gelb")
    g.prism(-6.4, -hd - 0.7, 0.0, 0.38, 0.9, 8, "Faesser rot")
    return g


# ------------------------------------------------------------------ Gasthaus
def gasthaus(b, cx, cy, theta):
    """Altes Gasthaus (18 x 10 m): Putz-Erdgeschoss auf Bruchsteinsockel, Fachwerkobergeschoss mit Ueberhang, grosses Ziegeldach mit zwei Gauben und
    dickem Kamin, Vordach auf Staendern, Wirtshausausleger mit Schild, Biertische, Fassbank, Holzstapel, schiefe Laeden. Fassade lokal -y."""
    rnd = random.Random(47)
    g = Lok(b, cx, cy, 0.0, theta)
    hw, hd = 9.0, 5.0
    z1, z2, rh, ue = 3.3, 6.5, 4.8, 0.6
    ov = 0.38
    g.box(-hw, -hd, -1.0, hw, hd, z1, "Putz gelb alt")
    g.box(-hw - 0.1, -hd - 0.1, -0.5, hw + 0.1, hd + 0.1, 0.95, "Stein dunkel")
    mauerwerk(g, "x", -hd - 0.1, -1, -hw - 0.1, hw + 0.1, -0.3, 0.95, rnd, [(-1.0, 1.0, -1, 3)])
    mauerwerk(g, "x", hd + 0.1, 1, -hw - 0.1, hw + 0.1, -0.3, 0.95, rnd)
    mauerwerk(g, "y", -hw - 0.1, -1, -hd, hd, -0.3, 0.95, rnd)
    mauerwerk(g, "y", hw + 0.1, 1, -hd, hd, -0.3, 0.95, rnd)
    g.box(-hw, -hd - ov, z1, hw, hd, z2, "Putz gelb alt")
    g.box(-hw - 0.1, -hd - ov, z1 - 0.1, hw + 0.1, hd + 0.1, z1 + 0.06, "Holz dunkel")
    for x in [-8.0 + 1.6 * k for k in range(11)]:
        g.box(x - 0.1, -hd - ov, z1 - 0.45, x + 0.1, -hd, z1 - 0.1, "Holz dunkel")
    xs = (-6.3, -3.4, 3.4, 6.3)
    ze, zo = 1.75, 4.8
    oeg = [(x - 0.55, x + 0.55, ze - 0.7, ze + 0.7) for x in xs] + [(-0.95, 0.95, -1, 2.3)]
    oog = [(x - 0.6, x + 0.6, zo - 0.8, zo + 0.8) for x in xs] + [(-0.6, 0.6, zo - 0.8, zo + 0.8)]
    fachwerk_z(g, "x", -hd - ov, -1, -hw, hw, z1, z2, oog, rnd)
    fachwerk_z(g, "x", hd, 1, -hw, hw, z1, z2, [(x - 0.55, x + 0.55, zo - 0.8, zo + 0.8) for x in (-6.0, 0.0, 6.0)], rnd)
    for sx in (-1, 1):
        fachwerk_z(g, "y", sx * hw, sx, -hd, hd, z1, z2, [(-0.55, 0.55, zo - 0.8, zo + 0.8)], rnd)
    for x in xs:
        fensterschmuck(g, "x", -hd, -1, x, ze, 1.1, 1.4, "Laden gruen alt", rnd.choice(("ok", "ok", "kaputt")), (rnd.choice(("ok", "schief")), rnd.choice(("ok", "ok", "fehlt"))))
        fensterschmuck(g, "x", -hd - ov, -1, x, zo, 1.2, 1.6, "Laden gruen alt", rnd.choice(("ok", "ok", "kaputt")), (rnd.choice(("ok", "ok", "schief")), "ok"))
    fensterschmuck(g, "x", -hd - ov, -1, 0.0, zo, 1.2, 1.6, "Laden gruen alt", "ok", ("ok", "ok"))
    for x in (-6.0, 0.0, 6.0):
        fensterschmuck(g, "x", hd, 1, x, ze, 1.0, 1.3, "Laden gruen alt", rnd.choice(("ok", "bretter")), ("ok", "schief"))
        fensterschmuck(g, "x", hd, 1, x, zo, 1.1, 1.5, "Laden gruen alt", "ok", ("schief", "ok"))
    for sx in (-1, 1):
        fensterschmuck(g, "y", sx * hw, sx, 0.0, zo, 1.1, 1.5, "Laden gruen alt", "ok", ("ok", "fehlt"))
        fensterschmuck(g, "y", sx * hw, sx, 0.0, ze, 1.0, 1.3, "Laden gruen alt", "kaputt", ("ok", "ok"))
    putzschaeden(g, "x", -hd, -1, -hw, hw, 0.9, z1, oeg, rnd, 6, "Ziegel dunkel alt")
    putzschaeden(g, "x", -hd - ov, -1, -hw, hw, z1 + 0.3, z2, oog, rnd, 5, "Ziegel dunkel alt")
    putzschaeden(g, "x", hd, 1, -hw, hw, 0.9, z2, [], rnd, 8, "Ziegel dunkel alt")
    for sx in (-1, 1):
        putzschaeden(g, "y", sx * hw, sx, -hd, hd, 0.9, z2, [], rnd, 5, "Ziegel dunkel alt")
    rzf = steilgiebel_dach(g, 2 * hw, 2 * hd, z2, rh, ue, rnd, "Putz gelb alt")
    for ax in (-4.0, 4.5):
        yf = -hd + 0.4
        gaube_alt(g, ax, yf, rzf(yf), rzf, rh, z2, hd, rnd, br=1.0, eh=1.7, laden="Laden gruen alt")
    kamin(g, hw - 1.6, 0.8, z2 + rh * 0.5, z2 + rh + 2.2, rnd, 1.3)
    kamin(g, -hw + 2.0, -0.8, z2 + rh * 0.5, z2 + rh + 1.7, rnd, 0.8)
    # Tuer mit Vordach
    g.box(-0.95, -hd - 0.02, 0.0, 0.95, -hd + 0.0, 2.3, "Tuer")
    g.box(-1.05, -hd - 0.06, 0.0, -0.95, -hd + 0.0, 2.45, "Holz dunkel")
    g.box(0.95, -hd - 0.06, 0.0, 1.05, -hd + 0.0, 2.45, "Holz dunkel")
    g.box(-1.05, -hd - 0.06, 2.3, 1.05, -hd + 0.0, 2.45, "Holz dunkel")
    for k in range(4):
        g.box(-1.5 - 0.1 * (k % 2), -hd - 0.45 * (k + 1), -0.3, 1.5 + 0.1 * ((k + 1) % 2), -hd, 0.55 - 0.15 * (k + 1) + 0.15, rnd.choice(("Stein", "Stein alt")))
    for sx in (-1.7, 1.7):
        g.box(sx - 0.12, -hd - 1.9, 0.0, sx + 0.12, -hd - 1.66, 2.9, "Holz dunkel")
    g.box(-1.9, -hd - 2.0, 2.9, 1.9, -hd - 1.56, 3.05, "Holz dunkel")
    g.poly([(-2.2, -hd - 2.2, 2.9), (2.2, -hd - 2.2, 2.9), (2.2, -hd - ov, 3.45), (-2.2, -hd - ov, 3.45)], (0, -1, 1), "Dach rot alt")
    for k in range(8):
        a = -2.2 + 0.55 * k
        g.poly([(a, -hd - 2.2, 2.92), (a + 0.45, -hd - 2.2, 2.92), (a + 0.45, -hd - ov, 3.47), (a, -hd - ov, 3.47)], (0, -1, 1), rnd.choice(("Dach rot", "Dach rot dunkel", "Dach rot alt")))
    # Ausleger + Schild (ohne Schrift: gemaltes Bierfass-Symbol)
    g.box(4.4, -hd - ov - 0.12, 4.2, 4.5, -hd - ov, 5.5, "Eisen")
    g.box(4.4, -hd - ov - 1.6, 5.4, 4.5, -hd - ov, 5.5, "Eisen")
    g.box(4.3, -hd - ov - 1.5, 4.2, 4.6, -hd - ov - 1.3, 5.3, "Holz dunkel") if False else None
    kr = 0.5
    ring = [(4.45 + 0.04, -hd - ov - 1.4 + kr * math.cos(2 * math.pi * k / 10), 4.6 + kr * math.sin(2 * math.pi * k / 10)) for k in range(10)]
    g.poly(ring, (1, 0, 0), "Markt rot")
    g.poly([(p[0] - 0.12, p[1], p[2]) for p in ring][::-1], (-1, 0, 0), "Markt rot")
    g.prism(4.45, -hd - ov - 1.4, 4.45, 0.2, 0.3, 8, "Holz alt")
    # Biertische + Baenke vor dem Haus, Fass, Holzstapel
    for tx in (-5.2, 5.6):
        g.box(tx - 0.8, -hd - 2.7, 0.76, tx + 0.8, -hd - 1.7, 0.82, "Holz alt")
        for ex in (-0.65, 0.65):
            g.box(tx + ex - 0.05, -hd - 2.6, 0.0, tx + ex + 0.05, -hd - 1.8, 0.76, "Holz dunkel")
        for yy in (-hd - 3.15, -hd - 1.25):
            g.box(tx - 0.8, yy - 0.15, 0.4, tx + 0.8, yy + 0.15, 0.45, "Holz alt")
            for ex in (-0.65, 0.65):
                g.box(tx + ex - 0.04, yy - 0.12, 0.0, tx + ex + 0.04, yy + 0.12, 0.4, "Holz dunkel")
    for k, (fx, fy) in enumerate(((-7.6, -hd - 0.5), (-6.9, -hd - 0.45), (-7.25, -hd - 1.15))):
        g.prism(fx, fy, 0.0, 0.34, 0.95, 8, "Faesser rot" if k % 2 == 0 else "Holz alt")
    for k in range(4):
        for l_ in range(4 - k):
            g.box(hw - 3.4 + 0.3 * k + 0.55 * l_ * 0.0, hd + 0.1 + 0.0, 0.0 + 0.3 * k, hw - 0.4 - 0.55 * 0, hd + 0.62, 0.3 * (k + 1), "Holz alt") if l_ == 0 else None
    return g
