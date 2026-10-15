# Patchnotes – Robins Experimental-Modus

Neueste Änderungen oben.

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

