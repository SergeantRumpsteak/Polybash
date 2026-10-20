# Patchnotes – Robins Experimental-Modus

Neueste Änderungen oben.

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
