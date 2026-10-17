"""Kleine 3D-Graeser auf allen Grasflaechen der Map (Rauschen: Flecken dichter Buschel, dazwischen Lichtungen und vereinzelte Halme).

Jeder Buschel besteht aus drei dreiseitigen Halmspitzen (3 Faces) in drei Gruentoenen, 12..40 cm hoch, auf der echten Wiesenhoehe. Nicht gewachsen wird auf
Strassen, Wegen, Plaetzen, in Haeusern und Hoefen, auf Feldern, im Steinbruch, im Burggelaende samt Ringweg, auf dem Flugplatz, an den Gleisen, im Teich
und auf dem Burgplateau; die Halme sind kein Hindernis."""
import math

import burg as B
import stadt as S
import talkessel as T
import umgebung as U
from burg import Bau

S.FARBEN.update({"Gras 1": ((0.27, 0.44, 0.15), 1.0, 0.0), "Gras 2": ((0.36, 0.52, 0.19), 1.0, 0.0), "Gras 3": ((0.21, 0.37, 0.13), 1.0, 0.0),
                 "Gras trocken": ((0.52, 0.52, 0.26), 1.0, 0.0)})
RASTER = 1.8


def _gras_ok(x, y, P, strs, aussen):
    if not (1.0 < x < 299.0 and 1.0 < y < 299.0):
        return False
    if math.hypot(x - U.C, y - U.C) < 63.0:                                              # Burg, Graben, Ringweg
        return False
    if x >= 205.0 and 48.0 <= y <= 252.0:                                              # Flugplatz mit Umfeld
        return False
    if 19.0 < y < 35.0 and x > 84.0:                                                    # Gleiskorridor
        return False
    if math.hypot(x - U.RUINE[0], y - U.RUINE[1]) < 15.5:                                # Burgplateau
        return False
    b = P["belegt"]
    for (x0, y0, x1, y1) in b.rechtecke:
        if x0 - 0.5 < x < x1 + 0.5 and y0 - 0.5 < y < y1 + 0.5:
            return False
    for (cx, cy, r) in b.kreise:
        if math.hypot(x - cx, y - cy) < r + 0.3:
            return False
    for (x0, y0, x1, y1) in P["plaetze"]:
        if x0 - 0.5 < x < x1 + 0.5 and y0 - 0.5 < y < y1 + 0.5:
            return False
    for tx, ty, tr in U.TEICHE:
        if math.hypot(x - tx, y - ty) < tr + 1.2:
            return False
    if S.strassenabstand(x, y, strs) < 0.6:
        return False
    for a, c in P["pfade"]:
        if U._seg_abstand(x, y, a, c) < 1.4:
            return False
    for a, c in aussen:
        if U._seg_abstand(x, y, a, c) < U.BREITE_WEG / 2 + 0.6:
            return False
    return True


def _spitze(b, x, y, z0, h, lean, r, ph, mat):
    base = [(x + r * math.cos(ph + 2.094 * k), y + r * math.sin(ph + 2.094 * k), z0) for k in range(3)]
    b.add(base + [(x + lean[0], y + lean[1], z0 + h)], [(0, 1, 3), (1, 2, 3), (2, 0, 3)], mat)


def bauen_gras(P):
    import ruine as RU
    strs = P["strs"]
    aussen = list(U.strassen_achsen())
    aussen += [(a, c) for a, c in zip(RU.WEG, RU.WEG[1:])]
    um = U.rund(U.UMFAHRUNG, U.RC, geschlossen=True)
    aussen += [(um[i], um[(i + 1) % len(um)]) for i in range(len(um))]
    b = Bau("gras")
    n = int(300.0 / RASTER)
    for ix in range(n):
        for iy in range(n):
            x = ix * RASTER + T._h01(ix, iy, 5001) * RASTER
            y = iy * RASTER + T._h01(ix, iy, 5002) * RASTER
            fl = T.fbm(x / 11.0, y / 11.0, T.SEED + 401, 3)                              # Flecken
            dichte = 0.08 + 0.85 * B.smoothstep(0.38, 0.62, fl)
            if T._h01(ix, iy, 5003) > dichte:
                continue
            if not _gras_ok(x, y, P, strs, aussen):
                continue
            z0 = U.gelaende_hoehe(x, y) - 0.02
            t = T._h01(ix, iy, 5004)
            mat = "Gras 1" if t < 0.4 else ("Gras 2" if t < 0.72 else ("Gras 3" if t < 0.93 else "Gras trocken"))
            hs = 0.12 + 0.28 * T.noise(x / 6.0, y / 6.0, T.SEED + 403) + 0.1 * T._h01(ix, iy, 5005)
            ph = T._h01(ix, iy, 5006) * 6.28
            for k in range(3):
                ox, oy = 0.1 * math.cos(ph + 2.1 * k), 0.1 * math.sin(ph + 2.1 * k)
                lean = (0.07 * math.cos(ph + 1.7 * k + 0.5) + 0.03, 0.07 * math.sin(ph + 1.7 * k + 0.5))
                _spitze(b, x + ox, y + oy, z0, hs * (1.0 - 0.18 * k), lean, 0.035, ph + k, mat)
    return b
