# Patchnotes

Neueste Änderungen oben.

## Testgelände: Dev-Sandbox mit F1-Menü (Robin, 2026-10-26)
Neue eingebaute Karte für alle Modi-Tests. **NET_VERSION 50**: neue Nachricht `dev` (Mitspieler -> Host) und Ereignis `devstate` - alle müssen aktualisieren.

Karte "Testgelände" (Setup: zweite Kachel neben Polytown, 240 x 240 m):
- Graubox-Look: heller Boden und alle Bauten mit 1-m-Raster (feine Linie je Meter, kräftige je 4 m), Akzentfarben je Bereich, wenig Nebel. Kein Gras, keine Bäume.
- Immer Deathmatch (Experimental geht auch), keine natürlichen Monster, keine Bonuskisten/-hasen, kein Tomahawk, Rundenzeit 2 h (das Zeitlimit im Setup gilt hier nicht).
- Die Karte entsteht auf jedem Rechner aus dem Code (`dev_map_raw`); übers Netz geht nur die Kennung. Keine Datei im Ordner `maps` nötig.

Abschnitte:
- **A Arsenal** (Raum im Südwesten): vier Tischreihen mit allen Waffen (ohne Dual Baretta - zwei Barettas nehmen), allen Nahkampfwaffen, allen Granatenarten inkl. Airdrop-Fackel und Jet-Strike, den drei Gadgets, allen aktuellen Ausrüstungsteilen, allen Aufsätzen und Visieren. Genommenes liegt nach 3 s wieder da (`DEV_ARS_RESPAWN`); Arsenal-Teile verfallen nicht und zählen nicht zur Drop-Obergrenze.
- **B Showroom** (17 m hohe Halle): Zombie, Jägerin, Brute, Drohne, Hase, Koloss und Titan als Standmodelle auf Sockeln (unverwundbar, keine KI, nicht wegschleuderbar), dazu die eigene Spielfigur.
- **C Testflächen** unter freiem Himmel:
  - Schlucht: zwei 8-m-Plateaus, dazwischen 14 m Lücke bis zum Boden; Hauptbrücke (2 m), Planke (0,8 m), kaputte Brücke (4 m Lücke); Treppen von Süden (beide) und Norden (West). Rote Kanten.
  - Labyrinth: 12 x 12 Zellen à 4 m, 3,2 m hohe Wände, mehrere Wege, Eingänge Süd/Nord/West.
  - Testhaus: drei Geschosse (3,6 m) + begehbares Dach mit Brüstung, Türen, Fenster, Zwischenwände, Treppen abwechselnd Ost/West mit offenen Treppenlöchern.
  - Fahrzeugzone: 6 Geländewagen, 4 Helipads mit Helikoptern, Container-Deckung, Slalom-Pfosten, Zielwände.

Dev-Menü (**F1**, nur auf dem Testgelände; nochmal F1 oder Esc schließt):
- Spawnpunkt ist der Punkt unter dem Fadenkreuz beim Öffnen (Boden, Dach, Plateau, Brücke - auch in der Höhe). Weitere Spawns werden ringsum frei verteilt.
- Monster: Zombie, Jägerin, Brute, Koloss, Titan, Drohne. KI-Verhalten: **Aggressiv** (sucht sofort), **Passiv** (greift nie an, wandert, folgt Geräuschen), **Zielscheibe** (steht, fällt nie unter 1 HP, nach 3 s ohne Treffer wieder voll). Höchstens 60 gleichzeitig; keine Beute, kein Respawn.
- Fahrzeuge: ein freier Geländewagen bzw. Helikopter aus dem Pool wird ans Fadenkreuz gestellt (reihum, voll repariert und munitioniert, Blick wie der Spieler).
- Loadout-Sets: Sturm, Sniper, Schwer, Anti-Fz, Nahkampf (Waffen, Nahkampf, Rüstung, Granaten; Sniper mit Zielfernrohr).
- Schnellbefehle: Godmode (kein Schaden, auch kein Fallschaden), Munition unendlich (Magazin, Reserve, Granatwerfer), Aggro zurücksetzen (alle Monster vergessen ihr Ziel), Alles entfernen (gespawnte Monster und Nester weg, Fahrzeuge zurück, lose Teile weg; Showroom und Arsenal bleiben).
- Mitspieler schicken die Befehle an den Host; Rückmeldung als Hinweis in der Bildmitte.

Erste Beobachtungen auf dem Testgelände (noch nicht geändert, zum Nachjustieren):
- Schlucht: Zombie/Brute auf dem einen Plateau laufen auf ein Ziel auf dem anderen Plateau direkt zu und fallen an der Kante hinunter, statt die Brücke zu nehmen.
- Labyrinth: Monster finden zum Spieler in der Mitte.
- Testhaus: ein Monster vor dem Haus verfolgt einen Spieler im 3. Geschoss nicht (Höhenunterschied > 3,5 m blendet das Ziel aus).

Technik: `DEV_*`-Konstanten, `dev_map_raw`, `dev_maze_walls`, `dev_arsenal_slots`, `dev_fill_ammo`; `World.dev`, `dev_setup`, `dev_refill`, `dev_update`, `dev_command`, `dev_kit`, `dev_aim`, `dev_free_spot`, `dev_add_mob`; `Mob.dev_ai` (show/aggr/passive/static); Textur `devgrid`; `Game.on_dev`, `show_dev`, `dev_cmd`; `ClientSession.send_dev`.

## Aufsatz-Inventar, Waffen-Fixes, Rüstungs-Rework, Hacker- und Nekromanten-Set (Robin, 2026-10-26)
Gilt für alle Modi. **NET_VERSION 49**: neue Ausrüstungs-Indizes, neue Nachrichten (`hscan`, `nest`, Dash-Zähler `ds`), Nester im Snapshot (`ne`), Granaten-Werfer im Snapshot - alle müssen aktualisieren.

Aufsätze und Beute:
- **Blank-Spawns überall**: Waffen liegen in allen Modi (auch Experimental/Pistolenstart) ohne Aufsätze in der Welt. Aufgehobene Waffen kommen ohne Visier - auch die **DSR** hat dann Kimme und Korn; Sniper-Visier, Mündungen, Griffe, Magazine gibt es nur als Beute. VSS und Karabiner 98k behalten ihr fest verbautes Glas (ist kein Aufsatz).
- **Aufsatz-Inventar**: Aufsatz aufheben -> Platz an der Waffe in der Hand frei: wird sofort montiert. Platz belegt: der neue wandert ins Aufsatz-Lager, der alte bleibt dran (nichts wird überschrieben). Wechseln über die Waffen-Inspektion (**T**). Wird eine Waffe getauscht, kommen ihre Aufsätze ins Lager statt verloren zu gehen.
- **Schalldämpfer-Verschleiß**: jeder gelootete Dämpfer hält zufällig **1,5-3 Magazine** (`SIL_DUR`); Rest steht im Inspektions-Fenster. Ist er aufgebraucht, fliegt er ab (Klirren, Splitter), die Waffe ist wieder laut, der Dämpfer ist weg.
- **Granatwerfer-Nachschub**: trägt der Colt M4 Carbine schon einen Werfer, gibt ein weiterer nur **+3 Granaten** (höchstens 6).

Waffen:
- **Stinger**: Erfassung nur noch auf Fahrzeuge, Helikopter und **fliegende Spieler** (Jetpack an oder > 2,5 m über dem Boden, `STINGER_AIR_H`), nie auf Monster; nur mit **freier Sichtlinie** (nichts hinter Wänden/Deckung). Die Rakete lenkt auch auf Spieler.
- **Minigun**: Anzeige "Anlauf %" entfernt. Das Hochdrehen hört man: mechanisches Rattern + Motorheulen, Tonhöhe und Takt steigen mit der Drehzahl (neuer Klang `minispin`).
- **Dual Baretta**: beide Pistolen tragen die Aufsätze der ersten (auch am Modell der linken); die Inspektion (T) zeigt nur die rechte; Nachladen nacheinander - erst links, dann rechts (je ein Magazin-Geräusch).

Ausrüstung - aus Sets werden Einzelteile:
- **Schweres Exo-Jetpack** (Torso, ersetzt Jetpack-Set): Steigen/Sinken x1,6, Tank 15 s, kein Fallschaden; **sperrt Kopf und Füsse** (getragene Teile fallen ab, neue lassen sich nicht anlegen); am Boden 12 % langsamer. Bulligeres Modell mit Exo-Rahmen.
- **Hermes-Boots** (Füsse, ersetzt Hermes-Set): x1,6 Tempo, **Blitzen-Dash** (15 m in 0,43 s), **60 s** Abklingzeit. Dafür doppelt so laute Schritte (Monster-Lärm und Schrittgeräusch für andere) und beim Dash ein **Überschallknall** (Lärmradius 110 m, bis ~400 m zu hören).
- Hermes-Helm, Hermes-Weste, Jet-Helm, Jetpack-Stiefel sind ausgemustert (Indizes bleiben, kommen nicht mehr aus der Beute).

Set-Reworks:
- **Schild-Set - Schockwelle (B)**: Radius 4 -> **9 m**; schleudert Getroffene bis an den Rand (Wände bremsen; Titan/Koloss nur betäubt); fremde **Schilde sofort auf 0** und 6 s keine Aufladung; **Jetpack-Tank leer**, **Dash lädt neu**. Trifft das eigene Team nicht mehr.
- **Springfeder-Set**: komplett -> in der Luft (Sprung, Doppelsprung, Wandsprung) und an der Wand streuen alle Waffen aus der Hüfte nur noch x0,35 (kein Luft-/Laufmalus); Fadenkreuz zieht sich zusammen. Kein Fallschaden wie bisher.
- **Zweite Chance**: unverändert.

Neue Sets:
- **Hacker-Set** (blau): *Visor* - bläuliche Sicht, feindliche C4/Claymores und fliegende Granaten in 70 m werden markiert (auch durch Wände); *Weste* - **Quadranten-Scan (B)** alle 45 s: welche Kartenfelder (Polytown: 4 Quadranten) Gegner enthalten, 8 s als Raster neben der Minimap und auf der Karte (M); *Stiefel* - halb so laute Schritte. Set-Bonus: Scan alle 30 s und 9 Sektoren.
- **Nekromanten-Set** (schwarz/Knochen): *Maske* - Monster bemerken dich erst aus halber Entfernung; *Robe* - 25 % weniger Monster-Schaden; *Grabstiefel* - Schritte locken keine Monster an. Set-Bonus: **Monster-Tarnung** (Monster ignorieren dich, bis du sie angreifst - je Monster) und das **Nest-Wählrad** (B halten, Maus wählt, loslassen setzt): Nest bis 12 m vor dir, lebt **5 min**, zerstörbar (Kugeln, Explosionen; nicht vom eigenen Team). Über die Lebensdauer schlüpfen ~20 Zombies / 14 Jägerinnen / 10 Brutes / 5 Kolosse / 2 Titanen; sie verschonen Beschwörer und Team, lassen keine Beute fallen und kommen nicht wieder. Ein Nest je Spieler, danach 30 s Pause.
- Beute-Tabelle der Ausrüstung neu verteilt (Spalten je 100).

Technik: `Gear.blocks`/`Gear.legacy`, `World.nests`/`Nest`, `hack_scan`, `place_nest`, `knock_mob`, Ereignisse `shockhit`, `hboom`, `hscan`, `nest*`, `silbreak`, `gearblock`; `attstate` trägt die Dämpfer-Haltbarkeit mit.

## Waffen-, Ausrüstungs- und Nahkampf-Paket (Robin, 2026-10-26)
Gilt für alle Modi (KotH, DM, CTF, Experimental). **NET_VERSION 48**: neue Waffen- und Nahkampf-Indizes, neue Nachrichten (`fire` mit `gl`, `axe`), alle müssen aktualisieren.

Umbenannt (nur Namen, Indizes 0-8 bleiben):
- Sturmgewehr -> **Colt M4 Carbine**, Scharfschützengewehr -> **DSR**, Maschinenpistole -> **MP9**, Pistole -> **Colt ACP**.

