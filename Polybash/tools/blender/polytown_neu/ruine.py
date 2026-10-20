"""Burgruine auf dem Burgberg nordlich der Stadt (hinter der Kirche), Gipfel bei umgebung.RUINE, Hoehe umgebung.RUINE_Z.

Rustikal und verfallen, keine fertige Burg: Bruchsteinmauern mit abgebrochenen Kronen, Fensterpfeiler ohne Sturz, Torruine mit
halbem Bogen, Bergfried-Stumpf, Palas mit Giebelrest und Kamin, Grundmauern eines Wirtschaftsbaus, Brunnen, Schutthalden, Efeu und
Moos. Ein Karrenweg (Pfad, Serpentinen) fuehrt von der Spange Nord zum Tor.

Begehbar (jede Stufe <= 0,30 m, Quader des Gebaeudes registrieren b.bx; feine Reliefs nicht):
  * Treppe an der Innenseite der Suedmauer -> Wehrgang (3,9 m) -> Eckbastion Suedwest; Zinnenreste an der Aussenkante.
  * Treppe im Bergfried (Innenwand, zwei Laeufe) -> Mauerkrone Nord/Ost (6,7 m) mit Aussicht ueber das Tal.
  * Steintreppe an der Nordmauer -> Nordmauerkrone (2,8 m) hinter dem Palas.
  * Schutthalde an der Ostmauer (Bresche): Stufenhalde von aussen in den Hof.
  * Grundmauern (0,28 m) und niedrige Quader im Hof zum Draufspringen."""
import math
import random

import burg as B
import stadt as S
import talkessel as T
import umgebung as U
import wald as W

S.FARBEN.update({"Efeu": ((0.15, 0.29, 0.11), 1.0, 0.0), "Efeu hell": ((0.24, 0.38, 0.14), 1.0, 0.0), "Russ": ((0.07, 0.065, 0.06), 1.0, 0.0),
                 "Burgstein": ((0.58, 0.55, 0.49), 0.95, 0.0), "Burgstein dunkel": ((0.36, 0.34, 0.31), 0.95, 0.0),
                 "Burgstein warm": ((0.63, 0.56, 0.45), 0.95, 0.0), "Felsen Burg": ((0.44, 0.42, 0.38), 0.97, 0.0)})
for _n, _c in (("Stein", ((0.62, 0.61, 0.58), 0.9, 0.0)), ("Stein alt", ((0.50, 0.48, 0.44), 0.95, 0.0)), ("Stein dunkel", ((0.34, 0.33, 0.31), 0.95, 0.0)),
               ("Moos", ((0.24, 0.31, 0.17), 1.0, 0.0)), ("Holz dunkel", ((0.22, 0.15, 0.10), 0.95, 0.0)), ("Eisen", ((0.18, 0.17, 0.16), 0.6, 0.4)),
               ("Pfad", ((0.52, 0.46, 0.36), 0.95, 0.0)), ("Brunnenwasser", ((0.12, 0.16, 0.17), 0.1, 0.0))):
    S.FARBEN.setdefault(_n, _c)

RX, RY = U.RUINE
MAUER = ("Burgstein", "Burgstein", "Stein alt", "Burgstein dunkel", "Stein alt", "Burgstein warm")
KERN = ("Stein alt", "Burgstein dunkel", "Stein dunkel")
WEG = ((90.0, 205.0), (82.0, 214.0), (73.0, 222.0), (66.0, 229.0), (72.0, 236.0), (62.0, 243.0), (46.0, 245.0), (51.0, 249.5), (54.0, 251.4))
BELEGT = ((86.0, 200.0, 94.0, 209.0), (78.0, 210.0, 87.0, 218.0), (70.0, 218.0, 78.0, 226.0), (62.0, 226.0, 70.0, 233.0), (36.0, 242.0, 80.0, 282.0))


def interp(pts):
    """Stueckweise lineare Hoehenfunktion durch (a, h)."""
    def f(a):
        if a <= pts[0][0]:
            return pts[0][1]
        for (a0, h0), (a1, h1) in zip(pts, pts[1:]):
            if a <= a1:
                return h0 + (h1 - h0) * (a - a0) / (a1 - a0) if a1 > a0 else h1
        return pts[-1][1]
    return f


