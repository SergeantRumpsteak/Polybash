# Polybash

Low-Poly-Partybox für lustige Abende (Panda3D, LAN-Multiplayer).

## Aufbau

```
Polybash/
├── spiel.py                          Hauptspiel (Sinan)
├── experimental/
│   └── robin_experimental.py         Modus "Experimental" = Robins Spielversion
├── maps/                             Karten (.json, .mcmap)
└── installer/                        Windows-Installer (Inno Setup)
.github/workflows/build-installer.yml baut den Installer auf GitHub (Actions)
```

## Wer ändert was

- **Sinan** ändert `Polybash/spiel.py` auf seinem Zweig.
- **Robin** ändert nur `Polybash/experimental/robin_experimental.py` auf seinem Zweig.
  Im Start-Menü steht "Experimental" gleichberechtigt neben King of the Hill und Deathmatch; `spiel.py`
  wechselt dann im selben Fenster-Slot in diese Datei (das Menü beendet sich mit Code 77, ein kleiner Aufpasser
  in `spiel.py` startet Robins Version; "Zum Hauptmenü" beendet sie mit Code 78 und das Menü kommt zurück).
  Die anderen Modi sind davon nicht betroffen. Beitreten: im normalen "Spiel beitreten" erscheinen auch
  Experimental-Hosts; dafür muss `EXP_NET_VERSION` in `spiel.py` gleich `NET_VERSION` in Robins Datei sein.
  Im Heli ist die Rüstungsanzeige rechts ausgeblendet.
  Regel in Experimental: Alle starten und respawnen nur mit der Pistole, alle anderen Waffen kommen aus Kisten.
  Das Ausrüstungsmenü (Aufsätze, Visier, Gadget), Sounds und Spielmechaniken stammen aus `spiel.py`
  (Stand: v0.8, zusammengeführt) - bei Änderungen im Hauptspiel bitte gelegentlich in Robins Datei übernehmen.
- `main` ist der Stand für alle Freunde. Zusammengeführt wird per Pull Request.

## Starten

- Linux: `python3 Polybash/spiel.py` (benötigt `panda3d>=1.10.14,<1.11`)
- Windows: Installer aus dem GitHub-Lauf "Polybash Installer bauen" (Actions → Artifacts)

## Hinweise für Robins Datei

- Sie darf auch allein gestartet werden: `python3 Polybash/experimental/robin_experimental.py`
  (aus dem Ordner `Polybash` starten, damit `maps` gefunden wird).
- Einstellungen und Fehlerprotokoll liegen getrennt vom Hauptspiel
  (`spiel_einstellungen_experimental.json`, `spiel_fehler_experimental.log`).
- Beim Start aus `spiel.py` übergibt das Hauptspiel Name, Karte und Zeitlimit über die Umgebungsvariable
  `POLYBASH_EXP_SPEC`; ausgewertet wird sie in `_exp_autostart` am Dateiende. Diese Funktion bitte nicht entfernen.

- Tasten in Experimental: 1-3 Waffen (3 = Spezialwaffe), 4 Nahkampf, 5 Gadget, Mausrad wechselt durch alles.
