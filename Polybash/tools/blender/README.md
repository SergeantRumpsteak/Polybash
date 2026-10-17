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

### Huegel und Senken (polytown_neu/umgebung.py: gelaende_hoehe)
- Das Tal ist nicht mehr eben: weiche Huegel (bis ca. 11 m) und flache Senken (bis ca. -5 m), grosse Wellen (~110 m), kleinere Kuppen (~55 m) und feine Bodenwellen. Die Wiese (`wiese`) hat ein 5-m-Raster und folgt der Hoehenfunktion `gelaende_hoehe(x, y)`.
- Eben bleiben: Burggelaende (Quadrat 42 m um die Mitte), das ganze Flughafengelaende (x >= 205, y 52..248, mit Zaun) und der Talrand (dort schliessen die Berge bei z = 0 an). Zwischen ebenen Flaechen und Huegeln gibt es weiche Uebergaenge.
- Entlang der Wege (Ring, Zufahrten, Abzweige) werden die Huegel stark abgeschwaecht, es bleiben nur kleine Bodenwellen (Ring: etwa -0,3 .. +0,5 m, hoechstens ca. 7 % Steigung). Alle Wege folgen dem Gelaende (je 3 m ein Querschnitt).
- Der Ringweg ist nicht mehr kreisrund: sein Mittelradius schwankt natuerlich zwischen 52 und 57,5 m (`ring_r(a)`, nach innen nie, dort liegt der Graben). Zufahrten, Abzweige und Zubringer docken an der echten Ringlinie an. Der Haupteingang des Flugplatzes liegt deshalb bei x = 217.
- Texturen koennen die Form spaeter nur zusaetzlich verfeinern; die Abweichung vom Kreis steckt in der Geometrie.

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

### Flughafen: Rundungen, Tankstelle, Helipad
- Der Asphalt um die Landebahn (Zufahrtsstrasse x=226 + Rollweg x=272) ist eine geschlossene Schleife mit Kurvenradius 12 m (`rund`/`pfad`), keine rechten Winkel.
- Der gelbe Rollweg-Mittelstrich beginnt am ersten und endet am letzten Anschluss und biegt in einem Bogen (Radius 4,5 m, `gelb_bogen`) in die Haltelinien ein; er endet am aeusseren (durchgezogenen) Strich. Auch die Zufahrten zu den Hallen und zur Tankstelle zweigen in Boegen ab.
- Tankstelle (asphaltiert, ohne Dach) am Ostzaun neben den Hangars, auf der Seite ohne Tower: Abstellposition 13,6 x 13,6 m fuer ein Kleinflugzeug (~11 m Spannweite) mit gelber Zufahrtslinie, Haltebalken und Verzurrringen, 2 Zapfsaeulen am Rand, Shop, 2 Tanks; Helipad (Radius 8 m, H) auf der Wiese neben dem Tower, per Weg an die Strasse angebunden.

### Stadt (polytown_neu/stadt.py)
- Stadt im Westen: Marktplatz 30 x 30 m mit Brunnen und 6 Staenden, Rathaus mit Uhrturm (Nord), Gasthaus (Sued), 4 Laeden; runde Marktring-Strasse; Hauptstrasse zum Ringweg. Zwei Spangen zu Nord-/Suedstrasse; im Norden ein Dorf mit Kreisverkehr, Dorfbrunnen, Scheune, im Sueden (statt des frueheren zweiten Kreisverkehrs) der Bahnhof, im Suedwesten der Steinbruch (siehe unten).
- 4 Teiche (`umgebung.TEICHE`, Mulden im Gelaende, Wasserflaechen `Teichwasser`), flache Bauzonen (`umgebung.STADT_ZONEN`).
- Jedes Haus hat einen Pfad zur Strasse (Test: Strassennetz zusammenhaengend, keine Ueberlappungen, nur auf ebenem Grund). Noch ohne Texturen.