Geänderte Waffen:
- **Colt M4 Carbine**: Schaden 17 -> 15, Hüftstreuung 1,6° -> 1,25° (weniger als die SCAR-L). Kein Schalldämpfer möglich. Exklusiv: Aufsatz **Granatwerfer** (Platz Griff, ersetzt ihn): Rückstoß x1,9, Streuung beim Zielen x2,6. **V** schaltet Auto -> Semi -> Granatwerfer; 40-mm-Granaten im Bogen (`GL_*`: 3 je Waffe, max. 6, 2,2 s Nachladen, Radius 4 m, 95 Schaden).
- **MP9**: Schaden 11 -> 8, starkes Spray im Dauerfeuer (Streuungszuwachs 0,10 -> 0,34, Seitenrückstoß 0,6 -> 1,5).
- **Colt ACP**: Hüftstreuung 0,9° -> 1,2°.
- **Minigun**: kein Zielen mehr (Rechtsklick wirkungslos), Hüftstreuung 3,0° -> 2,0°. **Anlauf**: 2 s aus dem Kaltstart; nach dem Loslassen dreht sie 1,5 s aus (`MINIGUN_SPIN_DECAY`). Wer in diesem Fenster wieder abdrückt, läuft nur den Rest an. HUD zeigt „Anlauf xx %“, Waffe zittert und surrt beim Hochdrehen.
- **Railgun**: 90 Schaden an Personen/Monstern (vorher 140), fest **200** an Fahrzeugen und Helikoptern (`Weapon.veh_dmg`, ohne Heli-Faktor).

Neue Waffen (nur aus Kisten/Beute, Loot-Tabellen neu verteilt):
- **SCAR-L** (Haupt): die alten Werte des Sturmgewehrs (17 Schaden, 1,6° Hüfte).
- **AK** (Haupt): 19 Schaden, deutlich mehr Rückstoß (1,45 / 0,85 seitlich).
- **VSS** (Haupt, DMR): Schaden an die Colt ACP gekoppelt (`PISTOL_DMG` = 28: 4 Körper- oder 2 Kopftreffer), Magazin 10, festes Zielfernrohr **4x -> 6x -> 8x per Mausrad** beim Zielen.
- **Karabiner 98k** (Haupt): keine Aufsätze, festes 10x-Glas, Repetierer: nach jedem Schuss 4 s Durchladen (Animation, Klicks, kurz aus dem Glas). Hüfte 7° (extrem ungenau). 100 Schaden Körper, 140 Kopf.
- **Baretta** (Sekundär): 24 Schaden, etwas langsamer als die Colt ACP, präziser (0,65°). Eine **zweite Baretta** macht daraus die **Dual Baretta**: beide Hände, abwechselnd links/rechts, doppelte Munition und Nachladezeit, nur aus der Hüfte, ungenauer. Restmunition der ersten wandert in die Reserve.
- **Abgesägte Schrotflinte** (Sekundär): gleicher Schaden wie die Schrotflinte (9 x 9), Streuung 8° statt 4,5°, 2 Schuss, Kipplauf-Nachladen.
- **Stinger** (Spezial): Zielerfassung nur auf Fahrzeuge/Helikopter, 4 s im Kegel halten. Fadenkreuz **rot** (kein Ziel) -> **gelb** (Erfassung, Piepen) -> **grün** (schussbereit); ohne Erfassung nur ein Klicken. Lenkrakete (`STINGER_*`): Volltreffer 260 an Fahrzeugen (zerstört), 520 an Helikoptern.

Neue Waffen benutzen das Modell ihres Vorbilds umgefärbt/gekürzt/ergänzt (`Weapon.model`, `GUN_SHAPES`-Varianten: SCAR-L sandfarben, AK mit Holz, VSS mit Schalldämpfer, 98k Holz/Brünierung mit Kammerstängel, Baretta silber, Abgesägte gekürzt, Stinger oliv mit Suchkopf) und dessen Klang leicht verstimmt.

Schalldämpfer und Aufsätze:
- **Schalldämpfer** (alle Waffen außer Colt M4 Carbine): Lärmradius höchstens wie ein laufender Spieler (`SILENCED_NOISE` = 10 m statt 43-60 m). Andere hören nur ein leises Zischen im Umkreis von ca. 16 m (neuer Klang `silenced`).
- In **normalen Modi** (KotH, DM, CTF) liegen Waffen immer **blank** in der Welt - auch fallengelassene oder von Toten. Aufsätze gibt es separat bzw. im Ausrüstungsmenü. Experimental bleibt wie bisher.
- Aufsatz-Auswahl (Menü und Tab-Fenster) zeigt nur, was an die Waffe passt (`att_fits(wi, si, v)`); unpassende Aufsätze werden beim Spawnen/Aufheben entfernt (`att_clean`).

Nahkampf:
- **Schwert**: 3-s-Halteangriff mit Kamerafahrt (Blick hebt sich mit der Klinge, beim Aufschlag von oben nach unten). Beim Aufschlag Luft-Druckwellen und Erde in **V-Form** ca. 2 m hoch; der halbtransparente Staub hängt 4-5 s und verschwindet dann ganz.
- **Erschöpfungsklinge** gestrichen (Waffe, Beute, Modell, Lebensraub/Erschöpfung).
- NEU **Kriegsaxt**: normaler Nahkampf (58 Schaden, Kopf x1,7) plus Wurf: halten lädt bis 100 % (1,2 s), loslassen wirft - ohne Flugbahn-Anzeige. Wurf 35-90 Schaden; die Axt fliegt aus der Hand (Messer bleibt) und liegt danach als Beute am Boden. In Fahrzeugen/Helikoptern bleibt sie 5-10 s stecken (zufällig) und macht 10 Schaden/s. Look: schwarzer Stiel mit Rauch, rote Wicklung, Bartaxt mit blutroter Schneide, Ziegenbock-Gravur mit rot leuchtenden Augen.

Technik: Granatwerfer/Lenkrakete laufen als Kugeln mit Explosion (`WI_GL`, `Bullet.target`), Axtwürfe als `World.axes` (Host) mit Ereignissen `axe_fly`/`axe_stick`/`axe_end` für die Darstellung.

## Mobs weichen Hindernissen aus (2026-10-25)
Nur Verhalten der Monster auf dem Host; das Netzprotokoll bleibt.
- NEU **Fühler-Ausweichen** (`Mob.steer_around`): Bodenmonster (Zombie, Brute, Jägerin, Koloss, Titan) prüfen im Verfolgen zwei Punkte voraus mit derselben Kollisionsabfrage wie die Bewegung (`push_out`). Liegt ein Hindernis voraus, laufen sie seitlich daran vorbei: die gewählte Richtung wird in Weltkoordinaten gemerkt und gehalten, bis der direkte Weg wieder frei ist (gleiten an der Wand bis zur Ecke, kein Hin-und-Her).
- NEU **Sackgassen**: pendelt ein Monster zwischen zwei Ecken (U-Form), läuft es erst ein Stück rückwärts heraus und dann seitlich am Hindernis vorbei (`MOB_AVOID_ESC`). Das alte Festfahren-Umweg-Verfahren bleibt als Reserve.
- Kosten: zwei Kollisionsabfragen alle 0,18 s je Monster (gemessen ca. +6 µs je Monster und Bild). Drohnen, Fluchttiere und Geräusch-/Wandern-Ziele ohne Verfolgung sind unverändert; Wege durch Gebäude (Tür) übernimmt weiter `nav_steer`.
- Grenzen: das ist lokales Ausweichen, keine Wegsuche über die ganze Karte. In sehr großen Sackgassen braucht ein Monster 30-60 s.

## Flak nur noch beweglich, mehr Sicht nach unten; Treppengeländer der Burg (2026-10-25)
**NET_VERSION 47**: Neigungsgrenze der Flak geändert (Host und Mitspieler müssen gleich klammern).
- GEÄNDERT Das feste Flak-Modell aus der Karte wird beim Laden entfernt (`_pt_strip_flak`, nur Darstellung); es gibt nur noch das bewegliche Geschütz, das sich mit dem Bediener dreht.
- GEÄNDERT **Flak zielt weiter nach unten**: Neigung bis -72° statt -50°; das Dach-Brett vorn am Gehäuse (verdeckte die Sicht nach unten) entfällt bei der Flak, die Kamera steigt beim Blick nach unten höher und weiter zurück.
- BEHOBEN **Absturz von der Burgtreppe**: an den Hoftreppen zum Wehrgang (West/Ost) waren nur Pfosten und schräge Holme modelliert, dazwischen konnte man durchfallen. `pt_rail_boxes` legt unsichtbare Kollision (Stufe für Stufe, Podest, Stirnseite) darüber. Andere Geländer der Karte sind noch nicht geprüft.

## Flak-Geschütze der Burg auf Polytown bedienbar (2026-10-25)
**NET_VERSION 46**: die Geschützliste der Welt ändert sich, alte Clients können nicht mehr beitreten.
- NEU Auf den Burg-Ecktürmen NW (128/172) und SO (172/128) stehen zwei Flak-Geschütze (`PT_FLAK`, Mitte 9,35 m über dem Sockel, den die Karte schon enthält). Wie in der alten Burg: **F** am Geschütz zum Bedienen, Maus zielt, Linke Maustaste schießt, Hitzebalken. Die Flak-Granate zündet in der Nähe von Helikoptern (`FLAK_PROX`) und macht Flächenschaden (`FLAK_R`/`FLAK_DMG`).
- Ton: `flak_single` (eingebettete Aufnahme, wurde schon für die alte Burg verwendet), Lautstärke 0,8 am eigenen Geschütz.

## Mausrad erreicht die Nahkampfwaffe (2026-10-25)
- GEÄNDERT Das Mausrad schaltet jetzt Slot 1 -> Slot 2 -> Nahkampfwaffe (Slot 5) -> wieder Slot 1 (rückwärts umgekehrt). Spezialwaffe (3) und Gadget (4) bleiben bei den Tasten; hat man eines davon in der Hand, geht das Rad zurück zur zuletzt benutzten Waffe aus Slot 1/2. Nur Eingabe, das Netzprotokoll bleibt.

## Heli: Zielsystem wie in BF3 (2026-10-25)
Nur Kamera, HUD und Richtung der Bordwaffen; am Netzprotokoll ändert sich nichts.
- GEÄNDERT **Kamera**: sie sitzt 15 m hinter und 4,2 m über dem Heli (`HELI_CAM_DIST`, `HELI_CAM_UP`) statt genau auf der Sichtachse. Der Heli hängt dadurch im unteren Bilddrittel unter dem Fadenkreuz, das Ziel am Boden bleibt frei.
- GEÄNDERT **Fadenkreuz an der Maus**: Minigun und Raketen zielen auf den Punkt unter dem Fadenkreuz (Blickstrahl des Piloten, Kugelabfall ausgeglichen) und schwenken dafür bis zu 14° seitlich und 12° in der Höhe aus der Rumpfachse (`HELI_GUN_YAW`, `HELI_GUN_PIT`). Das Kreuz bleibt so fast in der Bildmitte, auch wenn der Rumpf noch nachdreht. Außerhalb des Schwenkbereichs zeigt es weiter den echten Einschlagpunkt.
- GEÄNDERT **Heli folgt der Maus rascher**: Kurs 240°/s statt 125°/s, Nachlauf 8 statt 4; Nick 120°/s statt 62°/s, Nachlauf 9 statt 4,5 (90° Kurswechsel in ca. 0,5 s statt 0,9 s).

