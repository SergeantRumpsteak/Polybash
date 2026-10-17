"""Polybash - Talkessel: Polytown von Grund auf, Schritt 1 (Gelaende).

Ein Wiesental (eben; Huegel und Senken liefert umgebung.gelaende_hoehe) mit den Massen der Standardkarte (Spielflaeche 0..300 m in x und y, Mitte bei
150/150), ringsum alpine Berge. Strassen, Gebaeude usw. folgen in spaeteren Schritten; spiel.py bleibt unveraendert.

Start:    blender --background --python talkessel.py
          (optional Ausgabeordner:  ... -- /pfad/zum/ordner)
Ergebnis: ~/blender_out/talkessel.blend

Alle Masse in Metern, Blender ist Z-oben. Das Tal liegt bei z = 0 und ist exakt eben; die Berge steigen erst
ausserhalb der Spielflaeche an. Alle wichtigen Zahlen stehen unten bei "Parameter".
"""
import math
import os
import sys

import bpy

# ------------------------------------------------------------------ Parameter
TAL = 300.0         # Seitenlaenge der Spielflaeche (wie WORLD der Standardkarte)
ZELLE = 4.0         # Gitterweite des Berggelaendes (wie CELL im Spiel); TAL und GUERTEL muessen Vielfache sein
GUERTEL = 200.0     # Breite des Berglandes ausserhalb des Tals
BREITE = 150.0      # Abstand vom Talrand, bei dem der Bergkamm seine volle Hoehe erreicht (schwankt)
HOEHE = 105.0       # Grundhoehe der Berge; die Gipfel werden durch die Gratform deutlich hoeher
SCHNEE_H = 90.0     # Schneegrenze (m), schwankt um etwa 15 m
SOCKEL = -40.0      # Unterkante der Aussenwand (ausserhalb des Blickfelds)
WIESE_ZELLE = 5.0   # Raster der Wiesenflaeche (zum spaeteren Bearbeiten und Texturieren; auch Aufloesung der Huegel)
SEED = 7

_MATS = {}


# ------------------------------------------------------------------ Rauschen (ohne bpy, deterministisch)
def _h01(ix, iy, seed):
    h = (ix * 374761393 + iy * 668265263 + seed * 1442695041) & 0xFFFFFFFF
    h = ((h ^ (h >> 13)) * 1274126177) & 0xFFFFFFFF
    h ^= h >> 16
    return h / 4294967295.0


def _fade(t):
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0)


def noise(x, y, seed):
    """Gradientenrauschen, Werte etwa 0..1 (Mittel 0.5)."""
    ix, iy = math.floor(x), math.floor(y)
    fx, fy = x - ix, y - iy

    def g(cx, cy):
        a = _h01(cx, cy, seed) * 6.283185307179586
        return math.cos(a) * (x - cx) + math.sin(a) * (y - cy)

    u, v = _fade(fx), _fade(fy)
    n00, n10, n01, n11 = g(ix, iy), g(ix + 1, iy), g(ix, iy + 1), g(ix + 1, iy + 1)
    a = n00 + (n10 - n00) * u
    b = n01 + (n11 - n01) * u
    return min(1.0, max(0.0, 0.5 + (a + (b - a) * v) * 0.8))


def fbm(x, y, seed, okt=4):
    s, amp, f, tot = 0.0, 1.0, 1.0, 0.0
    for k in range(okt):
        s += amp * noise(x * f, y * f, seed + k * 17)
        tot += amp
        amp *= 0.5
        f *= 2.03
    return s / tot


def grat(x, y, seed, okt=4):
    """Gratiger Fraktalwert: scharfe Kaemme und spitze Gipfel, Werte etwa 0..1."""
    s, amp, f, tot = 0.0, 1.0, 1.0, 0.0
    for k in range(okt):
        n = 1.0 - abs(2.0 * noise(x * f, y * f, seed + k * 29) - 1.0)
        s += amp * n * n
        tot += amp
        amp *= 0.5
        f *= 2.1
    return s / tot


# ------------------------------------------------------------------ Hoehenfunktion
def abstand(x, y):
    """Abstand zur quadratischen Spielflaeche (0 darin und auf dem Rand); Ecken sind dadurch abgerundet."""
    return math.hypot(max(-x, x - TAL, 0.0), max(-y, y - TAL, 0.0))


TUNNEL_Y = 27.0          # Gleis 3 verlaesst das Tal nach Osten und verschwindet bei x = TUNNEL_X im Berg (ausserhalb der Spielflaeche)
TUNNEL_X = 352.0
TUNNEL_L = 16.0          # Laenge des Felsblocks (bahn/tunnel.py) hinter dem Portal, in dem das Gelaende ausgeschnitten bleibt


def _glatt(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3.0 - 2.0 * t)