### Wohnhaeuser (stadt.py: haus)
- 10 Haustypen, abwechselnd gesetzt: Dachformen Satteldach (Traufe oder Giebel zur Strasse), Walmdach, Mansarddach, Pultdach; Putz in 6 Farben, Klinker, sichtbares Fachwerk (Schwelle, Geschossbalken, Staender, Streben, um Fenster/Tuer ausgespart).
- Heruntergekommener 40er-Look (`verfall` 0..2): verwitterte Farben (`... alt`), Schmutzband am Sockel, abgeplatzter Putz mit Ziegel, Regenstreifen, Dachpappe- und Moosflicken, kaputte/zugenagelte Fenster, fehlende oder schief haengende Fensterlaeden, abgebrochene Kamine. Zufall je Haus ueber `seed`, daher reproduzierbar.
- Stil 1940er: Putzfassade (6 Farben) mit Sockel, Sprossenfenster mit Bank und Fensterlaeden, Haustuer mit Freitreppe und Vordach, Steildach mit Traufbrett, Gauben, Giebelfenster, Kamin, Fallrohr.
- 4 von 6 Haustypen mit begehbarem Obergeschoss (Flur mit Treppe, 15 Stufen, Treppenloch mit Gelaender, 2-3 Zimmer je Etage, Innentueren); 2 Typen eingeschossig, ebenfalls betretbar. Tuer offen, Fenster geschlossen.
- Jedes Haus steht mit der Tuer genau auf der Pfadachse zur Strasse; Spiegelung (`spiegel`) fuer Abwechslung.
- Test (Mock): Begehbarkeit per Raster-Suche (Koerper 1,8 m, Stufen <= 0,31 m): Flur, alle Zimmer, Treppe und Obergeschoss erreichbar, keine Absturzkanten, Dach nicht begehbar.
- Eingaenge (`eingang`): sieben Arten statt eines einheitlichen Vordachs - Vordach, Vordach mit Giebel, Windfang (Vorbau), Veranda, Portal mit Pilastern, schlichte Tuer, Rundbogentuer; je Haustyp festgelegt, Pfad endet vor der jeweiligen Tuer.

### Oeffentliche Gebaeude (polytown_neu/oeffentlich.py)
Sie ersetzen einzelne Wohnhaeuser (`stadt.setze_spezial`), gleiche Tuerseite und Strassenanbindung, alle im verwitterten 40er-Stil und betretbar:
- **Feuerwehr** (40 x 8,4 m, ersetzt die drei roten Klinkerhaeuser westlich des Rathauses): Halle mit drei Fluegeltoren (aufgeschwenkt), Aufschrift FEUERWEHR, Spinde, Werkbank, Schlauchregal, Leiter; Wachturm mit offener Feuerwehrtreppe (rechteckige Spirale um den Schacht, Blechbruestung wie im Flughafen-Tower) bis zum Wachraum, von dort Tuer auf die umlaufende Plattform (Gelaender, Stuetzbleche; Westseite grenzt ans Hallendach), Walmdach, Sirene; gepflasterter Vorplatz bis zur Strasse.
- **Supermarkt** (Konsum, 12 x 9 m): Schaufenster, gestreifte Markise, Schriftzug, Regale, Kasse, Kuehltruhe, Lieferanten- und Seitentuer, Flachdach mit Attika.
- **Post** (11 x 9 m, zwei Geschosse): Portal mit Schild POST, Posthorn, gelber Briefkasten, Schalterhalle mit drei Schaltern, Dienstraum mit Paketregal, Walmdach.
- **Kirche** (10,6 x 26 m): Turm mit Uhr, Schallluken und Spitzhelm samt Kreuz, Portal mit Vorhalle, Schiff mit Spitzbogen-Buntglasfenstern und Strebepfeilern, Chor mit Dreifachlanzette; innen Kirchenbaenke, Mittelgang, Chorstufen, Altar, Kanzel, Taufstein (Turm oben geschlossen).
- Tests (Mock, kein echtes Blender): Raster-Begehbarkeit je Gebaeude (Eingang bis Innenraeume, Turmtreppe der Feuerwehr, keine Absturzkanten), Stadt-Layout (Pfade, keine Ueberlappung mit Strassen, Zentrum, Haeusern, Teichen, Baeumen).

