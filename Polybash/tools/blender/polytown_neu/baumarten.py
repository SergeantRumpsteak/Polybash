"""Polybash - detailreiche Baumarten (Low-Poly mit deutlich mehr Flaechen als wald.py/_alt): Eiche, Birke, Fichte, Waldkiefer, Pappel und Obstbaum.

Aufbau: Staemme und Aeste sind Rohre aus mehreren Ringen (Wurzelanlauf, Verjuengung, Astgabeln), die Kronen sind unregelmaessige Kugelklumpen
(Breiten-/Laengenkreise mit Rauschen) bzw. mehrstufige Kegelschuerzen. Alle Funktionen haben die Signatur art(b, x, y, zb, rnd) mit rnd(i) -> 0..1;
nur der Stamm blockiert (b.bx), die Kronen beginnen ueber Kopfhoehe. baum() waehlt die Art; eiche/birke/... koennen einzeln benutzt werden."""
import math

import stadt as S

S.FARBEN.update({
    "Rinde": ((0.26, 0.18, 0.12), 0.95, 0.0), "Birke": ((0.86, 0.85, 0.80), 0.9, 0.0), "Birke dunkel": ((0.10, 0.10, 0.10), 0.9, 0.0),
    "Kiefer Stamm": ((0.46, 0.26, 0.15), 0.95, 0.0), "Kiefer Nadeln": ((0.19, 0.30, 0.14), 0.95, 0.0), "Kiefer Nadeln hell": ((0.27, 0.38, 0.17), 0.95, 0.0),
    "Laub dunkel": ((0.13, 0.26, 0.10), 0.95, 0.0), "Laub gelb": ((0.52, 0.44, 0.14), 0.95, 0.0), "Birkenlaub": ((0.42, 0.55, 0.20), 0.95, 0.0),
    "Birkenlaub hell": ((0.55, 0.65, 0.26), 0.95, 0.0), "Pappellaub": ((0.22, 0.36, 0.14), 0.95, 0.0), "Apfel": ((0.72, 0.12, 0.10), 0.7, 0.0),
    "Fichte dunkel": ((0.07, 0.17, 0.10), 0.95, 0.0), "Fichte": ((0.11, 0.24, 0.14), 0.95, 0.0), "Fichte hell": ((0.17, 0.32, 0.17), 0.95, 0.0),
})
for _k, _v in (("Laub herbst", ((0.45, 0.36, 0.12), 0.95, 0.0)), ("Tanne", ((0.10, 0.22, 0.13), 0.95, 0.0)), ("Tanne hell", ((0.16, 0.30, 0.16), 0.95, 0.0)), ("Stamm", ((0.30, 0.20, 0.12), 0.95, 0.0)), ("Laub", ((0.20, 0.36, 0.14), 0.95, 0.0)), ("Laub hell", ((0.30, 0.45, 0.17), 0.95, 0.0))):
    S.FARBEN.setdefault(_k, _v)


# ------------------------------------------------------------------ Werkzeuge
def _sub(a, c):
    return (a[0] - c[0], a[1] - c[1], a[2] - c[2])


def _cross(a, c):
    return (a[1] * c[2] - a[2] * c[1], a[2] * c[0] - a[0] * c[2], a[0] * c[1] - a[1] * c[0])


def _norm(a):
    ln = math.sqrt(a[0] ** 2 + a[1] ** 2 + a[2] ** 2) or 1.0
    return (a[0] / ln, a[1] / ln, a[2] / ln)


