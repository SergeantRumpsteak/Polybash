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

### Getreidefelder, Gras, Laternen, Gelaende-Feinschliff (felder.py, gras.py, laternen.py)
- **Getreidefelder** (`felder.py`, x 3..33, y 68..95, westlich vom Bauernhof): reifer Weizen, Gerste, junger Weizen und ein Stoppelfeld mit Strohballen, Feldweg vom Hof, Hecken, Vogelscheuche, Geraeteunterstand. Halme sind einzelne Spitzen mit Aehren, in Reihen mit Rauschen in Dichte und Hoehe; sie sind kein Hindernis.
- **Gras** (`gras.py`): kleine 3D-Buschel (drei Halmspitzen, 12..40 cm) als Rauschen ueber alle Grasflaechen (Flecken und Lichtungen); ausgenommen Strassen, Wege, Plaetze, Gebaeude, Hoefe, Felder, Steinbruch, Burggelaende, Flugplatz, Gleise, Teiche, Burgplateau.
- **Laternen** (`laternen.py`): Gusseisenlaternen mit leuchtendem Glas alle ~26 m, abwechselnd links/rechts entlang Marktring, Spangen, Nord-/Sued-/Werk-/Gueterstrasse und Ringweg samt Abzweigen.
- **Bahnwald**: statt zweier Huegel Rauschrelief (`umgebung._bahnrelief`, bis ~6 m) beiderseits des ebenen Gleiskorridors; die Baeume stehen rauschartig dicht (`wald.dichte`), ohne Streifen.
- **Burgberg-Kamm**: der Burgberg setzt sich als Kamm bis zur Nordwestecke fort (`umgebung._burgberg_gewichte`) und steigt dabei weiter an; die Berge ausserhalb setzen auf der Hoehe des Kamms an (`umgebung.rand_anschluss`, `talkessel.hoehe`), der Talrand ist dort also nicht mehr z = 0.
- **Steinbruchgrube** reicht bis zum Westrand der Map (`steinbruch.PIT` ab x = 0).

### Gras-Arten, Bodenrauschen, Streugehoelz (gras.py, wald.py, umgebung._wiesenrauschen)
- **Gras** waechst jetzt auch auf den Gruenflaechen des Flugplatzes (nur dort, wo kein Belag/Halle/Zaun liegt; Raster aus den Flaechen der Umgebung). Arten: Kurzgras, hohes Gras mit Samenstaenden (50..120 cm), Pfeifengras-Horste, Blumen (weiss/gelb/violett/rosa), Farn bei den Baeumen, Schilf mit Rohrkolben an den Teichen. Am Flugplatz in Belagsnaehe nur Kurzgras.
- **Bodenrauschen**: alle Gruenflaechen ausser Flugplatz, ebenen Bauzonen, Burggelaende, Grubenrand, Talrand und Burgplateau sind durch ein Rauschen (+-1 m) uneben.
- **Wald/Streugehoelz** (`wald.alle_baeume`): ein gemeinsames Dichtefeld; im Waldgebiet an der Bahn dichter (reicht bis an den Flugplatzzaun, bleibt nur am Gleiskorridor frei), sonst vereinzelte Baumgruppen. Dadurch keine Streifen mehr, der Wald geht nahtlos in die Bebaumung der Umgebung ueber.

