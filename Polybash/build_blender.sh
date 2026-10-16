#!/usr/bin/env bash
# Polybash - Blender-Karte bauen: holt den neuesten Stand, laesst das Skript die Karte erzeugen
# und oeffnet das Ergebnis in Blender.
#
#   ./build_blender.sh                       Polytown-Blockout
#   ./build_blender.sh pfad/zum/skript.py    anderes Blender-Skript (Pfad relativ zu diesem Ordner)
#   BLENDER=/pfad/zu/blender ./build_blender.sh   Blender-Programm von Hand angeben
cd "$(dirname "$(readlink -f "$0")")" || exit 1

SKRIPT="${1:-tools/blender/polytown/polytown_blockout.py}"
AUS="$HOME/blender_out"

fail() {
    echo
    echo "$1"
    read -r -p "Enter zum Beenden ..." _ 2>/dev/null
    exit 1
}

# 1. Neuesten Stand aus GitHub holen (nur in einem Git-Klon; ohne Netz einfach weiter)
if command -v git >/dev/null 2>&1 && git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "Hole neuesten Stand ..."
    git pull --ff-only || echo "Aktualisieren nicht moeglich - weiter mit dem vorhandenen Stand."
fi

# 2. Blender finden
if [ -z "$BLENDER" ]; then
    if command -v blender >/dev/null 2>&1; then
        BLENDER="$(command -v blender)"
    elif [ -x "$HOME/programs/blender-5.2.2-linux-x64/blender" ]; then
        BLENDER="$HOME/programs/blender-5.2.2-linux-x64/blender"
    else
        fail "Blender nicht gefunden. Entweder 'blender' in den Suchpfad legen oder BLENDER=/pfad/zu/blender setzen."
    fi
fi
[ -f "$SKRIPT" ] || fail "Skript nicht gefunden: $SKRIPT"

# 3. Karte erzeugen (Blender ohne Fenster)
echo "Erzeuge Karte mit $SKRIPT ..."
mkdir -p "$AUS"
LOG="$(mktemp)"
"$BLENDER" --background --python "$SKRIPT" -- "$AUS" 2>&1 | tee "$LOG"
if [ "${PIPESTATUS[0]}" -ne 0 ] || grep -q "Traceback (most recent call last)" "$LOG"; then
    rm -f "$LOG"
    fail "Das Skript meldet einen Fehler (siehe oben). Meldung bitte an Claude schicken."
fi
rm -f "$LOG"

# 4. Neueste .blend-Datei oeffnen
DATEI="$(ls -t "$AUS"/*.blend 2>/dev/null | head -n 1)"
[ -n "$DATEI" ] || fail "Keine .blend-Datei in $AUS gefunden."
echo "Oeffne $DATEI ..."
"$BLENDER" "$DATEI"
