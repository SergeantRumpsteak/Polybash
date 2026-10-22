# Polybash

Low-Poly-Partybox für lustige Abende (Panda3D, LAN-Multiplayer).

## Aufbau

```
Polybash/
├── spiel.py                          Das gesamte Spiel in einer Datei (alle Modi, auch Experimental)
├── maps/                             Karten (.json, .mcmap; polytown.ptmap = Standardkarte aus Blender)
└── installer/                        Windows-Installer (Inno Setup)
docs/PATCHNOTES.md                    Änderungsliste (neueste oben)
.github/workflows/build-installer.yml baut den Installer auf GitHub (Actions)
```

## Wer ändert was

- Es gibt nur noch `Polybash/spiel.py`, und alle Modi laufen auf denselben Klassen (`World`, `Player`, `Game`,
  `PlayerView`): **Karte, Physik (inkl. Fahrzeug-Trefferboxen, Dach-Fix), Fahrzeug-/Heli-Optik, Waffen, HUD, Timer, Killfeed,
  Geräuschkarte, Ping, Kugelpfeifen, Tooltips und Loot-Debug sind in allen Modi gleich.** Es gibt kein "Spiel im Spiel" mehr.
- Vier gleichberechtigte Modi: King of the Hill, Deathmatch, Capture the Flag und **Experimental**. Experimental ist
  Deathmatch, nur dass alle mit der Pistole starten und respawnen (kein Ausrüstungsmenü; alles Weitere kommt aus der
  Beute). Technisch: `World.exp` = Pistolenstart, `World.mode` = "dm". Keine Modus-Klasse steht über einer anderen.
- In **allen** Modi: Nahkampfwaffen (Taste 4 / F), alle Granatenarten (G halten, H wechselt), Rüstung, Brände, Rauch,
  **Tomahawk-Säulen** (Polytown: acht feste Orte auf der Kreisstraße um die Burg, steht die Säule lange unbenutzt, zeigt der Radar einen schrumpfenden Suchkreis; andere Karten wählen die Orte automatisch; es gibt keinen Kommandoraum-Knopf mehr), Airdrops, Heli-Abstürze, Buffs (Fluchttier) und Gadget-Beute (C4 / Claymore / Funkbake). **Taste 3** = Gadget bzw.
  Spezialwaffe in jedem Modus. Bonuskisten und Bonushasen sind überall standardmäßig an und lassen sich vor Rundenbeginn
  unter "Weitere Einstellungen" aus- und einschalten.
- Robins Patches 13a-13d und 13f (Granaten-Beute, Tomahawk-Radar, Geräusch-Pathing, Jet-Strike, lila Drohne, Boss-Zyklen,
  Wegsuche, Titan-Mörser) gelten ebenfalls in allen Modi. Ohne 13e (zerstörbare Umgebung, Baumwachstum).
- Netzwerk: ein Protokoll (`NET_VERSION`); der Host meldet per `exp`-Kennung den Regelsatz, die Ausrüstung gehört in allen
  Modi dem Host.
- `main` ist der Stand für alle Freunde. Zusammengeführt wird per Pull Request.
- Neue Regeln für einen Modus: über `world.exp` bzw. `world.mode` verzweigen, nicht Klassen duplizieren.

## Starten

- Linux: `python3 Polybash/spiel.py` (benötigt `panda3d>=1.10.14,<1.11`)
- Windows: Installer aus dem GitHub-Lauf "Polybash Installer bauen" (Actions → Artifacts)

## Hinweise zu Experimental

- Tasten (in allen Modi gleich): 1 / 2 Primär- und Sekundärwaffe, 3 Gadget bzw. Spezialwaffe, 4 Nahkampf, G Granate.
  Mausrad wechselt in dieser Reihenfolge. F schlägt ohne etwas Benutzbares mit der Nahkampfwaffe (Messer).