## Feste Waffen-Slots: Hauptwaffe und Sekundärwaffe (2026-10-25)
Gilt für KotH, DM, CTF und Experimental gleichermassen. **NET_VERSION 45**: alle müssen aktualisieren (Host und Mitspieler müssen dieselben Slot-Regeln haben).
- NEU **Waffenkategorie**: jede Waffe hat `weapon_type` (`WT_PRIMARY`, `WT_SECONDARY`, `WT_SPECIAL`). Haupt: Sturmgewehr, Schrotflinte, Scharfschütze. Sekundär: Pistole, Revolver, Maschinenpistole. Spezial (wie bisher nur Slot 3): Raketenwerfer, Minigun, Railgun. `PRIMARY_NAMES`/`SECONDARY_NAMES` werden daraus abgeleitet.
- NEU **Feste Slots** `SLOT_PRIMARY` (Taste 1) und `SLOT_SECONDARY` (Taste 2), dazu `TYPE_SLOT` (Kategorie -> Slot). Zwei Hauptwaffen oder zwei Sekundärwaffen gleichzeitig sind nicht mehr möglich.
- GEÄNDERT **Aufheben/Tauschen**: eine Waffe kommt immer in den Slot ihrer Kategorie. Ist er belegt, fällt die alte Waffe dort (mit Aufsätzen) auf den Boden. Bisher landete jede normale Waffe im ersten freien Slot bzw. tauschte die Waffe in der Hand. Der Hinweis „tauscht gegen …" zeigt die richtige Waffe.
- GEÄNDERT **Start**: Experimental startet mit der Pistole in Slot 2 (Slot 1 bleibt leer bis zur ersten Hauptwaffe). Ein ungültiges Loadout mit zwei Waffen derselben Kategorie behält nur die erste.
- GEÄNDERT **Mausrad** schaltet nur noch zwischen Slot 1 und Slot 2 um. Kistenwaffe (3), Gadget (4) und Nahkampf (5/F) nur noch über ihre Tasten; hält man eins davon, bringt das Mausrad die zuletzt benutzte Waffe aus Slot 1/2 zurück.

## Waffenleiste mit 6 Slots (2026-10-25)
- GEÄNDERT **Slots unten**: 1 Sturmgewehr, 2 Sekundärwaffe (beide wie bisher), **3 Spezialwaffe**, **4 Gadget** (neue eigene Karte), **5 Nahkampfwaffe**, **6 Granate**.
  Bisher teilten sich Gadget und Spezialwaffe Taste 3, die Nahkampfwaffe lag auf 4. Taste 3 wählt jetzt nur die Spezialwaffe aus der Kiste (ohne eine gibt es einen Hinweis).
- GEÄNDERT Die Granaten-Karte ist etwas kleiner als die anderen. Taste 6 wirkt wie G (halten lädt den Wurf, Loslassen wirft, H wechselt die Art); G bleibt.
- Nur die Oberfläche und die Tasten ändern sich, das Netzprotokoll bleibt (NET_VERSION 44).

## Netz: Snapshots komprimiert gegen Hamachi-Timeouts (2026-10-23)
**NET_VERSION 44**: alle müssen aktualisieren. Auswertung der Logs von Host und Client: Ein Snapshot ist ~8 KB und geht 30-mal pro Sekunde
(~2 MBit/s je Mitspieler) unkomprimiert durch Hamachi. Die Leitung staute sich ständig, nach rund einer Minute kam vom Host gar nichts mehr
an, und nach 30 s gab es die Zeitüberschreitung.
- GEÄNDERT Nachrichten ab 600 Byte (praktisch nur Snapshots) gehen als `Z` + base64(zlib(JSON)) (`pack_line`/`unpack_line`); kleine bleiben lesbar.

## Robins Patches 13a-13d und 13f in allen Modi, feste Tomahawk-Säulen auf der Kreisstraße (2026-10-23)
Alles gilt für KotH, DM, CTF und Experimental gleichermassen. Nicht übernommen: 13e (zerstörbare Umgebung) und alles zu
Baumwachstum/-hitbox, Baumfällen und zertrampelten Zäunen. **NET_VERSION 43**: alte Clients können nicht mehr beitreten.
- NEU **13a Granaten-Beute**: Monster haben eigene Granaten-Pools (`MOB_GREN_W`) und sichere Granaten-Teile (`MOB_GREN_SURE`): Zombies/Jägerin Standardgranaten, Brute mehr Drohnen/Airdrop-Fackeln, Koloss und Titan am meisten; mehr Beute von Zombies/Jägerin/Brute/Koloss (`MOB_LOOT`).
- NEU **13a Tomahawk-Radar**: steht die Säule 5 min unbenutzt, zeigen Minimap und Karte (M) einen gelben Suchkreis (120 m, nach je 1 min halbiert), zuletzt einen Pin genau auf der Säule (`TOMA_RADAR_*`, Netz: Feld `rd` in `tb`).
- GEÄNDERT **Feste Säulenorte auf Polytown**: acht Punkte auf der Kreisstraße um die Burg (55 m um die Kartenmitte, alle 45 Grad, `TOMA_SPOTS`); um jeden Ankerpunkt sucht `build_toma_spots_fixed` den nächsten freien, ebenen Platz. Andere Karten wählen die Orte weiter automatisch.
- NEU **13b Geräusch-Pathing**: Geräusch/Schütze weiter als 40 m: erst bis 20 m heran, dann genau auf den Punkt; getroffene Monster laufen exakt zum Schützen. Zombie/Brute/Jägerin erkennen Festhängen und nehmen Umwege. Der Titan steigt über freistehende niedrige Objekte (Zäune, Bänke, Schilder; `TITAN_LEG_H`).
- NEU **13c Jet-Strike-Granate** (nur vom Titan, 1-3 Stück): rote Rauchfackel, ein Jet wirft eine Bombe ab, 15 m Radius, im Zentrum tödlich. **Lebensbalken** der Monster blenden nach 1,5 s selbst aus.
- NEU **13d Lila Drohne**: 5 min Lebensdauer, zerstört feindliche Drohnen im Umkreis (ohne Beute), betäubt Titan/Koloss nah am Besitzer; Drohnen-Kästchen mit Uhrzeiger unten rechts.
- NEU **13f Boss-Zyklen**: Kolosse und Titanen kommen erst wieder, wenn der letzte seiner Art tot ist, und buddeln sich dann nacheinander am Kartenrand aus (unverwundbar). Wegsuche per A* um Aussenwände zur Tür, wenn das Ziel im Gebäude liegt. Titan-Mörserwurf im hohen Bogen über Dächer (Bück-Animation). Höchstens eine lila Drohne im ganzen Spiel, weitere Granaten frischen die Zeit auf; die Abwehrdrohne gibt es nicht mehr als Beute (alte Granaten starten die lila Drohne).
- GEFIXT Raketenwerfer-Treffer auf Fahrzeuge: kein Absturz mehr (Trefferquader von Fahrzeug/Heli kennen das Zaun-Flag `clip`).
- GEFIXT Drohnen-HUD fängt ein Modell ohne Ausdehnung ab.

## Neue Runde mit Ausrüstungswahl, Schaden und Netz modusunabhängig (2026-10-23)
- GEÄNDERT Nach dem Rundenende landen alle Spieler beim Start der nächsten Runde im Ausrüstungsmenü und drücken selbst auf Spawn (Experimental: Pistole, ebenfalls mit Spawn-Knopf).
- GEFIXT Die Maus bleibt im Rundenende-Menü sichtbar.
- GEÄNDERT Schadensmodell: Eigenbeschuss-Sperre hängt nicht mehr am Modus, sondern nur an Teams (`allied`). Sonst gab es im Schadenscode keine Modusabfrage.
- GEÄNDERT Netz: Snapshot-Format, Rundenstatistik und Tomahawk-Meldungen sind für alle Modi gleich (CTF-Block immer enthalten, `tb` immer). **NET_VERSION 42**: alte Clients können nicht mehr beitreten.

## Tomahawk-Säulen in allen Modi, Experimental = Deathmatch mit Pistole (2026-10-23)
- GEÄNDERT **Experimental** ist ein eigener, gleichberechtigter Modus: Deathmatch, nur mit Pistolenstart. Die Untermodus-Wahl (KotH/DM) entfällt.
- NEU **Tomahawk-Säulen in KotH, DM, CTF und Experimental**: der Knopf im Kommandoraum samt Zeitwahl-Gerät ist entfernt. Eine Säule fährt an einem freien, ebenen Ort auf (Orte pro Karte automatisch aus den Startpunkten gewählt, auf Host und Mitspielern gleich; eine Karte kann sie mit `meta.toma` vorgeben), Ziel und Countdown wählt man auf der Zielkarte, wer auslöst ist 5 min gesperrt, danach fährt woanders eine neue hoch. CTF startet mit Tomahawk nun ebenfalls an.
- GEÄNDERT Gebirge kann in allen Modi bestiegen werden (`MTN_CLIMB`), Scoreboard-Werte und Netzmeldung der Säule sind modusunabhängig.

## Kein "Spiel im Spiel" mehr: ein Regelwerk für alle Modi (2026-10-22)
- GEÄNDERT `ExpWorld`, `ExpPlayer`, `ExpGame`, `ExpPlayerView`, `ExpSetupPage` und `ExpEndSetupPage` gibt es nicht mehr. Es gibt `World(..., exp=False)`, `Player`, `Game`, `PlayerView`; Experimental ist der Regelsatz `world.exp`. Der Klassentausch beim Start (`_pb_to_exp`, `_exp_autostart`, `_pb_back`) ist weg, Experimental startet im Menü wie jeder andere Modus (Untermodus KotH/Deathmatch: Modus nochmal anklicken).
- GEÄNDERT **Karte und Physik für alle Modi gleich**: Fahrzeug-Trefferboxen, Dach-Fix (kein Hängenbleiben auf Fahrzeugdächern), Sprengschaden mit Sichtlinie, Mob-/Turm-/Strike-Logik, Landebahn und Tunnel kommen aus dem Experimental-Stand.
- GEÄNDERT **Optik** der Fahrzeuge, des Helis und der Soldaten (inkl. sichtbarer Rüstung) aus Experimental ist jetzt überall.
- GEÄNDERT **Gadgets auf Taste 3** in allen Modi (Taste 5 entfällt). Gadget-Beute (C4, Claymore, Funkbake) und Buffs gibt es in allen Modi; Vorrat gehört dem Host.
- GEÄNDERT **HUD** in allen Modi einheitlich: Timer, Killfeed, Geräuschkarte, Ping, Kugelpfeifen, Tooltips, Loot-Debug, Tab-Übersicht und Tastenlegende.
- GEÄNDERT **Bonuskisten/-hasen** sind in allen Modi standardmäßig an und lassen sich in "Weitere Einstellungen" abschalten. `MAX_DROPS` ist überall 120.
- GEÄNDERT Netz: Der Client schickt keine Slots/Aufsätze mehr (der Host besitzt die Ausrüstung in allen Modi); Beitritt zu Experimental-Hosts läuft ohne Fensterwechsel; Karten-/Regelwechsel baut die Welt neu auf.
- Verhalten, das sich im Hauptspiel dadurch ändert: Heli sinkt mit Strg, Ereignisformate sind die von Experimental, Performance-Änderungen von Experimental gelten überall.

