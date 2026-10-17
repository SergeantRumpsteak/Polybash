"""Strassenlaternen (Gusseisen, 40er-Jahre-Stil: Sockel, Mast mit Zierring, geschwungener Ausleger, Hauben-Laterne mit leuchtendem Glas) entlang aller
Strassen: Marktring, Spangen, Nord-/Sued-/Werk-/Gueterstrasse, Ringweg um die Burg samt Abzweigen (nicht auf dem Flugplatz). Abwechselnd
links und rechts, ca. alle 26 m; nicht auf Einfahrten, Pfaden, Haeusern oder anderen Strassen."""
import math

import burg as B
import stadt as S
import umgebung as U
from burg import Bau

S.FARBEN.update({"Laternenglas": ((1.0, 0.88, 0.55), 0.4, 4.0), "Laternenmast": ((0.12, 0.14, 0.13), 0.55, 0.0)})
ABSTAND = 26.0


def laterne(b, x, y, z, nx, ny):
    """Laterne bei (x, y), Ausleger zeigt in Richtung (nx, ny) (zur Strasse hin)."""
    m = "Laternenmast"
    n0 = len(b.bx)
    b.box(x - 0.17, y - 0.17, z, x + 0.17, y + 0.17, z + 0.22, "Stein alt")
    b.prism(x, y, z + 0.22, 0.11, 0.5, 6, m)
    b.prism(x, y, z + 0.72, 0.065, 3.1, 6, m)
    b.prism(x, y, z + 1.9, 0.1, 0.1, 6, m)                                               # Zierring
    b.prism(x, y, z + 3.65, 0.09, 0.08, 6, m)
    p0 = (x, y, z + 3.78)
    p1 = (x + nx * 0.45, y + ny * 0.45, z + 4.12)
    p2 = (x + nx * 1.0, y + ny * 1.0, z + 4.0)
    b.beam(p0, p1, 0.07, 0.07, m)
    b.beam(p1, p2, 0.07, 0.07, m)
    lx, ly = p2[0], p2[1]
    b.box(lx - 0.17, ly - 0.17, z + 3.58, lx + 0.17, ly + 0.17, z + 3.64, m)             # Boden
    b.box(lx - 0.14, ly - 0.14, z + 3.64, lx + 0.14, ly + 0.14, z + 4.0, "Laternenglas")  # Glas
    for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1)):                                  # Streben
        b.box(lx + sx * 0.14 - 0.015, ly + sy * 0.14 - 0.015, z + 3.64, lx + sx * 0.14 + 0.015, ly + sy * 0.14 + 0.015, z + 4.0, m)
    n = 6
    ring = [(lx + 0.27 * math.cos(2 * math.pi * k / n), ly + 0.27 * math.sin(2 * math.pi * k / n), z + 4.0) for k in range(n)]
    b.add(ring + [(lx, ly, z + 4.28)], [tuple(range(n - 1, -1, -1))] + [(i, (i + 1) % n, n) for i in range(n)], m)           # Haube
    del b.bx[n0:]
    b.bx.append((x - 0.12, y - 0.12, z, x + 0.12, y + 0.12, z + 3.7))


def _frei(x, y, P, strs):
    b = P["belegt"]
    for (cx, cy, r) in b.kreise:
        if math.hypot(x - cx, y - cy) < r + 0.4:
            return False
    for (x0, y0, x1, y1) in b.rechtecke:
        if x0 - 0.3 < x < x1 + 0.3 and y0 - 0.3 < y < y1 + 0.3 and (x0, y0, x1, y1) != S.PLATZ:
            return False
    if S.strassenabstand(x, y, strs) < 0.45:
        return False
    for a, c in P["pfade"]:
        if U._seg_abstand(x, y, a, c) < 2.3:
            return False
    for tx, ty, tr in U.TEICHE:
        if math.hypot(x - tx, y - ty) < tr + 1.5:
            return False
    return True


def _linien(P):
    """Liste (Punkte, halbe Breite, geschlossen)."""
    out = []
    for s in P["strs"]:
        if s["name"] == "Kreisverkehr Nord":
            continue
        out.append((s["pts"], s["w"] / 2, s["zu"]))
    import math as m
    ring = [U.ring_punkt(2 * m.pi * k / 120) for k in range(120)]
    out.append((ring, U.BREITE_WEG / 2, True))
    for p, q in U.strassen_achsen()[:]:
        out.append(([p, q], U.BREITE_WEG / 2, False))
    return out


def bauen_laternen(P):
    b = Bau("stadt_laternen")
    strs = P["strs"]
    gesetzt = []
    for pts, hw, zu in _linien(P):
        m = len(pts)
        seg = [(pts[i], pts[(i + 1) % m]) for i in range(m if zu else m - 1)]
        rest = ABSTAND * 0.5
        seite = 1
        for p, q in seg:
            ln = math.hypot(q[0] - p[0], q[1] - p[1])
            if ln < 1e-6:
                continue
            ux, uy = (q[0] - p[0]) / ln, (q[1] - p[1]) / ln
            t = rest
            while t < ln:
                nx, ny = -uy * seite, ux * seite                                          # Normale zur Seite der Laterne hin ist -n (Ausleger zur Strasse)
                x, y = p[0] + ux * t + nx * (hw + 0.85), p[1] + uy * t + ny * (hw + 0.85)
                if x < 216.0 and all(math.hypot(x - gx, y - gy) > 11.0 for gx, gy in gesetzt) and _frei(x, y, P, strs):
                    laterne(b, x, y, U.gelaende_hoehe(x, y), -nx, -ny)
                    gesetzt.append((x, y))
                    seite = -seite
                t += ABSTAND
            rest = t - ln
    return b