### Steinbruch und Bahnhof (polytown_neu/steinbruch.py, bahn.py)
Norden ist +y (Blickrichtung beim Betreten der Kirche), der Steinbruch liegt also in der Suedwestecke. Der suedliche Kreisverkehr samt Dorf ist entfallen: die Suedstrasse endet jetzt am Bahnhofsvorplatz (150, 62).
- **Talsenke** (45 x 40 m Loch in der Wiese, bis 9 m tief): kein rechteckiger Einbruch mehr, sondern eine natuerliche Mulde mit unregelmaessigem Umriss (Winkelrauschen), ebener Sohle bei -9 m, Hang mit Felsbaendern, aus einem Netz leicht verschobener Dreiecke (~1600 Facetten, Material nach Neigung und Hoehe: Schotter, Erde, drei Felstoene) plus rund 100 eckige Felsbrocken und neun grosse Felsnasen. Komplett begehbar (Hang <= ~0,3 m pro 0,1 m), deshalb ohne Zaeune. Die Grube (Loch 50 x 50 m) hat eine zweispurige **Schotterstrasse** (7 m, Spirale an der Wand, Gefaelle ca. 12 %, Fahrspuren und Randsteine) vom Hof im Osten bis auf die Sohle; sie ist als ebene Trasse in den Hang geschnitten (`strasse_linie`, `strasse_abstand`). Bagger, Kipper und Haufwerk auf der Sohle.
- **Schraegaufzug** (Kuebelbahn) von der Aufgabestelle in der Grube zum **Brecherturm** (Stahlgeruest mit Wellblech, Schwungrad, Rutsche, Leiter) und der **Verladebunker** aus Beton ueber dem Gleis (Durchfahrt 4,4 m, Trichter, Auslaufschuss ueber den Wagen).
- **Werkstatt** (16 x 10 m, Backstein mit Wellblechdach und Lichtband, begehbar): Schiebetor und Mannschaftstuer, Werkbank mit Schraubstoecken, Drehbank, Standbohrmaschine, Schmiede mit Esse, Laufkran, Buero mit Schreibtisch, Ofen und Aktenschrank. Dazu Sprengstoffhaeuschen (ACHTUNG, begehbar), Waechterhaus am Tor, Tor mit Schriftzug, Dieseltank, Fassstapel, Steinstapel, Schotterhaufen, Holzstapel, Lampen. Schotterhof zwischen Grube, Gleis und Werkstatt.
- **Gleise** (`bahn.gleise`): Gleis 3 (y = 27) vom Prellbock im Steinbruch unter dem Bunker hindurch, am Bahnhof vorbei und weiter nach Osten ueber den Talrand in einen Gelaendeeinschnitt (`talkessel.hoehe`) bis zum Tunnelportal bei x = 352 (`tunnel.py`, ausserhalb der Spielflaeche; Felsblock aus 2-m-Saeulen, gemauerter Tunnel, dunkle Abschlusswand), Gleis 2 und 1 zweigen ueber Weichenstrassen (S-Kurven bei x = 100 und 112) ab; Schotterbett, Schwellen alle 0,7 m, Schienen, Prellboecke, Formsignale, Bahnuebergang der Gueterstrasse mit Andreaskreuzen. Rollmaterial: beladene Muldenwagen unter dem Bunker, Dampflok mit Tender und zwei Personenwagen am Bahnsteig.
- **Bahnhof** (Mitte 150/47,5): Empfangsgebaeude 24 x 9 m (Schalterhalle mit Giebel, Uhr und Schriftzug BAHNHOF, Wartesaal, Gepaeck-/Vorsteherraum, begehbar), Hausbahnsteig (36 m, 0,28 m hoch) mit Dach, Namensschildern POLYTOWN, Baenken und Lampen; **Stellwerk** am Westende des Bahnsteigs (innen Treppe, oben verglaster Raum mit Hebelbank); **Gueterschuppen** am Gleis 3 mit Laderampe und Hintertuer; **Wasserturm** und Wasserkran am Ostende; gepflasterter Vorplatz mit Beeten, Baenken, Laternen, Fahrradstaendern und Telefonzelle.
- Strassen: Werkstrasse (Spange Sued -> Steinbruchtor), Gueterstrasse (Hof -> Bahnuebergang -> Gueterschuppen). Neue Bauzonen in `umgebung.STADT_ZONEN` (Steinbruch, Gleiskorridor); `polytown_neu.py` uebergibt `[B.LOCH, SB.PIT]` als Loecher an `build_tal`.
- Tests (Mock, kein echtes Blender): Raster-Begehbarkeit (Vorplatz -> Halle -> Bahnsteig -> Stellwerk-Obergeschoss, Schuppen von Strasse und Gleisseite, Werkstatt, Waechter-/Sprengstoffhaus, Grube von der Rampe bis zur Sohle) ohne unbewehrte Absturzkanten; Layout (nur in ebenen Zonen, nicht auf Strassen/Haeusern/Teichen/Baeumen, Strassen angeschlossen, Gleise vom Bunker bis hinter den Bahnsteig, keine Ueberschneidungen zwischen den Modulen).

