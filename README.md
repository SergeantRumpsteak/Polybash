# Polybash

Low-Poly-Partybox für lustige Abende (Panda3D, LAN-Multiplayer).

## Aufbau

```
Polybash/
├── spiel.py                          Hauptspiel (Sinan)
├── experimental/
│   └── spiel_experimental.py         Modus "Experimental" = Robins Spielversion
├── maps/                             Karten (.json, .mcmap)
└── installer/                        Windows-Installer (Inno Setup)
.github/workflows/build-installer.yml baut den Installer auf GitHub (Actions)
```

## Wer ändert was

- **Sinan** ändert `Polybash/spiel.py` auf seinem Zweig.
- **Robin** ändert nur `Polybash/experimental/spiel_experimental.py` auf seinem Zweig.
  Das ist ein eigenständiges Spiel: Im Menü wählt man den Modus "Experimental", dann startet `spiel.py`
  diese Datei als eigenen Prozess. Die anderen Modi sind davon nicht betroffen.
- `main` ist der Stand für alle Freunde. Zusammengeführt wird per Pull Request.

## Starten

- Linux: `python3 Polybash/spiel.py` (benötigt `panda3d>=1.10.14,<1.11`)
- Windows: Installer aus dem GitHub-Lauf "Polybash Installer bauen" (Actions → Artifacts)

## Hinweise für Robins Datei

- Sie darf auch allein gestartet werden: `python3 Polybash/experimental/spiel_experimental.py`
  (aus dem Ordner `Polybash` starten, damit `maps` gefunden wird).
- Einstellungen und Fehlerprotokoll liegen getrennt vom Hauptspiel
  (`spiel_einstellungen_experimental.json`, `spiel_fehler_experimental.log`).
- Beim Start aus `spiel.py` übergibt das Hauptspiel Name, Karte und Zeitlimit über die Umgebungsvariable
  `POLYBASH_EXP_SPEC`; ausgewertet wird sie in `_exp_autostart` am Dateiende. Diese Funktion bitte nicht entfernen.
