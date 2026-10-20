# Polybash

Low-Poly-Partybox für lustige Abende (Panda3D, LAN-Multiplayer).

## Aufbau

```
Polybash/
├── spiel.py                          Hauptspiel (Sinan)
├── experimental/
│   └── robin_experimental.py         Modus "Experimental" = Robins Spielversion
├── maps/                             Karten (.json, .mcmap; polytown.ptmap = Standardkarte aus Blender)
└── installer/                        Windows-Installer (Inno Setup)
.github/workflows/build-installer.yml baut den Installer auf GitHub (Actions)
```

## Wer ändert was

- **Sinan** ändert `Polybash/spiel.py` auf seinem Zweig.
- **Robin** ändert nur `Polybash/experimental/robin_experimental.py` auf seinem Zweig.
  Im Start-Menü steht "Experimental" gleichberechtigt neben King of the Hill und Deathmatch; `spiel.py`
  lädt dann diese Datei im selben Fenster: `spiel.py` wandelt die laufende Game-Instanz in Robins Klasse um
  (`_pb_switch`-Helfer: Tasks, Events und Szene des Menüs werden vorher abgeräumt; kein zweites Fenster, kein
  Neustart). "Zum Hauptmenü" ruft `POLYBASH_BACK` (von `spiel.py` gesetzt) und schaltet genauso zurück.
  Die anderen Modi sind davon nicht betroffen. Beitreten: im normalen "Spiel beitreten" erscheinen auch
  Experimental-Hosts; dafür muss `EXP_NET_VERSION` in `spiel.py` gleich `NET_VERSION` in Robins Datei sein.
  Robins Datei darf sich daher nicht auf `__main__` verlassen und `ShowBase.__init__(self)` nur in `Game.__init__` aufrufen.
  Im Heli ist die Rüstungsanzeige rechts ausgeblendet.
  Regel in Experimental: Alle starten und respawnen nur mit der Pistole, alle anderen Waffen kommen aus Kisten.
  Das Ausrüstungsmenü (Aufsätze, Visier, Gadget), Sounds und Spielmechaniken stammen aus `spiel.py`
  (Stand: v0.8, zusammengeführt) - bei Änderungen im Hauptspiel bitte gelegentlich in Robins Datei übernehmen.
- Spielmodi im Hauptspiel: King of the Hill, Deathmatch und Capture the Flag (zwei Teams, Flagge holen; die Regeln werden beim Start in einer eigenen Seite eingestellt), dazu "Experimental". Standardkarte ist `maps/polytown.ptmap`; die frühere im Code erzeugte Karte und Blood Gulch gibt es nicht mehr.
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

- Tasten in Experimental (Reihenfolge der Leiste): 1 Primär, 2 Sekundär, 3 Spezialwaffe (Kiste), 4 Nahkampf, G Granate; kein Gadget-Slot (am Start gibt es kein Gadget). Mausrad wechselt in dieser Reihenfolge. F schlägt immer mit der Nahkampfwaffe (Messer), nie mit der Schusswaffe.
