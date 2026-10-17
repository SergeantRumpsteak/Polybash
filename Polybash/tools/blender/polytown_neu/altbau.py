"""Polybash - gemeinsame 'Altbau'-Bausteine fuer alle zivilen Gebaeude (kein glatter Spielzeuglook): Ziegel-/Schieferbelag aus einzeln gesetzten, verschieden
verwitterten Stuecken auf jeder Dachflaeche, Bruchstein-Sockel, Fenstersturz und Gewaende, Sparrenkoepfe unter der Traufe, abgeplatzter Putz, Kamine.
Wird von stadt.dach / stadt.satteldach / stadt.aussenwand / stadt.fensterschmuck / stadt.haus aufgerufen."""
import math
import random

import stadt as S

_f = S.FARBEN


def _abgeleitet(name, basis, f):
    if basis in _f and name not in _f:
        (r, g, b), rough, met = _f[basis]
        _f[name] = ((min(1.0, r * f), min(1.0, g * f), min(1.0, b * f)), rough, met)


S.FARBEN.update({
    "Dach rot alt":    ((0.46, 0.21, 0.15), 0.9, 0.0),
    "Dach rot dunkel": ((0.33, 0.15, 0.12), 0.95, 0.0),
    "Dach rot hell":   ((0.60, 0.30, 0.20), 0.85, 0.0),
})
S.FARBEN.setdefault("Dach Schiefer", ((0.22, 0.24, 0.27), 0.8, 0.0))
for _b, _n in (("Dach grau", "Dach grau dunkel"), ("Dach Schiefer", "Dach Schiefer dunkel")):
    _abgeleitet(_n, _b, 0.72)
for _b, _n in (("Dach grau", "Dach grau hell"), ("Dach Schiefer", "Dach Schiefer hell")):
    _abgeleitet(_n, _b, 1.25)
S.FARBEN.update({
    "Dach rot braun":   ((0.40, 0.25, 0.17), 0.9, 0.0),
    "Dach rot orange":  ((0.72, 0.38, 0.20), 0.85, 0.0),
    "Dach rot grau":    ((0.40, 0.29, 0.27), 0.95, 0.0),
    "Dach ocker":       ((0.66, 0.50, 0.30), 0.9, 0.0),
    "Dach schwarz":     ((0.14, 0.12, 0.12), 0.9, 0.0),
    "Dach grau braun":  ((0.34, 0.30, 0.27), 0.9, 0.0),
    "Dach grau gruen":  ((0.26, 0.31, 0.28), 0.9, 0.0),
})
S.FARBEN.setdefault("Stein dunkel", ((0.40, 0.38, 0.35), 0.95, 0.0))

_ROT = (("Dach rot", 3), ("Dach rot alt", 3), ("Dach rot dunkel", 2), ("Dach rot hell", 1), ("Dach rot braun", 2), ("Dach rot orange", 1),
        ("Dach rot grau", 1), ("Dach ocker", 1), ("Dach schwarz", 1), ("Moos", 1))
_GRAU = (("Dach grau", 3), ("Dach grau alt", 3), ("Dach grau dunkel", 3), ("Dach grau hell", 1), ("Dach grau braun", 2), ("Dach grau gruen", 1),
         ("Dach schwarz", 1), ("Dach rot alt", 1), ("Moos", 1))
POOLS = {
    "Dach rot": _ROT, "Dach rot alt": _ROT, "Ziegel": _ROT, "Ziegel alt": _ROT, "Ziegel dunkel": _ROT, "Ziegel dunkel alt": _ROT, "Dach grau": _GRAU, "Dach grau alt": _GRAU,
    "Dach Schiefer": (("Dach Schiefer", 4), ("Dach Schiefer dunkel", 3), ("Dach Schiefer hell", 1), ("Dach grau gruen", 2), ("Dach schwarz", 1), ("Moos", 1)),
}


def _rnd(g, salt=0):
    return random.Random(int(g.cx * 100) * 31 + int(g.cy * 100) * 7 + len(g.b.f) + salt)