def stufen(pts):
    """Treppenfoermige Hoehenfunktion: pts = [(a_bis, h), ...]."""
    def f(a):
        for ab, h in pts:
            if a <= ab:
                return h
        return pts[-1][1]
    return f


class Ruine:
    def __init__(self, zb, name="burgruine"):
        self.b = B.Bau(name)
        self.zb = zb
        self.rnd = random.Random(40161)

    # ------------------------------------------------------------ Grundbausteine (lokale Koordinaten: x Ost, y Nord, z ueber dem Gipfel)
    def box(self, x0, y0, z0, x1, y1, z1, mat):
        self.b.box(RX + x0, RY + y0, self.zb + z0, RX + x1, RY + y1, self.zb + z1, mat)

    def fein(self, x0, y0, z0, x1, y1, z1, mat):
        """Wie box, aber kein Hindernis (Reliefs, Efeu, lose Steine)."""
        n = len(self.b.bx)
        self.box(x0, y0, z0, x1, y1, z1, mat)
        del self.b.bx[n:]

    def pbox(self, ach, a0, a1, p0, p1, z0, z1, mat, fein=False):
        if z1 - z0 < 1e-4 or a1 - a0 < 1e-4:
            return
        f = self.fein if fein else self.box
        if ach == "x":
            f(a0, p0, z0, a1, p1, z1, mat)
        else:
            f(p0, a0, z0, p1, a1, z1, mat)

    def pt(self, ach, a, p, z):
        return (RX + (a if ach == "x" else p), RY + (p if ach == "x" else a), self.zb + z)

    def relief(self, ach, face, sg, a0, a1, z0, z1, oeff=()):
        """Bruchsteinreihen aus der Wandflaeche (1..7 cm), nicht begehbar."""
        rnd = self.rnd
        z = z0
        while z < z1 - 0.1:
            h = min(rnd.uniform(0.26, 0.5), z1 - z)
            a = a0 + rnd.uniform(0.0, 0.4)
            while a < a1 - 0.15:
                w = min(rnd.uniform(0.4, 1.25), a1 - a)
                if w > 0.2 and not any(o[0] - 0.02 < a + w and o[1] + 0.02 > a and o[2] - 0.02 < z + h and o[3] + 0.02 > z for o in oeff):
                    p0, p1 = sorted((face, face + sg * rnd.uniform(0.012, 0.07)))
                    self.pbox(ach, a + 0.02, a + w - 0.02, p0, p1, z + 0.015, z + h - 0.015, rnd.choice(MAUER), fein=True)
                a += w
            z += h

    def mauer(self, ach, p, a0, a1, t, prof, opens=(), flach=False, efeu=0.22, innen=True, aussen=True, z0=-1.3):
        """Bruchsteinmauer entlang ach ('x' oder 'y') bei Quermitte p, Dicke t. prof(a) = Kronenhoehe (abgebrochen: je Stein +-0,3 m).
        opens: (oa0, oa1, z_unten, z_oben) - z_oben None: nach oben offen (Sturz und Mauer darueber fehlen)."""
        rnd = self.rnd
        cuts = {a0, a1}
        for o in opens:
            cuts |= {min(max(o[0], a0), a1), min(max(o[1], a0), a1)}
        cuts = sorted(cuts)
        for u0, u1 in zip(cuts, cuts[1:]):
            if u1 - u0 < 1e-3:
                continue
            op = [o for o in opens if o[0] - 1e-6 <= (u0 + u1) / 2 <= o[1] + 1e-6]
            a = u0
            while a < u1 - 1e-3:
                w = rnd.uniform(0.8, 1.9)
                if u1 - a - w < 0.5:
                    w = u1 - a
                b0, b1 = a, a + w
                a = b1
                top = prof((b0 + b1) / 2)
                if not flach:
                    top += rnd.uniform(-0.3, 0.25)
                top = max(top, 0.25)
                zs, zt = (op[0][2], op[0][3]) if op else (None, None)
                segs = []
                if op:
                    if zs > 0.05:
                        segs.append((z0, min(zs, top), 0.0))
                    if zt is not None and top > zt + 0.2:
                        segs.append((zt, top, zt))
                else:
                    segs.append((z0, top, 0.0))
                for (sa, sb, rz) in segs:
                    self.pbox(ach, b0, b1, p - t / 2, p + t / 2, sa, sb, rnd.choice(KERN))
                    zr = max(rz, 0.0)
                    if aussen:
                        self.relief(ach, p - t / 2, -1, b0, b1, zr, sb)
                    if innen:
                        self.relief(ach, p + t / 2, 1, b0, b1, zr, sb)
                    if not flach and sb > 0.6:                                   # lose Steine auf der Bruchkante
                        for _ in range(rnd.randint(0, 2)):
                            c = rnd.uniform(b0 + 0.15, b1 - 0.15)
                            q = rnd.uniform(p - t / 2 + 0.1, p + t / 2 - 0.4)
                            s = rnd.uniform(0.2, 0.5)
                            self.pbox(ach, c - s / 2, c + s / 2, q, q + s * rnd.uniform(0.6, 1.0), sb, sb + rnd.uniform(0.08, 0.3), rnd.choice(MAUER), fein=True)
                    elif flach and rnd.random() < 0.3:                          # Moos auf der Krone
                        self.pbox(ach, b0 + 0.1, b1 - 0.1, p - t / 2 + 0.2, p + t / 2 - 0.2, sb, sb + 0.035, "Moos", fein=True)
                    if sb > 2.2 and rnd.random() < efeu:                          # Efeu
                        sg = rnd.choice((-1, 1))
                        fc = p + sg * (t / 2 + 0.085)
                        h = rnd.uniform(1.2, min(sb - 0.3, 3.8))
                        c0 = rnd.uniform(b0, max(b0, b1 - 0.6))
                        self.pbox(ach, c0, min(b1, c0 + rnd.uniform(0.4, 1.0)), min(fc, fc + sg * 0.03), max(fc, fc + sg * 0.03), zr, zr + h, rnd.choice(("Efeu", "Efeu hell")), fein=True)

    def treppe(self, ach, vorz, start, quer0, quer1, n, rise, run, z_start=0.0, mat=None, rail=None):
        """Treppe laengs ach: Stufe i deckt [start + vorz*run*i, +run] ab, quer von quer0..quer1; Steigungen leicht unregelmaessig (<= 0,30 m)."""
        rnd = self.rnd
        steig = [rise * rnd.uniform(0.92, 1.06) for _ in range(n)]
        sc = rise * n / sum(steig)
        z = z_start
        for i in range(n):
            z += steig[i] * sc
            a0 = start + vorz * run * i
            a1 = a0 + vorz * run
            lo, hi = min(a0, a1), max(a0, a1)
            q0 = quer0
            m = mat or rnd.choice(("Burgstein", "Stein alt", "Burgstein warm"))
            self.pbox(ach, lo, hi, q0, quer1, z_start - 0.6 if i == 0 else z_start, z, m)
            if rail and i >= rail[1]:                                       # niedrige Bruchsteinbrüstung an der offenen Seite (Absturzschutz), rail = (Seite, ab Stufe)
                qa, qb = (quer0, quer0 + 0.2) if rail[0] == "min" else (quer1 - 0.2, quer1)
                self.pbox(ach, lo, hi, qa, qb, z, z + 0.85, "Burgstein dunkel")
        return z

    def brocken(self, x, y, z, r, mat=None, flach=0.7):
        """Lose Steinbrocken (unregelmaessiges 6-seitiges Polyeder), kein Hindernis."""
        rnd = self.rnd
        n = 6
        ph = rnd.uniform(0, 6.28)
        ring = [(RX + x + r * rnd.uniform(0.7, 1.15) * math.cos(2 * math.pi * i / n + ph), RY + y + r * rnd.uniform(0.7, 1.15) * math.sin(2 * math.pi * i / n + ph),
                 self.zb + z + r * rnd.uniform(0.25, 0.5)) for i in range(n)]
        top = (RX + x + r * rnd.uniform(-0.2, 0.2), RY + y + r * rnd.uniform(-0.2, 0.2), self.zb + z + r * rnd.uniform(0.7, 1.0) * flach + 0.15 * r)
        bot = (RX + x, RY + y, self.zb + z - 0.25 * r)
        self.b.add(ring + [top, bot], [(i, (i + 1) % n, n) for i in range(n)] + [((i + 1) % n, i, n + 1) for i in range(n)], mat or rnd.choice(MAUER))

    def bogen(self, ach, p, t, mitte, zk, halb, seite, n=4, hoehe=1.1):
        """Spitzbogenrest: n Wolbsteine (Balken) von der Kaempferlinie zk ausgehend; seite -1/+1 = linker/rechter Ast."""
        pts = []
        for i in range(n + 1):
            th = (i / n) * 1.15
            pts.append((mitte + seite * halb * math.cos(th) * (1.0 - 0.55 * i / n), zk + hoehe * math.sin(th) * 1.25))
        for (a0, z0), (a1, z1) in zip(pts, pts[1:]):
            self.b.beam(self.pt(ach, a0, p, z0), self.pt(ach, a1, p, z1), t + 0.1, 0.34, self.rnd.choice(MAUER))

    def halde(self, x0, y0, x1, y1, richt, n=8, rise=0.26, breite=0.45):
        """Stufenhalde (Schutt): n Lagen mit jeweils kleinerer Grundflaeche, begehbar; darauf lose Brocken. richt 'x': Kamm quer zur x-Achse."""
        rnd = self.rnd
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        for k in range(n):
            hw = breite * (n - k) + 0.4
            sh = 0.18 * k
            if richt == "x":
                self.box(cx - hw + rnd.uniform(-0.2, 0.2), y0 + sh + rnd.uniform(0, 0.15), -0.6 if k == 0 else 0.0, cx + hw + rnd.uniform(-0.2, 0.2), y1 - sh - rnd.uniform(0, 0.15),
                         rise * (k + 1), rnd.choice(MAUER))
            else:
                self.box(x0 + sh, cy - hw, -0.6 if k == 0 else 0.0, x1 - sh, cy + hw, rise * (k + 1), rnd.choice(MAUER))
        top = rise * n
        for _ in range(int(7 + (x1 - x0 + y1 - y0))):
            self.brocken(rnd.uniform(x0, x1), rnd.uniform(y0, y1), rnd.uniform(0.0, top * 0.8), rnd.uniform(0.25, 0.6))


