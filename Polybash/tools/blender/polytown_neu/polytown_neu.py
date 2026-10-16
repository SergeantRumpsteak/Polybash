"""Polybash - Polytown von Grund auf (Gesamtszene).

Setzt die einzelnen Schritte zusammen: Talkessel (ebenes Tal + Berge, talkessel.py) und Burg (burg.py).
Weitere Schritte (Strassen, Haeuser, Natur ...) kommen dazu, jeweils als eigenes Modul in diesem Ordner.

Start:    blender --background --python polytown_neu.py
          (optional Ausgabeordner:  ... -- /pfad/zum/ordner)
Ergebnis: ~/blender_out/polytown_neu.blend
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

import bpy  # noqa: E402
import talkessel as T  # noqa: E402
import burg as B  # noqa: E402
import umgebung as U  # noqa: E402
import stadt as S  # noqa: E402
import texturen as TX  # noqa: E402


def main():
    T.clear_scene()
    T.build_tal(loch=B.LOCH, hf=U.gelaende_hoehe)   # huegelige Wiese mit Aussparung fuer das Burggelaende (Graben)
    verts, tris, idx = T.build_berge()
    nb = B.bauen()
    nu = U.bauen()                    # Ringweg, Abzweige, Landebahn, Hangar, Tower
    ns = S.bauen()                    # Stadt im Westen, Doerfer im Norden/Sueden, Teiche
    TX.anwenden()                     # Texturen aus texturen/<ordner>/ (falls vorhanden)
    T.build_marker()
    T.setup_view()
    path = os.path.join(T.out_dir(), "polytown_neu.blend")
    bpy.ops.wm.save_as_mainfile(filepath=path)
    zmax = max(v[2] for v in verts)
    print(f"[Polybash] Polytown neu: Tal {T.TAL:.0f} x {T.TAL:.0f} m, hoechster Gipfel {zmax:.0f} m, "
          f"{len(tris)} Dreiecke Berge, {nb} Flaechen Burg, {nu} Flaechen Umgebung, {ns} Flaechen Stadt")
    print("[Polybash] gespeichert:", path)


if __name__ == "__main__":
    main()
