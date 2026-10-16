"""Polybash - Polytown als Blender-Blockout (graues Grundmodell mit den Massen des Spiels).

Start:   blender --background --python polytown_blockout.py
         (optional Ausgabeordner:  ... -- /pfad/zum/ordner)
Ergebnis: ~/blender_out/polytown_blockout.blend

Liest polytown_layout.json (erzeugt von dump_polytown.py aus der Standardkarte; spiel.py bleibt unveraendert).
Alle Masse in Metern, Blender ist Z-oben, Spielfeld 0..300 in x und y.
"""
import json
import math
import os
import sys

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
_MATS = {}


# ------------------------------------------------------------------ Hilfen
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


def material(name, rgb):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)
    try:
        m.use_nodes = True
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
            bsdf.inputs["Roughness"].default_value = 0.9
    except Exception:
        pass
    _MATS[name] = m
    return m


def collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def add_mesh(coll, name, verts, faces, mats, mat_index=None):
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], faces)
    me.update()
    for m in mats:
        me.materials.append(m)
    if mat_index is not None:
        for p, k in zip(me.polygons, mat_index):
            p.material_index = k
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def box_geo(x0, y0, z0, x1, y1, z1):
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    return v, f


class Geo:
    """Sammelt viele Koerper in einem Mesh."""
    def __init__(self):
        self.v, self.f = [], []

    def add(self, v, f):
        o = len(self.v)
        self.v.extend(v)
        self.f.extend(tuple(i + o for i in face) for face in f)

    def box(self, x0, y0, z0, x1, y1, z1):
        if x1 > x0 and y1 > y0 and z1 > z0:
            self.add(*box_geo(x0, y0, z0, x1, y1, z1))


def hexcol(c):
    return "%02x%02x%02x" % tuple(int(max(0.0, min(1.0, k)) * 255) for k in c)


def marker(coll, name, x, y, z, kind='ARROWS', size=1.0):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = kind
    ob.empty_display_size = size
    ob.location = (x, y, z)
    coll.objects.link(ob)
    return ob


# ------------------------------------------------------------------ Gelaende
class Terrain:
    def __init__(self, t):
        self.n, self.step, self.z = t["n"], t["step"], t["z"]

    def at(self, x, y):
        n, st = self.n, self.step
        fx = min(n - 1.000001, max(0.0, x / st))
        fy = min(n - 1.000001, max(0.0, y / st))
        i, j = int(fx), int(fy)
        tx, ty = fx - i, fy - j
        z = self.z
        a = z[j * n + i] + (z[j * n + i + 1] - z[j * n + i]) * tx
        b = z[(j + 1) * n + i] + (z[(j + 1) * n + i + 1] - z[(j + 1) * n + i]) * tx
        return a + (b - a) * ty


def build_terrain(d, T):
    coll = collection("Gelaende")
    n, st = T.n, T.step
    verts = [(i * st, j * st, T.z[j * n + i]) for j in range(n) for i in range(n)]
    faces, idx = [], []
    for j in range(n - 1):
        for i in range(n - 1):
            a, b, c, e = j * n + i, j * n + i + 1, (j + 1) * n + i + 1, (j + 1) * n + i
            faces.append((a, b, c, e))                           # gegen den Uhrzeigersinn: Normale nach oben
            dz = max(abs(T.z[b] - T.z[a]), abs(T.z[e] - T.z[a]), abs(T.z[c] - T.z[b]))
            idx.append(1 if dz / st > 0.7 else 0)                # steil: Fels
    add_mesh(coll, "gelaende", verts, faces, [material("Gras", (0.30, 0.40, 0.22)), material("Fels", (0.45, 0.42, 0.38))], idx)
    wc = collection("Wasser")
    for k, p in enumerate(d["ponds"]):
        m = 20
        v = [(p["x"], p["y"], p["water"])] + [(p["x"] + p["r"] * math.cos(2 * math.pi * q / m),
                                              p["y"] + p["r"] * math.sin(2 * math.pi * q / m), p["water"]) for q in range(m)]
        f = [(0, 1 + (q + 1) % m, 1 + q) for q in range(m)]      # Normale nach oben
        add_mesh(wc, f"teich_{k}", v, f, [material("Wasser", (0.20, 0.38, 0.62))])