# ------------------------------------------------------------------ die Anlage
def burg(R):
    rnd = R.rnd
    b = R.b
    # ---- Suedmauer (Torfront), Wehrgang auf der Westhaelfte
    R.mauer("x", -9.0, -8.6, -3.4, 1.5, lambda a: 3.9, opens=((-6.1, -5.7, 1.5, 2.7),), flach=True)
    R.mauer("x", -9.0, -3.4, -2.0, 1.5, interp([(-3.4, 5.4), (-2.0, 4.9)]))                        # Torpfeiler (stehende Seite)
    R.mauer("x", -9.0, 2.0, 3.0, 1.5, interp([(2.0, 3.4), (3.0, 2.8)]))                           # Torpfeiler (Ostseite, tiefer)
    R.mauer("x", -9.0, 3.0, 11.5, 1.5, interp([(3.0, 2.6), (5.5, 2.0), (8.0, 1.1), (9.5, 0.5), (11.5, 0.35)]))
    # Zinnenreste auf der Aussenkante des Wehrgangs
    x = -8.2
    while x < -3.5:
        if rnd.random() > 0.32:
            R.box(x, -9.75, 3.9, x + 0.8, -9.25, 4.85, rnd.choice(MAUER))
        x += 1.55
    # Treppe an der Innenseite zum Wehrgang
    R.treppe("x", -1, -3.0, -8.25, -7.25, 14, 3.9 / 14, 0.30, rail=("max", 3))
    # Plattform am oberen Ende (verbindet Treppe, Wehrgang und Eckbastion; Bruestung an den offenen Kanten)
    R.box(-8.6, -8.25, -1.3, -6.9, -6.8, 3.9, "Stein alt")
    R.box(-8.6, -6.95, 3.9, -6.9, -6.8, 4.75, "Burgstein dunkel")
    R.box(-7.05, -7.25, 3.9, -6.9, -6.95, 4.75, "Burgstein dunkel")
    # ---- Eckbastion Suedwest (Plattform 3,9 m)
    R.box(-12.0, -10.4, -1.3, -8.6, -6.8, 3.9, "Stein alt")
    R.relief("x", -10.4, -1, -12.0, -8.6, 0.0, 3.9)
    R.relief("y", -12.0, -1, -10.4, -6.8, 0.0, 3.9)
    R.relief("y", -8.6, 1, -10.4, -6.8, 0.0, 3.9)
    R.relief("x", -6.8, 1, -12.0, -8.6, 0.0, 3.9)
    for (xa, xb, ya, yb) in ((-12.0, -11.35, -9.7, -6.8), (-12.0, -8.6, -10.4, -9.85)):         # Brustwehr, teilweise eingestuerzt
        L = max(xb - xa, yb - ya)
        n = int(L / 0.9)
        for i in range(n):
            if rnd.random() < 0.3:
                continue
            if xb - xa > yb - ya:
                R.box(xa + i * L / n, ya, 3.9, xa + (i + 0.7) * L / n, yb, 3.9 + rnd.uniform(0.7, 1.15), rnd.choice(MAUER))
            else:
                R.box(xa, ya + i * L / n, 3.9, xb, ya + (i + 0.7) * L / n, 3.9 + rnd.uniform(0.7, 1.15), rnd.choice(MAUER))
    # ---- Westmauer: Wehrgang-Ende, dann Bruch, dann Palaswand mit drei Fenstern
    R.mauer("y", -10.75, -6.8, -3.0, 1.5, lambda a: 3.9, flach=True)
    R.mauer("y", -10.75, -3.0, 1.5, 1.5, interp([(-3.0, 2.7), (-0.5, 1.7), (1.5, 3.2)]))
    fenster = ((2.2, 3.4, 2.6, None), (4.3, 5.5, 2.6, None), (6.4, 7.6, 2.6, None))
    R.mauer("y", -10.75, 1.5, 9.25, 1.5, interp([(1.5, 7.0), (3.0, 8.2), (5.0, 8.7), (7.0, 7.9), (9.25, 6.4)]), opens=fenster)
    for (a0, a1), s in (((2.2, 3.4), -1), ((4.3, 5.5), 1), ((6.4, 7.6), 0)):                     # Bogenansaetze der Fenster (ein Ast ueberlebt)
        if s:
            R.bogen("y", -10.75, 1.5, (a0 + a1) / 2, 5.2, (a1 - a0) / 2 + 0.1, s, n=3)
    for (a0, a1, _, _) in fenster:                                                              # Fensterbank
        R.fein(-11.62, a0 - 0.1, 2.55, -9.88, a1 + 0.1, 2.68, "Burgstein warm")
    # ---- Nordmauer: Krone 2,8 m, Treppe von der Hofseite
    R.mauer("x", 10.0, -11.5, -9.5, 1.5, interp([(-11.5, 5.2), (-9.5, 3.4)]))
    R.mauer("x", 10.0, -9.5, 3.9, 1.5, lambda a: 2.8, opens=((-1.2, -0.7, 1.0, 2.0),), flach=True)
    R.treppe("x", -1, 3.1, 8.25, 9.25, 10, 2.8 / 10, 0.30, rail=("min", 3))
    # Plattform am oberen Ende (an der Palas-Giebelwand und der Nordmauerkrone; Bruestung an den offenen Seiten)
    R.box(-1.7, 7.6, -0.6, 0.1, 9.25, 2.8, "Stein alt")
    R.box(-1.7, 7.6, 2.8, 0.1, 7.75, 3.65, "Burgstein dunkel")
    R.box(-0.05, 7.75, 2.8, 0.1, 8.25, 3.65, "Burgstein dunkel")
    # ---- Ostmauer mit Bresche (Halde)
    R.mauer("y", 10.75, -8.25, -5.8, 1.5, interp([(-8.25, 3.4), (-5.8, 1.6)]))
    R.mauer("y", 10.75, -2.0, 3.0, 1.5, interp([(-2.0, 1.8), (0.5, 3.0), (3.0, 4.2)]))
    R.halde(9.9, -5.8, 11.9, -2.0, "x", n=8)
    # ---- Torruine: halber Spitzbogen links, Sturz am Boden, Eisenreste
    R.bogen("x", -9.0, 1.5, 0.0, 3.2, 2.0, -1, n=4, hoehe=1.15)
    R.fein(0.6, -12.2, 0.0, 2.2, -11.2, 0.55, "Burgstein warm")                                 # herabgefallener Sturz
    R.fein(-2.07, -9.3, 1.3, -1.97, -9.2, 1.7, "Eisen")                                         # Angelband
    R.fein(-2.07, -9.3, 2.3, -1.97, -9.2, 2.7, "Eisen")
    R.fein(-2.05, -9.78, 0.0, 2.05, -8.22, 0.04, "Burgstein dunkel")                           # Torschwelle
    # ---- Bergfried-Stumpf (Nordost): aussen 3,9..11,5 x 3,0..10,75, Waende 1,65
    R.mauer("x", 3.825, 3.9, 11.5, 1.65, interp([(3.9, 6.2), (6.0, 7.4), (8.0, 8.4), (10.0, 9.5), (11.5, 8.9)]), opens=((7.0, 7.4, 3.0, 4.2),))
    R.mauer("x", 9.925, 3.9, 6.2, 1.65, interp([(3.9, 3.4), (6.2, 5.0)]))
    R.mauer("x", 9.925, 6.2, 11.5, 1.65, lambda a: 6.72, flach=True)
    R.mauer("y", 4.725, 4.65, 9.1, 1.65, interp([(4.65, 5.4), (6.0, 4.6), (8.0, 3.9), (9.1, 4.8)]), opens=((6.0, 7.4, 0.0, 2.5),))
    R.mauer("y", 10.675, 4.65, 6.0, 1.65, interp([(4.65, 8.0), (6.0, 6.7)]), opens=((4.9, 5.3, 2.4, 3.6),))
    R.mauer("y", 10.675, 6.0, 9.1, 1.65, lambda a: 6.72, flach=True)
    # Treppen im Turm: Lauf A (Sued, nach Ost), Podest, Lauf B (Ost, nach Nord) bis zur Mauerkrone
    ra = R.treppe("x", 1, 5.55, 4.65, 5.65, 11, 0.28, 0.30)
    R.box(8.85, 4.65, -0.6, 9.85, 5.65, ra + 0.28, "Burgstein")                                  # Podest
    rb = R.treppe("y", 1, 5.65, 8.85, 9.85, 11, 0.28, 0.30, z_start=ra + 0.28, rail=("min", 0))
    R.box(8.85, 5.65 + 0.30 * 10, rb - 0.1, 9.85, 9.1, rb, "Burgstein")                         # oberste Stufe bis zur Krone
    # Plattform am Treppenende: Auflager an der Nordmauer (Krone 6,72 m) reicht 1,1 m in den Turm; Bruestung zur Turmmitte
    R.box(6.2, 8.0, 5.9, 8.85, 9.1, 6.72, "Burgstein")
    R.box(6.2, 7.85, 6.72, 8.85, 8.0, 7.55, "Burgstein dunkel")
    R.box(6.2, 8.0, 6.72, 6.4, 9.1, 7.55, "Burgstein dunkel")
    for (cx, cy) in ((5.7, 8.9), (5.7, 6.0)):                                                     # Balkenkonsolen der zerstoerten Decke
        R.fein(cx - 0.15, cy - 0.15, 4.0, cx + 0.2, cy + 0.2, 4.3, "Burgstein warm")
    for yy in (5.4, 6.9, 8.2):
        R.fein(5.55, yy, 4.2, 6.05, yy + 0.22, 4.45, "Burgstein warm")
    # ---- Palas: Giebelwand (Staffelgiebel) mit Fenster und Kamin, Suedmauer als niedrige Grundmauer
    R.mauer("y", -2.35, 1.5, 9.25, 1.3, stufen([(2.5, 5.2), (4.0, 6.4), (5.5, 7.6), (6.8, 8.7), (9.25, 6.0)]), opens=((3.9, 5.2, 2.2, None),), efeu=0.4)
    R.mauer("x", 0.9, -10.0, -3.0, 1.2, lambda a: 0.9, opens=((-6.2, -4.2, 0.0, None),), efeu=0.0)
    R.relief("y", -3.0, -1, 1.5, 9.25, 0.0, 4.0)
    # Kamin an der Giebelwand (Innenseite, x < -3.0)
    for yy in (6.3, 7.75):
        R.box(-3.95, yy, 0.0, -3.0, yy + 0.4, 1.7, "Burgstein warm")
    R.box(-3.95, 6.3, 1.7, -3.0, 8.15, 2.0, "Burgstein dunkel")
    R.box(-3.5, 6.5, 2.0, -3.0, 7.95, 4.4, "Burgstein")
    R.fein(-3.03, 6.7, 0.05, -3.0, 7.75, 1.6, "Russ")
    R.box(-3.0, 6.75, 5.0, -1.7, 7.95, 9.6, "Burgstein dunkel")                                   # Schornsteinrest ueber der Giebelkante
    R.fein(-3.0, 6.55, 0.0, -2.3, 6.9, 0.14, "Russ")
    # Bodenplatten im Palas
    for _ in range(9):
        px, py = rnd.uniform(-9.4, -3.8), rnd.uniform(1.8, 8.6)
        R.fein(px, py, 0.0, px + rnd.uniform(0.6, 1.1), py + rnd.uniform(0.5, 0.9), 0.05, rnd.choice(MAUER))
    # ---- Grundmauern eines Wirtschaftsbaus (0,28 m, begehbar) und Quader zum Hinaufsteigen
    for (x0, y0, x1, y1) in ((4.0, -6.5, 9.0, -6.0), (4.0, -2.8, 9.0, -2.3), (4.0, -6.5, 4.5, -2.3), (8.5, -6.5, 9.0, -4.8)):
        R.box(x0, y0, -0.3, x1, y1, 0.28, rnd.choice(MAUER))
    R.box(6.0, -5.0, 0.0, 7.2, -4.2, 0.56, "Burgstein warm")                                    # Herdstelle
    R.box(-1.2, -5.0, 0.0, 0.2, -4.2, 0.28, "Stein alt")                                       # Quaderstufen zum Draufsteigen
    R.box(0.2, -5.0, 0.0, 1.4, -4.2, 0.56, "Stein alt")
    R.box(1.4, -5.0, 0.0, 2.6, -4.2, 0.84, "Burgstein")
    # ---- Brunnen mit eingestuerzter Einfassung
    bx0, by0 = -3.0, -3.0
    b.prism(RX + bx0, RY + by0, R.zb, 1.15, 0.85, 8, "Burgstein")
    b.prism(RX + bx0, RY + by0, R.zb + 0.7, 0.78, 0.16, 8, "Brunnenwasser")
    b.bx.append((RX + bx0 - 1.1, RY + by0 - 1.1, R.zb, RX + bx0 + 1.1, RY + by0 + 1.1, R.zb + 0.85))
    for i in range(3):
        a = 0.6 + i * 2.1
        R.brocken(bx0 + 1.4 * math.cos(a), by0 + 1.4 * math.sin(a), 0.0, 0.35)
    # ---- Saeulentrommeln und Schutt im Hof, an den Mauerfuessen und aussen
    for (x, y) in ((-6.0, -2.0), (-5.2, -2.4), (0.8, 3.0), (7.8, -0.2)):
        R.b.prism(RX + x, RY + y, R.zb, 0.42, 0.55, 8, "Burgstein warm")
    for _ in range(80):
        x, y = rnd.uniform(-12.5, 12.5), rnd.uniform(-12.5, 10.5)
        if abs(x + 3.0) < 1.6 and abs(y + 3.0) < 1.6:
            continue
        if abs(x) < 2.3 and y < -8.2:
            continue
        R.brocken(x, y, 0.0, rnd.uniform(0.18, 0.5))