def rohr(b, stuetz, mat, n=7, kappe=True, ph=0.0):
    """Rohr durch die Stuetzpunkte [(x, y, z, r), ...]: pro Punkt ein n-Eck senkrecht zur lokalen Richtung; Kappe am Ende (und Boden am Anfang)."""
    ringe = []
    m = len(stuetz)
    for i, (x, y, z, r) in enumerate(stuetz):
        a = stuetz[max(0, i - 1)]
        c = stuetz[min(m - 1, i + 1)]
        d = _norm(_sub(c[:3], a[:3]))
        ref = (1.0, 0.0, 0.0) if abs(d[0]) < 0.9 else (0.0, 1.0, 0.0)
        u = _norm(_cross(ref, d))
        v = _cross(d, u)
        ringe.append([(x + r * (math.cos(ph + 2 * math.pi * k / n) * u[0] + math.sin(ph + 2 * math.pi * k / n) * v[0]),
                       y + r * (math.cos(ph + 2 * math.pi * k / n) * u[1] + math.sin(ph + 2 * math.pi * k / n) * v[1]),
                       z + r * (math.cos(ph + 2 * math.pi * k / n) * u[2] + math.sin(ph + 2 * math.pi * k / n) * v[2])) for k in range(n)])
    verts = [p for r_ in ringe for p in r_]
    faces = []
    for i in range(m - 1):
        for k in range(n):
            k2 = (k + 1) % n
            faces.append((i * n + k, i * n + k2, (i + 1) * n + k2, (i + 1) * n + k))
    if kappe:
        faces.append(tuple((m - 1) * n + k for k in range(n)))
        faces.append(tuple(range(n - 1, -1, -1)))
    b.add(verts, faces, mat)


def klumpen(b, cx, cy, cz, rx, ry, rz, mat, rnd, s, lat=4, lon=9, jit=0.22):
    """Unregelmaessiger Kugelklumpen (Laubkrone): lat Breitenkreise, lon Laengenkreise, Radius pro Punkt mit Rauschen; Normalen nach aussen."""
    verts = [(cx, cy, cz + rz * (1.0 + 0.1 * (rnd(s) - 0.5)))]
    for j in range(1, lat + 1):
        th = math.pi * j / (lat + 1)
        for k in range(lon):
            f = 1.0 - jit / 2 + jit * rnd(s + 7 * j + 3 * k + 1)
            ph = 2 * math.pi * (k + 0.3 * (j % 2)) / lon
            verts.append((cx + rx * f * math.sin(th) * math.cos(ph), cy + ry * f * math.sin(th) * math.sin(ph), cz + rz * f * math.cos(th)))
    verts.append((cx, cy, cz - rz * 0.85))
    faces = [(0, 1 + k, 1 + (k + 1) % lon) for k in range(lon)]
    for j in range(lat - 1):
        for k in range(lon):
            a, c = 1 + j * lon + k, 1 + j * lon + (k + 1) % lon
            faces.append((a, a + lon, c + lon, c))
    last = 1 + (lat - 1) * lon
    bt = len(verts) - 1
    faces += [(bt, last + (k + 1) % lon, last + k) for k in range(lon)]
    b.add(verts, faces, mat)


def schuerze(b, x, y, z, r, h, mat, rnd, s, n=10, haenge=0.35, stufen=2):
    """Fichtenetage: Kegel mit zackigem Rand und innerem Ring (haengende Zweige): oben Spitze, unten offener Ring."""
    ph = rnd(s) * 6.28
    spitze = (x, y, z + h)
    inner = [(x + r * 0.55 * math.cos(ph + 2 * math.pi * i / n), y + r * 0.55 * math.sin(ph + 2 * math.pi * i / n), z + h * 0.45) for i in range(n)]
    aussen = []
    for i in range(n):
        f = (1.0 if i % 2 == 0 else 0.72) * (0.88 + 0.24 * rnd(s + i + 1))
        aussen.append((x + r * f * math.cos(ph + 2 * math.pi * i / n), y + r * f * math.sin(ph + 2 * math.pi * i / n), z - haenge * f * (1 if i % 2 == 0 else 0.5)))
    verts = [spitze] + inner + aussen
    faces = []
    for i in range(n):
        i2 = (i + 1) % n
        faces.append((0, 1 + i, 1 + i2))
        faces.append((1 + i, 1 + n + i, 1 + n + i2, 1 + i2))
    boden = tuple(1 + n + i for i in range(n - 1, -1, -1))
    faces.append(boden)
    b.add(verts, faces, mat)


def _bx(b, x, y, zb, r, h):
    b.bx.append((x - r, y - r, zb, x + r, y + r, zb + h))


def _wurzeln(b, x, y, zb, r, rnd, s, mat, k=4):
    for i in range(k):
        a = 6.28 * (i + 0.5 * rnd(s + i)) / k
        l_ = r * (1.7 + 0.8 * rnd(s + 9 + i))
        rohr(b, [(x + 0.5 * r * math.cos(a), y + 0.5 * r * math.sin(a), zb + 0.25, r * 0.5), (x + l_ * math.cos(a), y + l_ * math.sin(a), zb - 0.05, r * 0.22)], mat, n=5)


