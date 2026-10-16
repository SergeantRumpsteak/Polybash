"""Polybash - Blender-Testskript: ein Raum mit Tuer, Fenster, Kiste und zwei Spawn-Markern.

Start (Terminal):   blender --background --python test_raum.py
Oder in Blender:    Tab "Scripting" -> Datei oeffnen -> "Run Script"

Optional Ausgabeordner:  blender --background --python test_raum.py -- /pfad/zum/ordner
Ergebnis: testraum.blend und testraum.glb (Standard: ~/blender_out)

Regeln fuer unseren Konverter (Namen im Outliner):
  col_*     massive, begehbare/blockierende Teile (Waende, Boden, Kisten)
  spawn_*   Empties: Spawnpunkte (Position = Fuesse des Spielers)
Alle Masse in Metern, Blender ist Z-oben.
"""
import os
import sys

import bpy

# --- Spielwerte (aus spiel.py): Spielerradius 0.4 m, Hoehe 1.8 m, Stufe 0.6 m
PLAYER_R, PLAYER_H, STEP_H = 0.4, 1.8, 0.6
DOOR_W = 2 * PLAYER_R + 0.4          # 1.2 m: Spieler passt mit Luft durch
DOOR_H = PLAYER_H + 0.35             # 2.15 m
WALL_T = 0.2
ROOM_W, ROOM_D, ROOM_H = 8.0, 6.0, 3.0


def out_dir():
    argv = sys.argv
    if "--" in argv and len(argv) > argv.index("--") + 1:
        d = argv[argv.index("--") + 1]
    else:
        d = os.path.join(os.path.expanduser("~"), "blender_out")
    os.makedirs(d, exist_ok=True)
    return d


def clear_scene():
    for ob in list(bpy.data.objects):
        bpy.data.objects.remove(ob, do_unlink=True)
    for me in list(bpy.data.meshes):
        bpy.data.meshes.remove(me)


_MATS = {}


def material(name, rgb):
    if name in _MATS:
        return _MATS[name]
    m = bpy.data.materials.new(name)
    m.diffuse_color = (rgb[0], rgb[1], rgb[2], 1.0)          # Ansicht im Viewport
    try:
        m.use_nodes = True                                     # fuer den glTF-Export (je nach Version schon aktiv)
    except Exception:
        pass
    try:
        bsdf = m.node_tree.nodes.get("Principled BSDF")
        if bsdf is not None:
            bsdf.inputs["Base Color"].default_value = (rgb[0], rgb[1], rgb[2], 1.0)
            bsdf.inputs["Roughness"].default_value = 0.9
    except Exception:
        pass
    _MATS[name] = m
    return m


def box(coll, name, x0, y0, z0, x1, y1, z1, mat):
    """Quader von (x0,y0,z0) bis (x1,y1,z1) als eigenes Objekt, Flaechen zeigen nach aussen."""
    assert x1 > x0 and y1 > y0 and z1 > z0, f"{name}: leerer Quader"
    v = [(x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),
         (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1)]
    f = [(0, 3, 2, 1), (4, 5, 6, 7), (0, 1, 5, 4), (1, 2, 6, 5), (2, 3, 7, 6), (3, 0, 4, 7)]
    me = bpy.data.meshes.new(name)
    me.from_pydata(v, [], f)
    me.update()
    me.materials.append(mat)
    ob = bpy.data.objects.new(name, me)
    coll.objects.link(ob)
    return ob


def marker(coll, name, x, y, z, size=0.5):
    ob = bpy.data.objects.new(name, None)
    ob.empty_display_type = 'ARROWS'
    ob.empty_display_size = size
    ob.location = (x, y, z)
    coll.objects.link(ob)
    return ob


