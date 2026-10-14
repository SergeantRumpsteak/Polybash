#!/usr/bin/env bash
# Doppelklick (Dateimanager: "Ausfuehren") oder ./build_linux.sh:
# richtet beim ersten Mal alles ein (Python-Umgebung + Panda3D) und startet das Spiel aus diesem Ordner.
cd "$(dirname "$(readlink -f "$0")")" || exit 1

fail() {
    echo
    echo "$1"
    read -r -p "Enter zum Beenden ..." _ 2>/dev/null
    exit 1
}

if [ ! -x .venv/bin/python ]; then
    PY=""
    for c in python3.12 python3.11 python3.10 python3.9 python3; do
        if command -v "$c" >/dev/null 2>&1 && "$c" -c 'import sys; sys.exit(0 if (3,9)<=sys.version_info[:2]<=(3,12) else 1)'; then
            PY="$c"; break
        fi
    done
    [ -n "$PY" ] || fail "Python 3.9 bis 3.12 fehlt. Ubuntu: sudo apt install python3 python3-venv python3-pip"
    echo "Erstelle Python-Umgebung ..."
    "$PY" -m venv .venv || fail "venv fehlgeschlagen. Ubuntu: sudo apt install python3-venv"
fi

if [ ! -f .venv/panda_ok.txt ]; then
    echo "Installiere Panda3D (nur beim ersten Start) ..."
    .venv/bin/python -m pip install --disable-pip-version-check "panda3d>=1.10.14,<1.11" \
        || fail "Installation fehlgeschlagen. Ist der Rechner online?"
    echo ok > .venv/panda_ok.txt
fi

echo "Starte Polybash ..."
.venv/bin/python spiel.py || fail "Das Spiel wurde mit einem Fehler beendet (Details: spiel_fehler.log)."