def _schnitt(P, zc):
    """Schnitt des konvexen Vielecks P mit der Ebene z = zc: zwei Punkte (oder None)."""
    pts = []
    n = len(P)
    for i in range(n):
        a, b = P[i], P[(i + 1) % n]
        if (a[2] - zc) * (b[2] - zc) < 0.0:
            t = (zc - a[2]) / (b[2] - a[2])
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, zc))
        elif abs(a[2] - zc) < 1e-9 and abs(b[2] - zc) < 1e-9:
            return a, b
    if len(pts) >= 2:
        return pts[0], pts[1]
    return None


def dachbelag(g, P, nrm, dm):
    """Belegt die ebene Dachflaeche P (lokal, Normale nrm) mit einzeln gesetzten Ziegel-/Schieferstuecken in Reihen von der Traufe zum First."""
    pool = POOLS.get(dm)
    if not pool or nrm[2] < 0.2:
        return
    zs = [p[2] for p in P]
    z0, z1 = min(zs), max(zs)
    if z1 - z0 < 0.25:
        return
    rnd = _rnd(g)
    pl = [m for m, w in pool for _ in range(w)]
    ln = math.sqrt(nrm[0] ** 2 + nrm[1] ** 2 + nrm[2] ** 2)
    nx, ny, nz = nrm[0] / ln, nrm[1] / ln, nrm[2] / ln
    hx, hy = -nrm[1], nrm[0]
    if abs(hx) + abs(hy) < 1e-9:
        hx, hy = 1.0, 0.0
    key = lambda p: p[0] * hx + p[1] * hy
    nr = max(3, min(40, int(round((z1 - z0) / 0.3))))
    haupt = [rnd.choice(pl) for _ in range(3)]                                      # drei vorherrschende Toene dieses Dachs
    flicken = [(rnd.randrange(nr), rnd.randint(1, 4), rnd.random(), rnd.uniform(0.15, 0.4), rnd.choice(pl)) for _ in range(rnd.randint(2, 5))]
    for k in range(nr):
        za, zb = z0 + (z1 - z0) * (k + 0.02) / nr, z0 + (z1 - z0) * (k + 0.98) / nr
        sa, sb = _schnitt(P, za), _schnitt(P, zb)
        if not sa or not sb:
            continue
        a0, b0 = sorted(sa, key=key)
        a1, b1 = sorted(sb, key=key)
        lng = math.hypot(b0[0] - a0[0], b0[1] - a0[1])
        t = (0.0 if k % 2 == 0 else rnd.uniform(0.0, 0.8) / max(lng, 0.5))
        while t < 0.999:
            w = rnd.uniform(0.5, 1.8) / max(lng, 0.5)
            t1 = min(1.0, t + w)
            if rnd.random() > 0.04 and t1 - t > 0.02:
                o = rnd.uniform(0.02, 0.07)
                o2 = o + 0.015
                lerp = lambda A, B, u, off: (A[0] + (B[0] - A[0]) * u + nx * off, A[1] + (B[1] - A[1]) * u + ny * off, A[2] + (B[2] - A[2]) * u + nz * off)
                m = rnd.choice(haupt) if rnd.random() < 0.45 else rnd.choice(pl)
                for (fk, fh, ft, fw, fm) in flicken:
                    if fk <= k < fk + fh and ft <= t < ft + fw:
                        m = fm
                g.poly([lerp(a0, b0, t, o), lerp(a0, b0, t1, o), lerp(a1, b1, t1, o2), lerp(a1, b1, t, o2)], nrm, m)
            t = t1


class Deko:
    """Proxy um Lok: Quader werden gebaut, aber nicht als Hindernis (bx) registriert - feine Reliefs (Quader, Gewaende) sollen weder begehbar noch im Weg sein."""

    def __init__(self, g):
        self.__dict__["_g"] = g

    def __getattr__(self, n):
        return getattr(self._g, n)

    def box(self, *a):
        n = len(self._g.b.bx)
        self._g.box(*a)
        del self._g.b.bx[n:]


class DachLok:
    """Proxy um Lok: jede Dachflaeche mit Material dm (Normale nach oben) bekommt zusaetzlich den Ziegel-/Schieferbelag."""

    def __init__(self, g, dm):
        self.__dict__["_g"], self.__dict__["_dm"] = g, dm

    def __getattr__(self, n):
        return getattr(self._g, n)

    def poly(self, verts, richtung, mat):
        self._g.poly(verts, richtung, mat)
        if mat == self._dm and richtung[2] > 0.2:
            dachbelag(self._g, verts, richtung, mat)