def build():
    clear_scene()
    coll = bpy.data.collections.new("Karte")
    bpy.context.scene.collection.children.link(coll)
    stone = material("Stein", (0.55, 0.54, 0.50))
    floor_m = material("Boden", (0.40, 0.32, 0.24))
    ground_m = material("Gras", (0.30, 0.42, 0.20))
    wood = material("Holz", (0.48, 0.37, 0.25))

    W, D, H, T = ROOM_W, ROOM_D, ROOM_H, WALL_T
    box(coll, "col_gelaende", -16, -17, -0.6, W + 16, D + 17, -0.2, ground_m)
    box(coll, "col_boden", -T, -T, -0.2, W + T, D + T, 0.0, floor_m)
    box(coll, "col_decke", -T, -T, H, W + T, D + T, H + T, stone)

    # Suedwand (y=0) mit Tuer in der Mitte
    dx0, dx1 = W / 2 - DOOR_W / 2, W / 2 + DOOR_W / 2
    box(coll, "col_wand_s_links", -T, -T, 0, dx0, 0, H, stone)
    box(coll, "col_wand_s_rechts", dx1, -T, 0, W + T, 0, H, stone)
    box(coll, "col_wand_s_sturz", dx0, -T, DOOR_H, dx1, 0, H, stone)

    # Nordwand (y=D) mit Fenster: Brustung 1.0 m, Oberkante 2.0 m
    wx0, wx1, wz0, wz1 = 3.0, 5.0, 1.0, 2.0
    box(coll, "col_wand_n_links", -T, D, 0, wx0, D + T, H, stone)
    box(coll, "col_wand_n_rechts", wx1, D, 0, W + T, D + T, H, stone)
    box(coll, "col_wand_n_brustung", wx0, D, 0, wx1, D + T, wz0, stone)
    box(coll, "col_wand_n_sturz", wx0, D, wz1, wx1, D + T, H, stone)

    # West- und Ostwand
    box(coll, "col_wand_w", -T, 0, 0, 0, D, H, stone)
    box(coll, "col_wand_o", W, 0, 0, W + T, D, H, stone)

    # Kiste (Deckung) und eine Stufe, nicht hoeher als STEP_H
    box(coll, "col_kiste", 5.5, 3.5, 0.0, 6.5, 4.5, 1.0, wood)
    box(coll, "col_stufe", 1.0, 4.5, 0.0, 2.5, 5.8, STEP_H, wood)

    marker(coll, "spawn_a", 1.0, 1.0, 0.0)
    marker(coll, "spawn_b", W - 1.0, D - 1.0, 0.0)

    # Sonne nur zur Ansicht in Blender (das Spiel hat eigenes Licht)
    sun = bpy.data.lights.new("Sonne", 'SUN')
    sun.energy = 3.0
    so = bpy.data.objects.new("Sonne", sun)
    so.rotation_euler = (0.9, 0.2, 0.6)
    coll.objects.link(so)
    return coll


def report(coll):
    n = 0
    lo = [1e9] * 3
    hi = [-1e9] * 3
    for ob in coll.objects:
        if ob.type != 'MESH':
            continue
        n += 1
        for c in ob.data.vertices:
            for i in range(3):
                lo[i] = min(lo[i], c.co[i])
                hi[i] = max(hi[i], c.co[i])
    print(f"[Polybash] {n} Quader, Ausdehnung x {lo[0]:.1f}..{hi[0]:.1f}  y {lo[1]:.1f}..{hi[1]:.1f}  z {lo[2]:.1f}..{hi[2]:.1f}")
    print(f"[Polybash] Tuer {DOOR_W:.2f} x {DOOR_H:.2f} m (Spieler {2 * PLAYER_R:.2f} x {PLAYER_H:.2f} m)")


def export(folder):
    blend = os.path.join(folder, "testraum.blend")
    glb = os.path.join(folder, "testraum.glb")
    bpy.ops.wm.save_as_mainfile(filepath=blend)
    print("[Polybash] gespeichert:", blend)
    try:
        bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB', export_apply=True)
    except TypeError:                                          # andere Parameternamen in anderer Version
        bpy.ops.export_scene.gltf(filepath=glb, export_format='GLB')
    print("[Polybash] exportiert:", glb)


if __name__ == "__main__":
    c = build()
    report(c)
    export(out_dir())
