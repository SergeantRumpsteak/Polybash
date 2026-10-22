# Polybash

Low-Poly-Partybox für lustige Abende (Panda3D, LAN-Multiplayer).

## Aufbau

```
Polybash/
├── spiel.py                          Das gesamte Spiel in einer Datei (alle Modi, auch Experimental)
├── experimental/
│   └── PATCHNOTES_experimental.md    Änderungsliste von Robins Modus
├── maps/                             Karten (.json, .mcmap; polytown.ptmap = Standardkarte aus Blender)
└── installer/                        Windows-Installer (Inno Setup)
.github/workflows/build-installer.yml baut den Installer auf GitHub (Actions)
```

## Wer ändert was

- Es gibt nur noch `Polybash/spiel.py`, und alle Modi laufen auf denselben Klassen (`World`, `Player`, `Game`,
  `PlayerView`): **Karte, Physik (inkl. Fahrzeug-Trefferboxen, Dach-Fix), Fahrzeug-/Heli-Optik, Waffen, HUD, Timer, Killfeed,
  Geräuschkarte, Ping, Kugelpfeifen, Tooltips und Loot-Debug sind in allen Modi gleich.** Es gibt kein "Spiel im Spiel" mehr.
- Modi sind Regelsätze: King of the Hill, Deathmatch, Capture the Flag (zwei Teams; Regeln beim Start auf eigener Seite)
  und **Experimental**. Experimental ist ein Flag der Welt (`World.exp`, im Menü wie jeder andere Modus anwählbar;
  nochmal anklicken wechselt zwischen King of the Hill und Deathmatch). Es gilt dort: Start und Respawn nur mit der Pistole
  (kein Ausrüstungsmenü), Tomahawk-Säulen statt Kommandoraum-Knopf, kein CTF.
- In **allen** Modi: Nahkampfwaffen (Taste 4 / F), alle Granatenarten (G halten, H wechselt), Rüstung, Brände, Rauch,
  Airdrops, Heli-Abstürze, Buffs (Fluchttier) und Gadget-Beute (C4 / Claymore / Funkbake). **Taste 3** = Gadget bzw.
  Spezialwaffe in jedem Modus. Bonuskisten und Bonushasen sind überall standardmäßig an und lassen sich vor Rundenbeginn
  unter "Weitere Einstellungen" aus- und einschalten.
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
