# Patchnotes – Robins Experimental-Modus

Neueste Änderungen oben.

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