## Experimental-Ausrüstung in allen Modi, Gadgets als Beute in Experimental (2026-10-22)
- NEU **Alle Modi (KotH, DM, CTF):** Nahkampfwaffen, alle 8 Granatenarten, Rüstung (Helm/Torso/Füße mit Sets, Schild, zweite Chance), Brände (Molotow) und Rauchwolken, **Airdrops** (Fackel-Granate), **Heli-Abstürze** und Drohnen-Granaten gibt es jetzt auch in den anderen Modi – ausschließlich als Beute (Bonuskisten, Monster, Gefallene), nicht im Ausrüstungsmenü. Man startet unverändert mit seinem Loadout; dazu kommen 2 Splittergranaten pro Leben.
- NEU Bedienung (alle Modi): **4** = Nahkampfwaffe, **F** ohne etwas Benutzbares = Schnellschlag, **G** halten = Wurf aufladen, **H** / Mausrad bei gehaltenem G = Granatenart, Stromstoss-Taste für das Schild-Set; HUD mit Rüstungs-Kacheln, Schildbalken, Nahkampf-Karte und Granaten-Karte. Taste 3 öffnet ohne Gadget eine Spezialwaffe aus der Kiste.
- GEÄNDERT Der alte Messerschlag des Hauptspiels (F) ist durch das Nahkampf-System ersetzt (Start-Nahkampfwaffe = Messer wie in Experimental).
- GEÄNDERT Das Welt-Regelwerk dazu (Schaden/Rüstung, Granaten, Nahkampf, Rauch, Feuer, Airdrop, Heli-Crash, Beute) liegt jetzt in `World` und gilt für alle Modi; `ExpWorld` erbt es. Ebenso `PlayerView`, `update_weapon` und `fly_heli`.
- NICHT übernommen: **Tomahawk** (die alte Luftschlag-Mechanik des Hauptspiels bleibt unverändert, der Luftschlag *ist* der Tomahawk), Buffs (Fluchttier-Buff gibt es nur in Experimental).
- NEU **Experimental:** **C4, Claymore und Funkbake** als Beute: Bonuskisten (je nach Stufe 12–22 % als 4. Teil), Monster-Beute (neue Kategorie „Gadget“) und Gefallene lassen Stapel fallen (C4 x2, Claymore x2, Funkbake x1); Vorrat je Art bis 6, Taste **5** nimmt das Gadget in die Hand (weiter drücken wechselt die Art, danach wird weggesteckt), Rechtsklick stellt es auf, Linksklick zündet C4. Der Vorrat gehört dem Host (Ereignis `gadget`) und verfällt beim Tod (ein Stapel fällt evtl. als Beute).
- GEFIXT Experimental: **Bewegung der Ausrüstung** (Dash, Doppelsprung, Jetpack, Krallenhelm) lief seit dem Refactor nicht mehr (`exp_step_once` wurde nicht aufgerufen); `_step_once` ist jetzt eine einzige Funktion für alle Modi.
- GEFIXT Experimental: Hinweistext beim Aufheben von Granaten-Stapeln („Waffe aufheben: Railgun“).
- GEÄNDERT Netz: Stapel-Drops tragen jetzt auch `gad:<Art>` (Index in `DROP_GK`).

## Refactor: alles in einer spiel.py (2026-10-22)
- GEÄNDERT `experimental/robin_experimental.py` gibt es nicht mehr. Robins Regeln stecken in `spiel.py` in den Klassen/Konstanten mit Präfix `Exp` / `EXP_` / `exp_` (ExpGame, ExpWorld, ExpPlayer, EXP_WEAPONS ...) und gelten nur im Modus Experimental.
- GEÄNDERT Monster (alle 9 Arten inkl. Drohnen, Koloss, Titan) sind jetzt in **allen** Modi (KotH, DM, CTF, Experimental) Robins Version; die alten Hauptspiel-Monster sind entfernt.
- GEÄNDERT Netzwerk ist vereinheitlicht: ein Protokoll (`NET_VERSION`), der Host meldet mit `exp`, ob Experimental läuft; `EXP_NET_VERSION` entfällt.
- GEÄNDERT Grafik, Texturen und Karte kommen vom Hauptspiel; Robins Waffen-/Granaten-/Nahkampfmodelle bleiben in Experimental.
- Änderungen an Robins Regeln künftig direkt in den `Exp*`-Teilen von `spiel.py`.

## Drohnen fliegen nicht mehr durch Gebäude und Wände (2026-10-21)
- GEFIXT Alle Drohnen (Elektro-, Spieler- und Abwehrdrohne) werden jetzt von Wänden und Gebäuden (Quader und Karten-Kollision) gestoppt (`push_out(..., air=True)` mit der Flughöhe der Drohne). Über Dächern, Bäumen und Fahrzeugen fliegen sie weiterhin frei. Hängen sie an einer Wand fest, suchen sie wie Titan/Koloss einen Umweg.

## CTF-Regelseite vor dem Start, Flugzeug-Kollision, Burgruine, Vorschaubild (2026-10-21)
- GEÄNDERT **CTF (Hauptspiel):** Bei Capture the Flag erscheint nach „Start“ zuerst die Seite „CTF-Regeln“ und muss bestätigt werden („Spiel starten“ / Enter; „Zurück“ / Esc bricht ab). Der Knopf „CTF-Regeln“ im normalen Menü und die Taste C entfallen. Ausserdem: CTF-Logik läuft jetzt wirklich im Spielschritt, Einzelspieler bekommt ein Team.
- GEFIXT Polytown: **Flugzeuge am Flugplatz sind fest** (Kollisionsboxen für Stuka und Jäger); Startpunkte liegen nicht darin.
- GEÄNDERT Polytown: Der Ring prismenartiger Felsen um die Burgruine auf dem Hügel ist entfernt.
- GEÄNDERT Vorschaubild von Polytown: Perspektivansicht (Stadt, Burg, Flugplatz), aus den Kartendaten gerendert.

## Aufräumen: CTF ins Hauptspiel, Blood Gulch und alte Polytown gelöscht (2026-10-21)
- GEÄNDERT **Capture the Flag** ist jetzt ein Spielmodus des Hauptspiels (`spiel.py`, Modus „Capture the Flag“ im Host-Setup neben King of the Hill und Deathmatch) und steht nicht mehr in `robin_experimental.py`. Die CTF-Änderungen aus „Experimental 11“ sind aus dieser Datei entfernt (Modus, Flaggen, Teams, HUD, Seite „CTF-Regeln“, Netzfelder).
- GEÄNDERT **NET_VERSION 42 → 41** (CTF-Netzfelder entfallen); `EXP_NET_VERSION` in `spiel.py` ist wieder 41.
- GELÖSCHT **Blood Gulch** (Karte `maps/blood_gulch.json`, Vorschaubild, Menüeintrag).
- GELÖSCHT **Alte Polytown** (im Code erzeugte Standardkarte): Gebirgsring und Wasserfälle, grosse Karte mit Wäldern, Ortskern, Aussenposten, Tomahawk-Orte, lange Tunnel, Burggraben/Radarstation. Standardkarte ist ausschliesslich `maps/polytown.ptmap`; fehlt sie, meldet das Setup-Menü das. Eigene Karten (.json) und die Minecraft-Karte (.mcmap) laufen unverändert.

## Experimental 12-Performance-Optimierung: Performance-Analyse & Bottleneck-Fixes (2026-10-20)
- ANALYSE (cProfile, Einzelspiel Polytown, Spieler läuft + schiesst): Hauptlast war **nicht** die Grafik, sondern die Monster-Kollision. `push_out` lief für jedes Monster in jedem Bild über **alle ~1800 Props** der Karte (seit 10g dichterer Ort/Wald und Monsterdichte ×1,5) = ca. 63 % der Bildzeit. Dazu: `separate_mobs` prüfte alle Monster-Paare (n²), Kugeln prüften in jedem Teilschritt alle Monster, Drohnen/Hasen/Jägerin wurden bei jedem Spawn neu modelliert (20–30 ms Ruckler je Spawn, Koloss beim ersten Auftauchen >0,5 s).
- Messung je Bild (Logik + Darstellung, ohne GPU), vorher → nachher: **Mäßig (78 Monster) 21,6 → 2,7 ms**, **Viel (146) 41,8 → 3,6 ms**, **Gottlos (238) 74,6 → 7,0 ms**; Gefecht auf „Viel" (Minigun-Dauerfeuer + alle Granatenarten) **51,4 → 9,5 ms**; „Gottlos" bei 20 FPS **122,6 → 8,2 ms**.
- **Kein Monster-Limit**, keine geänderten Spielwerte: Monsterzahl, Tempo, Aggro, Schaden, Beute unverändert.
- NEU Kollisionsraster für feste Props (`World.solid_near`, `SOLID_GRID` 8 m): `push_out` (Monster, Spieler, Fahrzeuge, Heli-Ausstieg) und die Spawn-Prüfungen (Monster, Kisten, Tomahawk, Startpunkte) fragen nur noch Props in der Nähe ab. Ergebnis **bitgenau wie vorher** (20 000 Vergleichsfälle, 0 Abweichung).
- NEU **Staggered Updates** (Vorschlag übernommen, `update_mobs_staggered`): Monster näher als `MOB_LOD_R` 70 m an einem lebenden Spieler oder aktiv (jagt, greift an, geht einem Geräusch nach, alarmiert, getroffen, betäubt/geblendet, Knockback, frisch tot, Spieler-/Abwehrdrohne) rechnen jedes Bild. Ferne Monster im Leerlauf sind auf `MOB_LOD_DIV` 4 Gruppen verteilt und rechnen reihum – mit der aufgelaufenen Zeit (gleich schnell, gleich weit), spätestens alle `MOB_LOD_MAX_DT` 0,12 s.
- NEU Stillstand-Erkennung (`Mob.needs_check`): steht ein Monster (oder liegt tot), entfallen Kollision und Bodenabfrage (`MOB_STILL_EPS` 2 mm; ausser ein Fahrzeug ist näher als `MOB_VEH_NEAR` 8 m).
- GEÄNDERT `separate_mobs`: Raster (`MOB_SEP_CELL` ≥ 4 m) statt n × n – gleiche Paar-Reihenfolge wie vorher.
- GEÄNDERT `nearest_player`: Geländehöhe nur noch, wenn sie gebraucht wird (2 Abfragen weniger je Monster und Bild).
- GEÄNDERT Kugeln: Monster nahe der Flugstrecke eines Bildes werden einmal vorgemerkt (`BULLET_MOB_PAD` 0,5 m), die ~1-m-Teilschritte prüfen nur diese statt aller Monster.
- NEU Modell-Vorlagen (`_mob_tpl`): jede Monsterart wird einmal gebaut und danach nur kopiert (Spawn jetzt ~0,05 ms statt bis 30 ms; Aussehen identisch, geprüft). Alle Monster-Modelle werden im Ladebildschirm vorgewärmt (`prewarm_mob_models`, ~0,6 s mehr Ladezeit, dafür kein Hänger beim ersten Koloss/Titan).
- GEÄNDERT Darstellung: `MobView` zeichnet ein Monster nur neu, wenn es aktualisiert oder getroffen wurde; Blob-Schatten nur bis `SHADOW_R` 90 m (Titan & Co. weiter) und mit Boden-Cache; Wind (Bäume/Gras/Fahnen) gestaffelt in `WIND_BUCKETS` 2 Gruppen (60 FPS → 30 Hz Wackeln); liegende Partikel (Hülsen, Splitter) ruhen ohne Physik, Geländehöhe erst nach `PART_GROUND_STEP` 0,15 m Weg neu; Wurfbogen-Vorschau (G halten) nur bei Änderung neu berechnet (vorher ~1,5 ms jedes Bild).
- GEÄNDERT Ton: Wand-Dämpfung des Kontrollraum-Funks nur alle `SND_OCC_T` 0,1 s und nur, wenn er überhaupt hörbar ist (`SND_OCC_MIN_VOL`) – vorher jedes Bild ein Strahltest durch alle Gebäudequader.
- Geprüft: KotH/DM/CTF auf Polytown, CTF Blood Gulch, Minecraft-Karte, Host-Modus; Monster jagen/greifen gleich oft an wie vorher (30-s-Test: 1 967 vs. 1 963 Angriffsbilder, 41 vs. 41 Treffer), kein Monster steckt in Props. Netz-Snapshot unverändert (238 Monster: 1,3 ms, 14 KB).
- Neue Tuning-Konstanten: `SOLID_GRID`, `SND_OCC_T`, `SND_OCC_MIN_VOL`, `MOB_STILL_EPS`, `MOB_VEH_NEAR`, `MOB_LOD_R`, `MOB_LOD_DIV`, `MOB_LOD_MAX_DT`, `MOB_SEP_CELL`, `SHADOW_R`, `WIND_BUCKETS`, `BULLET_MOB_PAD`, `PART_GROUND_STEP`.
- Protokoll unverändert gegenüber der Vorversion (NET_VERSION wurde später durch das Entfernen des CTF wieder 41, siehe oben).

