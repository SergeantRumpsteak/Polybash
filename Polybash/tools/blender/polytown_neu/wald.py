"""Dichter Mischwald mit Huegeln beiderseits der Bahnstrecke suedlich des Flugplatzes (x 196..296).

Die Strecke selbst liegt auf ebenem Grund (umgebung.STADT_ZONEN, schmaler Korridor y 22..32); direkt daneben steigen Huegel an
(umgebung.KUPPEN). Die Baeume stehen auf der tatsaechlichen Wiesenhoehe (U.gelaende_hoehe). Zwischen den Stammen kann man hindurch-
gehen: nur der Stamm blockiert (b.bx), die Kronen beginnen ueber Kopfhoehe. Lichtungen entstehen durch Rauschen."""
import math

import burg as B
import stadt as S
import talkessel as T
import umgebung as U

S.FARBEN.update({"Tanne": ((0.10, 0.22, 0.13), 0.95, 0.0), "Tanne hell": ((0.16, 0.30, 0.16), 0.95, 0.0), "Laub herbst": ((0.45, 0.36, 0.12), 0.95, 0.0),
                 "Busch": ((0.17, 0.27, 0.12), 1.0, 0.0), "Farn": ((0.22, 0.34, 0.14), 1.0, 0.0)})
S.FARBEN.setdefault("Stamm", ((0.30, 0.20, 0.12), 0.95, 0.0))
S.FARBEN.setdefault("Laub", ((0.20, 0.36, 0.14), 0.95, 0.0))
S.FARBEN.setdefault("Laub hell", ((0.30, 0.45, 0.17), 0.95, 0.0))

X0, X1 = 197.0, 293.0
RASTER = 2.6


def _h(ix, iy, s):
    return T._h01(ix, iy, 7000 + s)


def tanne(b, x, y, zb, rnd):
    """Fichte/Tanne: Stamm und vier Kronenstufen (Kegel, 7 Ecken); Krone beginnt bei ~2,2 m."""
    hs = 0.8 + 0.8 * rnd(1)
    b.prism(x, y, zb - 0.15, 0.24, 2.6 * hs + 0.15, 6, "Stamm")
    mat = "Tanne" if rnd(2) < 0.6 else "Tanne hell"
    for k, (r, z0, hh) in enumerate(((2.1, 2.0, 2.4), (1.7, 3.3, 2.2), (1.25, 4.5, 2.0), (0.8, 5.6, 1.8))):
        z0 *= hs
        hh *= hs
        n = 7
        ph = rnd(3 + k) * 2.0
        ring = [(x + r * (0.85 + 0.3 * rnd(10 + i + 7 * k)) * math.cos(2 * math.pi * i / n + ph),
                 y + r * (0.85 + 0.3 * rnd(10 + i + 7 * k)) * math.sin(2 * math.pi * i / n + ph), zb + z0) for i in range(n)]
        b.add(ring + [(x, y, zb + z0 + hh)], [tuple(range(n - 1, -1, -1))] + [(i, (i + 1) % n, n) for i in range(n)], mat)
    b.bx.append((x - 0.25, y - 0.25, zb, x + 0.25, y + 0.25, zb + 2.6 * hs))


def laubbaum(b, x, y, zb, rnd):
    """Eiche/Buche: hoher Stamm, zwei versetzte Kronenkoerper (Bipyramiden mit unregelmaessigem Ring)."""
    hs = 0.9 + 0.5 * rnd(1)
    b.prism(x, y, zb - 0.15, 0.28, 3.0 * hs + 0.15, 6, "Stamm")
    mat = "Laub" if rnd(2) < 0.5 else ("Laub hell" if rnd(2) < 0.85 else "Laub herbst")
    for k in range(2):
        cx = x + (rnd(20 + k) - 0.5) * 1.6 * k
        cy = y + (rnd(30 + k) - 0.5) * 1.6 * k
        cz = zb + (3.4 + 1.1 * k) * hs
        r = (2.6 - 0.5 * k) * hs
        n = 8
        ring = [(cx + r * (0.8 + 0.4 * rnd(40 + i + 9 * k)) * math.cos(2 * math.pi * i / n), cy + r * (0.8 + 0.4 * rnd(40 + i + 9 * k)) * math.sin(2 * math.pi * i / n),
                 cz + 0.5 * (rnd(60 + i) - 0.5)) for i in range(n)]
        top, bot = (cx, cy, cz + 1.9 * hs), (cx, cy, cz - 1.5 * hs)
        f = [(i, (i + 1) % n, n) for i in range(n)] + [((i + 1) % n, i, n + 1) for i in range(n)]
        b.add(ring + [top, bot], f, mat)
    b.bx.append((x - 0.28, y - 0.28, zb, x + 0.28, y + 0.28, zb + 3.0 * hs))


def busch(b, x, y, zb, rnd):
    r = 0.7 + 0.6 * rnd(1)
    n = 6
    ring = [(x + r * (0.8 + 0.4 * rnd(5 + i)) * math.cos(2 * math.pi * i / n), y + r * (0.8 + 0.4 * rnd(5 + i)) * math.sin(2 * math.pi * i / n), zb + 0.25) for i in range(n)]
    b.add(ring + [(x, y, zb + 0.4 + r)], [tuple(range(n - 1, -1, -1))] + [(i, (i + 1) % n, n) for i in range(n)], "Busch" if rnd(2) < 0.7 else "Farn")


def dichte(x, y):
    """Baumdichte 0..1 als Rauschen (Dickichte und Lichtungen, keine Streifen); fehlt am Gleiskorridor (y 22..32), am Flugplatz und an den Raendern."""
    if not (X0 <= x <= X1) or not (6.0 <= y <= 52.0):
        return 0.0
    if math.hypot(x - 192.0, y - 50.0) < 11.0:                            # Teich am Stationsende
        return 0.0
    dk = max(22.0 - y, y - 32.0, 0.0)
    rand = B.smoothstep(2.5, 9.0, dk) * B.smoothstep(X0, X0 + 16.0, x) * (1.0 - B.smoothstep(X1 - 10.0, X1, x)) * B.smoothstep(6.0, 11.0, y) * (1.0 - B.smoothstep(42.0, 52.0, y))
    n = 0.6 * T.fbm(x / 17.0, y / 17.0, T.SEED + 77, 3) + 0.4 * T.fbm(x / 6.5, y / 6.5, T.SEED + 79, 2)
    return rand * B.smoothstep(0.16, 0.46, n)


def baeume_liste():
    out = []
    for ix in range(int(X0 / RASTER) - 1, int(X1 / RASTER) + 2):
        for iy in range(0, int(54 / RASTER) + 1):
            x = ix * RASTER + (_h(ix, iy, 1) - 0.5) * 2.8
            y = iy * RASTER + (_h(ix, iy, 2) - 0.5) * 2.8
            if _h(ix, iy, 3) > dichte(x, y) * 1.05:
                continue
            out.append((x, y, int(_h(ix, iy, 4) * 10)))
    return out


def bauen_wald():
    b = B.Bau("wald")
    for x, y, k in baeume_liste():
        zb = U.gelaende_hoehe(x, y)
        s = k * 131 + int(x * 7) + int(y * 13)
        rnd = lambda i, s=s: T._h01(s, i, 7777)
        if k < 5:
            tanne(b, x, y, zb, rnd)
        elif k < 8:
            laubbaum(b, x, y, zb, rnd)
        else:
            busch(b, x, y, zb, rnd)
    return [b]
