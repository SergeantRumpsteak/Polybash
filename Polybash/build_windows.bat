@echo off
setlocal
cd /d "%~dp0"
title Polybash
rem Doppelklick: richtet beim ersten Mal alles ein (Python-Umgebung + Panda3D) und startet das Spiel aus diesem Ordner.

if exist ".venv\Scripts\python.exe" goto install

set "PY="
for %%V in (3.12 3.11 3.10 3.9) do (
    if not defined PY (
        py -%%V -c "import sys" >nul 2>nul && set "PY=py -%%V"
    )
)
if not defined PY (
    python -c "import sys; sys.exit(0 if (3,9)<=sys.version_info[:2]<=(3,12) else 1)" >nul 2>nul && set "PY=python"
)
if not defined PY (
    echo Python 3.9 bis 3.12 wurde nicht gefunden.
    echo Bitte Python 3.12 installieren: https://www.python.org/downloads/windows/
    echo Beim Installieren "Add python.exe to PATH" anhaken, dann diese Datei nochmal doppelklicken.
    pause
    exit /b 1
)
echo Erstelle Python-Umgebung ...
%PY% -m venv .venv
if errorlevel 1 (
    echo Konnte die Python-Umgebung nicht erstellen.
    pause
    exit /b 1
)

:install
if exist ".venv\panda_ok.txt" goto run
echo Installiere Panda3D (nur beim ersten Start, 1-3 Minuten) ...
".venv\Scripts\python.exe" -m pip install --disable-pip-version-check "panda3d>=1.10.14,<1.11"
if errorlevel 1 (
    echo Installation fehlgeschlagen. Ist der PC online?
    pause
    exit /b 1
)
echo ok> ".venv\panda_ok.txt"

:run
echo Starte Polybash ...
".venv\Scripts\python.exe" spiel.py
if errorlevel 1 (
    echo.
    echo Das Spiel wurde mit einem Fehler beendet. Details: spiel_fehler.log
    pause
)
endlocal