## Experimental 10h: Gegner-Lärm auf der Minimap, Sichtkontakt, Set-Rahmen, Abwehrdrohne (2026-10-19)
- Minimap/Karte (M): die roten Gegner-Marker bei jedem Schuss entfallen. Stattdessen Lärm-Pings: lauter Lärm anderer Spieler – Schüsse (Radius je Waffe, `NOISE_SHOT` × Lautstärke), Granaten/Explosionen/Raketen, Blendgranate, Decoy, Geschütze, fahrende Wagen und fliegende Helis – erscheint als grober roter Kreis in der Grösse des Lärmradius. Die Mitte liegt zufällig versetzt (bis `ENEMY_PING_OFFSET` 0,85 × Radius), der Gegner ist immer irgendwo im Kreis. Gehen, Rennen, Ducken erscheinen nicht.
- Ping bleibt `ENEMY_PING_T` 3 s und blendet aus; höchstens ein Ping je Gegner alle `ENEMY_PING_CD` 3 s (Dauerfeuer füllt die Karte nicht). Kreise werden am Rand der Minimap abgeschnitten.
- Pings nur, wenn man im Lärmradius ist – also es hören könnte (`ENEMY_PING_HEAR_ONLY` = True, Lärm als Kugel in 3D wie bei den Monstern). Vorschlag aus dem Prompt so umgesetzt.
- Sichtkontakt: siehst du einen Gegner wirklich (freie Sichtlinie auf Kopf oder Körper, im Blickfeld `ENEMY_SIGHT_FOV` 100°, bis `ENEMY_SIGHT_R` 150 m, kein Rauch dazwischen), erscheint er als roter Punkt mit genauer Position – solange du ihn siehst, danach `ENEMY_SEEN_GLOW` 1,5 s Nachleuchten an der letzten Stelle. Geprüft wird `ENEMY_SIGHT_RATE` 10× pro Sekunde.
- Team-vorbereitet: Sichtungen werden pro Spieler gesammelt (`Game.sightings`: Beobachter -> Gegner) und mit allen Verbündeten geteilt (`World.allied`, derzeit nur man selbst); gehörte Pings ebenso (es reicht, wenn ein Verbündeter im Lärmradius ist). Team-Modi brauchen nur `team_of`.
- Neues Ereignis "lnoise" (Decoy, Geschütz); "shotpos" trägt jetzt Lärmradius und Höhe mit.
- Set komplett: zusätzlich zu den einfärbten Kacheln ein Rahmen in der eigenen Spielerfarbe um den ganzen Block der drei Ausrüstungs-Slots (pulsiert leicht; `SET_FRAME_W`, `SET_FRAME_PAD`).
- Neue Granate Abwehrdrohne (`guard`, 1 pro Beute; Beute-Gewicht gewöhnlich 0 / selten 8 / gold 14): setzt eine orange Drohne frei (eigenes Modell: oranger Rumpf, Leuchtring um die ganze Drohne, gelbe Kuppel, Mob "gdrone"). Sie umkreist den Besitzer (`GDRONE_ORBIT_R` 2,4 m, `GDRONE_ORBIT_H` 2,7 m hoch; im Heli über dem Heli) und greift keine Spieler und keine normalen Monster an.
- Kommt eine Monster-Drohne oder eine gegnerische Spieler-/Abwehrdrohne in `GDRONE_R` 15 m an den Besitzer (Drohnen, die ihn bzw. sein Fahrzeug/seinen Heli lahmlegen: 22,5 m), fliegt sie hin (`GDRONE_SPEED` 13 m/s) und zerstört sie per Stromschlag (oranger Blitz, ab `GDRONE_ZAP_R` 3 m, alle `GDRONE_ZAP_CD` 0,9 s). Der Kill zählt für den Besitzer (inkl. Beute der Monster-Drohne).
- Begrenzt: `GDRONE_LIFE` 60 s und `GDRONE_KILLS` 3 Abschüsse, erlischt auch beim Tod des Besitzers. Eigene/verbündete Kugeln gehen durch die eigene Abwehrdrohne hindurch.
- NET_VERSION 40 → 41 (neue Granatenart, neuer Mob, neues Ereignis) – Sinan muss `EXP_NET_VERSION` in spiel.py auf 41 setzen.

## Experimental 10g: Mehr Monster, Hasen im Wald, zwei Titanen mit Revier, Treffer-Ping, dichterer Ort und Südwestwald (2026-10-19)
- Monsterdichte ×1,5 (`MOB_LEVELS`): Wenig 0,6 / Mäßig 1,5 / Viel 3,0 / Gottlos 5,0 (vorher 0,4 / 1,0 / 2,0 / 3,5). Drohnen bleiben fest bei `DRONE_COUNT`, Titanen bei `N_TITAN`, Kolosse bei `MAX_COLOSSUS`.
- Gebirge: Spieler und Monster kommen höher hinauf – die unsichtbare Wand steht jetzt 1,0 m statt 4,0 m vor dem Kamm (`MTN_WALL`); die Grenze bleibt am Kamm.
- Hasen bleiben im Flachland: kein Schritt ins Gebirge (`CRITTER_MTN_MAX` = 0,4 m Gebirgshöhe) – sie sammeln sich nicht mehr in Ecken und an Hängen.
- Hasen wohnen in den Wäldern: spawnen in einem Wald, hoppeln dort umher, ziehen nach `CRITTER_STAY` (35–80 s) zu einem der nächsten Wälder und queren Ort/Felder dabei zügig (`CRITTER_TRAVEL_K` ×2,6). Auf der Flucht schlagen sie weiter Haken, aber grob Richtung nächster Wald, der nicht hinter dem Auslöser liegt (`CRITTER_FOREST_PULL`).
- Hase erlegt: zusätzlich zum Buff 1 Gegenstand der Stufe Gold (`MOB_LOOT["critter"]`; ersetzt "Fluchttier: keine Beute").
- Zwei Titanen (`N_TITAN` = 2) mit eigenem Revier (`TITAN_HOMES`): Titan A im Nordwest-Viertel, Titan B im Südost-Viertel bei der Landebahn (Bunker/Container). Ohne Aggro bleiben sie in ihrem Revier; ein nachspawnender Titan nimmt das freie Revier. Kolosse haben ein Revier um ihren Startpunkt (`COLOSSUS_HOME_R` 40 m).
- Lärm wie bisher. Angeschossen (Schütze bekannt): Titan/Koloss bekommen einen fast genauen Ping auf den Schützen (±`TITAN_PING_ERR` 5 m) – egal wie weit weg – und laufen ohne Pause hin, bis sie ihn sehen; finden sie niemanden, kehren sie in ihr Revier zurück. Andere Monster laufen zur Stelle des Schützen beim Schuss (±`MOB_HIT_POS_ERR` 7 m, ohne die alte 80-m-Grenze) und laufen danach friedlich frei umher.
- Wegzeit zum Geräusch/Ping begrenzt (`MOB_TRAVEL_K` 1,8 × Idealzeit + `MOB_TRAVEL_EXTRA` 10 s): hängt ein Monster an Häusern/Burgmauern fest, sucht es dort und gibt auf (vorher konnte ein Titan am Rathaus ewig hängen).
- Karte: Polytown wächst vom Marktplatz nach Nordosten (`town_northeast`) – neue Gasse mit zwei Häuserreihen (6 Häuser im Stil des Marktplatzes, innen Treppen/Möbel, einer mit Laden "KRAMLADEN", zwei mit Balkon); der Unterstand am Acker liegt jetzt im Hinterhof.
- Karte: Südwestwald grösser und viel dichter (420 statt 170 Bäume, engerer Abstand `BIG_FOREST_GAP_DENSE` 2,4 m) plus nördlicher Ausläufer (230 Bäume) und Unterholz (`BIG_UNDERGROWTH`, rund 500 Büsche) – Sichtdeckung überall; Felsformation, Hütte und Lichtungen bleiben frei.
- Geprüft: Spawnpunkte (34, keiner in Wänden), Tomahawk-Orte (20 wie vorher; "Acker beim Hof" lag in der neuen Gasse → jetzt "Wiese hinter dem Hof"), Monster-Spawns, Tunneleingänge. Aufbau der Welt mit Raster für die Waldbäume genauso schnell wie vorher.
- NET_VERSION 39 → 40 (Karte geändert: neue Häuser/Bäume) – Sinan muss `EXP_NET_VERSION` in spiel.py auf 40 setzen.

## Experimental 10f: Detaillierte Granaten, Fahrzeuge und Heli; keine Durchstecher; Ausrüstung ersetzt Kosmetik (2026-10-19)
- Granaten detailliert (`gren_mesh`): Splittergranate mit geriffeltem Gusskörper ("Ananas"), Zünder, Sicherungsbügel, Ring und Splint; Decoy (Messingdose mit Lautsprechergitter, LED, Antenne); Blend (Alu-Zylinder mit Lochreihen); Rauch (Kanister mit Farbband, Aufschrift, Abströmlöchern); Drohnen-Granate (Kugel mit angelegten Rotorarmen, Kamera, Leuchtring); Molotow (Flasche mit Schulter, Benzin, Etikett, eingestopftem und abgebundenem Lappen); Airdrop-Fackel (Stab mit Griffrillen, Ringen, Zündkappe). Gilt in der Hand (Ego + Wurfanimation), im Flug/am Boden, an Mitspielern und bei Drops.
- HUD-Symbole der Granaten detaillierter (`gren_icon_mesh`: Riffelung, Zünder, Bügel, Ring, Lochreihen, Etikett/Lappen, Rotorarme).
- Geländewagen neu (`build_vehicle_model`, gleiche Masse): gefaste, gerundete Wanne (`bevel_box`), gewölbte Motorhaube mit Sicke, Kotflügel über den Rädern, runde Scheinwerfer mit Gittern, Blinker, Kühlergrill mit Lamellen, Türen mit Fugen und Griffen, Trittbretter, Rohr-Überrollbügel, durchscheinende Windschutzscheibe mit Rahmen, Armaturenbrett mit Lenkrad, gepolsterte Sitze, Reserverad, Kanister, Spiegel, Antenne, Abschlepphaken, Profilreifen mit Speichenfelgen.
- Helikopter neu (`build_heli_model`, gleiche Masse): aerodynamischer Rumpf aus Querschnitten, Cockpitverglasung mit Rahmen, Schiebetüren mit Fenstern und Laufschiene, zwei Turbinen mit Einlässen und Auspuff, verjüngter Heckausleger, Leitwerk mit Profil und Endscheiben, Rotorkopf mit Taumelscheibe, Blattgriffen und Steuerstangen, verjüngte Rotorblätter mit Warnspitzen, Heckrotor mit Getriebe, Kufen aus Rohren (vorn hochgebogen), Raketenbehälter mit Mündungen, Bug-Minigun mit sechs Läufen, Sensorkugel, Positionslichter, Antennen.
- Trefferzonen angepasst: statt grober Zylinder jetzt Quader im Fahrzeug-Koordinatensystem (drehen mit dem Kurs) – `VEH_HIT_BOXES` (Wanne + Überrollbügel; der Wagen war vorher zu breit und zu kurz), `HELI_HIT_BOXES` (Kabine, Heckausleger, Seitenleitwerk, Waffenträger, Kufen; der Heckausleger war vorher nicht treffbar, die Luft neben der Kabine schon). Gilt für Kugeln und für das Ankleben von C4 (Normale = getroffene Fläche). `vehicle_hit_t`.
- Kein Durchstechen: Vollbart dicker und weiter aussen, Kinn und Kiefer liegen komplett darin (Kinnpartie, Bart an den Wangen); Koteletten liegen am Kopf an (standen seitlich ab). Alle Kombinationen (Kopfbedeckung × Gesicht × Brille × Zubehör × Frisur, Weste × Rucksack) gerendert und geprüft.
- Ausrüstung ersetzt das Kosmetik-Teil: Kopf-Ausrüstung blendet die eigene Kopfbedeckung (inkl. Headset/Nachtsichtgerät) aus, Torso-Ausrüstung die eigene Weste und den Rucksack, Fuss-Ausrüstung die eigenen Stiefel – für Mitspieler genauso; nach dem Respawn (ohne Ausrüstung) ist das eigene Aussehen wieder komplett (`build_soldier` legt die Teile getrennt an, PythonTag "cos").
- Behoben: Effekte, Partikel und Leuchtspuren teilten sich als Instanzen dieselbe Lage (mehrere Explosionen/Blutspritzer/Leuchtspuren gleichzeitig lagen übereinander) – jetzt hat jede Instanz einen eigenen Knoten (`gren_inst`, `fx_spawn`, `add_particle`, Leuchtspuren).
- Charakter-Editor im Hauptmenü (spiel.py): gleiche Bart-Korrektur nötig – Nachricht an Sinan (siehe Abschluss).
- NET_VERSION bleibt 39 (keine Netzänderung).

