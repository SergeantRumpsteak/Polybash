"""Polybash - Flughafenschilder (Rollweg-Beschilderung) und Pistennummern (reine Geometrie, ohne bpy).

Schilder nach ICAO-Art: Standort (schwarz, gelbe Schrift und Rahmen), Richtung (gelb, schwarze Schrift mit Pfeil) und Haltepunkt
vor der Piste (rot, weisse Schrift). Die Schrift ist eine 5 x 7 Pixelschrift (Zeilenlaeufe zu Rechtecken zusammengefasst).
Pistennummern: weisse Strichziffern (Boegen und Geraden) hinter der Schwelle, fuer den anfliegenden Piloten lesbar.
"""
import math

FARBEN = {
    "Schild rot":        ((0.72, 0.05, 0.05), 0.5, 0.0),
    "Schild gelb":       ((0.95, 0.76, 0.05), 0.5, 0.0),
    "Schild schwarz":    ((0.03, 0.03, 0.035), 0.6, 0.0),
    "Schild weiss":      ((0.93, 0.93, 0.90), 0.5, 0.0),
    "Schild Pfosten":    ((0.30, 0.31, 0.33), 0.5, 0.0),
    "Schild gruen":      ((0.04, 0.42, 0.20), 0.5, 0.0),
}

_FONT = {
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("#####", "...#.", "..#..", "...#.", "....#", "#...#", ".###."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": ("..##.", ".#...", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "..#..", ".#...", ".#...", ".#..."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "...#.", ".##.."),
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".###.", "#...#", "#....", "#....", "#....", "#...#", ".###."),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "-": (".....", ".....", ".....", "#####", ".....", ".....", "....."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
}
PIX = 0.062                      # Pixelkante (m): Zeichenhoehe 7 x 0,062 = 0,43 m
TEILUNG = 0.40                   # Zeichenabstand
TAFEL_H = 0.85                   # Tafelhoehe
UNTEN = 0.42                     # Unterkante ueber dem Boden


def _flat(b, pts, mat, nvec):
    n = [0.0, 0.0, 0.0]
    for k in range(len(pts)):
        a, c = pts[k], pts[(k + 1) % len(pts)]
        n[0] += (a[1] - c[1]) * (a[2] + c[2])
        n[1] += (a[2] - c[2]) * (a[0] + c[0])
        n[2] += (a[0] - c[0]) * (a[1] + c[1])
    if n[0] * nvec[0] + n[1] * nvec[1] + n[2] * nvec[2] < 0:
        pts = pts[::-1]
    b.add(pts, [tuple(range(len(pts)))], mat)


def text_breite(text):
    return len(text) * TEILUNG - (TEILUNG - 5 * PIX)


def _tafel_breite(text, pfeil):
    return text_breite(text) + 0.36 + (0.55 if pfeil else 0.0)


def schild(b, x, y, face, tafeln, pfosten=True, unten=UNTEN):
    """Schild bei (x, y) mit Blickrichtung face ('N','S','E','W' = Richtung, in die die Vorderseite zeigt).

    tafeln: Liste (art, text, pfeil) von links nach rechts aus Sicht des Betrachters; art 'standort'|'richtung'|'halt',
    pfeil None|'links'|'rechts' (links/rechts aus Sicht des Betrachters). Rueckgabe: Breite des Schilds."""
    n = {"N": (0, 1), "S": (0, -1), "E": (1, 0), "W": (-1, 0)}[face]
    r = (-n[1], n[0])                                             # rechts aus Sicht des Betrachters
    def W(u, w, v):
        return (x + u * r[0] + w * n[0], y + u * r[1] + w * n[1], v)

    def lbox(u0, u1, w0, w1, v0, v1, mat):
        cs = [W(u, w, v) for u in (u0, u1) for w in (w0, w1) for v in (v0, v1)]
        b.box(min(c[0] for c in cs), min(c[1] for c in cs), min(c[2] for c in cs),
              max(c[0] for c in cs), max(c[1] for c in cs), max(c[2] for c in cs), mat)

    breiten = [_tafel_breite(t, p) for (_, t, p) in tafeln]
    gesamt = sum(breiten) + 0.04 * (len(tafeln) - 1)
    u = -gesamt / 2
    v0, v1 = unten, unten + TAFEL_H
    nv = (n[0], n[1], 0.0)
    for (art, text, pfeil), bw in zip(tafeln, breiten):
        grund, schrift, rahmen = {"standort": ("Schild schwarz", "Schild gelb", "Schild gelb"),
                                  "richtung": ("Schild gelb", "Schild schwarz", "Schild schwarz"),
                                  "halt": ("Schild rot", "Schild weiss", "Schild weiss"),
                                  "bus": ("Schild gruen", "Schild weiss", "Schild weiss")}[art]
        lbox(u, u + bw, -0.04, 0.04, v0, v1, grund)
        wf = 0.045
        d = 0.05                                                  # Rahmen-Inset
        for (a0, a1, c0, c1) in ((u + d, u + bw - d, v1 - d - 0.03, v1 - d), (u + d, u + bw - d, v0 + d, v0 + d + 0.03),
                                 (u + d, u + d + 0.03, v0 + d, v1 - d), (u + bw - d - 0.03, u + bw - d, v0 + d, v1 - d)):
            _flat(b, [W(a0, wf, c0), W(a1, wf, c0), W(a1, wf, c1), W(a0, wf, c1)], rahmen, nv)
        tb = text_breite(text)
        ux = u + (bw - tb - (0.55 if pfeil else 0.0)) / 2
        if pfeil == "links":
            ux += 0.55
        vt = v0 + (TAFEL_H - 7 * PIX) / 2
        for ch in text:
            rows = _FONT[ch]
            for ri, row in enumerate(rows):                       # Zeile 0 = oben
                vb = vt + (6 - ri) * PIX
                c = 0
                while c < 5:
                    if row[c] == "#":
                        c2 = c
                        while c2 < 5 and row[c2] == "#":
                            c2 += 1
                        _flat(b, [W(ux + c * PIX, wf, vb), W(ux + c2 * PIX, wf, vb), W(ux + c2 * PIX, wf, vb + PIX), W(ux + c * PIX, wf, vb + PIX)], schrift, nv)
                        c = c2
                    else:
                        c += 1
            ux += TEILUNG
        if pfeil:
            vc = (v0 + v1) / 2
            if pfeil == "links":
                ua, ub, sg = u + 0.12, u + 0.12 + 0.46, 1
            else:
                ua, ub, sg = u + bw - 0.12, u + bw - 0.12 - 0.46, -1
            kopf = ua + sg * 0.20
            _flat(b, [W(ua, wf, vc), W(kopf, wf, vc + 0.17), W(kopf, wf, vc - 0.17)], schrift, nv)
            _flat(b, [W(kopf, wf, vc - 0.045), W(ub, wf, vc - 0.045), W(ub, wf, vc + 0.045), W(kopf, wf, vc + 0.045)], schrift, nv)
        u += bw + 0.04
    if pfosten == "mitte":
        lbox(-0.05, 0.05, -0.05, 0.05, 0.0, v0 + 0.02, "Schild Pfosten")
    elif pfosten:
        for pu in (-gesamt / 2 + 0.25, gesamt / 2 - 0.25):
            lbox(pu - 0.04, pu + 0.04, -0.04, 0.04, 0.0, v0 + 0.02, "Schild Pfosten")
    return gesamt


# ------------------------------------------------------------------ Pistennummern
def _strich(b, pts, s, z, mat):
    """Linienzug als Folge von Vierecken (Breite s), Enden ueberlappen leicht."""
    for (x0, y0), (x1, y1) in zip(pts[:-1], pts[1:]):
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy)
        if L < 1e-6:
            continue
        ux, uy = dx / L, dy / L
        px, py = -uy * s / 2, ux * s / 2
        ex, ey = ux * s * 0.35, uy * s * 0.35
        q = [(x0 - ex + px, y0 - ey + py, z), (x1 + ex + px, y1 + ey + py, z), (x1 + ex - px, y1 + ey - py, z), (x0 - ex - px, y0 - ey - py, z)]
        _flat(b, q, mat, (0, 0, 1))