def hoehe(x, y):
    """Gelaendehoehe mit Bahneinschnitt: das Gleis laeuft in einer Schlucht (Sohle z = 0, Boeschung ueber 12 m) bis zum Tunnelportal; dahinter
    ersetzt ein Felsblock den ausgeschnittenen Berg (tunnel.py)."""
    h = hoehe_roh(x, y)
    if x < 130.0 and y > 190.0 and not (0.0 < x < TAL and 0.0 < y < TAL):                                              # Burgberg-Kamm (umgebung.rand_anschluss): Berge setzen auf seiner Hoehe an
        try:
            import umgebung as _U
            h += _U.rand_anschluss(x, y) * (1.0 - _glatt(0.0, 120.0, abstand(x, y)))
        except ImportError:
            pass
    if x > TAL and x < TUNNEL_X + TUNNEL_L:
        cut = (1.0 - _glatt(5.0, 17.0, abs(y - TUNNEL_Y)))
        h *= 1.0 - cut
    return h


def hoehe_roh(x, y):
    """Gelaendehoehe ohne Einschnitt: exakt 0 im Tal, ausserhalb steigen erst sanfte Auslaeufer, dann Felswaende und Gipfel."""
    d = abstand(x, y)
    if d <= 0.0:
        return 0.0
    breite = BREITE * (0.80 + 0.45 * noise(x / 300.0, y / 300.0, SEED + 3))   # Gebirge mal naeher, mal weiter weg
    s = min(1.0, d / breite)
    env = HOEHE * s ** 1.8                                                      # sanft am Fuss, steil in der Mitte
    form = (0.40 + 1.00 * grat(x / 120.0, y / 120.0, SEED, 3)                   # Kaemme und Gipfel
            + 0.35 * (fbm(x / 260.0, y / 260.0, SEED + 7, 2) - 0.5))            # grosse Massive
    fein = 0.20 * (fbm(x / 24.0, y / 24.0, SEED + 11, 2) - 0.5)                 # Felsstruktur
    return max(0.0, env * (form + fein))


# ------------------------------------------------------------------ Gitter und Dreiecke (ohne bpy)
def berg_netz():
    """Berggelaende als Dreiecksnetz um das Tal.

    Rueckgabe: (verts, tris, rand) - rand: Indizes der aeusseren Randpunkte, gegen den Uhrzeigersinn.
    Die Zellen im Tal werden ausgelassen (dort liegt die ebene Wiese); die Punkte auf dem Talrand haben z = 0.
    """
    n = int(round((TAL + 2.0 * GUERTEL) / ZELLE))
    off = GUERTEL
    verts, vid = [], {}

    def vert(i, j):
        k = (i, j)
        if k in vid:
            return vid[k]
        x, y = i * ZELLE - off, j * ZELLE - off
        innen = 0.0 <= x <= TAL and 0.0 <= y <= TAL
        aussen = i in (0, n) or j in (0, n)
        if not innen and not aussen:                    # leicht verschieben: unregelmaessige, natuerliche Facetten
            # +-0.2 Zellen je Achse: klein genug, dass kein Dreieck umklappt (Hoehe eines Dreiecks = 0.7 Zellen)
            x += (_h01(i, j, SEED + 1) - 0.5) * ZELLE * 0.4
            y += (_h01(i, j, SEED + 2) - 0.5) * ZELLE * 0.4
        vid[k] = len(verts)
        verts.append((x, y, hoehe(x, y)))
        return vid[k]

    tris = []
    for j in range(n):
        for i in range(n):
            cx, cy = (i + 0.5) * ZELLE - off, (j + 0.5) * ZELLE - off
            if 0.0 < cx < TAL and 0.0 < cy < TAL:
                continue                                 # Zelle liegt im Tal
            a, b, c, e = vert(i, j), vert(i + 1, j), vert(i + 1, j + 1), vert(i, j + 1)
            if (i + j) % 2 == 0:
                tris += [(a, b, c), (a, c, e)]
            else:
                tris += [(a, b, e), (b, c, e)]
    rand = ([vert(i, 0) for i in range(n)] + [vert(n, j) for j in range(n)]
            + [vert(i, n) for i in range(n, 0, -1)] + [vert(0, j) for j in range(n, 0, -1)])
    return verts, tris, rand


