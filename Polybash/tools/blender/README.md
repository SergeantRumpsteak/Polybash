# Blender-Werkzeuge (Karten-Design)

Arbeitet abgegrenzt vom Spiel: `spiel.py` wird hier nicht angefasst.

## Polytown-Blockout
1. `git pull`
2. `cd tools/blender/polytown && blender --background --python polytown_blockout.py`
3. Ergebnis: `~/blender_out/polytown_blockout.blend` (in Blender oeffnen)

`polytown_layout.json` enthaelt das ausgelesene Layout (Gelaende, Quader, Strassen, Haeuser, Baeume, Marker).
Neu erzeugen (nur falls sich die Standardkarte in spiel.py aendert):
`.venv/bin/python tools/blender/polytown/dump_polytown.py` im Ordner `Polybash/`.

Hinweis: Jeder Skriptlauf ueberschreibt die .blend-Datei. Handarbeit unter anderem Namen speichern.
