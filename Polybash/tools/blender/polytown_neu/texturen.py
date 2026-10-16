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

# Material -> {ordner: Unterordner in texturen/, kachel_m: Meter je Wiederholung, tint: 0..1 (Einfaerbung mit der Materialfarbe),
#            variation: 0..1 (Anti-Kachelung: zweite gedrehte Abtastung + grosse Helligkeitsflecken; 0 = aus)}
TEXTUREN = {
    # Boden: Hofpflaster und Stufen
    "Hof":              {"ordner": "festung_boden", "kachel_m": 2.0, "tint": 0.0, "variation": 0.0},
    # Feuerwehrtreppe: Trittbleche, Wangen, Podest (Metall) und Stuetzsaeulen
    "Stufen":           {"ordner": "festung_treppe", "kachel_m": 1.0, "tint": 0.0, "variation": 0.0},
    "Treppensaeule":    {"ordner": "festung_treppe", "kachel_m": 1.0, "tint": 0.0, "variation": 0.0},   # eigener Ordner festung_treppenseule moeglich
    # Waende: Mauern, Tuerme, Wachhaeuser, Kasematten, Deckungen
    "Mauerwerk":        {"ordner": "festung_wand", "kachel_m": 2.0, "tint": 0.0, "variation": 0.0},
    "Mauerwerk dunkel": {"ordner": "festung_wand", "kachel_m": 2.0, "tint": 0.6, "variation": 0.0},
}
ENDUNGEN = {"jpg", "jpeg", "png", "exr", "tif", "tiff", "webp"}


def finde_karten(dateien):
    """Ordnet Dateinamen (Poly-Haven-Schema <name>_<art>[_gl|_dx]_<aufloesung>.<endung>) den Kartenarten zu.

    Die Art ist das Wort direkt vor der Aufloesung (2k) bzw. vor gl/dx - der Namensteil davor (z. B. "metal_plate") zaehlt nicht.
    Rueckgabe: (dict mit farbe, rauheit, normal, ao, arm, metall - nur gefundene; Pfade unveraendert, Liste mit Hinweisen)."""
    out, hinweis = {}, []
    for pfad in sorted(dateien):
        name = os.path.basename(pfad).lower()
        stamm, _, ende = name.rpartition(".")
        if ende not in ENDUNGEN:
            continue
        toks = [x for x in re.split(r"[^a-z0-9]+", stamm) if x]
        r = next((k for k in range(len(toks) - 1, 0, -1) if re.fullmatch(r"\d+k", toks[k])), len(toks))
        art = toks[:r]
        fmt = None
        if art and art[-1] in ("gl", "dx"):
            fmt = art.pop()
        kind = art[-1] if art else ""
        if kind in ("nor", "normal"):
            if fmt == "dx":
                hinweis.append("DirectX-Normal-Map ignoriert (bitte 'nor_gl' / OpenGL laden): " + os.path.basename(pfad))
            else:
                out.setdefault("normal", pfad)
        elif kind in ("diff", "col", "color", "albedo", "basecolor"):
            out.setdefault("farbe", pfad)
        elif kind in ("rough", "roughness"):
            out.setdefault("rauheit", pfad)
        elif kind in ("ao", "occlusion"):
            out.setdefault("ao", pfad)
        elif kind == "arm":
            out.setdefault("arm", pfad)
        elif kind in ("metal", "metallic"):
            out.setdefault("metall", pfad)
        # disp/height/spec u. a. werden nicht benutzt
    return out, hinweis


def alle_dateien(ordner):
    res = []
    for wurzel, _d, fs in os.walk(ordner):
        res += [os.path.join(wurzel, f) for f in fs]
    return res


def _tex(nodes, links, mp, pfad, farbraum, x, y, var=None):
    """Bildknoten; Rueckgabe: Ausgang 'Color'. Mit var = (mapping2, maske) wird die Textur ein zweites Mal in anderem Massstab
    und gedreht abgetastet und per Maske mit der ersten gemischt (Anti-Kachelung)."""
    n = nodes.new("ShaderNodeTexImage")
    n.location = (x, y)
    n.image = bpy.data.images.load(pfad, check_existing=True)
    n.image.colorspace_settings.name = farbraum
    try:
        n.image.pack()                       # Bild in die .blend einbetten
    except Exception:
        pass
    links.new(mp.outputs["Vector"], n.inputs["Vector"])
    if var is None:
        return n.outputs["Color"]
    mp2, maske = var
    n2 = nodes.new("ShaderNodeTexImage")
    n2.location = (x, y - 120)
    n2.image = n.image
    links.new(mp2.outputs["Vector"], n2.inputs["Vector"])
    m = nodes.new("ShaderNodeMix")
    m.data_type = 'RGBA'
    m.blend_type = 'MIX'
    m.location = (x + 280, y)
    links.new(maske, m.inputs[0])
    links.new(n.outputs["Color"], m.inputs[6])
    links.new(n2.outputs["Color"], m.inputs[7])
    return m.outputs[2]


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