def sparren(g, form, w, d, H, rh, e):
    """Sparrenkoepfe unter der Traufe (alle 0,7 m), an allen Traufkanten der Dachform."""
    hw, hd = w / 2.0, d / 2.0
    if form in ("x", "walm"):
        zE = H - rh / hd * e
    elif form == "y":
        zE = H - rh / hw * e
    elif form == "mansard":
        zE = H - 2.3 / 1.3 * e
    else:
        zE = H - rh / d * e
    kanten = []
    if form in ("x", "walm", "mansard", "pult"):
        kanten += [("x", -hd - e + 0.02)] + ([("x", hd + e - 0.02)] if form != "pult" else [])
    if form in ("y", "walm"):
        kanten += [("y", -hw - e + 0.02), ("y", hw + e - 0.02)]
    for ach, c in kanten:
        L = hw + e if ach == "x" else hd + e
        n = int(2 * L / 0.7)
        for i in range(n + 1):
            a = -L + 0.1 + (2 * L - 0.2) * i / max(1, n)
            if ach == "x":
                g.box(a - 0.05, c - 0.07, zE - 0.16, a + 0.05, c + 0.07, zE - 0.02, "Holz dunkel")
            else:
                g.box(c - 0.07, a - 0.05, zE - 0.16, c + 0.07, a + 0.05, zE - 0.02, "Holz dunkel")


def sockel(g, ach, aussen, sg, a0, a1, oeff):
    """Bruchsteinsockel (bis 0,85 m) aus Quadern wechselnder Groesse statt glatter Platte."""
    import rustik
    rnd = _rnd(g, int(aussen * 10) + int(a0 * 10))
    rustik.mauerwerk(g, ach, aussen, sg, a0, a1, -0.05, 0.85, rnd, [o for o in oeff if o[2] < 0.9])


def fenster_zierde(g, ach, aussen, sg, ac, zc, w, h):
    """Sturz mit Schlussstein und wechselnde Gewaende-Quader (lange/kurze) beiderseits des Fensters."""
    def pb(a0, a1, o0, o1, z0, z1, m):
        p0, p1 = sorted((aussen + sg * o0, aussen + sg * o1))
        S.pbox(g, ach, a0, a1, p0, p1, z0, z1, m)
    g = Deko(g)
    zl, zh, al, ah = zc - h / 2, zc + h / 2, ac - w / 2, ac + w / 2
    pb(al - 0.16, ah + 0.16, 0.0, 0.1, zh + 0.09, zh + 0.27, "Stein alt")
    pb(ac - 0.1, ac + 0.1, 0.0, 0.13, zh + 0.09, zh + 0.33, "Stein")
    z = zl - 0.02
    k = 0
    while z < zh + 0.05:
        hh = 0.22 if k % 2 == 0 else 0.4
        for (a, b) in ((al - 0.16, al - 0.09), (ah + 0.09, ah + 0.16)):
            pb(a, b, 0.0, 0.08, z, min(z + hh - 0.03, zh + 0.07), "Stein alt" if k % 2 else "Stein")
        z += hh
        k += 1


def putz_flecken(g, ach, aussen, sg, a0, a1, z1, mat, oeff):
    """Abgeplatzter Putz und Regenstreifen an einer Aussenwand (Anzahl nach Wandlaenge)."""
    import rustik
    n = int((a1 - a0) / 3.5)
    if n < 1 or z1 < 2.5:
        return
    rnd = _rnd(g, int(aussen * 10) + int(a0 * 10) + 5)
    brick = "Klinker" in mat or "Ziegel" in mat
    rustik.putzschaeden(g, ach, aussen, sg, a0, a1, 0.95, z1 - 0.2, oeff, rnd, n, "Stein dunkel" if brick else "Klinker alt")


def scheunen_latten(g, ach, aussen, sg, a0, a1, z0, z1):
    """Senkrechte Deckleisten auf einer Bretterwand."""
    a = a0 + 0.3
    rnd = _rnd(g, int(aussen * 10))
    while a < a1 - 0.2:
        p0, p1 = sorted((aussen, aussen + sg * 0.05))
        S.pbox(g, ach, a, a + 0.1, p0, p1, z0, z1 - rnd.uniform(0.0, 0.3), "Holz dunkel")
        a += rnd.uniform(0.5, 0.75)
