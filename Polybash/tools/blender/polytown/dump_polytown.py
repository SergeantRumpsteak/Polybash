"""Liest die Standardkarte Polytown aus spiel.py aus (NUR LESEN, spiel.py wird nicht veraendert)
und schreibt sie als polytown_layout.json fuer das Blender-Skript.

Aufruf (im Ordner Polybash/, mit der Python-Umgebung des Spiels):
    .venv/bin/python tools/blender/polytown/dump_polytown.py
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))


def r(v, n=3):
    return round(float(v), n)


def rl(seq, n=3):
    return [r(v, n) for v in seq]


def dump(spiel_path=None, out_path=None):
    spiel_path = spiel_path or os.path.join(ROOT, "spiel.py")
    out_path = out_path or os.path.join(HERE, "polytown_layout.json")
    spec = importlib.util.spec_from_file_location("spiel_read", spiel_path)
    sp = importlib.util.module_from_spec(spec)
    sys.modules["spiel_read"] = sp
    spec.loader.exec_module(sp)
    w = sp.World(sp.SEED, spawn_mobs=False)            # Standardkarte, ohne Monster
    size, step = float(sp.WORLD), 2.0
    n = int(round(size / step)) + 1
    z = [r(w.surface_height(min(size, i * step), min(size, j * step)), 2) for j in range(n) for i in range(n)]
    out = {
        "world": size, "center": float(sp.CENTER), "terrain": {"n": n, "step": step, "z": z},
        "boxes": [rl([b.x0, b.y0, b.x1, b.y1, b.z0, b.z1]) + [rl(b.col, 2), 1 if b.vis else 0] for b in w.boxes],
        "roads": [rl(t[:5]) + [t[5]] for t in w.roads],
        "floors": [rl(f[:4]) + [rl(f[4], 2)] for f in w.floors],
        "decor": [rl(d[:6]) + [rl(d[6], 2), 1 if d[7] else 0] for d in w.decor],
        "ponds": [{"x": r(x), "y": r(y), "r": r(rr), "water": r(w.surface_height(x + rr * 1.05, y), 2)} for x, y, rr in w.ponds],
        "moats": [rl(m) for m in w.moats],
        "dams": [rl(d) for d in w.dams],
        "tunnels": [rl(t) for t in w.tunnels],
        "voids": [rl(v) for v in w.voids],
        "pads": [rl(p) for p in w.pads],
        "runway": rl(w.runway),
        "spawns": [rl(s) for s in w.spawns],
        "props": [{"kind": p.kind, "x": r(p.x), "y": r(p.y), "r": r(p.r), "z": r(p.z), "tk": getattr(p, "tk", None),
                   "h": r(getattr(p, "hit_h", 0.0))} for p in w.props if p.kind in ("tree", "rock")],
        "crates": [{"x": r(c.x), "y": r(c.y), "z": r(c.z)} for c in w.crates],
        "turrets": [{"kind": t.kind, "x": r(t.x), "y": r(t.y), "z": r(getattr(t, "z", 0.0))} for t in w.turrets],
        "vehicles": [{"x": r(v.x), "y": r(v.y)} for v in w.vehicles],
        "helis": [{"x": r(h.x), "y": r(h.y)} for h in w.helis],
        "vis": json.loads(json.dumps(w.vis, default=list)),
    }
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(out, f, separators=(",", ":"))
    print(f"geschrieben: {out_path}  ({len(out['boxes'])} Quader, {len(out['vis'])} Objekte, Terrain {n}x{n})")


if __name__ == "__main__":
    dump()