### Muehle, Koehlerhuette, Jagdhuette, Gras im Burgumfeld, feineres Huegelnetz (muehle.py, gras.py, talkessel.py, wald.py, umgebung.py)
- **Huegelland nordlich des Flugplatzes** (x 205..298, y 248..298): der dichte Wald dort ist gelichtet (`wald._nord_licht`: nur noch ~30 % Einzelbaeume und kleine Gruppen, um die Gebaeude Lichtungen); Huegel, Bodenrauschen, Gras und die uebrigen Baeume bleiben. Der Wald an der Bahn (suedlich des Flugplatzes) ist unveraendert.
- **Neue Gebaeude** (`muehle.py`), mit keiner Strasse und keinem Weg verbunden, jeweils auf einem ebenen Bauplatz (`umgebung.PLATEAUS`, Huegel gekappt/aufgefuellt, weiche Uebergaenge): **Bockwindmuehle** auf der Kuppe (236, 276) mit Untergestell (Hausbaum, Kreuzschwellen, Streben), Holzrumpf, Aussentreppe mit Handlauf, Innenraum (Mahlgang, Trichter, Kammrad, Mehlsaecke, Fass, Mehlkasten) und vier Fluegeln mit Latten/Segeltuch; **Koehlerhuette** (A-Rahmen mit Rasensoden, Feuerstelle, Strohlager, Kohlesaecke) mit **Kohlenmeiler** (Russflecken, Leiter, Reisigwand mit Durchgang, Holzstapel, Reisig-/Kohlehaufen, Unterstand mit Kohlesaecken); **Jagdhuette** (Blockhaus aus ueberkreuzten Bohlen, Veranda mit Stufe, Geweihe, Etagenbett, Tisch mit Baenken, Kanonenofen mit Rohr, Anrichte, Waffenschrank, Brennholzschuppen), **Hochsitz** (Treppe, Bruestung, Dach) und **Futterkrippe**.
- Alle Gebaeude sind achsenparallel (Drehung nur in 90-Grad-Schritten, weil die Kollision aus achsenparallelen Quadern besteht), begehbar (Stufen max. 0,29 m, Tueren, Innenraeume), Fluegel und Dachflaechen sind kein Hindernis. Die Footprints stehen in `muehle.BELEGT` (kein Gras/keine Baeume darin).
- **Gras ueberall**: die pauschale Sperre um die Burg (r < 63 m) ist weg; gesperrt sind jetzt nur noch Burg samt Graben, Boeschung, Bruecken mit Zufahrten, Ringweg und Wege. Damit waechst Gras auf der Wiese zwischen Festung und Kreisstrasse (Baeume bleiben dort weiter tabu).
- **Huegel detaillierter** (`talkessel.wiesen_netz`): Gitterweite 5 m -> 2,5 m (rund 25 700 Dreiecke), alle inneren Gitterpunkte sind deterministisch bis 0,3 Zellen verschoben und die Diagonalen wechseln unregelmaessig (keine umgeklappten Dreiecke), Talrand und Lochraender bleiben exakt. Damit beginnt kein Huegel mehr an einer langen geraden Gitterkante; zusaetzlich startet `huegel_roh` weich (kein Knick mehr an der Nullhoehenlinie).
- Hinweis: Tests laufen nur mit Mock-`bpy` (keine echte Blender-Pruefung); Begehbarkeit mit eigenem Raster-Test, Hoehenlinien/Neigungen per Stichprobe.

### Nordanlage zusammengeruckt, Zeltplatz, zweiter Hochsitz, Haeuser am Ringweg (muehle.py, umgebung.py, stadt.py)
- **Huegel im Huegelland nordlich des Flugplatzes** (x > 200, y > 240) sind um 60 % gedaempft (`umgebung._gelaende_basis`); die Hangneigung an den Bauplaetzen sinkt damit auf <= ~1,3.
- **Anordnung**: Bockwindmuehle (270, 284), Koehlerhuette mit Meiler (279..289, 264) und der neue **Zeltplatz mit Feuerstelle** in der Nordostecke (290, 290) liegen jetzt dicht beieinander (je ~20 m); Jagdhuette (255, 263), Hochsitz (246, 288) und Futterkrippe bleiben im Westen davon. Weiterhin keine Strasse/kein Weg.
- **Zeltplatz** (`muehle.zeltplatz`): Steinring mit Glut und Asche, Dreibein mit Kessel, vier Baumstamm-Sitze, drei Firstzelte (Zeltbahn, abgespannt, Rucksack), Tisch mit Baenken, Holzstapel, Wasserfass; Zelte sind niedrige Hindernisse, der Rest ist begehbar.
- **Zweiter Hochsitz** im Wald suedlich des Flugplatzes bei (250, 43) auf eigenem ebenen Bauplatz (Treppe, Bruestung, Dach), Lichtung im Wald.
- **Wohnhaeuser am Ringweg** (`stadt.ring_haeuser`): im Nordwest-Quartal zwischen Marktplatz und nordlichem Kreisel stehen auf der Gruenflaeche zwischen Ringweg und Spange Nord jetzt drei weitere Haeuser (Tuer zum Ring, Pfad zum Ringweg); die Flaeche ist als Bauzone eben (`STADT_ZONEN`).
- Tests nur mit Mock-`bpy` (kein echtes Blender).

