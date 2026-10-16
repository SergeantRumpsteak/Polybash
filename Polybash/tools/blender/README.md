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
  zwei Tore (Nord, Sued) mit Wachhaeusern, Warnstreifen und hochgeklappten Schranken; Radarschuessel auf Betonsockel;
  Kasematten, Deckungen, Loeschwasserbehaelter, Lampen, Fahnen.
* Graben um die Burg (2 m tief, Wasserspiegel -1,2 m, geschlossener Ring) mit Nordbruecke (Stahlfachwerk) und Suedbruecke (Beton) vor den beiden Toren; West- und Ostmauer haben keinen Eingang.
  Abweichung vom Spiel: die Bruecken Nord/Sued spannen ueber offenes Wasser (im Spiel liegt dort Boden unter den Bruecken).
* Collections: `Burg` (Objekte `burg_mauern`, `burg_ecktuerme`, `burg_tore`, `burg_radarsockel`, `burg_hof`, `burg_bruecken`,
  `burg_radar_flak`, `burg_gelaende`, `burggraben_wasser`) und `Burg-Marker` (`flak_nw`, `flak_so`, `kiste_burg_*`, `koth_zone`, Kameras).
* Die Positionen von Flak und Kisten stimmen mit der Standardkarte ueberein (128/172 und 172/128, z = 9,35).


### Drehbare Teile und Texturen (polytown_neu)
- Radarschüssel, Freya-Antennen und Flakrohre sind eigene Objekte (`radar_schuessel`, `freya_sw/no`, `flak_nw/so`) mit Drehpunkt als Objekt-Ursprung. Im Blender-Modell sind sie statisch (Animation gibt es nur im Spiel); zum Ansehen: Objekt wählen, `R` `Z` drehen. Die Platzhalter-Empties heißen `marker_flak_nw/so`.
- Texturen: Poly-Haven-Satz (Diffuse, Normal **GL**, Roughness, optional AO) in `tools/blender/polytown_neu/texturen/festung_boden/` legen, `./build_blender.sh` ausführen. Details in `texturen/README.txt`; Kachelgröße (Standard 2 m) in `texturen.py` (`TEXTUREN`).

### Umgebung der Burg (polytown_neu/umgebung.py)
- Bezugskante ist die Ostkante der Karte (die Ostmauer der Burg hat keinen Ausgang). Ringweg um die Burg (Mittelradius 52 m, 8 m breit, ausserhalb des Grabens) mit Zufahrten von Nord-/Suedbruecke. Zwei gerade Abzweige (45 Grad) enden an der Flughafenstrasse (x = 226), dazu ein Zubringer nach Osten zur Bahnmitte.
- Flughafen: Landebahn Nord-Sued bei x = 256, 150 x 14 m. Westlich der Bahn die Flughafenstrasse, auf halber Bahnlaenge der Tower neben dem Zubringer, am Suedende der grosse Hangar (offen zur Bahn). Oestlich der Bahn der parallele Rollweg (drei Anschluesse an die Bahn, an den Enden ueber Umfahrungen mit der Strasse verbunden), Vorfeld und die Hangarreihe zwischen Vorfeld und Bergen.
- Hangarreihe: drei getrennte Tonnenhallen mit je eigenem Halbkreis-Dach (Radius 10,4 m = halbe Teilung von 20,8 m); die Daecher beruehren sich am Boden, wo eines endet, beginnt das naechste. 19 m tief (x = 279 .. 298, Talkante bei 300), nach Westen (zur Burg) komplett offen.
- Gelbe Taxiways: gelbe Mittellinien laufen von der Bahn ueber die drei Anschluesse, den Rollweg und das Vorfeld bis hinten in jede der drei Hallen; ausserdem von der Bahn in den grossen Hangar und von der Zufahrt im Westen auf die Bahn. Vor der Bahnkante steht an den drei Rollweganschluessen im Osten je eine Haltelinie (hold short; am Tower-Zubringer und am grossen Hangar gibt es keine - sie sind nur ueber Asphalt mit der Bahn verbunden): zur Bahn hin zwei Strichlinien, auf der Wartseite zwei Vollstriche.
- Tower (begehbar): Sockelgebaeude (12 x 10 m, Tuer im Sueden) mit dem Treppenschacht (6 x 6 m). Darin eine offene Feuerwehrtreppe (Trittbleche, Wangen, Saeulen; Blechbruestung zur Schachtseite) als rechteckige Spirale um den freien Schacht, 6 Laeufe zu je 4 Stufen und Eckpodeste, 30 Stufen a 0,44 m bis in die Kanzel (Loch im Kanzelboden mit Gelaender). Die Kanzel hat eine Tuer nach Westen auf die Rundumplattform (1,5 m breit, Gelaender mit Fussleiste). Auf dem Kanzeldach dreht sich die Radaranlage (Objekt `tower_radar`, Drehung per Treiber 6 Grad je Bild, laeuft bei Animation/Play).
- Windsaecke: je einer an den beiden Bahnenden (westlich neben der Bahn).
- Grosser Hangar (begehbar, 12 x 28 m, 28 m in Bahnrichtung): Tuer in der Westwand (von der Strasse) und das komplett offene Osttor zur Bahn; Kisten stehen in den Ecken.
- Zaun und Eingang: das Gelaende ist eingezaeunt (x = 214 .. 299, y = 60 .. 240). Haupteingang ist der Zubringer: Checkpoint mit Mittelinsel, Wachhaus, Vordach ueber beiden Fahrstreifen und je einer (offenen) rot-weissen Schranke fuer Ein- und Ausfahrt. Die beiden Abzweige vom Ring haben je ein Tor mit zwei Schrankenbaeumen.
- Markierungen (weiss): Zebrastreifen an beiden Enden, ein Touchdown-Balkenpaar je Anflugrichtung und durchgehend die Mittelstriche; sonst nichts (keine Randlinien, keine Zusatzbalken).
- Noch ohne Texturen (nur Farben). Objekte in der Collection `Umgebung`: `umgebung_wege`, `umgebung_landebahn`, `umgebung_hangar`, `umgebung_hangarreihe`, `umgebung_tower`, `tower_radar`, `umgebung_zaun`, `umgebung_windsaecke`.
- Das Haus mit der Radarschuessel ist entfernt; die Schuessel steht auf einem runden Betonsockel (`burg_radarsockel`).