def build_roads(d, T):
    coll = collection("Strassen")
    groups = {}
    for x0, y0, x1, y1, hw, kind in d["roads"]:
        dx, dy = x1 - x0, y1 - y0
        ln = math.hypot(dx, dy)
        if ln < 0.01:
            continue
        nx, ny = -dy / ln * hw, dx / ln * hw
        g = groups.setdefault(kind, Geo())
        z0, z1 = T.at(x0, y0) + 0.06, T.at(x1, y1) + 0.06
        g.add([(x0 - nx, y0 - ny, z0), (x0 + nx, y0 + ny, z0), (x1 + nx, y1 + ny, z1), (x1 - nx, y1 - ny, z1)],
              [(0, 1, 2, 3)])
        fl = groups.get(kind)
    cols = {"dirt": (0.47, 0.38, 0.27), "cobble": (0.50, 0.49, 0.47)}
    for kind, g in groups.items():
        add_mesh(coll, f"weg_{kind}", g.v, g.f, [material("Weg_" + kind, cols.get(kind, (0.5, 0.45, 0.4)))])
    g = Geo()
    for x0, y0, x1, y1, col in d["floors"]:
        zc = T.at((x0 + x1) / 2, (y0 + y1) / 2)
        g.box(x0, y0, zc - 0.02, x1, y1, zc + 0.05)
    if g.v:
        add_mesh(coll, "bodenplatten", g.v, g.f, [material("Beton", (0.45, 0.45, 0.47))])


# ------------------------------------------------------------------ Bauten
def build_boxes(d):
    coll = collection("Gebaeude")
    hid = collection("Kollision_unsichtbar")
    groups, hidden = {}, Geo()
    for x0, y0, x1, y1, z0, z1, col, vis in d["boxes"]:
        if vis:
            groups.setdefault(hexcol(col), (col, Geo()))[1].box(x0, y0, z0, x1, y1, z1)
        else:
            hidden.box(x0, y0, z0, x1, y1, z1)
    for key, (col, g) in sorted(groups.items()):
        add_mesh(coll, "bau_" + key, g.v, g.f, [material("Bau_" + key, col)])
    if hidden.v:
        ob = add_mesh(hid, "kollision_unsichtbar", hidden.v, hidden.f, [material("Kollision", (0.9, 0.1, 0.1))])
        ob.display_type = 'WIRE'
    dc = collection("Deko")
    dg = {}
    for x0, y0, x1, y1, z0, z1, col, lit in d["decor"]:
        dg.setdefault(hexcol(col), (col, Geo()))[1].box(x0, y0, z0, x1, y1, z1)
    for key, (col, g) in sorted(dg.items()):
        add_mesh(dc, "deko_" + key, g.v, g.f, [material("Deko_" + key, col)])


def gable(cx, cy, w, dpt, base, rise, ridge, ov=0.4, ovr=0.3):
    """Satteldach als (Punkte, Flaechen). ridge 'x': First entlang x."""
    if ridge == "x":
        a, b = w / 2 + ovr, dpt / 2 + ov           # a: halbe Laenge entlang des Firsts, b: halbe Breite quer dazu
    else:
        a, b = dpt / 2 + ovr, w / 2 + ov
    loc = [(-a, -b, base), (a, -b, base), (a, b, base), (-a, b, base), (-a, 0, base + rise), (a, 0, base + rise)]
    faces = [(0, 1, 5, 4), (2, 3, 4, 5), (3, 0, 4), (1, 2, 5), (0, 3, 2, 1)]
    if ridge == "x":
        v = [(cx + p, cy + q, z) for p, q, z in loc]
    else:                                           # u,v vertauscht: Spiegelung, daher Flaechen umdrehen
        v = [(cx + q, cy + p, z) for p, q, z in loc]
        faces = [tuple(reversed(f)) for f in faces]
    return v, faces


def build_roofs(d):
    coll = collection("Daecher")
    groups = {}
    chim = Geo()
    for h in (o for o in d["vis"] if o["k"] == "house"):
        if h.get("flat") or h["rise"] <= 0:
            continue
        v, f = gable(h["x"], h["y"], h["w"], h["d"], h["H"], h["rise"], h["ridge"])
        groups.setdefault(hexcol(h["roof"]), (h["roof"], Geo()))[1].add(v, f)
        c = h.get("chim")
        if c:
            chim.box(c[0], c[1], h["H"] - 0.3, c[2], c[3], h["H"] + h["rise"] + 0.8)
    for key, (col, g) in groups.items():
        add_mesh(coll, "dach_" + key, g.v, g.f, [material("Dach_" + key, col)])
    if chim.v:
        add_mesh(coll, "schornsteine", chim.v, chim.f, [material("Ziegel", (0.55, 0.30, 0.22))])