### Airfield-Ausbau, Randguertel, Ausstattung, zweite Muehle (flugzeug.py, schilder.py, grenzwald.py, ausstattung.py, muehle2.py)
- **Flugzeuge** (`flugzeug.py`, detailliert aus Querschnittsringen): drei Sturzkampfbomber (Nase nach Suedwesten) auf der Gruenflaeche noerdlich der Hangars - die Wiese ist nur ca. 22 m breit, daher **gestaffelt statt exakt nebeneinander**; in jedem Hangar ein Weltkriegsflugzeug; Tankwagen auf eigenem Stellplatz an der erweiterten Tankstelle. Kein Hakenkreuz am Leitwerk (bewusst weggelassen).
- **Schilder** (`schilder.py`): Rollweg-Beschilderung nach ICAO-Art (Standort schwarz/gelb, Richtung gelb/schwarz, Haltepunkt rot/weiss, 5x7-Pixelschrift) auf der Gruenflaeche entlang der Rollwege; **Pistennummern 36 (Suedende) und 18 (Nordende)**.
- **Randguertel** (`grenzwald.py`): zwei Felsreihen direkt hinter dem Rand (lueckenlos, BFS-Lecktest 0 Zellen), danach dichter Wald und wachsende Felsgruppen, die in das Gebirge uebergehen; Bahneinschnitt mit Felswaenden bis zum Tunnelportal. Gruppen `grenze_felsen`/`grenze_wald` liegen bewusst ausserhalb 0..300 m.
- **Ausstattung** (`ausstattung.py`, automatisch platziert): 7 Trinkbrunnen, 7 Bushaltestellen und 23 Baenke an Strassenraendern/Plaetzen.
- **Zweite Muehle + Schaeferhuette** (`muehle2.py`): gemauerte Hollaender-Turmmuehle (Galerie mit Treppe, Innentreppe, Mahlgaenge) bei (224, 286) und Schaeferwagen mit Pferch bei (216, 262) am Nordrand; die NO-Ecke selbst ist durch Meiler, Zeltplatz und Airfield belegt.
- **Nordwest-Gruenflaeche**: Zone vergroessert, ein zusaetzliches Wohnhaus an der Spange Nord (viel mehr passt ohne neue Strasse nicht).
- Tests sind reine Mock-Tests (ohne echtes Blender).

### Feinschliff Ausstattung, Gras, Randsteine, Bank, Hubschrauber (ausstattung.py, gras.py, stadt.py, muehle*.py, bauernhof.py, felder.py)
- Bushaltestellen nur noch im Ort (4), keine im Flughafen; keine Baenke auf dem Airfield.
- Baenke: Rastplaetze an Gruenflaechen (Tisch, zwei Baenke gegenueber, 16) und Einzelbaenke an kleinen Teichen mit Blick zum Wasser (8); keine Bank auf Wasser. Brunnen (3 Stein, 2 Stahl) je an einem benannten Platz. Seerosen auf allen Teichen.
- Gras: Maske rasterbasiert (Belag/Wege/Plaetze), Haeuser mit echtem gedrehtem Grundriss statt Schutzkreisen; Grosszonen werden nicht mehr pauschal ausgeschlossen.
- Kartenrand: nur noch vereinzelte Steine/Felsen, keine lueckenlose Wand (der Rand ist damit absichtlich nicht mehr dicht).
- Beide Muehlen schauen nach Südwest; schraege Bauten registrieren Hindernisse als Kacheln (`Lok.kachel`), Innenraeume bleiben begehbar. Gilt auch fuer schraeg stehende Haeuser (Treppenloch im OG dafuer eine Stufe frueher).
- Hubschrauber auf dem Helipad (`flugzeug.hubschrauber`); Flugzeug aus dem Hangar am 36er Ende entfernt.
- Bankgebaeude (`oeffentlich.bankhaus`) auf der NW-Gruenflaeche im Kreis; Eckhaus an der Strassenbiegung zur Feuerwehr (45 Grad).
- Bauernhof-Zufahrt als geschwungener Feldweg; Getreidefelder gerade ausgerichtet; mehr Baeume im Nordosten.
- Tests sind reine Mock-Tests (kein echtes Blender).