## Experimental 10e: Granaten-Arsenal – 7 Arten, Wurf nach Haltedauer (2026-10-19)
- NEU Wurfweite nach Haltedauer: G halten lädt den Wurf auf (Ladebalken unter dem Fadenkreuz + gestrichelte Bogen-Vorschau mit Landering, berechnet mit der echten Granaten-Physik inkl. Abpraller), loslassen wirft. Kurz getippt (< `GREN_TAP_T` = 0,15 s) = kurzer Wurf. Tempo `GREN_SPEED_MIN` 8 bis `GREN_SPEED_MAX` 31 m/s (vorher fest 21 m/s ≈ 30 m, jetzt bis ca. 65–70 m), voll nach `GREN_CHARGE_T` = 1,0 s.
- NEU Mehrere Granatenarten im Inventar (`GREN_KINDS`, je Spieler `pl.gren` = Anzahl je Art). Art wechseln mit **H** (`GREN_KEY_NEXT`) oder **Mausrad bei gehaltenem G**. HUD-Kachel zeigt Symbol + Name + Anzahl der gewählten Art, darüber die übrigen Arten; Legende (Tab) ergänzt.
- Eigene, unterscheidbare Formen/Farben je Art (Welt, Hand/Ego, Mitspieler, Drops, HUD-Symbol): `gren_mesh`, `gren_icon_mesh`. In der Ego-Ansicht hält man die Granate beim Laden sichtbar rechts unten (Molotow mit brennendem Lappen), Mitspieler sehen die gehaltene Granate ebenfalls.
- Beute (Monster, Kategorie "Granaten"): Art nach Stufe `GREN_LOOT_W`, Stückzahl je Art `GREN_LOOT_N`: Decoy 3, Splitter 2, Blend 2, Rauch 2, Drohne 1, Molotow 2, Airdrop-Fackel 3. Tod: statt "Granaten" fällt EINE der getragenen Arten (mit Anzahl).
- 1) Decoy: wirkt nach der Landung `DECOY_T` = 6 s, `DECOY_SHOTS` = 9 "Schüsse" (Sturmgewehr/Pistole/MP/Schrot-Ton) mit `DECOY_NOISE` = 80 m Lärmradius → Monster laufen hin. Kein Schaden.
- 2) Splittergranate: Schaden wie bisher (`GREN_R`, `GREN_DMG`, `GREN_KILL_R`), 2 zum Start.
- 3) Blendgranate (`FLASH_*`): Wirkung bis `FLASH_R` = 10 m, nur mit freier Sicht (keine Wand/Decke dazwischen). Stärke aus Abstand und Blickrichtung: je näher, desto weniger zählt die Blickrichtung; je mehr man hinschaut, desto stärker. Volle Wirkung `FLASH_FULL_T` = 5 s: die ersten `FLASH_WHITE_T` = 2 s reines Weiss, dann blendet es langsam aus und man sieht ein verschwommenes Nachbild/erste Konturen. Ton dumpf (`FLASH_MUFFLE` = 85 % leiser) + Pfeifton. Monster in Reichweite: `FLASH_MOB_T` = bis 4 s orientierungslos (taumeln, sehen und hören nichts, greifen nicht an).
- 4) Rauchgranate (`SMOKE_*`): Wolke ca. `SMOKE_R` = 6 m Radius, `SMOKE_T` = 20 s (Aufbau 2 s, Auflösen 4 s). Ausbreitung über ein 3D-Raster nur bei freier Sicht von Zelle zu Zelle (`smoke_cells`): im Tunnel bleibt sie im Tunnel, oben kommt sie nicht hinein; in (fast) geschlossenen Räumen füllt sie den Raum und tritt nur an Türen/Fenstern anteilig aus (Volumen begrenzt, Weglänge `SMOKE_PATH_K`). Blockiert die Sicht: optisch (dichte Wolke) und für Monster (ab `SMOKE_BLOCK_M` = 1,4 m Rauch auf der Sichtlinie keine Sicht, auch kein Drohnen-Stromstoss). Jeder Rechner errechnet die Wolke selbst (gleiche Welt → gleiche Wolke).
- 5) Drohnen-Granate: setzt eine eigene, lila Spieler-Drohne frei (Mob `pdrone`, eigenes Modell mit hellem Leuchtring, lila Blitz). Wie die Monster-Drohne, aber langsamer (3,6 statt 5,5 m/s), seltener Stromstösse (alle 11 statt 7 s), kürzer betäubt (`PDRONE_STUN` 0,8–1,6 s), weniger Reichweite (15 m) und Leben (25 HP), kein Schaden; greift nie ihren Besitzer (bzw. später Verbündete) an. Lebensdauer `PDRONE_LIFE` = 35 s, abschiessbar, keine Beute, zählt nicht als Monster.
- 6) Molotow (`MOLO_*`): sichtbar angezündet (Hand, Flug). Zerschellt beim ersten Aufprall; brennt `MOLO_T` = 5 s auf ca. 5 m Fläche (`MOLO_R` = 2,5 m), `MOLO_DPS` = 24 Schaden/s (Spieler und Monster). Brennt nur auf der Ebene des Aufpralls (Dach bleibt Dach, nichts durch Ebenen/Tunnel, nicht durch Wände). Im Wasser: keine Wirkung (nur Platschen).
- 7) Airdrop-Fackel (`AIR_*`, 3 Stück je Beute): Wurf setzt eine rote Leuchtfackel mit rotem Rauch. Nach `AIR_PLANE_DELAY` = 4 s fliegt ein Frachtflugzeug (für alle sichtbar und hörbar, `AIR_PLANE_ALT` = 105 m) über die Karte und wirft an der Fackel eine Kiste am Fallschirm ab (`AIR_FALL_V` = 5,5 m/s). Die Kiste sieht neutral aus (Versorgungskiste, "F Versorgungskiste öffnen"); je Satz von drei Fackeln bringt eine eine braune, eine eine blaue, eine eine goldene Kiste (zufällige Reihenfolge, `pl.flare_q`). Inhalt wie die alten Kisten (3 Teile vor dem Öffnenden), Kisten-Logik aus 10b (`CRATES_ON_MAP`-Code) wiederverwendet; Airdrop-Kisten werden nach dem Öffnen nicht ersetzt.
- Alle Wirkungsbereiche in 3D und mit Wänden/Decken: Splitter (wie bisher `blast_los`), Blend (freie Sicht), Rauch (Ausbreitung), Molotow (Ebene + Sicht), Decoy (Lärmkugel).
- Neue Töne (selbst errechnet): Pfeifton, Feuer-Prasseln, Zischen (Rauch/Fackel), Frachtflugzeug, Glas, Sicherungsstift.
- Netz: Snapshot um Granatenart/-zustand, Rauch (`sm`), Feuer (`fi`), Airdrops (`ad`), Airdrop-Kisten-Flag, Drop-Granatenart und gehaltene Granate erweitert; neue Ereignisse `gren_inv`, `decoy`, `flash`, `smoke`, `molo`, `flare`, `airdrop`, `airland`, `pdrone`, `tempdown`.
- **NET_VERSION 38 -> 39** (Sinan: `EXP_NET_VERSION` in spiel.py auf 39 ziehen).

## Experimental 10d: Nahkampf – Effekte, Erschöpfungsklinge, Diebesdolch (2026-10-15)
- Katana-Rundumschlag: Beim Auslösen dreht sich die Figur einmal um sich selbst – in der Ego-Ansicht dreht die Kamera 360°, Mitspieler sehen die Figur rotieren. Ein weißer Slash-Ring breitet sich vom Spieler bis zum Schadensradius (`KATANA_SPIN_R`) aus und verblasst (`SLASH_FX_T` = 0,4 s). Laufen beim Aufladen bleibt.
- Schwert-Sprungangriff: Ein weißer Windstoß-Schnitt (Halbmond) fährt von oben nach unten durch den Trefferbereich vor dem Spieler. Beim Aufkommen quillt in der Mitte eine Staub-/Schockwelle auf und läuft nach links und rechts aus.
- Machete heißt jetzt "Erschöpfungsklinge" und hat die komplette Wirkung des bisherigen Erschöpfungsdolchs (Lebensraub 50 %, bei Spielertreffern deren Fähigkeiten auf Abklingzeit, eigene sofort bereit und ×2). Optik: dunkler Stahl mit glimmenden Runen, Ebenholzgriff mit Goldringen, Edelstein-Knauf. Werte und Loot-Anteile wie die Machete.
- Erschöpfungsdolch heißt jetzt "Diebesdolch" mit Schurken-Optik: schlanke, leicht gebogene Klinge, schwarzes Leder, Haken-Parierbügel, Ring-Knauf. Passiv: Monster damit erlegt = `THIEF_EXTRA` = 1 Gegenstand mehr aus einer weiteren, anderen Kategorie; gilt für alle Monsterarten, auch Fluchttiere.
- Hover-Infos zeigen die Besonderheit jeder Nahkampfwaffe. Damit hat jede Nahkampfwaffe ihre Eigenheit: Messer Start, Diebesdolch Beute, Erschöpfungsklinge Lebensraub/Erschöpfung, Schwert Sprungangriff, Katana Rundumschlag, Bratpfanne Essen.
- NET_VERSION 34 -> 35 (Waffennamen/Wirkung getauscht).

## Experimental 10c: Neue Sets – Zweite Chance, Jetpack, Springfeder; Hermes stärker (2026-10-15)
- Neues Set "Zweite Chance" (`second`), Stahl mit roten Streifen. Jedes Teil rettet einmal vor tödlichem Schaden: man überlebt mit `SAVE_HP` = 50 HP (vorher 10), das Teil zerbricht mit Hinweis.
  - Basic-Helm (Kopf): Kopftreffer.
  - NEU Splitterweste (Torso): normaler Schaden – Kugeln, Nahkampf, Monster, Überfahren.
  - NEU Druckwellen-Stiefel (Füße): Explosionen – Granate, Rakete, Heli-Rakete, Flak, C4, Claymore, Fahrzeug.
  - Set-Bonus: Ein tödlicher Tomahawk-Treffer wird überlebt (50 HP), dafür zerbricht die gesamte Ausrüstung.
- Hermes-Set stärker: Tempo `HERMES_SET_SPEED` 1,5 -> 1,6. Dash im Set doppelt so weit (`HERMES_SET_DASH_DIST` = 2, 15 -> 30 m) und 15 % schneller (`HERMES_SET_DASH` 2,0 -> 2,3). Gleiten mit gehaltenem Shift 30 -> 60 m (`HERMES_GLIDE_MAX`). Einzelteile wie bisher.
- Neues Jetpack-Set (`jet`), Orange/Alu:
  - Jetpack (Torso): halber Tank (`JET_PACK_SHARE`).
  - NEU Jet-Helm (Kopf): +50 % Treibstoff (`JET_HELM_SHARE`), zusammen ein voller Tank.
  - NEU Jetpack-Stiefel (Füße): kein Fallschaden.
  - Set-Bonus: Tank ×1,5 (`JET_SET_FUEL`), steigen und sinken ×1,6 (`JET_SET_SPEED`); waagerecht bleibt es langsam.
  - Steuerung: Leertaste in der Luft halten = steigen, Strg = sinken. Das Jetpack gibt keinen Doppelsprung mehr.
