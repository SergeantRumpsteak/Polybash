"""Polybash - Flugzeuge des 2. Weltkriegs und ein Tankwagen (reine Geometrie, ohne bpy).

Alle Modelle entstehen in einem Ortssystem (x = Nase, y = linker Fluegel, z = oben) und werden mit Kurs psi (Grad, mathematisch:
0 = Nase nach +x/Osten, 90 = Norden, 225 = Suedwesten) und Standort auf die Karte gesetzt. Rumpf und Fluegel sind Loftkoerper aus
Querschnittsringen (Rumpf: Rechteck mit Fasen, Fluegel: 4-Punkt-Profil), dazu Fahrwerk, Luftschraube, Leitwerk, Bewaffnung und
Hoheitszeichen (Balkenkreuz, Kokarde). Die Spornradflugzeuge stehen mit angehobener Nase (Bodenlage).

  * stuka()   Junkers Ju 87 B "Stuka": Knickfluegel, Hosenfahrwerk, 500-kg-Bombe unter dem Rumpf (Schwenkarm), 4 x 50 kg unter den
              Fluegeln, Kuehlerkinn, langes Doppelsitzer-Dach, gelbe Fluegelspitzen
  * jaeger()  Bf 109 E, Fw 190 A, Spitfire Mk I (einfacher Kurs-/Typparameter)
  * tankwagen()  Betankungsfahrzeug fuer die Flugplatz-Tankstelle (Kabine, Ovaltank, Schlauchtrommel, Raeder)
Das Hakenkreuz am Leitwerk fehlt bewusst; Balkenkreuze sind vorhanden.
"""
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

from burg import Bau  # noqa: E402

FARBEN = {
    "Flug Gruen":      ((0.16, 0.21, 0.13), 0.55, 0.0),      # RLM 71 dunkelgruen
    "Flug Schwarzgruen": ((0.09, 0.12, 0.10), 0.55, 0.0),    # RLM 70
    "Flug Hellblau":   ((0.56, 0.68, 0.76), 0.55, 0.0),      # RLM 65
    "Flug Grau":       ((0.36, 0.40, 0.43), 0.55, 0.0),      # RLM 74
    "Flug Hellgrau":   ((0.58, 0.62, 0.64), 0.55, 0.0),      # RLM 76
    "Flug Braun":      ((0.30, 0.23, 0.13), 0.6, 0.0),
    "Flug Sand":       ((0.62, 0.52, 0.32), 0.6, 0.0),
    "Flug Himmelgrau": ((0.60, 0.72, 0.66), 0.55, 0.0),
    "Flug Gelb":       ((0.90, 0.72, 0.08), 0.5, 0.0),
    "Flug Glas":       ((0.50, 0.66, 0.74), 0.1, 0.0),
    "Flug Metall":     ((0.20, 0.21, 0.23), 0.4, 0.0),
    "Flug Schwarz":    ((0.04, 0.04, 0.045), 0.7, 0.0),
    "Flug Weiss":      ((0.92, 0.92, 0.90), 0.6, 0.0),
    "Flug Rot":        ((0.72, 0.08, 0.07), 0.6, 0.0),
    "Flug Blau":       ((0.07, 0.12, 0.45), 0.6, 0.0),
    "Flug Reifen":     ((0.05, 0.05, 0.05), 0.95, 0.0),
    "Flug Bombe":      ((0.24, 0.27, 0.20), 0.6, 0.0),
    "Tankwagen Alu":   ((0.74, 0.76, 0.78), 0.35, 0.0),
    "Tankwagen Rot":   ((0.70, 0.07, 0.06), 0.5, 0.0),
    "Tankwagen Kabine": ((0.88, 0.88, 0.86), 0.5, 0.0),
    "Tankwagen Orange": ((0.95, 0.45, 0.05), 0.5, 0.0),
    "Tankwagen Lampe": ((0.95, 0.92, 0.70), 0.3, 0.0),
}


# ------------------------------------------------------------------ Grundwerkzeug
def _newell(poly):
    nx = ny = nz = 0.0
    for k in range(len(poly)):
        a, c = poly[k], poly[(k + 1) % len(poly)]
        nx += (a[1] - c[1]) * (a[2] + c[2])
        ny += (a[2] - c[2]) * (a[0] + c[0])
        nz += (a[0] - c[0]) * (a[1] + c[1])
    return nx, ny, nz


def _lerp(a, b, t):
    return a + (b - a) * t


def sek_ip(secs, y):
    """Fluegelprofil (xle, chord, zc, thick) bei Spannweitenstation y (lineare Interpolation der Schnitte)."""
    if y <= secs[0][0]:
        return secs[0][1:]
    for k in range(len(secs) - 1):
        if y <= secs[k + 1][0]:
            t = (y - secs[k][0]) / max(1e-9, secs[k + 1][0] - secs[k][0])
            return tuple(_lerp(secs[k][i], secs[k + 1][i], t) for i in range(1, 5))
    return secs[-1][1:]


def fl_z(secs, x, y, oben=True):
    """Hoehe der Fluegelober-/unterseite an (x, y)."""
    xle, c, zc, t = sek_ip(secs, y)
    f = min(1.0, max(0.0, (xle - x) / max(1e-6, c)))
    h = f / 0.3 if f < 0.3 else (1.0 - f) / 0.7
    return zc + (t / 2) * h * (1 if oben else -1)


def rbox(x, yc, zc, w, h, c):
    """Rumpfquerschnitt: Rechteck (Halbbreite w, Halbhoehe h) mit Fasen c; Punkte gegen den Uhrzeigersinn ab rechter Seite unten."""
    c = min(c, w * 0.95, h * 0.95)
    d = [(w, -(h - c)), (w, h - c), (w - c, h), (-(w - c), h), (-w, h - c), (-w, -(h - c)), (-(w - c), -h), (w - c, -h)]
    return [(x, yc + dy, zc + dz) for dy, dz in d]