def wiesen_netz(loch=None, hf=None):
    """Wiese, Raster WIESE_ZELLE, Flaechen gegen den Uhrzeigersinn (Normale nach oben).

    loch = (x0, y0, x1, y1) oder Liste solcher Rechtecke (auf dem Raster), die ausgespart werden, z. B. Burggelaende und Steinbruchgrube.
    hf(x, y) -> Hoehe: Huegel und Senken im Tal (muss am Talrand und am Lochrand 0 sein); ohne hf ist die Wiese eben (z = 0)."""
    n = int(round(TAL / WIESE_ZELLE))
    st = TAL / n
    verts, vid, faces = [], {}, []
    loecher = [] if loch is None else ([loch] if not isinstance(loch[0], (tuple, list)) else list(loch))

    def vert(i, j):
        if (i, j) not in vid:
            vid[(i, j)] = len(verts)
            verts.append((i * st, j * st, hf(i * st, j * st) if hf else 0.0))
        return vid[(i, j)]

    for j in range(n):
        for i in range(n):
            if loch is not None:
                cx, cy = (i + 0.5) * st, (j + 0.5) * st
                if any(l[0] < cx < l[2] and l[1] < cy < l[3] for l in loecher):
                    continue
            faces.append((vert(i, j), vert(i + 1, j), vert(i + 1, j + 1), vert(i, j + 1)))
    return verts, faces


def normale(p, q, r):
    ux, uy, uz = q[0] - p[0], q[1] - p[1], q[2] - p[2]
    vx, vy, vz = r[0] - p[0], r[1] - p[1], r[2] - p[2]
    nx, ny, nz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
    l = math.sqrt(nx * nx + ny * ny + nz * nz) or 1.0
    return nx / l, ny / l, nz / l


STOFFE = [
    ("Wiese",       (0.36, 0.56, 0.22)),   # 0 Talboden
    ("Alm",         (0.31, 0.50, 0.21)),   # 1 Gras an den Hangfuessen
    ("Wald",        (0.13, 0.29, 0.16)),   # 2 Nadelwald-Flecken
    ("Alm hoch",    (0.47, 0.50, 0.27)),   # 3 karges Berggras
    ("Fels",        (0.47, 0.44, 0.41)),   # 4
    ("Fels dunkel", (0.32, 0.30, 0.30)),   # 5 steile Wand
    ("Schnee",      (0.94, 0.96, 0.99)),   # 6
]


def glatte_neigung(x, y, s=9.0):
    """cos(Neigung) des Hanges, ueber +-s Meter gemittelt (ruhigere Materialflaechen als pro Dreieck)."""
    gx = (hoehe(x + s, y) - hoehe(x - s, y)) / (2.0 * s)
    gy = (hoehe(x, y + s) - hoehe(x, y - s)) / (2.0 * s)
    return 1.0 / math.sqrt(1.0 + gx * gx + gy * gy)


def stoff_index(zm, nz, x, y):
    """Welches Material eine Flaeche bekommt (Hoehe, geglaettete Neigung nz, etwas Zufall)."""
    schnee = SCHNEE_H + 30.0 * (noise(x / 70.0, y / 70.0, SEED + 5) - 0.5)
    if zm > schnee and nz > 0.45:
        return 6                                          # Schnee
    if nz < 0.50:
        return 5                                          # steile Wand: dunkler Fels
    if nz < 0.70 or zm > 85.0:
        return 4                                          # Fels
    if zm > 55.0:
        return 3                                          # karges Berggras
    if zm > 8.0 and nz > 0.80 and noise(x / 45.0, y / 45.0, SEED + 9) > 0.52:
        return 2                                          # Wald
    return 1                                              # Alm


def berg_stoffe(verts, tris):
    idx = []
    for a, b, c in tris:
        p, q, r = verts[a], verts[b], verts[c]
        x, y = (p[0] + q[0] + r[0]) / 3.0, (p[1] + q[1] + r[1]) / 3.0
        idx.append(stoff_index((p[2] + q[2] + r[2]) / 3.0, glatte_neigung(x, y), x, y))
    return idx


def aussenwand(verts, rand):
    """Senkrechte Wand rund um den Aussenrand, damit man von oben nicht ins Leere sieht.

    Gibt (neue Punkte, Vierecke) zurueck; die Indizes beziehen sich auf verts + neue Punkte."""
    base = len(verts)
    neue = [(verts[k][0], verts[k][1], SOCKEL) for k in rand]
    m = len(rand)
    quads = []
    for s in range(m):
        t = (s + 1) % m
        quads.append((rand[s], base + s, base + t, rand[t]))     # Normale nach aussen
    return neue, quads


# ------------------------------------------------------------------ Blender
def out_dir():
    argv = sys.argv
    d = argv[argv.index("--") + 1] if ("--" in argv and len(argv) > argv.index("--") + 1) else \
        os.path.join(os.path.expanduser("~"), "blender_out")
    os.makedirs(d, exist_ok=True)
    return d


def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for me in list(bpy.data.meshes):
        bpy.data.meshes.remove(me)


