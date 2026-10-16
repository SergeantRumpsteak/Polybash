"""Polybash - Texturen auf Materialien legen (Poly-Haven-Sets o. ae.).

Liegt im Ordner texturen/<name>/ ein Texturensatz, bekommt das zugeordnete Material automatisch Farbe, Rauheit,
Normal-Map (OpenGL) und AO. Fehlt der Ordner, bleibt das Material einfarbig - das Skript laeuft dann trotzdem durch.

Zuordnung Material -> Ordner und Kachelgroesse (Meter pro Wiederholung der Textur) steht in TEXTUREN.
Die UVs der Burg sind in Metern angelegt (burg.uv_in_metern), die Kachelgroesse regelt hier ein Mapping-Knoten.
"""
import os
import re

import bpy

HERE = os.path.dirname(os.path.abspath(__file__))
ORDNER = os.path.join(HERE, "texturen")

# Material -> {ordner: Unterordner in texturen/, kachel_m: Meter je Wiederholung, tint: 0..1 (Einfaerbung mit der Materialfarbe)}
TEXTUREN = {
    "Mauerwerk":        {"ordner": "stein_mauer", "kachel_m": 2.0, "tint": 0.0},
    "Mauerwerk dunkel": {"ordner": "stein_mauer", "kachel_m": 2.0, "tint": 0.6},
    "Stufen":           {"ordner": "stein_mauer", "kachel_m": 2.0, "tint": 0.5},
}
ENDUNGEN = {"jpg", "jpeg", "png", "exr", "tif", "tiff", "webp"}


def finde_karten(dateien):
    """Ordnet Dateinamen (Poly-Haven-Schema, z. B. rock_wall_08_nor_gl_2k.png) den Kartenarten zu.

    Rueckgabe: dict mit den Schluesseln farbe, rauheit, normal, ao, arm (nur gefundene); Pfade unveraendert."""
    out, hinweis = {}, []
    for pfad in sorted(dateien):
        name = os.path.basename(pfad).lower()
        stamm, _, ende = name.rpartition(".")
        if ende not in ENDUNGEN:
            continue
        t = set(re.split(r"[^a-z0-9]+", stamm))
        if "disp" in t or "displacement" in t or "height" in t or "metal" in t or "metallic" in t or "spec" in t:
            continue
        if ("nor" in t or "normal" in t) and ("dx" in t):
            hinweis.append("DirectX-Normal-Map ignoriert (bitte 'nor_gl' / OpenGL laden): " + os.path.basename(pfad))
            continue
        if "nor" in t or "normal" in t:
            out.setdefault("normal", pfad)
        elif "diff" in t or "col" in t or "color" in t or "albedo" in t or "basecolor" in t:
            out.setdefault("farbe", pfad)
        elif "rough" in t or "roughness" in t:
            out.setdefault("rauheit", pfad)
        elif "ao" in t or "occlusion" in t:
            out.setdefault("ao", pfad)
        elif "arm" in t:
            out.setdefault("arm", pfad)
    return out, hinweis


def alle_dateien(ordner):
    res = []
    for wurzel, _d, fs in os.walk(ordner):
        res += [os.path.join(wurzel, f) for f in fs]
    return res


def _tex(nodes, links, mp, pfad, farbraum, x, y):
    n = nodes.new("ShaderNodeTexImage")
    n.location = (x, y)
    n.image = bpy.data.images.load(pfad, check_existing=True)
    n.image.colorspace_settings.name = farbraum
    try:
        n.image.pack()                       # Bild in die .blend einbetten
    except Exception:
        pass
    links.new(mp.outputs["Vector"], n.inputs["Vector"])
    return n


def _mult(nodes, links, a_out, b_out, fac, x, y):
    """Mischt zwei Farben multiplikativ (fac 0 = nur a, 1 = a * b)."""
    m = nodes.new("ShaderNodeMix")
    m.data_type = 'RGBA'
    m.blend_type = 'MULTIPLY'
    m.location = (x, y)
    m.inputs[0].default_value = fac
    if isinstance(b_out, tuple):
        m.inputs[7].default_value = (b_out[0], b_out[1], b_out[2], 1.0)
    else:
        links.new(b_out, m.inputs[7])
    links.new(a_out, m.inputs[6])
    return m.outputs[2]