- Neues Springfeder-Set (`spring`), Grün mit Stahlfedern:
  - Springfeder-Schuhe (Füße): Sprung 1,5-mal so hoch (`SPRING_JUMP` 1,55 -> 1,2247 Sprungtempo).
  - NEU Sprungweste (Torso): Doppelsprung.
  - NEU Krallenhelm (Kopf): Läuft man in der Luft gegen eine Wand, krallt man sich fest und rutscht langsam herunter (`CLING_SLIDE_V` = 1,2 m/s). Das Kratzgeräusch ist für alle hörbar und zählt als Lärm (`NOISE_CLING` = 18 m). Sprung und Doppelsprung sind wieder bereit; Leertaste stößt von der Wand ab.
  - Set-Bonus: kein Fallschaden (`SPRING_SET_NOFALL`).
- Jetzt 6 Teile je Slot. Neue Teile sind in Loot-Tabellen, Set-Affinität, Modellen, Symbolen, Hover-Infos und Set-Anzeige im HUD enthalten. Jetpack-Anzeige nach echter Tankgröße.
- Ausrüstungsteile:

  | Teil | Slot | Wirkung | Set | Set-Bonus |
  |---|---|---|---|---|
  | Basic-Helm | Kopf | rettet bei tödlichem Kopftreffer (50 HP) | Zweite Chance | Tomahawk überleben, ganze Ausrüstung zerbricht |
  | Splitterweste | Torso | rettet bei tödlichem normalem Schaden | Zweite Chance | ″ |
  | Druckwellen-Stiefel | Füße | rettet bei tödlicher Explosion | Zweite Chance | ″ |
  | Armeehelm / Plattenrüstung / Kampfstiefel | K/T/F | je +25 max. HP | Rüstung | +75 max. HP |
  | Schild-Helm / Schild / Schild-Stiefel | K/T/F | Schild 15/30/15 | Schild | Stromstoß (B) |
  | Hermes-Helm / -Weste / -Schuhe | K/T/F | Dash | Hermes | ×1,6 Tempo, Dash ×2 weit und ×2,3 schnell, 60 m gleiten |
  | Jet-Helm / Jetpack / Jetpack-Stiefel | K/T/F | +50 % Tank / Jetpack (50 % Tank) / kein Fallschaden | Jetpack | Tank ×1,5, steigen/sinken ×1,6 |
  | Krallenhelm / Sprungweste / Springfeder-Schuhe | K/T/F | an Wänden krallen / Doppelsprung / ×1,5 Sprunghöhe | Springfeder | kein Fallschaden |

- NET_VERSION 33 -> 34 (neue Teile, Zustand "krallt" im Snapshot/st).

## Experimental 10b: Beute von Monstern, Kategorie-Gedächtnis, Set-Affinität (2026-10-15)
- Verteilte Kisten pausiert: `CRATES_ON_MAP = False`. Der Kisten-Code bleibt erhalten (Airdrops in 10e).
- Jedes getötete Monster lässt Beute fallen, verteilt im Kreis um seine Stelle (`MOB_LOOT_R`). Die Teile fliegen sichtbar heraus und werden mit F aufgehoben; Name und Werte erscheinen beim Anschauen. Monster-Beute gehört 3 s dem Schützen und verschwindet nach `MOB_LOOT_LIFE` = 45 s.
- Kategorien (`LOOT_CATS`): Fernkampfwaffe, Nahkampfwaffe, Granaten, Ausrüstung, Aufsatz/Visier. Aufsätze sind eine eigene Kategorie.
- Seltenheit nach Monster (`MOB_LOOT`, nutzt die Kisten-Tabellen als Qualitätsstufe):

  | Monster | Stufe | Teile |
  |---|---|---|
  | Grunt, Jägerin | braun | 2, aus verschiedenen Kategorien |
  | Brute, Drohne | blau | 2, aus verschiedenen Kategorien |
  | Koloss | gold | 2, aus verschiedenen Kategorien |
  | Titan | gold | 6 – jede Kategorie mindestens einmal, keine Doppelten (ersetzt die goldene Titan-Kiste) |
  | Fluchttier | – | keine Beute, bleibt beim Buff |

- Granaten als Beute: Päckchen mit 1/2/3 Splittergranaten je Stufe (`LOOT_GREN_COUNT`). Neues Drop-Feld `gren` (im Snapshot), Ereignis "gren_n".
- Kategorie-Gedächtnis pro Spieler und Leben (`cat_mul`): Die gerade bekommene Kategorie ×0,55 (`LOOT_CAT_DOWN`), alle anderen ×1,18 (`LOOT_CAT_UP`), Grenzen 0,15–4 (`LOOT_CAT_MIN`/`MAX`). Grundgewichte in `LOOT_CAT_BASE`. Das bisherige Gedächtnis innerhalb einer Kategorie bleibt.
- Set-Affinität: Hebt man ein Set-Teil auf, steigen die Chancen der fehlenden Teile desselben Sets bei jeder weiteren Ausrüstungs-Beute stufenweise: ×(1 + `SET_AFF_STEP` × Stufe), `SET_AFF_STEP` = 0,5, höchstens `SET_AFF_MAX` = 6 Stufen. Ein Teil eines anderen Sets macht dieses zum neuen Ziel; das alte fällt zurück.
- Simulation (60 Läufe, Monster-Mix wie auf der Karte, man hebt nur Teile seines Sets auf): komplettes Set im Median nach 16,5 Kills (Mittel 16,9; 90 % nach 27). Ohne Affinität im Median 27.
- Waffen behalten ihre Aufsätze und ihr Visier beim Abwerfen, Tauschen und Tod; wer sie aufhebt, bekommt sie mit. Abnehmen über T ins eigene Lager.
- Tod: Es fallen genau zwei Dinge – die aktive Waffe (mit Aufsätzen; ist die Nahkampfwaffe in der Hand, diese) und EIN zufälliges weiteres Teil aus Nahkampfwaffe, Granaten und den getragenen Ausrüstungsteilen. Ersetzt die bisherige Regel.
- `MAX_DROPS` 40 -> 120.
- NET_VERSION 32 -> 33 (Drop-Format).

## Experimental 10a: Echte Höhe – Lärm-Kugeln, KotH-Burg mit Kontrollturm, Strg = sinken (2026-10-15)
- Lärm als Kugel statt Säule: `make_noise(x, y, r, z)` misst den Abstand zum Monster in 3D (Mitte des Monsters), Schalter `NOISE_SPHERE`. Gilt für alle Quellen: Schritte, Fahrzeuge, Heli (Höhe des Helis), Schüsse, Geschütze, Explosionen, Nahkampf und Sonderattacken, Stromstoß, Bodenschlag, Steinbrocken und Tomahawk. Ein hoch fliegender Heli alarmiert am Boden kaum noch etwas.
- Minimap: Der eigene Lärmkreis und die Wellen zeigen den Schnitt der Lärm-Kugel mit dem Boden (`noise_ground_r`). Hoch in der Luft wird der Kreis kleiner oder verschwindet.
- Monster erkennen Spieler mit dem 3D-Abstand (aggro). Ein Heli hoch über ihnen zieht sie nicht mehr an.
- King of the Hill (Polytown): Die Zone ist jetzt das Burg-Volumen (`koth_box`): innerhalb der Mauern, auf den Mauern, im Kontrollturm und im Tunnel darunter. Sie zählt nicht im Heli oder Fahrzeug (auch nicht am Wagen-Geschütz) und nicht in der Luft über der höchsten Ebene + `KOTH_ZONE_TOL` = 1 m (z. B. Jetpack-Flug). Bodenmarkierung und Minimap zeigen das Burg-Quadrat statt des Kreises. Karten ohne diese Burg nutzen weiter den Kreis `ZONE_R`.
- Neuer Kontrollturm in der Burgmitte statt Bergfried/Radarschüssel (`KOTH_TOWER`, `KT_*`):
  - massiver Betonsockel ohne Zugang;
  - zwei Stege mit Geländer von der Nord- und Südmauer (Wehrgang 5 m) zur Tür der mittleren Etage;
  - im Schaft eine eckige Wendeltreppe mit 16 Stufen zu 0,45 m um einen Mittelpfeiler;
  - auskragender Turmraum (8,4 × 8,4 m) mit 1 m Brüstung (geduckt volle Deckung), Fenstern rundum, Dach mit Antenne, Fahne und Kistenplatz.
  - Begehbarkeit per Test geprüft: Steg → Tür → Treppe → Turmraum.
- Weitere 3D-Prüfungen:
  - Explosionen (Granate, Rakete, C4, Claymore, Fahrzeug) schaden nicht mehr durch Wände und Decken (`blast_los`).
  - Koloss-/Titan-Bodenschlag mit 3D-Abstand und Deckung.
  - Kisten und Drops lassen sich nicht mehr durch Decken oder Wände benutzen.
- Bereits 3D und unverändert: Stromstoß, Nahkampf und Sonderattacken, Rülpser (Tonreichweite), Tomahawk-Säule, Fahrzeuge, Geschütze, Kugel-Vorbeiflug.
- Einheitliche Steuerung hoch/runter: Heli Leertaste = steigen, Strg = sinken (vorher Shift). Jetpack: Leertaste = steigen, Strg in der Luft = kontrolliert sinken (`JET_DOWN_V` = 4 m/s, kein Fallschaden). Legende angepasst.
- NET_VERSION 31 -> 32.

## Experimental 9d: Ausrüstung detailliert + Monster-Makeover (2026-10-15)
- Alle Ausrüstungsteile neu modelliert (`gear_model`): Helme mit gerundeter Schale, Rand, Kinnriemen und Nieten; Westen mit Brust-/Rückenplatte, Schulterstücken, Taschen und Gurten; Jetpack mit Tanks, Düsen und Steuerkasten; Stiefel mit Sohle, Schaft und Schnürung. Gilt für Drops am Boden und für getragene Teile an der Figur (gleiche Maße wie vorher).
- Sets optisch zusammengehörig (`GEAR_LOOK`): Rüstungs-Set oliv mit Tarnband, Taschen und Schablonen-Nummer; Schild-Set dunkles Blaugrau mit leuchtenden Cyan-Linien, Visier und Generator-Kern; Hermes-Set Gold mit weißen Federflügeln. Basic-Helm stahlgrau, Jetpack orange/alu, Springfeder-Schuhe grün mit Stahlfeder.
- Neue Ausrüstungssymbole (`gear_icon`, Sinans Formsprache wie die Waffensymbole) in den HUD-Kacheln (mit kleinem Namen darunter) und in den Tab-Hover-Infos.
- Monster-Makeover, jede Art mit eigenem, detailliertem Modell:
  - Grunt: ausgemergelter, gebeugter Zombie mit zerrissenem, blutfleckigem Hemd, Rippen, hängendem Kiefer, einem greifenden und einem baumelnden Arm und einem nackten Fuß; schwankt beim Gehen.
  - Brute: massig, rote Haut, gebogene Hörner, Hauer, Stiernacken, riesige Arme mit Stachel-Armschienen, Lendenschurz.
  - Jägerin: schlank und tief geduckt, langer Zopf, Klingen-Finnen am Rücken, Maske mit glühenden Schlitzen, lange Krallen, Sprungbeine.
  - Koloss: Steinriese mit Felsplatten auf Brust, Schultern, Armen und Knien, glühenden Fugen und Felsbrocken-Fäusten.
  - Titan: Wald-/Berg-Riese mit Rindenhaut und Moos, Geweih aus Ästen, Wurzelbart, Bäumchen und Kristallen auf den Schultern, Kristallkern, langen Armen – ganz andere Silhouette als der Koloss.
  - Drohne: gerundeter Rumpf, Ausleger mit Rotorschutz-Ringen, Kamera-Auge mit Linse und LED, Elektro-Spulen mit Polen, Antenne, Positionslichter.
  - Hase: runder Körper, heller Bauch, Ohren mit rosa Innenseite, glänzende Augen, Schnurrhaare, Blume, lange Hinterläufe.