def runde(x, yc, zc, r, n=8, a0=0.0):
    return [(x, yc + r * math.cos(a0 + 2 * math.pi * k / n), zc + r * math.sin(a0 + 2 * math.pi * k / n)) for k in range(n)]


class Fz:
    """Ortskoordinaten -> Welt (Kurs psi, Nase um nick Grad angehoben um den Drehpunkt pivot=(x, z))."""

    def __init__(self, b, ox, oy, psi, z0=0.0, nick=0.0, pivot=(0.0, 0.0)):
        self.b, self.ox, self.oy, self.z0 = b, ox, oy, z0
        self.c, self.s = math.cos(math.radians(psi)), math.sin(math.radians(psi))
        self.cp, self.sp = math.cos(math.radians(nick)), math.sin(math.radians(nick))
        self.pv = pivot

    def N(self, x, y, z):
        px, pz = self.pv
        dx, dz = x - px, z - pz
        return (px + dx * self.cp - dz * self.sp, y, pz + dz * self.cp + dx * self.sp)

    def P(self, x, y, z, nick=True):
        if nick:
            x, y, z = self.N(x, y, z)
        return (self.ox + x * self.c - y * self.s, self.oy + x * self.s + y * self.c, self.z0 + z)

    def poly(self, pts, mat, hint=(0, 0, 1), nick=True):
        """Ebenes Vieleck, Normale zur Seite von hint (Ortsrichtung, nur Vorzeichen zaehlt)."""
        w = [self.P(*p, nick=nick) for p in pts]
        n = _newell(w)
        hw = (hint[0] * self.c - hint[1] * self.s, hint[0] * self.s + hint[1] * self.c, hint[2])
        if n[0] * hw[0] + n[1] * hw[1] + n[2] * hw[2] < 0:
            w = w[::-1]
        self.b.add(w, [tuple(range(len(w)))], mat)

    def loft(self, rings, mat, caps=(True, True), nick=True, spiegel=False):
        """Koerper aus Ringen (alle gleich viele Punkte); mat = ein Material oder je eine Kante (Ring-Segment) eins."""
        n = len(rings[0])
        W = [[self.P(p[0], -p[1] if spiegel else p[1], p[2], nick) for p in r] for r in rings]
        cen = [tuple(sum(q[i] for q in r) / n for i in range(3)) for r in W]
        mats = list(mat) if isinstance(mat, (list, tuple)) else [mat] * n
        for i in range(len(W) - 1):
            ref = tuple((cen[i][j] + cen[i + 1][j]) / 2 for j in range(3))
            for k in range(n):
                q = [W[i][k], W[i][(k + 1) % n], W[i + 1][(k + 1) % n], W[i + 1][k]]
                fc = tuple(sum(p[j] for p in q) / 4 for j in range(3))
                nn = _newell(q)
                if nn[0] * (fc[0] - ref[0]) + nn[1] * (fc[1] - ref[1]) + nn[2] * (fc[2] - ref[2]) < 0:
                    q = q[::-1]
                self.b.add(q, [(0, 1, 2, 3)], mats[k])
        for idx, (on, nb) in enumerate(((caps[0], 1), (caps[1], len(W) - 2))):
            if not on or len(W) < 2:
                continue
            r = 0 if idx == 0 else len(W) - 1
            q = W[r][:]
            nn = _newell(q)
            away = tuple(cen[r][j] - cen[nb][j] for j in range(3))
            if nn[0] * away[0] + nn[1] * away[1] + nn[2] * away[2] < 0:
                q = q[::-1]
            self.b.add(q, [tuple(range(n))], mats[0])

    def kasten(self, x0, x1, y0, y1, z0, z1, mat, nick=True):
        ring = lambda x: [(x, y0, z0), (x, y1, z0), (x, y1, z1), (x, y0, z1)]
        self.loft([ring(x0), ring(x1)], mat, nick=nick)

    def beam(self, a, b2, w, h, mat, na=True, nb=True):
        self.b.beam(self.P(*a, nick=na), self.P(*b2, nick=nb), w, h, mat)

    def rad(self, cx, cy, cz, r, w, mat_reifen="Flug Reifen", n=10):
        """Rad mit Achse in y (steht senkrecht in der Welt, ohne Nick)."""
        ring = lambda y, rr: [(cx + rr * math.cos(2 * math.pi * k / n), y, cz + rr * math.sin(2 * math.pi * k / n)) for k in range(n)]
        self.loft([ring(cy - w / 2, r), ring(cy + w / 2, r)], mat_reifen, nick=False)
        self.loft([ring(cy - w / 2 - 0.015, r * 0.55), ring(cy + w / 2 + 0.015, r * 0.55)], "Flug Metall", nick=False)

    def fluegel(self, secs, mats, tip_mat=None, tip_ab=None, spiegel=False, kappe=True):
        """Tragflaeche; Schnitt = (y, xle, chord, zc, thick). mats = (oben, unten); ab Index tip_ab anderes Material tip_mat."""
        def ring(s):
            y, xle, c, zc, t = s
            return [(xle, y, zc), (xle - 0.3 * c, y, zc + t / 2), (xle - c, y, zc), (xle - 0.3 * c, y, zc - t / 2)]
        ms = [mats[0], mats[0], mats[1], mats[1]]
        if tip_ab is None:
            self.loft([ring(s) for s in secs], ms, caps=(False, kappe), spiegel=spiegel)
        else:
            self.loft([ring(s) for s in secs[:tip_ab + 1]], ms, caps=(False, False), spiegel=spiegel)
            mt = [tip_mat] * 4
            self.loft([ring(s) for s in secs[tip_ab:]], mt, caps=(False, kappe), spiegel=spiegel)

    def schraube(self, x, zc, r, n=3, mat="Flug Schwarz", spitze="Flug Gelb", phase=90.0):
        st = [(0.20, 0.15), (0.55, 0.20), (r * 0.78, 0.24), (r * 0.93, 0.21), (r, 0.12)]
        for j in range(n):
            a = math.radians(phase + 360.0 * j / n)
            rings, rings_t = [], []
            for i, (rho, wd) in enumerate(st):
                tw = 0.45 * (1.0 - rho / r) + 0.15
                pts = []
                for xb, wb in ((-0.02, -wd / 2), (0.02, -wd / 2), (0.02, wd / 2), (-0.02, wd / 2)):
                    xb2 = xb * math.cos(tw) - wb * math.sin(tw)
                    wb2 = wb * math.cos(tw) + xb * math.sin(tw)
                    pts.append((x + xb2, rho * math.cos(a) - wb2 * math.sin(a), zc + rho * math.sin(a) + wb2 * math.cos(a)))
                rings.append(pts)
            self.loft(rings[:4], mat, caps=(False, False))
            self.loft(rings[3:], spitze if spitze else mat, caps=(False, True))

    def fluegel_zeichen(self, secs, y0, x0, d, art, oben=True, spiegel=False):
        """Hoheitszeichen auf Ober-/Unterseite: art 'kreuz' (Balkenkreuz) oder 'kokarde'."""
        sg = -1 if spiegel else 1
        z_of = lambda x, y, off: fl_z(secs, x, y, oben) + (off if oben else -off)
        hint = (0, 0, 1 if oben else -1)
        if art == "kreuz":
            for (s, a, off, mat) in ((d * 1.0, d * 0.17, 0.012, "Flug Weiss"), (d * 0.86, d * 0.12, 0.022, "Flug Schwarz")):
                for (u, v) in ((s, a), (a, s)):
                    q = [(x0 + du, sg * (y0 + dv), z_of(x0 + du, y0 + dv, off)) for du, dv in
                         ((-u / 2, -v / 2), (u / 2, -v / 2), (u / 2, v / 2), (-u / 2, v / 2))]
                    self.poly(q, mat, hint)
        else:
            for (rr, off, mat) in ((d * 0.5, 0.012, "Flug Blau"), (d * 0.40, 0.02, "Flug Weiss"), (d * 0.27, 0.028, "Flug Rot")):
                q = [(x0 + rr * math.cos(2 * math.pi * k / 14), sg * (y0 + rr * math.sin(2 * math.pi * k / 14)),
                      z_of(x0 + rr * math.cos(2 * math.pi * k / 14), y0 + rr * math.sin(2 * math.pi * k / 14), off)) for k in range(14)]
                self.poly(q, mat, hint)

    def rumpf_zeichen(self, stat, x0, d, art):
        """Zeichen auf beiden Rumpfseiten (senkrechte Flaeche bei y = +-(w + 0,015))."""
        w, zc = _stat_ip(stat, x0)
        for sg in (-1, 1):
            yy = sg * (w + 0.015)
            hint = (0, sg, 0)
            if art == "kreuz":
                for (s, a, dy, mat) in ((d, d * 0.17, 0.0, "Flug Weiss"), (d * 0.86, d * 0.12, 0.012 * sg, "Flug Schwarz")):
                    for (u, v) in ((s, a), (a, s)):
                        q = [(x0 + du, yy + dy, zc + dv) for du, dv in ((-u / 2, -v / 2), (u / 2, -v / 2), (u / 2, v / 2), (-u / 2, v / 2))]
                        self.poly(q, mat, hint)
            else:
                for (rr, dy, mat) in ((d * 0.5, 0.0, "Flug Blau"), (d * 0.40, 0.012 * sg, "Flug Weiss"), (d * 0.27, 0.024 * sg, "Flug Rot")):
                    q = [(x0 + rr * math.cos(2 * math.pi * k / 14), yy + dy, zc + rr * math.sin(2 * math.pi * k / 14)) for k in range(14)]
                    self.poly(q, mat, hint)