def material_belegen(mat, cfg, karten):
    mat.use_nodes = True
    nt = mat.node_tree
    nodes, links = nt.nodes, nt.links
    bsdf = nodes.get("Principled BSDF")
    if bsdf is None:
        return []
    k = 1.0 / cfg["kachel_m"]
    uv = nodes.new("ShaderNodeTexCoord")
    uv.location = (-1100, 0)
    mp = nodes.new("ShaderNodeMapping")
    mp.location = (-900, 0)
    mp.inputs["Scale"].default_value = (k, k, k)
    links.new(uv.outputs["UV"], mp.inputs["Vector"])
    benutzt = []
    farbe = ao = rau = None
    if "farbe" in karten:
        n = _tex(nodes, links, mp, karten["farbe"], "sRGB", -600, 300)
        farbe = n.outputs["Color"]
        benutzt.append("Farbe")
    if "ao" in karten:
        ao = _tex(nodes, links, mp, karten["ao"], "Non-Color", -600, 0).outputs["Color"]
        benutzt.append("AO")
    if "rauheit" in karten:
        rau = _tex(nodes, links, mp, karten["rauheit"], "Non-Color", -600, -300).outputs["Color"]
        benutzt.append("Rauheit")
    if "arm" in karten and (ao is None or rau is None):
        n = _tex(nodes, links, mp, karten["arm"], "Non-Color", -600, -600)
        try:
            sp = nodes.new("ShaderNodeSeparateColor")
            sp.location = (-350, -600)
            links.new(n.outputs["Color"], sp.inputs["Color"])
            if ao is None:
                ao = sp.outputs["Red"]
            if rau is None:
                rau = sp.outputs["Green"]
            benutzt.append("ARM")
        except Exception as e:
            print("[Polybash] ARM-Karte nicht benutzt:", e)
    if farbe is not None:
        try:
            if ao is not None:
                farbe = _mult(nodes, links, farbe, ao, 1.0, -250, 300)
            if cfg.get("tint", 0.0) > 0.0:
                farbe = _mult(nodes, links, farbe, tuple(mat.diffuse_color[:3]), cfg["tint"], -50, 300)
        except Exception as e:
            print("[Polybash] Mischknoten nicht benutzt (%s): %s" % (mat.name, e))
        links.new(farbe, bsdf.inputs["Base Color"])
    if rau is not None:
        links.new(rau, bsdf.inputs["Roughness"])
    if "normal" in karten:
        n = _tex(nodes, links, mp, karten["normal"], "Non-Color", -600, -900)
        nm = nodes.new("ShaderNodeNormalMap")
        nm.location = (-250, -900)
        links.new(n.outputs["Color"], nm.inputs["Color"])
        links.new(nm.outputs["Normal"], bsdf.inputs["Normal"])
        benutzt.append("Normal")
    return benutzt


def anwenden():
    """Belegt alle Materialien aus TEXTUREN, deren Ordner vorhanden ist."""
    for name, cfg in TEXTUREN.items():
        mat = bpy.data.materials.get(name)
        if mat is None:
            continue
        ordner = os.path.join(ORDNER, cfg["ordner"])
        if not os.path.isdir(ordner):
            print(f"[Polybash] Textur fuer '{name}': Ordner texturen/{cfg['ordner']} nicht gefunden - bleibt einfarbig")
            continue
        karten, hinweis = finde_karten(alle_dateien(ordner))
        for h in hinweis:
            print("[Polybash]", h)
        if not karten:
            print(f"[Polybash] Textur fuer '{name}': keine passenden Dateien in texturen/{cfg['ordner']}")
            continue
        try:
            benutzt = material_belegen(mat, cfg, karten)
            print(f"[Polybash] Textur fuer '{name}' aus texturen/{cfg['ordner']}: {', '.join(benutzt)} (Kachel {cfg['kachel_m']} m)")
        except Exception as e:
            print(f"[Polybash] Textur fuer '{name}' nicht angewendet: {e}")