- Leistung: Die Geometrie wird je Art einmal gebaut und geteilt. Ab `MOB_LOD_DIST` = 45 m (bei großen Monstern × Größe) zeigt ein LODNode das alte einfache Modell, dessen Farben zum neuen Look passen. Animationen (Laufen, Ausholen, Bodenschlag, Tritt) laufen unverändert über Rumpf und Beine.
- Trefferzonen: Die Kopfzone (obere 22 %) passt zum sichtbaren Kopf – `hit_h` Grunt 1,78, Brute 1,85 × 1,55, Jägerin 1,62 (geduckt); Koloss, Titan und Drohne bleiben.
- NET_VERSION 30 -> 31 (Trefferhöhen).

## Experimental 9c: Nahkampfwaffen – neue Optik + Sonderfähigkeiten (2026-10-15)
- Alle Nahkampfwaffen neu und detailliert modelliert, in Sinans Formsprache (`MELEE_SHAPES`): Klingen mit Rücken/Schneide-Fase, Hohlkehle, Parierstange, gewickelte Griffe, Knäufe, Nieten; Pfanne mit Boden, Kochfläche, Rand, Stiel und Holzgriff. Dieselben Formen ergeben Ego-Ansicht, Modell an Mitspielern, Drop und das neue HUD-Symbol (`melee_icon`). `MELEE_PARTS` entfällt.
- Kampfmesser heißt jetzt "Erschöpfungsdolch" (`DAGGER_NAME`): Ritualdolch mit gewellter Klinge, leuchtenden Runen, Ebenholzgriff mit Goldringen und Edelstein-Knauf. Loot-Tabelle umbenannt, Werte gleich.
- Erschöpfungsdolch, Lebensraub: jeder Treffer (Monster und Spieler) heilt den Träger um 50 % des verursachten Schadens (`DAGGER_LEECH`), höchstens bis Max-HP.
- Erschöpfungsdolch, Treffer an Spielern: Beim Getroffenen gehen Dash, Stromstoß und Jetpack (Tank leer) auf volle Abklingzeit; laufendes Essen bricht ab, und er kann `DAGGER_PAN_LOCK` = 8 s nicht essen.
- Erschöpfungsdolch, Angreifer: Seine Fähigkeiten sind sofort bereit. Der nächste Einsatz jeder Fähigkeit wirkt x2 (`DAGGER_AMP`), solange er innerhalb von `DAGGER_AMP_T` = 20 s kommt: Dash doppelt so weit, Jetpack mit doppeltem Schub, Stromstoß mit doppeltem Radius und doppelter Betäubung, Pfanne heilt doppelt. Der HUD zeigt "x2 bereit".
- Katana: Schlagtaste `MELEE_CHARGE_T` = 3 s halten (Ladebalken, Ton, Zittern), dann loslassen = Rundumschlag im Umkreis `KATANA_SPIN_R` = 2 m mit `KATANA_SPIN_MULT` = doppeltem Schaden. Ein kurzer Klick bleibt ein normaler Schlag (`MELEE_HOLD_START` = 0,3 s).
- Schwert: 3 s halten = Sprungangriff mit `SWORD_JUMP_H` = 1,5-facher Sprunghöhe und einem Satz von `SWORD_LEAP` = 1,5 m nach vorn, ohne Fallschaden. Beim Aufkommen trifft es alles bis `SWORD_SLAM_R` = 5 m vor einem (±`SWORD_SLAM_ARC` = 50°) mit doppeltem Schaden (`SWORD_SLAM_MULT`), dazu Staubwelle und Kamerastoß.
- Bratpfanne, Laden: Kills mit der Pfanne bringen Punkte (`PAN_POINTS`: Grunt 1, Fluchttier 1, Brute 2, Jägerin 2, Drohne 2, Koloss 5, Titan 10, Spieler 3; höchstens `PAN_MAX_PTS` = 10).
- Bratpfanne, Essen sichtbar: Die Pfanne füllt sich mit Bacon, Spiegeleiern, Steak, Pommes und Pizza (`FOOD_SHAPES`), je mehr Punkte, desto voller; auch bei Mitspielern sichtbar.
- Bratpfanne, Essen mit T: Stufe 1 ab 3 Punkten (2 s, +15 HP/s), Stufe 2 ab 6 (3 s, +20 HP/s), Stufe 3 ab 10 (5 s, je Sekunde ein Bissen mit Kaugeräusch, +20 HP, danach Rülpser); Werte in `PAN_STAGES`. Die Heilung geht höchstens bis Max-HP.
- Bratpfanne, beim Essen: kein Angriff, kein Waffenwechsel, nur langsames Gehen (`PAN_EAT_SPEED`). Die Ladung ist danach 0 und geht beim Tod oder beim Wechsel der Nahkampfwaffe verloren.
- Bratpfanne, Rülpser: nur für Spieler im Umkreis `PAN_BURP_R` = 20 m hörbar, kein Lärm für Monster.
- Bratpfanne, HUD und Optik: Der HUD zeigt die Stufe und die Punkte bis zur nächsten Stufe an der Nahkampf-Kachel. In der Ego-Ansicht ist die Pfanne zur Kamera gedreht (`PAN_FP_ROLL`).
- Bratpfanne, Schalter `PAN_STAGE3_ONLY_GRUNTS` (Startwert False): Bei True zählen über Stufe 2 hinaus nur noch Grunt-Kills.
- Tasten-Legende und Mausover-Infos um die Sonderfähigkeiten ergänzt. T mit Katana/Schwert zeigt einen Hinweis.
- Multiplayer: Der Host entscheidet über Treffer, Heilung, Ladung und Essen. Neue Client-Nachrichten "mspec" und "eat", neue Ereignisse "pan", "eat", "bite", "burp", "leech", "drain", "mspec". Animationen (Rundumschlag, Aufschlag, Essen) und Töne sind bei allen sichtbar und hörbar.
- NET_VERSION 29 -> 30.

## Experimental 9b: Drohnen, Waffen-Mods auf T, Tomahawk-Sound (2026-10-15)
- Drohnen: feste Anzahl statt anteilig zur Monsterzahl – höchstens `DRONE_COUNT` = 4 gleichzeitig (jede Monsterdichte außer "Aus"); Respawn wie bisher, aber nie über `DRONE_COUNT`. `N_DRONE` wird nicht mehr verwendet.
- Drohnen 1,4-mal so groß (`DRONE_SIZE`): Modell (scale) und Trefferzone (hit_r 0,42 -> 0,59, hit_h 0,5 -> 0,7) mitskaliert.
- Neu: Taste T = Waffen-Inspektion (`INSPECT_KEY`). Die Waffe in der Hand wird von der Seite präsentiert; an Visier, Lauf, Magazin und Griff sitzen anklickbare, pulsierende Markierungen mit dem aktuellen Teil. Klick öffnet die passenden Aufsätze aus dem Aufsatz-Lager (Symbol, Name, Wirkung); Klick steckt auf, das Modell ändert sich sofort, "Standard" geht immer.
- Inspektion: T oder Esc schließt; Laufen bleibt möglich, Schießen/Zielen ist gesperrt. Bei einem Waffenwechsel folgt die Ansicht der neuen Waffe. Neue Werte: `INSPECT_FILL`, `INSPECT_FILL_V`, `INSPECT_LIFT`, `INSPECT_BLEND`, `INSPECT_SWAY`.
- T mit einer Nahkampfwaffe in der Hand ist für deren Fähigkeit reserviert (Bratpfanne, 9c).
- Tab ist wieder nur Scoreboard + Legende (Klick auf Waffen öffnet nichts mehr). Legende: "T – Waffe ansehen / Aufsätze".
- Tomahawk: Sirene/Warnton halb so laut (`TOMA_SIREN_VOL` = 0,275, vorher 0,55).
- Tomahawk: Während des Anflugs läuft leise eine selbst synthetisierte Instrumentalfassung von "The Star-Spangled Banner" (gemeinfreie Melodie; Blechbläser, Streicher, Trommelwirbel); sie endet mit dem Einschlag. Werte: `TOMA_ANTHEM`, `TOMA_ANTHEM_VOL` = 0,22, `TOMA_ANTHEM_BPM` = 92. Der Rodeo-Reiter bleibt unverändert.
- NET_VERSION 28 -> 29 (Drohnen-Größe/Trefferzone und Anzahl).

## Experimental 9a: Gelände, Baumkronen, Alpen + Wasserfälle (2026-10-15)
- Baumkronen, Büsche, Schilf und hohes Gras sitzen wieder auf der richtigen Höhe (Wind-Knoten fehlte die Bandhöhe zref – Kronen schwebten in Senken und versanken auf Hügeln; alle Baumarten).
- Nichts schwebt mehr: bodennahe Mauern, Zäune, Sandsäcke, Splitterschutz und Beete bekommen ein Fundament bis unter das Gelände (`ground_boxes`, `GROUND_ANCHOR_Z`, `GROUND_FOOT_SINK`, `GROUND_FOOT_MAX`); Sandsäcke folgen dem Gelände (`GROUND_FOLLOW_TOL`); Felsen sitzen am Hang talseitig auf.
- Keine Ritzen mehr im Gelände: Kanten zwischen fein (Wege, Graben, Tunneleingänge) und grob unterteilten Zellen werden angeglichen (`TERRAIN_FINE_K`); Schürze am äusseren Geländerand (`TERRAIN_SKIRT_Z`).
- Alpen: unterschiedlich hohe Gipfel (`MTN_PEAK_MIN/MAX`), Grate (`MTN_RIDGE`), Felsstufen (`MTN_TERRACE`, `MTN_TERRACE_K`).
- Höhen-Farbverlauf: Bergwald/Alm (`MTN_FOREST_Z`), Geröll, Fels mit Gesteinsschichten (`MTN_ROCK_Z`), Schnee ab `MTN_SNOW_Z` (an steilen Stellen dünner: `MTN_SNOW_STEEP`, `MTN_SNOW_THIN`); neue Texturen Schnee und Wasserfall.
- 3 Wasserfälle (`WATERFALL_COUNT`, max. 4; `WF_*`): Felsscharte mit Klippe, fallendes Wasserband, Gischt, Becken zum Waten, leises Rauschen (`WF_VOL`, `WF_RANGE`).
- Etwas weniger Nebel auf der Gebirgskarte (`MTN_FOG` 0.0085 statt 0.012), damit die Berge sichtbar sind.
- MTN_CLIMB / MTN_WALL unverändert.
- NET_VERSION 27 -> 28 (Gelände hat sich geändert).


## Neues Polytown überall (Merge von main)
- `main` in diesen Branch gemergt (neues Polytown aus Blender: `maps/polytown.ptmap`, Texturen, Rauch, Brücken, Dach-/Treppenkollision u. a.).
- Die Standardkarte ist im Experimental-Modus jetzt immer das neue Polytown. Die alte, im Code erzeugte 450-m-Karte wird nicht mehr gestartet (fehlt die Datei, kommt eine Fehlermeldung statt der alten Karte). Kartensuche findet `../maps/polytown.ptmap`.
- Beide Spiel-Stände (Autoräder von 10f bleiben, Versionsnummer 42 bleibt). Nur mit Attrappen getestet (Welt baut in Koth/DM/CTF), nicht gerendert.


## T-Menü, Aufsatz-Inventar und Beute in allen Modi
- Das T-Menü (Waffe inspizieren, Aufsätze wählen) und das Aufsatz-Inventar gibt es jetzt in allen Modi. Das Inventar ist beim Spawn leer und enthält nur Aufsätze; Waffen liegen weiter in den Slots unten.
- Das Bonuskistensystem aus dem Experimental-Modus gilt überall, das alte System ist gelöscht.
- Zombies und tote Spieler lassen Waffen und Aufsätze fallen (Aufsätze/Waffen mit ihren Aufsätzen und Visier).
- Neue Checkboxen unter "Weitere Einstellungen": Bonuskisten und Bonushasen an/aus (auch im Pausenmenü für den Host, wirkt ab der nächsten Runde). Standard: Kisten an (im Experimental-Modus aus), Hasen an.
- Experimental bleibt ein eigener Modus. Nur mit Attrappen getestet, nicht gerendert.