### Rustikales Rathaus und Gasthaus, Huegel (polytown_neu/rustik.py, umgebung.py)
- **Beschriftungen** gibt es nur noch an der Post (sowie Tor und Bahnsteigtafel).
- `rustik.py`: Rathaus (22 x 12 m, Bruchsteinerdgeschoss, ueberkragendes Fachwerk-Obergeschoss, steiles Ziegeldach aus einzeln gesetzten, verschieden verwitterten Reihen mit Fehlstellen, Gauben, schiefe Kamine, Erker, Uhrturm mit Holz-Glockenstube und Kupferhelm, Rundbogenportal) und Gasthaus (18 x 10 m, Putz auf Bruchsteinsockel, Fachwerk, Vordach, Ausleger, Biertische). Abgeplatzter Putz, Risse, Moos, schiefe Laeden.
- Huegel: groessere Huegel und markante Kuppen (`umgebung.KUPPEN`), schmalere Auslaeufer der ebenen Zonen; wegen der vielen Bauzonen liegen die Huegel vor allem im Norden und in den Randstreifen.
- **Alle zivilen Gebaeude im Rathaus-Detailgrad** (`polytown_neu/altbau.py`, greift ueber `stadt.dach/satteldach/aussenwand/fensterschmuck` in Wohnhaeuser, Laeden, Post, Kirche, Feuerwehr, Supermarkt, Bahnhof usw.): jede Dachflaeche mit einzeln gesetzten, verschieden verwitterten Ziegeln/Schieferstuecken (Fehlstellen, Moos), Sparrenkoepfe unter der Traufe, Bruchsteinsockel aus Quadern, Fenstersturz mit Schlussstein und Gewaende, abgeplatzter Putz mit Regenstreifen, unregelmaessige Kamine, Deckleisten an Scheunen. Feine Reliefs sind nicht als Hindernis registriert (`altbau.Deko`), damit sie nicht begehbar sind.

### Bauernhof, Wald, Burgruine (polytown_neu/bauernhof.py, wald.py, ruine.py)
- **Dachziegel**: `altbau.POOLS` kennt jetzt auch rote/braune/orange/ockerfarbene/schwarze Ziegelmischungen; jedes Haus bekommt drei vorherrschende Toene plus Flickstellen, so wie beim Rathaus.
- **Steinbruch**: die Grube reicht weiter nach Sueden (`steinbruch.PIT`, `SENKE_R`).
- **Bauernhof** (x 34..64, y 64..93, zwischen Steinbruch und Ort): Fachwerk-Wohnhaus (begehbar), grosse Scheune mit Heuboden (Treppe, Gelaender), Stall, Silo, Brunnen, Zaeune, Heuballen, Obstbaeume; Schotterzufahrt zur Werkstrasse. Alle Hallen sind innen begehbar (`bauernhof.halle`).
- **Wald an der Bahn** (`wald.py`): dichter Misch-/Nadelwald beiderseits der Strecke suedlich des Flugplatzes (x 197..293). Gleiskorridor eben (`STADT_ZONEN`, y 22..32, Abfall 12 m), daneben Huegel (`KUPPEN`). Baeume stehen auf der echten Wiesenhoehe; nur der Stamm ist Hindernis, die Kronen beginnen ueber Kopfhoehe -> man laeuft zwischen den Staemmen durch.
- **Burgruine** (`ruine.py`) auf dem Burgberg nordlich der Kirche (`umgebung.RUINE`, Gipfel eben bei z = 16 m, Radius 14 m). Rustikal und verfallen: Bruchsteinmauern mit abgebrochenen Kronen, Fensterpfeiler ohne Sturz, Torruine mit halbem Spitzbogen, Bergfried-Stumpf, Palas mit Staffelgiebel und Kamin, Grundmauern, Brunnen, Schutt, Efeu und Moos; Karrenweg ab der Spange Nord. Begehbar: Treppe zum Wehrgang der Suedmauer (3,9 m) bis zur Eckbastion, Treppen im Bergfried bis zur Krone (6,7 m), Treppe zur Nordmauerkrone (2,8 m), Schutthalde an der Ostmauer, niedrige Quader zum Draufsteigen. Feine Reliefs (Quader, Efeu, lose Steine) sind keine Hindernisse. Der Teich im Nordwesten liegt jetzt bei (16, 236).
- Tests sind reine Mock-Tests (ohne echtes Blender): Geometrie und Begehbarkeit (Stufen <= 0,31 m, Koerper 1,8 m) werden in Python geprueft.