def material(name, rgb, rauh=0.95, emit=0.0):
    """Material mit Farbe (Solid-Ansicht und Base Color); emit > 0 laesst es leuchten (Lampen)."""
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)       # Farbe der Solid-Ansicht
    try:
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)   # Material Preview / Export
            bsdf.inputs["Roughness"].default_value = rauh
            if emit > 0.0:
                bsdf.inputs["Emission Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
                bsdf.inputs["Emission Strength"].default_value = emit
    except Exception:
        pass
    _MATS[name] = m
    return m


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def add_mesh(coll, name, verts, faces, mats, mat_index=None, edges=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, edges or [], faces)
    me.update()
    for m in mats:
        me.materials.append(m)
    if mat_index is not None:
        for p, k in zip(me.polygons, mat_index):
            p.material_index = k
    try:
        for p in me.polygons:
            p.use_smooth = False                          # Low-Poly: harte Kanten
    except Exception:
        pass
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def marker(coll, name, x, y, z, kind='PLAIN_AXES', size=1.0):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = kind
    ob.empty_display_size = size
    ob.location = (x, y, z)
    coll.objects.link(ob)
    return ob


def kamera(coll, name, pos, ziel, brennweite=24.0):
    """Kamera bei pos, die auf ziel blickt (Euler XYZ ohne mathutils berechnet)."""
    dx, dy, dz = ziel[0] - pos[0], ziel[1] - pos[1], ziel[2] - pos[2]
    l = math.sqrt(dx * dx + dy * dy + dz * dz)
    rx = math.acos(max(-1.0, min(1.0, -dz / l)))
    rz = math.atan2(-dx, dy)
    cam = bpy.data.cameras.new(name)
    cam.lens = brennweite
    cam.clip_end = 3000.0
    ob = bpy.data.objects.new(name, cam)
    ob.location = pos
    ob.rotation_euler = (rx, 0.0, rz)
    coll.objects.link(ob)
    return ob


def build_tal(loch=None, hf=None):
    coll = collection("Tal")
    v, f = wiesen_netz(loch, hf)
    add_mesh(coll, "wiese", v, f, [material(*STOFFE[0])])
    # Umriss der Spielflaeche (nur Linien) - zeigt die 300 x 300 m
    r = [(0, 0, 0.05), (TAL, 0, 0.05), (TAL, TAL, 0.05), (0, TAL, 0.05)]
    ob = add_mesh(coll, "spielflaeche_rand", r, [], [], edges=[(0, 1), (1, 2), (2, 3), (3, 0)])
    try:
        ob.display_type = 'WIRE'
    except Exception:
        pass


def build_berge():
    coll = collection("Berge")
    verts, tris, rand = berg_netz()
    idx = berg_stoffe(verts, tris)
    neue, quads = aussenwand(verts, rand)
    mats = [material(*s) for s in STOFFE]
    faces = list(tris) + list(quads)
    allv = list(verts) + neue
    idx = idx + [5] * len(quads)                     # Aussenwand: dunkler Fels
    add_mesh(coll, "berge", allv, faces, mats, idx)
    return verts, tris, idx


def build_marker():
    coll = collection("Marker")
    m = TAL / 2.0
    marker(coll, "mitte", m, m, 0.0, 'PLAIN_AXES', 5.0)
    for name, (x, y) in (("ecke_sw", (0, 0)), ("ecke_so", (TAL, 0)), ("ecke_no", (TAL, TAL)), ("ecke_nw", (0, TAL))):
        marker(coll, name, x, y, 0.0, 'ARROWS', 4.0)
    cam1 = kamera(coll, "kamera_nordwand", (m, 15.0, 14.0), (m, TAL + 150.0, 75.0))
    kamera(coll, "kamera_ecke", (12.0, 12.0, 10.0), (TAL * 0.85, TAL * 0.85, 55.0))
    try:
        bpy.context.scene.camera = cam1
    except Exception:
        pass


def setup_view():
    try:
        sun = bpy.data.lights.new("Sonne", 'SUN')
        sun.energy = 4.0
        so = bpy.data.objects.new("Sonne", sun)
        so.rotation_euler = (math.radians(50), math.radians(10), math.radians(35))
        bpy.context.scene.collection.objects.link(so)
        w = bpy.data.worlds.new("Himmel")
        w.color = (0.55, 0.72, 0.90)
        bpy.context.scene.world = w
    except Exception as e:
        print("[Polybash] Licht/Himmel nicht gesetzt:", e)


def main():
    clear_scene()
    build_tal()
    verts, tris, idx = build_berge()
    build_marker()
    setup_view()
    zmax = max(v[2] for v in verts)
    zeil = {s[0]: idx.count(k) for k, s in enumerate(STOFFE)}
    path = os.path.join(out_dir(), "talkessel.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print(f"[Polybash] Talkessel: Tal {TAL:.0f} x {TAL:.0f} m eben bei z=0, hoechster Gipfel {zmax:.0f} m, "
          f"{len(tris)} Dreiecke Berge")
    print("[Polybash] Flaechen je Material:", {k: v for k, v in zeil.items() if v})
    print("[Polybash] gespeichert:", path)


if __name__ == "__main__":
    main()