def _variation(nodes, links, uv, k, stark):
    """Baut die Knoten gegen sichtbare Wiederholung. Rueckgabe: (var, macro).
    var   = (zweites Mapping, Maske): zweite Abtastung der Textur (anderer Massstab, gedreht), per Noise-Maske verblendet.
    macro = grosse weiche Helligkeitsflecken (+-35 % * stark), werden mit der Farbe multipliziert."""
    mp2 = nodes.new("ShaderNodeMapping")
    mp2.location = (-900, -400)
    mp2.inputs["Scale"].default_value = (k * 0.43, k * 0.43, k * 0.43)
    mp2.inputs["Rotation"].default_value = (0.0, 0.0, 0.61)
    mp2.inputs["Location"].default_value = (0.37, 0.19, 0.0)
    links.new(uv.outputs["UV"], mp2.inputs["Vector"])
    n1 = nodes.new("ShaderNodeTexNoise")
    n1.location = (-900, -700)
    n1.inputs["Scale"].default_value = 0.35            # Flecken von ca. 3 m (UV in Metern)
    n1.inputs["Detail"].default_value = 2.0
    links.new(uv.outputs["UV"], n1.inputs["Vector"])
    r1 = nodes.new("ShaderNodeMapRange")
    r1.location = (-700, -700)
    r1.inputs["From Min"].default_value = 0.40
    r1.inputs["From Max"].default_value = 0.60
    links.new(n1.outputs["Fac"], r1.inputs["Value"])
    n2 = nodes.new("ShaderNodeTexNoise")
    n2.location = (-900, -1000)
    n2.inputs["Scale"].default_value = 0.11            # grosse Flecken von ca. 9 m
    n2.inputs["Detail"].default_value = 3.0
    links.new(uv.outputs["UV"], n2.inputs["Vector"])
    r2 = nodes.new("ShaderNodeMapRange")
    r2.location = (-700, -1000)
    r2.inputs["From Min"].default_value = 0.30
    r2.inputs["From Max"].default_value = 0.70
    r2.inputs["To Min"].default_value = 1.0 - 0.35 * stark
    r2.inputs["To Max"].default_value = 1.0 + 0.35 * stark
    links.new(n2.outputs["Fac"], r2.inputs["Value"])
    return (mp2, r1.outputs["Result"]), r2.outputs["Result"]


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
    var, macro = None, None
    stark = float(cfg.get("variation", 0.0))
    if stark > 0.0:
        try:
            var, macro = _variation(nodes, links, uv, k, stark)
            benutzt.append("Anti-Kachelung %.2f" % stark)
        except Exception as e:
            print("[Polybash] Anti-Kachelung nicht angewendet (%s): %s" % (mat.name, e))
            var, macro = None, None
    if "farbe" in karten:
        farbe = _tex(nodes, links, mp, karten["farbe"], "sRGB", -600, 300, var)
        benutzt.append("Farbe")
    if "ao" in karten:
        ao = _tex(nodes, links, mp, karten["ao"], "Non-Color", -600, 0, var)
        benutzt.append("AO")
    if "rauheit" in karten:
        rau = _tex(nodes, links, mp, karten["rauheit"], "Non-Color", -600, -300, var)
        benutzt.append("Rauheit")
    if "arm" in karten and (ao is None or rau is None):
        try:
            arm = _tex(nodes, links, mp, karten["arm"], "Non-Color", -600, -600, var)
            sp = nodes.new("ShaderNodeSeparateColor")
            sp.location = (-350, -600)
            links.new(arm, sp.inputs["Color"])
            if ao is None:
                ao = sp.outputs["Red"]
            if rau is None:
                rau = sp.outputs["Green"]
            benutzt.append("ARM")
        except Exception as e:
            print("[Polybash] ARM-Karte nicht benutzt:", e)
    if "metall" in karten:
        try:
            met = _tex(nodes, links, mp, karten["metall"], "Non-Color", -600, -1200, var)
            links.new(met, bsdf.inputs["Metallic"])
            benutzt.append("Metall")
        except Exception as e:
            print("[Polybash] Metall-Karte nicht benutzt:", e)
    if farbe is not None:
        try:
            if ao is not None:
                farbe = _mult(nodes, links, farbe, ao, 1.0, -250, 300)
            if cfg.get("tint", 0.0) > 0.0:
                farbe = _mult(nodes, links, farbe, tuple(mat.diffuse_color[:3]), cfg["tint"], -50, 300)
        except Exception as e:
            print("[Polybash] Mischknoten nicht benutzt (%s): %s" % (mat.name, e))
        if macro is not None:
            try:
                farbe = _mult(nodes, links, farbe, macro, 1.0, 150, 300)
            except Exception as e:
                print("[Polybash] Farbflecken nicht angewendet (%s): %s" % (mat.name, e))
        links.new(farbe, bsdf.inputs["Base Color"])
    if rau is not None:
        links.new(rau, bsdf.inputs["Roughness"])
    if "normal" in karten:
        nrm = _tex(nodes, links, mp, karten["normal"], "Non-Color", -600, -900)      # Normal nicht mischen (gedrehte Tangenten)
        nm = nodes.new("ShaderNodeNormalMap")
        nm.location = (-250, -900)
        links.new(nrm, nm.inputs["Color"])
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
