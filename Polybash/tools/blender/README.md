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

## Burg (Polytown von Grund auf, Schritt 2) - Gesamtszene
Tal, Berge und die Burg (Radarstation) in der Mitte, nachgebaut nach der Burg der Standardkarte (spiel.py bleibt unveraendert):

    ./build_blender.sh

(ohne Argument startet das Skript `tools/blender/polytown_neu/polytown_neu.py`; neue Schritte kommen als weitere Module hinzu,
die dieses Skript einbindet - der Befehl bleibt immer gleich.)

Ergebnis: `~/blender_out/polytown_neu.blend` (nur das Tal ohne Burg: weiter `talkessel.py`).

* Burg: Mauern 44 x 44 m mit Wehrgang, Bruestung und Stacheldraht; vier Ecktuerme (Flak auf NW und SO, Freya-Antennen auf SW und NO);
  zwei Tore (Nord, Sued) mit Wachhaeusern, Warnstreifen und hochgeklappten Schranken; Bergfried mit Radarschuessel;
  Kasematten, Deckungen, Loeschwasserbehaelter, Lampen, Fahnen.
* Graben um die Burg (2 m tief, Wasserspiegel -1,2 m, geschlossener Ring) mit Nordbruecke (Stahlfachwerk) und Suedbruecke (Beton) vor den beiden Toren; West- und Ostmauer haben keinen Eingang.
  Abweichung vom Spiel: die Bruecken Nord/Sued spannen ueber offenes Wasser (im Spiel liegt dort Boden unter den Bruecken).
* Collections: `Burg` (Objekte `burg_mauern`, `burg_ecktuerme`, `burg_tore`, `burg_bergfried`, `burg_hof`, `burg_bruecken`,
  `burg_radar_flak`, `burg_gelaende`, `burggraben_wasser`) und `Burg-Marker` (`flak_nw`, `flak_so`, `kiste_burg_*`, `koth_zone`, Kameras).
* Die Positionen von Flak und Kisten stimmen mit der Standardkarte ueberein (128/172 und 172/128, z = 9,35).


### Drehbare Teile und Texturen (polytown_neu)
- Radarschüssel, Freya-Antennen und Flakrohre sind eigene Objekte (`radar_schuessel`, `freya_sw/no`, `flak_nw/so`) mit Drehpunkt als Objekt-Ursprung. Im Blender-Modell sind sie statisch (Animation gibt es nur im Spiel); zum Ansehen: Objekt wählen, `R` `Z` drehen. Die Platzhalter-Empties heißen `marker_flak_nw/so`.
- Steintexturen: Poly-Haven-Satz (Diffuse, Normal **GL**, Roughness, optional AO) in `tools/blender/polytown_neu/texturen/stein_mauer/` legen, `./build_blender.sh` ausführen. Details in `texturen/README.txt`; Kachelgröße (Standard 2 m) in `texturen.py` (`TEXTUREN`).