### Wegweiser, hohes Gras, Gewaechshaus, Kampfhubschrauber, neue Baeume, Ruinenplattformen (ausstattung.py, gras.py, bauernhof.py, flugzeug.py, baumarten.py, ruine.py, muehle.py, stadt.py, oeffentlich.py)
- Wegweiser (gelbe Tafeln, Pfeile) an den Ringabzweigen: RATHAUS, BAHNHOF, FLUGPLATZ, KREISEL (= Nordkreisel), dazu STEINBRUCH am Abzweig nach Westen.
- Hoehere Graeser (35..90 cm, `gras._mittel`) per Streuraster mit Rauschen ueber alle Gruenflaechen (an der Piste niedriger). Gras auf Asphalt: Fahrbahnhoehe beruecksichtigt die Nachbarschaft des Wiesennetzes (`umgebung._z_auf`), quer mehrere Stuetzpunkte; Test: kein Wiesendreieck durchstoesst eine Fahrbahn.
- NW-Gruenflaeche im Kreis: Hotel (`oeffentlich.hotel`, begehbar, Rezeption, Zimmer; ein offenes Fenster) statt Bank. Die Bank steht jetzt auf der Zwischengruenflaeche im SW des Kreises, Eingang zum Bauernhof.
- Neues Wohnhaus am NW-Eck des Marktrings zwischen Feuerwehr und Kirche.
- Offene Fenster (`fensterschmuck(..., "offen")`, keine Scheibe, Fluegel aufgeschwenkt) im OG von etwa jedem dritten begehbaren Zweigeschosshaus. Treppenloch im OG beginnt jetzt eine Stufe frueher (Kopffreiheit bei schraeg gedrehten Haeusern).
- Kampfhubschrauber (`flugzeug.kampfhubschrauber`, ca. 17 m, Vierblattrotor, Stummelfluegel mit vier 19-Rohr-Raketenbehaeltern und zwei Lenkflugkoerpern, sechslaeufige Minigun am Kinn) auf dem Helipad.
- Gewaechshaus am Bauernhof (`bauernhof.gewaechshaus`): Halbzylinder 16 x 6,8 m aus durchsichtigem Glas (Material mit Alpha: `FARBEN`-Eintrag mit 4. Wert, `talkessel.material(..., alpha)`), Steinsockel, Rippen, Tuer zum Hof, innen begehbar mit Beeten und Pflanztisch.
- Neue Baumarten (`baumarten.py`, 230..430 Flaechen je Baum): Eiche, Birke, Fichte, Waldkiefer, Pappel, Obstbaum. `wald.tanne/laubbaum`, Ortsbaeume und Hofobstbaeume nutzen sie; der dichte Randguertel behaelt die einfachen Baeume (`tanne_alt/laubbaum_alt`).
- Hochsitz bei der Muehle entfernt; neuer Standort in der oestlichen Sattelsenke der Burgruine (94,5 / 264).
- Burgruine: die drei Steintreppen enden in begehbaren Plattformen (Suedtreppe am Eckbastion, Nordtreppe hinter dem Palas, Turmtreppe auf der Nordmauerkrone) mit Bruestung; Treppen haben Bruchsteinbruestungen an der offenen Seite.
- Tests sind reine Mock-Tests (kein echtes Blender).

### Korrekturen: Schilder, Hotel, Bankweg, offene Fenster, Ringbaeume, Bahnhofsuhr
- Schilder: Pfosten sitzen hinter den Tafeln (Wegweiser, Haltestellen-, Flughafen- und Pistenschilder), alle Schilder 20 % kleiner (`schilder.SCHILD_SKALA`, Skalierung um den Fusspunkt, auch fuer Hindernisquader).
- Hotel um 180 Grad gedreht (Eingang zur Spange Nord, Gebaeude dafuer etwas zum Ring hin verschoben); Zugangswege zu Hotel und Bank enden am naechsten Punkt einer Strassenlinie (`stadt._naechster_strassenpunkt`) und kreuzen nie das Gebaeude (Bank: gerader Weg von der Tuer zur Werkstrasse).
- Offene Fenster haben keine Laeden und keine Bretter. Alle Haeuser mit offenem Fenster (Stadthaus, Bauernhaus, Hotel) sind per Treppe bis ins Obergeschoss begehbar (Test).
- Einzelne Laubbaeume (`wald.ring_baeume`, 10 Stueck) auf den Gruenflaechen zwischen Burg und Kreisstrasse.
- Bahnhofsuhr sitzt jetzt auf dem Giebeldreieck vor dem Dachrand und ist komplett sichtbar (vorher verdeckte die Dachkante die obere Haelfte).