# ------------------------------------------------------------------ Natur und Marker
def cone(cx, cy, z, r, h, n=6):
    v = [(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n), z) for k in range(n)] + [(cx, cy, z + h)]
    f = [(k, (k + 1) % n, n) for k in range(n)] + [tuple(reversed(range(n)))]
    return v, f


def build_nature(d, T):
    coll = collection("Natur")
    crown, trunk, rocks = Geo(), Geo(), Geo()
    for p in d["props"]:
        z = p["z"] if p["kind"] == "tree" else T.at(p["x"], p["y"])
        if p["kind"] == "tree":
            h = max(4.0, p["h"] * 1.4)
            trunk.box(p["x"] - 0.15, p["y"] - 0.15, z, p["x"] + 0.15, p["y"] + 0.15, z + h * 0.4)
            crown.add(*cone(p["x"], p["y"], z + h * 0.3, p["r"] * 1.2, h * 0.7, 6))
        else:
            r = max(0.4, p["r"])
            c = (p["x"], p["y"], z)
            v = [(c[0] + r, c[1], c[2]), (c[0], c[1] + r, c[2]), (c[0] - r, c[1], c[2]), (c[0], c[1] - r, c[2]),
                 (c[0], c[1], c[2] + r * 0.9), (c[0], c[1], c[2] - r * 0.4)]
            rocks.add(v, [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4), (1, 0, 5), (2, 1, 5), (3, 2, 5), (0, 3, 5)])
    if trunk.v:
        add_mesh(coll, "baumstaemme", trunk.v, trunk.f, [material("Holz", (0.35, 0.25, 0.16))])
    if crown.v:
        add_mesh(coll, "baumkronen", crown.v, crown.f, [material("Laub", (0.22, 0.38, 0.18))])
    if rocks.v:
        add_mesh(coll, "felsen", rocks.v, rocks.f, [material("Felsen", (0.45, 0.43, 0.40))])


def build_markers(d, T):
    coll = collection("Marker")
    for i, s in enumerate(d["spawns"]):
        marker(coll, f"spawn_{i:02d}", s[0], s[1], T.at(s[0], s[1]))
    for i, c in enumerate(d["crates"]):
        marker(coll, f"kiste_{i:02d}", c["x"], c["y"], c["z"], 'CUBE', 0.4)
    for i, t in enumerate(d["turrets"]):
        marker(coll, f"turm_{t['kind']}_{i}", t["x"], t["y"], t["z"], 'SPHERE', 0.8)
    for i, v in enumerate(d["vehicles"]):
        marker(coll, f"fahrzeug_{i}", v["x"], v["y"], T.at(v["x"], v["y"]), 'CUBE', 1.5)
    for i, h in enumerate(d["helis"]):
        marker(coll, f"heli_{i}", h["x"], h["y"], T.at(h["x"], h["y"]), 'CUBE', 2.0)
    for i, p in enumerate(d["pads"]):
        marker(coll, f"landeplatz_{i}", p[0], p[1], T.at(p[0], p[1]), 'CIRCLE', 6.0)


def setup_view():
    try:
        sun = bpy.data.lights.new("Sonne", 'SUN')
        sun.energy = 3.5
        so = bpy.data.objects.new("Sonne", sun)
        so.rotation_euler = (0.9, 0.2, 0.6)
        bpy.context.scene.collection.objects.link(so)
        w = bpy.data.worlds.new("Himmel")
        w.color = (0.55, 0.68, 0.82)
        bpy.context.scene.world = w
    except Exception as e:
        print("[Polybash] Licht/Himmel nicht gesetzt:", e)


def main():
    with open(os.path.join(HERE, "polytown_layout.json"), encoding="utf-8") as f:
        d = json.load(f)
    clear_scene()
    T = Terrain(d["terrain"])
    build_terrain(d, T)
    build_roads(d, T)
    build_boxes(d)
    build_roofs(d)
    build_nature(d, T)
    build_markers(d, T)
    setup_view()
    n_ob = len(bpy.data.objects)
    path = os.path.join(out_dir(), "polytown_blockout.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    print(f"[Polybash] Polytown-Blockout: {n_ob} Objekte, {len(d['boxes'])} Quader, {len(d['props'])} Bäume/Felsen")
    print("[Polybash] gespeichert:", path)


if __name__ == "__main__":
    main()
