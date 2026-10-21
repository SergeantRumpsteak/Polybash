# Polybash

Low-Poly-Partybox für lustige Abende (Panda3D, LAN-Multiplayer).

## Aufbau

```
Polybash/
├── spiel.py                          Das gesamte Spiel in einer Datei (Hauptspiel + Modus "Experimental")
├── experimental/
│   └── PATCHNOTES_experimental.md    Änderungsliste von Robins Modus
├── maps/                             Karten (.json, .mcmap; polytown.ptmap = Standardkarte aus Blender)
└── installer/                        Windows-Installer (Inno Setup)
.github/workflows/build-installer.yml baut den Installer auf GitHub (Actions)
```

## Wer ändert was

- Es gibt nur noch `Polybash/spiel.py`. Robins Spielregeln stecken ausschließlich im Modus **Experimental**:
  Klassen, Konstanten und Funktionen mit Präfix `Exp` / `EXP_` / `exp_` (z. B. `ExpWorld`, `ExpPlayer`, `ExpGame`,
  `EXP_WEAPONS`). Sie erben vom Hauptspiel und überschreiben nur, was in Experimental anders ist.
- Gemeinsam für alle Modi (Robins Stand): **Monster** (Mob, MobView, Drohnen, Koloss, Titan ...) und **Netzwerk**
  (ein Protokoll, `NET_VERSION`; Host meldet per `exp`-Kennung, ob Experimental läuft).
  Gemeinsam (Stand des Hauptspiels): **Grafik, Texturen und Karte**.
- Nur in Experimental: Loot, Granatenarten, Nahkampf, Aufsätze, Buffs, Airdrops, Tomahawk-Säulen, Ausrüstungsanzeige.
- Experimental ist im Start-Menü gleichberechtigt: Die laufende `Game`-Instanz wird zu `ExpGame` umgewandelt
  (`_pb_to_exp`; Tasks, Events und Szene des Menüs werden vorher abgeräumt, kein zweites Fenster, kein Neustart).
  "Zum Hauptmenü" schaltet über `_pb_back` zurück. Beitreten: im normalen "Spiel beitreten" erscheinen auch
  Experimental-Hosts; das Fenster wechselt dann automatisch in den passenden Teil.
  Regel in Experimental: Alle starten und respawnen nur mit der Pistole, alle anderen Waffen kommen aus Kisten.
- Spielmodi: King of the Hill, Deathmatch und Capture the Flag (zwei Teams, Flagge holen; die Regeln werden beim Start in einer eigenen Seite eingestellt), dazu "Experimental" (King of the Hill bzw. Deathmatch nach Robins Regeln). Standardkarte ist `maps/polytown.ptmap`.
- `main` ist der Stand für alle Freunde. Zusammengeführt wird per Pull Request.
- Änderungen an Robins Regeln: in den `Exp*`-Teilen von `spiel.py` vornehmen, nicht im gemeinsamen Teil (Monster/Netz/Grafik),
  sonst ändert sich auch das Hauptspiel.

## Starten

- Linux: `python3 Polybash/spiel.py` (benötigt `panda3d>=1.10.14,<1.11`)
- Windows: Installer aus dem GitHub-Lauf "Polybash Installer bauen" (Actions → Artifacts)

## Hinweise zu Experimental

- Tasten in Experimental (Reihenfolge der Leiste): 1 Primär, 2 Sekundär, 3 Spezialwaffe (Kiste), 4 Nahkampf, G Granate; kein Gadget-Slot (am Start gibt es kein Gadget). Mausrad wechselt in dieser Reihenfolge. F schlägt immer mit der Nahkampfwaffe (Messer), nie mit der Schusswaffe.