### Uebertragung ins Spiel: Polytown neu ist jetzt die Standardkarte (export_spiel.py, ../../maps/polytown.ptmap, spiel.py)
- `python3 export_spiel.py` (reines Python, ohne Blender; baut dieselbe Szene mit einer bpy-Attrappe, ca. 45 s) schreibt `Polybash/maps/polytown.ptmap` (18,8 MB). Nach jeder Aenderung an der Karte neu ausfuehren und die Datei mit einchecken.
- Inhalt: 792k Flaechen in 32-m-Bloecken (je Block vier Klassen: opak, zweiseitig, durchsichtig, leuchtend; Licht wie `Mesh.tri` in die Vertexfarben eingebacken, Normalen fuer die Echtzeit-Schatten), 70k Gelaende-Dreiecke fuer die Kollision (`TriMesh` der Engine: Wiese, Berge, Burggelaende, Steinbruchgrube, Wege, Piste ...), 80k Kollisionsquader (`Bau.bx`, Kacheln gedrehter Waende verschmolzen), 61 Startpunkte, 12 Kisten, 2 Fahrzeuge, Helipad (240/184), Minimap und Menue-Vorschau.
- `spiel.py`: `pt_find`/`load_ptmap`/`pt_mapdata` laden die Datei, `World.build_pt` setzt die Quader (Raster 4 m), `build_pt_scene` baut die Grafik direkt aus den fertigen Vertex-Feldern. Fehlt `maps/polytown.ptmap`, startet die alte, im Code erzeugte Polytown-Karte. Mitspieler bekommen vom Host nur die Kopfzeile und laden die Datei aus ihrem Ordner `maps` (wie bei der Minecraft-Karte).
- Der flugfaehige Spiel-Hubschrauber steht auf dem Helipad; der statische Kampfhubschrauber der Blender-Szene wird dafuer nicht exportiert. Die Radarantenne auf dem Tower dreht sich (144 Grad/s wie in Blender).
- Tomahawk: Code, Zustand und Einstellungen bleiben unveraendert; der Knopf liegt ausser Reichweite, bis der Kontrollraum nachgebaut ist (`World.build_pt`, `button`/`timer_panel`).
- Tests: nur Spiellogik mit Panda3D-Attrappen (Weltaufbau, keine Luecken im Gelaende, Startpunkte, Haeuser betreten, Heli, Auto, Netz-Pruefsumme). Die Grafik (echte Panda3D-Geometrie, Schatten) konnte hier nicht gerendert werden.

