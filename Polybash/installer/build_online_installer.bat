@echo off
REM Baut dist\Polybash-Installer.exe (Online-Installer: laedt Python und Panda3D selbst nach).
REM Voraussetzung: Inno Setup 6.1 oder neuer  (https://jrsoftware.org/isdl.php)
REM Der Ordner "installer" liegt neben spiel.py und dem Ordner maps.
setlocal
title Polybash - Installer wird erstellt
cd /d "%~dp0"

if not exist "..\spiel.py" (
    echo FEHLER: ..\spiel.py nicht gefunden. Dieser Ordner muss neben spiel.py liegen.
    pause
    exit /b 1
)

set "ISCC="
if exist "%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles(x86)%\Inno Setup 6\ISCC.exe"
if exist "%ProgramFiles%\Inno Setup 6\ISCC.exe" set "ISCC=%ProgramFiles%\Inno Setup 6\ISCC.exe"
if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" set "ISCC=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not defined ISCC (
    echo FEHLER: Inno Setup 6 wurde nicht gefunden.
    echo Bitte von https://jrsoftware.org/isdl.php installieren und dieses Skript noch einmal starten.
    pause
    exit /b 1
)

echo Installer wird erstellt ...
"%ISCC%" /Q polybash_online_setup.iss
if errorlevel 1 (
    echo.
    echo FEHLER beim Erstellen. Die Meldung steht direkt darueber.
    pause
    exit /b 1
)
echo.
echo Fertig:  %cd%\dist\Polybash-Installer.exe
echo Diese eine Datei kannst du an Freunde schicken (ca. 15 MB).
pause