def _stat_ip(stat, x):
    """Halbbreite und Mittelhoehe des Rumpfs bei x (stat: Liste (x, zc, w, h, c) mit fallendem x)."""
    for k in range(len(stat) - 1):
        if stat[k][0] >= x >= stat[k + 1][0]:
            t = (stat[k][0] - x) / max(1e-9, stat[k][0] - stat[k + 1][0])
            return (_lerp(stat[k][2], stat[k + 1][2], t), _lerp(stat[k][1], stat[k + 1][1], t))
    return (stat[-1][2], stat[-1][1])


def rumpf(f, stat, mats, kappe_vorn=False):
    f.loft([rbox(x, 0.0, zc, w, h, c) for (x, zc, w, h, c) in stat], mats, caps=(kappe_vorn, True))


def spinner(f, x0, zc, r, x_spitze, mat="Flug Schwarzgruen", band=None):
    n = 10
    rings = [runde(x0, 0.0, zc, r, n)]
    for fx, fr in ((0.35, 0.85), (0.7, 0.55), (0.92, 0.25)):
        rings.append(runde(_lerp(x0, x_spitze, fx), 0.0, zc, r * fr, n))
    rings.append(runde(x_spitze, 0.0, zc, 0.02, n))
    f.loft(rings, mat, caps=(True, False))
    if band:
        f.loft([runde(_lerp(x0, x_spitze, 0.30), 0.0, zc, r * 0.88 + 0.005, n), runde(_lerp(x0, x_spitze, 0.42), 0.0, zc, r * 0.78 + 0.005, n)],
               band, caps=(False, False))


def bombe(f, x, y, z, L, r, mat="Flug Bombe", nick=True):
    """Bombe mit Spitze und Leitwerk (Kreuzleitwerk im Ring)."""
    n = 8
    xs = [(L / 2, 0.05), (L / 2 - 0.10 * L, 0.78), (L / 2 - 0.28 * L, 1.0), (-L / 2 + 0.34 * L, 1.0), (-L / 2 + 0.10 * L, 0.55), (-L / 2, 0.4)]
    f.loft([runde(x + a, y, z, r * b, n) for a, b in xs], mat, caps=(False, True), nick=nick)
    xa, xb = x - L / 2, x - L / 2 + 0.26 * L
    for ang in (0, 90):
        c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
        d = r * 1.7
        f.loft([[(xa, y - c * d / 2 - 0.008, z - s * d / 2), (xa, y + c * d / 2 - 0.008, z + s * d / 2), (xa, y + c * d / 2 + 0.008, z + s * d / 2), (xa, y - c * d / 2 + 0.008, z - s * d / 2)],
                [(xb, y - c * d / 2 - 0.008, z - s * d / 2), (xb, y + c * d / 2 - 0.008, z + s * d / 2), (xb, y + c * d / 2 + 0.008, z + s * d / 2), (xb, y - c * d / 2 + 0.008, z - s * d / 2)]],
               mat, nick=nick)
    f.loft([runde(xa, y, z, r * 0.9, n), runde(xb - 0.02, y, z, r * 0.9, n)], "Flug Metall", caps=(False, False), nick=nick)


