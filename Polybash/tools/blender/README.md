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

## Talkessel (Polytown von Grund auf, Schritt 1: Gelaende)
Ebenes Wiesental mit den Massen der Standardkarte (Spielflaeche 300 x 300 m, Ecke bei 0/0, Mitte bei 150/150),
ringsum alpine Berge. Strassen und Gebaeude kommen in spaeteren Schritten.

    ./build_blender.sh tools/blender/polytown_neu/talkessel.py

oder: `blender --background --python tools/blender/polytown_neu/talkessel.py` -> `~/blender_out/talkessel.blend`

* Collections: `Tal` (Objekt `wiese`, Linie `spielflaeche_rand`), `Berge` (Objekt `berge`), `Marker` (`mitte`, vier Ecken, zwei Kameras).
* Das Tal liegt exakt bei z = 0; die Berge steigen erst ausserhalb der Spielflaeche an (Gelaende ca. 700 x 700 m).
* Alle Zahlen (Talgroesse, Gebirgsbreite, Hoehe, Schneegrenze, Zufallswert `SEED`) stehen oben im Skript unter "Parameter".
* Materialien: Wiese, Alm, Wald, Alm hoch, Fels, Fels dunkel, Schnee (nach Hoehe und Neigung vergeben, Flat Shading).
* Kameras `kamera_nordwand` und `kamera_ecke` (in Blender: `Strg+Numpad0` bzw. Kamera im Outliner waehlen).