#### Nachbesserung: Zaeune, Heli, Daecher, Wasser, Texturen (Format `ver` 2)
- **Zaeune**: `Bau.kol` (nur Kollision) liefert durchgehende, 0,6 m dicke Zaunwaende (Flugplatz `zaunstrecke`, Weidezaun in `bauernhof.zaun`) - vorher standen nur 0,12-m-Pfosten und duenne Holme, durch die man bei niedriger Bildrate (und zwischen den Pfosten) hindurchkam. `spiel.step` zerlegt lange Bilder ausserdem in Schritte von hoechstens 0,05 s. Im Nord- und im Suedzaun des Flugplatzes ist bei x = 247..253 (`ZAUN_LUECKE`, `zaun_umgeknickt`) eine durchgebogene Stelle ohne Kollision, durch die man gehen kann.
- **Hubschrauber**: der statische Kampfhubschrauber ist jetzt ein eigenes Objekt `umgebung_heli` (`umgebung.hubschrauber()`), das der Export weglaesst (`WEGLASSEN`); vorher blieben Rotor, Mast und Streben (Material "Flug ...") am Boden stehen, wenn der Spiel-Heli abhob.
- **Daecher**: alle nach oben zeigenden Flaechen mit "dach" im Materialnamen (16978 Dreiecke) kommen als Kollisionsdreiecke dazu (`kind` 6 = Dach + zweiseitig; `TriMesh` nimmt sie nicht in die Gelaendehoehe "ups" auf). Man laeuft auf dem Schraegdach des Feuerwehrhauses (und aller Haeuser), solange es flacher als ca. 50 Grad ist.
- **Wasser**: `wasser_maske` schreibt eine 0,5-m-Maske der tiefen Zellen (Burggraben, Teiche) in die Datei; `World.water_at` verhindert, dass Spieler und Fahrzeuge von Land aus hineingehen (Bruecken ab 1,5 m ueber dem Spiegel nicht; wer drin ist, kommt heraus). Wasser ist leicht durchsichtig (Alpha 0,9).
- **Texturen**: `export_spiel.TEXMAP` ordnet Blender-Materialien den Spiel-Texturen zu (`pt_grass`: Wiese; `pt_asphalt`: Strasse/Weg/Piste/Vorfeld/Fahrbahn; `pt_water`: Wasser; `pt_fort`: Mauerwerk/Hof/Stufen/Burgstein). Die Gruppen tragen dafuer Texturkoordinaten (Ebene passend zur Flaechenrichtung, in Kacheln) und `tx`; `spiel.py` erzeugt die Texturen selbst (`_t_pt_*`, `TEXGEN`, je 256 x 256 px, nahtlos) und multipliziert sie mit den Vertexfarben.
- Tests (nur Attrappen, **keine** echte Grafik): Zaun-Durchlauf bei 60/30/10 fps (nur die Luecken sind passierbar), Fallen und Laufen auf Daechern, Wasser (197 Anlaeufe von Land: 0 im tiefen Wasser; 120 von 120 kommen heraus), alte Polytown-Tests. Die Texturen wurden als PNG geprueft, ihr Aussehen im Spiel nicht.
- Mitspieler brauchen die neue `maps/polytown.ptmap` (gleiche Kennung, neues Format).

#### Nachbesserung 2: Marktplatz-Laeden, Ruine, Haustexturen, Strassenrand, Muehlen, Rauch
- **Laeden am Marktplatz** (`stadt.laden`, `plane_stadt`): 8 x 7,6 m statt 8 x 10 m, Mittelpunkte x = 36 (West) und 74 (Ost) - sie stehen jetzt zwischen Marktring-Strasse (Kante x = 31 / 79) und Platz (x = 40 / 70) auf der Gruenflaeche (Raster-Pruefung: keine Strassenzellen im Grundriss). Alle vier sind blau.
- **Burgruine**: `TEXPART` ordnet fuer das Teil `burgruine` alle Steinmaterialien ("Stein alt", "Stein dunkel", "Felsen Burg", "Burgstein ...") der Burgstein-Textur `pt_fort` zu; vorher fielen "Stein alt" (6546 Flaechen) und "Felsen Burg" heraus.
- **Haeuser/Daecher/Schilder** (`TEXMAP`): `pt_plaster` (Putz, abgeplatzt), `pt_brick` (Backstein/Klinker), `pt_rubble` (Bruchstein: "Stein ...", ausser an der Ruine), `pt_tile` (rote Tondaecher mit Moos), `pt_slate` (graue/schwarze Daecher, Schiefer), `pt_wood` (Holz, Dielen, Laeden, Tueren), `pt_sign` (lackiertes Blech: Schilder bleiben gelb/weiss/rot/gruen, bekommen Kratzer und Rost). Texturkoordinaten: `uv_koord` (u entlang der waagerechten Tangente, v in Hangrichtung, Reihen bleiben auch auf Schraegdaechern waagerecht).
- **Strassenrand**: `strassenraender` legt an den Kanten von "Strasse"/"Weg" einen 1,4 m breiten, durchsichtig auslaufenden Streifen (Alpha 0,8 -> 0, Farbe Asphalt -> Verge) auf den Rasen - nur wo aussen Wiese liegt (Rasterpruefung gegen Platz/Pflaster, Haeuser, Wasser, andere Wege). 1737 Streifen, eigene Gruppen der Klasse 2.
- **Muehlen**: die Fluegel beider Muehlen sind eigene Objekte (`nord_muehle_fluegel`, `nord2_muehle_fluegel`, Drehpunkt/Wellenrichtung in `FLUEGEL_ACHSE`). Im Export liegen ihre Vertices lokal um die Nabe (Welle = +y); das Spiel dreht den Knoten um diese Achse (`roll`: `setHpr(h0, 0, t * speed)`), 22 bzw. 16 Grad/s.
- **Rauch**: `rustik.kamin` merkt sich jede Kaminoeffnung (`SCHORNSTEINE`); der Export laesst aus 13 von 25 Schornsteinen Rauch aufsteigen (`meta.smoke`). Im Spiel steigen je 7 weiche, grauer werdende Puffs auf, wachsen, driften mit dem Wind und verblassen (nur im Umkreis von 110 m berechnet).
- Test: nur Attrappen (Weltaufbau, Kollision, Szenenaufbau); die Nabenlage der Fluegel wurde rechnerisch geprueft (Radius 4,5 / 7,7 m, Achsversatz < 1 m). Rauch, Strassenrand und Texturen im echten Spiel nicht gesehen.