def leitwerk(f, fin, rud, stab, mat_fin, mat_rud, mat_stab, dicke=0.1, streben=None):
    """Seitenleitwerk (Polygone in x/z) mit Ruder, Hoehenleitwerk (Schnitte) und optionale Streben [(von, nach)]."""
    for poly, m in ((fin, mat_fin), (rud, mat_rud)):
        f.loft([[(x, -dicke / 2, z) for x, z in poly], [(x, dicke / 2, z) for x, z in poly]], m)
    for sp in (False, True):
        f.fluegel(stab, (mat_stab, mat_stab), spiegel=sp)
    if streben:
        for (a, b2) in streben:
            for sg in (-1, 1):
                f.beam((a[0], sg * a[1], a[2]), (b2[0], sg * b2[1], b2[2]), 0.05, 0.05, "Flug Metall")


# ------------------------------------------------------------------ Junkers Ju 87 B "Stuka"
def stuka(b, ox, oy, psi, z0=0.0):
    f = Fz(b, ox, oy, psi, z0, nick=11.0, pivot=(0.8, 2.0))
    G, B_ = "Flug Gruen", "Flug Hellblau"
    stat = [(5.02, 2.00, .30, .30, .12), (4.60, 2.05, .40, .46, .15), (3.60, 2.12, .44, .60, .18), (2.40, 2.18, .46, .75, .20),
            (1.20, 2.20, .46, .85, .20), (-0.20, 2.15, .46, .88, .20), (-1.80, 2.15, .40, .80, .20), (-3.20, 2.20, .30, .64, .18),
            (-4.60, 2.30, .20, .44, .12), (-5.80, 2.38, .10, .24, .06)]
    rumpf(f, stat, [G, G, G, G, G, B_, B_, B_])
    spinner(f, 5.0, 2.0, 0.30, 5.72, "Flug Schwarzgruen", band="Flug Gelb")
    f.schraube(5.04, 2.0, 1.7, 3, "Flug Schwarzgruen", "Flug Gelb")
    # Kuehlerkinn unter der Nase mit dunklem Einlauf
    f.loft([rbox(4.50, 0, 1.60, .34, .20, .05), rbox(3.60, 0, 1.50, .44, .30, .08), rbox(2.60, 0, 1.55, .40, .22, .06), rbox(2.15, 0, 1.64, .28, .12, .04)],
           B_, caps=(False, True))
    f.loft([rbox(4.50, 0, 1.60, .34, .20, .05), rbox(4.56, 0, 1.60, .30, .17, .05)], "Flug Schwarz", caps=(True, True))
    # Auspuffstutzen (6 je Seite) und MG-Wuelste auf der Haube
    for sg in (-1, 1):
        for k in range(6):
            xx = 3.0 + 0.27 * k
            f.beam((xx, sg * 0.42, 2.22), (xx + 0.05, sg * 0.56, 2.16), 0.10, 0.08, "Flug Metall")
    # Dach/Kanzel (Doppelsitzer) mit Rahmen
    glas = [rbox(1.75, 0, 3.02, .24, .12, .05), rbox(1.25, 0, 3.17, .36, .30, .12), rbox(0.2, 0, 3.26, .43, .40, .14),
            rbox(-1.2, 0, 3.22, .41, .38, .14), rbox(-2.4, 0, 3.05, .31, .22, .10), rbox(-3.0, 0, 2.90, .18, .10, .04)]
    f.loft(glas, "Flug Glas")
    for xx, zz, w_, h_ in ((1.25, 3.17, .365, .305), (0.2, 3.26, .435, .405), (-0.5, 3.25, .43, .395), (-1.2, 3.22, .415, .385), (-2.4, 3.05, .315, .225)):
        f.loft([rbox(xx, 0, zz, w_, h_, .12), rbox(xx - 0.06, 0, zz, w_, h_, .12)], "Flug Gruen", caps=(False, False))
    f.beam((-1.35, 0.0, 3.30), (-3.15, 0.0, 3.46), 0.05, 0.05, "Flug Schwarz")                       # MG 15 des Bordschuetzen
    f.beam((1.9, 0.0, 3.08), (1.86, 0.0, 3.50), 0.04, 0.04, "Flug Metall")                           # Antennenmast
    f.beam((1.86, 0.0, 3.50), (-5.5, 0.0, 4.20), 0.012, 0.012, "Flug Schwarz")
    # Tragflaeche: Knickfluegel (innen nach unten, aussen nach oben)
    secs = [(0.40, 1.50, 3.30, 1.75, .46), (1.40, 1.45, 3.15, 1.62, .44), (2.50, 1.20, 2.85, 1.42, .38), (4.20, 0.85, 2.20, 1.70, .26),
            (5.90, 0.50, 1.50, 2.05, .17), (6.75, 0.32, 1.00, 2.25, .10), (6.90, 0.25, 0.45, 2.28, .05)]
    for sp in (False, True):
        f.fluegel(secs, (G, B_), tip_mat="Flug Gelb", tip_ab=4, spiegel=sp)
        sg = -1 if sp else 1
        # Hoheitszeichen oben und unten auf dem Aussenfluegel
        f.fluegel_zeichen(secs, 4.5, -0.15, 1.15, "kreuz", True, sp)
        f.fluegel_zeichen(secs, 4.5, -0.15, 1.15, "kreuz", False, sp)
        # Querruder-/Klappenfugen
        for (ya, yb, xx) in ((4.2, 6.5, -0.65), (0.9, 2.3, -1.15)):
            q = [(xx, sg * ya, fl_z(secs, xx, ya) + 0.012), (xx - 0.05, sg * ya, fl_z(secs, xx - 0.05, ya) + 0.012),
                 (xx - 0.05, sg * yb, fl_z(secs, xx - 0.05, yb) + 0.012), (xx, sg * yb, fl_z(secs, xx, yb) + 0.012)]
            f.poly(q, "Flug Schwarzgruen", (0, 0, 1))
        # Sturzflugbremse: Klappenstangen unter der Hinterkante
        for k in range(3):
            ya = 2.9 + 0.7 * k
            xle, c, zc, t = sek_ip(secs, ya)
            f.beam((xle - c + 0.15, sg * ya, zc - t / 2 - 0.05), (xle - c + 0.15, sg * (ya + 0.45), zc - t / 2 - 0.05), 0.5, 0.05, "Flug Metall")
        # MG 17 im Fluegel
        xle, c, zc, t = sek_ip(secs, 3.3)
        f.beam((xle + 0.55, sg * 3.3, zc + 0.02), (xle - 0.25, sg * 3.3, zc + 0.02), 0.07, 0.07, "Flug Metall")
        # 2 x 50-kg-Bomben unter dem Fluegel
        for ya in (3.55, 4.35):
            xle, c, zc, t = sek_ip(secs, ya)
            zb = zc - t / 2 - 0.20
            f.beam((xle - 0.55 * c, sg * ya, zb + 0.16), (xle - 0.55 * c, sg * ya, zb + 0.28), 0.10, 0.28, "Flug Metall")
            bombe(f, xle - 0.55 * c, sg * ya, zb, 1.05, 0.10)
    # Fahrwerkshosen (starr) mit Raedern
    for sg in (-1, 1):
        yy = sg * 2.45
        sp_ = [(1.15, .50, .12, .28, .06), (0.65, .70, .21, .60, .08), (-0.45, .72, .22, .64, .08), (-1.30, .88, .15, .45, .06), (-1.75, .98, .07, .16, .03)]
        f.loft([rbox(x, yy, zc_, w_, h_, c_) for (x, zc_, w_, h_, c_) in sp_], "Flug Gruen", caps=(False, True), nick=False)
        f.rad(0.0, yy, 0.50, 0.50, 0.46)
        f.beam((0.3, sg * 2.45, 1.28), (0.3, sg * 2.45, 1.44), 0.18, 0.18, "Flug Metall", False, False)
    # Sporn
    a = f.N(-5.05, 0.0, 2.15)
    f.beam((a[0], 0.0, a[2]), (a[0] - 0.10, 0.0, 0.34), 0.07, 0.07, "Flug Metall", False, False)
    f.rad(a[0] - 0.12, 0.0, 0.22, 0.22, 0.12, n=8)
    # Leitwerk
    fin = [(-3.1, 2.80), (-4.7, 4.30), (-5.1, 4.30), (-5.2, 2.65)]
    rud = [(-5.1, 4.30), (-5.85, 4.28), (-5.95, 2.60), (-5.2, 2.65)]
    stab = [(0.15, -4.05, 1.75, 2.46, .12), (1.30, -4.35, 1.40, 2.50, .09), (2.10, -4.55, 0.90, 2.52, .06), (2.18, -4.62, 0.40, 2.52, .03)]
    leitwerk(f, fin, rud, stab, G, "Flug Gruen", G, streben=[((-4.2, 0.12, 2.05), (-4.6, 1.55, 2.46))])
    # Rumpfkreuze
    f.rumpf_zeichen(stat, -3.15, 0.78, "kreuz")
    # Mittelbombe 500 kg am Schwenkarm (Gabel)
    for xx in (-0.15, 0.75):
        for sg in (-1, 1):
            f.beam((xx, sg * 0.32, 1.38), (xx, sg * 0.30, 0.96), 0.07, 0.07, "Flug Metall")
    bombe(f, 0.30, 0.0, 0.90, 1.65, 0.25)
    return b