def _bogen(cx, cy, rx, ry, a0, a1, n=14):
    return [(cx + rx * math.cos(math.radians(a0 + (a1 - a0) * k / n)), cy + ry * math.sin(math.radians(a0 + (a1 - a0) * k / n))) for k in range(n + 1)]


def ziffer(ch, H, Wd, s):
    """Linienzuege (in u/v, Ursprung links unten) einer Pistenziffer."""
    if ch == "1":
        return [[(Wd * 0.62, 0.0), (Wd * 0.62, H)], [(Wd * 0.62, H), (Wd * 0.14, H * 0.78)]]
    if ch == "8":
        ro, ru = H * 0.25 - s / 2, H * 0.29 - s / 2
        return [_bogen(Wd / 2, H * 0.29, Wd / 2 - s / 2, ru, 0, 360, 20), _bogen(Wd / 2, H * 0.73, Wd / 2 - s / 2 - 0.2, ro, 0, 360, 20)]
    if ch == "3":
        ro, ru = H * 0.25 - s / 2, H * 0.27 - s / 2
        return [_bogen(Wd / 2 - 0.1, H * 0.74, Wd / 2 - s / 2 - 0.3, ro, 155, -90, 16), _bogen(Wd / 2, H * 0.27, Wd / 2 - s / 2, ru, 90, -155, 18)]
    if ch == "6":
        ru = H * 0.29 - s / 2
        stiel = [(Wd * 0.10, H * 0.32), (Wd * 0.10, H * 0.55), (Wd * 0.24, H * 0.80), (Wd * 0.50, H - s / 2), (Wd * 0.82, H - s * 0.8)]
        return [_bogen(Wd / 2, H * 0.29, Wd / 2 - s / 2, ru, 0, 360, 20), stiel]
    raise ValueError(ch)


def pistennummer(b, text, x_mitte, y_ab, nach_norden, z, mat="Markierung weiss", H=9.0, Wd=4.4, s=0.95, luecke=1.7):
    """Zwei Ziffern; y_ab = Fusslinie der Ziffern (Seite zur Schwelle). nach_norden=True: Schrift liest sich beim Anflug von Sueden."""
    gesamt = len(text) * Wd + (len(text) - 1) * luecke
    u0 = -gesamt / 2
    for i, ch in enumerate(text):
        uu = u0 + i * (Wd + luecke)
        for zug in ziffer(ch, H, Wd, s):
            if nach_norden:
                pts = [(x_mitte + uu + u, y_ab + v) for (u, v) in zug]
            else:
                pts = [(x_mitte - (uu + u), y_ab - v) for (u, v) in zug]
            _strich(b, pts, s, z, mat)
    return b