# ------------------------------------------------------------------ Arten
def eiche(b, x, y, zb, rnd):
    """Eiche: kurzer, dicker Stamm mit Wurzelanlauf, drei Hauptaeste in einer Gabel, 8-10 Laubklumpen, zwei Laubfarben."""
    hs = 0.9 + 0.5 * rnd(1)
    r0 = 0.34 * hs
    hoehe = 2.5 * hs
    rohr(b, [(x, y, zb - 0.15, r0 * 1.7), (x, y, zb + 0.35, r0 * 1.15), (x + 0.04, y, zb + hoehe * 0.55, r0), (x + 0.05 * (rnd(2) - 0.5), y, zb + hoehe, r0 * 0.85)], "Rinde", n=8)
    _wurzeln(b, x, y, zb, r0, rnd, 40, "Rinde")
    mat1 = "Laub" if rnd(3) < 0.55 else ("Laub hell" if rnd(3) < 0.85 else "Laub gelb")
    mat2 = "Laub dunkel" if mat1 != "Laub gelb" else "Laub herbst"
    ph = rnd(4) * 6.28
    spitzen = []
    for k in range(3):
        a = ph + 2 * math.pi * k / 3 + 0.4 * (rnd(5 + k) - 0.5)
        l_ = (1.9 + 0.7 * rnd(8 + k)) * hs
        ex, ey, ez = x + l_ * math.cos(a), y + l_ * math.sin(a), zb + hoehe + (1.7 + 0.5 * rnd(11 + k)) * hs
        rohr(b, [(x, y, zb + hoehe - 0.1, r0 * 0.75), (x + 0.45 * (ex - x), y + 0.45 * (ey - y), zb + hoehe + 0.55 * hs, r0 * 0.5), (ex, ey, ez, r0 * 0.28)], "Rinde", n=6)
        spitzen.append((ex, ey, ez))
        sx, sy, sz = x + 0.55 * (ex - x), y + 0.55 * (ey - y), zb + hoehe + 0.9 * hs                   # Seitenast
        a2 = a + 0.9 * (1 if k % 2 else -1)
        rohr(b, [(sx, sy, sz, r0 * 0.34), (sx + 1.1 * hs * math.cos(a2), sy + 1.1 * hs * math.sin(a2), sz + 0.8 * hs, r0 * 0.16)], "Rinde", n=5)
        spitzen.append((sx + 1.1 * hs * math.cos(a2), sy + 1.1 * hs * math.sin(a2), sz + 0.8 * hs))
    for i, (px, py, pz) in enumerate(spitzen):
        rr = (1.9 + 0.6 * rnd(20 + i)) * hs
        klumpen(b, px, py, pz + 0.5 * hs, rr, rr * 0.95, rr * 0.8, mat1 if i % 3 else mat2, rnd, 100 + 17 * i, lat=4, lon=9)
    klumpen(b, x, y, zb + hoehe + 2.9 * hs, 2.1 * hs, 2.0 * hs, 1.5 * hs, mat1, rnd, 400, lat=4, lon=9)
    _bx(b, x, y, zb, 0.32 * hs + 0.1, hoehe)


