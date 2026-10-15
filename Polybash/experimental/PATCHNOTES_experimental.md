# Patchnotes – Robins Experimental-Modus

Neueste Änderungen oben.

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

