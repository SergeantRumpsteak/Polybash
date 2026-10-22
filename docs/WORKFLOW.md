# Workflow: Sinan-Branch, Robin-Branch und main

Jeder entwickelt im eigenen Branch (`Sinan-Branch`, `Robin-Branch`). `main` ist das Hauptspiel und bekommt nur fertig
integrierte Staende, ausschliesslich als Fast-Forward (nie Force-Push, nie direkt auf main arbeiten).

## Ablauf, wenn eine Aenderung reif fuer main ist
1. `git fetch origin` und pruefen, ob `origin/main` neue Commits hat.
2. `git merge origin/main` im eigenen Branch (kein Rebase: die Branches liegen auf GitHub, Rebase braeuchte Force-Push).
3. Konflikte: dem Nutzer melden. Der Besitzer des Branches entscheidet; danach Merge-Commit.
   Feste Regeln fuer die Dauerbrenner:
   - `NET_VERSION`: den hoeheren Wert nehmen; haben beide das Protokoll geaendert, hoechster Wert + 1.
   - `BUILD`: egal welche Seite, wird im Release-Commit (Schritt 5) neu gesetzt.
   - `docs/PATCHNOTES.md`: beide Eintraege behalten, neueste oben.
4. Tests laufen lassen (ein konfliktfreier Merge heisst nicht, dass beide Aenderungen zusammen funktionieren).
5. Release-Commit fuer die Build-Nummer: `POLYBASH_BUMP=1 git commit --allow-empty -m "Release: Build hochzaehlen"`
   (der Hook `hooks/pre-commit` setzt dann `BUILD`; einmal pro Klon `git config core.hooksPath hooks`).
6. Nach Zustimmung des Nutzers: `git push origin <eigener-Branch>` und `git push origin <eigener-Branch>:main`.
   Wird der Push abgelehnt, hat der andere inzwischen gepusht: zurueck zu Schritt 1. Niemals `--force`.

## Regeln
- Jeder pusht nur in den eigenen Branch; auf `main` nur Fast-Forward und nur mit ausdruecklicher Zustimmung des Nutzers.
- Absprache, wer an welchem Bereich der (sehr grossen) `spiel.py` arbeitet, verringert Konflikte.
- Nach einem Push auf main sind beide Branches wieder gleich: der andere holt `main` per Merge, bevor er weiterarbeitet.
- Empfohlen: GitHub-Branch-Protection auf `main` (kein Force-Push, keine Loeschung).