# ------------------------------------------------------------------ Jaeger: Bf 109 E, Fw 190 A, Spitfire Mk I
def jaeger(b, ox, oy, psi, typ, z0=0.0, anstrich=None):
    f = Fz(b, ox, oy, psi, z0, nick=12.0, pivot=(0.3, 1.0))
    if typ == "fw190":
        up, lo = "Flug Grau", "Flug Hellgrau"
        stat = [(2.55, 1.45, .55, .55, .26), (2.20, 1.45, .62, .62, .28), (1.40, 1.47, .60, .64, .26), (0.50, 1.50, .48, .66, .20),
                (-0.70, 1.50, .40, .62, .18), (-2.20, 1.50, .30, .50, .14), (-3.80, 1.55, .20, .34, .10), (-4.90, 1.60, .08, .20, .05)]
        spin = (2.55, 1.45, .34, 3.00)
        secs = [(0.45, 0.55, 2.60, 0.95, .34), (1.50, 0.50, 2.45, 0.97, .30), (3.20, 0.28, 1.85, 1.05, .20), (4.70, 0.05, 1.20, 1.15, .13),
                (5.15, -0.08, 0.80, 1.18, .08), (5.25, -0.12, 0.30, 1.19, .03)]
        gear = (1.35, 1.78, .41, .20)
        fin = [(-3.0, 1.95), (-4.1, 3.25), (-4.55, 3.25), (-4.7, 1.80)]
        rud = [(-4.55, 3.25), (-5.15, 3.15), (-5.25, 1.75), (-4.7, 1.80)]
        stab = [(0.15, -3.7, 1.5, 1.60, .10), (1.5, -4.05, 1.1, 1.62, .08), (2.1, -4.2, .6, 1.63, .05), (2.2, -4.25, 0.25, 1.63, .03)]
        glas = [rbox(1.0, 0, 2.05, .22, .1, .05), rbox(0.55, 0, 2.17, .36, .27, .12), rbox(-0.5, 0, 2.20, .36, .30, .12), rbox(-1.5, 0, 2.05, .26, .18, .08), rbox(-2.0, 0, 1.92, .16, .08, .03)]
        rahm = ((0.55, 2.17, .36, .27), (-0.5, 2.20, .36, .30), (-1.5, 2.05, .26, .18))
        marke, mfl = "kreuz", "kreuz"
        schr = (3, 1.6)
    elif typ == "spitfire":
        up, lo = "Flug Gruen", "Flug Himmelgrau"
        stat = [(3.20, 1.42, .24, .26, .10), (2.40, 1.45, .32, .38, .13), (1.20, 1.50, .38, .52, .15), (0.20, 1.52, .40, .62, .16),
                (-0.90, 1.50, .34, .56, .14), (-2.40, 1.50, .26, .44, .12), (-3.90, 1.52, .16, .30, .08), (-5.00, 1.55, .07, .17, .04)]
        spin = (3.20, 1.42, .27, 3.85)
        secs = [(0.45, 0.80, 2.70, 0.95, .33), (1.50, 0.85, 2.55, 0.97, .28), (3.00, 0.90, 2.00, 1.04, .20), (4.50, 0.90, 1.20, 1.12, .12),
                (5.35, 0.88, 0.60, 1.16, .07), (5.58, 0.86, 0.25, 1.17, .03)]
        gear = (2.0, 2.0, .36, .19)
        fin = [(-3.3, 1.90), (-4.35, 3.00), (-4.8, 3.05), (-5.0, 1.75)]
        rud = [(-4.8, 3.05), (-5.25, 2.85), (-5.3, 1.70), (-5.0, 1.75)]
        stab = [(0.15, -3.9, 1.4, 1.56, .09), (1.5, -4.2, 1.0, 1.58, .07), (2.1, -4.45, 0.55, 1.59, .05), (2.2, -4.5, 0.25, 1.59, .03)]
        glas = [rbox(1.0, 0, 2.00, .20, .09, .04), rbox(0.55, 0, 2.15, .32, .28, .12), rbox(-0.5, 0, 2.18, .32, .30, .12), rbox(-1.5, 0, 2.03, .22, .16, .07), rbox(-2.1, 0, 1.90, .12, .07, .03)]
        rahm = ((0.55, 2.15, .32, .28), (-0.5, 2.18, .32, .30), (-1.5, 2.03, .22, .16))
        marke, mfl = "kokarde", "kokarde"
        schr = (3, 1.55)
    else:                                                                       # bf109
        up, lo = (anstrich or ("Flug Gruen", "Flug Hellblau"))
        stat = [(3.30, 1.40, .26, .26, .10), (2.70, 1.43, .34, .36, .12), (1.60, 1.47, .40, .50, .14), (0.40, 1.47, .40, .60, .16),
                (-0.80, 1.45, .36, .58, .16), (-2.20, 1.48, .28, .46, .13), (-3.60, 1.52, .19, .33, .09), (-4.65, 1.56, .08, .18, .05)]
        spin = (3.30, 1.40, .27, 3.95)
        secs = [(0.38, 0.85, 2.45, 0.95, .32), (1.20, 0.80, 2.30, 0.97, .28), (2.60, 0.62, 1.85, 1.05, .20), (4.30, 0.42, 1.25, 1.16, .13), (4.93, 0.36, 1.05, 1.19, .10)]
        gear = (1.05, 1.05, .37, .17)
        fin = [(-2.9, 1.95), (-4.0, 3.10), (-4.3, 3.10), (-4.35, 1.80)]
        rud = [(-4.3, 3.10), (-4.9, 3.00), (-4.95, 1.70), (-4.35, 1.80)]
        stab = [(0.15, -3.5, 1.4, 1.58, .10), (1.4, -3.85, 1.0, 1.60, .08), (1.95, -4.0, 0.7, 1.61, .06)]
        glas = [rbox(1.1, 0, 1.95, .20, .10, .04), rbox(0.7, 0, 2.07, .34, .26, .10), rbox(-0.3, 0, 2.13, .36, .30, .10), rbox(-1.4, 0, 2.00, .28, .20, .08), rbox(-2.0, 0, 1.82, .18, .10, .04)]
        rahm = ((0.7, 2.07, .34, .26), (-0.3, 2.13, .36, .30), (-1.4, 2.00, .28, .20))
        marke, mfl = "kreuz", "kreuz"
        schr = (3, 1.55)
    rumpf(f, stat, [up, up, up, up, up, lo, lo, lo])
    x0, zc0, r0, xt = spin
    spinner(f, x0, zc0, r0, xt, "Flug Schwarzgruen" if typ != "fw190" else "Flug Grau", band="Flug Gelb" if typ == "bf109" else None)
    f.schraube(x0 + 0.04, zc0, schr[1], schr[0], "Flug Schwarzgruen", "Flug Gelb" if typ == "bf109" else None)
    f.loft(glas, "Flug Glas")
    for (xx, zz, w_, h_) in rahm:
        f.loft([rbox(xx, 0, zz, w_ + .008, h_ + .008, .1), rbox(xx - 0.05, 0, zz, w_ + .008, h_ + .008, .1)], up, caps=(False, False))
    # Tragflaechen mit Zeichen
    for sp in (False, True):
        sg = -1 if sp else 1
        f.fluegel(secs, (up, lo), spiegel=sp, tip_mat=("Flug Gelb" if typ == "bf109" else None), tip_ab=(len(secs) - 2 if typ == "bf109" else None))
        yz = secs[-1][0] * 0.62
        f.fluegel_zeichen(secs, yz, sek_ip(secs, yz)[0] - sek_ip(secs, yz)[1] * 0.5, 0.95, mfl, True, sp)
        f.fluegel_zeichen(secs, yz, sek_ip(secs, yz)[0] - sek_ip(secs, yz)[1] * 0.5, 0.95, mfl, False, sp)
        # Querruderfuge
        ya, yb = secs[-1][0] * 0.55, secs[-1][0] * 0.97
        xl, ch = sek_ip(secs, ya)[0], sek_ip(secs, ya)[1]
        xx = xl - 0.72 * ch
        q = [(xx, sg * ya, fl_z(secs, xx, ya) + 0.01), (xx - 0.04, sg * ya, fl_z(secs, xx - 0.04, ya) + 0.01),
             (xx - 0.04, sg * yb, fl_z(secs, xx - 0.04, yb) + 0.01), (xx, sg * yb, fl_z(secs, xx, yb) + 0.01)]
        f.poly(q, "Flug Schwarzgruen", (0, 0, 1))
        # Fahrwerk: Bein, Rad, Abdeckung
        ya, yw, rw, ww = gear
        yb_ = sg * ya
        zt = fl_z(secs, 0.4, ya if typ != "bf109" else 0.6, False) + 0.03
        f.beam((0.35, sg * (0.6 if typ == "bf109" else ya), zt), (0.30, sg * yw, rw + 0.05), 0.10, 0.07, "Flug Metall", True, False)
        f.rad(0.30, sg * yw + sg * 0.02, rw, rw, ww)
        f.beam((0.35, sg * (0.6 if typ == "bf109" else ya), zt - 0.02), (0.30, sg * (yw + 0.12), rw * 1.4), 0.04, 0.34, up, True, False)
        # Bewaffnung: Kanonen/MG vor der Vorderkante
        xl, c_, zc_, t_ = sek_ip(secs, secs[-1][0] * 0.4)
        f.beam((xl + 0.35, sg * secs[-1][0] * 0.4, zc_ + 0.0), (xl - 0.2, sg * secs[-1][0] * 0.4, zc_ + 0.0), 0.06, 0.06, "Flug Metall")
        if typ == "bf109":                                                       # Tragflaechenkuehler
            f.kasten(0.35, -0.7, sg * 1.9, sg * 2.5, 0.62, 0.9, "Flug Metall")
        if typ == "spitfire":                                                    # Kuehlerbaeuche unter den Fluegeln
            f.kasten(0.05, -0.85, sg * 2.4, sg * 3.0, 0.68, 0.92, lo)
    # Rumpfdetails
    if typ == "bf109":
        f.loft([rbox(2.9, 0, 1.12, .22, .14, .05), rbox(2.2, 0, 1.10, .26, .16, .05), rbox(1.7, 0, 1.15, .18, .10, .03)], "Flug Metall", caps=(True, True))
    if typ == "fw190":
        f.loft([runde(2.58, 0, 1.45, 0.58), runde(2.50, 0, 1.45, 0.58)], "Flug Metall", caps=(True, True))        # Kuehlerlufteinlauf-Kragen
        f.loft([runde(2.55, 0, 1.45, 0.50), runde(2.52, 0, 1.45, 0.50)], "Flug Schwarz", caps=(True, True))
        f.loft([rbox(2.35, 0, 1.45, .56, .56, .26), rbox(2.22, 0, 1.45, .58, .58, .27)], "Flug Gelb", caps=(False, False))
    if typ == "spitfire":
        for sg in (-1, 1):
            for k in range(6):
                f.beam((2.5 - 0.22 * k, sg * 0.34, 1.62), (2.5 - 0.22 * k - 0.04, sg * 0.46, 1.58), 0.09, 0.06, "Flug Metall")
        f.loft([rbox(1.5, 0, 1.55, .20, .12, .04), rbox(0.8, 0, 1.58, .22, .13, .04)], up, caps=(True, True))
    leitwerk(f, fin, rud, stab, up, "Flug Gelb" if typ == "bf109" else up, up,
             streben=[((-3.9, 0.12, 1.55), (-4.1, 1.2, 1.58))] if typ == "bf109" else None)
    f.rumpf_zeichen(stat, -2.65 if typ != "spitfire" else -2.75, 0.8 if typ != "spitfire" else 0.9, marke)
    # Spornrad
    a = f.N(-4.2, 0.0, 1.55)
    f.beam((a[0], 0.0, a[2]), (a[0] - 0.05, 0.0, 0.22), 0.06, 0.06, "Flug Metall", False, False)
    f.rad(a[0] - 0.06, 0.0, 0.17, 0.17, 0.09, n=8)
    return b