def bewuchs(R):
    """Baeume und Buesche in der Ruine (Eiche im Hof, Buesche an den Mauern)."""
    W.laubbaum(R.b, RX - 6.5, RY - 4.8, R.zb, lambda i: T._h01(88, i, 4142))
    for (x, y) in ((-9.6, -5.5), (9.3, -8.0), (2.4, 9.0), (-1.0, -7.0), (9.5, 1.5), (-9.2, 0.2)):
        W.busch(R.b, RX + x, RY + y, R.zb, lambda i, x=x, y=y: T._h01(int(x * 10), i + int(y), 4143))


def berghang(zb_fn=None):
    """Baeume am Burgberg und auf dem Kamm zur Nordwestecke (nicht auf dem Gipfelplateau und nicht auf dem Karrenweg)."""
    b = B.Bau("ruine_hang")
    for ix in range(0, 24):
        for iy in range(0, 16):
            x = 6.0 + ix * 4.4 + (T._h01(ix, iy, 4150) - 0.5) * 3.6
            y = 226.0 + iy * 4.6 + (T._h01(ix, iy, 4151) - 0.5) * 3.6
            dr = math.hypot(x - RX, y - RY)
            if dr < 17.0 or U._burgberg_abstand(x, y) > 37.0 or y > 293.0 or x < 5.0:
                continue
            dichte = 0.25 + 0.5 * T.fbm(x / 16.0, y / 16.0, T.SEED + 91, 2)
            if T._h01(ix, iy, 4152) > dichte or min(_dist_weg(x, y), 99.0) < 4.5:
                continue
            zb = U.gelaende_hoehe(x, y)
            k = int(T._h01(ix, iy, 4153) * 10)
            s = ix * 97 + iy * 31
            rnd = lambda i, s=s: T._h01(s, i, 4154)
            if k < 5:
                W.tanne(b, x, y, zb, rnd)
            elif k < 8:
                W.laubbaum(b, x, y, zb, rnd)
            else:
                W.busch(b, x, y, zb, rnd)
    return b