#### Nachbesserung 3: Treppen, Schienen, Fenster, Kollision, Boeden, Teiche, Rauch
- **Treppen**: Das Treppenloch der Haeuser (`stadt.haus`, `oeffentlich`) beginnt jetzt schon bei der 2. Stufe (vorher 4.), und `push_out` ignoriert Quader, in die nur der Kopf (`HEAD_TOL` 0,35 m) hineinragt - sonst blieb man beim Abstieg am OG-Geländer/an der Decke haengen.
- **Schienen**: Gleisteile (Bett, Schwellen, Schienen) sind nur Optik, ohne Kollisionsquader - man laeuft auf Gelaendehoehe ohne Wackeln.
- **Fenster**: Die Scheibe sitzt buendig an der Wandflaeche (vorher 17 cm tief in vollen Kernen = "zugemauert", v. a. Rathaus/Gasthaus am Markt).
- **Schuesse durch Zaeune**: Zaunpfosten/-holme sind nur Optik; die Spielerkollision macht die Zaunwand (`kol`), die im `.ptmap` als `meta.nclip` letzte Quader steht und als `Box.clip` Schuesse (`seg_box`) durchlaesst.
- **Fahrzeuge**: niedrige senkrechte Kanten (< 0,3 m, z. B. Pistenmarkierungen) sind keine Kollisionswaende mehr; Schranken und Torstuetzen am Flughafen haben keine Kollision mehr (Spur war enger als der Wagen).
- **Hangars**: die Rundbogenhallen haben Kollision an den steilen Bogenteilen und der Rueckwand.
- **Unsichtbare Waende**: schraeg gedrehte Quader (`Lok.kachel`) werden immer als Kacheln (0,6 m) erfasst statt als ausgerichteter Rahmen.
- **Boeden**: neue Texturen `pt_gravel` (Pfad, Schotter, Schotterbett, Bruch Erde), `pt_cobble` (Pflaster, Bahnsteig), `pt_dirt` (Hofboden, Acker, Schlamm), `concrete` (Beton, Hangar Boden).
- **Bankweg**: Pfade enden an der Strassenkante statt mitten auf dem Asphalt.
- **Teiche**: Wasserflaeche reicht bis `tr + 3,2` (Mulde endet bei `tr + 3,5`), keine Luecke zum Ufer.
- **Rauch**: 14 Puffs, 16 m hoch, dunkel (0,09) und dichter (Alpha 0,92).
- **Raketenwerfer**: Beim Nachladen kommt die Rakete von links unten ins Bild, die Hand fasst sie von der Seite.
- Test: nur Attrappen (kein Blender, kein Panda3D-Rendering).
- Weitere Punkte dieser Runde: Wasserpruefung (`water_at`) zaehlt Brueckenplanken nicht als Wasser, Nordbruecke hat eine durchgehende Fahrbahn-Kollision; Dachdreiecke sind bis ca. 73 Grad immer begehbar (kein Durchfallen); Marktbrunnen/Dorfbrunnen haben Kollision (`kreis_sperre`); Laternen stehen nicht auf Umlandwegen; Boeschung der Festungsinsel traegt die Gras-Textur; Stellwerk-Treppenloch beginnt am Treppenfuss; Steinbruch-Wegweiser siehe unten.