# ------------------------------------------------------------------ Tankwagen
def tankwagen(b, ox, oy, psi, z0=0.0):
    f = Fz(b, ox, oy, psi, z0)
    # Fahrgestell mit Leiterrahmen
    f.kasten(-5.0, 5.0, -0.55, 0.55, 0.62, 0.88, "Flug Metall", nick=False)
    # Fahrerhaus
    f.loft([rbox(5.12, 0, 1.95, 1.12, 1.0, 0.16), rbox(3.35, 0, 1.95, 1.18, 1.05, 0.12)], "Tankwagen Kabine", caps=(True, True), nick=False)
    f.kasten(5.12, 5.16, -0.95, 0.95, 1.85, 2.72, "Flug Glas", nick=False)                         # Frontscheibe
    for sg in (-1, 1):
        f.kasten(3.95, 4.95, sg * 1.17, sg * 1.2, 1.85, 2.72, "Flug Glas", nick=False)            # Seitenscheibe
        f.kasten(3.52, 3.88, sg * 1.17, sg * 1.2, 1.85, 2.62, "Flug Glas", nick=False)
        f.kasten(5.12, 5.17, sg * 0.82, sg * 1.02, 1.0, 1.25, "Tankwagen Lampe", nick=False)        # Scheinwerfer
        f.beam((4.9, sg * 1.2, 2.0), (4.95, sg * 1.45, 2.3), 0.04, 0.04, "Flug Metall", False, False)  # Spiegelarm
        f.kasten(4.88, 4.98, sg * 1.42, sg * 1.5, 2.1, 2.55, "Flug Schwarz", nick=False)
        f.kasten(4.0, 4.9, sg * 1.17, sg * 1.19, 0.95, 1.0, "Flug Metall", nick=False)             # Trittbrett
    f.kasten(5.12, 5.18, -0.7, 0.7, 1.05, 1.65, "Flug Schwarz", nick=False)                         # Kuehlergrill
    f.kasten(5.1, 5.45, -1.15, 1.15, 0.55, 0.85, "Flug Metall", nick=False)                         # Stossstange
    f.kasten(4.15, 4.55, -0.25, 0.25, 2.98, 3.2, "Flug Gelb", nick=False)                           # Rundumleuchte
    f.beam((3.2, 1.0, 2.1), (3.2, 1.0, 4.0), 0.14, 0.14, "Flug Metall", False, False)               # Auspuffrohr hinter der Kabine
    # Tank: Ovalquerschnitt, Abschnitte mit Bandagen
    def oval(x, k=1.0):
        return [(x, 1.12 * k * math.cos(2 * math.pi * i / 16), 2.05 + 0.92 * k * math.sin(2 * math.pi * i / 16)) for i in range(16)]
    f.loft([oval(-4.35, 0.9), oval(-4.25), oval(2.85), oval(2.95, 0.9)], "Tankwagen Alu", nick=False)
    for xx in (-2.45, -0.1, 2.0):
        f.loft([oval(xx - 0.06, 1.015), oval(xx + 0.06, 1.015)], "Flug Metall", caps=(False, False), nick=False)
    for sg in (-1, 1):                                                                              # rotes Band und Schriftfeld
        f.poly([(-3.9, sg * 1.145, 1.80), (2.5, sg * 1.145, 1.80), (2.5, sg * 1.145, 2.05), (-3.9, sg * 1.145, 2.05)], "Tankwagen Rot", (0, sg, 0), nick=False)
        f.poly([(-1.6, sg * 1.15, 1.35), (0.4, sg * 1.15, 1.35), (0.4, sg * 1.15, 1.72), (-1.6, sg * 1.15, 1.72)], "Tankwagen Orange", (0, sg, 0), nick=False)
    # Mannloecher, Laufsteg mit Gelaender, Armaturenhaube
    for xx in (-3.2, -0.9, 1.4):
        f.kasten(xx - 0.35, xx + 0.35, -0.35, 0.35, 2.92, 3.2, "Flug Metall", nick=False)
        f.kasten(xx - 0.25, xx + 0.25, -0.25, 0.25, 3.2, 3.26, "Tankwagen Alu", nick=False)
    f.kasten(-4.0, 2.7, -0.2, 0.2, 2.96, 3.0, "Flug Metall", nick=False)
    for sg in (-1, 1):
        f.beam((-3.9, sg * 0.45, 3.0), (2.6, sg * 0.45, 3.0), 0.04, 0.04, "Flug Gelb", False, False)
    # Heck: Armaturenschrank, Schlauchtrommel, Leiter
    f.kasten(-5.55, -4.3, -1.1, 1.1, 0.88, 2.0, "Tankwagen Rot", nick=False)
    f.kasten(-5.58, -5.55, -1.0, -0.1, 1.0, 1.9, "Flug Metall", nick=False)
    f.kasten(-5.58, -5.55, 0.1, 1.0, 1.0, 1.9, "Flug Metall", nick=False)
    n = 12
    trommel = lambda y, r: [(-5.0 + r * math.cos(2 * math.pi * k / n), y, 2.35 + r * math.sin(2 * math.pi * k / n)) for k in range(n)]
    f.loft([trommel(-0.9, 0.36), trommel(0.9, 0.36)], "Flug Schwarz", nick=False)                  # aufgewickelter Schlauch
    f.loft([trommel(-0.95, 0.12), trommel(0.95, 0.12)], "Flug Metall", nick=False)
    for sg in (-1, 1):
        f.kasten(-5.6, -5.0, sg * 0.97, sg * 1.05, 2.0, 2.7, "Flug Metall", nick=False)
    for k in range(5):
        f.beam((-5.3, -1.06, 0.9 + 0.5 * k), (-5.3, -0.62, 0.9 + 0.5 * k), 0.04, 0.04, "Flug Metall", False, False)
    f.beam((-5.2, 1.06, 0.7), (-5.2, 1.06, 2.9), 0.05, 0.05, "Flug Metall", False, False)
    f.beam((-4.7, 1.06, 0.7), (-4.7, 1.06, 2.9), 0.05, 0.05, "Flug Metall", False, False)
    for k in range(5):
        f.beam((-5.2, 1.06, 1.0 + 0.45 * k), (-4.7, 1.06, 1.0 + 0.45 * k), 0.04, 0.04, "Flug Metall", False, False)
    # Raeder: Vorderachse einfach, Hinterachsen doppelt bereift (Tandem), Kotfluegel
    for xx, zwill in ((3.9, False), (-2.7, True), (-4.0, True)):
        for sg in (-1, 1):
            if zwill:
                f.rad(xx, sg * 1.05, 0.55, 0.55, 0.26)
                f.rad(xx, sg * 1.35, 0.55, 0.55, 0.26)
            else:
                f.rad(xx, sg * 1.1, 0.55, 0.55, 0.30)
            ym = sg * (1.2 if zwill else 1.1)
            f.kasten(xx - 0.7, xx + 0.7, ym - 0.28 if sg > 0 else ym - 0.52, ym + 0.52 if sg > 0 else ym + 0.28, 1.05, 1.1, "Tankwagen Kabine", nick=False)
    # Kollision (nur bei Kurs in 90-Grad-Schritten achsenparallel)
    if round(psi) % 90 == 0:
        hw = [f.P(x, y, 0.0, False) for x in (-5.6, 5.45) for y in (-1.5, 1.5)]
        xs, ys = [p[0] for p in hw], [p[1] for p in hw]
        b.bx.append((min(xs), min(ys), z0, max(xs), max(ys), z0 + 3.3))
    return b