def _dist_weg(x, y):
    best = 1e9
    for (ax, ay), (bx, by) in zip(WEG, WEG[1:]):
        best = min(best, U._seg_abstand(x, y, (ax, ay), (bx, by)))
    return best


def weg():
    """Karrenweg von der Spange Nord zum Burgtor (folgt dem Gelaende), mit Randsteinen."""
    b = B.Bau("ruine_weg")
    U.pfad(b, list(WEG), 3.0, 0.05, "Pfad")
    for (ax, ay), (bx, by) in zip(WEG, WEG[1:]):
        n = int(math.hypot(bx - ax, by - ay) / 3.2)
        for i in range(1, n):
            t = i / n
            x, y = ax + (bx - ax) * t, ay + (by - ay) * t
            dx, dy = bx - ax, by - ay
            ln = math.hypot(dx, dy)
            for sg in (-1, 1):
                if T._h01(i, int(x), 4160 + sg) < 0.5:
                    px, py = x - dy / ln * 1.9 * sg, y + dx / ln * 1.9 * sg
                    b.box(px - 0.22, py - 0.22, U.gelaende_hoehe(px, py) - 0.05, px + 0.22, py + 0.22, U.gelaende_hoehe(px, py) + 0.3, "Stein alt")
    return b


def bauen_ruine(zb=None):
    """Rueckgabe: Liste von Bau (Ruine, Hang, Weg). zb = Hoehe des Gipfels (None = umgebung.RUINE_Z)."""
    R = Ruine(U.RUINE_Z if zb is None else zb)
    burg(R)
    bewuchs(R)
    return [R.b, berghang(), weg()]