def birke(b, x, y, zb, rnd):
    """Birke: schlanker weisser Stamm mit dunklen Rindenbaendern, leicht geneigt, lichte Krone aus sechs kleinen Klumpen und Hangzweigen."""
    hs = 0.9 + 0.5 * rnd(1)
    lean = (rnd(2) - 0.5) * 0.9
    la = rnd(3) * 6.28
    hoehe = 5.4 * hs
    pts = []
    for i in range(6):
        t = i / 5.0
        pts.append((x + lean * t * t * math.cos(la), y + lean * t * t * math.sin(la), zb - 0.1 + hoehe * t, 0.17 * hs * (1.15 - 0.75 * t)))
    rohr(b, pts, "Birke", n=7)
    for i in range(1, 5):                                                                      # dunkle Rindenbaender (schmale Ringe)
        px, py, pz, pr = pts[i]
        rohr(b, [(px, py, pz - 0.05, pr * 1.06), (px, py, pz + 0.09 + 0.05 * rnd(50 + i), pr * 1.04)], "Birke dunkel", n=7, kappe=False)
    top = pts[-1]
    for k in range(4):                                                                         # Aeste zur Krone
        a = 6.28 * k / 4 + rnd(60 + k)
        z = zb + hoehe * (0.5 + 0.1 * k)
        bx_, by_ = pts[min(5, 3 + k // 2)][0], pts[min(5, 3 + k // 2)][1]
        ex, ey, ez = bx_ + (1.1 + 0.4 * rnd(70 + k)) * math.cos(a), by_ + (1.1 + 0.4 * rnd(70 + k)) * math.sin(a), z + 1.2
        rohr(b, [(bx_, by_, z, 0.06), (ex, ey, ez, 0.03)], "Birke", n=5)
        klumpen(b, ex, ey, ez + 0.3, 1.1 * hs, 1.1 * hs, 1.0 * hs, "Birkenlaub" if k % 2 else "Birkenlaub hell", rnd, 200 + 13 * k, lat=3, lon=8)
        for j in range(3):                                                                      # Haengezweige
            jx, jy = ex + 0.7 * math.cos(a + j * 2.1), ey + 0.7 * math.sin(a + j * 2.1)
            rohr(b, [(jx, jy, ez + 0.1, 0.012), (jx + 0.1 * math.cos(a), jy + 0.1 * math.sin(a), ez - 1.0, 0.008)], "Birkenlaub", n=4)
    klumpen(b, top[0], top[1], top[2] + 0.4, 1.1 * hs, 1.1 * hs, 1.5 * hs, "Birkenlaub hell", rnd, 300, lat=4, lon=8)
    _bx(b, x, y, zb, 0.2, 3.0)


def fichte(b, x, y, zb, rnd):
    """Fichte: gerader Stamm, 9 Etagen aus zackigen Kegelschuerzen (nach oben kleiner, abwechselnd gedreht), Spitzentrieb, Wurzelanlauf."""
    hs = 0.8 + 0.8 * rnd(1)
    hoehe = 2.2 * hs
    rohr(b, [(x, y, zb - 0.15, 0.36 * hs), (x, y, zb + 0.4, 0.26 * hs), (x, y, zb + hoehe + 3.5 * hs, 0.08)], "Rinde", n=6)
    mats = ("Fichte dunkel", "Fichte", "Fichte hell") if rnd(2) < 0.7 else ("Tanne", "Tanne hell", "Tanne")
    n_et = 9
    for k in range(n_et):
        t = k / (n_et - 1)
        r = (2.5 - 2.0 * t) * hs ** 0.7
        z = zb + (1.9 + 5.6 * t) * hs
        schuerze(b, x, y, z, r, 1.5 * hs * (1.0 - 0.3 * t), mats[k % 3], rnd, 10 + 9 * k, n=10, haenge=0.4 * hs)
    schuerze(b, x, y, zb + 7.7 * hs, 0.35, 1.2 * hs, mats[0], rnd, 200, n=6, haenge=0.1)
    _wurzeln(b, x, y, zb, 0.26 * hs, rnd, 60, "Rinde", 3)
    _bx(b, x, y, zb, 0.27 * hs, 2.6 * hs)


def kiefer(b, x, y, zb, rnd):
    """Waldkiefer: krummer rotbrauner Stamm, kahl bis ins obere Drittel, dort vier waagrechte Nadelpolster auf Aesten und eine Krone."""
    hs = 0.85 + 0.6 * rnd(1)
    la = rnd(2) * 6.28
    sw = 0.5 + 0.7 * rnd(3)
    hoehe = 7.0 * hs
    pts = []
    for i in range(7):
        t = i / 6.0
        w = sw * math.sin(t * 3.4)
        pts.append((x + w * math.cos(la) * 0.5, y + w * math.sin(la) * 0.5, zb - 0.1 + hoehe * t, 0.28 * hs * (1.2 - 0.85 * t)))
    rohr(b, pts, "Kiefer Stamm", n=7)
    _wurzeln(b, x, y, zb, 0.28 * hs, rnd, 70, "Kiefer Stamm", 3)
    for k in range(4):
        a = la + 1.57 * k + 0.5 * rnd(80 + k)
        i = 3 + k // 2 + (1 if k == 3 else 0)
        px, py, pz = pts[min(i, 6)][:3]
        l_ = (1.7 + 0.8 * rnd(90 + k)) * hs
        ex, ey, ez = px + l_ * math.cos(a), py + l_ * math.sin(a), pz + 0.6
        rohr(b, [(px, py, pz, 0.1 * hs), (ex, ey, ez, 0.045)], "Kiefer Stamm", n=5)
        klumpen(b, ex, ey, ez + 0.2, 1.7 * hs, 1.7 * hs, 0.65 * hs, "Kiefer Nadeln" if k % 2 else "Kiefer Nadeln hell", rnd, 500 + 11 * k, lat=3, lon=9, jit=0.3)
    top = pts[-1]
    klumpen(b, top[0], top[1], top[2] + 0.2, 1.5 * hs, 1.5 * hs, 0.8 * hs, "Kiefer Nadeln hell", rnd, 600, lat=3, lon=9, jit=0.3)
    _bx(b, x, y, zb, 0.3 * hs, 3.0)


def pappel(b, x, y, zb, rnd):
    """Pappel: hoher, schlanker Stamm und schmale Saeulenkrone aus uebereinander gestapelten Klumpen."""
    hs = 0.9 + 0.5 * rnd(1)
    rohr(b, [(x, y, zb - 0.1, 0.3 * hs), (x, y, zb + 1.5, 0.2 * hs), (x, y, zb + 4.0 * hs, 0.12)], "Rinde", n=6)
    for k in range(7):
        t = k / 6.0
        r = (1.35 - 0.7 * abs(t - 0.35)) * hs
        klumpen(b, x + 0.12 * (rnd(30 + k) - 0.5), y + 0.12 * (rnd(40 + k) - 0.5), zb + (2.8 + 6.5 * t) * hs, r, r, 1.05 * hs, "Pappellaub" if k % 2 else "Laub dunkel", rnd, 700 + 13 * k, lat=3, lon=8)
    _bx(b, x, y, zb, 0.25 * hs, 3.0)


def obstbaum(b, x, y, zb, rnd):
    """Obstbaum (Apfel): niedriger, knorriger Stamm, breite runde Krone aus fuenf Klumpen mit roten Fruechten."""
    hs = 0.85 + 0.4 * rnd(1)
    rohr(b, [(x, y, zb - 0.1, 0.3 * hs), (x, y, zb + 0.5, 0.21 * hs), (x + 0.08, y, zb + 1.5 * hs, 0.17 * hs), (x + 0.1, y + 0.05, zb + 2.0 * hs, 0.14 * hs)], "Rinde", n=7)
    ph = rnd(2) * 6.28
    for k in range(4):
        a = ph + 1.57 * k
        ex, ey, ez = x + 1.1 * hs * math.cos(a), y + 1.1 * hs * math.sin(a), zb + 2.5 * hs
        rohr(b, [(x + 0.1, y + 0.05, zb + 1.9 * hs, 0.09), (ex, ey, ez, 0.04)], "Rinde", n=5)
        klumpen(b, ex, ey, ez + 0.5 * hs, 1.25 * hs, 1.25 * hs, 1.0 * hs, "Laub" if k % 2 else "Laub hell", rnd, 800 + 9 * k, lat=3, lon=8)
        for j in range(3):
            fa = a + 0.7 * j
            b.prism(ex + 1.0 * hs * math.cos(fa), ey + 1.0 * hs * math.sin(fa), ez + 0.5 * hs + 0.2 * (j - 1), 0.07, 0.12, 5, "Apfel")
    klumpen(b, x + 0.1, y, zb + 3.4 * hs, 1.3 * hs, 1.3 * hs, 0.95 * hs, "Laub hell", rnd, 900, lat=3, lon=8)
    _bx(b, x, y, zb, 0.25 * hs, 2.0)


NADEL = (fichte, kiefer)
LAUB = (eiche, birke, pappel, eiche, birke)


def nadelbaum(b, x, y, zb, rnd):
    (fichte if rnd(15) < 0.68 else kiefer)(b, x, y, zb, rnd)


def laubbaum(b, x, y, zb, rnd):
    LAUB[int(rnd(16) * len(LAUB)) % len(LAUB)](b, x, y, zb, rnd)
