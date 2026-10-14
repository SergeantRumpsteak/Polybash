#!/usr/bin/env python3
"""
Polybash - Mehrspieler-Shooter in einer 3D-Low-Poly-Welt (Panda3D).

Steuerung:
  W A S D        laufen          Maus / Pfeiltasten   umschauen
  Shift          rennen (mit Hermes-Schuhen: Dash)
  Leertaste      springen (in der Luft nochmal: Doppelsprung mit Jetpack-Schuhen;
                 in der Luft halten: Jetpack)
  Linke Maus     schiessen       Rechte Maus          zielen (Zoom)
  R              nachladen       1-3 / Mausrad        Waffe wechseln (Slot 1, 2, 3)
  Q / E          nach links / rechts um die Ecke lehnen
  G              Granate werfen (2 zum Start, 2,5 s Zündzeit)
  F              benutzen: Kiste öffnen, am Boden liegende Waffe aufheben,
                 Fahrzeug ein-/aussteigen; ist nichts Benutzbares in der Nähe: Nahkampfwaffe ziehen
  4              Nahkampfwaffe (zurück zu den Schusswaffen mit 1-3 / Mausrad); Linke Maus = zuschlagen
  Tab (halten)   Übersicht: Scoreboard (Punkte, Kills, Tode, Monster, Kisten, Buffs) und Tasten-Legende;
                 die Maus ist solange frei - Mausover über Waffen, Ausrüstung und Buff zeigt die Werte
  Esc            Menü (Maus frei; dort auch Beenden mit Sicherheitsabfrage; J = ja, N = nein)
  C / Strg       ducken          M Ton an/aus            F3 Bildrate anzeigen
  Menüs          auch mit der Maus bedienbar (Hover = gelb, Klick = wählen)
  R (tot)        respawnen (immer nur mit der Pistole)
  Fahrzeug       W/S Gas/Rückwärts, A/D lenken, Leertaste Handbremse, Maus: Kamera

Nahkampf: Jeder hat zusätzlich eine Nahkampfwaffe im eigenen Slot (Start/Respawn: Messer). Aus Kisten (Art "melee",
LOOT_MELEE_TABLES): Kampfmesser, Machete, Schwert, Katana (stark) und die Bratpfanne (Kopftreffer = BONG). Werte in
MELEE (Schaden, Schläge, Reichweite, Kopf-Faktor, Schlagwinkel). Ein Schlag ist sehr leise (NOISE_MELEE ~ Ducken):
nur das getroffene Monster merkt etwas, ahnungslose Monster nehmen MELEE_SNEAK-fachen Schaden - so erledigt man
sie leise. Neue Nahkampfwaffe ersetzt die alte (die fällt, ausser dem Messer); gleiche: "Hast du schon". Stirbt man
mit der Nahkampfwaffe in der Hand, fällt sie statt der Schusswaffe (das Messer nicht). Nahkampf-Kills zählen in
der Statistik (Special Shots).
Eigener Lärm auf der Minimap (NOISE_MINIMAP): ein dezenter weisser Kreis zeigt, wie weit man gerade zu hören ist
(geduckt/gehen/rennen/fahren); bei Schuss, Schlag oder eigener Explosion breitet sich eine Welle bis zum
Lärmradius aus. Ist sie grösser als der Ausschnitt, zoomt die Minimap kurz heraus (NOISE_MINIMAP_ZOOM).
Rundenende: Statt des Banners kommt ein Endbildschirm (das Spiel steht still): Siegerpodest (1./2./3.) und
Reiter mit der Rundenstatistik - Übersicht, Jäger (Monster je Art), Looten (Kisten je Art, Buffs), Tomahawk
(ausgelöst, Kills), Special Shots (weitester Kill mit Waffe, Kopfschüsse, Treffer), Bewegung (zu Fuss, im Wagen,
im Heli, Fahrten, Flüge). Umschalten mit der Maus, den Pfeiltasten, 1-6 oder Tab; der Beste je Spalte ist gold,
je Reiter gibt es einen Ehrentitel (Meister-Jäger, Schatzsucher ...). Der Host zählt (new_stats/end_tabs - neue
Werte dort ergänzen) und schickt die Statistik am Rundenende an alle; danach Countdown bis zur nächsten Runde.
HUD: oben Mitte Modus und Rundenzeit, oben links der Killfeed (nur Spieler-Kills und Wichtiges), unten links
Leben/Schild, Minimap und Fähigkeits-/Buff-Symbole, unten Mitte die Waffen-Slots, unten rechts die Munition,
rechts die Ausrüstung. Kurze Hinweise (Buff, Tomahawk wieder da, Helm zerstört ...) erscheinen dezent in der
Mitte und verschwinden wieder.

Waffen und Kisten (in allen Modi und auf allen Karten):
  Jeder startet und respawnt nur mit der Pistole. Alle anderen Waffen gibt es ausschliesslich in Kisten.
  Slot 1 und 2 sind freie Plätze für normale Waffen (Pistole, Revolver, MP, Schrotflinte, Sturmgewehr,
  Scharfschütze) - auch zwei Hauptwaffen sind erlaubt. Slot 3 ist nur für Spezialwaffen (Raketenwerfer,
  Minigun, Railgun). Sind die Plätze voll, wird getauscht: die Waffe in der Hand (normale Waffe) bzw. die
  Spezialwaffe fällt auf den Boden. Hält man die Spezialwaffe und hebt eine normale Waffe auf, wird die
  zuletzt benutzte normale Waffe getauscht. Hat man die Waffe schon, gibt es stattdessen Munition.
  Drei Kistenarten: braune Holzkiste (überall, meist Schrotflinte/MP), blau leuchtende Metallkiste (seltener,
  meist Sturmgewehr/Revolver/Minigun) und goldene Kiste mit rotem Rubin (nur ein paar pro Karte, meist Railgun,
  Raketenwerfer, Scharfschütze). In jeder Kiste ist jede Waffe möglich; die Prozente stehen in LOOT_TABLES.
  Waffen, die man gerade trägt, werden beim Öffnen herausgerechnet - so zieht man nicht ständig dasselbe.
  Dazu hat jeder Spieler ein Kisten-Gedächtnis für sein aktuelles Leben (beim Tod gelöscht): die zuletzt
  gezogene Waffe kommt in der nächsten Kiste nicht, und jede gezogene Waffe gibt pro Zug LOOT_PITY_STEP
  Prozentpunkte an jede andere Waffe ab (in allen Kistenarten) - so werden die guten Waffen mit jeder
  Kiste wahrscheinlicher. Kisten liegen zufällig verteilt (bei Gebäuden, Türmen,
  Aussenposten, im Tunnel und im Gelände) und sind nicht auf der Minimap. Eine geöffnete Kiste verschwindet;
  nach CRATE_RESPAWN Sekunden (je Art) taucht anderswo eine neue derselben Art auf.
  Beim Tod fällt die Waffe in der Hand und EIN zufälliges getragenes Ausrüstungsteil auf den Boden (F zum
  Aufheben), alles andere geht verloren.

Ausrüstung (aus allen Kistenarten, Tabelle GEAR + LOOT_GEAR_TABLES; LOOT_CATEGORIES = Anteil Ausrüstung je Kiste):
  Drei Slots: Kopf, Torso, Füsse - pro Slot ein Teil. Ein neues Teil ersetzt das alte (das alte fällt als Drop),
  ein identisches Teil lässt sich nicht aufheben ("Hast du schon"). Treibstoff und Abklingzeiten gehören dem
  Spieler, Tauschen setzt nichts zurück. Das Kisten-Gedächtnis gilt auch für Ausrüstung.
  Kopf   Basic-Helm      fängt einmal einen tödlichen Kopftreffer ab (überlebt mit SAVE_HP), dann zerstört.
  Torso  Plattenrüstung  dasselbe für tödliche Körpertreffer.
         Schild          30 HP, fängt Schaden vor den Lebenspunkten ab; 5 s ohne Treffer -> +5 HP/s.
         Jetpack         Leertaste in der Luft halten = Schub; ~10 s Treibstoff, leer -> voll in ~10 s.
  Füsse  Hermes-Schuhe   Shift (beim Laufen) = Dash 15 m in der halben Laufzeit, 10 s Abklingzeit.
         Springfedern    springt deutlich höher.
         Jetpack-Schuhe  Doppelsprung (Leertaste in der Luft); mit Jetpack: erst Doppelsprung, dann Schub.
  Helm/Platte retten nicht vor Sofort-Toden (Tomahawk, Granate im Nahradius, Sturz, Bodenschlag-Zentrum).
  HUD: Schildbalken unter den HP, drei Slot-Kacheln senkrecht am rechten Rand (Kopf/Torso/Füsse, dezenter Umriss
  im Hintergrund, darüber das getragene Teil - GEAR_HUD_*), Fähigkeitssymbole mit Kreis-Timer links über
  der Minimap, Treibstoffbalken. Andere sehen Helm, Platte/Schild/Jetpack und Schuhe an der Figur.
  Tasten stehen zentral in KEYS (Vorbereitung für frei belegbare Steuerung).

Spielmodi (vom Host im Start-Menü gewählt, mit einstellbarem Zeitlimit):
  King of the Hill  Die Burg in der Mitte ist die Zone. Jeder Spieler in der Zone
                    bekommt 1 Punkt pro Sekunde (auch mehrere gleichzeitig).
                    Ein Kill gibt 10 Punkte, steht der Killer dabei in der Zone: 20.
  Deathmatch        Jeder gegen jeden. Das Ranking am Ende entscheidet die K/D.
Standardkarte (300 x 300 m): ringsum ein Gebirgszug. Spieler UND Monster können ihn hochlaufen (MTN_CLIMB) -
oben hat man freies Schussfeld (z. B. mit der Sniper), ist aber selbst gut zu sehen. Am Kamm (MTN_WALL m vor dem
Kartenrand) ist für alle Schluss (unsichtbare Wand); Fahrzeuge schaffen nur flache Hänge (VEH_SLOPE). Neben Burg, Häusern und Türmen gibt es Aussenposten mit Deckung am
Boden UND gegen Beschuss aus der Luft: Containerlager (überdachter Gang, Aussichtspunkt auf den Stapeln),
Bunkerstellung, offene Scheune mit Heuboden, Felsformation mit Überhang, Ruinendorf, Hangar an der Landebahn,
Splitterschutzwände an den Helipads, kleine Unterstände und Wäldchen. Kartendateien bleiben 200 x 200 m.
Fallschaden: bis 5,5 m Fallhöhe nichts, darüber 11 HP pro Meter (Sprung vom Turm ~50, ab ~14,5 m tödlich).
Mitgelieferte Karte "TTT Minecraft b5": eine Minecraft-Welt Block für Block mit Originaltexturen
(Datei maps/ttt_minecraft_b5.mcmap, im Setup-Menü Zeile 7 wählbar; Deathmatch ohne Monster;
Leitern: W/Leertaste klettern, Ducken hält fest). Alle Spieler brauchen die .mcmap-Datei im Ordner 'maps'.
Eigene Karten: .json-Dateien aus dem Kartenbau-Editor in den Ordner 'maps' neben
dem Spiel legen; der Host wählt sie im Setup-Menü (Zeile 7). Mitspieler bekommen
die Karte beim Beitritt automatisch vom Host.
Die Monster (Mobs) können im Host-Menü abgeschaltet werden. Spieler können sich
gegenseitig Schaden machen (Kopfschuss = doppelter Schaden, Raketen und
Explosionen auch gegen sich selbst).
Stirbt ein Spieler, lässt er die Waffe in der Hand und ein zufälliges Ausrüstungsteil fallen
(F zum Aufheben); der Rest ist weg. Die Lebenspunkte regenerieren sich 30 s nach dem letzten
Treffer mit 2 HP pro Sekunde. Zwei Geländewagen stehen ausserhalb der Burg; eine
Rakete des Raketenwerfers zerstört sie mit einem Treffer; zerstörte Wagen stehen
nach 35 s wieder an ihrem Platz. Eine Granate tötet jeden im Umkreis von 2,6 m sofort.
Auf den vier freistehenden Türmen, in den Burgtürmen (Flak) und hinten auf dem Wagen
stehen Geschütze mit unbegrenzter Munition. Sie schiessen NICHT von selbst: F am
Geschütz = bedienen (Maus zielt, Linke Maus feuert, Rechte Maus zoomt, F = verlassen).
Die Rohre heizen sich auf (glühen, danach blau mit Dampf) und müssen abkühlen.
Der Wagen hat zwei Sitze: F = Fahrer (oder Schütze, wenn der Fahrersitz besetzt ist),
V = Schütze. Beide können gleichzeitig im Wagen sitzen.
Helikopter (zwei Stück, je auf einem Helipad auf gegenüberliegenden Seiten der Karte,
West und Ost): F einsteigen, WASD fliegen (relativ zur Blickrichtung), Leertaste steigen,
Shift sinken, Maus zielt (der Rumpf dreht nach), Linke Maus Minigun, Rechte Maus Rakete -
geschossen wird entlang der Sichtlinie. Munition ist begrenzt (300 Minigun-Schuss, 6 Raketen)
und wird nur nachgeladen, wenn man auf einem Helipad aufsetzt. Normale Waffen richten am
Helikopter wenig Schaden an (3 volle Sturmgewehr-Magazine zerstören ihn, die Pistole gar
nichts), eine Rakete zerstört ihn sofort; die Flak-Geschütze der Burg (F) schiessen
Sprenggranaten. Zerstört steht nach 45 s ein neuer auf dem Pad. Die Landebahn im Süden
bleibt als Kulisse.
Der Raketenwerfer hat ein Visier mit Entfernungsmesser und Vorhaltmarken (Rechte Maus).
Die Burg hat Kasematten, Barrikaden und Splitterschutzwände, der Innenhof (King-of-the-
Hill-Zone) bleibt offen. Man erreicht die Burg auch durch die Tunnel.
Unter der Burg und den Häusern verläuft ein Tunnelnetz (offene Eingänge mit orangem
Rand und Lampe, Treppen nach unten, auf der Minimap orange markiert). Auf der Standardkarte führen zwei lange
Tunnel vom Kartenrand herein (TUN_LONG): einer von Norden (Eingang kurz vor dem Gebirge) bis in den Ost-West-Gang,
mit einem Abzweig nach Osten zwischen den Aussenposten; einer von Süden (Eingang hinter der Landebahn) bis in den
Kommandoraum, mit einem Abzweig nach Westen zum Aussenposten Südwest. Im Tunnel schützt man sich vor dem
Tomahawk, dort können Kisten liegen (CRATE_TUNNEL_SHARE), Monster laufen die Treppen hinunter (MOB_TUNNELS),
Fahrzeuge passen nicht hinein.
Tomahawk (nur Standardkarte): Der rote Knopf sitzt oben auf einer Säule, die an einem von 20 gut sichtbaren
Orten aus dem Boden fährt (TOMA_SPOTS: auf Burgmauern, Burg- und Feldtürmen, dem Bergfried mitten in der
King-of-the-Hill-Zone, Bunkerdach, Heuboden, Ruinen, Unterstanddächern und auf freien Plätzen wie der Rollbahn).
Über dem Knopf pulsiert nur ein schwacher roter Schein - suchen muss man sie trotzdem; auf der Minimap ist sie nie.
Nach dem Hochfahren (3 s, mit Hydraulik-Ton) öffnet F die Zielkarte: Einschlagpunkt anklicken, Countdown wählen
(10/20/30/60 s, mindestens 10 s), abfeuern. Andere Spieler sind auf der Zielkarte nicht zu sehen
(TOMA_SHOW_PLAYERS). Danach ist der Knopf unbrauchbar, die Säule versinkt langsam im Boden, und nach der
Abklingzeit (Host-Menü, zufällig +-30 %: TOMA_RESPAWN_JITTER) fährt an einem ANDEREN Ort eine neue hoch; bei
"nur einmal pro Runde" erst in der nächsten Runde. Wer ausgelöst hat, ist danach 5 min selbst gesperrt
(TOMA_PLAYER_CD). Während des Countdowns fliegt die Rakete für alle sichtbar von weit hinter dem Gebirge in
einem hohen Bogen heran (Rauchschweif, Triebwerksglühen; leises Dröhnen, erst in den letzten 2 s laut mit
Pfeifen) - den
Zielort zeigt sonst nichts an, nur der Auslöser sieht ihn als roten Kreis auf seiner Minimap. Die Rakete tötet
alle oberirdisch im Gebiet sofort - in allen Modi ein Kreis mit 30 m Radius um das Ziel. Wer im Tunnel ist,
überlebt.

Monster: Grunt (grün), Brute (rot, Hörner), Jägerin, dazu
  Koloss - 3x so gross, 780 HP, selten (1 auf der Karte). Leichter Schlag (holt 1,2 s sichtbar aus, 85 Schaden)
           oder Bodenschlag (holt 2,4 s weit aus, Flächenschaden 7 m, im Zentrum bis 3 m tödlich; kommt, wenn 2+
           Spieler nah sind oder zufällig mit 25 %). Staubwelle, Beben, dumpfer Knall.
  Titan (Boss) - 7x so gross (gut 13 m), 4500 HP, höchstens 1 auf der Karte, nach dem Tod erst nach 5 min ein
           neuer (TITAN_RESPAWN). Langsam, eher stationär. Nah: Schlag (160 Schaden) oder Stampfer (holt 3,2 s
           aus, 11 m Radius, bis 4,5 m tödlich). Ab 20 m (bis 70 m): Steinwurf - holt mit dem Fuss aus, reisst
           einen Brocken aus dem Boden und tritt ihn im flachen Bogen auf dich (95 Schaden im Zentrum, 5 m Radius;
           eine Wand dazwischen schützt; wer seitlich wegläuft, weicht aus). Stirbt er, liegt an seiner Stelle
           eine goldene Kiste mit goldener Lichtsäule (wie jede goldene Kiste, wird nicht ersetzt).
  Elektro-Drohne - schwebt, schiesst aus bis 20 m einen Blitz (höchstens alle 7 s): kein Schaden, aber 1-3 s
           betäubt (nicht laufen, schiessen; umschauen geht), danach 3 s immun (STUN_IMMUNE); höchstens eine
           Drohne beschiesst denselben Spieler (DRONE_MAX_PER_TARGET). Bild flackert blau, auch für andere.
           Im Wagen/Heli trifft der Blitz das Fahrzeug: Motor aus (Wagen rollt aus, lenkt schwach) bzw. Antrieb
           aus (Heli sinkt spürbar, ein harter Aufprall beschädigt ihn). Aussteigen (F) geht jederzeit.
  Fluchttier - ein Feldhase (braun-grau, unauffällig), greift nie an. Sieht oder hört es dich, flieht es schnell
           in Haken. Wer es erlegt, bekommt EINEN zufälligen Buff: Tempo (+40 % für 10 s), Schaden (150 % für
           15 s) oder Tank (150 oder 200 max. HP für 30 s, Anzeige z. B. "160 / 200", danach anteilig zurück auf
           100). Hinweis in der Bildmitte ("Buff: Schaden 150 % - 15 s"), Symbol mit Kreis-Timer links.
  Monster im Fahrzeug: Sitzt du im Wagen (auch als Heckschütze) oder Heli, treffen Monster das Fahrzeug, nicht
           dich - auch Bodenschlag und Steinbrocken. Erst wenn es zerstört ist, gelten die normalen Regeln. Am
           freistehenden Geschütz (Turm, Burg) wirst du wie zu Fuss getroffen.
Lärm: Monster hören dich. Geduckt bist du fast lautlos (~3 m), normales Laufen hört man ~10 m weit, Sprinten
~22 m, einen Schuss ~60 m (je nach Waffe: Pistole leiser, Minigun/Raketenwerfer lauter), Explosionen ~90 m,
fahrende Wagen ~30 m, Helikopter ~55 m (NOISE_* oben in der Datei). Ein Monster, das etwas hört, läuft zum
Ort des Geräuschs - nicht direkt zu dir - und sucht dort ein paar Sekunden; sieht es dabei einen Spieler,
greift es an. Wände dämpfen den Lärm (noch) nicht.
Monster-Geräusche (MOB_SND, MOB_VOL): Schritte je nach Grösse (die Jägerin schleicht leise), ab und zu Knurren
(Grunt), tiefes Knurren (Brute), Fauchen (Jägerin); Drohnen surren leise, piepen/scannen, wenn sie dich
entdecken, und laden hörbar auf; Koloss und Titan brummen beim Ausholen bzw. bauen den Bodenschlag anschwellend
auf; der Titan reisst den Brocken krachend heraus, der Brocken rauscht im Flug; der Hase tapst und quiekt beim
Entdecken. Laute sind begrenzt (MOB_SND_MAX je MOB_SND_WINDOW s, nur die MOB_SND_NEAREST nächsten Monster).
Kugeln: Fliegt eine Kugel nah an einem Monster vorbei (BULLET_NOISE_R) oder schlägt neben ihm ein, läuft es 10-20 m
grob in die Richtung, aus der sie kam, sieht sich ~5 s um und kehrt dann zurück. Wird es getroffen, dreht es
sich sofort um und läuft Richtung Schütze (bis 80 m), auch ohne Sicht. Fluchttiere fliehen jeweils weg.
Eine fremde Kugel, die dir bis 3 m am Kopf vorbeifliegt, hörst du zischen (bis 1 m voll laut, aus der richtigen
Richtung; WHIZ_*).

Mehrspieler im WLAN (bis zu 8 Spieler):
  Hauptmenü: Name eingeben, dann "Spielen" (Spiel hosten oder beitreten - allein testen: einfach
  hosten, ohne dass jemand beitritt) oder Einstellungen (Name, Grafik, Bildrate, Maus). Der Host simuliert die Welt (Monster, Kugeln, Schaden,
  Punkte) und schickt 30x pro Sekunde einen Snapshot an alle Mitspieler (TCP,
  Port 37020, eine JSON-Nachricht pro Zeile). Jeder Spieler steuert seine eigene
  Figur direkt (kein Ruckeln beim Laufen) und meldet Position und Schüsse an den
  Host. Der Host sendet zusätzlich per UDP-Broadcast (Port 37021) "hier läuft ein
  Spiel", damit Mitspieler ihn im Menü automatisch finden. Sonst einfach die
  IP-Adresse des Hosts eintippen.

Aufbau:
  World / Player / Mob / Bullet / step() / update_weapon()
                          = reine Spiellogik, kein Zeichnen
  Mesh, build_*()         = Polygon-Geometrie erzeugen
  Conn, HostSession, ClientSession, ...
                          = Netzwerk (nur Standardbibliothek: socket, json)
  Game                    = Fenster, Menü, Eingabe, Kamera, Effekte, HUD, Minimap
Die Welt entsteht aus einem SEED: alle Mitspieler bekommen mit dem gleichen
Seed dieselbe Welt (Gelände, Burg, Gebäude, Türme, Bäume, Felsen), ohne dass
sie übertragen wird. Einheiten: 1 Einheit = 1 Meter, Zeit in Sekunden.

Gebäude bestehen aus Quadern (Box). Man kann auf Quader steigen, wenn ihre Oberkante
höchstens STEP_H über den Füssen liegt (Treppenstufen, niedrige Mauern per Sprung);
höhere Quader blockieren. Kugeln werden als Strecke gegen alle Quader geprüft.

Ballistik: Jede Kugel ist ein Massepunkt mit Startgeschwindigkeit v0 und
  dv_z/dt = -g * grav,  g = 9.81 m/s^2  (Bulletdrop). Pro Frame wird in
  Teilschritten von <= 1 m integriert und jedes Teilstück als Strecke gegen Mobs,
  Spieler, Bäume, Felsen, Gebäude, Wasser und Gelände geprüft (kein Durchtunneln).
  Raketen explodieren beim Aufprall und machen Flächenschaden (linear abfallend).
Rückstoss: Das Waffenmodell hängt an gedämpften Federn
  x'' = -k x - c x'   (Impuls beim Schuss -> Ausschwingen), ebenso die Kamera.
"""
import json
import math
import os
import random
import socket
import struct
import sys
import threading
import time
import zlib
from array import array
from dataclasses import dataclass
from types import SimpleNamespace

from panda3d.core import (AmbientLight, AntialiasAttrib, Camera, CardMaker, ColorBlendAttrib,
                          CullFaceAttrib, DirectionalLight, Fog, Geom, GeomNode, GeomTriangles, GeomVertexData,
                          GeomVertexFormat, GeomVertexWriter, KeyboardButton, MouseButton,
                          NodePath, PerspectiveLens, PNMImage, RenderState, Texture,
                          TextureAttrib, TextureStage, TextNode, TransparencyAttrib,
                          WindowProperties, loadPrcFileData)

# Konfiguration muss VOR dem Erzeugen des Fensters passieren
loadPrcFileData("", "window-title Polybash Experimental\nwin-size 1280 720\n"
                    "show-frame-rate-meter 0\nsync-video 0\n"
                    "framebuffer-multisample 1\nmultisamples 4\n")
if getattr(sys, "frozen", False):  # in der Executable gibt es keine Config.prc: Grafiktreiber nennen
    loadPrcFileData("", "load-display pandagl\naux-display p3tinydisplay\n")
if os.environ.get("SPIEL_OFFSCREEN"):  # nur für automatische Tests ohne Bildschirm
    loadPrcFileData("", "window-type offscreen\nload-display p3tinydisplay\n")

from direct.gui.OnscreenText import OnscreenText  # noqa: E402
from direct.showbase.ShowBase import ShowBase     # noqa: E402

# ---------------------------------------------------------------- Konstanten
SEED = 42
MAP_WORLD = 200.0        # Kartendateien (Editor, Minecraft): Spielfeld 0..200 m
STD_WORLD = 300.0        # Standardkarte: grösser, aussen ringsum ein Gebirgszug
WORLD = STD_WORLD        # Spielfeld: 0..WORLD in x und y (wird pro Karte gesetzt, siehe set_world_size)
CENTER = WORLD / 2       # Mitte der Karte = Burg
MARGIN = 30.0            # Gelände wird über den Rand hinaus gezeichnet
CELL = 4.0               # Gitterweite des Geländes
EYE = 1.7                # Augenhöhe
PLAYER_R = 0.4
WALK, RUN = 4.0, 7.5     # m/s
JUMP_V, GRAVITY = 6.5, 18.0
WATER_LEVEL = -1.2
MOUSE_SENS = 0.12        # Grad pro Pixel
MOUSE_WARP_GRACE = 3     # Frames beim Einfangen der Maus: so lange wird auf die Fenstermitte gewartet
MOUSE_WARP_RETRY = 6     # Frames: kommt das Zurücksetzen des Zeigers so lange nicht an, wird es wiederholt
KEY_TURN = 110.0         # Grad/s mit Pfeiltasten
FOV = 80.0

GRAV_BULLET = 9.81       # Bulletdrop
PLAYER_HP = 100.0
REGEN_DELAY, REGEN_RATE = 30.0, 2.0  # nach 30 s ohne Treffer: 2 HP/s (Rate im Host-Menü einstellbar)
REGEN_CHOICES = (0.0, 1.0, 2.0, 5.0, 10.0)   # HP/s (0 = keine Regeneration)
RESPAWN_CHOICES = (0, 3, 5, 10, 15, 20)       # Wartezeit bis zum Respawn eines Spielers (s)
RESPAWN_DEFAULT = 5
SWITCH_T = 0.38          # Dauer des Waffenwechsels
N_GRUNT, N_BRUTE, N_HUNT = 8, 3, 5
N_COLOSSUS = 1           # Koloss: selten (höchstens MAX_COLOSSUS gleichzeitig)
MAX_COLOSSUS = 2
N_TITAN = 1              # Titan (Boss): höchstens so viele gleichzeitig
TITAN_RESPAWN = 300.0    # s nach dem Tod, bis ein neuer Titan auftaucht
# Steinbrocken des Titans
ROCK_SPEED = 26.0        # m/s waagerecht (gut ausweichbar: ab 20 m gut 1 s Flug, dazu das lange Ausholen)
ROCK_GRAV = 14.0         # m/s² - flacher Bogen
ROCK_DMG = 95.0          # Schaden im Zentrum des Aufpralls ...
ROCK_R = 5.0             # ... linear weniger bis zu diesem Radius; Deckung (Wand dazwischen) schützt
ROCK_SIZE = 1.4          # m Durchmesser (Darstellung und Treffer)
TITAN_BEAM_H = 60.0      # m: goldene Lichtsäule über der Kiste, die der Titan fallen lässt
N_DRONE = 4              # Elektro-Drohnen
N_CRITTER = 5            # Fluchttiere (spawnen wie alle Monster nach RESPAWN_T wieder nach)
RESPAWN_T = 12.0

NET_PORT = 37020         # TCP: Spielverbindung
DISCOVERY_PORT = 37021   # UDP: Host-Suche im WLAN
NET_VERSION = 21         # Protokollversion: nur gleiche Versionen spielen zusammen
SNAP_RATE = 30.0         # Snapshots pro Sekunde (Host -> Mitspieler)
INPUT_RATE = 30.0        # Zustandsmeldungen pro Sekunde (Mitspieler -> Host)
NET_TIMEOUT = 10.0       # so lange ohne Daten, dann gilt die Verbindung als tot
MAX_PLAYERS = 8

STEP_H = 0.6             # so viel darf man ohne Sprung hochsteigen (Treppenstufe)
PLAYER_H = 1.8           # Körpergrösse (Trefferzylinder)
PLAYER_HIT_R = 0.45      # Trefferradius der Spieler
PROTECT_T = 3.0          # Spawnschutz in s (endet beim Schiessen)
SB_EVERY = 15            # Scoreboard-Werte (Tab) nur in jedem so-vielten Snapshot (2x pro Sekunde)
OVER_T = 15.0            # so lange bleibt die Rangliste nach Rundenende stehen

MODES = ("koth", "dm")
MODE_NAMES = {"koth": "King of the Hill", "dm": "Deathmatch"}
TIME_CHOICES = (3, 5, 10, 15, 20, 30)   # wählbare Zeitlimits in Minuten
ZONE_R = 15.0            # Radius der King-of-the-Hill-Zone (Burghof)
ZONE_PTS = 1.0           # Punkte pro Sekunde in der Zone (für jeden Spieler darin)
KILL_PTS = 10.0          # Punkte pro Kill (in der Zone als Killer: doppelt)

# --- Lehnen (Q/E): die Figur verschiebt sich wirklich seitlich (Wände begrenzen)
LEAN_MAX = 0.55          # m seitlicher Versatz
LEAN_RATE = 3.6          # m/s
CROUCH_DROP = 0.65       # so viel sinkt die Augenhöhe beim Ducken (m)
CROUCH_H = 1.15          # Trefferhöhe geduckt (stehend: PLAYER_H)
CROUCH_SPEED = 0.5       # Tempo geduckt (Faktor)
LEAN_ROLL = 16.0         # Grad Kamerakippung bei vollem Lehnen

# --- Granaten
GRENADES_START = 2
GREN_FUSE = 2.5          # s bis zur Explosion
GREN_SPEED = 21.0        # m/s Abwurfgeschwindigkeit (ca. 30 m weit)
GREN_G = 14.0            # Schwerkraft der Granate
GREN_R, GREN_DMG = 7.0, 120.0
GREN_COOLDOWN = 0.7

# --- Fahrzeug (Geländewagen)
VEH_HP = 220.0
VEH_R = 1.5              # Kollisionsradius
VEH_HIT_H = 1.7          # Trefferzylinder für Kugeln
VEH_ACC, VEH_MAX, VEH_REV = 13.0, 17.0, 6.0
VEH_TURN = 80.0          # Grad/s bei voller Lenkung
VEH_RESPAWN = 35.0       # s bis ein zerstörtes Fahrzeug wieder dasteht
VEH_BLAST_R, VEH_BLAST_DMG = 5.5, 110.0
ROCKET_KILL_R = 5.5      # Rakete: Fahrzeug innerhalb dieses Radius ist sofort zerstört
DROP_LIFE = 90.0         # s, so lange liegt eine fallengelassene Waffe herum
MAX_DROPS = 24

GREN_KILL_R = 2.6        # Granate: wer näher als das steht, stirbt sofort

# --- Geschütze auf den Türmen (unbegrenzte Munition, aber sie überhitzen)
TUR_RANGE = 42.0
TUR_DMG, TUR_INTERVAL, TUR_SPEED, TUR_SPREAD = 11.0, 0.11, 380.0, 2.0
TUR_HEAT_SHOT = 0.05     # Hitze pro Schuss (1.0 = überhitzt)
TUR_COOL, TUR_COOL_OVER, TUR_RESUME = 0.12, 0.30, 0.25   # Abkühlung/s, im Cooldown, Wiederanlauf
TUR_TURN = 150.0         # Grad/s

# --- Tomahawk (Knopf auf einer wandernden Säule)
STRIKE_T = 10.0          # Countdown in s (Standard)
STRIKE_OPTIONS = (10, 20, 30, 60)   # Countdown-Länge, wird auf der Zielkarte gewählt (mind. 10 s)
STRIKE_R = 30.0          # King of the Hill: doppelter Radius der Zone
STRIKE_CD = 120.0        # Standard-Abklingzeit des Tomahawk (s); 0 = nur einmal pro Runde
STRIKE_CD_CHOICES = (0, 30, 60, 120, 180, 300)   # im Host-Menü einstellbar
# Der Tomahawk-Knopf sitzt oben auf einer Säule, die an einem von vielen gut sichtbaren Orten aus dem Boden fährt.
# Viele Orte, dafür nicht versteckt: auf Mauern, Türmen, Dächern, Plattformen und auf freien Plätzen.
# (dx, dy, z) relativ zur Kartenmitte; z = Standhöhe (erhöhter Ort) oder None (am Boden, Platz wird frei gesucht).
TOMA_SPOTS = (
    (1.5, -1.0, 6.0),       # Bergfried-Dach mitten in der King-of-the-Hill-Zone (Treppe)
    (-20.2, 3.0, 5.0),      # Burg: Wehrgang West (Treppe im Hof)
    (20.2, -3.0, 5.0),      # Burg: Wehrgang Ost
    (-21.0, -21.0, 8.0),    # Burg: Eckturm Südwest (Treppe vom Wehrgang)
    (21.0, 21.0, 8.0),      # Burg: Eckturm Nordost
    (-57.1, 56.8, 9.0),     # Feldturm Nordwest (lange Treppe)
    (57.1, -59.2, 9.0),     # Feldturm Südost
    (-74.0, -36.0, 3.5),    # Dach der Bunkerstellung (Sandsack-Rampe)
    (81.0, 39.5, 2.4),      # Heuboden der Scheune
    (2.0, 87.0, 3.3),       # Ruinendorf, auf den Mauerresten
    (52.0, 74.0, 2.6),      # Dach eines Unterstands (über die Sandsäcke)
    (-52.0, -70.0, 2.6),    # Dach eines Unterstands
    # Bodenorte nur auf freien Flächen (TOMA_GROUND_CLEAR): nicht auf Rollbahn oder Helipads, nicht an Engstellen
    (40.0, -40.0, None),    # freies Feld Südost
    (44.0, 14.0, None),     # freies Feld östlich der Burg
    (60.0, -76.0, None),    # Feld östlich hinter der Rollbahn
    (-80.0, -56.0, None),   # Feld Südwest
    (-64.0, 76.0, None),    # Feld Nordwest
    (-40.0, 52.0, None),    # Wiese Nordwest
    (4.0, 60.0, None),      # Wiese nördlich der Burg
    (76.0, 56.0, None),     # Feld Nordost
)
TOMA_GROUND_CLEAR = 9.0  # m: so viel Platz brauchen Bodenorte zu Wänden/Deckung (keine Engstellen für Fahrzeuge)
TOMA_KEEP_FREE = 12.0    # m Abstand zu Rollbahn, Helipads und Fahrzeug-Startplätzen
TOMA_SEE_R = 120.0       # Mitspieler erfahren vom Host (und sehen) die Säule nur in dieser Entfernung
TOMA_RISE_T = 3.0        # s: so lange fährt die Säule hoch; erst danach ist der Knopf benutzbar
TOMA_SINK_T = 8.0        # s: so lange versinkt die benutzte Säule wieder im Boden
# Stellschrauben gegen die "Ablauf-Meta" (Tomahawk holen, auf der Karte alle sehen, abräumen):
TOMA_SHOW_PLAYERS = False   # Zielkarte zeigt die Positionen der anderen Spieler
TOMA_PLAYER_CD = 300.0      # s: wer den Tomahawk ausgelöst hat, kann ihn so lange selbst nicht mehr auslösen
TOMA_RESPAWN_JITTER = 0.30  # Abklingzeit bis zur nächsten Säule zufällig +- 30 %
# Anflug der Rakete (reine Darstellung, jeder rechnet sie selbst aus Ziel, Richtung und Countdown)
TOMA_ROCKET_SPEED = 45.0    # m/s waagerecht
TOMA_ROCKET_MIN = 420.0     # m: so weit (mindestens) startet sie vom Ziel entfernt - weit hinter dem Gebirge
TOMA_ROCKET_ALT = 230.0     # m: Flughöhe über dem Ziel (das Gebirge ist bis ~95 m hoch)
TOMA_LOUD_T = 2.0           # s vor dem Einschlag: erst dann wird der Raketenton laut (dazu das Pfeifen)
TOMA_JET_QUIET = 0.05       # Lautstärke des Dröhnens im Anflug (leise im Hintergrund)
TOMA_JET_VOL = 0.55         # Lautstärke in der letzten Sekunde
TOMA_WHISTLE_VOL = 0.5      # Lautstärke des Pfeifens
CASTLE_HALF = 22.0       # Deathmatch: alles innerhalb der Burgmauern
TO = CENTER - 80.0       # Verschiebung der Tunnel-Koordinaten (entworfen für eine 160-m-Karte)


def set_world_size(size):
    """Spielfeldgrösse für die nächste Welt setzen (Standardkarte 300 m, Kartendateien 200 m).
    WORLD, CENTER und TO sind Modul-Variablen, die überall zur Laufzeit gelesen werden."""
    global WORLD, CENTER, TO
    WORLD = float(size)
    CENTER = WORLD / 2
    TO = CENTER - 80.0


# --- Fallschaden
FALL_SAFE = 5.5          # bis zu dieser Fallhöhe (m) passiert nichts (Hausdach, Burgmauer, Sprung in den Tunnelschacht)
FALL_DMG = 11.0          # Schaden pro Meter darüber (Sprung vom 9-m-Turm: ~50, ab ~14,6 m tödlich)
WI_FALL = -9             # "Waffe" in der Kill-Anzeige
WI_SLAM = -10            # Bodenschlag des Kolosses
WI_ROCK = -11            # Steinbrocken des Titans

# --- Gebirge am Rand der Standardkarte
MTN_BAND = 46.0          # so breit ist der Gebirgsgürtel (m, schwankt)
MTN_H = 36.0             # Höhe am Kartenrand (dahinter steigt es weiter)
MTN_CLIMB = True         # True: Spieler UND Monster können das Gebirge hochlaufen (Sniper-Posten oben);
                         # False: alter Zustand - Felswände steiler als MTN_SLOPE sperren, jetzt auch für Monster
MTN_SLOPE = 0.95         # (nur bei MTN_CLIMB = False) steiler als das (ca. 43 Grad) kommt man nicht hoch
MTN_WALL = 4.0           # unsichtbare Wand: so weit vor dem Kartenrand (Gebirgskamm) ist Schluss - für alle
VEH_SLOPE = 0.7          # ... mit dem Geländewagen

# --- Helikopter, Flak
HELI_HP = 1000.0
# Monster gegen Fahrzeuge (5b): Wer im Wagen (Fahrer oder Heckschütze) oder Helikopter sitzt, wird von Monstern
# nicht direkt getroffen - der Schaden geht ans Fahrzeug. Die Drohne legt das Fahrzeug stattdessen lahm.
MOB_VEH_DMG = 1.0         # Faktor: Monsterschaden am Fahrzeug (x Schaden, den der Spieler bekommen hätte)
VEH_STALL_STEER = 0.4     # Wagen lahmgelegt: Motor aus (kein Gas), Lenkung nur noch zu diesem Anteil
HELI_STALL_SINK = 6.0     # m/s: so schnell sinkt ein lahmgelegter Heli (kein freier Fall)
HELI_STALL_DRAG = 0.6     # 1/s: so schnell verliert er dabei Vorwärtsfahrt
HELI_CRASH_V = 3.0        # m/s: Aufprall schneller als das (lahmgelegt) beschädigt den Heli ...
HELI_CRASH_DMG = 70.0     # ... mit so viel Schaden je m/s darüber
HELI_K = HELI_HP / (3 * 30 * 17.0)   # Schadensfaktor normaler Waffen: 3 volle Sturmgewehr-Magazine (3 x 30 x 17) töten ihn
HELI_MG_MAX, HELI_RK_MAX = 300, 6    # Munition: Minigun-Schuss / Raketen (nur auf dem Helipad nachladbar)
HELI_VMAX, HELI_VUP, HELI_VDN = 24.0, 8.0, 9.0
HELI_CEIL = 70.0
HELI_R, HELI_HIT_H = 3.0, 3.0
HELI_RESPAWN = 45.0
HELI_MG_CD, HELI_RK_CD, HELI_SPREAD = 0.05, 1.2, 1.3
HELI_RELOAD_MG, HELI_RELOAD_RK = 90.0, 1.0   # Schuss/s bzw. s pro Rakete auf dem Pad
HELI_PAD_R = 8.0
HELI_ROCKET_KILL_R = 3.5             # Rakete: Treffer näher als HELI_R + dieser Wert zerstört ihn sofort
FLAK_R, FLAK_DMG, FLAK_PROX = 10.0, 75.0, 8.0
FLAK_SPEED, FLAK_INTERVAL, FLAK_LIFE, FLAK_HEAT = 260.0, 0.55, 2.6, 0.14

# --- Geheime Tunnel
TUN_Z = -4.2             # Boden der Tunnel (unter dem ebenen Gelände um Burg und Häuser)
MOB_TUNNELS = True       # Monster dürfen die Treppen hinunter in die Tunnel (Drohnen nicht)
TUN_LONG = True          # Standardkarte: die langen Tunnel vom Kartenrand (Nord, Süd) mit je einem Abzweig
TUN_COVER_MIN = -0.5     # m: tiefer darf das Gelände über einem Gang nicht liegen (sonst wird es dort angehoben)
TUN_SEG = 8.0            # m: Wände/Decke in Stücken, deren Oberkante dem Gelände darüber folgt
TUN_ENTRY_FLAT = 10.0    # m: so weit ist das Gelände um die neuen Eingänge ganz eben (keine Ritzen im Gelände)
TUN_LAMP = 9.0           # m Abstand der Lampen in den neuen Gängen
TUN_ROOF = -1.7          # Unterkante der Decke (Gang: 2,5 m hoch)

STONE = (0.56, 0.54, 0.50)
STONE_D = (0.44, 0.42, 0.40)
ROOF = (0.60, 0.27, 0.22)
PLASTER = (0.70, 0.62, 0.50)
WOOD_F = (0.48, 0.37, 0.25)
COBBLE = (0.50, 0.48, 0.42)
CONCRETE = (0.55, 0.55, 0.57)
ROCK_C = (0.47, 0.45, 0.42)       # Felsformationen
SANDBAG = (0.66, 0.59, 0.42)      # Sandsäcke
CONT_COLS = ((0.22, 0.36, 0.55), (0.62, 0.27, 0.20), (0.27, 0.45, 0.33), (0.70, 0.52, 0.18))   # Container

SKY = (0.70, 0.82, 0.93)          # Dunstfarbe am Horizont (Nebel und Hintergrund)
SUN = (0.45, 0.30, 0.84)  # Richtung zur Sonne (wird normiert)
AMBIENT, DIFFUSE = 0.60, 0.66   # etwas kräftiger, weil die Texturen im Mittel ~0.8 abdunkeln


# ------------------------------------------------------------ Vektor-Helfer
def sub(a, b):
    return (a[0] - b[0], a[1] - b[1], a[2] - b[2])


def add(a, b):
    return (a[0] + b[0], a[1] + b[1], a[2] + b[2])


def cross(a, b):
    return (a[1] * b[2] - a[2] * b[1], a[2] * b[0] - a[0] * b[2], a[0] * b[1] - a[1] * b[0])


def dot(a, b):
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def norm(v):
    l = math.sqrt(dot(v, v)) or 1.0
    return (v[0] / l, v[1] / l, v[2] / l)


SUN = norm(SUN)


def seg_point_dist(a, b, p):
    """Abstand des Punkts p von der Strecke a-b (3D)."""
    ab = (b[0] - a[0], b[1] - a[1], b[2] - a[2])
    ap = (p[0] - a[0], p[1] - a[1], p[2] - a[2])
    l2 = ab[0] * ab[0] + ab[1] * ab[1] + ab[2] * ab[2]
    t = 0.0 if l2 < 1e-12 else max(0.0, min(1.0, (ap[0] * ab[0] + ap[1] * ab[1] + ap[2] * ab[2]) / l2))
    return math.dist(p, (a[0] + ab[0] * t, a[1] + ab[1] * t, a[2] + ab[2] * t))


def clampf(v, lo, hi):
    return max(lo, min(hi, v))


def smoothstep(e0, e1, x):
    t = max(0.0, min(1.0, (x - e0) / (e1 - e0)))
    return t * t * (3 - 2 * t)


def jc(col, rng, amt=0.06):
    """Farbe leicht variieren -> facettierter Low-Poly-Look."""
    f = 1 + rng.uniform(-amt, amt)
    return (col[0] * f, col[1] * f, col[2] * f)


def seg_cyl(p0, p1, cx, cy, r, z0, z1):
    """Schnitt der Strecke p0->p1 mit einem senkrechten Zylinder
    (Mittelachse (cx,cy), Radius r, Höhe z0..z1).
    Gibt den kleinsten Parameter t in [0,1] des Eintritts zurück oder None.
    Lösung: |p0_xy + t d_xy - c|^2 = r^2  ->  a t^2 + b t + c0 = 0."""
    dx, dy, dz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
    fx, fy = p0[0] - cx, p0[1] - cy
    a = dx * dx + dy * dy
    c0 = fx * fx + fy * fy - r * r
    if a > 1e-12:
        b = 2 * (fx * dx + fy * dy)
        disc = b * b - 4 * a * c0
        if disc < 0:
            return None
        s = math.sqrt(disc)
        lo, hi = (-b - s) / (2 * a), (-b + s) / (2 * a)
    else:
        if c0 > 0:
            return None
        lo, hi = 0.0, 1.0
    lo, hi = max(lo, 0.0), min(hi, 1.0)
    if lo > hi:
        return None
    if abs(dz) > 1e-12:                      # Höhenintervall dazuschneiden
        ta, tb = (z0 - p0[2]) / dz, (z1 - p0[2]) / dz
        if ta > tb:
            ta, tb = tb, ta
        lo, hi = max(lo, ta), min(hi, tb)
    elif not (z0 <= p0[2] <= z1):
        return None
    return lo if lo <= hi else None


# ------------------------------------------------------------------ Waffen
@dataclass(frozen=True)
class Weapon:
    name: str
    dmg: float            # Schaden pro Kugel
    interval: float       # s zwischen zwei Schüssen
    mag: int              # Magazingrösse
    max_reserve: int
    speed: float          # Mündungsgeschwindigkeit m/s
    spread: float         # Streukegel (Grad, Halbwinkel) bei Hüftfeuer
    reload: float         # Nachladezeit s
    auto: bool = False
    pellets: int = 1
    kick: float = 1.0         # bleibender Rückstoss nach oben (Grad)
    kick_yaw: float = 0.3     # zufälliger Seitenversatz (Grad)
    kick_back: float = 3.0    # Stärke des Federimpulses am Waffenmodell
    ads_fov: float = 60.0
    ads_spread: float = 0.3   # Faktor auf spread beim Zielen
    bloom: float = 0.0        # Streuungszuwachs pro Schuss
    pickup: int = 0           # Munition pro erlegtem Mob/Spieler
    kind: str = "normal"      # normal (Slot 1/2) | special (nur Slot 3: Raketenwerfer, Minigun, Railgun)
    scope: bool = False       # Zielfernrohr-Ansicht beim Zielen
    sight: str = ""           # 'rocket' = Visier mit Entfernungsmesser und Vorhaltmarken
    grav: float = 1.0         # Faktor auf die Schwerkraft der Kugel
    blast_r: float = 0.0      # Explosionsradius (0 = normale Kugel)
    blast_dmg: float = 0.0    # Schaden im Explosionszentrum
    loud: float = 1.0         # Lautstärke-Faktor des Schusses (Lärmsystem: NOISE_SHOT * loud)


WEAPONS = (
    Weapon("Pistole", 28, 0.30, 12, 96, 240, 0.9, 1.3, kick=1.6, kick_yaw=0.4,
           kick_back=3.5, ads_fov=61, bloom=0.25, pickup=12, loud=0.75),
    Weapon("Sturmgewehr", 17, 0.09, 30, 240, 360, 1.6, 2.0, auto=True, kick=0.9,
           kick_yaw=0.5, kick_back=2.2, ads_fov=55, bloom=0.12, pickup=30, loud=1.0),
    Weapon("Schrotflinte", 9, 0.85, 6, 36, 200, 4.5, 2.4, pellets=9, kick=5.0,
           kick_yaw=0.8, kick_back=7.0, ads_fov=65, ads_spread=0.6, pickup=6, loud=1.1),
    Weapon("Scharfschütze", 120, 1.3, 5, 25, 650, 0.6, 2.8, kick=4.0, kick_yaw=0.5,
           kick_back=6.0, ads_fov=16, ads_spread=0.03, pickup=5, scope=True, loud=1.25),
    Weapon("Revolver", 55, 0.55, 6, 48, 320, 0.7, 2.2, kick=3.0, kick_yaw=0.5,
           kick_back=5.0, ads_fov=59, bloom=0.3, pickup=6, loud=0.9),
    Weapon("Maschinenpistole", 11, 0.065, 32, 224, 290, 2.2, 1.8, auto=True, kick=0.5,
           kick_yaw=0.6, kick_back=1.6, ads_fov=59, bloom=0.10, pickup=32, loud=0.85),
    Weapon("Raketenwerfer", 0, 1.4, 1, 6, 95, 0.4, 2.6, kick=5.0, kick_yaw=0.4,
           kick_back=9.0, ads_fov=26, ads_spread=0.5, grav=0.12, blast_r=6.0, sight="rocket",
           blast_dmg=130, kind="special", loud=1.4),
    Weapon("Minigun", 9, 0.045, 150, 450, 380, 3.0, 4.0, auto=True, kick=0.35,
           kick_yaw=0.7, kick_back=1.4, ads_fov=66, ads_spread=0.6, bloom=0.05, kind="special", loud=1.3),
    Weapon("Railgun", 140, 1.5, 4, 20, 1100, 0.15, 3.0, kick=4.5, kick_yaw=0.3,
           kick_back=7.0, ads_fov=25, ads_spread=0.05, grav=0.02, scope=True, kind="special", loud=1.2),
)
WEAPON_IDX = {w.name: i for i, w in enumerate(WEAPONS)}


@dataclass
class Melee:
    """Nahkampfwaffe (eigener Slot, belegt nie einen Waffenslot)."""
    name: str
    dmg: float            # Schaden pro Treffer
    interval: float       # s zwischen zwei Schlägen
    reach: float          # m Reichweite (ab Augenhöhe, Rand des Ziels)
    head: float = 1.5     # Faktor bei Kopftreffer
    arc: float = 40.0     # Grad: so weit neben der Blickrichtung trifft der Schlag noch
    short: str = ""       # kurzer Name fürs HUD
    sound: str = "slash"  # Treffergeräusch


MELEE = (
    Melee("Messer", 25, 0.45, 1.6, short="Messer"),                       # Start (0815-Messer)
    Melee("Kampfmesser", 34, 0.42, 1.7, short="Kampfmesser"),
    Melee("Machete", 46, 0.6, 2.0, short="Machete"),
    Melee("Schwert", 62, 0.75, 2.4, short="Schwert"),
    Melee("Katana", 75, 0.55, 2.5, head=1.6, arc=45.0, short="Katana"),
    Melee("Bratpfanne", 38, 0.7, 1.9, head=2.6, arc=50.0, short="Pfanne", sound="bong"),   # Spass: Kopf = BONG
)
MELEE_IDX = {m.name: i for i, m in enumerate(MELEE)}
START_MELEE = 0
MELEE_SEL = -2            # "Auswahl" für die Nahkampfwaffe (Taste 4 / F ohne Ziel / Mausrad)
MELEE_WI0 = 100           # Kill-Anzeige/Statistik: Waffe = MELEE_WI0 + Index in MELEE
MELEE_SNEAK = 2.0         # Faktor, wenn das Monster nichts ahnt (idle, nicht am Suchen/Jagen) - leise erledigen
NOISE_MELEE = 3.0         # m Lärmradius eines Schlags/Treffers (etwa wie Ducken)

# ======================================================================== LOOT (zum Balancen)
# --- Waffen-Slots
N_FREE_SLOTS = 2               # Slot 1..N_FREE_SLOTS: freie Plätze für jede normale Waffe
SPECIAL_SLOT = N_FREE_SLOTS    # der Slot danach (Taste 3) ist nur für Spezialwaffen
N_SLOTS = N_FREE_SLOTS + 1     # Slots insgesamt (Tasten 1..N_SLOTS)
START_WEAPON = WEAPON_IDX["Pistole"]   # damit startet/respawnt jeder; kommt nicht in Kisten
DUP_AMMO_MAGS = 2              # hebt man eine Waffe auf, die man schon trägt: so viele Magazine Reserve dazu

# --- Kisten auf der Karte (drei Arten: braun = gewöhnlich, blau = selten, gold = legendär)
CRATE_KINDS = ("common", "rare", "gold")      # Index in den Snapshots
CRATE_NAMES = {"common": "Kiste", "rare": "seltene Kiste", "gold": "goldene Kiste"}
CRATES_STD = {"common": 30, "rare": 8, "gold": 4}   # gleichzeitig auf der Standardkarte (300 x 300 m)
CRATES_MAP = {"common": 18, "rare": 5, "gold": 2}   # auf Kartendateien und der Minecraft-Karte (200 x 200 m)
CRATE_RESPAWN = {"common": 20.0, "rare": 35.0, "gold": 60.0}   # s nach dem Öffnen bis zur Ersatzkiste (gleiche Art)
CRATE_GAP = 11.0               # Mindestabstand zwischen zwei Kisten (m)
CRATE_GOLD_GAP = 70.0          # goldene Kisten liegen mind. so weit auseinander (Standardkarte, kleinere anteilig)
CRATE_PLAYER_GAP = 12.0        # während der Runde taucht keine Kiste näher als das an einem Spieler auf
CRATE_REUSE_GAP = 20.0         # die Ersatzkiste taucht mind. so weit von der geöffneten entfernt auf
CRATE_SPOT_SHARE = 0.5         # Anteil der Kisten an Bauwerken (Türme, Häuser, Burg, Aussenposten ...)
CRATE_TUNNEL_SHARE = 0.12      # Anteil im Tunnelnetz (nur Standardkarte); der Rest liegt im freien Gelände

# --- Was steckt in den Kisten? (Prozent je Kistenart, jede Spalte ergibt 100)
# In jeder Kiste ist jede Waffe möglich, nur unterschiedlich wahrscheinlich. Beim Öffnen werden Waffen, die
# der Spieler gerade trägt, herausgerechnet (LOOT_SKIP_OWNED), damit man nicht ständig dasselbe zieht.
# Wohin ihr Anteil geht, bestimmt LOOT_SHARE_MODE:
#   "proportional": im Verhältnis der übrigen Werte - die Kiste behält ihren Charakter. Braune Kiste, man trägt
#                   die Schrotflinte: MP 30 -> 42,9 %, Scharfschütze 1 -> 1,4 %.
#   "equal":        zu gleichen Teilen auf alle übrigen (je 30/7 = 4,3 %). Hebt seltene Waffen stark an:
#                   Scharfschütze 1 -> 5,3 %, mit Schrotflinte UND MP sogar 11 % aus der braunen Kiste.
# Kisten-Gedächtnis (LOOT_SKIP_LAST, LOOT_PITY): siehe Konstanten unten. Mit LOOT_PITY_STEP = 1.0 zieht man laut
# Simulation (10.000 Läufe, 6 braune / 3 blaue / 1 goldene Kiste in zufälliger Reihenfolge) mindestens eine
# Top-Waffe (Scharfschütze, Railgun, Raketenwerfer): nach 5 Kisten in 82 %, nach 10 Kisten in 99,8 % der Fälle
# (ohne Gedächtnis: 71 % / 96 %). Nur braune Kisten: 61 % / 98 % (ohne: 36 % / 64 %).
# Die Pistole (Startwaffe) kommt nie in Kisten. Die Scharfschütze war im Test "verdammt böse": in der braunen
# Kiste nur 1 %, auch in Blau und Gold bewusst niedriger als Railgun und Raketenwerfer (Waffenwerte unverändert).
LOOT_SKIP_OWNED = True
LOOT_SHARE_MODE = "proportional"
# --- Kisten-Gedächtnis (pro Spieler und Leben, nur beim Host; beim Tod/Respawn zurückgesetzt)
LOOT_SKIP_LAST = True          # die zuletzt gezogene Waffe kommt in der nächsten Kiste nicht (auch wenn weggeworfen)
LOOT_PITY = True               # Aufbau-Ausgleich an/aus
LOOT_PITY_STEP = 1.0           # je Zug: jede ANDERE Waffe +so viele Prozentpunkte, die gezogene verliert die Summe
LOOT_DEBUG = False             # True: beim Öffnen die Chancen des Spielers je Kistenart einblenden + ins Log
LOOT_TABLES = {
    #  Waffe               braun  blau   gold
    "Schrotflinte":     (30.0, 10.0,  2.0),
    "Maschinenpistole": (30.0, 10.0,  2.0),
    "Sturmgewehr":      (13.0, 22.0,  7.0),
    "Revolver":         (13.0, 22.0,  7.0),
    "Minigun":          ( 9.0, 16.0, 16.0),
    "Railgun":          ( 2.0,  8.0, 27.0),
    "Raketenwerfer":    ( 2.0,  8.0, 27.0),
    "Scharfschütze":    ( 1.0,  4.0, 12.0),
}
# Ausrüstung in Kisten: Prozent innerhalb der Ausrüstung (jede Spalte ergibt 100). Helm und Platte eher braun,
# Schild/Jetpack/Schuhe eher blau und gold.
LOOT_GEAR_TABLES = {
    #  Teil                   braun  blau   gold
    "Basic-Helm":          (35.0, 10.0,  5.0),
    "Plattenrüstung":      (30.0, 10.0,  5.0),
    "Schild":              (10.0, 20.0, 20.0),
    "Jetpack":             ( 5.0, 15.0, 20.0),
    "Hermes-Schuhe":       ( 7.0, 15.0, 17.0),
    "Springfeder-Schuhe":  ( 8.0, 15.0, 15.0),
    "Jetpack-Schuhe":      ( 5.0, 15.0, 18.0),
}
# Wie oft eine Kiste Waffe bzw. Ausrüstung enthält (je Kistenart). Danach entscheidet die jeweilige Tabelle.
LOOT_MELEE_TABLES = {
    #  Nahkampf              braun  blau   gold   (das Start-Messer kommt nie aus Kisten)
    "Kampfmesser":         (40.0, 15.0,  5.0),
    "Machete":             (30.0, 25.0, 10.0),
    "Schwert":             (12.0, 30.0, 30.0),
    "Katana":              ( 3.0, 15.0, 40.0),
    "Bratpfanne":          (15.0, 15.0, 15.0),
}
LOOT_CATEGORIES = {"common": {"weapon": 0.62, "gear": 0.25, "melee": 0.13},
                   "rare":   {"weapon": 0.57, "gear": 0.30, "melee": 0.13},
                   "gold":   {"weapon": 0.57, "gear": 0.30, "melee": 0.13}}
LOOT_TABLES.update(LOOT_GEAR_TABLES)
LOOT_TABLES.update(LOOT_MELEE_TABLES)
# Art jedes Eintrags ("weapon" | "gear"; später z. B. "grenade"). Das Kisten-Gedächtnis (Ausgleich,
# "zuletzt gezogen", getragene herausrechnen) gilt je Art - Waffen und Ausrüstung nehmen sich nichts weg.
LOOT_ITEMS = {name: ("gear" if name in LOOT_GEAR_TABLES else "melee" if name in LOOT_MELEE_TABLES else "weapon")
              for name in LOOT_TABLES}
# ======================================================================== AUSRÜSTUNG
# Drei Slots, pro Slot ein Teil. Neue Teile: eine Zeile in GEAR (und in LOOT_GEAR_TABLES) - Platz für 5 je Slot.
GEAR_SLOTS = ("head", "torso", "feet")
GEAR_SLOT_NAMES = {"head": "Kopf", "torso": "Torso", "feet": "Füsse"}


@dataclass
class Gear:
    name: str
    slot: str                  # head | torso | feet
    kind: str                  # Wirkung: save_head | save_body | shield | jetpack | dash | spring | double_jump
    short: str                 # Kürzel für HUD
    col: tuple = (0.8, 0.8, 0.8)
    hud: str = ""              # kurzer Name für die Slot-Übersicht im HUD


GEAR = (
    Gear("Basic-Helm", "head", "save_head", "H", (0.55, 0.58, 0.5), "Helm"),
    Gear("Plattenrüstung", "torso", "save_body", "P", (0.6, 0.62, 0.66), "Platte"),
    Gear("Schild", "torso", "shield", "S", (0.3, 0.7, 1.0), "Schild"),
    Gear("Jetpack", "torso", "jetpack", "J", (1.0, 0.55, 0.15), "Jetpack"),
    Gear("Hermes-Schuhe", "feet", "dash", "D", (1.0, 0.85, 0.3), "Hermes"),
    Gear("Springfeder-Schuhe", "feet", "spring", "F", (0.6, 1.0, 0.4), "Federn"),
    Gear("Jetpack-Schuhe", "feet", "double_jump", "2", (1.0, 0.45, 0.2), "Jet-Schuhe"),
)
GEAR_IDX = {g.name: i for i, g in enumerate(GEAR)}
SAVE_HP = 10.0            # Helm/Platte: man überlebt den tödlichen Treffer mit so viel HP (Teil ist danach kaputt)
SHIELD_HP = 30.0          # Schild fängt zuerst so viel Schaden ab
SHIELD_DELAY = 5.0        # s ohne Schildschaden, dann lädt es auf
SHIELD_RATE = 5.0         # HP/s Aufladen
JET_FUEL = 10.0           # s Flug mit vollem Tank
JET_REFILL_T = 10.0       # s, bis ein leerer Tank wieder voll ist (füllt nur, wenn nicht geflogen wird)
JET_ACC = 26.0            # m/s² Schub (Schwerkraft ist 18): hebt an
JET_VMAX = 5.5            # m/s höchstens nach oben
DASH_DIST = 15.0          # m Dash nach vorn (10-20)
DASH_TIME = DASH_DIST / RUN * 0.5   # halb so lange, wie Sprinten bräuchte (1 s)
DASH_CD = 10.0            # s Abklingzeit
SPRING_JUMP = 1.55        # Springfedern: Sprunggeschwindigkeit x1,55 (gut doppelt so hoch: ~2,8 m)
DOUBLE_JUMP_V = JUMP_V    # Doppelsprung: zweiter Sprung in der Luft
# Zentrale Tastenzuordnung (Grundlage für ein späteres Menü "Steuerung"). Gelesen werden sie mit
# Game.key_down(name); die übrigen Tasten (F, R, G, V, Tab, 1-3 ...) sind noch per accept() verdrahtet.
KEYS = {"forward": "w", "back": "s", "left": "a", "right": "d", "sprint": "shift", "jump": "space",
        "duck": "control", "lean_left": "q", "lean_right": "e", "use": "f", "reload": "r", "grenade": "g"}
# ======================================================================== Ende Loot

ROCKET_WI = next(i for i, w in enumerate(WEAPONS) if w.blast_r > 0)   # Raketenwerfer
PISTOL_WI = next(i for i, w in enumerate(WEAPONS) if w.name == "Pistole")   # richtet am Helikopter keinen Schaden an
MINIGUN_WI = next(i for i, w in enumerate(WEAPONS) if w.name == "Minigun")
WI_GRENADE, WI_VEHICLE, WI_TURRET, WI_TOMAHAWK = -2, -3, -4, -5   # "Waffe" in der Kill-Anzeige
WI_HELI, WI_FLAK = -6, -8


def weapon_name(wi):
    if 0 <= wi < len(WEAPONS):
        return WEAPONS[wi].name
    if 0 <= wi - MELEE_WI0 < len(MELEE):
        return MELEE[wi - MELEE_WI0].name
    return {WI_GRENADE: "Granate", WI_VEHICLE: "Fahrzeug", WI_TURRET: "Geschütz",
            WI_TOMAHAWK: "Tomahawk", WI_HELI: "Helikopter",
            WI_FLAK: "Flak", WI_FALL: "Sturz"}.get(wi, "?")

def strike_cd_label(cd):
    cd = int(cd)
    if cd <= 0:
        return "nur einmal pro Runde"
    return f"{cd // 60} min" if cd % 60 == 0 else f"{cd} s"


def respawn_label(t):
    t = int(t)
    return "sofort" if t <= 0 else f"{t} s" + (" (normal)" if t == RESPAWN_DEFAULT else "")


def regen_label(r):
    return "aus" if r <= 0 else f"{r:g} HP/s" + (" (normal)" if r == REGEN_RATE else "")


TURRET_NAMES = {"mg": "MG-Geschütz", "flak": "Flak", "car": "Wagen-Geschütz"}

MOB_KINDS = {     # hear = Hör-Empfindlichkeit (Faktor auf die Lärmradien)
    "grunt": dict(hp=60.0, speed=4.6, wander=1.1, dmg=9.0, cooldown=0.9, windup=0.35,
                  aggro=24.0, scale=1.0, hear=1.0),
    "brute": dict(hp=220.0, speed=3.0, wander=0.9, dmg=22.0, cooldown=1.5, windup=0.55,
                  aggro=18.0, scale=1.55, hear=0.8),                # schwerhörig
    "huntress": dict(hp=45.0, speed=6.4, wander=1.3, dmg=8.0, cooldown=0.65, windup=0.28,
                     aggro=30.0, scale=0.96, hear=1.3),             # flink, zerbrechlich, gute Ohren
    # Koloss: 3x so gross, 780 HP (3,5x Brute). Leichter Schlag: holt 1,2 s sichtbar aus, 85 Schaden (fast
    # One-Hit). Bodenschlag: holt 2,4 s aus, Flächenschaden im Umkreis slam_r - im Zentrum (slam_kill) tödlich,
    # nach aussen linear weniger. Bodenschlag, wenn 2+ Spieler in slam_crowd m sind, sonst mit slam_chance.
    "colossus": dict(hp=780.0, speed=1.9, wander=0.6, dmg=85.0, cooldown=2.8, windup=1.2, recover=0.9,
                     aggro=24.0, scale=3.0, hear=0.9, slam_windup=2.4, slam_r=7.0, slam_dmg=110.0,
                     slam_kill=3.0, slam_chance=0.25, slam_crowd=8.0),
    # Titan (Boss): 7x so gross wie ein Grunt (2,3x Koloss), 4500 HP, langsam, eher stationär. Drei Angriffe:
    # leichter Schlag im Nahbereich (dmg, praktisch One-Shot), Stampfer wie der Koloss mit grösserem Radius
    # (slam_*), und ab rock_min m der Steinwurf: holt mit dem Fuss aus (rock_windup), reisst einen Brocken aus
    # dem Boden und tritt ihn auf den Spieler (ROCK_*). Ab rock_max m läuft er langsam heran.
    "titan": dict(hp=4500.0, speed=1.4, wander=0.45, dmg=160.0, cooldown=3.2, windup=1.6, recover=1.2,
                  aggro=45.0, scale=7.0, hear=0.8, slam_windup=3.2, slam_r=11.0, slam_dmg=150.0,
                  slam_kill=4.5, slam_chance=0.3, slam_crowd=12.0,
                  rock_min=20.0, rock_max=70.0, rock_windup=2.4, rock_recover=1.4),
    # Elektro-Drohne: schwebt in fly m Höhe, schiesst aus bis zu range m (freie Sicht nötig); kein Schaden,
    # betäubt für STUN_MIN..STUN_MAX s. Wenig HP, aber klein (hit_r/hit_h) und in der Luft.
    "drone": dict(hp=35.0, speed=5.5, wander=2.0, dmg=0.0, cooldown=7.0, windup=0.6, recover=0.3,
                  aggro=30.0, scale=1.0, hear=1.1, fly=3.6, range=20.0, hit_r=0.42, hit_h=0.5),
    # Fluchttier: greift nie an (calm). Sieht (aggro) oder hört es einen Spieler, flieht es in Haken
    # (Strecken CRITTER_LEG_MIN..MAX m, Richtung zufällig, aber grob weg vom Auslöser).
    "critter": dict(hp=20.0, speed=11.5, wander=1.6, dmg=0.0, cooldown=1.0, windup=0.3, aggro=16.0,
                    scale=0.55, hear=1.2, calm=True),
}
STUN_MIN, STUN_MAX = 1.0, 3.0   # s Betäubung durch die Drohne (zufällig dazwischen)
STUN_IMMUNE = 3.0               # s nach dem Ende einer Betäubung: immun (Drohnen schiessen dann gar nicht)
DRONE_MAX_PER_TARGET = 1        # höchstens so viele Drohnen beschiessen gleichzeitig denselben Spieler
CRITTER_LEG_MIN, CRITTER_LEG_MAX = 7.0, 11.0   # m je Fluchthaken
CRITTER_TURN = 75.0             # Grad: so weit darf ein Haken von "weg vom Auslöser" abweichen
CRITTER_FLEE_T = 8.0            # s Flucht nach dem letzten Alarm
CRITTER_COLORS = {"standard": (0.52, 0.42, 0.30),   # Fell des Fluchttiers (Feldhase, braun-grau), je Kartenart;
                  "karte": (0.52, 0.42, 0.30)}      # alle Exemplare gleich, unauffällig (kein Leuchten)
# Buffs beim Töten eines Fluchttiers (einer zufällig): Tempo, Schaden, Tank
BUFF_KINDS = ("speed", "damage", "tank")
BUFF_NAMES = {"speed": "Tempo", "damage": "Schaden", "tank": "Tank"}
BUFF_T = {"speed": 10.0, "damage": 15.0, "tank": 30.0}   # s
BUFF_SPEED = 1.4                # Tempo-Buff: +40 % Lauf- und Renntempo
BUFF_DAMAGE = 1.5               # Schadens-Buff: eigene Treffer (Kugeln, Explosionen) 150 %
BUFF_TANK_HP = (150.0, 200.0)   # Tank-Buff: max. Leben zufällig eines davon (HP werden mitskaliert)
HUD_MARGIN = 0.05                     # einheitlicher Abstand der HUD-Elemente zum Bildrand
HUD_TEXT = 0.042                      # Schriftgrösse für Killfeed, Legende, Tooltips
FEED_T, FEED_N = 6.0, 5               # Killfeed: so lange (s) und höchstens so viele Zeilen
TAB_COLS = ((-0.88, "l"), (-0.78, "l"), (-0.05, "r"), (0.13, "r"), (0.3, "r"), (0.52, "r"), (0.71, "r"), (0.88, "r"))
TAB_W = 0.95                          # halbe Breite der Tab-Übersicht (passt auch bei 4:3 zwischen die HUD-Ränder)
GEAR_HUD_W, GEAR_HUD_H = 0.26, 0.15   # Ausrüstungs-Kacheln am rechten Rand (Breite, Höhe)
GEAR_HUD_Y0 = 0.17                    # Mitte der oberen Kachel (Kopf), relativ zur Bildschirmmitte
GEAR_HUD_TEXT = 0.038                 # Schriftgrösse des getragenen Teils
TOAST_T = 3.0                   # s: so lange steht ein Hinweis wie "Buff: Schaden 150 % - 15 s" in der Bildmitte


KEY_LEGEND = (("W A S D", "laufen"), ("Shift", "rennen / Dash"), ("Leertaste", "springen / Jetpack"),
              ("Maus", "umschauen"), ("Linke M.", "schiessen"), ("Rechte M.", "zielen"), ("R", "nachladen"),
              ("1 2 3", "Waffe wählen"), ("Mausrad", "Waffe wechseln"), ("G", "Granate"), ("F", "benutzen / Nahkampf"),
              ("4", "Nahkampfwaffe"),
              ("V", "Wagen: Schütze"), ("Q / E", "lehnen"), ("Strg / C", "ducken"), ("Tab", "Übersicht"),
              ("M", "Ton an/aus"), ("F3", "Bildrate"), ("Esc", "Menü"))


MOB_NAMES = {"grunt": "Grunt", "brute": "Brute", "huntress": "Jägerin", "colossus": "Koloss", "drone": "Drohne",
             "critter": "Hase", "titan": "Titan"}


def end_tabs(koth):
    """Reiter des Endbildschirms: (Titel, [(Spaltenkopf, Wert(e) -> Zahl/Text, hervorheben?)],
    Ehrentitel, Wert(e) für den Ehrentitel). Neue Statistik = neue Spalte/neuer Reiter hier."""
    kd = lambda e: e["kills"] / max(1, e["deaths"])                                       # noqa: E731
    st = lambda e, k: e["stats"].get(k, 0)                                                  # noqa: E731
    mob = lambda e, k: e["stats"].get("mob", {}).get(k, 0)                                  # noqa: E731
    crate = lambda e, k: e["stats"].get("crate", {}).get(k, 0)                              # noqa: E731
    tabs = [("Übersicht", ([("Punkte", lambda e: int(e["score"]), True)] if koth else [])
             + [("Kills", lambda e: e["kills"], True), ("Tode", lambda e: e["deaths"], False),
                ("K/D", lambda e: round(kd(e), 2), True)]
             + ([("Zeit in der Burg", lambda e: f"{int(st(e, 'zone_t')) // 60}:{int(st(e, 'zone_t')) % 60:02d}",
                  False)] if koth else []),
             "Sieger", None),
            ("Jäger", [(MOB_NAMES.get(k, k), (lambda e, k=k: mob(e, k)), True) for k in KINDS]
             + [("Gesamt", lambda e: sum(e["stats"].get("mob", {}).values()), True)],
             "Meister-Jäger", lambda e: sum(e["stats"].get("mob", {}).values())),
            ("Looten", [(CRATE_NAMES[k].split()[0].capitalize() if k in CRATE_NAMES else k, (lambda e, k=k: crate(e, k)), True)
                        for k in CRATE_KINDS]
             + [("Gesamt", lambda e: sum(e["stats"].get("crate", {}).values()), True),
                ("Buffs", lambda e: st(e, "buffs"), True)],
             "Schatzsucher", lambda e: sum(e["stats"].get("crate", {}).values())),
            ("Tomahawk", [("Ausgelöst", lambda e: st(e, "toma_fired"), True),
                          ("Tomahawk-Kills", lambda e: st(e, "toma_kills"), True)],
             "Raketen-Profi", lambda e: st(e, "toma_kills") * 100 + st(e, "toma_fired")),
            ("Special Shots", [("Nahkampf-Kills", lambda e: st(e, "melee_kills"), True),
                               ("Weitester Kill", lambda e: f"{st(e, 'longest'):.0f} m" if st(e, "longest") else "-", False),
                               ("mit", lambda e: weapon_name(st(e, "longest_w")) if st(e, "longest_w") >= 0 else "-", False),
                               ("Kopfschüsse", lambda e: st(e, "heads"), True),
                               ("Treffer", lambda e: st(e, "hits"), True),
                               ("Kopf-Quote", lambda e: f"{100 * st(e, 'heads') / max(1, st(e, 'hits')):.0f} %", False)],
             "Scharfschütze", lambda e: st(e, "longest")),
            ("Bewegung", [("Zu Fuss", lambda e: f"{st(e, 'walk'):.0f} m", False),
                          ("Im Wagen", lambda e: f"{st(e, 'drive'):.0f} m", False),
                          ("Fahrten", lambda e: st(e, "drives"), True),
                          ("Im Heli", lambda e: f"{st(e, 'fly'):.0f} m", False),
                          ("Flüge", lambda e: st(e, "flights"), True)],
             "Weltenbummler", lambda e: st(e, "walk") + st(e, "drive") + st(e, "fly"))]
    return tabs


def weapon_info(wi, gun=None):
    """Mausover-Info einer Waffe - direkt aus WEAPONS (stimmt nach Balancing-Änderungen automatisch)."""
    w = WEAPONS[wi]
    lines = [w.name + ("  (Spezialwaffe)" if w.kind == "special" else "")]
    if w.blast_r > 0:
        lines.append(f"Explosion: {w.blast_dmg:.0f} Schaden, Radius {w.blast_r:.0f} m")
    else:
        lines.append(f"Schaden: {w.dmg:.0f} pro {'Schrot' if w.pellets > 1 else 'Schuss'}"
                     + (f" x {w.pellets}" if w.pellets > 1 else "") + "  (Kopf x2)")
    rpm = 60.0 / w.interval
    lines.append(f"Feuerrate: {rpm:.0f} Schuss/min" + ("  (Dauerfeuer)" if w.auto else ""))
    mag = f"Magazin: {gun.mag}/{w.mag}" if gun is not None else f"Magazin: {w.mag}"
    res = f"   Reserve: {gun.reserve}" if gun is not None else f"   Reserve max. {w.max_reserve}"
    lines.append(mag + res)
    lines.append(f"Nachladen: {w.reload:.1f} s")
    lines.append(f"Streuung: {w.spread:.1f}° (zielen x{w.ads_spread:g})")
    extra = []
    if w.scope:
        extra.append("Zielfernrohr")
    if w.sight == "rocket":
        extra.append("Visier mit Entfernungsmesser")
    if w.grav < 0.5:
        extra.append("kaum Kugelfall")
    extra.append(f"Tempo {w.speed:.0f} m/s")
    lines.append(", ".join(extra))
    return "\n".join(lines)


def melee_info(mi):
    """Mausover-Info der Nahkampfwaffe - aus MELEE."""
    m = MELEE[mi]
    return (f"{m.name}  (Nahkampf)\nSchaden: {m.dmg:.0f}  (Kopf x{m.head:g})\n"
            f"Tempo: {60.0 / m.interval:.0f} Schläge/min\nReichweite: {m.reach:.1f} m, Winkel ±{m.arc:.0f}°\n"
            f"Leise (Lärm {NOISE_MELEE:.0f} m); ahnungslose Monster x{MELEE_SNEAK:g}")


def gear_info(gi):
    """Mausover-Info eines Ausrüstungsteils - aus GEAR und den Konstanten."""
    g = GEAR[gi]
    desc = {
        "save_head": f"Fängt einen tödlichen Kopftreffer ab (du überlebst mit {SAVE_HP:.0f} HP),\n"
                     "danach zerstört. Nicht gegen Tomahawk, Nahgranate, Sturz.",
        "save_body": f"Fängt einen tödlichen Körpertreffer ab (du überlebst mit {SAVE_HP:.0f} HP),\n"
                     "danach zerstört. Nicht gegen Tomahawk, Nahgranate, Sturz.",
        "shield": f"Schild {SHIELD_HP:.0f} HP fängt Schaden vor den Lebenspunkten ab.\n"
                  f"{SHIELD_DELAY:.0f} s ohne Treffer: lädt mit {SHIELD_RATE:.0f} HP/s auf.",
        "jetpack": f"Leertaste in der Luft halten: Schub.\nTreibstoff {JET_FUEL:.0f} s, leer -> voll in {JET_REFILL_T:.0f} s.",
        "dash": f"Shift beim Laufen: Dash {DASH_DIST:.0f} m nach vorne in {DASH_TIME:.1f} s,\n{DASH_CD:.0f} s Abklingzeit.",
        "spring": f"Springt deutlich höher (Sprungkraft x{SPRING_JUMP:g}).",
        "double_jump": "Leertaste in der Luft: Doppelsprung.",
    }.get(g.kind, "")
    return f"{g.name}  ({GEAR_SLOT_NAMES[g.slot]})\n{desc}"


def buff_info(kind, pl=None):
    left = f"   noch {int(math.ceil(pl.buff_t))} s" if pl is not None and pl.buff_t > 0 else ""
    desc = {"speed": f"Du läufst und rennst {int(round((BUFF_SPEED - 1) * 100))} % schneller.",
            "damage": f"Deine Treffer machen {int(round(BUFF_DAMAGE * 100))} % Schaden (Spieler und Monster).",
            "tank": "Mehr maximale Lebenspunkte; danach anteilig zurück auf 100."}.get(kind, "")
    return f"Buff: {buff_text(kind, getattr(pl, 'max_hp', PLAYER_HP))}{left}\n{desc}"


def buff_text(kind, max_hp=PLAYER_HP):
    """Buff als kurzer Text mit Wirkung: "Schaden 150 %", "Tempo +40 %", "Tank 200 HP"."""
    if kind == "damage":
        return f"Schaden {int(round(BUFF_DAMAGE * 100))} %"
    if kind == "speed":
        return f"Tempo +{int(round((BUFF_SPEED - 1) * 100))} %"
    if kind == "tank":
        return f"Tank {int(max_hp)} HP"
    return BUFF_NAMES.get(kind, str(kind))

# --- Lärm: Monster hören Spieler. Ein Geräusch alarmiert alle Monster im Radius (x hear der Art); aggressive
# laufen zum Ort des Geräuschs (nicht direkt zum Spieler!) und suchen dort, Fluchttiere fliehen.
# Die Radien orientieren sich an der Sichtweite der Monster (aggro 18-30 m): Schleichen bleibt darunter,
# Laufen etwa halb so weit, Sprinten etwa so weit wie sie sehen, ein Schuss weckt ein ganzes Areal.
NOISE_CROUCH = 3.0        # geduckt: fast lautlos, nur direkt daneben
NOISE_WALK = 10.0         # normal laufen: die nähere Umgebung
NOISE_RUN = 22.0          # sprinten: deutlich weiter
NOISE_SHOT = 60.0         # Schuss (x Weapon.loud: Pistole 0,75 ... Raketenwerfer 1,4)
NOISE_EXPLOSION = 90.0    # Granate, Rakete, zerstörtes Fahrzeug
NOISE_TOMAHAWK = 160.0    # Tomahawk-Einschlag
NOISE_VEHICLE = 30.0      # fahrender Wagen (wie Sprinten, etwas lauter)
NOISE_HELI = 55.0         # fliegender Helikopter
NOISE_TICK = 0.4          # s: so oft wird der Bewegungslärm der Spieler ausgewertet
NOISE_SEARCH_T = 5.0      # s: so lange sucht ein Monster am Geräuschort, dann zurück zu idle/wandern
NOISE_INVESTIGATE = 0.75  # Faktor aufs Lauftempo beim Hinlaufen zum Geräusch
# Monster-Geräusche (5d). Je Art: Schritt-Sound, Schrittweite (m, wächst mit der Grösse), Lautstärke, Tonhöhe;
# Laut (Knurren/Fauchen) mit zufälligem Abstand voice_gap (s) - nie als Dauerschleife; range = Hörweite (m).
MOB_SND = {
    "grunt":    dict(range=40, step="mstep", stride=1.5, step_vol=0.45, step_rate=(1.05, 1.25),
                     voice="growl", voice_gap=(7.0, 16.0), voice_vol=0.55, voice_rate=(0.95, 1.15)),
    "brute":    dict(range=50, step="mstep_heavy", stride=1.6, step_vol=0.7, step_rate=(0.7, 0.85),
                     voice="growl_deep", voice_gap=(8.0, 18.0), voice_vol=0.75, voice_rate=(0.9, 1.05)),
    "huntress": dict(range=32, step="mstep", stride=1.4, step_vol=0.18, step_rate=(1.35, 1.6),   # schleichend
                     voice="hiss", voice_gap=(9.0, 20.0), voice_vol=0.5, voice_rate=(0.95, 1.12)),
    "colossus": dict(range=90, step="mstep_heavy", stride=1.3, step_vol=1.0, step_rate=(0.45, 0.55),
                     voice="growl_deep", voice_gap=(10.0, 20.0), voice_vol=0.9, voice_rate=(0.55, 0.65)),
    "titan":    dict(range=160, step="mstep_giant", stride=0.9, step_vol=1.0, step_rate=(0.6, 0.72),
                     voice="growl_deep", voice_gap=(12.0, 24.0), voice_vol=1.0, voice_rate=(0.35, 0.42)),
    "drone":    dict(range=45),                                         # Surren statt Schritte (s. MOB_VOL)
    "critter":  dict(range=18, step="tap", stride=0.7, step_vol=0.35, step_rate=(0.9, 1.2)),
}
MOB_VOL = {"drone_hum": 0.35, "drone_scan": 0.7, "drone_charge": 0.75, "colossus_rumble": 0.85,
           "colossus_build": 0.9, "titan_rumble": 1.0, "titan_build": 1.0, "titan_rip": 1.0, "rock_fly": 0.8,
           "critter_squeak": 0.55}
MOB_SND_NEAREST = 8       # nur die so vielen nächsten Monster werden vertont
MOB_SND_MAX = 3           # höchstens so viele Monsterlaute (Knurren usw.) je MOB_SND_WINDOW Sekunden
MOB_SND_WINDOW = 1.5
MOB_SND_HUMS = 2          # höchstens so viele Drohnen surren gleichzeitig
MOB_SND_ROCKS = 3         # höchstens so viele fliegende Brocken rauschen gleichzeitig
# Vorbeizischende Kugeln (5b, nur Ton beim Spieler): fremde Kugel bis WHIZ_FULL m am Kopf vorbei = volle
# Lautstärke, bis WHIZ_MAX leiser werdend, darüber nichts. Eigene Schüsse zischen nicht.
WHIZ_FULL = 1.0
WHIZ_MAX = 3.0
WHIZ_VOL = 0.9
# Kugeln entlang ihrer Flugbahn (5b): Monster, an denen eine Kugel vorbeifliegt oder neben denen sie einschlägt,
# laufen grob in die Richtung, aus der sie kam, und suchen dort.
BULLET_NOISE_R = 3.0      # m: so nah muss eine Kugel an einem Monster vorbeifliegen
BULLET_IMPACT_R = 4.0     # m: so nah muss sie neben ihm einschlagen
BULLET_ALERT_MIN, BULLET_ALERT_MAX = 10.0, 20.0   # m: so weit läuft es in Richtung Herkunft
BULLET_SEARCH_T = 5.0     # s: so lange sieht es sich dort um, dann zurück zu idle/wandern
BULLET_DIR_ERR = 25.0     # Grad: so ungenau schätzt es die Herkunftsrichtung
MOB_HIT_RUN = 80.0        # m: angeschossen läuft es bis zu so weit in Richtung Schütze (auch ohne Sicht)
MOB_HIT_SEARCH_T = 6.0    # s: Suchzeit dort
MOB_HIT_ERR = 8.0         # Grad: Richtungsfehler nach einem Treffer (spürt genauer, woher es kam)
MOB_HIT_SPEED = 1.0       # Faktor aufs Lauftempo beim Hinlaufen nach einem Treffer
NOISE_MINIMAP = True      # eigenen Lärm auf der Minimap zeigen (Kreis beim Laufen, Welle bei Schuss/Explosion)
NOISE_MINIMAP_ZOOM = True # Welle grösser als der Ausschnitt: Minimap zoomt kurz heraus und wieder zurück
NOISE_MM_ALPHA = 0.10     # Deckkraft der Kreisfläche (Rand etwas deutlicher)
NOISE_WAVE_T = 0.7        # s: so lange breitet sich eine Schuss-Welle aus (Explosion: etwas länger)
NOISE_ZOOM_MAX = 200.0    # m: weiter zoomt die Minimap nie heraus
NOISE_DEBUG = False       # True: Lärmradien als Ringe am Boden anzeigen (Einzelspiel/Host)


# --------------------------------------------------------------- Spiellogik
def hills(x, y):
    return (math.sin(x * 0.045) * math.cos(y * 0.038) * 3.2
            + math.sin(x * 0.11 + 1.3) * math.sin(y * 0.09) * 1.2
            + math.sin((x + y) * 0.02) * 2.0)


def mountain(x, y):
    """Gebirgszug am Rand der Standardkarte: 0 im Inneren, steigt zum Rand hin (erst sanfte Ausläufer,
    dann steile Felswände) und hinter dem Rand weiter. Gipfel und Sättel wechseln sich ab."""
    W = WORLD
    ex, ey = min(x, W - x), min(y, W - y)
    k = 16.0                                             # weiche Ecken (Soft-Minimum der Randabstände)
    m = min(ex, ey)
    d = m - k * math.log(math.exp((m - ex) / k) + math.exp((m - ey) / k))
    wob = (6.0 * math.sin(x * 0.037 + 1.9) + 5.0 * math.sin(y * 0.041 - 0.6)
           + 3.0 * math.sin((x - y) * 0.023 + 0.4))      # Breite des Gürtels schwankt
    t = (MTN_BAND + wob - d) / (MTN_BAND + wob)
    if t <= 0.0:
        return 0.0
    peaks = 0.62 + 0.38 * (0.5 + 0.5 * math.sin(x * 0.061 + 0.8) * math.cos(y * 0.057 - 1.3))
    if t <= 1.0:
        h = MTN_H * peaks * t ** 3
    else:                                                # hinter dem Kartenrand: weiter bergauf, flacher
        h = MTN_H * peaks * (1.0 + 1.6 * (1.0 - math.exp(-(t - 1.0) * 1.5)))
    rug = (1.4 * math.sin(x * 0.19 + 0.3) * math.sin(y * 0.23 - 0.9)
           + 0.8 * math.sin(x * 0.47 + y * 0.31)) * min(1.0, t * 1.4)   # Felsstruktur
    return max(0.0, h + rug * min(1.0, t * 2.0))


# ------------------------------------------------------------ Kartendateien (vom Karteneditor)
MAP_FORMAT = "polybash-map"
MAP_COLORS = {"stone": STONE, "stone_d": STONE_D, "plaster": PLASTER, "wood": WOOD_F, "concrete": CONCRETE,
              "roof": ROOF, "cobble": COBBLE, "metal": (0.55, 0.57, 0.60), "dark": (0.30, 0.30, 0.32),
              "brick": (0.55, 0.30, 0.24)}
MAP_MAX = dict(ponds=24, rocks=300, trees=700, blocks=800, houses=60, towers=30, ruins=30, spawns=80,
               crates=60, turrets=40, vehicles=12, pads=8)


def _mnum(v, lo, hi, default=None):
    try:
        f = float(v)
    except (TypeError, ValueError):
        return default
    if not math.isfinite(f):
        return default
    return min(hi, max(lo, f))


def decode_terrain(t):
    """Höhenraster aus der Kartendatei -> (n, schritt, Liste in Metern) oder None."""
    import base64
    import zlib
    from array import array
    if not isinstance(t, dict):
        return None
    try:
        n, step = int(t.get("n", 0)), float(t.get("step", 0))
        if not (3 <= n <= 401) or abs((n - 1) * step - MAP_WORLD) > 0.01:
            return None
        raw = base64.b64decode(str(t.get("z", "")))
        if t.get("enc", "zlib") == "zlib":
            raw = zlib.decompress(raw)
        a = array("h")
        a.frombytes(raw)
        if sys.byteorder == "big":
            a.byteswap()
        if len(a) != n * n:
            return None
        return n, step, [min(14.0, max(-6.0, v / 10.0)) for v in a]
    except Exception:
        return None


def sanitize_map(raw):
    """Prüft eine Kartendatei und gibt eine bereinigte Fassung zurück (ValueError bei Unsinn).
    Fehlt eine Liste, nimmt das Spiel für diese Sache die Standard-Karte; eine vorhandene (auch leere) Liste gilt wörtlich."""
    if not isinstance(raw, dict) or raw.get("format") != MAP_FORMAT:
        raise ValueError("Das ist keine Polybash-Karte")
    m = {"name": str(raw.get("name") or "Karte")[:40], "author": str(raw.get("author") or "")[:30]}
    kp = raw.get("keep") if isinstance(raw.get("keep"), dict) else {}
    m["keep"] = {k: bool(kp.get(k, True)) for k in ("castle", "runway", "tunnels")}
    m["terrain"] = decode_terrain(raw.get("terrain"))

    def lst(key):
        v = raw.get(key)
        if not isinstance(v, list):
            return None
        return v[:MAP_MAX[key]]

    def pt(v, lo=2.0):
        if not isinstance(v, (list, tuple)) or len(v) < 2:
            return None
        x, y = _mnum(v[0], lo, MAP_WORLD - lo), _mnum(v[1], lo, MAP_WORLD - lo)
        return None if x is None or y is None else (x, y)

    def circ(key, rlo, rhi):
        v = lst(key)
        if v is None:
            return None
        out = []
        for it in v:
            p = pt(it)
            r = _mnum(it[2], rlo, rhi) if p and len(it) > 2 else None
            if p and r:
                out.append((p[0], p[1], r))
        return out

    m["ponds"], m["rocks"], m["trees"] = circ("ponds", 2.0, 14.0), circ("rocks", 0.4, 3.0), circ("trees", 1.0, 4.0)
    v = lst("blocks")
    if v is not None:
        out = []
        for b in v:
            if not isinstance(b, dict):
                continue
            xs = [_mnum(b.get("x0"), 0, MAP_WORLD), _mnum(b.get("x1"), 0, MAP_WORLD)]
            ys = [_mnum(b.get("y0"), 0, MAP_WORLD), _mnum(b.get("y1"), 0, MAP_WORLD)]
            h = _mnum(b.get("h"), 0.2, 30.0)
            if None in xs or None in ys or h is None:
                continue
            c = b.get("c")
            col = MAP_COLORS.get(c) if isinstance(c, str) else None
            if col is None and isinstance(c, list) and len(c) == 3:
                col = tuple(_mnum(q, 0.0, 1.0, 0.5) for q in c)
            x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
            if x1 - x0 < 0.3 or y1 - y0 < 0.3:
                continue
            out.append(dict(x0=x0, y0=y0, x1=x1, y1=y1, h=h, c=col or STONE_D, mm=bool(b.get("mm", h >= 2.0))))
        v = out
    m["blocks"] = v
    v = lst("houses")
    if v is not None:
        out = []
        for b in v:
            if not isinstance(b, dict):
                continue
            x, y = _mnum(b.get("x"), 6, MAP_WORLD - 6), _mnum(b.get("y"), 6, MAP_WORLD - 6)
            w, d, h = _mnum(b.get("w"), 3, 30), _mnum(b.get("d"), 3, 30), _mnum(b.get("h"), 2.2, 9.0)
            if None in (x, y, w, d, h):
                continue
            sides = lambda k: "".join(c for c in "NSEW" if c in str(b.get(k, "")))      # noqa: E731
            col = MAP_COLORS.get(b.get("c")) if isinstance(b.get("c"), str) else None
            out.append(dict(x=x, y=y, w=w, d=d, h=h, doors=sides("doors"), win=sides("win"), crate=bool(b.get("crate")),
                            c=col or PLASTER))
        v = out
    m["houses"] = v
    v = lst("towers")
    if v is not None:
        out = []
        for b in v:
            if isinstance(b, dict):
                x, y = _mnum(b.get("x"), 6, MAP_WORLD - 6), _mnum(b.get("y"), 6, MAP_WORLD - 6)
                if x is not None and y is not None:
                    out.append(dict(x=x, y=y, side=b.get("side") if b.get("side") in ("N", "S", "E", "W") else "E",
                                    crate=bool(b.get("crate", True))))
        v = out
    m["towers"] = v
    for key in ("ruins", "spawns", "crates"):
        v = raw.get(key)
        if isinstance(v, list):
            v = [p for p in (pt(it, 4.0) for it in v[:MAP_MAX[key]]) if p]
        else:
            v = None
        m[key] = v
    v = lst("turrets")
    if v is not None:
        out = []
        for b in v:
            if isinstance(b, dict):
                x, y = _mnum(b.get("x"), 4, MAP_WORLD - 4), _mnum(b.get("y"), 4, MAP_WORLD - 4)
                if x is not None and y is not None:
                    out.append((x, y, "flak" if b.get("kind") == "flak" else "mg"))
        v = out
    m["turrets"] = v
    for key in ("vehicles", "pads"):
        v = lst(key)
        if v is not None:
            out = []
            for it in v:
                p = pt(it, 8.0)
                if p:
                    out.append((p[0], p[1], _mnum(it[2], -720, 720, 0.0) if len(it) > 2 else 0.0))
            v = out
        m[key] = v
    return m


def map_dirs():
    base = os.path.dirname(sys.executable) if getattr(sys, "frozen", False) else os.path.dirname(os.path.abspath(__file__))
    out = [os.path.join(base, "maps")]
    if os.path.abspath(os.getcwd()) != os.path.abspath(base):
        out.append(os.path.join(os.getcwd(), "maps"))
    bundle = getattr(sys, "_MEIPASS", None)             # in der Einzeldatei-Executable entpackte Daten
    if bundle:
        out.append(os.path.join(bundle, "maps"))
    return out


def list_maps():
    """Kartendateien im Ordner 'maps' neben dem Spiel: [(Anzeigename, Pfad)]."""
    found = []
    for d in map_dirs():
        try:
            names = sorted(os.listdir(d))
        except OSError:
            continue
        for fn in names:
            if fn.lower().endswith(".mcmap"):
                path = os.path.join(d, fn)
                try:
                    found.append((str(mc_read_header(path).get("name") or os.path.splitext(fn)[0])[:30], path))
                except (OSError, ValueError):
                    pass
            elif fn.lower().endswith((".json", ".polymap")):
                path = os.path.join(d, fn)
                try:
                    with open(path, encoding="utf-8") as f:
                        raw = json.load(f)
                    if isinstance(raw, dict) and raw.get("format") == MAP_FORMAT:
                        found.append((str(raw.get("name") or os.path.splitext(fn)[0])[:30], path))
                except (OSError, ValueError):
                    pass
    return found


# ---------------------------------------------------------------- Minecraft-Karten (.mcmap)
MC_FORMAT = "polybash-mcmap"
MC_MAGIC = b"PBMC1\n"


def _mc_head(f):
    if f.read(len(MC_MAGIC)) != MC_MAGIC:
        raise ValueError("keine Minecraft-Karte")
    n = struct.unpack("<I", f.read(4))[0]
    if n > 65536:
        raise ValueError("Kopfzeile zu gross")
    h = json.loads(f.read(n).decode("utf-8"))
    if not isinstance(h, dict) or h.get("format") != MC_FORMAT:
        raise ValueError("falsches Kartenformat")
    return h


def mc_read_header(path):
    """Kopfzeile einer .mcmap-Datei (Name, Autor, Kennung) - ohne die Geometrie zu laden."""
    with open(path, "rb") as f:
        return _mc_head(f)


def mc_find(map_id):
    """Pfad der lokalen .mcmap-Datei mit dieser Kennung (oder None)."""
    for _name, path in list_maps():
        if path.lower().endswith(".mcmap"):
            try:
                if mc_read_header(path).get("id") == map_id:
                    return path
            except (OSError, ValueError):
                pass
    return None


def load_mcmap(path):
    """Minecraft-Karte laden: {'head', 'meta', 'tex': {name: (w, h, bytes)}, 'groups': [...], 'boxes': [...],
    'minimap': bytes}. Die Geometrie liegt als Quads vor (Positionen in 1/64 m, Texturkoordinaten in 1/16 Texel)."""
    with open(path, "rb") as f:
        head = _mc_head(f)
        blen = struct.unpack("<I", f.read(4))[0]
        blob = zlib.decompress(f.read(blen))
    mlen = struct.unpack_from("<I", blob, 0)[0]
    meta = json.loads(blob[4:4 + mlen].decode("utf-8"))
    pos = 4 + mlen
    tex = {}
    for t in meta["tex"]:
        n = t["w"] * t["h"] * 4
        tex[t["n"]] = (t["w"], t["h"], t["a"], blob[pos:pos + n])
        pos += n
    groups = []
    for g in meta["groups"]:
        nq = g["n"]
        P, UV, C = array("h"), array("h"), array("B")
        P.frombytes(blob[pos:pos + nq * 24]); pos += nq * 24
        UV.frombytes(blob[pos:pos + nq * 16]); pos += nq * 16
        C.frombytes(blob[pos:pos + nq * 16]); pos += nq * 16
        groups.append({"tex": g["tex"], "kind": g["kind"], "n": nq, "P": P, "UV": UV, "C": C})
    nb = meta["nbox"]
    boxes = array("f")
    boxes.frombytes(blob[pos:pos + nb * 24]); pos += nb * 24
    mm = blob[pos:pos + meta["mm"] * meta["mm"] * 3]
    if sys.byteorder != "little":
        for a in [g[k] for g in groups for k in ("P", "UV")] + [boxes]:
            a.byteswap()
    return {"head": head, "meta": meta, "tex": tex, "groups": groups, "boxes": boxes, "minimap": mm}


def mc_mapdata(path):
    """Kartendaten für World: wie sanitize_map, dazu der Schlüssel 'mc' mit der geladenen Minecraft-Welt."""
    mc = load_mcmap(path)
    md = sanitize_map({"format": MAP_FORMAT, "name": mc["head"].get("name", "Minecraft")})
    md["mc"] = mc
    raw = {"format": MC_FORMAT, "id": mc["head"].get("id"), "name": mc["head"].get("name")}
    return md, raw


class Prop:
    def __init__(self, kind, x, y, r, solid_r):
        self.kind, self.x, self.y = kind, x, y
        self.r = r                # Sichtradius (für Platzierung)
        self.solid_r = solid_r    # Kollisionsradius
        self.z = 0.0
        self.base_r = r
        self.hit_r = 0.0          # Trefferzylinder für Kugeln (0 = Kugeln fliegen durch)
        self.hit_h = 0.0


class Bullet:
    def __init__(self, x, y, z, vx, vy, vz, dmg, owner=0, bid=0, wi=-1):
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.dmg = dmg
        self.owner = owner        # Spieler-ID des Schützen (für Munition/Trefferanzeige)
        self.bid = bid            # Kugel-ID (für das Netzwerk)
        self.wi = wi              # Waffe, aus der die Kugel stammt
        wp = WEAPONS[wi] if 0 <= wi < len(WEAPONS) else None
        self.grav = wp.grav if wp else 1.0
        self.blast_r = wp.blast_r if wp else 0.0
        self.blast_dmg = wp.blast_dmg if wp else 0.0
        self.life = 4.0
        self.travel = 0.0
        self.alerted = set()      # Monster, die diese Kugel schon bemerkt haben (nur Host)


class Grenade:
    """Wurfgranate (Host simuliert, Mitspieler bekommen Position und Geschwindigkeit)."""

    def __init__(self, gid, x, y, z, vx, vy, vz, owner, fuse=GREN_FUSE):
        self.gid, self.owner = gid, owner
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.fuse = fuse


class Drop:
    """Waffe, Ausrüstungsteil oder Nahkampfwaffe am Boden (F zum Aufheben). wi = Waffe (-1 sonst),
    gear = Teil (-1), melee = Nahkampfwaffe (-1)."""

    def __init__(self, did, x, y, z, wi, gear=-1, melee=-1):
        self.did, self.x, self.y, self.z, self.wi = did, x, y, z, wi
        self.gear = gear
        self.melee = melee
        self.life = DROP_LIFE


class Turret:
    """Stationäre Waffe, von einem Spieler bedient (F am Geschütz). Unbegrenzte Munition, aber sie
    heizt sich auf; nach Überhitzung (over) zwingt die Pause zur Abkühlung.
    kind: mg (Turm), flak (Burg, schiesst in die Luft), car (hinten auf dem Geländewagen)."""

    def __init__(self, tid, x, y, z, heading, kind="mg", vid=-1):
        self.id, self.x, self.y, self.z = tid, x, y, z     # z = Drehpunkt (Höhe der Rohrmitte)
        self.kind, self.vid = kind, vid
        self.heading, self.pitch = heading, 0.0
        self.heat, self.over, self.firing = 0.0, False, False
        self.cd = 0.0
        self.op = -1                                       # Spieler-ID des Bedieners
        self.pmin, self.pmax = {"mg": (-65.0, 55.0), "flak": (-50.0, 88.0), "car": (-40.0, 50.0)}[kind]
        self.seat = 1.35 if kind != "car" else 1.25         # Drehpunkt über den Füssen des Schützen


class Heli:
    """Helikopter. Position bestimmt der Pilot (sein Rechner), Lebenspunkte/Munition der Host."""

    def __init__(self, hid, x, y, z, heading):
        self.id = hid
        self.home = (x, y, z, heading)
        self.reset()

    def reset(self):
        self.x, self.y, self.z, self.heading = self.home
        self.pitch = self.roll = self.speed = self.vx = self.vy = self.vz = 0.0
        self.hp, self.driver, self.dead_t = HELI_HP, -1, 0.0
        self.mg, self.rk = float(HELI_MG_MAX), HELI_RK_MAX
        self.ground = True
        self.stall_t = -1.0       # Drohne: Antrieb lahmgelegt (s, > 0) - der Heli sinkt; bis -1 s danach zählt
                                  # ein Aufprall noch als Folge (Netzlaufzeit)
        self.impact = 0.0         # Pilot: stärkster Aufprall seit der letzten Meldung (m/s)
        self.mg_cd = self.rk_cd = self.rel_t = 0.0
        self.firing = False
        self.side = 1


class Vehicle:
    """Geländewagen. Position und Tempo bestimmt der Fahrer (sein Rechner), Lebenspunkte der Host."""

    def __init__(self, vid, x, y, z, heading):
        self.id = vid
        self.home = (x, y, heading)
        self.x, self.y, self.z, self.heading = x, y, z, heading
        self.speed = 0.0
        self.hp = VEH_HP
        self.driver = -1          # Spieler-ID oder -1
        self.dead_t = 0.0         # Zeit seit der Zerstörung

        self.stall_t = 0.0        # Drohne: Motor aus (s) - der Wagen rollt aus

    def reset(self):
        self.x, self.y, self.heading = self.home
        self.speed, self.hp, self.driver, self.dead_t = 0.0, VEH_HP, -1, 0.0
        self.stall_t = 0.0


class Mob:
    def __init__(self, kind, x, y, world):
        k = MOB_KINDS[kind]
        rng = world.mrng
        self.id = 0               # wird vom World vergeben (für das Netzwerk)
        self.kind = kind
        self.x, self.y = x, y
        self.hover = k.get("fly", 0.0)                 # Flughöhe (Drohne), sonst 0
        self.gz = world.height(x, y)                   # Bodenhöhe unter dem Monster
        self.z = self.gz + self.hover
        self.scale = k["scale"]
        self.radius = k.get("hit_r", 0.45 * self.scale)
        self.height = k.get("hit_h", 1.9 * self.scale)
        self.reach = self.radius + PLAYER_R + 0.6 * self.scale   # Angriffsreichweite
        self.max_hp = self.hp = k["hp"]
        self.heading = rng.uniform(0, 360)
        self.state = "idle"       # idle | chase | attack | dead
        self.dead_t = 0.0
        self.hurt_t = 0.0
        self.alert_t = 0.0        # bleibt aggressiv, wenn angeschossen
        self.atk_cd = rng.uniform(0.0, 1.0)
        self.atk_t = 0.0
        self.did_hit = False
        self.wander_t = rng.uniform(0, 3)
        self.tx, self.ty = x, y
        self.kx = self.ky = 0.0   # Knockback-Geschwindigkeit
        self.phase = rng.uniform(0, 6.28)
        self.speed_now = 0.0
        self.noise_at = None      # (x, y) eines gehörten Geräuschs, zu dem es hinläuft
        self.search_t = 0.0       # restliche Suchzeit am Geräuschort
        self.searching = False    # schon am Geräuschort angekommen?
        self.inv_speed = NOISE_INVESTIGATE   # Tempo-Faktor beim Hinlaufen (Geräusch / Kugel / Treffer)
        self.fear = None          # nicht aggressive Arten: (x, y), wovor es flieht
        self.flee_from = None     # Punkt, von dem es gerade wegflieht
        self.flee_t = 0.0
        self.leg_left, self.leg_dir = 0.0, 0.0   # aktueller Fluchthaken: Reststrecke, Richtung (rad)
        self.atk_kind = 0         # 0 = normaler/leichter Angriff, 1 = Bodenschlag (Koloss)
        self.zap_pid, self.zap_hold = -1, 0.0   # Drohne: wen sie gerade beschiesst (für DRONE_MAX_PER_TARGET)
        self.next_slam = rng.random() < k.get("slam_chance", 0.0)

    def aggressive(self):
        return not MOB_KINDS[self.kind].get("calm", False)

    def on_noise(self, x, y, world):
        """Ein Geräusch bei (x, y) gehört. Jede Art entscheidet selbst: aggressive laufen hin und suchen,
        nicht aggressive (calm) fliehen davon weg."""
        if self.state == "dead":
            return
        if not self.aggressive():
            self.fear = (x, y)
            return
        if self.state in ("chase", "attack") and self.noise_at is None:
            return                                         # jagt schon einen Spieler, den es sieht
        self.noise_at = (x, y)
        self.search_t = NOISE_SEARCH_T
        self.searching = False
        self.inv_speed = NOISE_INVESTIGATE

    def on_shot(self, world, d, hit=False, shooter=None):
        """Eine Kugel flog nah vorbei / schlug daneben ein (hit=False) oder hat getroffen (hit=True). d = Flug-
        richtung der Kugel, shooter = (x, y) des Schützen, falls bekannt. Aggressive Monster drehen sich in
        Richtung Herkunft und laufen ein Stück dorthin (getroffen: Richtung Schütze, bis MOB_HIT_RUN), suchen
        dort und kehren dann zurück; sehen sie dabei einen Spieler, greifen sie an. Fluchttiere fliehen."""
        if self.state == "dead":
            return
        if not self.aggressive():
            self.fear = (self.x - d[0] * 5.0, self.y - d[1] * 5.0)   # weg von der Schussrichtung
            return
        if self.state == "attack" or (self.state == "chase" and self.noise_at is None and not hit):
            return                                         # kämpft schon / jagt einen Spieler, den es sieht
        rng = world.mrng
        bx, by = -d[0], -d[1]
        l = math.hypot(bx, by)
        if l < 1e-6:                                       # senkrecht von oben: Richtung unklar
            a = rng.uniform(0, 2 * math.pi)
        else:
            a = math.atan2(by, bx)
        if hit and shooter is not None:
            dist = min(MOB_HIT_RUN, math.hypot(shooter[0] - self.x, shooter[1] - self.y))
            a = math.atan2(shooter[1] - self.y, shooter[0] - self.x)
        else:
            dist = MOB_HIT_RUN if hit else rng.uniform(BULLET_ALERT_MIN, BULLET_ALERT_MAX)
        a += math.radians(rng.uniform(-1, 1) * (MOB_HIT_ERR if hit else BULLET_DIR_ERR))
        lo = edge_margin(world)
        tx = clampf(self.x + math.cos(a) * dist, lo + 2, WORLD - lo - 2)
        ty = clampf(self.y + math.sin(a) * dist, lo + 2, WORLD - lo - 2)
        self.noise_at = (tx, ty)
        self.search_t = MOB_HIT_SEARCH_T if hit else BULLET_SEARCH_T
        self.searching = False
        self.inv_speed = MOB_HIT_SPEED if hit else NOISE_INVESTIGATE
        self.heading = math.degrees(math.atan2(-(tx - self.x), ty - self.y))   # sofort in die Richtung drehen
        if self.state == "idle":
            self.state = "chase"

    def windup(self):
        k = MOB_KINDS[self.kind]
        if self.atk_kind == 2:
            return k["rock_windup"]
        return k["slam_windup"] if self.atk_kind == 1 else k["windup"]

    def recover(self):
        k = MOB_KINDS[self.kind]
        return k.get("rock_recover", 1.0) if self.atk_kind == 2 else k.get("recover", 0.4)

    def turn_toward(self, dx, dy, dt, rate=420.0):
        target = math.degrees(math.atan2(-dx, dy))   # Blick = (-sin h, cos h)
        diff = (target - self.heading + 180.0) % 360.0 - 180.0
        self.heading += max(-rate * dt, min(rate * dt, diff))

    def nearest_player(self, players, world=None):
        """Nächster lebender Spieler oder None. Wer auf einem Turm/Dach steht, ist unerreichbar; wer im
        Gebirge auf dem Gelände steht, nicht (MTN_CLIMB: Monster laufen hinterher)."""
        best, bd = None, 1e18
        on_terrain = (world is not None and MTN_CLIMB and self.hover <= 0
                      and abs(self.gz - world.height(self.x, self.y)) < 0.6)
        for p in players:
            if p.hp <= 0:
                continue
            if (abs(p.z - self.gz) > max(3.5, self.height * 0.6)
                    and not (on_terrain and abs(p.z - world.height(p.x, p.y)) < 0.6)):
                continue
            d2 = (p.x - self.x) ** 2 + (p.y - self.y) ** 2
            if d2 < bd:
                best, bd = p, d2
        return best

    def update(self, dt, world, players):
        k = MOB_KINDS[self.kind]
        decay = math.exp(-7.0 * dt)
        if self.state == "dead":
            self.dead_t += dt
            self.x += self.kx * dt
            self.y += self.ky * dt
            self.kx *= decay
            self.ky *= decay
            self.x, self.y = push_out(self.x, self.y, self.radius * 0.5, world, self.gz)
            self.gz = world.floor_at(self.x, self.y, self.gz)
            self.hover = max(0.0, self.hover - 6.0 * dt)  # abgeschossene Drohne fällt herunter
            self.z = self.gz + self.hover
            return
        rng = world.mrng
        self.hurt_t = max(0.0, self.hurt_t - dt)
        self.alert_t = max(0.0, self.alert_t - dt)
        self.atk_cd = max(0.0, self.atk_cd - dt)
        self.zap_hold = max(0.0, self.zap_hold - dt)
        pl = self.nearest_player(players, world)   # Ziel: nächster lebender Spieler
        if pl is None:
            dx = dy = 0.0
            d = 1e9
        else:
            dx, dy = pl.x - self.x, pl.y - self.y
            d = math.hypot(dx, dy)
        sees = pl is not None and (d < k["aggro"] or (self.alert_t > 0 and d < 90))
        reach = self.reach                                 # sitzt das Ziel im Fahrzeug: dessen Hülle angreifen
        if pl is not None and (pl.vehicle >= 0 or pl.heli >= 0 or pl.mount >= 0):
            occ = world.occupied_vehicle(pl)
            if occ is not None:
                reach += VEH_R * 0.9 if occ[0] == "car" else HELI_R * 0.6
        ux = uy = speed = 0.0
        ranged = "range" in k
        if not self.aggressive():                          # Fluchttier: nie angreifen, nur fliehen
            ux, uy, speed = self.calm_move(dt, world, pl, d, sees and d < k["aggro"])
        elif self.state == "attack":
            self.atk_t += dt
            if pl is not None:
                self.turn_toward(dx, dy, dt, (200.0, 60.0, 90.0)[self.atk_kind])
            if not self.did_hit and self.atk_t >= self.windup():
                self.did_hit = True
                if self.atk_kind == 2:
                    world.titan_kick(self, pl)
                elif self.atk_kind == 1:
                    world.colossus_slam(self)
                elif ranged:
                    world.drone_zap(self, pl)
                elif pl is not None and d <= reach * 1.25 and abs(pl.z - self.gz) < 2.5 + self.height * 0.15:
                    world.mob_damage(pl, k["dmg"])
            if self.atk_t >= self.windup() + self.recover():
                self.state = "chase"
                self.atk_cd = k["cooldown"]
                self.next_slam = rng.random() < k.get("slam_chance", 0.0)
        elif sees:
            self.state = "chase"
            self.noise_at, self.searching = None, False    # sieht einen Spieler: Geräusch egal
            self.turn_toward(dx, dy, dt)
            if ranged:                                     # Drohne: auf Abstand bleiben und umkreisen
                want = k["range"] * 0.6
                side = 1.0 if (self.id % 2) else -1.0
                if d > want + 2.0:
                    ux, uy, speed = dx / d, dy / d, k["speed"]
                elif d < want - 3.0:
                    ux, uy, speed = -dx / d, -dy / d, k["speed"] * 0.8
                else:
                    ux, uy, speed = -dy / d * side, dx / d * side, k["speed"] * 0.5
                if (d <= k["range"] and self.atk_cd <= 0 and pl.stun_lock <= 0
                        and world.drone_may_target(self, pl)
                        and world.los((self.x, self.y, self.z + 0.3), (pl.x, pl.y, pl.z + 1.3))):
                    self.state, self.atk_t, self.did_hit, self.atk_kind = "attack", 0.0, False, 0
                    self.zap_pid, self.zap_hold = pl.pid, k["windup"] + k["cooldown"]
            elif "rock_min" in k:                          # Titan: Steinwurf auf Distanz, nah Schlag/Stampfer
                crowd = sum(1 for q in players if q.hp > 0 and math.hypot(q.x - self.x, q.y - self.y) < k["slam_crowd"])
                slam = crowd >= 2 or self.next_slam
                if d > k["rock_max"] or (d < k["rock_min"] and d > reach * 0.85):
                    speed = k["speed"]                     # langsam heran - nie gross rennen
                    ux, uy = dx / d, dy / d
                if self.atk_cd <= 0:
                    if d <= reach or (slam and d <= k["slam_r"] * 0.55):
                        self.state, self.atk_t, self.did_hit = "attack", 0.0, False
                        self.atk_kind = 1 if slam else 0
                    elif (k["rock_min"] <= d <= k["rock_max"]
                          and world.los((self.x, self.y, self.gz + 2.0), (pl.x, pl.y, pl.z + 1.2))):
                        self.state, self.atk_t, self.did_hit, self.atk_kind = "attack", 0.0, False, 2
            elif "slam_r" in k:                            # Koloss: leichter Schlag oder Bodenschlag
                crowd = sum(1 for q in players if q.hp > 0 and math.hypot(q.x - self.x, q.y - self.y) < k["slam_crowd"])
                if d > reach * 0.85:
                    speed = k["speed"]
                    ux, uy = dx / d, dy / d
                slam = crowd >= 2 or self.next_slam          # vorab gewürfelt (nicht jedes Bild neu)
                if self.atk_cd <= 0 and (d <= reach or (slam and d <= k["slam_r"] * 0.55)):
                    self.state, self.atk_t, self.did_hit = "attack", 0.0, False
                    self.atk_kind = 1 if slam else 0
            else:
                if d > reach * 0.85:
                    speed = k["speed"]
                    ux, uy = dx / d, dy / d
                if d <= reach and self.atk_cd <= 0:
                    self.state, self.atk_t, self.did_hit = "attack", 0.0, False
        elif self.noise_at is not None:                    # Geräusch gehört: hinlaufen und dort suchen
            self.state = "chase"
            nx, ny = self.noise_at
            tdx, tdy = nx - self.x, ny - self.y
            td = math.hypot(tdx, tdy)
            if td <= 2.0:
                self.searching = True                      # angekommen: ab jetzt läuft die Suchzeit
            if self.searching:
                self.search_t -= dt
            if self.search_t <= 0:                         # nichts gefunden: aufgeben
                self.noise_at, self.searching = None, False
                self.state = "idle"
            elif td > 2.0:
                self.turn_toward(tdx, tdy, dt)
                speed = k["speed"] * (0.5 if self.searching else self.inv_speed)
                ux, uy = tdx / td, tdy / td
            else:                                          # kurz umsehen
                self.heading += 90.0 * dt
                if rng.random() < dt * 0.8:                # ein paar Schritte in eine zufällige Richtung
                    a = rng.uniform(0, 2 * math.pi)
                    self.noise_at = (clampf(nx + math.cos(a) * 4, 4, WORLD - 4),
                                     clampf(ny + math.sin(a) * 4, 4, WORLD - 4))
        else:
            self.state = "idle"
            self.wander_t -= dt
            if self.wander_t <= 0:
                a, r = rng.uniform(0, 2 * math.pi), rng.uniform(3, 10)
                self.tx = clampf(self.x + math.cos(a) * r, 4, WORLD - 4)
                self.ty = clampf(self.y + math.sin(a) * r, 4, WORLD - 4)
                if rng.random() < 0.4:                 # manchmal einfach stehen bleiben
                    self.tx, self.ty = self.x, self.y
                self.wander_t = rng.uniform(3, 7)
            tdx, tdy = self.tx - self.x, self.ty - self.y
            td = math.hypot(tdx, tdy)
            if td > 0.5:
                self.turn_toward(tdx, tdy, dt, 200.0)
                speed = k["wander"]
                ux, uy = tdx / td, tdy / td
        ox, oy = self.x, self.y
        self.x += (ux * speed + self.kx) * dt
        self.y += (uy * speed + self.ky) * dt
        self.kx *= decay
        self.ky *= decay
        if self.hover <= 0:                          # Fliegende stossen nicht an niedrige Hindernisse
            self.x, self.y = push_out(self.x, self.y, self.radius, world, self.gz)
        lo = edge_margin(world)
        self.x = clampf(self.x, lo, WORLD - lo)
        self.y = clampf(self.y, lo, WORLD - lo)
        if world.in_void(self.x, self.y, 0.3) and (self.hover > 0 or not MOB_TUNNELS):   # Treppenschacht
            self.x, self.y = ox, oy
        if (not MTN_CLIMB and getattr(world, "mtn", False) and self.hover <= 0
                and steep_uphill(world, ox, oy, self.x, self.y, self.gz)):   # gleiche Regel wie für Spieler
            if not steep_uphill(world, ox, oy, self.x, oy, self.gz):
                self.y = oy
            elif not steep_uphill(world, ox, oy, ox, self.y, self.gz):
                self.x = ox
            else:
                self.x, self.y = ox, oy
        if self.hover > 0:
            self.gz = world.height(self.x, self.y)
            self.hover = k.get("fly", 0.0)
            self.z = self.gz + self.hover + 0.25 * math.sin(self.phase * 0.7 + self.id)
        else:
            self.gz = world.floor_at(self.x, self.y, self.gz)
            self.z = self.gz
        if speed > 0 and ux * ux + uy * uy > 0 and math.hypot(self.x - ox, self.y - oy) < speed * dt * 0.3:
            self.leg_left = 0.0                      # festgefahren: Fluchttier schlägt neuen Haken
        self.speed_now = speed
        self.phase += (speed if speed > 0 else (1.5 if self.hover > 0 else 0.0)) * dt * 2.0

    def calm_move(self, dt, world, pl, d, sees):
        """Fluchttier: sieht oder hört es etwas, flieht es in unvorhersehbaren Haken - jede Strecke zufällig lang,
        Richtung zufällig, aber grob weg vom Auslöser. Sonst gemütlich umherhoppeln. -> (ux, uy, Tempo)"""
        k = MOB_KINDS[self.kind]
        rng = world.mrng
        if sees and pl is not None:
            self.fear = (pl.x, pl.y)
        if self.fear is not None:
            self.flee_from, self.flee_t, self.fear = self.fear, CRITTER_FLEE_T, None
        if self.flee_t > 0:
            self.flee_t -= dt
            self.state = "chase"
            if self.leg_left <= 0:
                fx, fy = self.flee_from
                away = math.atan2(self.y - fy, self.x - fx)
                self.leg_dir = away + math.radians(rng.uniform(-CRITTER_TURN, CRITTER_TURN))
                self.leg_left = rng.uniform(CRITTER_LEG_MIN, CRITTER_LEG_MAX)
            ux, uy = math.cos(self.leg_dir), math.sin(self.leg_dir)
            self.leg_left -= k["speed"] * dt
            self.turn_toward(ux, uy, dt, 900.0)
            return ux, uy, k["speed"]
        self.state = "idle"
        self.wander_t -= dt
        if self.wander_t <= 0:
            a, r = rng.uniform(0, 2 * math.pi), rng.uniform(2, 6)
            self.tx = clampf(self.x + math.cos(a) * r, 4, WORLD - 4)
            self.ty = clampf(self.y + math.sin(a) * r, 4, WORLD - 4)
            self.wander_t = rng.uniform(2, 5)
        tdx, tdy = self.tx - self.x, self.ty - self.y
        td = math.hypot(tdx, tdy)
        if td > 0.5:
            self.turn_toward(tdx, tdy, dt, 300.0)
            return tdx / td, tdy / td, k["wander"]
        return 0.0, 0.0, 0.0


def seg_box(p0, p1, b):
    """Schnitt der Strecke p0->p1 mit einem Quader (Slab-Methode).
    Gibt den Eintrittsparameter t in [0,1] zurück oder None."""
    t0, t1 = 0.0, 1.0
    for a0, d, lo, hi in ((p0[0], p1[0] - p0[0], b.x0, b.x1),
                          (p0[1], p1[1] - p0[1], b.y0, b.y1),
                          (p0[2], p1[2] - p0[2], b.z0, b.z1)):
        if abs(d) < 1e-12:
            if a0 < lo or a0 > hi:
                return None
        else:
            ta, tb = (lo - a0) / d, (hi - a0) / d
            if ta > tb:
                ta, tb = tb, ta
            t0, t1 = max(t0, ta), min(t1, tb)
            if t0 > t1:
                return None
    return t0


class Box:
    """Achsenparalleler Quader (Mauer, Turm, Treppenstufe, Dach ...)."""
    __slots__ = ("x0", "y0", "x1", "y1", "z0", "z1", "col", "mm")

    def __init__(self, x0, y0, x1, y1, z0, z1, col, mm=False):
        self.x0, self.y0 = min(x0, x1), min(y0, y1)
        self.x1, self.y1 = max(x0, x1), max(y0, y1)
        self.z0, self.z1 = z0, z1
        self.col = col
        self.mm = mm              # auf der Minimap zeichnen?


def new_stats():
    """Statistik eines Spielers für die laufende Runde (nur der Host zählt). Neue Werte einfach hier ergänzen
    und dort hochzählen, wo es passiert; Scoreboard und Endbildschirm lesen sie aus STAT_TABS."""
    return {"mob": {k: 0 for k in KINDS}, "crate": {k: 0 for k in CRATE_KINDS}, "buffs": 0, "melee_kills": 0,
            "toma_fired": 0, "toma_kills": 0, "longest": 0.0, "longest_w": -1, "heads": 0, "hits": 0,
            "walk": 0.0, "drive": 0.0, "drives": 0, "fly": 0.0, "flights": 0, "zone_t": 0.0}


def stat_summary(p):
    """(Monster-Kills, geöffnete Kisten, Buffs) für das Tab-Scoreboard: beim Host aus pl.stats, beim
    Mitspieler aus dem Snapshot (pl.sb)."""
    st = getattr(p, "stats", None)
    if st is not None and getattr(p, "sb", None) is None:
        return sum(st["mob"].values()), sum(st["crate"].values()), st["buffs"]
    return getattr(p, "sb", None) or (0, 0, 0)


class Crate:
    """Kiste auf der Karte. kind = 'common' | 'rare'. Der Inhalt wird erst beim Öffnen gewürfelt (nur beim Host),
    geöffnete Kisten verschwinden."""

    def __init__(self, cid, x, y, z, kind="common"):
        self.cid, self.x, self.y, self.z = cid, x, y, z
        self.kind = kind if kind in CRATE_KINDS else "common"
        self.bonus = False        # Belohnung (Titan): wird nach dem Öffnen nicht ersetzt, Lichtsäule


class Rock:
    """Steinbrocken des Titans (Host simuliert, Mitspieler bekommen Position und Geschwindigkeit)."""

    def __init__(self, rid, x, y, z, vx, vy, vz, owner=-1):
        self.rid, self.owner = rid, owner
        self.x, self.y, self.z = x, y, z
        self.vx, self.vy, self.vz = vx, vy, vz
        self.life = 8.0


def loot_base(kind, history=None, art="weapon"):
    """Prozentwerte einer Kistenart für eine Art ("weapon"/"gear") nach dem Aufbau-Ausgleich (LOOT_PITY):
    jedes Mal, wenn ein Eintrag in diesem Leben schon gezogen wurde, verliert er LOOT_PITY_STEP Punkte pro
    anderem Eintrag derselben Art, und jeder andere bekommt LOOT_PITY_STEP dazu. Nie unter 0 - fehlt etwas,
    wird nur verteilt, was da ist."""
    col = CRATE_KINDS.index(kind) if kind in CRATE_KINDS else 0
    base = {n: max(0.0, float(v[col])) for n, v in LOOT_TABLES.items()
            if LOOT_ITEMS.get(n) == art and WEAPON_IDX.get(n) != START_WEAPON}
    if LOOT_PITY and history:
        for name in sorted(history):                 # feste Reihenfolge: Host und Test rechnen gleich
            if name not in base:
                continue
            others = [n for n in base if n != name]
            if not others:
                continue
            for _ in range(max(0, int(history[name]))):
                take = min(base[name], LOOT_PITY_STEP * len(others))
                if take <= 0:
                    break
                base[name] -= take
                for n in others:
                    base[n] += take / len(others)
    return base


def loot_chances(kind, owned=(), history=None, last=None, art="weapon", worn=()):
    """Wahrscheinlichkeiten (Name -> Anteil 0..1) innerhalb einer Art für einen bestimmten Spieler.
    Reihenfolge: Grundwerte (LOOT_TABLES) -> Aufbau-Ausgleich aus dem Kisten-Gedächtnis (history: Name -> wie oft
    in diesem Leben gezogen) -> Ausschluss der zuletzt gezogenen (last, LOOT_SKIP_LAST), der getragenen Waffen
    (owned) und der getragenen Ausrüstung (worn, Namen); deren Anteil verteilt LOOT_SHARE_MODE -> normieren."""
    base = loot_base(kind, history, art)
    skip = set(worn)
    if LOOT_SKIP_OWNED:
        skip |= {WEAPONS[wi].name for wi in owned if wi is not None and 0 <= wi < len(WEAPONS)}
    if LOOT_SKIP_LAST and last:
        skip.add(last)
    keep = [n for n in base if n not in skip and base[n] > 0]
    if not keep:
        if art in ("gear", "melee"):
            return {}                                # alles schon getragen: nichts dieser Art aus dieser Kiste
        keep, skip = [n for n in base if base[n] > 0] or list(base), set()
    freed = sum(base[n] for n in base if n in skip)
    if LOOT_SHARE_MODE == "equal":
        probs = {n: base[n] + freed / len(keep) for n in keep}
    else:                                           # proportional: einfach neu normieren
        probs = {n: base[n] for n in keep}
    tot = sum(probs.values()) or 1.0
    return {n: p / tot for n, p in probs.items()}


def roll_loot(kind, rng, owned=(), history=None, last=None, worn=()):
    """Inhalt einer Kiste würfeln -> (Art, Name): erst Waffe oder Ausrüstung (LOOT_CATEGORIES), dann das Teil."""
    cats = dict(LOOT_CATEGORIES.get(kind) or {"weapon": 1.0})
    while cats:
        art = rng.choices(list(cats), weights=list(cats.values()))[0]
        ch = loot_chances(kind, owned, history, last, art, worn)
        if ch:
            names = list(ch)
            name = rng.choices(names, weights=[ch[n] for n in names])[0]
            return LOOT_ITEMS[name], name
        del cats[art]
    return "weapon", "Sturmgewehr"


def worn_names(pl):
    """Getragene Ausrüstung und Nahkampfwaffe (Namen) - werden beim Öffnen einer Kiste herausgerechnet."""
    out = [GEAR[gi].name for gi in getattr(pl, "gear", {}).values() if gi is not None]
    mi = getattr(pl, "melee", START_MELEE)
    if 0 <= mi < len(MELEE):
        out.append(MELEE[mi].name)
    return out


def gear_list(pl):
    """Getragene Ausrüstung als Liste [Kopf, Torso, Füsse] (Index in GEAR oder -1) - fürs Netz."""
    return [pl.gear.get(sl) if pl.gear.get(sl) is not None else -1 for sl in GEAR_SLOTS]


def wears(pl, kind):
    """Trägt der Spieler ein Teil mit dieser Wirkung?"""
    for gi in getattr(pl, "gear", {}).values():
        if gi is not None and GEAR[gi].kind == kind:
            return True
    return False


def remember_loot(pl, name):
    """Kisten-Gedächtnis des Spielers (nur beim Host): name wurde gerade aus einer Kiste gezogen."""
    pl.loot_history[name] = pl.loot_history.get(name, 0) + 1
    pl.last_loot = name


def push_out(x, y, r, world, z=None, veh=-1):
    """Kreis (x,y,r) aus allen festen Objekten (Bäume, Felsen, Teiche, Gebäude,
    Fahrzeuge) schieben. z = Fusshöhe: Quader, über deren Oberkante man steht
    (abzüglich STEP_H), und Quader über dem Kopf blockieren nicht.
    veh = ID eines Fahrzeugs, das ignoriert wird (das eigene)."""
    for p in world.props:
        ddx, ddy = x - p.x, y - p.y
        min_d = p.solid_r + r
        if abs(ddx) > min_d or abs(ddy) > min_d:
            continue
        d = math.hypot(ddx, ddy)
        if d < min_d:
            if d == 0:
                ddx, ddy, d = 1.0, 0.0, 1.0
            x = p.x + ddx / d * min_d
            y = p.y + ddy / d * min_d
    for v in world.vehicles:                     # Fahrzeuge sind feste Hindernisse
        if v.hp <= 0 or v.id == veh or (z is not None and abs(z - v.z) > 2.0):
            continue
        ddx, ddy = x - v.x, y - v.y
        min_d = VEH_R + r
        if abs(ddx) > min_d or abs(ddy) > min_d:
            continue
        d = math.hypot(ddx, ddy)
        if d < min_d:
            if d == 0:
                ddx, ddy, d = 1.0, 0.0, 1.0
            x = v.x + ddx / d * min_d
            y = v.y + ddy / d * min_d
    if world.boxes:
        if z is None:
            z = world.height(x, y)
        for _ in range(2):                       # 2 Durchgänge: Ecken zwischen zwei Mauern
            for b in world.boxes_near(x - r, y - r, x + r, y + r):
                if z >= b.z1 - STEP_H or z + PLAYER_H <= b.z0:
                    continue
                nx, ny = clampf(x, b.x0, b.x1), clampf(y, b.y0, b.y1)
                dx, dy = x - nx, y - ny
                d2 = dx * dx + dy * dy
                if d2 >= r * r:
                    continue
                if d2 > 1e-12:
                    k = r / math.sqrt(d2)
                    x, y = nx + dx * k, ny + dy * k
                else:                            # Mittelpunkt im Quader: über die nächste Kante hinaus
                    opts = ((x - b.x0, -1, 0), (b.x1 - x, 1, 0), (y - b.y0, 0, -1), (b.y1 - y, 0, 1))
                    _d, sx, sy = min(opts)
                    if sx:
                        x = (b.x0 - r) if sx < 0 else (b.x1 + r)
                    else:
                        y = (b.y0 - r) if sy < 0 else (b.y1 + r)
    return x, y


class World:
    GRID = 10.0   # Rastergrösse für die Kugel-Kollision

    def __init__(self, seed=SEED, spawn_mobs=True, mode="koth", limit=600.0, strike_cd=STRIKE_CD, regen=REGEN_RATE,
                 respawn=RESPAWN_DEFAULT, mapdata=None):
        set_world_size(STD_WORLD if mapdata is None else MAP_WORLD)   # vor allem anderen: Grösse dieser Karte
        rng = random.Random(seed)
        self.map = mapdata                   # bereinigte Kartendatei (sanitize_map) oder None = Standardkarte
        self.mc = mapdata.get("mc") if mapdata else None      # Minecraft-Welt (.mcmap) oder None
        self.mtn = mapdata is None           # Standardkarte: Gebirgszug ringsum
        if self.mc:
            spawn_mobs, mode = False, "dm"   # Minecraft-Karte: Deathmatch ohne Monster
        self.hgrid = mapdata["terrain"] if mapdata else None
        self.respawn_delay = float(respawn)  # Sekunden Wartezeit nach dem Tod (vom Host einstellbar)
        self.strike_cd = float(strike_cd)    # Abklingzeit des Tomahawk (0 = nur einmal pro Runde)
        self.regen_rate = float(regen)       # Lebensregeneration in HP/s (0 = aus)
        self.strike_wait = 0.0               # Sekunden, bis der Knopf wieder geht
        self.seed = seed
        self.mode = mode if mode in MODES else "koth"
        self.limit = float(limit)         # Zeitlimit in Sekunden
        self.mobs_on = spawn_mobs         # Monster an/aus (der Client bekommt sie vom Host)
        self.ponds = []   # (x, y, r)
        self.props = []
        self.boxes = []
        self.flats = []   # (x, y, r_innen, r_aussen): hier ist das Gelände eben (Höhe 0)
        self.floors = []  # (x0, y0, x1, y1, Farbe): Bodenfarbe in Gebäuden
        self.crates = []      # Kisten, die gerade auf der Karte liegen (beim Client: aus den Snapshots)
        self.crate_spots = [] # (x, y, z): gute Kistenplätze an Bauwerken (Türme, Häuser, Aussenposten ...)
        self.crate_wait = []  # [Restzeit, Art, x, y]: geöffnete Kisten, die woanders neu auftauchen
        self.next_cid = 1
        self.rocks = []       # Steinbrocken des Titans in der Luft
        self.next_rid = 1
        self.voids = []   # (x0, y0, x1, y1): Löcher im Gelände = Tunneltreppen (Boden bei TUN_Z)
        self.tunnels = [] # (x0, y0, x1, y1): Tunnelgänge (ein Stockwerk unter dem Gelände)
        self.decor = []   # (x0, y0, x1, y1, z0, z1, Farbe, beleuchtet): nur Darstellung, nicht fest
        self.vehicles = []
        self.grenades = []
        self.drops = []
        self.turrets = []
        self.helis = []
        self.pads = []     # (x, y): Helipads
        self.runway = None
        self.strike, self.strike_t, self.strike_by = 0, 0.0, -1   # 0 bereit, 1 Countdown, 2 benutzt
        self.toma_spots = []                 # mögliche Orte der Tomahawk-Säule: (x, y, z, Blick zur Kartenmitte)
        self.toma_idx = -1                   # aktiver Ort (-1 = gerade keiner: Countdown, Abklingzeit, verbraucht)
        self.toma_age = 0.0                  # s seit die aktive Säule aufgetaucht ist (Hochfahren: TOMA_RISE_T)
        self.toma_last = -1                  # zuletzt benutzter Ort (der nächste ist ein anderer)
        self.toma_sink_idx, self.toma_sink_t = -1, 0.0   # benutzte Säule, die gerade versinkt
        self.toma_lock = {}                  # Spieler-ID -> s, bis er selbst wieder auslösen darf (TOMA_PLAYER_CD)
        self.strike_ang = 0.0                # Himmelsrichtung, aus der die Rakete anfliegt (Grad)
        self.button = SimpleNamespace(x=-999.0, y=-999.0, z=-999.0)
        self.timer_panel = SimpleNamespace(x=-999.0, y=-999.0, z=-999.0)
        self.strike_dur = STRIKE_T
        self.strike_x, self.strike_y = float(CENTER), float(CENTER)   # Einschlagpunkt (nur Host/Schütze kennt ihn)
        self.spawn_zs = {}
        self.ladders = {}
        if self.mc:
            self.build_mc()
        else:
            self.build_structures()

        def free(x, y, r):
            for fx, fy, rin, _rout in self.flats:
                if math.hypot(x - fx, y - fy) < rin + r:
                    return False
            for p in self.props:
                if math.hypot(x - p.x, y - p.y) < r + p.r + 0.4:
                    return False
            return True

        def scatter(count, kind, rmin, rmax, solid):
            placed = tries = 0
            while placed < count and tries < count * 60:
                tries += 1
                r = rng.uniform(rmin, rmax)
                x = rng.uniform(r + 3, WORLD - r - 3)
                y = rng.uniform(r + 3, WORLD - r - 3)
                vis = r * (1.4 if kind == "pond" else 1.0)
                if self.mtn:                          # Teiche nur im Tal, Bäume nicht an den Felswänden
                    mz = mountain(x, y)
                    if kind == "pond" and (mz > 0.0 or mountain(x + vis * 2, y) + mountain(x - vis * 2, y)
                                           + mountain(x, y + vis * 2) + mountain(x, y - vis * 2) > 0.0):
                        continue
                    if kind == "tree" and mz > 16.0:
                        continue
                if free(x, y, vis * (1.6 if kind == "pond" else 1.0)):
                    p = Prop(kind, x, y, vis, solid(r))
                    p.base_r = r
                    self.props.append(p)
                    if kind == "pond":
                        self.ponds.append((x, y, r))
                    placed += 1

        mp = self.map or {}
        big = 1.6 if self.mtn else 1.0             # Standardkarte: mehr Fläche, mehr Bäume und Felsen
        for kind, key, count, rmin, rmax, solid in (() if self.mc else
                                                    (("pond", "ponds", 5 if self.mtn else 4, 4.5, 8.0, lambda r: r * 0.72),
                                                     ("rock", "rocks", int(35 * big * 1.3), 0.7, 1.8, lambda r: r * 0.85),
                                                     ("tree", "trees", int(110 * big), 1.6, 2.8, lambda r: 0.45))):
            if mp.get(key) is None:
                scatter(count, kind, rmin, rmax, solid)
            else:                                    # Karte aus dem Editor: genau diese Objekte
                for x, y, r in mp[key]:
                    vis = r * (1.4 if kind == "pond" else 1.0)
                    p = Prop(kind, x, y, vis, solid(r))
                    p.base_r = r
                    self.props.append(p)
                    if kind == "pond":
                        self.ponds.append((x, y, r))
        if self.mtn:
            self.add_groves(rng)
        if not self.mc:
            if mp.get("blocks") is None:
                self.add_cover(rng)
            self.add_map_objects()
        self.build_grids()
        self.last_spawn = {}
        self.spawns = self.make_spawns(rng)
        if not self.mc:
            self.build_vehicles()
        if self.mtn:
            self.build_toma_spots()                  # nach den Fahrzeugen: deren Startplätze bleiben frei

        # --- Mobs, Kugeln, Ereignisse (eigener RNG: ändert die Welt nicht)
        self.mrng = random.Random(seed + 2)
        self.bullets = []
        self.mobs = []
        self.pending = []        # [Restzeit, Art] zum Wiederauftauchen
        self.noise_clock = 0.0   # Lärm: nächste Auswertung der Spielerbewegung
        self.noise_log = []      # NOISE_DEBUG: (x, y, Radius, Restzeit) zur Anzeige
        self.events = []         # für die Darstellung (Treffer, Schüsse, ...)
        self.kills = 0           # erlegte Monster
        self.players = {}        # Spieler-ID -> Player (beim Host: alle, beim Client: nur Anzeige)
        self.shot_sink = None    # Client: Schüsse zum Host schicken statt selbst zu simulieren
        self.gren_sink = None    # Client: Granatenwürfe zum Host schicken
        self.melee_sink = None   # Client: Nahkampf-Schläge zum Host schicken
        self.next_gid = 1
        self.next_did = 1
        self.runover = {}        # Überfahren: Opfer -> Sperrzeit (damit nicht jedes Frame Schaden kommt)
        self.next_bid = 1
        self.next_mid = 1
        self.phase = "play"      # play | over (Rangliste wird gezeigt)
        self.time_left = self.limit
        self.over_t = 0.0
        self.reset_crates()
        self.place_toma()        # beim Mitspieler überschreibt der Host das (Nachricht 'tb')
        if spawn_mobs:           # der Client bekommt die Monster vom Host
            self.populate_mobs()

    def prop_count(self):
        """Prüfsumme für den Beitritt: stimmt nur bei gleicher Version und Seed."""
        return len(self.props) + len(self.boxes) + len(self.vehicles) + len(self.turrets) + len(self.helis)

    # ------------------------------------------------------------ Karte
    def add_box(self, x0, y0, x1, y1, z0, z1, col, mm=False):
        b = Box(x0, y0, x1, y1, z0, z1, col, mm)
        self.boxes.append(b)
        return b

    def add_crate(self, x, y, z):
        """Merkt einen guten Kistenplatz an einem Bauwerk vor (die Kisten selbst verteilt reset_crates zufällig)."""
        self.crate_spots.append((x, y, z))

    def stairs(self, x, y, d, n, w, base, sh=0.5, sd=0.8, col=STONE_D):
        """Treppe aus n Stufen (Höhe sh, Tiefe sd, Breite w). Die Stufe i steigt in
        Richtung d (N=+y, S=-y, E=+x, W=-x); (x,y) ist die Ecke der untersten Stufe."""
        z0 = -2 if base == 0 else base
        for i in range(n):
            top = base + (i + 1) * sh
            if d == "N":
                self.add_box(x, y + i * sd, x + w, y + (i + 1) * sd, z0, top, col)
            elif d == "S":
                self.add_box(x, y - (i + 1) * sd, x + w, y - i * sd, z0, top, col)
            elif d == "E":
                self.add_box(x + i * sd, y, x + (i + 1) * sd, y + w, z0, top, col)
            else:
                self.add_box(x - (i + 1) * sd, y, x - i * sd, y + w, z0, top, col)

    def wall_x(self, xa, xb, ya, yb, h, ops, col):
        """Mauer entlang x mit Öffnungen ops = (Mitte, halbe Breite, z unten, z oben)."""
        cur = xa
        for p0, p1, zlo, zhi in sorted((c - hw, c + hw, zl, zh) for c, hw, zl, zh in ops):
            if p0 > cur:
                self.add_box(cur, ya, p0, yb, -2, h, col, True)
            if zlo > 0:
                self.add_box(p0, ya, p1, yb, -2, zlo, col, True)
            if zhi < h:
                self.add_box(p0, ya, p1, yb, zhi, h, col, True)
            cur = p1
        if cur < xb:
            self.add_box(cur, ya, xb, yb, -2, h, col, True)

    def wall_y(self, ya, yb, xa, xb, h, ops, col):
        cur = ya
        for p0, p1, zlo, zhi in sorted((c - hw, c + hw, zl, zh) for c, hw, zl, zh in ops):
            if p0 > cur:
                self.add_box(xa, cur, xb, p0, -2, h, col, True)
            if zlo > 0:
                self.add_box(xa, p0, xb, p1, -2, zlo, col, True)
            if zhi < h:
                self.add_box(xa, p0, xb, p1, zhi, h, col, True)
            cur = p1
        if cur < yb:
            self.add_box(xa, cur, xb, yb, -2, h, col, True)

    def build_mc(self):
        """Minecraft-Karte: jeder Block ist schon als Kollisionsquader (verschmolzen) in der Datei. Das Gelände ist der
        flache Meeresboden; alles andere sind Quader. Keine Burg, kein Tunnel, kein Tomahawk."""
        mc = self.mc
        self.mc_floor = float(mc["meta"]["floor_z"])
        b = mc["boxes"]
        col = (0.5, 0.5, 0.5)
        for i in range(0, len(b), 6):
            self.add_box(b[i], b[i + 1], b[i + 3], b[i + 4], b[i + 2], b[i + 5], col)
        self.ladders = {}                                                   # (Zelle x, Zelle y) -> [z der Blockunterkante]
        for x, y, z in mc["meta"].get("ladders", ()):
            self.ladders.setdefault((int(round(x)), int(round(y))), []).append(float(z))
        self.button = SimpleNamespace(x=-999.0, y=-999.0, z=-999.0)         # kein Tomahawk-Knopf
        self.timer_panel = SimpleNamespace(x=-999.0, y=-999.0, z=-999.0)

    def build_structures(self):
        """Burg in der Mitte, vier Türme in den Ecken, Häuser, Lagerhalle, Ruine (oder die Auswahl der Karte)."""
        mp = self.map or {}
        keep = mp.get("keep", {})
        c = CENTER
        if keep.get("castle", True):
            self.build_castle()
        if mp.get("towers") is None:
            d = 58.0
            for tx, ty, side in ((c - d, c - d, "E"), (c + d, c - d, "W"),
                                 (c - d, c + d, "E"), (c + d, c + d, "W")):
                self.build_tower(tx, ty, side, crate=(tx, ty) != (c + d, c + d))
        else:
            for t in mp["towers"]:
                self.build_tower(t["x"], t["y"], t["side"], t["crate"])
        if keep.get("runway", True):
            self.build_runway()
        self.build_helipads(mp.get("pads"))
        if mp.get("houses") is None:
            self.default_houses()
        else:
            for h in mp["houses"]:
                self.map_house(h)
        if self.mtn:
            self.build_outposts()
        if mp.get("ruins") is None:
            self.build_ruin(c - 30, c + 35)
        else:
            for x, y in mp["ruins"]:
                self.build_ruin(x, y)
        if keep.get("tunnels", True):
            self.build_tunnels()
            if self.map:                                  # der Tunnel braucht ebenes Gelände darüber
                for x0, y0, x1, y1 in self.tunnels:
                    n = max(1, int(max(x1 - x0, y1 - y0) // 5.0))
                    for i in range(n + 1):
                        fx = x0 + (x1 - x0) * i / n if x1 - x0 >= y1 - y0 else (x0 + x1) / 2
                        fy = y0 + (y1 - y0) * i / n if y1 - y0 > x1 - x0 else (y0 + y1) / 2
                        half = min(x1 - x0, y1 - y0) / 2
                        self.flats.append((fx, fy, half + 3.0, half + 10.0))

    def default_houses(self):
        c = CENTER
        door = lambda ctr: [(ctr, 1.1, 0.0, 2.4)]
        win = lambda ctr: [(ctr, 0.9, 1.2, 2.2)]
        self.build_house(c - 35, c, 10, 8, 3.2, {"E": door(c), "W": win(c), "N": win(c - 35), "S": win(c - 35)},
                         crate=(c - 38, c - 2))
        self.build_house(c + 35, c, 10, 8, 3.2, {"W": door(c), "E": win(c), "N": win(c + 35), "S": win(c + 35)})
        self.build_house(c, c - 42, 10, 8, 3.2, {"N": door(c), "S": win(c), "W": win(c - 42), "E": win(c - 42)})
        self.build_house(c, c + 42, 10, 8, 3.2, {"S": door(c), "N": win(c), "W": win(c + 42), "E": win(c + 42)},
                         crate=(c, c + 44))
        wx, wy = c + 35, c + 42            # Lagerhalle: zwei Türen im Süden, eine im Norden
        self.build_house(wx, wy, 16, 8, 4.2,
                         {"S": [(wx - 4, 1.6, 0.0, 3.2), (wx + 4, 1.6, 0.0, 3.2), (wx - 7.5, 0.7, 1.5, 2.7)],
                          "N": [(wx, 1.6, 0.0, 3.2), (wx - 6, 0.7, 1.5, 2.7), (wx + 6, 0.7, 1.5, 2.7)],
                          "W": [(wy, 0.9, 1.5, 2.7)], "E": [(wy, 0.9, 1.5, 2.7)]},
                         floor=CONCRETE, flat_r=14.0, col=(0.55, 0.57, 0.60))

    def map_house(self, h):
        """Haus aus der Kartendatei: Türen und Fenster jeweils in der Wandmitte."""
        x, y = h["x"], h["y"]
        ops = {}
        for side in "NSEW":
            ctr = x if side in "NS" else y
            ops[side] = []
            if side in h["doors"]:
                ops[side].append((ctr, 1.1 if h["h"] < 4 else 1.6, 0.0, 2.4 if h["h"] < 4 else 3.2))
            elif side in h["win"]:
                ops[side].append((ctr, 0.9, 1.2, 2.2))
        crate = (x - h["w"] / 4, y - h["d"] / 4) if h["crate"] else None
        self.build_house(x, y, h["w"], h["d"], h["h"], ops, crate=crate,
                         flat_r=max(10.0, max(h["w"], h["d"]) * 0.75 + 3.0), col=h["c"])

    def add_map_objects(self):
        """Deckungsblöcke, freie Kisten und Geschütze aus der Kartendatei (nach Gelände und Teichen)."""
        mp = self.map
        if not mp:
            return
        for b in mp.get("blocks") or ():
            gz = self.height((b["x0"] + b["x1"]) / 2, (b["y0"] + b["y1"]) / 2)
            self.add_box(b["x0"], b["y0"], b["x1"], b["y1"], gz - 2.5, gz + b["h"], b["c"], b["mm"])
        for x, y in mp.get("crates") or ():
            self.add_crate(x, y, self.height(x, y))
        for x, y, kind in mp.get("turrets") or ():
            gz = self.height(x, y)
            self.add_box(x - 0.45, y - 0.45, x + 0.45, y + 0.45, gz - 1.0, gz + 0.9, (0.30, 0.32, 0.34))
            self.turrets.append(Turret(len(self.turrets), x, y, gz + 0.9 + 1.35,
                                       math.degrees(math.atan2(-(CENTER - x), CENTER - y)), kind))

    # ------------------------------------------------------------ Geheime Tunnel
    def build_tunnels(self):
        """Tunnelnetz unter dem ebenen Gelände (dort ist die Höhe exakt 0).

        Ein Gang (Rechteck in self.tunnels) liegt bei TUN_Z. Wer unter -1 m ist und in
        einem solchen Rechteck steht, hat den Tunnelboden unter den Füssen (siehe
        floor_at) - oben darüber läuft man ganz normal auf dem Gelände. Die vier
        Treppenschächte (self.voids) sind Löcher im Gelände: von oben sehen sie aus
        wie Boden (die Karte zeichnet eine Abdeckung), man fällt aber hinein. Unten
        führen die Treppen in den Gang, an ihrem oberen Ende kommt man wieder heraus.
        Wände, Decke und Stufen sind ganz normale Quader (Kollision, Kugeln)."""
        q = 0.2
        o = TO
        corr = [(41.0, 76.4, 119.0, 79.0), (89.0, 79.0, 91.6, 92.0),
                (79.4, 70.0, 82.0, 76.4),                    # Gang zum Kommandoraum
                (73.0, 62.0, 87.0, 70.0)]                    # Kommandoraum
        wells = [(41.4, 79.0, 44.0, 83.0, "N"),      # Westhaus
                 (116.0, 79.0, 118.6, 83.0, "N"),    # Osthaus
                 (66.0, 72.4, 68.6, 76.4, "S"),      # Burghof Südwest
                 (89.0, 92.0, 91.6, 96.0, "N")]      # Burghof Nordost
        new = []
        if self.mtn and TUN_LONG:                    # Standardkarte: lange Tunnel vom Kartenrand (Norden, Süden)
            new = [(104.0, 79.0, 106.6, 178.0),          # Nord: vom Ost-West-Gang bis kurz vors Gebirge
                   (106.6, 129.0, 130.0, 131.6),         #   Abzweig nach Osten (zwischen den Aussenposten)
                   (81.2, -10.0, 83.8, 62.0),            # Süd: vom Kommandoraum unter der Landebahn durch
                   (30.0, 41.0, 81.2, 43.6)]             #   Abzweig nach Westen (beim Aussenposten Südwest)
            corr += new
            wells += [(104.0, 178.0, 106.6, 182.0, "N"),  # Nord-Eingang am Gebirgsrand
                      (130.0, 129.0, 134.0, 131.6, "E"),  # Ausgang Abzweig Ost
                      (81.2, -14.0, 83.8, -10.0, "S"),    # Süd-Eingang hinter der Landebahn
                      (26.0, 41.0, 30.0, 43.6, "W")]      # Ausgang Abzweig West
        corr = [(a + o, b + o, c + o, d + o) for a, b, c, d in corr]
        wells = [(a + o, b + o, c + o, d + o, e) for a, b, c, d, e in wells]
        new = [(a + o, b + o, c + o, d + o) for a, b, c, d in new]
        for x0, y0, x1, y1, _d in wells[4:]:        # neue Eingänge: Gelände eben (die Treppe ist auf Höhe 0 gebaut)
            self.flats.append(((x0 + x1) / 2, (y0 + y1) / 2, TUN_ENTRY_FLAT, TUN_ENTRY_FLAT + 7.0))
        for x0, y0, x1, y1 in new:                   # über dem Gang darf das Gelände nicht zu tief liegen
            n = max(1, int(max(x1 - x0, y1 - y0) // 3.0))
            for i in range(n + 1):
                fx = x0 + (x1 - x0) * i / n if x1 - x0 >= y1 - y0 else (x0 + x1) / 2
                fy = y0 + (y1 - y0) * i / n if y1 - y0 > x1 - x0 else (y0 + y1) / 2
                if self.surface_height(fx, fy) < TUN_COVER_MIN:
                    self.flats.append((fx, fy, 3.0, 8.0))
        wall_col, roof_col, floor_col = (0.34, 0.32, 0.30), (0.28, 0.27, 0.27), (0.30, 0.28, 0.26)
        n_st, sd = 8, 0.5
        sh = (-0.1 - TUN_Z) / n_st
        rects = list(corr) + [w[:4] for w in wells]

        def ci(v):
            return int(round(v / q))

        floor = set()
        for x0, y0, x1, y1 in rects:
            for i in range(ci(x0), ci(x1)):
                for j in range(ci(y0), ci(y1)):
                    floor.add((i, j))
        # Wände: überall, wo neben einer Bodenzelle keine mehr liegt (zu Quadern verschmolzen)
        runs = {}
        for (i, j) in floor:
            for side, (di, dj) in (("W", (-1, 0)), ("E", (1, 0)), ("S", (0, -1)), ("N", (0, 1))):
                if (i + di, j + dj) not in floor:
                    key = (side, i if side in "WE" else j)
                    runs.setdefault(key, []).append(j if side in "WE" else i)
        T = 0.6
        seg = int(TUN_SEG / q)                       # lange Wände in Stücke: Oberkante folgt dem Gelände darüber

        def top_over(x0, y0, x1, y1):
            """Oberkante für Wand/Decke: knapp unter dem tiefsten Geländepunkt darüber (nie über -0.02)."""
            h = min(self.surface_height(x, y) for x in (x0, (x0 + x1) / 2, x1) for y in (y0, (y0 + y1) / 2, y1))
            return min(-0.02, h - 0.12)

        def wall(x0, y0, x1, y1):
            self.add_box(x0, y0, x1, y1, -6.0, top_over(x0, y0, x1, y1), wall_col)
        for (side, line), cells in runs.items():
            cells.sort()
            start = prev = cells[0]
            for c in cells[1:] + [None]:
                if c is not None and c == prev + 1 and prev - start < seg:
                    prev = c
                    continue
                a, b = start * q, (prev + 1) * q
                if side == "W":
                    wall(line * q - T, a, line * q, b)
                elif side == "E":
                    wall((line + 1) * q, a, (line + 1) * q + T, b)
                elif side == "S":
                    wall(a, line * q - T, b, line * q)
                else:
                    wall(a, (line + 1) * q, b, (line + 1) * q + T)
                if c is not None:
                    start = prev = c
        for x0, y0, x1, y1 in corr:
            lx_, ly_ = x1 - x0, y1 - y0                  # Decke in Stücken (Oberkante unter dem Gelände)
            n = max(1, int(math.ceil(max(lx_, ly_) / TUN_SEG)))
            for i in range(n):
                if lx_ >= ly_:
                    a0, a1, b0, b1 = x0 + lx_ * i / n, x0 + lx_ * (i + 1) / n, y0, y1
                else:
                    a0, a1, b0, b1 = x0, x1, y0 + ly_ * i / n, y0 + ly_ * (i + 1) / n
                self.add_box(a0, b0, a1, b1, TUN_ROOF, top_over(a0, b0, a1, b1), roof_col)
            self.tunnels.append((x0, y0, x1, y1))
            self.decor.append((x0, y0, x1, y1, TUN_Z - 0.3, TUN_Z, floor_col, True))
        for x0, y0, x1, y1, d in wells:
            self.voids.append((x0, y0, x1, y1))
            for i in range(n_st):                        # Stufe 0 liegt am Gang, die letzte oben
                top = TUN_Z + (i + 1) * sh
                if d == "N":
                    self.add_box(x0, y0 + i * sd, x1, y0 + (i + 1) * sd, TUN_Z - 1.0, top, STONE_D)
                elif d == "S":
                    self.add_box(x0, y1 - (i + 1) * sd, x1, y1 - i * sd, TUN_Z - 1.0, top, STONE_D)
                elif d == "E":
                    self.add_box(x0 + i * sd, y0, x0 + (i + 1) * sd, y1, TUN_Z - 1.0, top, STONE_D)
                else:
                    self.add_box(x1 - (i + 1) * sd, y0, x1 - i * sd, y1, TUN_Z - 1.0, top, STONE_D)
        lamp = (1.0, 0.85, 0.5)
        for x0, y0, x1, y1, d in wells:                      # Eingänge deutlich markieren
            rim = (0.95, 0.55, 0.10)
            for a0, b0, a1, b1 in ((x0 - 0.3, y0 - 0.3, x1 + 0.3, y0), (x0 - 0.3, y1, x1 + 0.3, y1 + 0.3),
                                   (x0 - 0.3, y0, x0, y1), (x1, y0, x1 + 0.3, y1)):
                self.decor.append((a0, b0, a1, b1, 0.0, 0.16, rim, True))
            if d in "NS":
                px, py = x0 - 0.5, y1 + 0.3 if d == "N" else y0 - 0.5
            else:
                px, py = (x1 + 0.3 if d == "E" else x0 - 0.5), y0 - 0.5
            self.decor.append((px - 0.08, py - 0.08, px + 0.08, py + 0.08, 0.0, 2.4, (0.2, 0.2, 0.22), True))
            self.decor.append((px - 0.25, py - 0.25, px + 0.25, py + 0.25, 2.4, 2.7, lamp, False))
        # Kommandoraum: Konsolen, Kartentisch, Bildschirme
        self.add_box(79.0 + o, 62.1 + o, 81.0 + o, 63.0 + o, TUN_Z - 1.0, TUN_Z + 1.0, (0.25, 0.27, 0.30))
        self.add_box(84.0 + o, 62.1 + o, 86.0 + o, 63.0 + o, TUN_Z - 1.0, TUN_Z + 1.0, (0.25, 0.27, 0.30))
        self.add_box(76.0 + o, 65.5 + o, 84.0 + o, 67.0 + o, TUN_Z - 1.0, TUN_Z + 0.9, (0.35, 0.28, 0.2))
        self.decor.append((75.0 + o, 62.05 + o, 78.0 + o, 62.2 + o, TUN_Z + 1.2, TUN_Z + 2.0, (0.2, 0.9, 0.4), False))
        for lx in (76.0, 80.0, 84.0):
            self.decor.append((lx - 0.3 + o, 65.7 + o, lx + 0.3 + o, 66.3 + o, TUN_ROOF - 0.1, TUN_ROOF, lamp, False))
        for lx in range(48, 116, 9):
            self.decor.append((lx - 0.25 + o, 77.5 + o, lx + 0.25 + o, 77.9 + o, TUN_ROOF - 0.1, TUN_ROOF, lamp, False))
        for ly in (84, 90):
            self.decor.append((89.9 + o, ly - 0.25 + o, 90.7 + o, ly + 0.25 + o, TUN_ROOF - 0.1, TUN_ROOF, lamp, False))
        for x0, y0, x1, y1 in new:                   # Lampen in den neuen Gängen alle TUN_LAMP m
            if x1 - x0 >= y1 - y0:
                cy = (y0 + y1) / 2
                for k in range(1, int((x1 - x0) // TUN_LAMP) + 1):
                    lx = x0 + k * TUN_LAMP - TUN_LAMP / 2
                    self.decor.append((lx - 0.25, cy - 0.2, lx + 0.25, cy + 0.2, TUN_ROOF - 0.1, TUN_ROOF, lamp, False))
            else:
                cx = (x0 + x1) / 2
                for k in range(1, int((y1 - y0) // TUN_LAMP) + 1):
                    ly = y0 + k * TUN_LAMP - TUN_LAMP / 2
                    self.decor.append((cx - 0.2, ly - 0.25, cx + 0.2, ly + 0.25, TUN_ROOF - 0.1, TUN_ROOF, lamp, False))

    def in_tunnel(self, x, y):
        for x0, y0, x1, y1 in self.tunnels:
            if x0 <= x <= x1 and y0 <= y <= y1:
                return True
        return False

    def in_void(self, x, y, m=0.0):
        """True, wenn (x,y) (mit Rand m) über einem Treppenschacht liegt."""
        for x0, y0, x1, y1 in self.voids:
            if x0 - m <= x <= x1 + m and y0 - m <= y <= y1 + m:
                return True
        return False

    def ground_for(self, x, y, z):
        """Boden für Kugeln, Granaten, Partikel in Höhe z (kennt die Tunnel)."""
        if z < -1.0 and self.in_tunnel(x, y):
            return TUN_Z
        return self.height(x, y)

    # ------------------------------------------------------------ Fahrzeuge
    def build_vehicles(self):
        """Zwei Geländewagen ausserhalb der Burg, mit der Front zur Burg."""
        if self.map and self.map.get("vehicles") is not None:
            for k, (x, y, hd) in enumerate(self.map["vehicles"]):
                z = self.height(x, y)
                self.vehicles.append(Vehicle(k, x, y, z, hd))
                self.turrets.append(Turret(len(self.turrets), x, y, z + 1.75, hd, "car", k))
            return
        for k, base in enumerate((45.0, 225.0)):
            done = False
            for dr in (0, 1, 2, 3, 4, 5):
                for da in (0, 1, -1, 2, -2):
                    a = math.radians(base + da * 6.0)
                    r = 46.0 + dr * 2.5
                    x, y = CENTER + math.cos(a) * r, CENTER + math.sin(a) * r
                    if (self.height(x, y) < WATER_LEVEL + 1.0 or self.in_solid(x, y, 2.6)
                            or any(math.hypot(x - px, y - py) < pr * 1.8 + 3 for px, py, pr in self.ponds)
                            or any(math.hypot(x - p.x, y - p.y) < p.solid_r + 3.2 for p in self.props)
                            or any(self.height(x + ox, y + oy) > self.height(x, y) + 0.8
                                   for ox, oy in ((2, 0), (-2, 0), (0, 2), (0, -2)))):
                        continue
                    hd = math.degrees(math.atan2(-(CENTER - x), CENTER - y))
                    self.vehicles.append(Vehicle(k, x, y, self.height(x, y), hd))
                    self.turrets.append(Turret(len(self.turrets), x, y, self.height(x, y) + 1.75, hd, "car", k))
                    done = True
                    break
                if done:
                    break

    def vehicle_by_id(self, vid):
        for v in self.vehicles:
            if v.id == vid:
                return v
        return None

    def build_castle(self):
        cx = cy = CENTER
        H, T, ZW, ZT, PW = 22.0, 3.0, 5.0, 8.0, 0.6
        x0, x1, y0, y1 = cx - H, cx + H, cy - H, cy + H
        g0, g1 = cx - 4.0, cx + 4.0                     # Tore im Süden und Norden
        B = self.add_box
        for a, b, c, d in ((x0, y0, g0, y0 + T), (g1, y0, x1, y0 + T),
                           (x0, y1 - T, g0, y1), (g1, y1 - T, x1, y1),
                           (x0, y0, x0 + T, y1), (x1 - T, y0, x1, y1)):
            B(a, b, c, d, -2, ZW, STONE, True)          # Mauern mit Wehrgang
        for a, b, c, d in ((x0, y0, g0, y0 + PW), (g1, y0, x1, y0 + PW),
                           (x0, y1 - PW, g0, y1), (g1, y1 - PW, x1, y1),
                           (x0, y0, x0 + PW, y1), (x1 - PW, y0, x1, y1)):
            B(a, b, c, d, ZW, ZW + 1.2, STONE_D)        # Brüstung aussen
        n, sd = 6, 0.7
        for sx in (-1, 1):
            for sy in (-1, 1):
                tx, ty = cx + sx * H, cy + sy * H
                B(tx - 3.5, ty - 3.5, tx + 3.5, ty + 3.5, -2, ZT, STONE, True)       # Eckturm
                ex, ey = tx + sx * 3.5, ty + sy * 3.5
                B(min(ex, ex - sx * PW), ty - 3.5, max(ex, ex - sx * PW), ty + 3.5, ZT, ZT + 1.2, STONE_D)
                B(tx - 3.5, min(ey, ey - sy * PW), tx + 3.5, max(ey, ey - sy * PW), ZT, ZT + 1.2, STONE_D)
                fx, fy = tx - sx * 3.5, ty - sy * 3.5   # Innenkanten des Turms
                wy = (y0 + PW) if sy < 0 else (y1 - T)  # Wehrgang der Nord/Süd-Mauer
                wxx = (x0 + PW) if sx < 0 else (x1 - T)  # Wehrgang der West/Ost-Mauer
                if sx < 0:
                    self.stairs(fx + n * sd, wy, "W", n, T - PW, ZW, 0.5, sd)
                else:
                    self.stairs(fx - n * sd, wy, "E", n, T - PW, ZW, 0.5, sd)
                if sy < 0:
                    self.stairs(wxx, fy + n * sd, "S", n, T - PW, ZW, 0.5, sd)
                else:
                    self.stairs(wxx, fy - n * sd, "N", n, T - PW, ZW, 0.5, sd)
        # Treppen im Hof hinauf zu den Wehrgängen West und Ost
        self.stairs(x0 + T, cy - 10, "N", 10, 2.5, 0, 0.5, 0.8)
        self.stairs(x1 - T - 2.5, cy + 10, "S", 10, 2.5, 0, 0.5, 0.8)
        # Bergfried in der Mitte mit Treppe aufs Dach
        B(cx - 4, cy - 4, cx + 4, cy + 4, -2, 6.0, STONE, True)
        B(cx - 4, cy + 4 - PW, cx + 4, cy + 4, 6.0, 7.2, STONE_D)
        B(cx - 4, cy - 4, cx - 4 + PW, cy + 4, 6.0, 7.2, STONE_D)
        self.stairs(cx + 4 - 12 * 0.8, cy - 4 - 2.5, "E", 12, 2.5, 0, 0.5, 0.8)
        # niedrige Deckung: vor den Toren aussen und im Hof
        for s in (-1, 1):
            for a, b in ((cx - 5, cx - 2), (cx + 2, cx + 5)):
                B(a, cy + s * 27, b, cy + s * 27 + 0.7, -2, 1.2, STONE_D)
                B(cx + s * 27, a - cx + cy, cx + s * 27 + 0.7, b - cx + cy, -2, 1.2, STONE_D)
            B(cx - 5, cy + s * 14, cx + 5, cy + s * 14 + 0.7, -2, 1.2, STONE_D)
        # Kasematten: überdachte Räume an der Innenseite der Mauern (Schutz vor Feuer von oben und aussen)
        def casemate(xa, ya, xb, yb, front):
            B(xa, ya, xb, yb, 3.0, 3.5, STONE_D)                                 # Dach
            if front in "NS":
                B(xa, ya, xa + PW, yb, -2, 3.0, STONE)
                B(xb - PW, ya, xb, yb, -2, 3.0, STONE)
                fy = yb - PW if front == "N" else ya
                for k in (1 / 3, 2 / 3):
                    px = xa + (xb - xa) * k
                    B(px - 0.35, fy, px + 0.35, fy + PW, -2, 3.0, STONE)
            else:
                B(xa, ya, xb, ya + PW, -2, 3.0, STONE)
                B(xa, yb - PW, xb, yb, -2, 3.0, STONE)
                fx_ = xb - PW if front == "E" else xa
                for k in (1 / 3, 2 / 3):
                    py = ya + (yb - ya) * k
                    B(fx_, py - 0.35, fx_ + PW, py + 0.35, -2, 3.0, STONE)
        casemate(cx - 14, cy - 19, cx - 6, cy - 14, "N")
        casemate(cx + 6, cy - 19, cx + 14, cy - 14, "N")
        casemate(cx - 14, cy + 14, cx - 6, cy + 19, "S")
        casemate(cx - 19, cy + 4, cx - 14, cy + 14, "E")
        casemate(cx + 14, cy - 14, cx + 19, cy - 4, "W")
        # freistehende Mauerstücke (2 m, volle Deckung) um den Bergfried und Sprengschutz hinter den Toren
        for sx, sy in ((-1, -1), (1, -1), (-1, 1), (1, 1)):
            B(cx + sx * 10 - 2.5, cy + sy * 10, cx + sx * 10 + 2.5, cy + sy * 10 + 0.6, -2, 2.0, STONE_D)
        for sy in (-1, 1):
            B(cx - 2, cy + sy * 17, cx + 2, cy + sy * 17 + 0.6, -2, 2.2, STONE_D)
        # Flak auf zwei Ecktürmen der Burg (Bedienung per F)
        for sx, sy in ((-1, 1), (1, -1)):
            tx, ty = cx + sx * H, cy + sy * H
            B(tx - 0.45, ty - 0.45, tx + 0.45, ty + 0.45, ZT, ZT + 0.9, (0.30, 0.32, 0.34))
            self.turrets.append(Turret(len(self.turrets), tx, ty, ZT + 1.35,
                                       math.degrees(math.atan2(-(cx - tx), cy - ty)), "flak"))
        self.floors.append((x0 + T, y0 + T, x1 - T, y1 - T, COBBLE))
        self.flats.append((cx, cy, 36.0, 50.0))
        self.add_crate(cx - 12, cy + 8, 0.0)
        self.add_crate(cx + 12, cy - 8, 0.0)

    def build_helipads(self, pads=None):
        """Zwei Helipads auf gegenüberliegenden Seiten der Karte (West und Ost), je mit einem Helikopter."""
        if pads is None:
            pads = ((CENTER - 78.0, CENTER, 270.0), (CENTER + 78.0, CENTER, 90.0))
        for hid, (x, y, hd) in enumerate(pads):
            self.pads.append((x, y))
            self.flats.append((x, y, 11.0, 19.0))
            self.floors.append((x - 8.0, y - 8.0, x + 8.0, y + 8.0, (0.26, 0.27, 0.30)))
            white, yel = (0.92, 0.92, 0.9), (0.95, 0.8, 0.15)
            self.decor.append((x - 2.6, y - 3.2, x - 1.8, y + 3.2, 0.0, 0.04, white, True))     # "H"
            self.decor.append((x + 1.8, y - 3.2, x + 2.6, y + 3.2, 0.0, 0.04, white, True))
            self.decor.append((x - 2.6, y - 0.4, x + 2.6, y + 0.4, 0.0, 0.04, white, True))
            for sx in (-1, 1):
                for sy in (-1, 1):
                    self.decor.append((x + sx * 7.4 - 0.5, y + sy * 7.4 - 0.5, x + sx * 7.4 + 0.5, y + sy * 7.4 + 0.5,
                                       0.0, 0.05, yel, True))
            self.helis.append(Heli(hid, x, y, 0.0, hd))

    def build_runway(self):
        """Landebahn im Süden (Ost-West)."""
        c = CENTER
        y, hw = c - 76.0, 7.0
        x0, x1 = c - 50.0, c + 50.0
        self.runway = (x0, y - hw, x1, y + hw)
        for x in range(int(x0) - 6, int(x1) + 7, 8):
            self.flats.append((float(x), y, 10.0, 18.0))
        self.floors.append((x0, y - hw, x1, y + hw, (0.24, 0.24, 0.27)))
        white, red = (0.92, 0.92, 0.9), (0.9, 0.2, 0.15)
        for xa in range(int(x0) + 4, int(x1) - 4, 8):
            self.decor.append((xa, y - 0.2, xa + 4.0, y + 0.2, 0.0, 0.04, white, True))
        for sgn in (-1, 1):
            self.decor.append((x0, y + sgn * (hw - 0.5) - 0.12, x1, y + sgn * (hw - 0.5) + 0.12, 0.0, 0.04, white, True))
        for xe in (x0, x1 - 0.6):
            self.decor.append((xe, y - hw, xe + 0.6, y + hw, 0.0, 0.04, red, True))
            for yy in (y - hw, y + hw):
                self.decor.append((xe + 0.1, yy - 0.15, xe + 0.5, yy + 0.15, 0.0, 1.2, (0.9, 0.5, 0.1), False))

    def build_tower(self, cx, cy, side, crate):
        """Freistehender Turm (5x5, 9 m hoch) mit langer Treppe an der Seite 'side'."""
        hs, hh, n, sd, w, pw = 2.5, 9.0, 18, 0.7, 2.5, 0.6
        x0, x1, y0, y1 = cx - hs, cx + hs, cy - hs, cy + hs
        self.add_box(x0, y0, x1, y1, -2, hh, STONE, True)
        edges = {"W": (x0, y0, x0 + pw, y1), "E": (x1 - pw, y0, x1, y1),
                 "S": (x0, y0, x1, y0 + pw), "N": (x0, y1 - pw, x1, y1)}
        for s, e in edges.items():
            if s != side:
                self.add_box(*e, hh, hh + 1.2, STONE_D)
        if side == "E":
            self.stairs(x1, y1 - n * sd, "N", n, w, 0, 0.5, sd)
        elif side == "W":
            self.stairs(x0 - w, y0 + n * sd, "S", n, w, 0, 0.5, sd)
        elif side == "N":
            self.stairs(x0 + n * sd, y1, "W", n, w, 0, 0.5, sd)
        else:
            self.stairs(x1 - n * sd, y0 - w, "E", n, w, 0, 0.5, sd)
        self.flats.append((cx, cy, 17.0, 28.0))
        if crate:
            self.add_crate(cx, cy, hh)
        tx = cx - 1.7 if side == "E" else cx + 1.7           # Geschütz auf der Seite ohne Treppe
        ty = cy + 1.7
        self.add_box(tx - 0.45, ty - 0.45, tx + 0.45, ty + 0.45, hh, hh + 0.9, (0.30, 0.32, 0.34))
        self.turrets.append(Turret(len(self.turrets), tx, ty, hh + 1.35,
                                   math.degrees(math.atan2(-(CENTER - tx), CENTER - ty)), "mg"))

    def build_house(self, cx, cy, w, d, h, ops, crate=None, floor=WOOD_F, flat_r=10.0, col=PLASTER):
        t = 0.5
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
        self.wall_x(x0, x1, y0, y0 + t, h, ops.get("S", ()), col)
        self.wall_x(x0, x1, y1 - t, y1, h, ops.get("N", ()), col)
        self.wall_y(y0 + t, y1 - t, x0, x0 + t, h, ops.get("W", ()), col)
        self.wall_y(y0 + t, y1 - t, x1 - t, x1, h, ops.get("E", ()), col)
        self.add_box(x0 - 0.3, y0 - 0.3, x1 + 0.3, y1 + 0.3, h, h + 0.4, ROOF)
        self.floors.append((x0, y0, x1, y1, floor))
        self.flats.append((cx, cy, flat_r, flat_r + 10.0))
        if crate:
            self.add_crate(crate[0], crate[1], 0.0)

    def build_ruin(self, cx, cy):
        for a, b, c, d in ((cx - 5, cy - 4, cx + 1, cy - 3.4), (cx - 5, cy - 4, cx - 4.4, cy + 2),
                           (cx + 3, cy - 4, cx + 3.6, cy - 1), (cx - 2, cy + 3, cx + 5, cy + 3.6),
                           (cx + 5, cy - 2, cx + 5.6, cy + 3.6)):
            self.add_box(a, b, c, d, -2, 2.6, STONE_D)
        self.add_box(cx - 1, cy - 1, cx + 0.2, cy + 0.2, -2, 1.2, STONE_D)
        self.flats.append((cx, cy, 10.0, 20.0))

    # ------------------------------------------------------------ Aussenposten (nur Standardkarte)
    def build_outposts(self):
        """Zusätzliche Deckung auf der grossen Standardkarte - am Boden UND gegen Beschuss aus der Luft
        (Dächer, Überhänge, überdachte Gassen): Containerlager, Bunkerstellung, Scheune, Felsformation,
        Ruinendorf, Hangar an der Landebahn, Splitterschutz an den Helipads, kleine Unterstände."""
        c = CENTER
        self.container_yard(c + 74, c - 36)
        self.bunker_post(c - 74, c - 36)
        self.barn(c + 76, c + 38)
        self.rock_outcrop(c - 76, c + 40)
        self.ruin_village(c, c + 84)
        self.hangar(c - 66, c - 77)
        for sx in (-1, 1):
            self.pad_walls(c + sx * 78.0, c, sx)
        for x, y, side in ((c + 48, c - 20, "W"), (c - 50, c + 18, "E"), (c + 20, c - 58, "N"),
                           (c - 22, c + 62, "S"), (c + 52, c + 74, "S"), (c - 52, c - 70, "N")):
            self.lean_to(x, y, side)

    def sandbags(self, x0, y0, x1, y1, h=1.15):
        self.add_box(x0, y0, x1, y1, -1.0, h, SANDBAG)

    def shed_roof(self, x0, y0, x1, y1, z, col=ROOF, t=0.35, post=0.35, posts=None):
        """Dach auf Pfosten (offen): Deckung von oben. posts = Liste (x, y) oder automatisch an den Ecken."""
        if posts is None:
            posts = [(x0 + post / 2, y0 + post / 2), (x1 - post / 2, y0 + post / 2),
                     (x0 + post / 2, y1 - post / 2), (x1 - post / 2, y1 - post / 2)]
        for px, py in posts:
            self.add_box(px - post / 2, py - post / 2, px + post / 2, py + post / 2, -1.0, z, WOOD_F)
        self.add_box(x0 - 0.3, y0 - 0.3, x1 + 0.3, y1 + 0.3, z, z + t, col, True)

    def container(self, x, y, along_x, col, z0=0.0, hollow=False):
        """Schiffscontainer 6 x 2,4 x 2,6 m. hollow: an den Enden offen (begehbar, Dach schützt von oben)."""
        L, W, H, t = 6.0, 2.4, 2.6, 0.14
        hx, hy = (L / 2, W / 2) if along_x else (W / 2, L / 2)
        x0, y0, x1, y1 = x - hx, y - hy, x + hx, y + hy
        zb = -1.0 if z0 <= 0.0 else z0
        if not hollow:
            self.add_box(x0, y0, x1, y1, zb, z0 + H, col, True)
            return
        if along_x:
            self.add_box(x0, y0, x1, y0 + t, zb, z0 + H, col, True)
            self.add_box(x0, y1 - t, x1, y1, zb, z0 + H, col, True)
        else:
            self.add_box(x0, y0, x0 + t, y1, zb, z0 + H, col, True)
            self.add_box(x1 - t, y0, x1, y1, zb, z0 + H, col, True)
        self.add_box(x0, y0, x1, y1, z0 + H - t, z0 + H, col)

    def container_yard(self, cx, cy):
        """Containerlager: Gassen zwischen zweistöckigen Stapeln, begehbare Container, überdachte Gasse,
        Kistentreppe auf die Stapel (Aussichtspunkt 5,2 m)."""
        C = CONT_COLS
        # drei Spalten (x = -8, 0, 8) zu je vier Containern, dazwischen Gassen
        for i, (dx, dy, stack, hollow) in enumerate((
                (-8.0, -6.5, 2, False), (-8.0, -3.6, 1, True), (-8.0, 3.2, 2, False), (-8.0, 6.1, 1, False),
                (0.0, -6.5, 1, False), (0.0, -0.8, 1, True), (0.0, 6.1, 2, False), (0.0, 3.2, 2, False),
                (8.0, -6.5, 2, False), (8.0, -3.6, 2, False), (8.0, 3.2, 1, True), (8.0, 6.1, 1, False))):
            col = C[i % len(C)]
            self.container(cx + dx, cy + dy, True, col, 0.0, hollow)
            if stack > 1:
                self.container(cx + dx + 0.3, cy + dy, True, C[(i + 2) % len(C)], 2.6)
        # Planen über der Mittelgasse: zusammen mit dem begehbaren Container in der Mitte ein von oben
        # gedeckter Gang quer durchs Lager (Schutz vor Helikoptern)
        tarp = (0.35, 0.42, 0.30)
        for x0 in (cx - 11.0, cx + 5.0):
            self.add_box(x0, cy - 2.4, x0 + 6.0, cy + 2.0, 2.48, 2.62, tarp)
        # Kistentreppe (je 1,3 m) auf den zweistöckigen Stapel im Nordwesten: Aussichtspunkt in 5,2 m Höhe
        for ox, h in ((-13.5, 1.3), (-12.5, 2.6), (-11.5, 3.9)):
            self.add_box(cx + ox - 0.5, cy + 2.2, cx + ox + 0.5, cy + 4.2, -1.0, h, WOOD_F)
        self.add_crate(cx, cy - 0.8, 0.0)                # Lootkiste im begehbaren Container in der Mitte
        self.flats.append((cx, cy, 16.0, 26.0))

    def bunker_post(self, cx, cy):
        """Betonbunker mit Sehschlitzen Richtung Burg, dicker Decke, Eingang hinten; davor Sandsack-Stellungen."""
        w, d, h = 9.0, 6.0, 2.8
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
        slit = lambda a, b: [(a, 1.3, 1.25, 1.65), (b, 1.3, 1.25, 1.65)]       # noqa: E731
        t = 0.6
        self.wall_y(y0 + t, y1 - t, x1 - t, x1, h, slit(cy - 1.4, cy + 1.4), CONCRETE)          # Front (Ost)
        self.wall_y(y0 + t, y1 - t, x0, x0 + t, h, [(cy, 1.0, 0.0, 2.3)], CONCRETE)            # Eingang (West)
        self.wall_x(x0, x1, y0, y0 + t, h, [(cx + 1.5, 1.1, 1.25, 1.65)], CONCRETE)            # Süd mit Schlitz
        self.wall_x(x0, x1, y1 - t, y1, h, [(cx + 1.5, 1.1, 1.25, 1.65)], CONCRETE)            # Nord mit Schlitz
        self.add_box(x0 - 0.6, y0 - 0.6, x1 + 0.6, y1 + 0.6, h, h + 0.7, CONCRETE, True)       # Betondecke
        self.floors.append((x0, y0, x1, y1, CONCRETE))
        self.add_crate(cx - 2.6, cy + 1.6, 0.0)
        # Rampe/Erdhügel hinten aufs Dach (Stufen aus Sandsäcken)
        self.stairs(x0 - 0.6 - 7 * 0.7, cy - 3.8, "E", 7, 1.4, 0, 0.5, 0.7, SANDBAG)
        # Sandsack-Stellungen vor dem Bunker (U-Form) und seitlich
        for oy in (-6.5, 6.5):
            fx = x1 + 6.0
            self.sandbags(fx, cy + oy - 2.0, fx + 0.8, cy + oy + 2.0)
            self.sandbags(fx - 2.6, cy + oy - 2.0, fx, cy + oy - 1.3)
            self.sandbags(fx - 2.6, cy + oy + 1.3, fx, cy + oy + 2.0)
        self.sandbags(x1 + 9.0, cy - 1.8, x1 + 9.8, cy + 1.8, 1.0)
        self.sandbags(x0 - 5.0, y1 + 3.0, x0 - 1.0, y1 + 3.8)
        self.shed_roof(x1 + 3.4, cy + 5.0, x1 + 6.6, cy + 8.0, 2.3, (0.33, 0.38, 0.28))   # Tarndach über einer Stellung
        self.flats.append((cx + 2.0, cy, 16.0, 26.0))

    def barn(self, cx, cy):
        """Offene Scheune: grosses Dach auf Pfosten, Rückwand, halbe Seitenwände, Heuboden mit Treppe,
        Kistenstapel als Deckung; davor ein Pferch mit Zaun."""
        w, d, h = 15.0, 10.0, 4.6
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
        posts = [(x0 + 0.2, y0 + 0.2), (cx - 2.5, y0 + 0.2), (cx + 2.5, y0 + 0.2), (x1 - 0.2, y0 + 0.2),
                 (x0 + 0.2, y1 - 0.2), (cx - 2.5, y1 - 0.2), (cx + 2.5, y1 - 0.2), (x1 - 0.2, y1 - 0.2)]
        self.shed_roof(x0, y0, x1, y1, h, ROOF, 0.45, 0.4, posts)
        self.add_box(x1 - 0.4, y0, x1, y1, -1.0, h, WOOD_F, True)                  # Rückwand (Ost)
        self.add_box(x0 + 5.5, y0, x1, y0 + 0.3, -1.0, 2.2, WOOD_F, True)           # halbe Seitenwände
        self.add_box(x0 + 5.5, y1 - 0.3, x1, y1, -1.0, 2.2, WOOD_F, True)
        self.add_box(cx + 1.0, y0 + 0.3, x1 - 0.4, y1 - 0.3, 2.2, 2.4, WOOD_F)      # Heuboden (Osthälfte)
        self.stairs(cx + 1.0 - 6 * 0.7, y0 + 0.4, "E", 6, 1.3, 0, 0.4, 0.7, WOOD_F)
        self.floors.append((x0, y0, x1, y1, WOOD_F))
        hay = (0.74, 0.64, 0.36)
        for bx, by, bw, bd, bh in ((cx - 4.5, cy + 1.5, 2.4, 1.2, 1.2), (cx - 4.5, cy + 1.5, 1.2, 1.2, 2.4),
                                   (cx - 1.5, cy - 2.2, 1.2, 2.4, 1.2), (cx + 3.5, cy + 2.5, 2.4, 1.2, 1.2),
                                   (cx + 4.5, cy - 1.0, 1.2, 1.2, 1.2)):
            self.add_box(bx, by, bx + bw, by + bd, -1.0, bh, hay)                      # Heuballen
        self.add_crate(cx + 4.0, cy + 1.0, 2.4)                                      # Lootkiste auf dem Heuboden
        # Pferch mit Zaun westlich der Scheune (Öffnung zur Scheune)
        px0, px1, py0, py1 = x0 - 12.0, x0 - 2.0, cy - 6.0, cy + 6.0
        fence = (0.42, 0.31, 0.21)
        self.add_box(px0, py0, px1, py0 + 0.15, -1.0, 1.0, fence)
        self.add_box(px0, py1 - 0.15, px1, py1, -1.0, 1.0, fence)
        self.add_box(px0, py0, px0 + 0.15, cy - 1.5, -1.0, 1.0, fence)
        self.add_box(px0, cy + 1.5, px0 + 0.15, py1, -1.0, 1.0, fence)
        self.add_box(px0 + 3.0, cy - 2.0, px0 + 4.2, cy - 0.8, -1.0, 1.2, hay)
        self.flats.append((cx - 4.0, cy, 17.0, 27.0))

    def rock_outcrop(self, cx, cy):
        """Felsformation: Felsbogen (Überhang = Deckung von oben), grosse Blöcke, gestufter Aussichtsfelsen."""
        R = ROCK_C
        self.add_box(cx - 4.5, cy - 1.5, cx - 2.5, cy + 1.5, -1.0, 4.0, R, True)         # Bogen: zwei Pfeiler ...
        self.add_box(cx + 2.5, cy - 1.0, cx + 4.3, cy + 1.6, -1.0, 4.4, R, True)
        self.add_box(cx - 5.0, cy - 2.2, cx + 4.8, cy + 2.4, 4.0, 5.4, R, True)          # ... und Deckplatte
        self.add_box(cx - 3.0, cy + 2.4, cx + 1.0, cy + 6.5, 3.6, 4.6, R)                # Überhang nach Norden
        self.add_box(cx - 3.2, cy + 5.0, cx - 1.6, cy + 6.6, -1.0, 3.6, R, True)         # Stütze
        # gestufter Aussichtsfelsen (je 1,2 m, mit Sprung erreichbar)
        for ox, oy, hh in ((7.0, -4.0, 1.2), (8.6, -4.2, 2.4), (10.2, -4.0, 3.6)):
            self.add_box(cx + ox - 0.9, cy + oy - 1.4, cx + ox + 0.9, cy + oy + 1.4, -1.0, hh, R, True)
        self.add_box(cx + 9.4, cy - 6.4, cx + 11.4, cy - 2.6, -1.0, 3.6, R, True)
        # verstreute Blöcke (geduckt / stehend Deckung)
        for ox, oy, sx, sy, hh in ((-9.0, -3.0, 2.2, 1.6, 1.3), (-8.0, 4.5, 1.6, 2.6, 2.2), (-2.0, -7.0, 3.0, 1.4, 1.2),
                                   (4.0, 8.0, 2.0, 2.0, 2.4), (-12.0, 1.0, 1.4, 1.4, 1.1), (1.5, -10.0, 1.8, 2.4, 2.0)):
            self.add_box(cx + ox - sx / 2, cy + oy - sy / 2, cx + ox + sx / 2, cy + oy + sy / 2, -1.0, hh, R, True)
        self.flats.append((cx, cy, 15.0, 25.0))

    def ruin_village(self, cx, cy):
        """Ruinendorf: zerschossene Häuser mit Teildächern, eingestürzte Mauern, ein Brunnen."""
        P, S = PLASTER, STONE_D
        # Haus West: Dach nur zur Hälfte, Ostwand eingestürzt
        x0, x1, y0, y1 = cx - 19.0, cx - 10.0, cy - 4.0, cy + 3.0
        self.wall_x(x0, x1, y0, y0 + 0.5, 3.2, [(cx - 14.5, 1.1, 0.0, 2.4)], P)
        self.wall_x(x0, x1, y1 - 0.5, y1, 3.2, [(cx - 16.5, 0.9, 1.2, 2.2), (cx - 12.0, 0.9, 1.2, 2.2)], P)
        self.wall_y(y0 + 0.5, y1 - 0.5, x0, x0 + 0.5, 3.2, [(cy - 0.5, 0.9, 1.2, 2.2)], P)
        self.add_box(x1 - 0.5, y0 + 0.5, x1, cy - 1.5, -2, 1.4, P, True)                  # Mauerrest
        self.add_box(x0 - 0.3, y0 - 0.3, cx - 13.5, y1 + 0.3, 3.2, 3.6, ROOF)              # halbes Dach
        self.floors.append((x0, y0, x1, y1, WOOD_F))
        # Haus Mitte: zwei Stockwerke, Obergeschoss ohne Dach (Kampfplattform), Treppe innen
        x0, x1, y0, y1 = cx - 4.0, cx + 5.0, cy - 2.0, cy + 6.0
        self.wall_x(x0, x1, y0, y0 + 0.5, 3.0, [(cx + 2.5, 1.1, 0.0, 2.4), (cx - 2.0, 0.9, 1.2, 2.2)], S)
        self.wall_x(x0, x1, y1 - 0.5, y1, 3.0, [(cx, 0.9, 1.2, 2.2)], S)
        self.wall_y(y0 + 0.5, y1 - 0.5, x0, x0 + 0.5, 3.0, [(cy + 2.0, 0.9, 1.2, 2.2)], S)
        self.wall_y(y0 + 0.5, y1 - 0.5, x1 - 0.5, x1, 3.0, [(cy + 2.0, 0.9, 1.2, 2.2)], S)
        self.add_box(x0, cy + 1.5, x1, y1, 3.0, 3.3, WOOD_F)                             # Zwischendecke (Nordteil)
        self.stairs(x0 + 0.5, cy - 1.4, "E", 6, 1.2, 0, 0.5, 0.7, WOOD_F)                 # 6 Stufen = 3 m
        self.add_box(x0 + 0.5 + 6 * 0.7, cy - 1.4, x0 + 0.5 + 6 * 0.7 + 1.2, cy + 1.5, 2.7, 3.0, WOOD_F)  # Podest
        self.add_box(x0, y1 - 0.5, x1, y1, 3.3, 4.4, S, True)                            # Brüstung OG Nord
        self.add_box(x0, cy + 1.5, x0 + 0.5, y1, 3.3, 4.4, S)
        self.add_box(x1 - 0.5, cy + 1.5, x1, cy + 3.5, 3.3, 4.4, S)
        self.floors.append((x0, y0, x1, y1, WOOD_F))
        # Haus Ost: nur noch Grundmauern und eine Ecke
        x0, x1, y0, y1 = cx + 11.0, cx + 19.0, cy - 3.0, cy + 4.0
        self.add_box(x0, y0, x0 + 0.5, y1, -2, 2.8, P, True)
        self.add_box(x0, y1 - 0.5, cx + 15.0, y1, -2, 2.8, P, True)
        self.add_box(x0, y0, x1, y0 + 0.5, -2, 1.1, P, True)
        self.add_box(x1 - 0.5, y0, x1, cy + 1.0, -2, 1.6, P, True)
        self.add_box(x0 - 0.3, cy + 0.5, cx + 15.3, y1 + 0.3, 2.8, 3.1, ROOF)                # Rest vom Dach
        self.floors.append((x0, y0, x1, y1, COBBLE))
        # Brunnen und Mauerreste auf dem Platz
        self.add_box(cx + 6.8, cy - 7.5, cx + 8.6, cy - 5.7, -1.0, 0.9, S, True)
        self.add_box(cx - 8.0, cy - 8.0, cx - 4.0, cy - 7.4, -1.0, 1.2, S)
        self.add_box(cx + 1.0, cy - 9.5, cx + 1.6, cy - 6.5, -1.0, 1.8, S)
        self.add_crate(cx - 15.0, cy + 1.0, 0.0)
        self.flats.append((cx, cy, 23.0, 32.0))

    def hangar(self, cx, cy):
        """Flugzeughangar am Westende der Landebahn: grosses Dach (Schutz vor Helikoptern), offen nach Osten."""
        w, d, h = 15.0, 14.0, 6.0
        x0, x1, y0, y1 = cx - w / 2, cx + w / 2, cy - d / 2, cy + d / 2
        M = (0.55, 0.57, 0.60)
        self.wall_y(y0, y1, x0, x0 + 0.4, h, [(cy, 0.9, 0.0, 2.3)], M)                    # Rückwand mit Tür
        self.wall_x(x0, x1, y0, y0 + 0.4, h, [(cx - 3.0, 0.9, 1.6, 2.6), (cx + 3.0, 0.9, 1.6, 2.6)], M)
        self.wall_x(x0, x1, y1 - 0.4, y1, h, [(cx - 3.0, 0.9, 1.6, 2.6), (cx + 3.0, 0.9, 1.6, 2.6)], M)
        self.add_box(x0 - 0.4, y0 - 0.4, x1 + 0.6, y1 + 0.4, h, h + 0.5, M, True)          # Dach
        self.floors.append((x0, y0, x1, y1, CONCRETE))
        for bx, by, bw, bd, bh in ((cx - 4.5, cy - 4.5, 2.4, 2.4, 1.3), (cx - 4.5, cy - 4.5, 1.2, 1.2, 2.6),
                                   (cx + 1.0, cy + 2.5, 1.2, 2.4, 1.3), (cx - 3.0, cy + 3.5, 2.4, 1.2, 1.3),
                                   (cx + 3.5, cy - 3.0, 1.2, 1.2, 1.3)):
            self.add_box(bx, by, bx + bw, by + bd, -1.0, bh, WOOD_F)
        self.add_crate(cx - 5.5, cy + 4.5, 0.0)
        # Betonbarrieren entlang der Landebahn (Nordseite)
        for k in range(5):
            bx = cx + 18.0 + k * 19.0
            self.add_box(bx, cy + 9.0, bx + 3.2, cy + 9.7, -1.0, 1.1, CONCRETE)
        self.flats.append((cx, cy, 14.0, 24.0))

    def pad_walls(self, px, py, sx):
        """Splitterschutzwände an der Aussenseite eines Helipads (mit Lücken), dazu zwei Sandsack-Nester."""
        ox = px + sx * 11.0
        for a, b in ((-9.0, -2.0), (2.0, 9.0)):
            self.add_box(min(ox, ox + sx * 0.6), py + a, max(ox, ox + sx * 0.6), py + b, -1.0, 2.6, CONCRETE, True)
        for oy in (-11.0, 11.0):
            self.add_box(px - 4.0, py + oy - 0.3, px + 4.0, py + oy + 0.3, -1.0, 2.6, CONCRETE, True)
        for oy in (-1, 1):                                # Sandsack-Winkel auf der Innenseite (zur Burg)
            nx, ny = px - sx * 11.5, py + oy * 9.5
            self.sandbags(nx - 1.4, ny - 0.4, nx + 1.4, ny + 0.4)
            self.sandbags(nx - 1.4, min(ny, ny - oy * 2.0), nx - 0.6, max(ny, ny - oy * 2.0))

    def lean_to(self, cx, cy, side):
        """Kleiner Unterstand: Dach auf Pfosten (Deckung von oben), Sandsäcke zur Seite 'side'."""
        self.shed_roof(cx - 2.0, cy - 1.6, cx + 2.0, cy + 1.6, 2.3, (0.33, 0.38, 0.28))
        if side in "NS":
            y = cy + 1.6 if side == "N" else cy - 2.4
            self.sandbags(cx - 2.2, y, cx + 2.2, y + 0.8)
        else:
            x = cx + 2.0 if side == "E" else cx - 2.8
            self.sandbags(x, cy - 1.8, x + 0.8, cy + 1.8)
        self.flats.append((cx, cy, 5.0, 12.0))

    def add_groves(self, rng):
        """Wäldchen (dichte Baumgruppen): Sichtschutz gegen Helikopter am Rand des Tals."""
        c = CENTER
        for gx, gy in ((c - 42, c - 96), (c + 46, c + 96), (c + 98, c - 70), (c - 98, c + 70),
                       (c - 100, c - 30), (c + 100, c + 8)):
            placed = 0
            for _ in range(80):
                if placed >= 13:
                    break
                a, r = rng.uniform(0, 2 * math.pi), 9.0 * math.sqrt(rng.random())
                x, y = gx + math.cos(a) * r, gy + math.sin(a) * r
                br = rng.uniform(1.8, 2.8)
                if not (6 < x < WORLD - 6 and 6 < y < WORLD - 6) or mountain(x, y) > 12.0:
                    continue
                if any(math.hypot(x - fx, y - fy) < rin + 2 for fx, fy, rin, _ro in self.flats):
                    continue
                if any(math.hypot(x - p.x, y - p.y) < (2.6 if p.kind == "tree" else p.r + 1.5) for p in self.props):
                    continue
                p = Prop("tree", x, y, br, 0.45)
                p.base_r = br
                self.props.append(p)
                placed += 1

    def add_cover(self, rng):
        """Verstreute Deckungsblöcke im Gelände (nach Bäumen und Felsen)."""
        placed = tries = 0
        want = 30 if self.mtn else 12
        while placed < want and tries < want * 35:
            tries += 1
            x, y = rng.uniform(10, WORLD - 10), rng.uniform(10, WORLD - 10)
            if self.mtn and mountain(x, y) > 0.3:
                continue
            sx, sy = rng.choice((1.2, 1.6, 2.4)), rng.choice((1.2, 2.0, 3.0))
            top = rng.choice((1.1, 1.4))
            if any(math.hypot(x - fx, y - fy) < rin + 3 for fx, fy, rin, _ro in self.flats):
                continue
            if any(math.hypot(x - p.x, y - p.y) < p.r + 3 for p in self.props):
                continue
            h0 = self.height(x, y)
            self.add_box(x - sx / 2, y - sy / 2, x + sx / 2, y + sy / 2, h0 - 2.0, h0 + top, STONE_D)
            placed += 1

    def build_grids(self):
        c = self.GRID
        self.grid = {}
        for p in self.props:
            p.z = self.height(p.x, p.y)
            if p.kind == "rock":
                p.hit_r, p.hit_h = p.base_r * 0.9, p.base_r * 1.0
            elif p.kind == "tree":
                p.hit_r, p.hit_h = 0.4, 5.0
            if p.hit_r > 0:
                for i in range(int((p.x - p.hit_r) // c), int((p.x + p.hit_r) // c) + 1):
                    for j in range(int((p.y - p.hit_r) // c), int((p.y + p.hit_r) // c) + 1):
                        self.grid.setdefault((i, j), []).append(p)
        self.bgrid = {}
        for b in self.boxes:
            for i in range(int(b.x0 // c), int(b.x1 // c) + 1):
                for j in range(int(b.y0 // c), int(b.y1 // c) + 1):
                    self.bgrid.setdefault((i, j), []).append(b)

    def boxes_near(self, x0, y0, x1, y1):
        c = self.GRID
        out = []
        for i in range(int(min(x0, x1) // c), int(max(x0, x1) // c) + 1):
            for j in range(int(min(y0, y1) // c), int(max(y0, y1) // c) + 1):
                out += self.bgrid.get((i, j), ())
        return out

    def props_near(self, x0, y0, x1, y1):
        c = self.GRID
        out = []
        for i in range(int(min(x0, x1) // c), int(max(x0, x1) // c) + 1):
            for j in range(int(min(y0, y1) // c), int(max(y0, y1) // c) + 1):
                out += self.grid.get((i, j), ())
        return out

    def in_solid(self, x, y, r, z=None):
        """True, wenn ein Kreis (x,y,r) auf Bodenhöhe in einem Quader steckt."""
        if z is None:
            z = self.height(x, y)
        for b in self.boxes_near(x - r, y - r, x + r, y + r):
            if (z < b.z1 - STEP_H and z + PLAYER_H > b.z0
                    and b.x0 - r < x < b.x1 + r and b.y0 - r < y < b.y1 + r):
                return True
        return False

    def spawn_ok(self, x, y):
        if not (8 < x < WORLD - 8 and 8 < y < WORLD - 8):
            return False
        if self.mtn and mountain(x, y) > 1.0:            # nicht im Gebirge starten
            return False
        if self.height(x, y) < WATER_LEVEL + 0.6:
            return False
        if any(math.hypot(x - px, y - py) < r * 1.8 for px, py, r in self.ponds):
            return False
        if any(math.hypot(x - p.x, y - p.y) < p.solid_r + 1.5 for p in self.props):
            return False
        return not self.in_solid(x, y, 1.5)

    def make_spawns(self, rng):
        """Viele Startpunkte (36 Sektoren um die Burg, verschiedene Radien). Die Liste ist so sortiert,
        dass die ersten Einträge möglichst weit auseinander liegen (so starten die ersten Spieler verteilt)."""
        pts = []
        radii = (58.0, 70.0, 82.0, 64.0, 76.0) + ((92.0, 100.0) if self.mtn else ())
        given = [p for p in (self.map.get("spawns") or ()) if self.spawn_ok(*p)] if self.map else []
        if self.mc:
            given = []
            for x, y, z in self.mc["meta"]["spawns"]:
                given.append((x, y))
                self.spawn_zs[(round(x, 2), round(y, 2))] = z
        for k in range(0 if given else 36):
            ang = math.radians(5.0 + 10.0 * k)
            base = radii[k % len(radii)]
            for t in range(40):
                r = base if t == 0 else base + rng.uniform(-8, 8)
                a = ang + (0.0 if t == 0 else rng.uniform(-0.08, 0.08))
                x, y = CENTER + math.cos(a) * r, CENTER + math.sin(a) * r
                if self.spawn_ok(x, y):
                    pts.append((x, y))
                    break
        pts = given or pts
        if not pts:
            return [(CENTER + 30.0, CENTER)]
        order = [pts.pop(0)]
        while pts:                                   # entferntester Punkt zuerst
            nxt = max(pts, key=lambda p: min(math.hypot(p[0] - q[0], p[1] - q[1]) for q in order))
            pts.remove(nxt)
            order.append(nxt)
        return order

    def hills_height(self, x, y):
        """Grundgelände vor Ebenen und Teichen: Kartenraster (bilinear) oder die Standard-Hügel."""
        g = self.hgrid
        if g is None:
            if self.mtn:                                 # Hügel um die Burg wie auf der alten 200-m-Karte, dazu das Gebirge
                return hills(x - CENTER + 100.0, y - CENTER + 100.0) + mountain(x, y)
            return hills(x, y)
        n, st, z = g
        fx = min(n - 1.000001, max(0.0, x / st))
        fy = min(n - 1.000001, max(0.0, y / st))
        i, j = int(fx), int(fy)
        tx, ty = fx - i, fy - j
        k = j * n + i
        a = z[k] + (z[k + 1] - z[k]) * tx
        b = z[k + n] + (z[k + n + 1] - z[k + n]) * tx
        return a + (b - a) * ty

    def height(self, x, y):
        """Bodenhöhe für Spielfiguren: Gelände, aber Treppenschächte sind Löcher."""
        for x0, y0, x1, y1 in self.voids:
            if x0 <= x <= x1 and y0 <= y <= y1:
                return TUN_Z
        return self.surface_height(x, y)

    def on_ladder(self, x, y, z):
        """Steckt der Körper (Füsse z .. z+1,7) in einer Leiter-Zelle?"""
        zs = self.ladders.get((int(math.floor(x)), int(math.floor(y))))
        if not zs:
            return False
        return any(z0 <= z + 1.5 and z0 + 1.0 >= z + 0.1 for z0 in zs)

    def spawn_z(self, x, y):
        """Starthöhe der Füsse: bei Minecraft-Karten die Höhe des Standplatzes, sonst das Gelände."""
        z = self.spawn_zs.get((round(x, 2), round(y, 2)))
        return self.height(x, y) if z is None else z

    def surface_height(self, x, y):
        """Sichtbares Gelände (ohne Löcher) - die Karte wird damit gezeichnet."""
        if self.mc:
            return self.mc_floor
        h = self.hills_height(x, y)
        m, dip = 1.0, 0.0
        for fx, fy, rin, rout in self.flats:
            dx, dy = x - fx, y - fy
            if dx > rout or dx < -rout or dy > rout or dy < -rout:
                continue                                 # weit weg: Faktor 1 (spart Zeit, gleiches Ergebnis)
            m *= smoothstep(rin, rout, math.hypot(dx, dy))
        for px, py, r in self.ponds:
            d = math.hypot(x - px, y - py)
            if d >= r * 2.2:
                continue
            m *= smoothstep(r * 1.0, r * 2.2, d)
            dip -= 3.0 * (1 - smoothstep(r * 0.3, r * 1.0, d))
        return h * m + dip

    def floor_at(self, x, y, z):
        """Höhe des Bodens unter (x,y) für jemanden, dessen Füsse auf Höhe z sind:
        Gelände oder die höchste Quader-Oberkante, die man noch erreichen kann."""
        g = self.height(x, y)
        if z < -1.0 and self.tunnels and self.in_tunnel(x, y):
            g = TUN_Z                                    # im Tunnel: der Boden ein Stockwerk tiefer
        for b in self.boxes_near(x, y, x, y):
            if b.x0 <= x <= b.x1 and b.y0 <= y <= b.y1 and g < b.z1 <= z + STEP_H:
                g = b.z1
        return g

    def ceiling_at(self, x, y, z):
        """Unterkante des tiefsten Quaders über dem Kopf (für Sprünge unter Decken)."""
        c = 1e9
        for b in self.boxes_near(x, y, x, y):
            if b.x0 <= x <= b.x1 and b.y0 <= y <= b.y1 and b.z0 > z + 1.0 and b.z0 < c:
                c = b.z0
        return c

    # ------------------------------------------------------------ Spawns
    def first_spawn(self, pid):
        return self.spawns[pid % len(self.spawns)]

    SPAWN_MIN_DEATH = 70.0       # so weit soll der neue Startpunkt vom Todesort entfernt sein

    def pick_spawn(self, pid):
        """Startpunkt: weit weg vom Todesort, von lebenden Gegnern und Monstern, und nicht zweimal derselbe.
        Zufall nur unter den guten Kandidaten."""
        me = self.players.get(pid)
        death = getattr(me, "death_pos", None)
        foes = [(p.x, p.y) for p in self.players.values() if p.pid != pid and p.hp > 0]
        foes += [(m.x, m.y) for m in self.mobs if m.state != "dead"]
        last = self.last_spawn.get(pid)
        scored = []
        for sx, sy in self.spawns:
            d_foe = min((math.hypot(sx - x, sy - y) for x, y in foes), default=150.0)
            d_death = math.hypot(sx - death[0], sy - death[1]) if death is not None else 150.0
            score = min(d_foe, 120.0) + 0.8 * min(d_death, 140.0)
            if d_death < self.SPAWN_MIN_DEATH:
                score -= 400.0 - 4.0 * d_death           # zu nah am Todesort: nur wenn es nichts anderes gibt
            if d_foe < 25.0:
                score -= 150.0                           # direkt neben einem Gegner: vermeiden
            if last is not None and math.hypot(sx - last[0], sy - last[1]) < 10.0:
                score -= 60.0
            scored.append((score + self.mrng.uniform(0.0, 12.0), (sx, sy)))
        best = max(scored)[1]
        self.last_spawn[pid] = best
        return best

    def can_respawn(self, pl):
        """Tot, Runde läuft und die Wartezeit ist um."""
        return pl.hp <= 0 and self.phase == "play" and pl.dead_age >= self.respawn_delay

    def respawn_player(self, pl):
        """Host/Einzelspiel: Figur neu aufstellen (nur mit der Pistole). Die Darstellung läuft über das
        Ereignis 'respawn'."""
        x, y = self.pick_spawn(pl.pid)
        pl.respawn(self, x, y)
        self.events.append(("respawn", pl.pid, round(x, 2), round(y, 2)))

    # ------------------------------------------------------------ Mobs
    def populate_mobs(self):
        k = 1.3 if self.mtn else 1.0                     # grössere Standardkarte: ein paar Monster mehr
        for kind, n in (("grunt", N_GRUNT), ("brute", N_BRUTE), ("huntress", N_HUNT),
                        ("colossus", N_COLOSSUS), ("drone", N_DRONE), ("critter", N_CRITTER), ("titan", N_TITAN)):
            cnt = int(n * k + 0.5) if kind not in ("colossus", "titan") else min(MAX_COLOSSUS, n)
            for _ in range(cnt):
                self.spawn_mob(kind, [], 0.0)

    def spawn_mob(self, kind, avoid, min_dist):
        """avoid: Liste von (x, y), von denen das neue Monster mind. min_dist entfernt sein soll."""
        rng = self.mrng
        for _ in range(80):
            x, y = rng.uniform(6, WORLD - 6), rng.uniform(6, WORLD - 6)
            if math.hypot(x - CENTER, y - CENTER) < 40.0:          # nicht in/an der Burg
                continue
            if self.mtn and mountain(x, y) > 1.0:                # nicht oben im Gebirge
                continue
            if any(math.hypot(x - ax, y - ay) < min_dist for ax, ay in avoid):
                continue
            if any(math.hypot(x - px, y - py) < r * 1.7 for px, py, r in self.ponds):
                continue
            if any(p.kind != "pond" and math.hypot(x - p.x, y - p.y) < p.solid_r + 1.2
                   for p in self.props):
                continue
            big = MOB_KINDS[kind]["scale"] * 0.45
            if self.in_solid(x, y, max(1.2, big + 0.8)):
                continue
            if big > 2.0 and any(p.kind != "pond" and math.hypot(x - p.x, y - p.y) < p.solid_r + big + 1.0
                                 for p in self.props):
                continue
            m = Mob(kind, x, y, self)
            m.id = self.next_mid
            self.next_mid += 1
            self.mobs.append(m)
            return True
        return False

    # ------------------------------------------------------------ Lärm
    def make_noise(self, x, y, r):
        """Geräusch mit Radius r bei (x, y): alarmiert jedes Monster, das näher als r * hear ist
        (nur beim Host bzw. im Einzelspiel - dort laufen die Monster)."""
        if r <= 0:
            return
        if NOISE_DEBUG:
            self.noise_log.append((x, y, r, 0.6))
        for m in self.mobs:
            if m.state == "dead":
                continue
            if (m.x - x) ** 2 + (m.y - y) ** 2 <= (r * MOB_KINDS[m.kind].get("hear", 1.0)) ** 2:
                m.on_noise(x, y, self)

    def player_noise(self, pl):
        """Lärmradius, den ein Spieler gerade durch Bewegung/Fahrzeug macht."""
        if pl.hp <= 0:
            return 0.0
        if pl.heli >= 0:
            hc = self.heli_by_id(pl.heli)
            return NOISE_HELI if hc is not None and not hc.ground else NOISE_VEHICLE
        if pl.vehicle >= 0:
            v = self.vehicle_by_id(pl.vehicle)
            return NOISE_VEHICLE if v is not None and abs(v.speed) > 1.0 else 0.0
        if pl.mount >= 0 or not pl.moving:
            return 0.0
        if pl.crouch > 0.5:
            return NOISE_CROUCH
        return NOISE_RUN if getattr(pl, "running", False) else NOISE_WALK

    def update_noise(self, dt, players):
        self.noise_clock -= dt
        if self.noise_clock > 0:
            return
        self.noise_clock = NOISE_TICK
        if self.mobs:
            for pl in players:
                r = self.player_noise(pl)
                if r > 0:
                    self.make_noise(pl.x, pl.y, r)
        if NOISE_DEBUG:
            self.noise_log = [(x, y, r, t - NOISE_TICK) for x, y, r, t in self.noise_log if t > NOISE_TICK]

    # ------------------------------------------------------------ Spielregeln
    def in_zone(self, pl):
        return math.hypot(pl.x - CENTER, pl.y - CENTER) <= ZONE_R

    def ranking(self):
        ps = list(self.players.values())
        if self.mode == "koth":
            ps.sort(key=lambda p: (-p.score, -p.kills, p.deaths))
        else:
            ps.sort(key=lambda p: (-(p.kills / max(1, p.deaths)), -p.kills, p.deaths))
        return ps

    def damage_player(self, pl, dmg, attacker=-1, wi=-1, head=False):
        """attacker = Spieler-ID des Schützen, -1 = Monster. head: Kopftreffer (für den Helm)."""
        if pl.hp <= 0 or pl.protect > 0 or self.phase != "play":
            return
        if pl.mount >= 0 and attacker == pl.pid:         # am Geschütz kann man sich nie selbst verletzen
            return
        instant = dmg >= 9000 or wi in (WI_FALL, WI_TOMAHAWK)   # Sofort-Tode: kein Schutz
        if not instant and wears(pl, "shield") and pl.shield_hp > 0 and wi != WI_FALL:
            absorb = min(pl.shield_hp, dmg)              # Schild fängt zuerst ab
            pl.shield_hp -= absorb
            pl.shield_t = 0.0
            dmg -= absorb
            if absorb > 0:
                self.events.append(("shieldhit", pl.pid, round(absorb, 1)))
            if dmg <= 0:
                return
        if not instant and dmg >= pl.hp:                 # tödlich: Helm (Kopf) bzw. Platte (Körper) rettet einmal
            save = "save_head" if head else "save_body"
            slot = "head" if head else "torso"
            gi = pl.gear.get(slot)
            if gi is not None and GEAR[gi].kind == save:
                pl.gear[slot] = None
                pl.hp = SAVE_HP
                pl.since_hurt = 0.0
                self.events.append(("gearbreak", pl.pid, gi, gear_list(pl)))
                self.events.append(("player_hurt", dmg, pl.pid))
                return
        pl.hp = max(0.0, pl.hp - dmg)
        pl.since_hurt = 0.0
        self.events.append(("player_hurt", dmg, pl.pid))
        if pl.hp <= 0:
            self.player_died(pl, attacker, wi)

    def player_died(self, pl, attacker, wi):
        pl.deaths += 1
        pl.death_pos = (pl.x, pl.y)
        if pl.melee_out:                                 # Nahkampfwaffe in der Hand: sie fällt (das Start-
            if pl.melee != START_MELEE:                  # Messer nicht), die Schusswaffen sind verloren
                self.add_drop(pl.x, pl.y, pl.z, -1, -1, pl.melee)
        else:
            act = pl.cur                                 # nur die Waffe in der Hand fällt auf den Boden,
            if not 0 <= act < len(WEAPONS) or act not in pl.slots:   # alle anderen sind verloren
                act = next((wi for wi in pl.slots if wi is not None), START_WEAPON)
            self.add_drop(pl.x, pl.y, pl.z, act)
        worn = [gi for gi in pl.gear.values() if gi is not None]
        if worn:                                         # dazu genau EIN zufälliges getragenes Teil
            self.add_drop(pl.x + 0.8, pl.y + 0.4, pl.z, -1, self.mrng.choice(worn))
        pl.gear = {sl: None for sl in GEAR_SLOTS}
        pl.slots = [None] * N_SLOTS
        pl.loot_history, pl.last_loot = {}, None         # Kisten-Gedächtnis gilt nur für ein Leben
        self.end_buff(pl)                                # Buff läuft beim Tod sofort ab
        pl.stun_t = pl.stun_lock = 0.0
        self.leave_vehicle(pl)
        self.leave_turret(pl)
        self.leave_heli(pl)
        k = self.players.get(attacker)
        if k is not None and k is not pl:
            k.kills += 1
            if wi == WI_TOMAHAWK:
                k.stats["toma_kills"] += 1
            elif wi >= MELEE_WI0:
                k.stats["melee_kills"] += 1
            elif 0 <= wi < len(WEAPONS):                 # weitester Kill-Schuss
                dist = math.hypot(pl.x - k.x, pl.y - k.y)
                if dist > k.stats["longest"]:
                    k.stats["longest"], k.stats["longest_w"] = round(dist, 1), wi
            if self.mode == "koth":                      # in der Zone zählt ein Kill doppelt
                k.score += KILL_PTS * (2.0 if k.hp > 0 and self.in_zone(k) else 1.0)
            self.events.append(("reward", k.pid))        # Munition für den Schützen
        else:
            k = None
        self.events.append(("player_dead", pl.pid))
        self.events.append(("kill", k.pid if k is not None else -1, pl.pid, wi))

    def dmg_mult(self, owner):
        """Schadens-Buff des Verursachers (Fluchttier): eigene Treffer machen BUFF_DAMAGE-fachen Schaden."""
        p = self.players.get(owner) if isinstance(owner, int) and owner >= 0 else None
        return BUFF_DAMAGE if p is not None and p.buff == "damage" and p.buff_t > 0 else 1.0

    def stun_player(self, pl, dur):
        """Betäubung (Drohne): nicht laufen, nicht schiessen, nicht steuern - Umschauen geht."""
        if pl.hp <= 0 or pl.protect > 0 or self.phase != "play":
            return
        if pl.stun_lock > 0:                             # noch betäubt oder kurz danach immun
            return
        pl.stun_t = max(pl.stun_t, dur)
        pl.stun_lock = dur + STUN_IMMUNE
        self.events.append(("stun", pl.pid, round(dur, 2)))

    def occupied_vehicle(self, pl):
        """Fahrzeug, in dem pl sitzt und das ihn vor Monstern schützt: ("car", Wagen) / ("heli", Heli) / None."""
        if pl.heli >= 0:
            hc = self.heli_by_id(pl.heli)
            if hc is not None and hc.hp > 0:
                return "heli", hc
        vid = self.own_vehicle_id(pl.pid)                # Fahrer oder Heckschütze
        if vid >= 0:
            v = self.vehicle_by_id(vid)
            if v is not None and v.hp > 0:
                return "car", v
        return None

    def mob_damage(self, pl, dmg, wi=-1):
        """Monsterschaden an einem Spieler - sitzt er im Wagen/Heli, trifft es das Fahrzeug."""
        occ = self.occupied_vehicle(pl)
        if occ is None:
            self.damage_player(pl, dmg, -1, wi)
        elif occ[0] == "car":
            self.damage_vehicle(occ[1], dmg * MOB_VEH_DMG, -1)
        else:
            self.damage_heli(occ[1], dmg * MOB_VEH_DMG, -1)

    def drone_may_target(self, m, pl):
        """DRONE_MAX_PER_TARGET: beschiessen schon genug andere Drohnen diesen Spieler?"""
        n = sum(1 for o in self.mobs if o is not m and o.kind == "drone" and o.state != "dead"
                and o.zap_pid == pl.pid and o.zap_hold > 0)
        return n < DRONE_MAX_PER_TARGET

    def drone_zap(self, m, pl):
        """Elektroschuss der Drohne: trifft bei freier Sicht und Reichweite und betäubt zufällig lang."""
        k = MOB_KINDS[m.kind]
        src = (round(m.x, 2), round(m.y, 2), round(m.z + 0.3, 2))
        if pl is None or pl.hp <= 0:
            return
        dst = (pl.x, pl.y, pl.z + 1.2)
        hit = (math.dist(src, dst) <= k["range"] * 1.15 and self.los(src, dst))
        self.events.append(("zap", src, tuple(round(c, 2) for c in dst), 1 if hit else 0))
        if hit:
            dur = self.mrng.uniform(STUN_MIN, STUN_MAX)
            occ = self.occupied_vehicle(pl)
            if occ is None:
                self.stun_player(pl, dur)
            elif pl.stun_lock <= 0:                      # im Fahrzeug: nicht der Spieler, das Fahrzeug fällt aus
                occ[1].stall_t = max(occ[1].stall_t, dur)
                pl.stun_lock = dur + STUN_IMMUNE         # gleiche Pause wie nach einer Betäubung
                self.events.append(("stall", occ[0], occ[1].id, round(dur, 2)))

    def titan_kick(self, m, pl):
        """Titan-Steinwurf: Fuss reisst einen Brocken aus dem Boden und tritt ihn in flachem Bogen auf den Spieler
        (auf dessen Position beim Abwurf - wer weiterläuft, weicht aus)."""
        a = math.radians(m.heading)
        fx, fy = -math.sin(a), math.cos(a)
        sx, sy = m.x + fx * m.radius * 1.2, m.y + fy * m.radius * 1.2
        sz = self.height(sx, sy) + 1.0
        self.events.append(("rockkick", (round(sx, 2), round(sy, 2), round(sz - 1.0, 2))))
        self.make_noise(m.x, m.y, NOISE_EXPLOSION * 0.4)
        if pl is None or pl.hp <= 0:
            return
        tx, ty, tz = pl.x, pl.y, pl.z + 1.0
        hd = math.hypot(tx - sx, ty - sy)
        T = max(0.5, hd / ROCK_SPEED)
        vx, vy = (tx - sx) / T, (ty - sy) / T
        vz = (tz - sz + 0.5 * ROCK_GRAV * T * T) / T
        self.rocks.append(Rock(self.next_rid, sx, sy, sz, vx, vy, vz, m.id))
        self.next_rid += 1

    def update_rocks(self, dt):
        """Steinbrocken fliegen; Aufprall an Gelände, Wand, Spieler oder Fahrzeug -> Flächenschaden."""
        keep = []
        rr = ROCK_SIZE * 0.5
        for r in self.rocks:
            r.life -= dt
            n = max(1, int(math.sqrt(r.vx ** 2 + r.vy ** 2 + r.vz ** 2) * dt / 0.5) + 1)
            hit = r.life <= 0
            for _ in range(n):
                if hit:
                    break
                h = dt / n
                r.vz -= ROCK_GRAV * h
                r.x += r.vx * h
                r.y += r.vy * h
                r.z += r.vz * h
                g = self.ground_for(r.x, r.y, r.z)
                if r.z - rr <= g:
                    r.z = g + rr * 0.5
                    hit = True
                elif self.in_solid(r.x, r.y, rr * 0.7, r.z):
                    hit = True
                elif any(p.hp > 0 and math.dist((r.x, r.y, r.z), (p.x, p.y, p.z + 0.9)) < rr + 0.6
                         for p in self.players.values()):
                    hit = True
                elif any(v.hp > 0 and math.dist((r.x, r.y, r.z), (v.x, v.y, v.z + 0.8)) < rr + VEH_R
                         for v in self.vehicles):
                    hit = True
            if hit:
                self.rock_impact(r)
            elif -60 < r.x < WORLD + 60 and -60 < r.y < WORLD + 60:
                keep.append(r)
        self.rocks = keep

    def rock_impact(self, r):
        pos = (round(r.x, 2), round(r.y, 2), round(r.z, 2))
        self.events.append(("rockhit", pos, ROCK_R))
        self.make_noise(r.x, r.y, NOISE_EXPLOSION * 0.5)
        self.area_damage(r.x, r.y, r.z, ROCK_R, 0.0, ROCK_DMG, WI_ROCK, cover=True)

    def titan_loot(self, m):
        """Titan erlegt: an seiner Stelle eine goldene Kiste (gleicher Inhalt wie jede goldene Kiste, Kisten-
        Gedächtnis des Öffnenden gilt). Sie wird nach dem Öffnen nicht ersetzt."""
        x, y = m.x, m.y
        for _ in range(12):                                # nicht in einer Wand
            if not self.in_solid(x, y, 0.8):
                break
            x, y = x + self.mrng.uniform(-3, 3), y + self.mrng.uniform(-3, 3)
        z = self.floor_at(x, y, m.gz + 0.5)
        c = Crate(self.next_cid, x, y, z, "gold")
        c.bonus = True
        self.next_cid += 1
        self.crates.append(c)
        self.events.append(("titanloot", c.cid, round(x, 2), round(y, 2), round(z, 2)))

    def colossus_slam(self, m):
        """Bodenschlag des Kolosses: Flächenschaden im Umkreis slam_r, im Zentrum (slam_kill) tödlich."""
        k = MOB_KINDS[m.kind]
        r = k["slam_r"]
        self.events.append(("slam", (round(m.x, 2), round(m.y, 2), round(m.gz, 2)), r))
        self.make_noise(m.x, m.y, NOISE_EXPLOSION * 0.6)
        self.area_damage(m.x, m.y, m.gz, r, k["slam_kill"], k["slam_dmg"], WI_SLAM)

    def area_damage(self, x, y, z, r, kill_r, dmg_max, wi, cover=False):
        """Flächenangriff eines Monsters (Bodenschlag, Steinbrocken): im Umkreis kill_r tödlich, bis r linear
        weniger. Fahrzeuge im Umkreis nehmen den Schaden; ihre Insassen sind geschützt, bis es zerstört ist."""
        def amount(d):
            return 9999.0 if d < kill_r else dmg_max * (1.0 - (d - kill_r) / max(r - kill_r, 0.01))
        inside = {pl.pid for pl in self.players.values() if self.occupied_vehicle(pl) is not None}
        src = (x, y, z + 0.8)

        def covered(p):                                  # Deckung: Wand zwischen Aufprall und Ziel
            return cover and not self.los(src, p)
        for v in self.vehicles:
            if v.hp > 0 and abs(v.z - z) < 3.0:
                d = max(0.0, math.hypot(v.x - x, v.y - y) - VEH_R * 0.6)
                if d <= r and not covered((v.x, v.y, v.z + 1.0)):
                    self.damage_vehicle(v, min(amount(d), VEH_HP * 1.5) * MOB_VEH_DMG, -1)
        for hc in self.helis:
            if hc.hp > 0 and hc.z - z < 2.5:              # nur am Boden / ganz tief
                d = max(0.0, math.hypot(hc.x - x, hc.y - y) - HELI_R * 0.5)
                if d <= r:
                    self.damage_heli(hc, min(amount(d), HELI_HP * 0.5) * MOB_VEH_DMG, -1)
        for pl in list(self.players.values()):
            if pl.hp <= 0 or abs(pl.z - z) > 2.5 or pl.heli >= 0 or pl.pid in inside:
                continue
            d = math.hypot(pl.x - x, pl.y - y) if not cover else math.dist((pl.x, pl.y, pl.z + 0.9), (x, y, z))
            if d <= r and not covered((pl.x, pl.y, pl.z + 1.0)):
                self.damage_player(pl, amount(d), -1, wi)

    def give_buff(self, pl):
        """Fluchttier erlegt: ein zufälliger Buff (Tempo, Schaden, Tank)."""
        if pl is None or pl.hp <= 0:
            return
        self.end_buff(pl)
        kind = self.mrng.choice(BUFF_KINDS)
        pl.buff, pl.buff_t = kind, BUFF_T[kind]
        if kind == "tank":
            mx = self.mrng.choice(BUFF_TANK_HP)
            pl.hp = pl.hp * mx / pl.max_hp               # Leben mitskalieren (80/100 -> 160/200)
            pl.max_hp = mx
        pl.stats["buffs"] += 1
        self.events.append(("buff", pl.pid, kind, BUFF_T[kind], pl.max_hp))

    def end_buff(self, pl):
        if pl.buff == "tank" and pl.max_hp != PLAYER_HP:
            if pl.hp > 0:
                pl.hp = max(1.0, pl.hp * PLAYER_HP / pl.max_hp)   # prozentual zurück: 180/200 -> 90/100
            pl.max_hp = PLAYER_HP
        pl.buff, pl.buff_t = None, 0.0

    def hit_player(self, pl, dmg, pos, d, head, owner, wi):
        dmg *= self.dmg_mult(owner)
        pct = round(min(dmg, max(pl.hp, 0.0)) / PLAYER_HP * 100.0)
        self.events.append(("pl_hit", pos, d, dmg, head, owner, pct))
        self.damage_player(pl, dmg, owner, wi, head)

    def note_hit(self, owner, head, target_pos=None, wi=-1, kill=False):
        """Statistik des Schützen: Treffer, Kopfschüsse, weitester Kill-Schuss (mit Waffe)."""
        p = self.players.get(owner) if isinstance(owner, int) else None
        if p is None:
            return
        p.stats["hits"] += 1
        if head:
            p.stats["heads"] += 1
        if kill and target_pos is not None and 0 <= wi < len(WEAPONS):
            dist = math.hypot(target_pos[0] - p.x, target_pos[1] - p.y)
            if dist > p.stats["longest"]:
                p.stats["longest"], p.stats["longest_w"] = round(dist, 1), wi

    def hurt_mob(self, m, dmg, pos, d, head, owner=0, wi=-1):
        dmg *= self.dmg_mult(owner)
        pct = round(min(dmg, max(m.hp, 0.0)) / m.max_hp * 100.0)
        m.hp -= dmg
        m.hurt_t = 0.15
        m.alert_t = 10.0
        sh = self.players.get(owner)
        m.on_shot(self, d, True, (sh.x, sh.y) if sh is not None else None)   # reagiert immer: Richtung Schütze
        imp = dmg * 0.03 / m.scale                       # Knockback in Schussrichtung
        m.kx = clampf(m.kx + d[0] * imp, -6, 6)
        m.ky = clampf(m.ky + d[1] * imp, -6, 6)
        self.events.append(("mob_hit", pos, d, dmg, head, owner, pct))
        if m.hp <= 0 and m.state != "dead":
            m.state, m.dead_t = "dead", 0.0
            self.kills += 1
            self.events.append(("mob_kill", (m.x, m.y, m.z + m.height * 0.5), owner))
            self.events.append(("reward", owner))        # Munition für den Schützen
            killer = self.players.get(owner)
            if killer is not None:
                killer.stats["mob"][m.kind] = killer.stats["mob"].get(m.kind, 0) + 1
                if 0 <= wi < len(WEAPONS):
                    self.note_hit(owner, False, (m.x, m.y), wi, True)
                    killer.stats["hits"] -= 1                # (der Treffer wurde schon gezählt)
                elif wi >= MELEE_WI0:
                    killer.stats["melee_kills"] += 1
            if not m.aggressive():                       # Fluchttier erlegt: Buff für den Schützen
                self.give_buff(self.players.get(owner))
            if m.kind == "titan":                        # Boss erlegt: goldene Kiste an seiner Stelle
                self.titan_loot(m)

    def explode(self, pos, owner, r, dmg, wi):
        """Flächenschaden: linear abfallend, gegen sich selbst nur halb.
        Eine Rakete zerstört ein Fahrzeug in ROCKET_KILL_R Umkreis sofort."""
        self.events.append(("explosion", tuple(round(c, 2) for c in pos), r, owner))
        self.make_noise(pos[0], pos[1], NOISE_EXPLOSION)
        for v in list(self.vehicles):
            if v.hp <= 0:
                continue
            d = math.dist(pos, (v.x, v.y, v.z + 0.8))
            if wi == ROCKET_WI and d < ROCKET_KILL_R:
                self.destroy_vehicle(v, owner)
            elif d < r + VEH_R:
                self.damage_vehicle(v, dmg * (1.0 - d / (r + VEH_R)), owner)
        for hc in list(self.helis):
            if hc.hp <= 0 or (owner >= 0 and hc.driver == owner):     # eigener Helikopter bleibt heil
                continue
            d = math.dist(pos, (hc.x, hc.y, hc.z + 1.2))
            if wi == ROCKET_WI and d < HELI_R + HELI_ROCKET_KILL_R:
                self.destroy_heli(hc, owner)                           # Rakete: ein Treffer genügt
            elif d < r + HELI_R:
                f = 1.0 - d / (r + HELI_R)
                self.damage_heli(hc, dmg * f * (1.0 if wi == WI_FLAK else HELI_K), owner)
        for pl in list(self.players.values()):
            if pl.hp <= 0 or pl.protect > 0 or pl.heli >= 0:
                continue
            d = math.dist(pos, (pl.x, pl.y, pl.z + 0.9))
            if pl.pid == owner and pl.mount >= 0:      # Schütze am Geschütz bleibt unversehrt
                continue
            if wi == WI_GRENADE and d < GREN_KILL_R:   # sofort tot
                self.damage_player(pl, 9999.0, owner, wi)
            elif d < r:
                f = 1.0 - d / r
                if pl.pid == owner:
                    f *= 0.5
                self.damage_player(pl, dmg * f * self.dmg_mult(owner), owner, wi)
        for m in self.mobs:
            if m.state == "dead":
                continue
            mp = (m.x, m.y, m.z + m.height * 0.5)
            d = math.dist(pos, mp)
            if d < r + m.radius:
                f = max(0.0, 1.0 - d / (r + m.radius))
                if wi == WI_GRENADE and d < GREN_KILL_R + m.radius:
                    f = 9999.0 / max(dmg, 1.0)
                dx, dy = m.x - pos[0], m.y - pos[1]
                l = math.hypot(dx, dy) or 1.0
                self.hurt_mob(m, dmg * f, mp, (dx / l, dy / l, 0.3), False, owner)

    # ------------------------------------------------------------ Loot
    def crate_counts(self):
        """So viele Kisten je Art sollen gleichzeitig auf der Karte liegen."""
        return CRATES_STD if self.mtn else CRATES_MAP

    def crate_target(self):
        return sum(self.crate_counts().values())

    def reset_crates(self):
        """Rundenstart: alle Kisten neu und zufällig verteilen (Anzahl je Art: CRATES_STD / CRATES_MAP).
        Die wertvollsten zuerst, damit sie sicher einen Platz bekommen."""
        self.crates = []
        self.crate_wait = []
        cnt = self.crate_counts()
        kinds = [k for k in reversed(CRATE_KINDS) for _ in range(int(cnt.get(k, 0)))]
        for k in kinds:
            if self.spawn_crate(k) is None:
                self.crate_wait.append([1.0, k, -999.0, -999.0])     # kein Platz gefunden: gleich nochmal

    def spawn_crate(self, kind, avoid=(), mid_round=False):
        """Neue Kiste an einer zufälligen gültigen Stelle. avoid: [(x, y, Abstand)].
        mid_round: nicht direkt neben einem lebenden Spieler auftauchen lassen."""
        rng = self.mrng
        for attempt in range(120):
            p = self.crate_spot(rng)
            if p is None:
                continue
            x, y, z = p
            gap = CRATE_GAP if attempt < 80 else CRATE_GAP * 0.5      # notfalls etwas dichter
            if any(math.hypot(x - c.x, y - c.y) < gap for c in self.crates):
                continue
            if kind == "gold" and attempt < 100:          # goldene Kisten über die ganze Karte verteilen
                gg = CRATE_GOLD_GAP * WORLD / STD_WORLD
                if any(c.kind == "gold" and math.hypot(x - c.x, y - c.y) < gg for c in self.crates):
                    continue
            if any(math.hypot(x - ax, y - ay) < ad for ax, ay, ad in avoid):
                continue
            if mid_round and any(q.hp > 0 and math.hypot(x - q.x, y - q.y) < CRATE_PLAYER_GAP
                                 for q in self.players.values()):
                continue
            c = Crate(self.next_cid, x, y, z, kind)
            self.next_cid += 1
            self.crates.append(c)
            return c
        return None

    def crate_spot(self, rng):
        """Zufällige gültige Kistenstelle (x, y, z) oder None (dann nochmal würfeln)."""
        if self.mc:
            return self.mc_crate_spot(rng)
        r = rng.random()
        if r < CRATE_SPOT_SHARE:                                  # an einem Bauwerk:
            if self.crate_spots and rng.random() < 0.5:
                return rng.choice(self.crate_spots)               # fest vorgesehene Plätze (Turm, Heuboden ...)
            return self.wall_crate_spot(rng)                      # oder an einer Mauer, Wand, Deckung
        if r < CRATE_SPOT_SHARE + CRATE_TUNNEL_SHARE and self.tunnels:
            x0, y0, x1, y1 = rng.choices(self.tunnels, weights=[(c - a) * (d - b) for a, b, c, d in self.tunnels])[0]
            x = rng.uniform(x0 + 0.7, x1 - 0.7) if x1 - x0 > 1.4 else (x0 + x1) / 2
            y = rng.uniform(y0 + 0.7, y1 - 0.7) if y1 - y0 > 1.4 else (y0 + y1) / 2
            z = self.floor_at(x, y, TUN_Z + 0.1)
            if self.in_void(x, y, 1.0) or self.in_solid(x, y, 0.6, z):
                return None
            return (x, y, z)
        return self.ground_crate_spot(rng)

    def wall_crate_spot(self, rng):
        """Direkt neben einer Wand oder Deckung (drinnen oder draussen) auf dem Boden."""
        b = rng.choice(self.boxes) if self.boxes else None
        if b is None or b.z1 - max(b.z0, 0.0) < 0.9 or b.z0 > 2.5 or b.z1 < 0.8:
            return None                                           # Böden, Dächer, Tunnelteile: nein
        off = rng.choice((-0.95, 0.95))
        if rng.random() < 0.5:
            x, y = rng.uniform(b.x0, b.x1), (b.y0 - 0.95 if off < 0 else b.y1 + 0.95)
        else:
            x, y = (b.x0 - 0.95 if off < 0 else b.x1 + 0.95), rng.uniform(b.y0, b.y1)
        p = self.ground_crate_spot(rng, x, y)
        if p is not None and p[2] > self.height(x, y) + 0.7:      # nicht oben auf etwas anderem
            return None
        return p

    def ground_crate_spot(self, rng, x=None, y=None):
        """Freies Gelände: nicht im Wasser, nicht in Wänden, Bäumen oder Felsen, nicht am steilen Hang."""
        if x is None:
            x, y = rng.uniform(8, WORLD - 8), rng.uniform(8, WORLD - 8)
        if not (8 < x < WORLD - 8 and 8 < y < WORLD - 8):
            return None
        if self.mtn and mountain(x, y) > 1.0:                     # nicht im Gebirge
            return None
        h = self.height(x, y)
        if h < WATER_LEVEL + 0.6 or terrain_slope(self, x, y) > 0.5 or self.in_void(x, y, 1.0):
            return None
        if any(math.hypot(x - px, y - py) < r * 1.8 for px, py, r in self.ponds):
            return None
        if any(math.hypot(x - p.x, y - p.y) < p.solid_r + 1.0 for p in self.props):
            return None
        if self.in_solid(x, y, 0.6):
            return None
        return (x, y, self.floor_at(x, y, h))

    def mc_crate_spot(self, rng):
        """Minecraft-Karte: in der Nähe eines Startpunkts auf derselben Ebene (kein Dach, kein Loch, kein Wasser)."""
        if not self.spawns:
            return None
        sx, sy = rng.choice(self.spawns)
        sz = self.spawn_z(sx, sy)
        a, r = rng.uniform(0.0, 2.0 * math.pi), rng.uniform(0.0, 7.0)
        x, y = sx + math.cos(a) * r, sy + math.sin(a) * r
        if not (2.0 < x < WORLD - 2.0 and 2.0 < y < WORLD - 2.0):
            return None
        z = self.floor_at(x, y, sz + 0.3)
        if abs(z - sz) > 1.2 or self.in_solid(x, y, 0.5, z) or self.ceiling_at(x, y, z) < z + 2.0:
            return None
        return (x, y, z)

    def update_crates(self, dt):
        """Geöffnete Kisten tauchen nach CRATE_RESPAWN an einer anderen Stelle wieder auf."""
        for e in self.crate_wait[:]:
            e[0] -= dt
            if e[0] > 0:
                continue
            if self.spawn_crate(e[1], ((e[2], e[3], CRATE_REUSE_GAP),), True) is not None:
                self.crate_wait.remove(e)
            else:
                e[0] = 1.0                                       # gerade kein Platz frei: gleich nochmal

    def use_crate(self, pl, c):
        """Kiste öffnen: Inhalt würfeln, Kiste verschwindet, später taucht woanders eine neue auf."""
        if c not in self.crates:
            return
        for _ in range(20):
            art, name = roll_loot(c.kind, self.mrng, pl.slots, pl.loot_history, pl.last_loot, worn_names(pl))
            if art == "weapon" and name in WEAPON_IDX and WEAPON_IDX[name] != START_WEAPON:
                break
            if art == "gear" and name in GEAR_IDX:
                break
            if art == "melee" and name in MELEE_IDX:
                break
        else:
            return
        if LOOT_DEBUG:
            self.loot_debug(pl, c.kind)                   # Chancen VOR dem Zug (so wurde gerade gewürfelt)
        remember_loot(pl, name)
        pl.stats["crate"][c.kind] = pl.stats["crate"].get(c.kind, 0) + 1
        self.crates.remove(c)
        if not c.bonus:                                  # Titan-Kiste wird nicht ersetzt
            self.crate_wait.append([CRATE_RESPAWN.get(c.kind, 25.0), c.kind, c.x, c.y])
        if art == "gear":
            self.give_gear(pl, GEAR_IDX[name], CRATE_KINDS.index(c.kind))
        elif art == "melee":
            self.give_melee(pl, MELEE_IDX[name], CRATE_KINDS.index(c.kind))
        else:
            self.give_weapon(pl, WEAPON_IDX[name], "loot", CRATE_KINDS.index(c.kind))

    def give_gear(self, pl, gi, crate=-1):
        """Ausrüstung anlegen. Gleiches Teil schon getragen: blockiert (sonst liessen sich Treibstoff/Abklingzeiten
        durch Tauschen zurücksetzen). Anderes Teil im Slot: wird getauscht, das alte fällt auf den Boden.
        -> True, wenn angelegt."""
        g = GEAR[gi]
        if pl.gear.get(g.slot) == gi:
            self.events.append(("hasgear", pl.pid, gi))
            return False
        old = pl.gear.get(g.slot)
        if old is not None:
            self.add_drop(pl.x, pl.y, pl.z, -1, old)
        pl.gear[g.slot] = gi
        if g.kind == "shield" and old != gi:
            pl.shield_t = 0.0                            # Schildstand gehört dem Spieler (kein Zurücksetzen)
        self.events.append(("gear", pl.pid, gi, gear_list(pl), crate))
        return True

    def loot_debug(self, pl, kind):
        """LOOT_DEBUG: aktuelle Chancen des Spielers je Kistenart ins Log und als Hinweis an ihn."""
        short = {"Schrotflinte": "SG", "Maschinenpistole": "MP", "Sturmgewehr": "AR", "Revolver": "Rev",
                 "Minigun": "Mini", "Railgun": "Rail", "Raketenwerfer": "RPG", "Scharfschütze": "Sniper"}
        lines = []
        for k in CRATE_KINDS:
            ch = loot_chances(k, pl.slots, pl.loot_history, pl.last_loot)
            ch.update({f"[{n}]": v for n, v in loot_chances(k, (), pl.loot_history, pl.last_loot, "gear",
                                                             worn_names(pl)).items()})
            parts = "  ".join(f"{short.get(n, n)} {ch[n] * 100:.0f}" if ch[n] >= 0.095 else f"{short.get(n, n)} {ch[n] * 100:.1f}" for n in sorted(ch, key=lambda n: -ch[n]))
            lines.append(f"{'>' if k == kind else ' '}{k}: {parts}")
        txt = f"Chancen {pl.name} (gezogen: {dict(pl.loot_history) or '-'}):\n" + "\n".join(lines)
        try:
            with open(_log_path(), "a", encoding="utf-8") as f:
                f.write(time.strftime("%H:%M:%S ") + txt + "\n")
        except OSError:
            pass
        self.events.append(("lootdbg", pl.pid, txt))

    def give_weapon(self, pl, wi, how, extra=0):
        """Host/Einzelspiel: Waffe ins Inventar legen; eine verdrängte Waffe fällt auf den Boden.
        Das Ereignis trägt die neue Slot-Belegung, der Mitspieler übernimmt sie genau so."""
        out, dup = take_weapon(pl, wi)
        if out is not None:
            self.add_drop(pl.x, pl.y, pl.z, out)
        self.events.append((how, pl.pid, wi, list(pl.slots), 1 if dup else 0, extra))

    def nearest_use(self, pl):
        """Was würde F jetzt tun? -> (Art, Objekt) oder None.
        Art: crate | drop | vehicle | turret | heli | exit | exit_turret | exit_heli | button | timer."""
        if pl.mount >= 0:
            return ("exit_turret", self.turrets[pl.mount]) if pl.mount < len(self.turrets) else None
        if pl.heli >= 0:
            hc = self.heli_by_id(pl.heli)
            return ("exit_heli", hc) if hc is not None else None
        if pl.vehicle >= 0:
            v = self.vehicle_by_id(pl.vehicle)
            return ("exit", v) if v is not None else None
        best, bs = None, 1.0
        vehs = []
        for v in self.vehicles:
            if v.hp > 0:
                t = self.car_turret(v)
                if v.driver < 0 or (t is not None and t.op < 0):
                    vehs.append(v)
        for kind, objs, rng in (("crate", self.crates, 3.2),
                                ("drop", self.drops, 2.6),
                                ("vehicle", vehs, 3.6),
                                ("heli", [q for q in self.helis if q.hp > 0 and q.driver < 0 and q.ground], 6.0),
                                ("turret", [t for t in self.turrets if t.kind != "car" and t.op < 0], 2.3)):
            for o in objs:
                d = math.hypot(pl.x - o.x, pl.y - o.y) / rng
                oz = o.z - o.seat if kind == "turret" else o.z
                if d < bs and abs(pl.z - oz) < 2.5:
                    best, bs = (kind, o), d
        if self.strike != 1 and self.phase == "play":
            for kind, b in (("button", self.button),):
                d = math.hypot(pl.x - b.x, pl.y - b.y) / 2.4
                if d < bs and abs(pl.z - b.z) < 2.5:
                    best, bs = (kind, b), d
        return best

    def use_object(self, pl, alt=False):
        """F gedrückt (alt = V): Kiste, Waffe, Fahrzeug (Fahrer/Schütze), Geschütz, Helikopter, Knöpfe."""
        if pl.hp <= 0 or self.phase != "play":
            return
        if alt:                                          # V: Schützensitz auf dem Wagen
            if pl.mount >= 0 or pl.heli >= 0 or pl.vehicle >= 0:
                return
            for v in self.vehicles:
                t = self.car_turret(v)
                if (v.hp > 0 and t is not None and t.op < 0 and abs(pl.z - v.z) < 2.5
                        and math.hypot(pl.x - v.x, pl.y - v.y) < 3.6):
                    self.sync_turret_pos()
                    self.mount_turret(pl, t)
                    return
            return
        r = self.nearest_use(pl)
        if r is None:
            return
        kind, o = r
        if kind == "crate":
            self.use_crate(pl, o)
        elif kind == "drop":
            self.pickup_drop(pl, o)
        elif kind == "button":
            self.press_button(pl)
        elif kind == "turret":
            self.mount_turret(pl, o)
        elif kind == "exit_turret":
            self.leave_turret(pl, True)
        elif kind == "heli":
            o.driver, o.speed, o.vx, o.vy, o.vz = pl.pid, 0.0, 0.0, 0.0, 0.0
            pl.heli, pl.ads, pl.trig = o.id, False, False
            pl.stats["flights"] += 1
            self.events.append(("henter", pl.pid, o.id))
        elif kind == "exit_heli":
            if o.ground and o.speed < 4.0:
                self.leave_heli(pl, True)
        elif kind == "vehicle":
            if o.driver < 0:
                o.driver, o.speed = pl.pid, 0.0
                pl.vehicle, pl.ads = o.id, False
                pl.stats["drives"] += 1
                self.events.append(("venter", pl.pid, o.id))
            else:
                t = self.car_turret(o)
                if t is not None and t.op < 0:
                    self.sync_turret_pos()
                    self.mount_turret(pl, t)
        else:
            self.leave_vehicle(pl, True)

    # ------------------------------------------------------------ Waffen am Boden
    def melee_swing(self, pl, d):
        """Nahkampf-Schlag von pl in Richtung d. Mitspieler schicken ihn an den Host (melee_sink)."""
        if self.melee_sink is not None:
            self.melee_sink(pl, d)
            return
        self.melee_hit(pl, d)

    def melee_hit(self, pl, d):
        """Host/Einzelspiel: trifft den nächsten Gegner (Monster oder Spieler) in Reichweite und Schlagwinkel.
        Sehr leise (NOISE_MELEE). Ahnungslose Monster nehmen MELEE_SNEAK-fachen Schaden."""
        if pl.hp <= 0 or self.phase != "play":
            return
        mi = pl.melee if 0 <= pl.melee < len(MELEE) else START_MELEE
        m = MELEE[mi]
        pl.protect = 0.0
        self.events.append(("mswing", pl.pid, mi))
        self.make_noise(pl.x, pl.y, NOISE_MELEE)
        eye = (pl.x, pl.y, pl.z + eye_h(pl))
        hl = math.hypot(d[0], d[1]) or 1.0
        fx, fy = d[0] / hl, d[1] / hl
        cos_arc = math.cos(math.radians(m.arc))
        best = None
        cands = [(mob, mob.radius, mob.z, mob.z + mob.height) for mob in self.mobs if mob.state != "dead"]
        cands += [(q, PLAYER_R, q.z, q.z + body_h(q)) for q in self.players.values()
                  if q is not pl and q.hp > 0 and q.protect <= 0 and q.vehicle < 0 and q.heli < 0]
        for t, rad, z0, z1 in cands:
            dx, dy = t.x - pl.x, t.y - pl.y
            dist = math.hypot(dx, dy)
            if dist - rad > m.reach or eye[2] < z0 - m.reach or eye[2] > z1 + m.reach:
                continue
            if dist > 0.05 and (dx * fx + dy * fy) / dist < cos_arc and dist > rad + 0.3:
                continue
            if not self.los(eye, (t.x, t.y, min(max(eye[2], z0 + 0.3), z1 - 0.1))):
                continue
            if best is None or dist < best[1]:
                best = (t, dist, rad, z0, z1)
        if best is None:
            return
        t, dist, rad, z0, z1 = best
        az = eye[2] + d[2] * max(0.0, dist - rad * 0.5)             # Höhe, auf die gezielt wurde
        hz = clampf(az, z0 + 0.1, z1 - 0.05)
        head = hz > z0 + 0.78 * (z1 - z0)
        dmg = m.dmg * (m.head if head else 1.0)
        pos = (t.x - fx * rad * 0.8, t.y - fy * rad * 0.8, hz)
        wi = MELEE_WI0 + mi
        snd = m.sound if (m.sound != "bong" or head) else "slash"
        self.events.append(("mhit", tuple(round(c, 2) for c in pos), snd, pl.pid))
        if isinstance(t, Mob):
            if t.aggressive() and t.state == "idle" and t.noise_at is None:
                dmg *= MELEE_SNEAK                        # von hinten / ahnungslos: leise erledigen
            self.note_hit(pl.pid, head)
            self.hurt_mob(t, dmg, pos, (fx, fy, 0.0), head, pl.pid, wi)
        else:
            self.note_hit(pl.pid, head)
            self.hit_player(t, dmg, pos, (fx, fy, 0.0), head, pl.pid, wi)

    def give_melee(self, pl, mi, crate=-1):
        """Neue Nahkampfwaffe: ersetzt die alte (fällt als Drop, ausser dem Start-Messer). Gleiche Waffe:
        Aufnehmen blockiert. -> True, wenn genommen."""
        if pl.melee == mi:
            self.events.append(("hasmelee", pl.pid, mi))
            return False
        if pl.melee != START_MELEE:
            self.add_drop(pl.x, pl.y, pl.z, -1, -1, pl.melee)
        pl.melee = mi
        self.events.append(("melee", pl.pid, mi, crate))
        return True

    def add_drop(self, x, y, z, wi, gear=-1, melee=-1):
        while len(self.drops) >= MAX_DROPS:
            self.drops.pop(0)
        d = Drop(self.next_did, x, y, max(z, self.ground_for(x, y, z + 0.3)), wi, gear, melee)
        self.next_did += 1
        self.drops.append(d)
        return d

    def pickup_drop(self, pl, d):
        """Waffe vom Boden aufheben (gleiche Slot-Regeln wie bei Kisten, siehe take_weapon)."""
        if d not in self.drops:
            return
        if d.gear >= 0:                                  # Ausrüstung: identisches Teil -> bleibt liegen
            if self.give_gear(pl, d.gear):
                self.drops.remove(d)
            return
        if d.melee >= 0:                                 # Nahkampfwaffe: gleiche -> bleibt liegen
            self.drops.remove(d)
            if not self.give_melee(pl, d.melee):
                self.drops.append(d)
            return
        self.drops.remove(d)
        self.give_weapon(pl, d.wi, "pickup")

    # ------------------------------------------------------------ Fahrzeuge
    def damage_vehicle(self, v, dmg, attacker):
        if v.hp <= 0 or dmg <= 0:
            return
        v.hp -= dmg
        if v.hp <= 0:
            self.destroy_vehicle(v, attacker)

    def destroy_vehicle(self, v, attacker):
        if v.hp <= 0 and v.dead_t > 0:
            return
        v.hp, v.dead_t, v.speed = 0.0, 0.001, 0.0
        drv = self.players.get(v.driver)
        v.driver = -1
        if drv is not None:
            drv.vehicle = -1
        self.explode((v.x, v.y, v.z + 0.8), attacker, VEH_BLAST_R, VEH_BLAST_DMG, WI_VEHICLE)
        self.events.append(("vboom", v.id))

    def leave_vehicle(self, pl, announce=False):
        """Spieler verlässt sein Fahrzeug (F, Tod): Fahrer wird neben das Auto gesetzt."""
        v = self.vehicle_by_id(pl.vehicle) if pl.vehicle >= 0 else None
        pl.vehicle = -1
        if v is None:
            return
        if v.driver == pl.pid:
            v.driver = -1
        a = math.radians(v.heading)
        for side in (1.0, -1.0):
            x, y = v.x + math.cos(a) * 2.4 * side, v.y + math.sin(a) * 2.4 * side
            if not self.in_solid(x, y, PLAYER_R + 0.2, v.z) and not self.in_void(x, y, 0.5):
                break
        pl.x, pl.y = push_out(x, y, PLAYER_R, self, v.z)
        pl.z, pl.vz = self.floor_at(pl.x, pl.y, v.z + 0.5), 0.0
        if announce:
            self.events.append(("vexit", pl.pid, round(pl.x, 2), round(pl.y, 2), round(pl.z, 2)))

    def update_vehicles(self, dt):
        for v in self.vehicles:
            if v.hp <= 0:                                # Wrack, nach einer Weile steht ein neues da
                v.dead_t += dt
                if v.dead_t > VEH_RESPAWN:
                    v.reset()
                    self.events.append(("vreset", v.id))
                continue
            v.stall_t = max(0.0, v.stall_t - dt)
            drv = self.players.get(v.driver)
            if v.driver >= 0 and (drv is None or drv.hp <= 0 or drv.vehicle != v.id):
                v.driver = -1
            if v.driver < 0:
                v.speed = 0.0
                continue
            if abs(v.speed) > 5.0:                       # Überfahren
                for pl in self.players.values():
                    if (pl.pid == v.driver or pl.hp <= 0 or pl.vehicle >= 0
                            or self.runover.get(pl.pid, 0.0) > 0 or abs(pl.z - v.z) > 2.0
                            or math.hypot(pl.x - v.x, pl.y - v.y) > VEH_R + 0.7):
                        continue
                    self.runover[pl.pid] = 0.8
                    self.damage_player(pl, min(100.0, abs(v.speed) * 9.0), v.driver, WI_VEHICLE)
                for m in self.mobs:
                    if (m.state != "dead" and self.runover.get(-m.id, 0.0) <= 0
                            and math.hypot(m.x - v.x, m.y - v.y) < VEH_R + m.radius + 0.3):
                        self.runover[-m.id] = 0.8
                        self.hurt_mob(m, min(150.0, abs(v.speed) * 12.0),
                                      (m.x, m.y, m.z + 1.0), (-math.sin(math.radians(v.heading)),
                                                              math.cos(math.radians(v.heading)), 0.3),
                                      False, v.driver)
        for k in list(self.runover):
            self.runover[k] -= dt
            if self.runover[k] <= 0:
                del self.runover[k]

    # ------------------------------------------------------------ Geschütze (von Spielern bedient)
    def los(self, p0, p1):
        """Freie Sichtlinie (keine Quader, keine Bäume/Felsen dazwischen)?"""
        for b in self.boxes_near(p0[0], p0[1], p1[0], p1[1]):
            if seg_box(p0, p1, b) is not None:
                return False
        for q in self.props_near(p0[0], p0[1], p1[0], p1[1]):
            if q.hit_r > 0 and seg_cyl(p0, p1, q.x, q.y, q.hit_r, q.z - 0.3, q.z + q.hit_h) is not None:
                return False
        return True

    def sync_turret_pos(self):
        """Das Geschütz auf dem Wagen fährt mit."""
        for t in self.turrets:
            if t.kind == "car":
                v = self.vehicle_by_id(t.vid)
                if v is not None:
                    h = math.radians(v.heading)
                    t.x, t.y, t.z = v.x + math.sin(h) * 0.9, v.y - math.cos(h) * 0.9, v.z + 1.75

    def car_turret(self, v):
        return next((t for t in self.turrets if t.kind == "car" and t.vid == v.id), None)

    def mount_turret(self, pl, t):
        t.op, pl.mount, pl.ads = pl.pid, t.id, False
        pl.x, pl.y, pl.z = t.x, t.y, t.z - t.seat
        pl.heading, pl.pitch = t.heading, clampf(t.pitch, t.pmin, t.pmax)
        pl.lean = pl.lean_x = pl.lean_y = 0.0
        pl.duck, pl.crouch = False, 0.0
        self.events.append(("tmount", pl.pid, t.id))

    def leave_turret(self, pl, announce=False):
        if pl.mount < 0 or pl.mount >= len(self.turrets):
            pl.mount = -1
            return
        t = self.turrets[pl.mount]
        if t.op == pl.pid:
            t.op = -1
        pl.mount, pl.trig = -1, False
        if t.kind == "car":
            v = self.vehicle_by_id(t.vid)
            if v is not None:
                a = math.radians(v.heading)
                for side in (1.0, -1.0):
                    x, y = v.x + math.cos(a) * 2.4 * side, v.y + math.sin(a) * 2.4 * side
                    if not self.in_solid(x, y, PLAYER_R + 0.2, v.z) and not self.in_void(x, y, 0.5):
                        break
                pl.x, pl.y = push_out(x, y, PLAYER_R, self, v.z)
                pl.z, pl.vz = self.floor_at(pl.x, pl.y, v.z + 0.5), 0.0
        else:
            pl.z = self.floor_at(pl.x, pl.y, pl.z + 0.3)
        if announce:
            self.events.append(("vexit", pl.pid, round(pl.x, 2), round(pl.y, 2), round(pl.z, 2)))

    def update_turrets(self, dt):
        """Geschütze feuern nur, wenn ein Spieler sie bedient (Maus zielt, Linke Maustaste schiesst).
        Munition ist unbegrenzt, aber die Rohre heizen sich auf: bei 100 % Zwangspause."""
        self.sync_turret_pos()
        play = self.phase == "play"
        for t in self.turrets:
            op = self.players.get(t.op) if t.op >= 0 else None
            v = self.vehicle_by_id(t.vid) if t.kind == "car" else None
            if t.op >= 0 and (op is None or op.hp <= 0 or not play
                              or (t.kind == "car" and (v is None or v.hp <= 0))):
                if op is not None:
                    op.mount, op.trig = -1, False
                t.op, op = -1, None
            was, t.firing = t.firing, False
            t.noise_t = getattr(t, "noise_t", 0.0) - dt
            if t.over:
                t.heat = max(0.0, t.heat - TUR_COOL_OVER * dt)
                if t.heat <= TUR_RESUME:
                    t.over = False
            elif not was:
                t.heat = max(0.0, t.heat - TUR_COOL * dt)
            t.cd = max(0.0, t.cd - dt)
            if op is None:
                continue
            op.mount = t.id
            op.x, op.y, op.z = t.x, t.y, t.z - t.seat
            op.pitch = clampf(op.pitch, t.pmin, t.pmax)
            t.heading, t.pitch = op.heading % 360.0, op.pitch
            if not op.trig or t.over or t.cd > 0 or not play:
                continue
            flak = t.kind == "flak"
            t.firing = True
            if getattr(t, "noise_t", 0.0) <= 0:            # Geschütz feuert: laut (alle 0,5 s gemeldet)
                self.make_noise(t.x, t.y, NOISE_SHOT * 1.2)
                t.noise_t = 0.5
            t.cd = FLAK_INTERVAL if flak else TUR_INTERVAL
            t.heat += FLAK_HEAT if flak else TUR_HEAT_SHOT
            if t.heat >= 1.0:
                t.heat, t.over = 1.0, True
            op.protect = 0.0
            sp = math.radians(0.5 if flak else TUR_SPREAD * 0.7)
            h = math.radians(t.heading) + self.mrng.uniform(-sp, sp)
            p = math.radians(t.pitch) + self.mrng.uniform(-sp, sp)
            d = (-math.sin(h) * math.cos(p), math.cos(h) * math.cos(p), math.sin(p))
            spd = FLAK_SPEED if flak else TUR_SPEED
            b = Bullet(t.x + d[0] * 1.2, t.y + d[1] * 1.2, t.z + d[2] * 1.2,
                       d[0] * spd, d[1] * spd, d[2] * spd, TUR_DMG, op.pid, self.next_bid,
                       WI_FLAK if flak else WI_TURRET)
            if flak:
                b.blast_r, b.blast_dmg, b.life = FLAK_R, FLAK_DMG, FLAK_LIFE
            self.bullets.append(b)
            self.next_bid += 1
            self.events.append(("tshot", t.id))

    # ------------------------------------------------------------ Helikopter
    def heli_by_id(self, hid):
        return next((h for h in self.helis if h.id == hid), None)

    def on_pad(self, x, y):
        return any(math.hypot(x - px, y - py) <= HELI_PAD_R for px, py in self.pads)

    def heli_crash(self, h, impact):
        """Aufprall eines (von einer Drohne) lahmgelegten Helis: Schaden je m/s über HELI_CRASH_V. Nur kurz nach
        dem Lahmlegen (der Pilot meldet den Aufprall, der Host prüft)."""
        if h.stall_t <= -1.0 + 1e-6:
            return
        impact = min(float(impact), HELI_STALL_SINK + 2.0)
        if impact > HELI_CRASH_V:
            self.damage_heli(h, (impact - HELI_CRASH_V) * HELI_CRASH_DMG, -1)
            self.events.append(("hcrash", h.id, round(impact, 1)))

    def damage_heli(self, h, dmg, attacker):
        if h.hp <= 0 or dmg <= 0:
            return
        h.hp -= dmg
        if h.hp <= 0:
            self.destroy_heli(h, attacker)

    def destroy_heli(self, h, attacker):
        if h.hp <= 0 and h.dead_t > 0:
            return
        h.hp, h.dead_t, h.speed, h.vx, h.vy, h.vz, h.firing = 0.0, 0.001, 0.0, 0.0, 0.0, 0.0, False
        drv = self.players.get(h.driver)
        h.driver = -1
        if drv is not None:
            drv.heli, drv.protect, drv.trig = -1, 0.0, False
            self.damage_player(drv, 9999.0, attacker, WI_HELI)
        self.explode((h.x, h.y, h.z + 1.2), attacker, 7.0, 100.0, WI_VEHICLE)
        self.events.append(("hboom", h.id))

    def leave_heli(self, pl, announce=False):
        hc = self.heli_by_id(pl.heli) if pl.heli >= 0 else None
        pl.heli, pl.trig = -1, False
        if hc is None:
            return
        if hc.driver == pl.pid:
            hc.driver = -1
        a = math.radians(hc.heading)
        x, y = hc.x + math.cos(a) * 4.2, hc.y + math.sin(a) * 4.2
        pl.x, pl.y = push_out(x, y, PLAYER_R, self, hc.z)
        pl.z, pl.vz = self.floor_at(pl.x, pl.y, hc.z + 0.5), 0.0
        if announce:
            self.events.append(("vexit", pl.pid, round(pl.x, 2), round(pl.y, 2), round(pl.z, 2)))

    def heli_dir(self, pl):
        hr, pr = math.radians(pl.heading), math.radians(pl.pitch)
        return (-math.sin(hr) * math.cos(pr), math.cos(hr) * math.cos(pr), math.sin(pr))

    def heli_rocket(self, pl):
        """Rechte Maustaste im Cockpit: eine Rakete entlang der Blickrichtung (abwechselnd links/rechts)."""
        hc = self.heli_by_id(pl.heli) if pl.heli >= 0 else None
        if (hc is None or hc.driver != pl.pid or hc.hp <= 0 or hc.rk <= 0 or hc.rk_cd > 0
                or hc.ground or self.phase != "play"):
            return False
        d = self.heli_dir(pl)
        hr = math.radians(pl.heading)
        hc.side = -hc.side
        ox = hc.x + d[0] * 1.8 + math.cos(hr) * 1.4 * hc.side
        oy = hc.y + d[1] * 1.8 + math.sin(hr) * 1.4 * hc.side
        oz = hc.z + 2.3 + d[2] * 1.8
        spd = WEAPONS[ROCKET_WI].speed
        self.bullets.append(Bullet(ox, oy, oz, d[0] * spd, d[1] * spd, d[2] * spd, 0.0, pl.pid, self.next_bid, ROCKET_WI))
        self.next_bid += 1
        hc.rk -= 1
        hc.rk_cd = HELI_RK_CD
        pl.protect = 0.0
        self.events.append(("hrk", pl.pid))
        return True

    def update_helis(self, dt):
        for hc in self.helis:
            if hc.hp <= 0:                               # Wrack stürzt ab; später steht ein neuer da
                hc.dead_t += dt
                hc.vz -= 18.0 * dt
                gz = self.ground_for(hc.x, hc.y, hc.z)
                hc.z = max(gz, hc.z + hc.vz * dt)
                if hc.z <= gz:
                    hc.vz = 0.0
                if hc.dead_t > HELI_RESPAWN:
                    hc.reset()
                    self.events.append(("hreset", hc.id))
                continue
            hc.stall_t = max(-1.0, hc.stall_t - dt)
            drv = self.players.get(hc.driver)
            if hc.driver >= 0 and (drv is None or drv.hp <= 0 or drv.heli != hc.id):
                if drv is not None and drv.heli == hc.id:
                    drv.heli = -1
                hc.driver = -1
                if not hc.ground:                        # Pilot weg mitten im Flug: Absturz
                    self.destroy_heli(hc, -1)
                    continue
            hc.mg_cd = max(-0.1, hc.mg_cd - dt)          # darf kurz negativ sein: gleichmässige Feuerrate
            hc.rk_cd = max(0.0, hc.rk_cd - dt)
            hc.firing = False
            if hc.driver < 0:
                hc.speed = hc.vx = hc.vy = 0.0
            elif drv is not None and drv.trig and not hc.ground and self.phase == "play":
                for _ in range(3):                       # Minigun
                    if hc.mg_cd > 0 or hc.mg < 1:
                        break
                    hc.mg_cd += HELI_MG_CD
                    hc.mg -= 1
                    hc.firing = True
                    drv.protect = 0.0
                    sp = math.radians(HELI_SPREAD)
                    h = math.radians(drv.heading) + self.mrng.uniform(-sp, sp)
                    p = math.radians(drv.pitch) + self.mrng.uniform(-sp, sp)
                    d = (-math.sin(h) * math.cos(p), math.cos(h) * math.cos(p), math.sin(p))
                    w = WEAPONS[MINIGUN_WI]
                    self.bullets.append(Bullet(hc.x + d[0] * 1.5, hc.y + d[1] * 1.5, hc.z + 2.5 + d[2] * 1.5,
                                               d[0] * w.speed, d[1] * w.speed, d[2] * w.speed, w.dmg, drv.pid,
                                               self.next_bid, MINIGUN_WI))
                    self.next_bid += 1
            if hc.ground and hc.speed < 3.0 and self.on_pad(hc.x, hc.y):
                hc.mg = min(float(HELI_MG_MAX), hc.mg + HELI_RELOAD_MG * dt)       # auf dem Pad: auftanken
                if hc.rk < HELI_RK_MAX:
                    hc.rel_t += dt
                    if hc.rel_t >= HELI_RELOAD_RK:
                        hc.rel_t = 0.0
                        hc.rk += 1
                        self.events.append(("reload", hc.id))
            else:
                hc.rel_t = 0.0

    # ------------------------------------------------------------ Tomahawk
    def in_strike(self, x, y):
        return math.hypot(x - self.strike_x, y - self.strike_y) <= STRIKE_R      # in allen Modi kreisförmig

    def build_toma_spots(self):
        """Orte der Tomahawk-Säule (TOMA_SPOTS). Erhöhte Orte stehen fest; für Bodenorte wird in der Nähe ein
        freier, ebener Platz gesucht (kein Baum, Fels, Teich, keine Wand). Gleiches Ergebnis bei allen Spielern."""
        for dx, dy, z in TOMA_SPOTS:
            x, y = CENTER + dx, CENTER + dy
            if z is None:
                best = None
                for r in (0.0, 1.5, 3.0, 4.5, 6.0, 8.0, 10.0):
                    for k in range(1 if r == 0 else 12):
                        a = k * math.tau / 12
                        px, py = x + math.cos(a) * r, y + math.sin(a) * r
                        if self.toma_ground_ok(px, py):
                            best = (px, py)
                            break
                    if best:
                        break
                if best is None:
                    continue
                x, y = best
                z = self.floor_at(x, y, self.height(x, y))
            h = math.degrees(math.atan2(-(CENTER - x), CENTER - y)) if (x, y) != (CENTER, CENTER) else 0.0
            self.toma_spots.append((x, y, float(z), h))

    def toma_ground_ok(self, x, y):
        if self.mtn and mountain(x, y) > 0.5:
            return False
        rw = self.runway                                   # Rollbahn, Helipads, Fahrzeugplätze freihalten
        if rw and rw[0] - TOMA_KEEP_FREE <= x <= rw[2] + TOMA_KEEP_FREE and \
                rw[1] - TOMA_KEEP_FREE <= y <= rw[3] + TOMA_KEEP_FREE:
            return False
        if any(math.hypot(x - px, y - py) < TOMA_KEEP_FREE + 8.0 for px, py in self.pads):
            return False
        if any(math.hypot(x - v.x, y - v.y) < TOMA_KEEP_FREE for v in self.vehicles):
            return False
        for b in self.boxes_near(x - TOMA_GROUND_CLEAR, y - TOMA_GROUND_CLEAR,
                                 x + TOMA_GROUND_CLEAR, y + TOMA_GROUND_CLEAR):
            if b.z1 > 0.3 and b.z0 < 2.5 and math.hypot(max(b.x0 - x, 0, x - b.x1),
                                                        max(b.y0 - y, 0, y - b.y1)) < TOMA_GROUND_CLEAR:
                return False                               # zu nah an Wand/Deckung: keine Engstelle zustellen
        if self.height(x, y) < WATER_LEVEL + 0.6 or terrain_slope(self, x, y) > 0.4 or self.in_void(x, y, 1.5):
            return False
        if any(math.hypot(x - px, y - py) < r * 1.8 for px, py, r in self.ponds):
            return False
        if any(math.hypot(x - p.x, y - p.y) < p.solid_r + 4.0 for p in self.props):
            return False
        return not self.in_solid(x, y, 1.3)

    def set_toma(self, i, age=0.0):
        """Aktiven Säulen-Ort setzen (-1 = keiner). age = s seit dem Auftauchen."""
        if not (isinstance(i, int) and 0 <= i < len(self.toma_spots)):
            i = -1
        self.toma_idx = i
        self.toma_age = float(age)
        if i < 0:
            self.button = SimpleNamespace(x=-999.0, y=-999.0, z=-999.0)
            return
        x, y, z, _h = self.toma_spots[i]
        self.button = SimpleNamespace(x=x, y=y, z=z)

    def toma_ready(self):
        """Steht eine Säule ganz oben (Knopf benutzbar)?"""
        return self.toma_idx >= 0 and self.toma_age >= TOMA_RISE_T

    def place_toma(self):
        """Host: die Säule an einem zufälligen Ort hochfahren lassen - nie dort, wo sie zuletzt benutzt wurde."""
        n = len(self.toma_spots)
        if n == 0:
            self.set_toma(-1)
            return
        choices = [i for i in range(n) if i != self.toma_last] or list(range(n))
        self.set_toma(self.mrng.choice(choices), 0.0)

    def press_button(self, pl, tx=None, ty=None, dur=None):
        """Tomahawk starten; (tx, ty) = gewählter Einschlagpunkt (ohne Angabe: Kartenmitte), dur = Countdown
        (STRIKE_OPTIONS). Die Säule wird unbrauchbar und versinkt; nach der Abklingzeit fährt woanders eine hoch.
        Wer auslöst, ist danach TOMA_PLAYER_CD Sekunden für den Tomahawk gesperrt."""
        if (self.strike != 0 or self.phase != "play" or pl.hp <= 0 or not self.toma_ready()
                or self.toma_lock.get(pl.pid, 0.0) > 0):
            return False
        if dur in STRIKE_OPTIONS:
            self.strike_dur = float(dur)
        elif self.strike_dur not in STRIKE_OPTIONS:
            self.strike_dur = float(STRIKE_T)
        if tx is None or ty is None or not (math.isfinite(tx) and math.isfinite(ty)):
            tx, ty = CENTER, CENTER
        self.strike_x, self.strike_y = clampf(float(tx), 4.0, WORLD - 4.0), clampf(float(ty), 4.0, WORLD - 4.0)
        self.strike, self.strike_t, self.strike_by = 1, self.strike_dur, pl.pid
        pl.stats["toma_fired"] += 1
        self.strike_ang = self.mrng.uniform(0.0, 360.0)
        self.toma_last = self.toma_idx
        self.toma_sink_idx, self.toma_sink_t = self.toma_idx, 0.0
        if TOMA_PLAYER_CD > 0:
            self.toma_lock[pl.pid] = float(TOMA_PLAYER_CD)
        self.set_toma(-1)
        self.events.append(("strike", pl.pid))
        return True

    def update_strike(self, dt):
        self.toma_age += dt
        if self.toma_sink_idx >= 0:
            self.toma_sink_t += dt
            if self.toma_sink_t >= TOMA_SINK_T:
                self.toma_sink_idx = -1
        for pid in list(self.toma_lock):
            self.toma_lock[pid] -= dt
            if self.toma_lock[pid] <= 0:
                del self.toma_lock[pid]
        if self.strike == 2 and self.strike_cd > 0 and self.phase == "play":
            self.strike_wait -= dt                       # Abklingzeit läuft; danach ist der Knopf wieder bereit
            if self.strike_wait <= 0:
                self.strike, self.strike_wait = 0, 0.0
                self.place_toma()                        # an einem anderen Ort
                self.events.append(("strikeready",))
            return
        if self.strike != 1:
            return
        if self.phase != "play":
            return
        self.strike_t -= dt
        if self.strike_t <= 0:
            self.strike_hit()

    def strike_hit(self):
        self.strike, self.strike_t = 2, 0.0
        j = max(0.0, min(0.95, TOMA_RESPAWN_JITTER))
        self.strike_wait = self.strike_cd * self.mrng.uniform(1.0 - j, 1.0 + j)
        tx, ty = self.strike_x, self.strike_y
        cz = self.height(tx, ty)
        self.make_noise(tx, ty, NOISE_TOMAHAWK)
        self.events.append(("tomahawk", round(tx, 1), round(ty, 1)))
        self.events.append(("explosion", (round(tx, 2), round(ty, 2), round(cz + 1.0, 2)), 16.0))
        n, rr = 8, STRIKE_R * 0.6
        for i in range(n):
            a = i * math.tau / n
            x, y = tx + math.cos(a) * rr, ty + math.sin(a) * rr
            self.events.append(("explosion", (round(x, 2), round(y, 2), round(self.height(x, y) + 1.0, 2)), 9.0))
        for v in list(self.vehicles):
            if v.hp > 0 and v.z > -1.5 and self.in_strike(v.x, v.y):
                self.destroy_vehicle(v, self.strike_by)
        for hc in self.helis:
            if hc.hp > 0 and self.in_strike(hc.x, hc.y):
                self.destroy_heli(hc, self.strike_by)
        for pl in list(self.players.values()):
            if pl.hp > 0 and pl.z > -1.5 and self.in_strike(pl.x, pl.y):
                pl.protect = 0.0
                self.damage_player(pl, 9999.0, self.strike_by, WI_TOMAHAWK)
        for m in self.mobs:
            if m.state != "dead" and m.z > -1.5 and self.in_strike(m.x, m.y):
                self.hurt_mob(m, 9999.0, (m.x, m.y, m.z + m.height * 0.5), (0.0, 0.0, 1.0), False, self.strike_by)

    # ------------------------------------------------------------ Granaten
    def throw_grenade(self, pl, eye, d):
        """Granate werfen. Beim Client geht der Wurf an den Host (er simuliert sie)."""
        if (pl.hp <= 0 or pl.grenades <= 0 or self.phase != "play" or pl.vehicle >= 0
                or pl.mount >= 0 or pl.heli >= 0):
            return False
        pl.grenades -= 1
        pl.protect = 0.0
        if self.gren_sink is not None:
            self.gren_sink(pl, eye, d)
        else:
            self.spawn_grenade(pl.pid, eye, d)
        return True

    def spawn_grenade(self, owner, eye, d):
        g = Grenade(self.next_gid, eye[0], eye[1], eye[2],
                    d[0] * GREN_SPEED, d[1] * GREN_SPEED, d[2] * GREN_SPEED + 2.0, owner)
        self.next_gid += 1
        self.grenades.append(g)
        self.events.append(("throw", owner))

    def update_grenades(self, dt):
        alive = []
        for g in self.grenades:
            g.fuse -= dt
            if g.fuse <= 0:
                self.explode((g.x, g.y, g.z + 0.1), g.owner, GREN_R, GREN_DMG, WI_GRENADE)
                continue
            n = int(math.sqrt(g.vx ** 2 + g.vy ** 2 + g.vz ** 2) * dt / 0.25) + 1
            h = dt / n
            for _ in range(n):
                self.grenade_step(g, h)
            if -40 < g.x < WORLD + 40 and -40 < g.y < WORLD + 40 and g.z > -30:
                alive.append(g)
        self.grenades = alive

    def grenade_step(self, g, h):
        """Ein Teilschritt: Schwerkraft, Abprallen an Quadern, Bäumen, Felsen und am Boden."""
        g.vz -= GREN_G * h
        nx, ny, nz = g.x + g.vx * h, g.y + g.vy * h, g.z + g.vz * h
        for b in self.boxes_near(nx - 0.15, ny - 0.15, nx + 0.15, ny + 0.15):
            if b.x0 - 0.1 < nx < b.x1 + 0.1 and b.y0 - 0.1 < ny < b.y1 + 0.1 and b.z0 - 0.1 < nz < b.z1 + 0.1:
                if not (b.x0 - 0.1 < g.x < b.x1 + 0.1):          # von der Seite aufgetroffen
                    g.vx, nx = -g.vx * 0.45, g.x
                elif not (b.y0 - 0.1 < g.y < b.y1 + 0.1):
                    g.vy, ny = -g.vy * 0.45, g.y
                elif g.z >= b.z1:                                # von oben: liegen bleiben
                    nz, g.vz = b.z1 + 0.1, (abs(g.vz) * 0.35 if abs(g.vz) > 1.5 else 0.0)
                    g.vx *= 0.8
                    g.vy *= 0.8
                else:                                            # von unten gegen die Decke
                    nz, g.vz = b.z0 - 0.1, -abs(g.vz) * 0.3
                g.vx *= 0.85
                g.vy *= 0.85
        for p in self.props_near(nx, ny, nx, ny):
            dx, dy = nx - p.x, ny - p.y
            d = math.hypot(dx, dy)
            if d < p.hit_r + 0.1 and p.z - 0.3 < nz < p.z + p.hit_h:
                d = d or 0.01
                nx, ny = p.x + dx / d * (p.hit_r + 0.1), p.y + dy / d * (p.hit_r + 0.1)
                dv = (g.vx * dx + g.vy * dy) / d             # Geschwindigkeit nach aussen
                if dv < 0:
                    g.vx -= 1.6 * dv * dx / d
                    g.vy -= 1.6 * dv * dy / d
        gz = self.ground_for(nx, ny, nz) + 0.1
        if nz < gz:
            nz = gz
            if g.vz < 0:
                g.vz = -g.vz * 0.4 if g.vz < -1.5 else 0.0
            fr = math.exp(-5.0 * h)                              # Rollreibung
            g.vx *= fr
            g.vy *= fr
        g.x, g.y, g.z = nx, ny, nz

    # ------------------------------------------------------------ Kugeln
    def add_shot(self, pl, eye, dirs, w):
        """Kugeln eines Schusses erzeugen. Beim Client (shot_sink) werden sie
        stattdessen an den Host geschickt - der simuliert alle Kugeln."""
        self.events.append(("shot", pl.cur, pl.pid))
        if self.shot_sink is not None:
            self.shot_sink(pl, eye, dirs, w)
            return
        self.events.append(("shotpos", pl.pid, round(pl.x, 1), round(pl.y, 1)))
        pl.protect = 0.0                                 # Spawnschutz endet beim Schiessen
        self.make_noise(pl.x, pl.y, NOISE_SHOT * getattr(w, "loud", 1.0))
        for d in dirs:
            self.bullets.append(Bullet(eye[0], eye[1], eye[2],
                                       d[0] * w.speed, d[1] * w.speed, d[2] * w.speed,
                                       w.dmg, pl.pid, self.next_bid, pl.cur))
            self.next_bid += 1

    def own_vehicle_id(self, pid):
        """ID des Wagens, in dem Spieler pid fährt oder dessen Heckgeschütz er bedient (sonst -1)."""
        pl = self.players.get(pid)
        if pl is None:
            return -1
        if pl.vehicle >= 0:
            return pl.vehicle
        if pl.mount >= 0:
            t = next((t for t in self.turrets if t.id == pl.mount), None)
            if t is not None and t.kind == "car":
                return t.vid
        return -1

    def bullet_substep(self, b, h):
        """Ein Integrationsschritt der Dauer h; False, wenn die Kugel endet."""
        x0, y0, z0 = b.x, b.y, b.z
        b.vz -= GRAV_BULLET * b.grav * h                 # Bulletdrop
        x1, y1, z1 = x0 + b.vx * h, y0 + b.vy * h, z0 + b.vz * h
        p0, p1 = (x0, y0, z0), (x1, y1, z1)
        best_t, hit, who = 2.0, None, None
        for m in self.mobs:
            if m.state == "dead":
                continue
            if (max(x0, x1) < m.x - m.radius or min(x0, x1) > m.x + m.radius
                    or max(y0, y1) < m.y - m.radius or min(y0, y1) > m.y + m.radius):
                continue
            t = seg_cyl(p0, p1, m.x, m.y, m.radius, m.z, m.z + m.height)
            if t is not None and t < best_t:
                best_t, hit, who = t, "mob", m
        own_v = self.own_vehicle_id(b.owner)
        for v in self.vehicles:
            if v.hp <= 0 or v.id == own_v:               # der eigene Wagen wird nie vom eigenen Geschütz getroffen
                continue
            if (max(x0, x1) < v.x - VEH_R or min(x0, x1) > v.x + VEH_R
                    or max(y0, y1) < v.y - VEH_R or min(y0, y1) > v.y + VEH_R):
                continue
            t = seg_cyl(p0, p1, v.x, v.y, VEH_R, v.z, v.z + VEH_HIT_H)
            if t is not None and t < best_t:
                best_t, hit, who = t, "vehicle", v
        for hc in self.helis:
            if hc.hp <= 0 or (b.owner >= 0 and hc.driver == b.owner):
                continue
            if (max(x0, x1) < hc.x - HELI_R or min(x0, x1) > hc.x + HELI_R
                    or max(y0, y1) < hc.y - HELI_R or min(y0, y1) > hc.y + HELI_R):
                continue
            t = seg_cyl(p0, p1, hc.x, hc.y, HELI_R, hc.z, hc.z + HELI_HIT_H)
            if t is not None and t < best_t:
                best_t, hit, who = t, "heli", hc
        if self.phase == "play":
            for pl in self.players.values():
                if pl.hp <= 0 or pl.pid == b.owner or pl.protect > 0 or pl.vehicle >= 0 or pl.heli >= 0:
                    continue
                if (max(x0, x1) < pl.x - PLAYER_HIT_R or min(x0, x1) > pl.x + PLAYER_HIT_R
                        or max(y0, y1) < pl.y - PLAYER_HIT_R or min(y0, y1) > pl.y + PLAYER_HIT_R):
                    continue
                t = seg_cyl(p0, p1, pl.x, pl.y, PLAYER_HIT_R, pl.z, pl.z + body_h(pl))
                if t is not None and t < best_t:
                    best_t, hit, who = t, "player", pl
        for p in self.props_near(x0, y0, x1, y1):
            t = seg_cyl(p0, p1, p.x, p.y, p.hit_r, p.z - 0.3, p.z + p.hit_h)
            if t is not None and t < best_t:
                best_t, hit, who = t, p.kind, None
        for bx in self.boxes_near(x0, y0, x1, y1):
            t = seg_box(p0, p1, bx)
            if t is not None and t < best_t:
                best_t, hit, who = t, "rock", None       # Gebäude splittern wie Stein
        if hit is None and z0 >= WATER_LEVEL > z1:
            for px, py, r in self.ponds:
                if math.hypot(x1 - px, y1 - py) < r * 1.3:
                    best_t, hit = (z0 - WATER_LEVEL) / (z0 - z1), "water"
                    break
        if hit is None and z1 <= self.ground_for(x1, y1, z1):
            best_t, hit = 1.0, "ground"
        if hit is None:
            b.x, b.y, b.z = x1, y1, z1
            b.travel += math.sqrt((x1 - x0) ** 2 + (y1 - y0) ** 2 + (z1 - z0) ** 2)
            return True
        hx, hy, hz = x0 + (x1 - x0) * best_t, y0 + (y1 - y0) * best_t, z0 + (z1 - z0) * best_t
        if hit == "ground":
            hz = self.ground_for(hx, hy, hz)
        b.x, b.y, b.z = hx, hy, hz
        d = norm((b.vx, b.vy, b.vz))
        if b.blast_r > 0:                                # Rakete: Explosion kurz vor dem Ziel
            self.explode((hx - d[0] * 0.3, hy - d[1] * 0.3, hz - d[2] * 0.3),
                         b.owner, b.blast_r, b.blast_dmg, b.wi)
        elif hit == "mob":
            b.alerted.add(who.id)
            head = hz > who.z + 0.78 * who.height
            self.note_hit(b.owner, head)
            self.hurt_mob(who, b.dmg * (2.0 if head else 1.0), (hx, hy, hz), d, head, b.owner, b.wi)
        elif hit == "player":
            head = hz > who.z + 0.78 * body_h(who)
            if b.owner != who.pid:
                self.note_hit(b.owner, head)
            self.hit_player(who, b.dmg * (2.0 if head else 1.0), (hx, hy, hz), d, head, b.owner, b.wi)
        elif hit == "vehicle":
            self.events.append(("impact", (hx, hy, hz), "rock"))
            self.damage_vehicle(who, b.dmg, b.owner)
        elif hit == "heli":
            self.events.append(("impact", (hx, hy, hz), "rock"))
            self.damage_heli(who, 0.0 if b.wi == PISTOL_WI else b.dmg * HELI_K, b.owner)
        else:
            self.events.append(("impact", (hx, hy, hz), hit))
        return False

    def update_bullets(self, dt):
        alive = []
        for b in self.bullets:
            b.life -= dt
            if b.wi == WI_FLAK:                          # Flak: Zünder im Umkreis eines Helikopters / nach Ablauf
                near = any(hc.hp > 0 and math.dist((b.x, b.y, b.z), (hc.x, hc.y, hc.z + 1.5)) < FLAK_PROX
                           for hc in self.helis)
                if near or b.life <= 0:
                    self.explode((b.x, b.y, b.z), b.owner, b.blast_r, b.blast_dmg, WI_FLAK)
                    continue
            if b.life <= 0:
                continue
            speed = math.sqrt(b.vx ** 2 + b.vy ** 2 + b.vz ** 2)
            n = max(1, int(speed * dt / 1.0) + 1)        # Teilstücke <= ~1 m
            ok = True
            p0 = (b.x, b.y, b.z)
            for _ in range(n):
                if not self.bullet_substep(b, dt / n):
                    ok = False
                    break
            if self.mobs and b.blast_r <= 0:
                self.bullet_alert(b, p0, not ok)
            if ok and -50 < b.x < WORLD + 50 and -50 < b.y < WORLD + 50:
                alive.append(b)
        self.bullets = alive

    def bullet_alert(self, b, p0, ended):
        """Kugellärm entlang der Flugbahn: Monster, an denen die Kugel in diesem Schritt (p0 -> jetzt) näher als
        BULLET_NOISE_R vorbeiflog oder neben denen sie (ended) einschlug, bemerken sie."""
        p1 = (b.x, b.y, b.z)
        d = norm((b.vx, b.vy, b.vz))
        x0, x1 = min(p0[0], p1[0]) - BULLET_IMPACT_R - 2, max(p0[0], p1[0]) + BULLET_IMPACT_R + 2
        y0, y1 = min(p0[1], p1[1]) - BULLET_IMPACT_R - 2, max(p0[1], p1[1]) + BULLET_IMPACT_R + 2
        for m in self.mobs:
            if m.state == "dead" or m.id in b.alerted or not (x0 < m.x < x1 and y0 < m.y < y1):
                continue
            c = (m.x, m.y, m.z + m.height * 0.5)
            near = seg_point_dist(p0, p1, c) < BULLET_NOISE_R + m.radius
            if not near and ended:
                near = math.dist(p1, c) < BULLET_IMPACT_R + m.radius
            if near:
                b.alerted.add(m.id)
                m.on_shot(self, d, False)

    def separate_mobs(self):
        """Monster schieben sich gegenseitig auseinander."""
        ms = [m for m in self.mobs if m.state != "dead"]
        for i, a in enumerate(ms):
            for b in ms[i + 1:]:
                dx, dy = b.x - a.x, b.y - a.y
                md = a.radius + b.radius
                if abs(dx) > md or abs(dy) > md:
                    continue
                d = math.hypot(dx, dy) or 0.01
                if d < md:
                    push = (md - d) / 2
                    a.x -= dx / d * push
                    a.y -= dy / d * push
                    b.x += dx / d * push
                    b.y += dy / d * push

    def push_player(self, pl):
        """Spieler aus lebenden Monstern herausschieben."""
        if pl.hp <= 0:
            return
        for a in self.mobs:
            if a.state == "dead":
                continue
            dx, dy = pl.x - a.x, pl.y - a.y
            md = a.radius + PLAYER_R
            if abs(dx) > md or abs(dy) > md:
                continue
            d = math.hypot(dx, dy)
            if d < md:
                d = d or 0.01
                pl.x, pl.y = a.x + dx / d * md, a.y + dy / d * md

    # ------------------------------------------------------------ Runde
    def end_match(self):
        self.phase, self.over_t, self.time_left = "over", OVER_T, 0.0
        self.bullets, self.grenades, self.rocks = [], [], []
        self.events.append(("matchend",))
        self.events.append(("stats", self.match_stats()))   # an alle: Endbildschirm

    def match_stats(self):
        """Rundenstatistik aller Spieler (Reihenfolge = Rangliste) - geht einmal am Rundenende an alle."""
        out = []
        for p in self.ranking():
            st = p.stats
            out.append({"pid": p.pid, "name": p.name, "kills": p.kills, "deaths": p.deaths,
                        "score": round(p.score, 1), "mode": self.mode,
                        "stats": {k: (round(v, 1) if isinstance(v, float) else v) for k, v in st.items()}})
        return out

    def new_match(self):
        """Neue Runde: Punkte, Monster, Kisten und Spieler zurücksetzen."""
        self.bullets, self.mobs, self.pending = [], [], []
        self.grenades, self.drops, self.rocks = [], [], []
        for v in self.vehicles:
            v.reset()
        self.strike, self.strike_t, self.strike_by, self.strike_wait = 0, 0.0, -1, 0.0
        self.strike_x = self.strike_y = float(CENTER)
        self.toma_lock.clear()
        self.toma_sink_idx, self.toma_sink_t = -1, 0.0
        self.place_toma()
        for t in self.turrets:
            t.heat, t.over, t.firing, t.op = 0.0, False, False, -1
        for hc in self.helis:
            hc.reset()
        self.kills = 0
        self.reset_crates()
        if self.mobs_on:
            self.populate_mobs()
        self.phase, self.time_left, self.over_t = "play", self.limit, 0.0
        for pl in list(self.players.values()):
            pl.kills = pl.deaths = 0
            pl.score = 0.0
            pl.death_pos = None
            pl.stats = new_stats()
        for pl in list(self.players.values()):
            self.respawn_player(pl)
        self.events.append(("newmatch",))

    def update(self, dt):
        """Simulation der Welt (Monster, Kugeln, Schaden, Punkte) - läuft nur beim Host
        bzw. im Einzelspiel. Die Gegenseite sind alle Spieler in self.players."""
        players = list(self.players.values())
        if self.phase == "over":                         # Endbildschirm: die Welt steht still
            self.over_t -= dt
            if self.over_t <= 0:
                self.new_match()
            return
        for pl in players:                               # Strecken für die Statistik
            last = getattr(pl, "stat_pos", None)
            pl.stat_pos = (pl.x, pl.y, pl.z)
            if last is None or pl.hp <= 0:
                continue
            d = math.hypot(pl.x - last[0], pl.y - last[1])
            if d > 12.0:                                 # Respawn / Sprung: nicht zählen
                continue
            if pl.heli >= 0:
                pl.stats["fly"] += d
            elif pl.vehicle >= 0:
                pl.stats["drive"] += d
            elif pl.mount < 0:
                pl.stats["walk"] += d
        self.update_bullets(dt)
        self.update_grenades(dt)
        self.update_vehicles(dt)
        self.update_turrets(dt)
        self.update_helis(dt)
        self.update_strike(dt)
        self.update_crates(dt)
        for d in [d for d in self.drops if d.life <= dt]:
            self.drops.remove(d)
        for d in self.drops:
            d.life -= dt
        self.update_noise(dt, players)
        for m in self.mobs:
            m.update(dt, self, players)
        if self.rocks:
            self.update_rocks(dt)
        self.separate_mobs()
        for pl in players:
            self.push_player(pl)
        for m in [m for m in self.mobs if m.state == "dead" and m.dead_t > 4.0]:
            self.mobs.remove(m)
            self.pending.append([TITAN_RESPAWN if m.kind == "titan" else RESPAWN_T, m.kind])
        avoid = [(p.x, p.y) for p in players if p.hp > 0] or [(CENTER, CENTER)]
        for e in self.pending[:]:
            e[0] -= dt
            if e[0] <= 0:
                if self.spawn_mob(e[1], avoid, 45.0):
                    self.pending.remove(e)
                else:
                    e[0] = 1.0
        for pl in players:
            pl.dead_age = pl.dead_age + dt if pl.hp <= 0 else 0.0
            pl.since_hurt += dt
            pl.protect = max(0.0, pl.protect - dt)
            if self.regen_rate > 0 and 0 < pl.hp < pl.max_hp and pl.since_hurt > REGEN_DELAY:
                pl.hp = min(pl.max_hp, pl.hp + self.regen_rate * dt)
            pl.stun_t = max(0.0, pl.stun_t - dt)
            pl.stun_lock = max(0.0, pl.stun_lock - dt)
            if pl.hp > 0 and wears(pl, "shield"):
                pl.shield_t += dt
                if pl.shield_t >= SHIELD_DELAY and pl.shield_hp < SHIELD_HP:
                    pl.shield_hp = min(SHIELD_HP, pl.shield_hp + SHIELD_RATE * dt)
            if pl.buff is not None:
                pl.buff_t -= dt
                if pl.buff_t <= 0:
                    self.end_buff(pl)
                    self.events.append(("buffend", pl.pid))
        if self.phase == "play":
            self.time_left -= dt
            if self.mode == "koth":                      # jeder in der Burg-Zone bekommt Punkte
                for pl in players:
                    if pl.hp > 0 and self.in_zone(pl):
                        pl.score += ZONE_PTS * dt
                        pl.stats["zone_t"] += dt
            if self.time_left <= 0:
                self.end_match()
        else:
            self.over_t -= dt
            if self.over_t <= 0:
                self.new_match()


class GunState:
    def __init__(self, w):
        self.mag = w.mag
        self.reserve = min(w.max_reserve, w.mag * 3)
        self.cd = 0.0


class Player:
    def __init__(self, x, y, world, pid=0, name=""):
        self.pid, self.name = pid, name
        self.kills = self.deaths = 0
        self.score = 0.0                  # King of the Hill: Punkte
        self.death_pos = None             # wo er zuletzt gestorben ist (für den Startpunkt)
        self.dead_age = 0.0               # Sekunden seit dem Tod (Wartezeit bis zum Respawn)
        self.respawn(world, x, y)

    def respawn(self, world, x, y):
        """Figur neu aufstellen (Punkte, Kills und Tode bleiben). Bewaffnung: nur die Pistole in Slot 1."""
        self.x, self.y = x, y
        self.z = world.spawn_z(x, y)
        self.vz = 0.0
        self.on_ground = True
        # Blick Richtung Burg (Blick = (-sin h, cos h))
        self.heading = math.degrees(math.atan2(-(CENTER - x), CENTER - y))
        self.pitch = 0.0
        self.phase = 0.0     # für das Kopfwippen beim Laufen
        self.moving = False
        self.hp = PLAYER_HP
        self.max_hp = PLAYER_HP           # Tank-Buff: höher
        self.stun_t = 0.0                 # Betäubung (Drohne): s
        self.stun_lock = 0.0              # Betäubung + Immunität danach (nur Host): solange keine neue
        self.buff, self.buff_t = None, 0.0   # Buff vom Fluchttier: "speed" | "damage" | "tank", Restzeit
        self.gear = {sl: None for sl in GEAR_SLOTS}   # Ausrüstung je Slot (Index in GEAR)
        self.shield_hp, self.shield_t = SHIELD_HP, 99.0   # Schild: Stand, s seit dem letzten Schildschaden
        self.jet_fuel = JET_FUEL          # Jetpack-Treibstoff (s); gehört dem Spieler, nicht dem Teil
        self.jet_on = False               # Jetpack feuert gerade (Anzeige, auch für andere)
        self.dash_cd, self.dash_t = 0.0, 0.0   # Hermes: Abklingzeit, laufender Dash (s)
        self.dash_dir = (0.0, 0.0)
        self.air_jump = False             # Doppelsprung in diesem Sprung schon benutzt
        self.jump_edge = self.run_edge = False   # Taste in diesem Bild neu gedrückt (für Doppelsprung/Dash)
        self.since_hurt = 99.0
        self.guns = [GunState(w) for w in WEAPONS]
        self.stats = new_stats()          # Rundenstatistik (Host)
        self.sb = None                    # Mitspieler: (Monster, Kisten, Buffs) aus dem Snapshot
        self.loot_history = {}            # Kisten-Gedächtnis (nur beim Host benutzt): Name -> in diesem Leben gezogen
        self.last_loot = None             # zuletzt aus einer Kiste gezogen (kommt in der nächsten nicht)
        self.slots = [None] * N_SLOTS     # Slot 1..N_FREE_SLOTS: normale Waffen, danach: Spezialwaffe
        self.slots[0] = START_WEAPON
        self.last_slot = 0                # zuletzt benutzter normaler Slot (für den Tausch, wenn man die
        self.melee, self.melee_out = START_MELEE, False   # Nahkampfwaffe (Index in MELEE), gerade in der Hand?
        self.melee_cd = self.swing_t = 0.0                 # Abklingzeit, laufender Schlag (Animation)
        self.cur = self.switch_to = START_WEAPON   # Spezialwaffe hält und beide normalen Slots voll sind)
        self.switch_t = 0.0
        self.reload_t = 0.0
        self.ads = False
        self.bloom = 0.0
        self.trigger_buf = 0.0
        self.protect = PROTECT_T          # Spawnschutz in Sekunden
        self.grenades = GRENADES_START
        self.gren_cd = 0.0
        self.vehicle = -1                 # ID des Fahrzeugs, in dem er sitzt (-1 = zu Fuss)
        self.mount = -1                   # ID des Geschützes, das er bedient
        self.heli = -1                    # ID des Helikopters, den er fliegt
        self.trig = False                 # Abzug gehalten (für Geschütze)
        self.lean = 0.0                   # seitlicher Versatz durch Lehnen (m, + = rechts)
        self.lean_x = self.lean_y = 0.0
        self.duck = False                 # Duck-Taste gehalten
        self.crouch = 0.0                 # 0 = stehend .. 1 = geduckt (weich)
        self.fall_dmg = 0.0               # Fallschaden, der noch gemeldet/verrechnet werden muss
        self.fall_h = 0.0                 # Höhe des letzten schmerzhaften Sturzes (Anzeige)


def note_hand(pl):
    """Merkt sich den zuletzt benutzten normalen Slot (für den Sonderfall beim Tausch)."""
    if 0 <= pl.cur < len(WEAPONS) and WEAPONS[pl.cur].kind != "special" and pl.cur in pl.slots[:N_FREE_SLOTS]:
        pl.last_slot = pl.slots.index(pl.cur)


def stock_ammo(pl, wi):
    """Waffe aufgehoben, die man schon trägt: Reserve auffüllen statt eines zweiten Exemplars."""
    w, g = WEAPONS[wi], pl.guns[wi]
    g.reserve = min(w.max_reserve, g.reserve + w.mag * DUP_AMMO_MAGS)


def target_slot(pl, wi):
    """In welchen Slot käme die Waffe wi (Regeln siehe take_weapon)?"""
    if WEAPONS[wi].kind == "special":
        return SPECIAL_SLOT
    slot = next((i for i in range(N_FREE_SLOTS) if pl.slots[i] is None), None)
    if slot is None:
        slot = pl.slots.index(pl.cur) if pl.cur in pl.slots[:N_FREE_SLOTS] else pl.last_slot
        slot = slot if 0 <= slot < N_FREE_SLOTS else 0
    return slot


def take_weapon(pl, wi):
    """Waffe ins Inventar legen. Regeln:
    - normale Waffe: in einen freien Slot 1..N_FREE_SLOTS; sind alle voll, wird die normale Waffe in der Hand
      getauscht - hält man gerade die Spezialwaffe, die zuletzt benutzte normale Waffe (pl.last_slot);
    - Spezialwaffe: nur in SPECIAL_SLOT; ist er belegt, wird die alte Spezialwaffe getauscht;
    - trägt man die Waffe schon: nur Munition (stock_ammo).
    Neue Waffen kommen mit frischer Munition. -> (verdrängte Waffe oder None, schon_vorhanden)"""
    if wi in pl.slots:
        stock_ammo(pl, wi)
        return None, True
    w = WEAPONS[wi]
    note_hand(pl)
    slot = target_slot(pl, wi)
    out = pl.slots[slot]
    pl.slots[slot] = wi
    pl.guns[wi] = GunState(w)
    if out is not None and pl.cur == out:        # die Waffe in der Hand wurde getauscht: sofort die neue nehmen
        pl.cur = pl.switch_to = wi
        pl.switch_t = SWITCH_T * 0.5             # zweite Hälfte der Wechsel-Animation (Waffe hochnehmen)
        pl.reload_t = 0.0
    if WEAPONS[pl.cur].kind != "special" and pl.cur in pl.slots[:N_FREE_SLOTS]:
        note_hand(pl)
    return out, False


def eye_h(pl):
    """Augenhöhe über den Füssen (geduckt niedriger)."""
    return EYE - CROUCH_DROP * pl.crouch


def body_h(pl):
    """Körpergrösse für Treffer (geduckt kleiner)."""
    return PLAYER_H - (PLAYER_H - CROUCH_H) * pl.crouch


def update_crouch(pl, dt, world):
    """Ducken (Taste gehalten): weich ab-/aufstehen. Unter niedriger Decke bleibt man geduckt."""
    want = 1.0 if pl.duck else 0.0
    if want < pl.crouch and world.ceiling_at(pl.x, pl.y, pl.z + 0.1) - pl.z < PLAYER_H + 0.05:
        want = 1.0
    pl.crouch += clampf(want - pl.crouch, -6.0 * dt, 6.0 * dt)


def step(pl, forward, strafe, run, jump, dt, world):
    """Ein Simulationsschritt. forward/strafe in -1..1.
    Später läuft derselbe Code auf dem Server."""
    h = math.radians(pl.heading)
    fx, fy = -math.sin(h), math.cos(h)
    rx, ry = math.cos(h), math.sin(h)
    dx = fx * forward + rx * strafe
    dy = fy * forward + ry * strafe
    l = math.hypot(dx, dy)
    pl.moving = l > 0
    pl.running = pl.moving and bool(run) and pl.crouch < 0.3        # für das Lärmsystem
    ox, oy = pl.x, pl.y
    gear = getattr(pl, "gear", None)
    if gear is not None:                                            # Ausrüstung: Abklingzeiten (beim Spieler)
        pl.dash_cd = max(0.0, pl.dash_cd - dt)
        if (pl.run_edge and pl.moving and pl.dash_cd <= 0 and pl.dash_t <= 0 and pl.crouch < 0.3
                and wears(pl, "dash")):                             # Hermes: Shift drücken = Dash nach vorn
            pl.dash_t, pl.dash_cd = DASH_TIME, DASH_CD
            pl.dash_dir = (dx / l, dy / l)
        pl.run_edge = False
    if gear is not None and pl.dash_t > 0:
        pl.dash_t -= dt
        sp = DASH_DIST / DASH_TIME
        pl.x += pl.dash_dir[0] * sp * dt
        pl.y += pl.dash_dir[1] * sp * dt
        pl.moving = True
    elif pl.moving:
        speed = RUN if (run and pl.crouch < 0.3) else WALK     # geduckt kein Rennen
        if pl.ads:
            speed *= 0.6
        speed *= 1.0 - (1.0 - CROUCH_SPEED) * pl.crouch
        if getattr(pl, "buff", None) == "speed" and pl.buff_t > 0:
            speed *= BUFF_SPEED
        pl.x += dx / l * speed * dt
        pl.y += dy / l * speed * dt
        if pl.on_ground:
            pl.phase += speed * dt * 1.6

    pl.x, pl.y = push_out(pl.x, pl.y, PLAYER_R, world, pl.z)
    lo = edge_margin(world)                          # Kartenrand / Gebirgskamm: unsichtbare Wand
    pl.x = max(lo, min(WORLD - lo, pl.x))
    pl.y = max(lo, min(WORLD - lo, pl.y))
    if getattr(world, "mtn", False) and pl.moving and not MTN_CLIMB:
        too_steep(pl, ox, oy, world)                 # Felswände im Gebirge: nicht hinauf (auch nicht springend)

    ground = world.floor_at(pl.x, pl.y, pl.z)       # Gelände oder Treppe/Mauer/Dach
    if world.ladders and world.on_ladder(pl.x, pl.y, pl.z):      # Leiter: W/Leertaste klettern, Ducken hält, sonst langsam runter
        pl.vz = 2.4 if (forward > 0 or jump) else (0.0 if pl.duck else -2.4)
        pl.z += pl.vz * dt
        if pl.z <= ground:
            pl.z, pl.vz, pl.on_ground = ground, 0.0, True
        else:
            pl.on_ground = False
        return
    jedge = getattr(pl, "jump_edge", False)
    pl.jump_edge = False
    if jump and pl.on_ground and pl.crouch < 0.3:
        pl.vz = JUMP_V * (SPRING_JUMP if wears(pl, "spring") else 1.0)   # Springfedern: deutlich höher
        pl.on_ground = False
        pl.air_jump = False
        jedge = False                                # dieser Druck war der normale Sprung
    elif jedge and not pl.on_ground and not pl.air_jump and wears(pl, "double_jump"):
        pl.vz = max(pl.vz, DOUBLE_JUMP_V)            # Jetpack-Schuhe: zweiter Sprung in der Luft
        pl.air_jump = True
        jedge = False
    jet = (gear is not None and jump and not pl.on_ground and not jedge and wears(pl, "jetpack")
           and pl.jet_fuel > 0 and (pl.air_jump or not wears(pl, "double_jump")))
    pl.jet_on = jet                                  # Jetpack: Leertaste in der Luft halten
    if jet:
        pl.jet_fuel = max(0.0, pl.jet_fuel - dt)
        pl.vz = min(JET_VMAX, pl.vz + JET_ACC * dt)
    elif gear is not None:
        pl.jet_fuel = min(JET_FUEL, pl.jet_fuel + JET_FUEL / JET_REFILL_T * dt)
    pl.vz -= GRAVITY * dt
    pl.z += pl.vz * dt
    if pl.vz > 0:                                    # Kopf stösst an eine Decke
        cap = world.ceiling_at(pl.x, pl.y, pl.z) - PLAYER_H
        if pl.z > cap:
            pl.z, pl.vz = max(cap, ground), 0.0
    if pl.z <= ground:
        pl.air_jump = False
        if pl.vz < 0:                                # Aufprall: Fallhöhe aus der Aufprallgeschwindigkeit
            fall = pl.vz * pl.vz / (2.0 * GRAVITY)
            if fall > FALL_SAFE:
                pl.fall_dmg = getattr(pl, "fall_dmg", 0.0) + (fall - FALL_SAFE) * FALL_DMG
                pl.fall_h = fall
        pl.z, pl.vz, pl.on_ground = ground, 0.0, True
    elif pl.on_ground and pl.z - ground < STEP_H and pl.vz <= 0:
        pl.z, pl.vz = ground, 0.0   # an Hängen und Treppen "kleben"
    else:
        pl.on_ground = False


def terrain_slope(world, x, y, e=0.75):
    """Steigung des Geländes (Betrag des Gradienten, 1.0 = 45 Grad)."""
    gx = world.surface_height(x + e, y) - world.surface_height(x - e, y)
    gy = world.surface_height(x, y + e) - world.surface_height(x, y - e)
    return math.hypot(gx, gy) / (2 * e)


def edge_margin(world):
    """Abstand der unsichtbaren Wand zum Kartenrand: auf der Standardkarte (Gebirge) MTN_WALL, sonst 1 m."""
    return MTN_WALL if getattr(world, "mtn", False) else 1.0


def steep_uphill(world, ox, oy, x, y, z):
    """Wäre der Schritt von (ox, oy) nach (x, y) eine Felswand hinauf (steiler als MTN_SLOPE)?"""
    if (x == ox and y == oy) or mountain(x, y) < 0.5:
        return False
    h_old, h_new = world.surface_height(ox, oy), world.surface_height(x, y)
    return h_new > h_old + 1e-4 and h_new > z - 1.3 and terrain_slope(world, x, y) > MTN_SLOPE


def too_steep(pl, ox, oy, world):
    """Gebirge: Ist das Gelände an der neuen Stelle steiler als MTN_SLOPE und geht es dorthin bergauf (und liegt
    es nicht weit unter den Füssen), geht es nicht weiter - die Figur gleitet an der Wand entlang (nur x oder
    nur y), sonst bleibt sie stehen. Gemessen wird die echte Steigung, schräg hinauf geht es also auch nicht.
    Gebäude zählen nicht (die regelt push_out), nur das Gelände."""
    h_old = world.surface_height(ox, oy)

    def blocked(x, y):
        if (x == ox and y == oy) or mountain(x, y) < 0.5:
            return False
        h_new = world.surface_height(x, y)
        return h_new > h_old + 1e-4 and h_new > pl.z - 1.3 and terrain_slope(world, x, y) > MTN_SLOPE
    if not blocked(pl.x, pl.y):
        return
    for x, y in ((pl.x, oy), (ox, pl.y)):
        if not blocked(x, y):
            pl.x, pl.y = x, y
            return
    pl.x, pl.y = ox, oy


def update_lean(pl, key, dt, world):
    """Q/E: um die Ecke lehnen. key = -1 (links), 0, +1 (rechts). Die Figur verschiebt sich
    wirklich seitlich (Wände halten sie auf) - Mitspieler sehen und treffen sie also dort."""
    cur = pl.lean
    nxt = cur + clampf(key * LEAN_MAX - cur, -LEAN_RATE * dt, LEAN_RATE * dt)
    if cur * nxt < 0:
        nxt = 0.0
    if nxt == cur:
        return
    if abs(nxt) < abs(cur):                          # zurücklehnen: denselben Weg zurück
        f = (cur - nxt) / cur
        dx, dy = pl.lean_x * f, pl.lean_y * f
        pl.x -= dx
        pl.y -= dy
        pl.lean_x -= dx
        pl.lean_y -= dy
        pl.lean = nxt
        return
    h = math.radians(pl.heading)
    d = nxt - cur
    x0, y0 = pl.x, pl.y
    pl.x, pl.y = push_out(x0 + math.cos(h) * d, y0 + math.sin(h) * d, PLAYER_R, world, pl.z)
    pl.lean_x += pl.x - x0
    pl.lean_y += pl.y - y0
    pl.lean = math.copysign(math.hypot(pl.lean_x, pl.lean_y), nxt)


def drive(v, throttle, steer, brake, dt, world):
    """Ein Schritt des Geländewagens (arcade): Gas/Rückwärts, Lenken, Handbremse.
    Läuft auf dem Rechner des Fahrers; er meldet Position und Tempo dem Host."""
    sp = v.speed
    if throttle > 0:
        sp += (VEH_ACC * 2.0 if sp < 0 else VEH_ACC) * throttle * dt
    elif throttle < 0:
        sp -= (VEH_ACC * 2.0 if sp > 0 else VEH_ACC * 0.6) * -throttle * dt
    sp -= sp * 0.35 * dt + (math.copysign(1.5 * dt, sp) if abs(sp) > 0.2 else 0.0)   # Rollwiderstand
    if brake:
        sp *= math.exp(-5.0 * dt)
    sp = clampf(sp, -VEH_REV, VEH_MAX)
    if abs(sp) < 0.05 and throttle == 0:
        sp = 0.0
    v.heading -= steer * VEH_TURN * dt * clampf(sp / 5.0, -1.0, 1.0)
    h = math.radians(v.heading)
    fx, fy = -math.sin(h), math.cos(h)
    nx, ny = v.x + fx * sp * dt, v.y + fy * sp * dt
    px, py = push_out(nx, ny, VEH_R, world, v.z, v.id)
    blocked = math.hypot(px - nx, py - ny)
    if blocked > 0.01:
        # nur der Anteil der Fahrt GEGEN das Hindernis bremst; Entlangschrammen (Hang mit Steinen,
        # Bäumen) kostet kaum Tempo - früher blieb der Wagen schon bei jeder Berührung fast stehen
        into = max(0.0, -(fx * (px - nx) + fy * (py - ny)) / blocked * (1.0 if sp >= 0 else -1.0))
        step = max(abs(sp) * dt, 1e-6)
        sp *= 1.0 - 0.5 * into * min(1.0, blocked / (0.6 * step))   # streifen kostet fast nichts, frontal viel
    px, py = clampf(px, 2.0, WORLD - 2.0), clampf(py, 2.0, WORLD - 2.0)
    lo = WATER_LEVEL - 0.2                       # bis ans Ufer fahren (früher stoppte schon die flache Böschung davor)
    h_old = world.height(v.x, v.y)

    def passable(ax, ay):
        hh = world.height(ax, ay)
        if getattr(world, "mtn", False) and mountain(ax, ay) > 0.5:            # Gebirge: zu steil für den Wagen?
            dist = math.hypot(ax - v.x, ay - v.y)
            if dist > 1e-6 and hh - h_old > VEH_SLOPE * dist:
                return False
        return not world.in_void(ax, ay, 1.5) and (hh >= lo or hh >= h_old)   # aus einer Senke darf man heraus

    if not passable(px, py):                     # Teich, Treppenschacht, tiefe Senke: seitlich entlanggleiten
        for ax, ay in ((px, v.y), (v.x, py)):
            if passable(ax, ay):
                px, py, sp = ax, ay, sp * 0.98
                break
        else:
            px, py, sp = v.x, v.y, sp * 0.7
    v.x, v.y, v.speed = px, py, sp
    v.z = world.floor_at(px, py, v.z)


def fly_heli(h, fwd, strafe, vert, yaw, dt, world, stall=False):
    """Ein Schritt des Helikopters (arcade): fwd/strafe -1..1 in Blickrichtung, vert +1 steigen / -1 sinken,
    yaw = Wunsch-Blickrichtung (Maus, die Kurve dreht mit begrenzter Rate nach). Läuft auf dem Rechner des Piloten.
    Hindernisse (Gebäude, Bäume) blockieren nur, sie verursachen keinen Schaden; die Landung wird abgefedert.
    stall (Drohne): Antrieb aus - keine Steuerung, der Heli verliert Fahrt und sinkt mit HELI_STALL_SINK; der
    Aufprall wird nicht abgefedert und in h.impact gemerkt (der Host macht daraus Schaden)."""
    if stall:
        fwd = strafe = 0.0
        yaw = h.heading
    dh = (yaw - h.heading + 180.0) % 360.0 - 180.0
    h.heading += clampf(dh, -110.0 * dt, 110.0 * dt)
    a = math.radians(h.heading)
    fx, fy, rx, ry = -math.sin(a), math.cos(a), math.cos(a), math.sin(a)
    mx, my = fx * fwd + rx * strafe, fy * fwd + ry * strafe
    m = math.hypot(mx, my)
    if m > 1.0:
        mx, my = mx / m, my / m
    vmax = HELI_VMAX * (0.25 if h.ground else 1.0)
    k = min(1.0, 1.6 * dt)
    if stall:                                          # rollt in der Luft aus
        h.vx *= math.exp(-HELI_STALL_DRAG * dt)
        h.vy *= math.exp(-HELI_STALL_DRAG * dt)
    else:
        h.vx += (mx * vmax - h.vx) * k
        h.vy += (my * vmax - h.vy) * k
    gz = max(world.ground_for(h.x, h.y, h.z), world.floor_at(h.x, h.y, h.z))
    alt = h.z - gz
    tvz = vert * (HELI_VUP if vert > 0 else HELI_VDN)
    if vert < 0 and alt < 8.0:
        tvz = max(tvz, -(1.2 + alt * 0.8))                 # sanft aufsetzen
    if h.ground and vert <= 0:
        tvz = 0.0
    if stall:
        tvz = 0.0 if h.ground else -HELI_STALL_SINK
    h.vz += (tvz - h.vz) * min(1.0, (1.2 if stall else 3.5) * dt)
    if h.z > HELI_CEIL:
        h.vz = min(h.vz, 0.0)

    def blocked(x, y):
        if world.in_solid(x, y, HELI_R, h.z) or world.in_solid(x, y, HELI_R, h.z + 1.5):
            return True
        for q in world.props_near(x, y, x, y):
            if q.hit_r > 0 and math.hypot(x - q.x, y - q.y) < q.hit_r + HELI_R * 0.7 and h.z < q.z + q.hit_h + 0.5:
                return True
        return False

    nx, ny = h.x + h.vx * dt, h.y + h.vy * dt
    if blocked(nx, ny):
        if not blocked(nx, h.y):
            ny, h.vy = h.y, 0.0
        elif not blocked(h.x, ny):
            nx, h.vx = h.x, 0.0
        else:
            nx, ny, h.vx, h.vy = h.x, h.y, 0.0, 0.0
    h.x, h.y = clampf(nx, 3.0, WORLD - 3.0), clampf(ny, 3.0, WORLD - 3.0)
    gz = max(world.ground_for(h.x, h.y, h.z), world.floor_at(h.x, h.y, h.z))
    nz = h.z + h.vz * dt
    if nz <= gz:
        if stall and not h.ground:
            h.impact = max(getattr(h, "impact", 0.0), -h.vz)
        nz, h.vz, h.ground = gz, 0.0, True
    else:
        h.ground = False
    h.z = nz
    h.speed = math.hypot(h.vx, h.vy)
    if h.ground:
        h.pitch = h.roll = 0.0
    else:
        vf, vr = h.vx * fx + h.vy * fy, h.vx * rx + h.vy * ry
        h.pitch += (-vf / HELI_VMAX * 14.0 - h.pitch) * min(1.0, 4.0 * dt)
        h.roll += (vr / HELI_VMAX * 16.0 - h.roll) * min(1.0, 4.0 * dt)


def fire(pl, w, world):
    """Erzeugt die Kugeln eines Schusses und wendet den Rückstoss auf die Blickrichtung an."""
    rng = world.mrng
    hr, pr = math.radians(pl.heading), math.radians(pl.pitch)
    cp, sp = math.cos(pr), math.sin(pr)
    f = (-math.sin(hr) * cp, math.cos(hr) * cp, sp)      # Blickrichtung
    r = (math.cos(hr), math.sin(hr), 0.0)                # rechts
    u = cross(r, f)                                      # oben
    eye = (pl.x, pl.y, pl.z + eye_h(pl))
    spread = w.spread * (w.ads_spread if pl.ads else 1.0)
    spread *= 1.0 - 0.3 * pl.crouch
    spread *= 1.0 + pl.bloom + (0.8 if pl.moving else 0.0) + (1.0 if not pl.on_ground else 0.0)
    dirs = []
    for _ in range(w.pellets):
        a = math.radians(spread) * math.sqrt(rng.random())   # gleichverteilt im Kegel
        ph = rng.uniform(0, 2 * math.pi)
        t = math.tan(a)
        d = norm((f[0] + t * (math.cos(ph) * r[0] + math.sin(ph) * u[0]),
                  f[1] + t * (math.cos(ph) * r[1] + math.sin(ph) * u[1]),
                  f[2] + t * (math.cos(ph) * r[2] + math.sin(ph) * u[2])))
        dirs.append(d)
    world.add_shot(pl, eye, dirs, w)        # Host: Kugeln erzeugen, Client: an den Host senden
    pl.bloom = min(2.0, pl.bloom + w.bloom)
    pl.pitch = min(85.0, pl.pitch + w.kick * (0.6 if pl.ads else 1.0))
    pl.heading += rng.uniform(-1, 1) * w.kick_yaw


def update_weapon(pl, world, dt, trigger, edge, reload_req, ads, select):
    """Schiessen, Nachladen, Waffenwechsel. trigger = Abzug gehalten,
    edge = Abzug in diesem Frame neu gedrückt (für Halbautomaten)."""
    g = pl.guns[pl.cur]
    w = WEAPONS[pl.cur]
    g.cd = max(0.0, g.cd - dt)
    pl.bloom = max(0.0, pl.bloom - 5.0 * dt)
    pl.trigger_buf = max(0.0, pl.trigger_buf - dt)
    if edge:
        pl.trigger_buf = 0.18          # zu früh geklickt -> Schuss wird vorgemerkt
    pl.melee_cd = max(0.0, pl.melee_cd - dt)
    pl.swing_t = max(0.0, pl.swing_t - dt)
    if (select is not None and pl.switch_t <= 0
            and ((select == MELEE_SEL and not pl.melee_out) or (select != MELEE_SEL and (select != pl.cur or pl.melee_out)))):
        pl.switch_to, pl.switch_t, pl.reload_t = select, SWITCH_T, 0.0
    if pl.switch_t > 0:
        before = pl.switch_t
        pl.switch_t = max(0.0, pl.switch_t - dt)
        if before > SWITCH_T / 2 >= pl.switch_t:
            if pl.switch_to == MELEE_SEL:          # Nahkampfwaffe ziehen (die Schusswaffe bleibt "cur")
                pl.melee_out = True
            else:
                pl.melee_out = False
                pl.cur = pl.switch_to      # in der Mitte der Animation tauschen
                note_hand(pl)
        pl.ads = False
        return
    if pl.melee_out:                       # Nahkampf: Linke Maus = zuschlagen (gehalten = weiter schlagen)
        pl.ads = False
        if (trigger or pl.trigger_buf > 0) and pl.melee_cd <= 0:
            m = MELEE[pl.melee] if 0 <= pl.melee < len(MELEE) else MELEE[START_MELEE]
            pl.melee_cd = pl.swing_t = m.interval
            pl.trigger_buf = 0.0
            hr, pr = math.radians(pl.heading), math.radians(pl.pitch)
            d = (-math.sin(hr) * math.cos(pr), math.cos(hr) * math.cos(pr), math.sin(pr))
            world.melee_swing(pl, d)
        return
    pl.ads = ads and pl.reload_t <= 0
    if pl.reload_t > 0:
        pl.reload_t -= dt
        if pl.reload_t <= 0:
            take = min(w.mag - g.mag, g.reserve)
            g.mag += take
            g.reserve -= take
            pl.reload_t = 0.0
        return
    wants = trigger if w.auto else pl.trigger_buf > 0
    if (reload_req or (g.mag == 0 and wants)) and g.mag < w.mag and g.reserve > 0:
        pl.reload_t = w.reload
        pl.ads = False
        world.events.append(("wreload", pl.pid, pl.cur))
        return
    if wants and g.cd <= 0 and g.mag > 0:
        g.cd = w.interval
        g.mag -= 1
        pl.trigger_buf = 0.0
        fire(pl, w, world)


# ------------------------------------------------------------ Prozedurale Texturen
# Alle Texturen werden beim Start berechnet (keine Bilddateien nötig) und sind nahtlos kachelbar.
# Sie sind nahezu neutral (Mittelwert ~0.85) und werden mit den Vertexfarben multipliziert.
REAL_PANDA = isinstance(PNMImage, type)      # in den Tests ersetzen Attrappen Panda3D


def _smooth01(t):
    return t * t * (3 - 2 * t)


def _grid(S, px, py, rnd):
    """Wertrauschen mit px x py Gitterzellen, nahtlos kachelbar, Werte 0..1."""
    grid = [[rnd.random() for _ in range(px)] for _ in range(py)]
    xs = []
    for x in range(S):
        f = x * px / S
        i = int(f)
        xs.append((i % px, (i + 1) % px, _smooth01(f - i)))
    out = []
    for y in range(S):
        f = y * py / S
        j = int(f)
        fy = _smooth01(f - j)
        g0, g1 = grid[j % py], grid[(j + 1) % py]
        row = []
        for i0, i1, fx in xs:
            a = g0[i0] + (g0[i1] - g0[i0]) * fx
            b = g1[i0] + (g1[i1] - g1[i0]) * fx
            row.append(a + (b - a) * fy)
        out.append(row)
    return out


def _fbm(S, seed, base=4, octaves=4, gain=0.5, px=None, py=None):
    """Mehrere Rauschoktaven übereinander (px/py: unterschiedliche Frequenz in x und y -> Streifen)."""
    rnd = random.Random(seed)
    acc = [[0.0] * S for _ in range(S)]
    amp = tot = 1.0
    tot = 0.0
    for o in range(octaves):
        gx = min(S, (px or base) * 2 ** o)
        gy = min(S, (py or base) * 2 ** o)
        g = _grid(S, gx, gy, rnd)
        for y in range(S):
            acc[y] = [a + b * amp for a, b in zip(acc[y], g[y])]
        tot += amp
        amp *= gain
    return [[v / tot for v in row] for row in acc]


def _voronoi(S, cells, seed):
    """Zellrauschen: je Pixel (Abstand zum nächsten Punkt, Abstand zum zweitnächsten, Zellnummer)."""
    rnd = random.Random(seed)
    cs = S / cells
    pts = [[((i + 0.1 + rnd.random() * 0.8) * cs, (j + 0.1 + rnd.random() * 0.8) * cs)
            for i in range(cells)] for j in range(cells)]
    rows = []
    for y in range(S):
        cj = int(y // cs)
        row = []
        for x in range(S):
            ci = int(x // cs)
            d1 = d2 = 1e9
            best = 0
            for dj in (-1, 0, 1):
                jj = cj + dj
                for di in (-1, 0, 1):
                    ii = ci + di
                    p = pts[jj % cells][ii % cells]
                    dx = p[0] + (ii // cells) * S - x
                    dy = p[1] + (jj // cells) * S - y
                    d = dx * dx + dy * dy
                    if d < d1:
                        d2, d1, best = d1, d, (jj % cells) * cells + ii % cells
                    elif d < d2:
                        d2 = d
            row.append((math.sqrt(d1) / cs, math.sqrt(d2) / cs, best))
        rows.append(row)
    return rows


def _hash01(n):
    n = (n * 374761393 + 668265263) & 0xFFFFFFFF
    n = ((n ^ (n >> 13)) * 1274126177) & 0xFFFFFFFF
    return ((n ^ (n >> 16)) & 0xFFFF) / 65535.0


def _rgb(v, t=(1.0, 1.0, 1.0)):
    return (min(1.0, max(0.0, v * t[0])), min(1.0, max(0.0, v * t[1])), min(1.0, max(0.0, v * t[2])))


def _shade(h, S, k):
    """Prägung aus einem Höhenfeld (nahtlos): Licht von links oben, Hänge zur Lichtseite werden heller."""
    out = []
    for y in range(S):
        hm, hr, hp = h[(y - 1) % S], h[y], h[(y + 1) % S]
        row = []
        for x in range(S):
            d = (hr[(x + 1) % S] - hr[x - 1]) + (hp[x] - hm[x])
            row.append(min(1.55, max(0.5, 1.0 + k * d)))
        out.append(row)
    return out


def _finish(S, cols, h, k):
    """cols: Zeilen von RGB-Tupeln; h: Höhenfeld -> Farben * Prägung."""
    sh = _shade(h, S, k)
    return [[(min(1.0, c[0] * s), min(1.0, c[1] * s), min(1.0, c[2] * s)) for c, s in zip(cr, sr)]
            for cr, sr in zip(cols, sh)]


def _sstep(e0, e1, v):
    return _smooth01(min(1.0, max(0.0, (v - e0) / (e1 - e0))))


def _t_grass(S):
    patch, mid = _fbm(S, 11, 4, 4), _fbm(S, 12, 14, 3, 0.55)
    blade, fine = _fbm(S, 13, 4, 3, px=110, py=44), _fbm(S, 14, 70, 3, 0.6)
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        for x in range(S):
            p = patch[y][x]
            v = (0.88 + 0.38 * (p - 0.5) + 0.40 * (mid[y][x] - 0.5) + 0.30 * (blade[y][x] - 0.5)
                 + 0.22 * (fine[y][x] - 0.5))
            t = _sstep(0.30, 0.70, p)                    # satt-grün <-> leicht sonnig
            tint = (0.86 + 0.10 * t, 0.98 + 0.02 * t, 0.70 + 0.06 * t)
            crow.append(_rgb(v, tint))
            hrow.append(0.7 * blade[y][x] + 0.5 * fine[y][x])
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 1.2)


def _t_dirt(S):
    a, b, c = _fbm(S, 21, 4, 4), _fbm(S, 22, 30, 3, 0.55), _fbm(S, 23, 80, 2)
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        for x in range(S):
            peb = _sstep(0.60, 0.74, b[y][x])            # Kieselchen
            hole = _sstep(0.40, 0.26, b[y][x])
            v = (0.84 + 0.6 * (a[y][x] - 0.5) + 0.25 * (c[y][x] - 0.5)) * (1.0 + 0.2 * peb - 0.22 * hole)
            crow.append(_rgb(v, (1.0, 0.93 - 0.03 * peb, 0.84 - 0.05 * peb)))
            hrow.append(0.9 * peb - 0.5 * hole + 0.4 * c[y][x])
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 0.8)


def _t_sand(S):
    a, b = _fbm(S, 31, 4, 3), _fbm(S, 32, 60, 3, 0.6)
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        for x in range(S):
            rip = math.sin(2 * math.pi * (y * 7 / S + a[y][x] * 1.5))
            crow.append(_rgb(0.9 + 0.35 * (a[y][x] - 0.5) + 0.16 * (b[y][x] - 0.5) + 0.05 * rip, (1.0, 0.97, 0.9)))
            hrow.append(0.35 * rip + 0.6 * b[y][x])
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 0.8)


def _blocks(S, bw, bh, seed, mortar=0.5, var=0.18, bevel=0.1, tint=(1.0, 1.0, 1.0)):
    n1, n2, n3 = _fbm(S, seed, 6, 4), _fbm(S, seed + 1, 40, 3, 0.6), _fbm(S, seed + 2, 90, 2)
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        r, ly = y // bh, y % bh
        off = bw // 2 if r % 2 else 0
        for x in range(S):
            xo = (x + off) % S
            col, lx = xo // bw, xo % bw
            e = min(lx, ly, bw - 1 - lx, bh - 1 - ly)          # Abstand zum Fugenrand
            rise = _sstep(0.0, 4.0, e)                        # Stein steigt aus der Fuge
            if e < 2:
                v = mortar + 0.22 * (n2[y][x] - 0.5)
            else:
                v = (0.92 - var * _hash01(r * 131 + col * 7 + seed) + 0.5 * (n1[y][x] - 0.5)
                     + 0.22 * (n2[y][x] - 0.5) + 0.12 * (n3[y][x] - 0.5))
            crow.append(_rgb(v, tint))
            hrow.append(1.5 * rise + 0.5 * n2[y][x] + 0.3 * n3[y][x])
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 0.55)


def _t_stone(S):
    return _blocks(S, S // 4, S // 8, 41)


def _t_roof(S):
    n, n2 = _fbm(S, 51, 8, 3), _fbm(S, 52, 60, 2)
    bh = S // 8
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        r, ly = y // bh, y % bh
        off = (S // 8) if r % 2 else 0
        for x in range(S):
            xo = (x + off) % S
            lx = xo % (S // 4)
            v = (0.72 + 0.32 * ly / bh - 0.14 * _hash01(r * 17 + xo // (S // 4) + 3)
                 + 0.3 * (n[y][x] - 0.5) + 0.12 * (n2[y][x] - 0.5))
            if lx < 1 or ly >= bh - 2:
                v *= 0.62                                    # Fuge / Schatten unter der Ziegelreihe
            crow.append(_rgb(v))
            hrow.append(1.2 * ly / bh - (1.0 if lx < 2 else 0.0) + 0.3 * n2[y][x])
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 0.6)


def _t_cobble(S):
    vor = _voronoi(S, 7, 61)
    n, n2 = _fbm(S, 62, 12, 3), _fbm(S, 63, 70, 2)
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        for x in range(S):
            d1, d2, cid = vor[y][x]
            edge = d2 - d1
            dome = _sstep(0.0, 0.30, edge)
            v = 0.62 + 0.38 * _hash01(cid + 50) + 0.4 * (n[y][x] - 0.5) + 0.15 * (n2[y][x] - 0.5) - 0.12 * d1
            v *= 0.42 + 0.58 * min(1.0, edge / 0.22)
            crow.append(_rgb(v))
            hrow.append(2.0 * dome - 0.4 * d1 + 0.3 * n2[y][x])
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 0.5)


def _t_rock(S):
    vor = _voronoi(S, 5, 71)
    a, b, c = _fbm(S, 72, 5, 4), _fbm(S, 73, 32, 3, 0.6), _fbm(S, 74, 90, 2)
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        for x in range(S):
            d1, d2, cid = vor[y][x]
            crack = _sstep(0.10, 0.0, d2 - d1)
            v = (0.85 + 0.65 * (a[y][x] - 0.5) + 0.3 * (b[y][x] - 0.5) + 0.14 * (c[y][x] - 0.5)
                 + 0.12 * (_hash01(cid) - 0.5)) * (1.0 - 0.5 * crack)
            crow.append(_rgb(v, (1.0, 0.99, 0.96)))
            hrow.append(1.2 * a[y][x] + 0.8 * b[y][x] + 0.4 * c[y][x] - 1.4 * crack + 0.5 * _hash01(cid))
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 0.55)


def _t_wood(S):
    g, n = _fbm(S, 81, 3, 3, px=26, py=3), _fbm(S, 82, 6, 2)
    fine = _fbm(S, 83, 3, 2, px=120, py=6)
    pw = S // 8
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        for x in range(S):
            p = x // pw
            ring = math.sin(2 * math.pi * (x * 9 / S + g[y][x] * 2.5))
            v = (0.86 + 0.5 * (g[y][x] - 0.5) + 0.12 * (_hash01(p + 90) - 0.5) + 0.2 * (n[y][x] - 0.5)
                 + 0.06 * ring + 0.10 * (fine[y][x] - 0.5))
            gap = x % pw < 2
            if gap:
                v *= 0.5                                     # Fuge zwischen den Brettern
            crow.append(_rgb(v, (1.0, 0.93, 0.82)))
            hrow.append(0.5 * ring + 0.8 * fine[y][x] - (1.5 if gap else 0.0))
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 0.45)


def _t_bark(S):
    g, n = _fbm(S, 91, 3, 3, px=30, py=3), _fbm(S, 92, 8, 2)
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        for x in range(S):
            groove = _sstep(0.38, 0.22, g[y][x])
            crow.append(_rgb(0.8 + 0.8 * (g[y][x] - 0.5) + 0.3 * (n[y][x] - 0.5) - 0.25 * groove,
                             (1.0, 0.94, 0.86)))
            hrow.append(1.2 * g[y][x] - 1.2 * groove + 0.3 * n[y][x])
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 0.9)


def _t_leaves(S):
    a, b, c = _fbm(S, 101, 9, 3), _fbm(S, 102, 26, 3, 0.6), _fbm(S, 103, 5, 2)
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        for x in range(S):
            lo, hi = _sstep(0.38, 0.22, b[y][x]), _sstep(0.62, 0.78, b[y][x])
            v = (0.82 + 0.7 * (a[y][x] - 0.5) + 0.4 * (b[y][x] - 0.5)) * (1.0 - 0.32 * lo + 0.2 * hi)
            t = _sstep(0.3, 0.7, c[y][x])
            crow.append(_rgb(v, (0.84 + 0.12 * t, 1.0, 0.80 + 0.04 * t)))
            hrow.append(1.0 * hi - 1.0 * lo + 0.5 * b[y][x])
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 0.55)


def _t_plaster(S):
    a, b, c = _fbm(S, 111, 4, 3), _fbm(S, 112, 50, 3, 0.6), _fbm(S, 113, 2, 2, px=2, py=5)
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        for x in range(S):
            crow.append(_rgb(0.9 + 0.35 * (a[y][x] - 0.5) + 0.15 * (b[y][x] - 0.5)
                             - 0.18 * max(0.0, c[y][x] - 0.55), (1.0, 0.98, 0.94)))
            hrow.append(1.0 * b[y][x] + 0.3 * a[y][x])
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 0.55)


def _t_concrete(S):
    a, b = _fbm(S, 121, 6, 4), _fbm(S, 122, 60, 3, 0.6)
    cols, h = [], []
    for y in range(S):
        crow, hrow = [], []
        for x in range(S):
            pit = _sstep(0.74, 0.88, b[y][x])
            v = (0.88 + 0.45 * (a[y][x] - 0.5) + 0.2 * (b[y][x] - 0.5)) * (1.0 - 0.3 * pit)
            seam = x % (S // 2) < 1 or y % (S // 2) < 1
            if seam:
                v *= 0.68                                    # Plattenfuge
            crow.append(_rgb(v))
            hrow.append(0.8 * b[y][x] - 1.0 * pit - (1.5 if seam else 0.0))
        cols.append(crow)
        h.append(hrow)
    return _finish(S, cols, h, 0.5)


def _t_metal(S):
    br = _fbm(S, 131, 3, 3, px=3, py=60)
    n = _fbm(S, 132, 5, 2)
    h = S // 2
    out = []
    for y in range(S):
        row = []
        for x in range(S):
            v = 0.84 + 0.38 * (br[y][x] - 0.5) + 0.18 * (n[y][x] - 0.5)
            if x % h < 2 or y % h < 2:
                v *= 0.55                                    # Blechfuge
            elif x % h < 3 or y % h < 3:
                v *= 1.12
            # Nieten
            if (x % h in (6, h - 7)) and (y % 16 in (7, 8)) or (y % h in (6, h - 7)) and (x % 16 in (7, 8)):
                v *= 1.25
            row.append(_rgb(v, (0.97, 0.99, 1.02)))
        out.append(row)
    return out


def _t_cloth(S):
    n = _fbm(S, 141, 8, 2)
    return [[_rgb(0.86 + 0.09 * (1 if ((x // 2) + (y // 2)) % 2 else -1) + 0.3 * (n[y][x] - 0.5))
             for x in range(S)] for y in range(S)]


def _t_water(S):
    n = _fbm(S, 151, 6, 3)
    waves = ((3, 2, 0.0), (-2, 4, 1.7), (5, -1, 3.1), (1, 6, 0.6))
    out = []
    for y in range(S):
        row = []
        for x in range(S):
            s = 0.0
            for kx, ky, ph in waves:
                s += math.sin(2 * math.pi * (kx * x + ky * y) / S + ph)
            v = 0.78 + 0.07 * s + 0.2 * (n[y][x] - 0.5)
            if v > 1.0:
                v = 1.0 + (v - 1.0) * 0.5                    # Glanzlichter
            row.append(_rgb(v, (0.92, 0.98, 1.0)))
        out.append(row)
    return out


def _t_fire(S):
    a, b = _fbm(S, 161, 4, 4), _fbm(S, 162, 12, 2)
    return [[_rgb(0.62 + 0.9 * (a[y][x] - 0.5) + 0.5 * (b[y][x] - 0.5) + 0.3) for x in range(S)]
            for y in range(S)]


def _t_cloud(S):
    n = _fbm(S, 171, 3, 5, 0.55)
    out = []
    for y in range(S):
        row = []
        for x in range(S):
            v = n[y][x]
            a = _smooth01(min(1.0, max(0.0, (v - 0.46) / 0.26)))
            sh = 1.0 - 0.22 * _smooth01(min(1.0, max(0.0, (v - 0.55) / 0.35)))
            row.append((0.96 * sh, 0.97 * sh, 1.0 * sh, a * 0.92))
        out.append(row)
    return out


def _radial(S, power, peak=1.0, rgb=(1.0, 1.0, 1.0)):
    c = (S - 1) / 2.0
    out = []
    for y in range(S):
        row = []
        for x in range(S):
            d = math.hypot(x - c, y - c) / (S / 2.0)
            a = max(0.0, 1.0 - d) ** power * peak
            row.append((rgb[0], rgb[1], rgb[2], min(1.0, a)))
        out.append(row)
    return out


def _t_blob(S):
    return _radial(S, 1.6, 1.0)


def _t_glow(S):
    return _radial(S, 2.4, 1.0, (1.0, 0.95, 0.82))


def _t_edge(S):
    out = []
    for y in range(S):
        row = []
        v = min((y + 0.5) / S, 1 - (y + 0.5) / S) / 0.25
        for x in range(S):
            u = min((x + 0.5) / S, 1 - (x + 0.5) / S) / 0.25
            a = _smooth01(min(1.0, u)) * _smooth01(min(1.0, v))
            row.append((1.0, 1.0, 1.0, a ** 1.3))
        out.append(row)
    return out


def _t_vignette(S):
    c = (S - 1) / 2.0
    out = []
    for y in range(S):
        row = []
        for x in range(S):
            d = math.hypot(x - c, y - c) / (S / 2.0)
            row.append((0.0, 0.0, 0.05, 0.62 * _smooth01(min(1.0, max(0.0, (d - 0.62) / 0.55)))))
        out.append(row)
    return out


# Name -> (Auflösung, Maler, hat Alpha, kachelt, Meter pro Kachel)
TEXGEN = {
    "grass": (384, _t_grass, False, True, 5.0), "dirt": (256, _t_dirt, False, True, 4.0),
    "sand": (128, _t_sand, False, True, 4.0), "stone": (256, _t_stone, False, True, 4.0),
    "roof": (128, _t_roof, False, True, 3.0), "cobble": (256, _t_cobble, False, True, 3.0),
    "rock": (256, _t_rock, False, True, 3.0), "wood": (128, _t_wood, False, True, 3.0),
    "bark": (64, _t_bark, False, True, 1.6), "leaves": (96, _t_leaves, False, True, 1.5),
    "plaster": (256, _t_plaster, False, True, 3.0), "concrete": (128, _t_concrete, False, True, 4.0),
    "metal": (128, _t_metal, False, True, 2.0), "cloth": (32, _t_cloth, False, True, 0.4),
    "water": (128, _t_water, False, True, 6.0), "fire": (64, _t_fire, False, True, 3.0),
    "cloud": (128, _t_cloud, True, True, 200.0), "blob": (64, _t_blob, True, False, 1.0),
    "glow": (64, _t_glow, True, False, 1.0), "edge": (64, _t_edge, True, False, 1.0),
    "vignette": (96, _t_vignette, True, False, 1.0),
}
TILE = {k: v[4] for k, v in TEXGEN.items()}
_TEX_CACHE = {}
_STATE_CACHE = {}


def get_tex(name):
    """Textur (wird beim ersten Gebrauch berechnet). None, wenn es kein echtes Panda3D gibt."""
    if not REAL_PANDA or name is None or name not in TEXGEN:
        return None
    tex = _TEX_CACHE.get(name)
    if tex is None:
        S, fn, alpha, tile, _t = TEXGEN[name]
        rows = fn(S)
        img = PNMImage(S, S, 4 if alpha else 3)
        for y, row in enumerate(rows):
            for x, px in enumerate(row):
                if alpha:
                    img.setXelA(x, y, px[0], px[1], px[2], px[3])
                else:
                    img.setXel(x, y, px[0], px[1], px[2])
        tex = Texture(name)
        tex.load(img)
        tex.setMagfilter(Texture.FTLinear)
        tex.setMinfilter(Texture.FTLinearMipmapLinear if tile else Texture.FTLinear)
        try:
            tex.setAnisotropicDegree(8 if tile else 1)
        except Exception:
            pass
        if not tile:
            tex.setWrapU(Texture.WMClamp)
            tex.setWrapV(Texture.WMClamp)
        _TEX_CACHE[name] = tex
    return tex


def mat_state(name):
    """RenderState mit der Textur (oder None)."""
    st = _STATE_CACHE.get(name)
    if st is None:
        tex = get_tex(name)
        if tex is None:
            return None
        st = _STATE_CACHE[name] = RenderState.make(TextureAttrib.make(tex))
    return st


_MATC = {tuple(round(c, 3) for c in col): m for col, m in (
    (STONE, "stone"), (STONE_D, "stone"), (ROOF, "roof"), (PLASTER, "plaster"),
    (WOOD_F, "wood"), (COBBLE, "cobble"), (CONCRETE, "concrete"), (ROCK_C, "rock"), (SANDBAG, "cloth"))
    + tuple((c, "metal") for c in CONT_COLS)}


def mat_for_color(col):
    """Passendes Material zu einer Gebäudefarbe."""
    m = _MATC.get(tuple(round(c, 3) for c in col[:3]))
    if m:
        return m
    r, g, b = col[:3]
    if b > r + 0.03 and b >= g - 0.02:
        return "metal"
    if r > g * 1.25 and r > b * 1.5:
        return "roof" if r > 0.5 else "wood"
    if abs(r - g) < 0.06 and abs(g - b) < 0.08:
        return "stone" if (r + g + b) / 3 < 0.5 else "concrete"
    return "plaster"


# ------------------------------------------------------------ Polygon-Mesh
class Mesh:
    """Sammelt Dreiecke mit eingebackener Beleuchtung (flat shading) und automatischen Texturkoordinaten.
    Je Material ein Geom (ein Draw-Call pro Material); Vertexfarbe x Textur ergibt das Aussehen."""

    def __init__(self, alpha=1.0, lit=True):
        self.vdata = GeomVertexData("mesh", GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
        self.vw = GeomVertexWriter(self.vdata, "vertex")
        self.nw = GeomVertexWriter(self.vdata, "normal")
        self.cw = GeomVertexWriter(self.vdata, "color")
        self.tw = GeomVertexWriter(self.vdata, "texcoord")
        self.prims = {}
        self.n = 0
        self.alpha = alpha
        self.lit = lit
        self.mat = None                 # aktuelles Material für alle folgenden Dreiecke

    def tri(self, a, b, c, col, ref=None, vk=None, mat=None, uv=None, nd=None):
        """Dreieck. Mit ref (Punkt 'innen/unten') zeigt die Vorderseite automatisch vom Punkt weg.
        col: eine Farbe oder drei (je Ecke); vk: Helligkeit je Ecke (Verdunklung nahe am Boden);
        uv: Texturkoordinaten je Ecke (sonst automatisch aus der Lage); nd: n.Sonne je Ecke (weiche Beleuchtung)."""
        cols = list(col) if isinstance(col[0], (tuple, list)) else [col, col, col]
        vk = list(vk) if (vk and self.lit) else None
        uv = list(uv) if uv else None
        nd = list(nd) if nd else None
        n = cross(sub(b, a), sub(c, a))
        if ref is not None:
            cen = ((a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3, (a[2] + b[2] + c[2]) / 3)
            if dot(n, sub(cen, ref)) < 0:
                b, c = c, b
                n = (-n[0], -n[1], -n[2])
                cols[1], cols[2] = cols[2], cols[1]
                for lst in (vk, uv, nd):
                    if lst:
                        lst[1], lst[2] = lst[2], lst[1]
        n = norm(n)
        mat = mat or self.mat
        pts = (a, b, c)
        if uv is None:
            T = TILE.get(mat, 4.0)
            ax, ay, az = abs(n[0]), abs(n[1]), abs(n[2])
            i, j = (0, 1) if (az >= ax and az >= ay) else ((1, 2) if ax >= ay else (0, 2))
            uv = [(p[i] / T, p[j] / T) for p in pts]
        d0 = max(0.0, dot(n, SUN))
        for k, p in enumerate(pts):
            cc = cols[k]
            if self.lit:
                d = max(0.0, nd[k]) if nd else d0
                kd = DIFFUSE * d
                f = vk[k] if vk else 1.0              # warmes Sonnenlicht, kühles Umgebungslicht
                fr, fg, fb = (AMBIENT * 0.94 + kd * 1.07) * f, (AMBIENT + kd) * f, (AMBIENT * 1.07 + kd * 0.9) * f
            else:
                fr = fg = fb = 1.0
            self.vw.addData3(*p)
            self.nw.addData3(*n)
            self.cw.addData4(min(1.0, cc[0] * fr), min(1.0, cc[1] * fg), min(1.0, cc[2] * fb),
                             cc[3] if len(cc) > 3 else self.alpha)
            self.tw.addData2(*uv[k])
        prim = self.prims.get(mat)
        if prim is None:
            prim = self.prims[mat] = GeomTriangles(Geom.UHStatic)
        prim.addVertices(self.n, self.n + 1, self.n + 2)
        self.n += 3

    def node(self, name):
        gn = GeomNode(name)
        for mat, prim in self.prims.items():
            geom = Geom(self.vdata)
            geom.addPrimitive(prim)
            st = mat_state(mat)
            if st is not None:
                gn.addGeom(geom, st)
            else:
                gn.addGeom(geom)
        return gn


def mix(a, b, t):
    return tuple(x * (1 - t) + y * t for x, y in zip(a, b))


def ring(cx, cy, z, r, sides, rng, jitter):
    pts = []
    for i in range(sides):
        a = 2 * math.pi * i / sides
        rr = r * (1 + rng.uniform(-jitter, jitter))
        pts.append((cx + math.cos(a) * rr, cy + math.sin(a) * rr, z))
    return pts


def cone(m, cx, cy, z0, r, h, sides, col, rng, jitter=0.1):
    apex = (cx + rng.uniform(-0.1, 0.1), cy + rng.uniform(-0.1, 0.1), z0 + h)
    rg = ring(cx, cy, z0, r, sides, rng, jitter)
    ref = (cx, cy, z0 + h * 0.3)
    for i in range(sides):
        m.tri(rg[i], rg[(i + 1) % sides], apex, jc(col, rng), ref, vk=(0.72, 0.72, 1.0))


def prism(m, cx, cy, z0, r, h, sides, col, rng, taper=1.0):
    bot = ring(cx, cy, z0, r, sides, rng, 0.05)
    top = [(cx + (p[0] - cx) * taper, cy + (p[1] - cy) * taper, z0 + h) for p in bot]
    ref = (cx, cy, z0 + h / 2)
    for i in range(sides):
        j = (i + 1) % sides
        c = jc(col, rng, 0.05)
        m.tri(bot[i], bot[j], top[j], c, ref, vk=(0.62, 0.62, 1.0))
        m.tri(bot[i], top[j], top[i], c, ref, vk=(0.62, 1.0, 1.0))


def box(m, cx, cy, cz, sx, sy, sz, col, rng=None, mat=None, ao=True):
    """Quader um (cx,cy,cz) mit den Kantenlängen sx,sy,sz. Grosse Quader werden zum Boden hin
    abgedunkelt (Ambient Occlusion)."""
    hx, hy, hz = sx / 2, sy / 2, sz / 2
    x0, x1, y0, y1, z0, z1 = cx - hx, cx + hx, cy - hy, cy + hy, cz - hz, cz + hz
    ref = (cx, cy, cz)
    use_ao = ao and m.lit and sz >= 1.0
    if use_ao:
        bh = 1.3 if sz > 2.2 else sz
        levels = [(z0, 0.62), (z0 + bh, 1.0)] + ([(z1, 1.0)] if sz > 2.2 else [])
    else:
        levels = [(z0, 1.0), (z1, 1.0)]
    for (xa, ya), (xb, yb) in (((x0, y0), (x1, y0)), ((x1, y0), (x1, y1)), ((x1, y1), (x0, y1)), ((x0, y1), (x0, y0))):
        col2 = jc(col, rng, 0.04) if rng else col
        for (za, ka), (zb, kb) in zip(levels, levels[1:]):
            p = ((xa, ya, za), (xb, yb, za), (xb, yb, zb), (xa, ya, zb))
            m.tri(p[0], p[1], p[2], col2, ref, vk=(ka, ka, kb), mat=mat)
            m.tri(p[0], p[2], p[3], col2, ref, vk=(ka, kb, kb), mat=mat)
    col2 = jc(col, rng, 0.04) if rng else col
    for z, k in ((z1, 1.0), (z0, 0.6)):
        p = ((x0, y0, z), (x1, y0, z), (x1, y1, z), (x0, y1, z))
        m.tri(p[0], p[1], p[2], col2, ref, mat=mat, vk=(k, k, k))
        m.tri(p[0], p[2], p[3], col2, ref, mat=mat, vk=(k, k, k))


def blob(m, cx, cy, cz, rx, ry, rz, col, rng, jitter=0.2, subdiv=1, moss=0.0, mat=None):
    """Unregelmäßiger Klumpen (Fels, Laubkrone): unterteiltes Oktaeder. Unten dunkler (AO),
    moss: nach oben zeigende Flächen werden grün."""
    verts = [(1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)]
    faces = [(0, 2, 4), (2, 1, 4), (1, 3, 4), (3, 0, 4), (2, 0, 5), (1, 2, 5), (3, 1, 5), (0, 3, 5)]
    for _ in range(subdiv):
        cache, new = {}, []

        def mid(i, j):
            key = (min(i, j), max(i, j))
            if key not in cache:
                verts.append(norm(add(verts[i], verts[j])))
                cache[key] = len(verts) - 1
            return cache[key]

        for a, b, c in faces:
            ab, bc, ca = mid(a, b), mid(b, c), mid(c, a)
            new += [(a, ab, ca), (b, bc, ab), (c, ca, bc), (ab, bc, ca)]
        faces = new
    pts = []
    for v in verts:
        j = 1 + rng.uniform(-jitter, jitter)
        pts.append((cx + v[0] * rx * j, cy + v[1] * ry * j, cz + v[2] * rz * j))
    ref = (cx, cy, cz)
    for a, b, c in faces:
        cc = jc(col, rng, 0.05)
        if moss > 0:
            nrm = norm(cross(sub(pts[b], pts[a]), sub(pts[c], pts[a])))
            if dot(nrm, sub(pts[a], ref)) < 0:
                nrm = (-nrm[0], -nrm[1], -nrm[2])
            if nrm[2] > 0.55:
                cc = mix(cc, (0.22, 0.40, 0.14), moss * smoothstep(0.55, 0.9, nrm[2]))
        vk = tuple(0.66 + 0.34 * (verts[i][2] * 0.5 + 0.5) for i in (a, b, c))
        m.tri(pts[a], pts[b], pts[c], cc, ref, vk=vk, mat=mat)


def decal(mesh, world, xs, ys, us, vs, alpha, mat, lift=0.07):
    """Auf das Gelände gelegtes Raster (Schatten, Verdunklung am Gebäudefuss)."""
    g = [[(x, y, world.surface_height(x, y) + lift) for x in xs] for y in ys]
    col = (0.0, 0.0, 0.0, alpha)
    for j in range(len(ys) - 1):
        for i in range(len(xs) - 1):
            p00, p10, p11, p01 = g[j][i], g[j][i + 1], g[j + 1][i + 1], g[j + 1][i]
            ref = (p00[0], p00[1], min(p00[2], p11[2]) - 5.0)
            mesh.tri(p00, p10, p11, col, ref, mat=mat, uv=((us[i], vs[j]), (us[i + 1], vs[j]), (us[i + 1], vs[j + 1])))
            mesh.tri(p00, p11, p01, col, ref, mat=mat, uv=((us[i], vs[j]), (us[i + 1], vs[j + 1]), (us[i], vs[j + 1])))


def decal_disc(mesh, world, cx, cy, r, alpha):
    xs = [cx - r + 2 * r * i / 4 for i in range(5)]
    ys = [cy - r + 2 * r * i / 4 for i in range(5)]
    us = [i / 4 for i in range(5)]
    decal(mesh, world, xs, ys, us, us, alpha, "blob")


def _axis(a0, a1, m, seg=4.0):
    """Stützstellen von a0-m bis a1+m (innen alle seg Meter) und passende Texturkoordinaten."""
    n = max(1, int(math.ceil((a1 - a0) / seg)))
    pos = [a0 - m] + [a0 + (a1 - a0) * i / n for i in range(n + 1)] + [a1 + m]
    uvs = [0.0] + [0.25 + 0.5 * i / n for i in range(n + 1)] + [1.0]
    return pos, uvs


def decal_rect(mesh, world, x0, y0, x1, y1, m, alpha):
    xs, us = _axis(x0, x1, m)
    ys, vs = _axis(y0, y1, m)
    decal(mesh, world, xs, ys, us, vs, alpha, "edge")


_MC_TEX = {}


def mc_texture(name, w, h, alpha, data):
    """Minecraft-Textur: scharfe Pixel (nearest), Kacheln wiederholen sich (grosse Flächen sind zusammengefasst)."""
    tex = _MC_TEX.get(name)
    if tex is None:
        img = PNMImage(w, h, 4)
        k = 0
        for y in range(h):
            for x in range(w):
                img.setXelA(x, y, data[k] / 255.0, data[k + 1] / 255.0, data[k + 2] / 255.0, data[k + 3] / 255.0)
                k += 4
        tex = Texture(name)
        tex.load(img)
        tex.setMagfilter(Texture.FTNearest)
        tex.setMinfilter(Texture.FTNearestMipmapLinear)
        tex.setWrapU(Texture.WMRepeat)
        tex.setWrapV(Texture.WMRepeat)
        _MC_TEX[name] = tex
    return tex


def build_mc_scene(world):
    """Minecraft-Karte: eine Geometrie je Textur. Beleuchtung (Licht, Schatten, Ambient Occlusion) steckt in den
    Vertexfarben. Gibt dieselben vier Rückgaben wie build_scene: Land (undurchsichtig + Ausschnitt), Wasser
    (durchscheinend), Zone, extra."""
    mc = world.mc
    meta = mc["meta"]
    ps, us = 1.0 / meta["pscale"], 1.0 / meta["uvscale"]
    land, water = GeomNode("mc_land"), GeomNode("mc_water")
    for g in mc["groups"]:
        w, h, a, data = mc["tex"][g["tex"]]
        tex = mc_texture(g["tex"], w, h, a, data)
        kind = g["kind"]
        attribs = TextureAttrib.make(tex)
        st = RenderState.make(attribs)
        if kind == 1:                                       # Ausschnitt (Laub, Glas, Fackeln): beidseitig, harte Kante
            st = st.setAttrib(TransparencyAttrib.make(TransparencyAttrib.MBinary))
            st = st.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))
        elif kind == 2:                                     # Wasser, Portal
            st = st.setAttrib(CullFaceAttrib.make(CullFaceAttrib.MCullNone))
        vdata = GeomVertexData("mc_" + g["tex"], GeomVertexFormat.getV3n3c4t2(), Geom.UHStatic)
        vw = GeomVertexWriter(vdata, "vertex")
        nw = GeomVertexWriter(vdata, "normal")
        cw = GeomVertexWriter(vdata, "color")
        tw = GeomVertexWriter(vdata, "texcoord")
        prim = GeomTriangles(Geom.UHStatic)
        P, UV, C = g["P"], g["UV"], g["C"]
        n = 0
        for q in range(g["n"]):
            for j in range(4):
                i3 = q * 12 + j * 3
                vw.addData3(P[i3] * ps, P[i3 + 1] * ps, P[i3 + 2] * ps)
                nw.addData3(0.0, 0.0, 1.0)
                i4 = q * 16 + j * 4
                cw.addData4(C[i4] / 255.0, C[i4 + 1] / 255.0, C[i4 + 2] / 255.0, C[i4 + 3] / 255.0)
                i2 = q * 8 + j * 2
                tw.addData2(UV[i2] * us, 1.0 - UV[i2 + 1] * us)
            prim.addVertices(n, n + 1, n + 2)
            prim.addVertices(n, n + 2, n + 3)
            n += 4
        geom = Geom(vdata)
        geom.addPrimitive(prim)
        (water if kind == 2 else land).addGeom(geom, st)
    empty = GeomNode("leer")
    return land, water, [], [GeomNode("leer2"), [], GeomNode("leer3"), empty]


def build_scene(world):
    """Baut Gelände, Bäume, Felsen, Gebäude (ein Mesh) und das Wasser (zweites Mesh).
    extra = [Lampen, Gras, Schattenflächen, zweite Wasserschicht]."""
    rng = random.Random(world.seed + 1)
    m = Mesh()
    ponds = world.ponds
    mtn = getattr(world, "mtn", False)
    shc = {}

    def sh(x, y):                                   # Geländehöhe mit Zwischenspeicher (Gitterpunkte kommen 4x vor)
        key = (x, y)
        v = shc.get(key)
        if v is None:
            v = shc[key] = world.surface_height(x, y)
        return v

    snc = {}

    def snormal(x, y):
        key = (round(x, 2), round(y, 2))
        v = snc.get(key)
        if v is None:
            e = 1.5
            v = norm((sh(x - e, y) - sh(x + e, y), sh(x, y - e) - sh(x, y + e), 2 * e))
            snc[key] = v
        return v

    def sand_w(x, y):
        s = 0.0
        for px, py, r in ponds:
            s = max(s, 1.0 - smoothstep(0.85, 1.9, math.hypot(x - px, y - py) / r))
        return s

    def terrain_col(x, y, z):
        t = 0.5 + 0.5 * math.sin(x * 0.11) * math.cos(y * 0.09)
        u = 0.5 + 0.5 * math.sin(x * 0.43 + 1.3) * math.sin(y * 0.37 + 0.4)
        dry = smoothstep(0.35, 0.9, 0.5 + 0.5 * math.sin(x * 0.045 + 2.0) * math.sin(y * 0.05 - 1.0))
        col = (0.26 + 0.08 * t + 0.03 * u, 0.50 + 0.10 * t - 0.03 * u, 0.20 + 0.05 * t)
        col = mix(col, (0.52, 0.50, 0.25), dry * 0.40)                    # trockene Flecken
        col = mix(col, (0.45, 0.52, 0.30), smoothstep(3.0, 9.0, z) * 0.35)  # Hügelkuppen
        col = mix(col, (0.74, 0.67, 0.47), sand_w(x, y))                  # Sandufer
        if z < WATER_LEVEL + 0.4:
            col = mix(col, (0.45, 0.40, 0.28), 0.6)                       # nasser Boden
        if mtn:
            mz = mountain(x, y)
            if mz > 2.0:                                                  # Gebirge: Geröll, Fels, oben Schnee
                g = 0.47 + 0.05 * math.sin(x * 0.3 + y * 0.17) + 0.04 * u
                col = mix(col, (g * 1.02, g * 0.97, g * 0.88), smoothstep(2.0, 12.0, mz))
                col = mix(col, (0.92, 0.93, 0.96), smoothstep(46.0, 58.0, z + 6.0 * t))
        return col

    def rock_w(x, y):
        return smoothstep(5.0, 12.0, mountain(x, y)) if mtn else 0.0

    # --- Gelände
    marg = 72.0 if mtn else MARGIN                  # Standardkarte: Gebirge auch hinter dem Rand zeigen
    n0 = int(-marg // CELL)
    n1 = int((WORLD + marg) // CELL) + 1

    def cell(x0, y0, x1, y1, par):
        if world.voids and world.in_void((x0 + x1) / 2, (y0 + y1) / 2):
            return                                  # Tunneleingang: hier ist das Gelände offen
        p00 = (x0, y0, sh(x0, y0))
        p10 = (x1, y0, sh(x1, y0))
        p11 = (x1, y1, sh(x1, y1))
        p01 = (x0, y1, sh(x0, y1))
        tris = ((p00, p10, p11), (p00, p11, p01)) if par % 2 else ((p00, p10, p01), (p10, p11, p01))
        for a, b, c in tris:
            n = norm(cross(sub(b, a), sub(c, a)))
            if n[2] < 0:
                b, c = c, b
                n = (-n[0], -n[1], -n[2])
            cx_, cy_ = (a[0] + b[0] + c[0]) / 3, (a[1] + b[1] + c[1]) / 3
            floor = None
            for fx0, fy0, fx1, fy1, fc in world.floors:    # Hof und Fussböden in Gebäuden
                if fx0 <= cx_ <= fx1 and fy0 <= cy_ <= fy1:
                    floor = fc
            if floor is not None:
                m.tri(a, b, c, jc(floor, rng, 0.04), mat=mat_for_color(floor))
                continue
            k = smoothstep(0.86, 0.72, n[2]) if n[2] < 0.86 else 0.0      # steil: Erde/Fels
            cols, nds = [], []
            for p in (a, b, c):
                col = terrain_col(p[0], p[1], p[2])
                if k > 0:
                    col = mix(col, (0.50, 0.44, 0.36), k)
                cols.append(jc(col, rng, 0.03))
                sn = snormal(p[0], p[1])
                nb = norm((n[0] * 0.55 + sn[0] * 0.45, n[1] * 0.55 + sn[1] * 0.45, n[2] * 0.55 + sn[2] * 0.45))
                nds.append(dot(nb, SUN))
            sw = (sand_w(a[0], a[1]) + sand_w(b[0], b[1]) + sand_w(c[0], c[1])) / 3
            mat = ("rock" if rock_w(cx_, cy_) > 0.5 else "dirt") if k > 0.5 else ("sand" if sw > 0.6 else "grass")
            if mtn and mat == "grass" and rock_w(cx_, cy_) > 0.6:
                mat = "rock"
            m.tri(a, b, c, cols, mat=mat, nd=nds)

    for iy in range(n0, n1):
        for ix in range(n0, n1):
            x0, y0 = ix * CELL, iy * CELL
            x1, y1 = x0 + CELL, y0 + CELL
            if any(vx0 < x1 and vx1 > x0 and vy0 < y1 and vy1 > y0 for vx0, vy0, vx1, vy1 in world.voids):
                k = int(round(CELL / 0.2))          # Zellen an Eingängen fein unterteilen
                for j in range(k):
                    for i in range(k):
                        cell(x0 + CELL * i / k, y0 + CELL * j / k, x0 + CELL * (i + 1) / k,
                             y0 + CELL * (j + 1) / k, ix + iy)
            else:
                cell(x0, y0, x1, y1, ix + iy)

    shadows = Mesh(lit=False)

    # --- Bäume und Felsen
    for p in world.props:
        if p.kind == "rock":
            r = p.base_r
            g = rng.uniform(0.46, 0.62)
            blob(m, p.x, p.y, p.z + r * 0.25, r, r * rng.uniform(0.8, 1.2), r * 0.7,
                 (g, g, g + 0.03), rng, jitter=0.25, subdiv=2, moss=0.55, mat="rock")
            decal_disc(shadows, world, p.x - SUN[0] * r * 0.3, p.y - SUN[1] * r * 0.3, r * 1.5, 0.42)
        elif p.kind == "tree":
            r = p.base_r
            h = rng.uniform(5.0, 9.0)
            trunk_h = h * 0.3
            green = (rng.uniform(0.12, 0.22), rng.uniform(0.38, 0.52), rng.uniform(0.15, 0.25))
            if rng.random() < 0.12:                                    # gelegentlich Herbstlaub
                green = (rng.uniform(0.55, 0.7), rng.uniform(0.38, 0.5), rng.uniform(0.1, 0.16))
            prism(m, p.x, p.y, p.z - 0.3, 0.3, trunk_h + 0.5, 7, (0.46, 0.33, 0.22), rng, taper=0.8)
            prism(m, p.x, p.y, p.z - 0.3, 0.52, 0.55, 7, (0.42, 0.30, 0.20), rng, taper=0.6)   # Wurzelansatz
            m.mat = "leaves"
            if rng.random() < 0.6:       # Nadelbaum: vier gestapelte Kegel
                for i in range(4):
                    z0 = p.z + trunk_h * 0.65 + i * h * 0.17
                    cone(m, p.x, p.y, z0, r * (1.05 - 0.2 * i), h * 0.34, 9,
                         (green[0] * (1 - 0.08 * i), green[1] * (1 + 0.07 * i), green[2]), rng)
            else:                        # Laubbaum: Hauptkrone mit zwei Nebenkronen
                cz = p.z + trunk_h + r * 0.9
                col = (green[0] + 0.12, green[1] + 0.06, green[2])
                blob(m, p.x, p.y, cz, r * 1.1, r * 1.1, r * 1.0, col, rng, jitter=0.16)
                for _ in range(2):
                    a = rng.uniform(0, 2 * math.pi)
                    blob(m, p.x + math.cos(a) * r * 0.7, p.y + math.sin(a) * r * 0.7,
                         cz - r * 0.15 + rng.uniform(0, r * 0.4), r * 0.7, r * 0.7, r * 0.65,
                         jc(col, rng, 0.06), rng, jitter=0.18)
            m.mat = None
            decal_disc(shadows, world, p.x - SUN[0] * h * 0.25, p.y - SUN[1] * h * 0.25, r * 1.35 + h * 0.18, 0.40)

    # --- Büsche und Gras (nur Dekoration, ohne Kollision)
    gcells = {}

    def gm_at(x, y):                                  # Gras in 25-m-Zellen: ausserhalb des Bildes wird es nicht gezeichnet
        k = (int(x // 25), int(y // 25))
        if k not in gcells:
            gcells[k] = Mesh(lit=False)
        return gcells[k]

    def free_spot(x, y, clear):
        if not (2 < x < WORLD - 2 and 2 < y < WORLD - 2):
            return None
        if world.voids and world.in_void(x, y):
            return None
        z = world.surface_height(x, y)
        if z < WATER_LEVEL + 0.5 or snormal(x, y)[2] < 0.93 or sand_w(x, y) > 0.35:
            return None
        if any(fx0 - clear <= x <= fx1 + clear and fy0 - clear <= y <= fy1 + clear
               for fx0, fy0, fx1, fy1, _fc in world.floors):
            return None
        if any(True for _b in world.boxes_near(x - clear, y - clear, x + clear, y + clear)):
            return None
        return z

    nb = 0
    for _ in range(300):
        if nb >= 40:
            break
        x, y = rng.uniform(0, WORLD), rng.uniform(0, WORLD)
        z = free_spot(x, y, 2.0)
        if z is None or any(math.hypot(x - q.x, y - q.y) < q.base_r + 1.5 for q in world.props):
            continue
        nb += 1
        r = rng.uniform(0.45, 0.8)
        g = rng.uniform(0.0, 0.08)
        m.mat = "leaves"
        blob(m, x, y, z + r * 0.45, r, r, r * 0.7, (0.16 + g, 0.40 + g, 0.15), rng, jitter=0.2)
        m.mat = None
        decal_disc(shadows, world, x - SUN[0] * r * 0.3, y - SUN[1] * r * 0.3, r * 1.4, 0.35)

    ntuft = 0
    for _ in range(9000):
        if ntuft >= 3000:
            break
        x, y = rng.uniform(0, WORLD), rng.uniform(0, WORLD)
        z = free_spot(x, y, 0.4)
        if z is None:
            continue
        ntuft += 1
        base = terrain_col(x, y, z)
        flower = rng.random() < 0.05
        for _b in range(3):
            a = rng.uniform(0, 2 * math.pi)
            bx, by = x + rng.uniform(-0.15, 0.15), y + rng.uniform(-0.15, 0.15)
            h = rng.uniform(0.3, 0.65)
            w = 0.045
            lean = rng.uniform(0.05, 0.22)
            tip = (bx + math.cos(a) * lean, by + math.sin(a) * lean, z + h)
            dx, dy = -math.sin(a) * w, math.cos(a) * w
            lo = tuple(c * 0.62 for c in base)
            hi = tuple(min(1.0, c * 1.25 + 0.04) for c in base)
            gm_at(x, y).tri((bx - dx, by - dy, z - 0.03), (bx + dx, by + dy, z - 0.03), tip, (lo, lo, hi))
        if flower:
            fc = rng.choice(((1.0, 1.0, 0.95), (1.0, 0.85, 0.2), (0.95, 0.3, 0.35), (0.7, 0.55, 0.95)))
            fz = z + 0.42
            s = 0.07
            for sx, sy in ((1, 0), (0, 1), (-1, 0), (0, -1)):
                gm_at(x, y).tri((x, y, fz + 0.04), (x + sx * s, y + sy * s, fz), (x - sy * s, y + sx * s, fz), fc)

    # --- Gebäude (Burg, Türme, Häuser, Treppen, Deckung)
    for b in world.boxes:
        cx_, cy_ = (b.x0 + b.x1) / 2, (b.y0 + b.y1) / 2
        box(m, cx_, cy_, (b.z0 + b.z1) / 2, b.x1 - b.x0, b.y1 - b.y0, b.z1 - b.z0, b.col, rng,
            mat=mat_for_color(b.col))
        dx, dy = b.x1 - b.x0, b.y1 - b.y0
        gz = world.surface_height(cx_, cy_)
        if b.z1 > 0.8 and b.z0 <= gz + 0.6 and max(dx, dy) >= 3.0 and min(dx, dy) >= 0.4 and b.z1 - gz >= 1.8:
            decal_rect(shadows, world, b.x0, b.y0, b.x1, b.y1, 1.3, 0.5)     # Verdunklung am Gebäudefuss

    # --- Tunnel: nur zur Darstellung (Boden, Lampen, Eingangsrahmen). Die Treppenschächte sind offene Löcher.
    for x0, y0, x1, y1, z0, z1, col, lit in world.decor:
        if lit:
            box(m, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0, col, rng,
                mat="concrete")
    lamps = Mesh(lit=False)
    for x0, y0, x1, y1, z0, z1, col, lit in world.decor:
        if not lit:
            box(lamps, (x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2, x1 - x0, y1 - y0, z1 - z0, col)

    # --- Wasser: Mitte tief, zum Ufer hin heller und durchsichtiger (Schaum), zwei Wellenschichten
    w = Mesh(alpha=0.80)
    w2 = Mesh(alpha=0.30)
    w.mat = w2.mat = "water"
    rings = ((0.0, (0.10, 0.34, 0.58, 0.90)), (0.6, (0.16, 0.42, 0.68, 0.86)),
             (0.85, (0.62, 0.80, 0.88, 0.60)), (1.3, (0.75, 0.88, 0.92, 0.0)))
    for px, py, r in ponds:
        pts = [ring(px, py, WATER_LEVEL, max(r * f, 0.01), 20, random.Random(int(px * 7 + py)), 0.0)
               for f, _c in rings]
        below = (px, py, WATER_LEVEL - 1)
        for k in range(len(rings) - 1):
            for i in range(20):
                j = (i + 1) % 20
                ca, cb = rings[k][1], rings[k + 1][1]
                if k == 0:
                    w.tri((px, py, WATER_LEVEL), pts[1][i], pts[1][j], (ca, cb, cb), below)
                else:
                    w.tri(pts[k][i], pts[k + 1][i], pts[k + 1][j], (ca, cb, cb), below)
                    w.tri(pts[k][i], pts[k + 1][j], pts[k][j], (ca, cb, ca), below)
        cc = (0.85, 0.95, 1.0, 0.22)
        for i in range(20):
            j = (i + 1) % 20
            w2.tri((px, py, WATER_LEVEL + 0.03), pts[2][i], pts[2][j], cc, below)
            w2.tri(pts[2][i], pts[3][i], pts[3][j], (cc, (cc[0], cc[1], cc[2], 0.0), (cc[0], cc[1], cc[2], 0.0)), below)
            w2.tri(pts[2][i], pts[3][j], pts[2][j], (cc, (cc[0], cc[1], cc[2], 0.0), cc), below)
    # --- King-of-the-Hill-Zone: gelber Ring mit Pfosten und leicht getönter Boden
    zone = []
    if world.mode == "koth":
        fill, edge = Mesh(alpha=0.16, lit=False), Mesh(alpha=0.9, lit=False)
        n, zc = 72, (CENTER, CENTER)
        below = (CENTER, CENTER, -5.0)

        def zp(r, a, z=0.08):
            return (zc[0] + math.cos(a) * r, zc[1] + math.sin(a) * r, z)

        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            fill.tri((zc[0], zc[1], 0.07), zp(ZONE_R, a0, 0.07), zp(ZONE_R, a1, 0.07),
                     (1.0, 0.85, 0.2), ref=below)
            for qa, qb, qc in ((zp(ZONE_R - 0.5, a0), zp(ZONE_R, a0), zp(ZONE_R, a1)),
                               (zp(ZONE_R - 0.5, a0), zp(ZONE_R, a1), zp(ZONE_R - 0.5, a1))):
                edge.tri(qa, qb, qc, (1.0, 0.85, 0.15), ref=below)
        for i in range(8):
            px, py, _pz = zp(ZONE_R - 0.25, 2 * math.pi * i / 8)
            box(edge, px, py, 1.6, 0.25, 0.25, 3.2, (1.0, 0.85, 0.15))
        zone = [fill.node("zone_fill"), edge.node("zone_ring")]
    extra = [lamps.node("lamps"), [c.node("grass") for c in gcells.values()], shadows.node("decals"), w2.node("water2")]
    return m.node("land"), w.node("water"), zone, extra


# ------------------------------------------------------------ Himmel
SKY_ZENITH = (0.22, 0.45, 0.85)
SKY_RADIUS = 320.0


def sky_color(d):
    """Himmelsfarbe in Richtung d (normiert): Dunst am Horizont, tiefes Blau oben, warmer Schein zur Sonne."""
    t = max(0.0, d[2]) ** 0.55
    col = mix(SKY, SKY_ZENITH, t)
    glow = max(0.0, dot(d, SUN)) ** 6
    return mix(col, (1.0, 0.9, 0.7), min(0.55, glow * 0.55 * (1.0 - 0.6 * t)))


def build_sky():
    """Gibt (Kuppel, Wolken, Sonne-Glanz, Sonne-Kern) als Knoten zurück: Mesh-Knoten und zwei Karten."""
    dm = Mesh(lit=False)
    elev = (-25, 0, 5, 12, 22, 36, 54, 90)
    seg = 28
    rg = []
    for e in elev:
        er = math.radians(e)
        row = []
        for i in range(seg if e < 90 else 1):
            a = 2 * math.pi * i / seg
            d = (math.cos(er) * math.cos(a), math.cos(er) * math.sin(a), math.sin(er))
            row.append((tuple(c * SKY_RADIUS for c in d), sky_color(d)))
        rg.append(row)
    for k in range(len(elev) - 1):
        lo, hi = rg[k], rg[k + 1]
        for i in range(seg):
            j = (i + 1) % seg
            if len(hi) == 1:
                dm.tri(lo[i][0], lo[j][0], hi[0][0], (lo[i][1], lo[j][1], hi[0][1]))
            else:
                dm.tri(lo[i][0], lo[j][0], hi[j][0], (lo[i][1], lo[j][1], hi[j][1]))
                dm.tri(lo[i][0], hi[j][0], hi[i][0], (lo[i][1], hi[j][1], hi[i][1]))
    cm = Mesh(lit=False)
    cm.mat = "cloud"
    radii = (0, 70, 140, 230, 330, 420)
    fade = (1.0, 1.0, 0.85, 0.55, 0.22, 0.0)
    cz, cseg = 75.0, 24
    prs = []
    for r in radii:
        prs.append([(r * math.cos(2 * math.pi * i / cseg), r * math.sin(2 * math.pi * i / cseg), cz)
                    for i in range(cseg if r else 1)])
    for k in range(len(radii) - 1):
        lo, hi = prs[k], prs[k + 1]
        for i in range(cseg):
            j = (i + 1) % cseg
            ca, cb = (1, 1, 1, fade[k]), (1, 1, 1, fade[k + 1])
            uv = lambda p: (p[0] / TILE["cloud"], p[1] / TILE["cloud"])    # noqa: E731
            if len(lo) == 1:
                cm.tri(lo[0], hi[i], hi[j], (ca, cb, cb), uv=(uv(lo[0]), uv(hi[i]), uv(hi[j])))
            else:
                cm.tri(lo[i], hi[i], hi[j], (ca, cb, cb), uv=(uv(lo[i]), uv(hi[i]), uv(hi[j])))
                cm.tri(lo[i], hi[j], lo[j], (ca, cb, ca), uv=(uv(lo[i]), uv(hi[j]), uv(lo[j])))
    return dm.node("sky_dome"), cm.node("sky_clouds")


# ------------------------------------------------------- Modelle: Mobs, Waffen
MOB_LOOK = {
    "grunt": dict(skin=(0.35, 0.62, 0.28), cloth=(0.45, 0.32, 0.18), eye=(1.0, 0.9, 0.2),
                  w=0.5, horns=False),
    "brute": dict(skin=(0.62, 0.30, 0.25), cloth=(0.25, 0.22, 0.24), eye=(1.0, 0.35, 0.1),
                  w=0.72, horns=True),
    "huntress": dict(skin=(0.88, 0.74, 0.66), cloth=(0.62, 0.10, 0.22), eye=(1.0, 0.3, 0.9),
                     w=0.36, horns=False, female=True, hair=(0.12, 0.07, 0.05)),
    "colossus": dict(skin=(0.46, 0.47, 0.52), cloth=(0.20, 0.17, 0.15), eye=(1.0, 0.55, 0.1),
                     w=0.85, horns=True, plates=(0.32, 0.30, 0.28)),
    "titan": dict(skin=(0.50, 0.44, 0.38), cloth=(0.26, 0.22, 0.19), eye=(1.0, 0.22, 0.08),
                  w=0.9, horns=True, plates=(0.36, 0.33, 0.30), crags=(0.40, 0.37, 0.33)),
}


def build_drone():
    """Elektro-Drohne: flacher Rumpf mit vier Rotorarmen, blau leuchtendes Auge, Spulen unten.
    Gleiche Rückgabe wie build_mob; 'Beine' sind die Rotoren (drehen sich)."""
    rng = random.Random(77)
    root = NodePath("drone")
    body, glow = Mesh(), Mesh(lit=False)
    body.mat = "metal"
    box(body, 0, 0, 0.32, 0.5, 0.5, 0.18, (0.22, 0.24, 0.30), rng)
    box(body, 0, 0, 0.44, 0.3, 0.3, 0.08, (0.16, 0.17, 0.22), rng)
    for sx, sy in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
        box(body, sx * 0.3, sy * 0.3, 0.36, 0.34, 0.06, 0.04, (0.30, 0.32, 0.36))
    box(glow, 0, 0.26, 0.32, 0.16, 0.03, 0.1, (0.35, 0.8, 1.0))        # Auge vorne
    box(glow, 0, 0, 0.18, 0.06, 0.06, 0.12, (0.4, 0.85, 1.0))          # Elektrode unten
    torso = root.attachNewNode("torso")
    torso.attachNewNode(body.node("b"))
    g = torso.attachNewNode(glow.node("g"))
    g.setFogOff()
    rm = Mesh(lit=False)                                                 # Rotorblatt (Kreuz)
    box(rm, 0, 0, 0, 0.36, 0.05, 0.01, (0.75, 0.78, 0.82))
    box(rm, 0, 0, 0, 0.05, 0.36, 0.01, (0.75, 0.78, 0.82))
    rotors = [rm, rm]
    legs = []
    for i, (ox, oy) in enumerate(((0.45, 0.45), (-0.45, -0.45), (0.45, -0.45), (-0.45, 0.45))):
        n = torso.attachNewNode("rotor")
        n.setPos(ox, oy, 0.42)
        n.attachNewNode(rotors[i % 2].node("r"))
        legs.append(n)
    bar = root.attachNewNode("bar")
    bar.setPos(0, 0, 1.0)
    return root, torso, legs, bar


def build_critter(col):
    """Fluchttier: Feldhase - gestreckter Körper, lange Ohren mit dunklen Spitzen, helle Blume (Schwanz),
    kräftige Hinterläufe. Unauffällige Fellfarbe, kein Leuchten. Gleiche Rückgabe wie build_mob."""
    rng = random.Random(5)
    root = NodePath("critter")
    m = Mesh()
    dark = tuple(c * 0.62 for c in col)
    belly = tuple(min(1.0, c * 1.35 + 0.12) for c in col)
    blob(m, 0, -0.05, 0.02, 0.36, 0.56, 0.36, col, rng, jitter=0.07)        # Rumpf (hinten höher)
    blob(m, 0, -0.22, 0.12, 0.34, 0.34, 0.34, col, rng, jitter=0.05)        # Hinterteil
    blob(m, 0, 0.0, -0.12, 0.28, 0.4, 0.14, belly, rng, jitter=0.04)       # heller Bauch
    blob(m, 0, 0.42, 0.26, 0.24, 0.3, 0.24, col, rng, jitter=0.05)         # Kopf
    box(m, 0, 0.62, 0.2, 0.1, 0.08, 0.08, dark, rng)                       # Nase
    for sx in (-1, 1):
        box(m, sx * 0.07, 0.34, 0.62, 0.08, 0.05, 0.42, col, rng)          # Ohren, leicht nach hinten
        box(m, sx * 0.07, 0.32, 0.86, 0.085, 0.055, 0.1, (0.12, 0.1, 0.09), rng)   # dunkle Ohrspitzen
        box(m, sx * 0.13, 0.54, 0.3, 0.04, 0.06, 0.06, (0.06, 0.05, 0.05))  # Augen (seitlich)
    blob(m, 0, -0.5, 0.2, 0.12, 0.1, 0.12, (0.92, 0.9, 0.86), rng, jitter=0.03)   # Blume
    torso = root.attachNewNode("torso")
    torso.setZ(0.45)
    torso.attachNewNode(m.node("m"))
    legs = []
    for sx in (-1, 1):                                # Hinterläufe (gross); die Vorderpfoten hängen am Rumpf
        lm = Mesh()
        box(lm, 0, 0.12, -0.17, 0.12, 0.42, 0.1, dark, rng)
        leg = root.attachNewNode("leg")
        leg.setPos(sx * 0.17, -0.22, 0.25)
        leg.attachNewNode(lm.node("l"))
        legs.append(leg)
    fm = Mesh()
    for sx in (-1, 1):
        box(fm, sx * 0.1, 0.32, -0.32, 0.07, 0.08, 0.26, dark, rng)       # Vorderläufe
    torso.attachNewNode(fm.node("f"))
    bar = root.attachNewNode("bar")
    bar.setPos(0, 0, 1.6)
    return root, torso, legs, bar


def mob_bar(bar):
    """Lebensbalken (Billboard) an einen vorhandenen Knoten hängen. -> (bar, Vordergrund)"""
    bar.setBillboardPointEye()
    bar.setLightOff()
    bar.setTwoSided(True)
    cm = CardMaker("bg")
    cm.setFrame(-0.5, 0.5, -0.05, 0.05)
    bg = bar.attachNewNode(cm.generate())
    bg.setColor(0, 0, 0, 1)
    cm = CardMaker("fg")
    cm.setFrame(0, 1, -0.035, 0.035)
    fg = bar.attachNewNode(cm.generate())
    fg.setPos(-0.5, -0.01, 0)
    fg.setColor(0.85, 0.1, 0.1, 1)
    fg.setDepthOffset(1)
    bar.hide()
    return bar, fg


def build_mob(kind, look=None):
    """Gibt (root, torso, legL, legR, bar, bar_fg) zurück. Hüfte liegt bei z=0.75,
    Füsse bei z=0, Blick Richtung +y. look: eigenes Aussehen (für Mitspieler)."""
    if kind == "drone":
        root, torso, legs, bar = build_drone()
        bar, fg = mob_bar(bar)
        return root, torso, legs[0], legs[1], bar, fg, legs
    if kind == "critter":
        root, torso, legs, bar = build_critter((look or {}).get("fur", CRITTER_COLORS["standard"]))
        bar, fg = mob_bar(bar)
        return root, torso, legs[0], legs[1], bar, fg
    L = look or MOB_LOOK[kind]
    rng = random.Random(sum(map(ord, kind)))      # stabil auf allen Rechnern
    root = NodePath(kind)
    tm = Mesh()
    w = L["w"]
    fem = bool(L.get("female"))
    if not fem:
        box(tm, 0, 0, 0.34, w, 0.34, 0.68, L["cloth"], rng, mat="cloth")                  # Torso
    blob(tm, 0, 0.02, 0.98, 0.26, 0.24, 0.26, L["skin"], rng, jitter=0.1)    # Kopf
    for sx in (-1, 1):
        box(tm, sx * 0.1, 0.22, 1.02, 0.07, 0.04, 0.05, L["eye"])            # Augen
        box(tm, sx * (w / 2 + 0.1), 0.05, 0.38, 0.11 if fem else 0.14, 0.11 if fem else 0.14, 0.62, L["skin"], rng)  # Arme
        if L["horns"]:
            cone(tm, sx * 0.2, 0.0, 1.15, 0.07, 0.3, 5, (0.85, 0.82, 0.7), rng)
        if L.get("plates"):                                                   # Koloss: Schulterplatten, Pranken
            box(tm, sx * (w / 2 + 0.06), 0.0, 0.66, 0.3, 0.36, 0.12, L["plates"], rng)
            box(tm, sx * (w / 2 + 0.1), 0.05, 0.02, 0.22, 0.22, 0.16, L["skin"], rng)
        if L.get("crags"):                                                    # Titan: Felszacken auf dem Rücken
            for i in range(3):
                cone(tm, sx * (0.12 + 0.1 * i), -0.2, 0.75 - 0.18 * i, 0.08, 0.28 - 0.05 * i, 5, L["crags"], rng)
    if fem:                                                                   # Gegnerin: Sanduhr-Figur
        hair, cl = L["hair"], L["cloth"]
        trim = tuple(min(1.0, c * 1.5 + 0.1) for c in cl)
        box(tm, 0, 0, 0.52, w, 0.27, 0.34, cl, rng, mat="cloth")                           # Oberkörper (schmale Schultern)
        box(tm, 0, 0.0, 0.30, w * 0.74, 0.22, 0.14, cl, rng, mat="cloth")                  # Taille
        box(tm, 0, 0.0, 0.20, w * 0.80, 0.22, 0.04, trim)                     # Gürtel
        box(tm, 0, 0.0, 0.08, w * 1.45, 0.34, 0.20, cl, rng, mat="cloth")                  # Hüfte / Rockansatz
        box(tm, 0, 0.0, -0.09, w * 1.90, 0.44, 0.17, cl, rng, mat="cloth")                 # Rock, ausgestellt
        box(tm, 0, 0.0, -0.26, w * 2.30, 0.54, 0.17, cl, rng, mat="cloth")
        box(tm, 0, 0.0, -0.36, w * 2.35, 0.56, 0.04, trim)                    # Saum
        box(tm, 0, 0.0, 0.69, w * 0.5, 0.2, 0.08, L["skin"], rng)             # Hals / Ausschnitt
        blob(tm, 0, -0.05, 1.03, 0.29, 0.27, 0.29, hair, rng, jitter=0.06)    # Haare
        box(tm, 0, 0.13, 1.14, 0.36, 0.05, 0.10, hair, rng)                   # Pony
        for sx in (-1, 1):
            box(tm, sx * 0.17, 0.0, 0.90, 0.07, 0.11, 0.36, hair, rng)        # Strähnen am Gesicht
            box(tm, sx * 0.1, 0.235, 1.06, 0.10, 0.02, 0.015, (0.02, 0.02, 0.03))   # Wimpern
        box(tm, 0, -0.20, 0.76, 0.38, 0.12, 0.78, hair, rng)                  # lange Haare über den Rücken
        box(tm, 0, -0.21, 0.34, 0.28, 0.10, 0.22, hair, rng)
        box(tm, 0, 0.255, 0.935, 0.09, 0.02, 0.03, (0.85, 0.10, 0.25))        # Lippen
        box(tm, 0.19, -0.1, 1.22, 0.07, 0.07, 0.07, trim)                     # Schleife
    torso = root.attachNewNode("torso")
    torso.setZ(0.75)
    torso.attachNewNode(tm.node("t"))
    legs = []
    for sx in (-1, 1):
        lm = Mesh()
        if fem:
            box(lm, 0, 0, -0.38, 0.14, 0.15, 0.76, L["skin"], rng)                # schlanke Beine
            box(lm, 0, 0.05, -0.71, 0.16, 0.26, 0.08, (0.35, 0.05, 0.10), rng)     # Schuhe
        else:
            box(lm, 0, 0, -0.38, 0.2, 0.22, 0.76, tuple(c * 0.8 for c in L["cloth"]), rng, mat="cloth")
            box(lm, 0, 0.06, -0.7, 0.22, 0.3, 0.1, (0.2, 0.15, 0.1), rng)
        leg = root.attachNewNode("leg")
        leg.setPos(sx * 0.15, 0, 0.75)
        leg.attachNewNode(lm.node("l"))
        legs.append(leg)
    bar = root.attachNewNode("bar")
    bar.setPos(0, 0, 2.2)
    bar.setBillboardPointEye()
    bar.setLightOff()
    bar.setTwoSided(True)
    cm = CardMaker("bg")
    cm.setFrame(-0.5, 0.5, -0.05, 0.05)
    bg = bar.attachNewNode(cm.generate())
    bg.setColor(0, 0, 0, 1)
    cm = CardMaker("fg")
    cm.setFrame(0, 1, -0.035, 0.035)
    fg = bar.attachNewNode(cm.generate())
    fg.setPos(-0.5, -0.01, 0)
    fg.setColor(0.85, 0.1, 0.1, 1)
    fg.setDepthOffset(1)
    bar.hide()
    return root, torso, legs[0], legs[1], bar, fg


# Höhe der Visierlinie über dem Waffenursprung beim Zielen (Kimme und Korn liegen auf dieser Höhe)
ADS_Z = {"Pistole": 0.069, "Sturmgewehr": 0.079}
ADS_Z_DEFAULT = 0.095

# (cx, cy, cz, sx, sy, sz, farbe) in Waffen-Koordinaten: +y vorwärts, +x rechts
GUN_PARTS = {
    "Pistole": ([(0, 0.12, 0.03, 0.05, 0.26, 0.055, (0.22, 0.22, 0.25)),
                 (0, 0.08, -0.005, 0.045, 0.20, 0.04, (0.15, 0.15, 0.17)),
                 (0, 0.0, -0.07, 0.045, 0.07, 0.13, (0.30, 0.20, 0.12)),
                 # Kimme: zwei Backen mit Ausschnitt; Korn: Pfosten mit Schutzbacken und Leuchtpunkten
                 (-0.0135, 0.0, 0.0665, 0.011, 0.014, 0.018, (0.10, 0.10, 0.12)),
                 (0.0135, 0.0, 0.0665, 0.011, 0.014, 0.018, (0.10, 0.10, 0.12)),
                 (0, 0.235, 0.0665, 0.010, 0.012, 0.018, (0.10, 0.10, 0.12)),
                 (-0.0135, -0.0075, 0.0675, 0.004, 0.002, 0.004, (0.95, 0.95, 0.9)),
                 (0.0135, -0.0075, 0.0675, 0.004, 0.002, 0.004, (0.95, 0.95, 0.9)),
                 (0, 0.2285, 0.0675, 0.004, 0.002, 0.004, (0.95, 0.95, 0.9))], (0, 0.26, 0.035)),
    "Sturmgewehr": ([(0, 0.20, 0.0, 0.055, 0.45, 0.075, (0.20, 0.22, 0.20)),
                     (0, 0.55, 0.02, 0.025, 0.35, 0.025, (0.1, 0.1, 0.1)),
                     (0, 0.40, 0.0, 0.06, 0.25, 0.07, (0.18, 0.20, 0.18)),
                     (0, -0.15, -0.01, 0.05, 0.28, 0.09, (0.30, 0.33, 0.22)),
                     (0, 0.05, -0.09, 0.04, 0.06, 0.12, (0.30, 0.20, 0.12)),
                     (0, 0.18, -0.12, 0.04, 0.09, 0.16, (0.12, 0.12, 0.12)),
                     # Kimme: Sockel mit zwei Backen (Ausschnitt dazwischen); Korn: Sockel, Pfosten, Schutzbacken
                     (0, 0.13, 0.052, 0.036, 0.09, 0.03, (0.12, 0.12, 0.13)),
                     (-0.0145, 0.15, 0.0745, 0.012, 0.014, 0.025, (0.08, 0.08, 0.09)),
                     (0.0145, 0.15, 0.0745, 0.012, 0.014, 0.025, (0.08, 0.08, 0.09)),
                     (0, 0.66, 0.045, 0.03, 0.05, 0.035, (0.12, 0.12, 0.13)),
                     (0, 0.66, 0.074, 0.010, 0.008, 0.03, (0.06, 0.06, 0.07)),
                     (-0.014, 0.66, 0.072, 0.005, 0.012, 0.036, (0.1, 0.1, 0.11)),
                     (0.014, 0.66, 0.072, 0.005, 0.012, 0.036, (0.1, 0.1, 0.11)),
                     (0, 0.655, 0.0875, 0.004, 0.002, 0.004, (0.95, 0.5, 0.1))], (0, 0.74, 0.02)),
    "Schrotflinte": ([(0, 0.45, 0.03, 0.04, 0.70, 0.04, (0.15, 0.15, 0.18)),
                      (0, 0.40, -0.015, 0.04, 0.55, 0.035, (0.17, 0.17, 0.2)),
                      (0, 0.05, 0.0, 0.06, 0.25, 0.085, (0.25, 0.25, 0.28)),
                      (0, 0.35, -0.04, 0.06, 0.20, 0.05, (0.40, 0.26, 0.14)),
                      (0, -0.22, -0.03, 0.05, 0.35, 0.10, (0.40, 0.26, 0.14))], (0, 0.80, 0.03)),
    "Scharfschütze": ([(0, 0.10, 0.0, 0.05, 0.60, 0.07, (0.20, 0.25, 0.22)),
                       (0, 0.65, 0.02, 0.025, 0.55, 0.025, (0.1, 0.1, 0.1)),
                       (0, 0.15, 0.08, 0.04, 0.22, 0.04, (0.05, 0.05, 0.06)),
                       (0, -0.30, -0.02, 0.05, 0.35, 0.10, (0.30, 0.30, 0.28)),
                       (0, 0.10, -0.07, 0.035, 0.08, 0.08, (0.12, 0.12, 0.12))], (0, 0.95, 0.02)),
    "Revolver": ([(0, 0.14, 0.03, 0.05, 0.30, 0.06, (0.30, 0.30, 0.33)),
                  (0, 0.06, 0.0, 0.07, 0.10, 0.09, (0.25, 0.25, 0.28)),
                  (0, -0.02, -0.07, 0.045, 0.07, 0.13, (0.35, 0.22, 0.12))], (0, 0.30, 0.035)),
    "Maschinenpistole": ([(0, 0.12, 0.0, 0.05, 0.30, 0.07, (0.18, 0.18, 0.20)),
                          (0, 0.30, 0.01, 0.025, 0.15, 0.025, (0.1, 0.1, 0.1)),
                          (0, 0.08, -0.09, 0.04, 0.06, 0.14, (0.12, 0.12, 0.12)),
                          (0, -0.02, -0.05, 0.045, 0.07, 0.11, (0.25, 0.18, 0.12))], (0, 0.40, 0.01)),
    "Raketenwerfer": ([(0, 0.25, 0.02, 0.14, 0.95, 0.14, (0.25, 0.30, 0.22)),
                       (0, 0.78, 0.02, 0.18, 0.12, 0.18, (0.15, 0.15, 0.15)),
                       (0, -0.20, 0.02, 0.17, 0.12, 0.17, (0.15, 0.15, 0.15)),
                       (0, 0.10, -0.10, 0.04, 0.08, 0.14, (0.12, 0.12, 0.12)),
                       (0, 0.35, 0.12, 0.04, 0.20, 0.05, (0.10, 0.10, 0.10))], (0, 0.88, 0.02)),
    "Minigun": ([(0, 0.0, 0.0, 0.14, 0.30, 0.14, (0.20, 0.20, 0.22)),
                 (0.04, 0.45, 0.04, 0.03, 0.70, 0.03, (0.35, 0.35, 0.38)),
                 (-0.04, 0.45, 0.04, 0.03, 0.70, 0.03, (0.35, 0.35, 0.38)),
                 (0.04, 0.45, -0.04, 0.03, 0.70, 0.03, (0.35, 0.35, 0.38)),
                 (-0.04, 0.45, -0.04, 0.03, 0.70, 0.03, (0.35, 0.35, 0.38)),
                 (0, 0.0, -0.12, 0.04, 0.08, 0.14, (0.12, 0.12, 0.12))], (0, 0.82, 0.0)),
    "Railgun": ([(0, 0.30, 0.0, 0.07, 0.90, 0.09, (0.15, 0.20, 0.30)),
                 (0, 0.30, 0.06, 0.03, 0.70, 0.03, (0.20, 0.70, 0.90)),
                 (0, -0.10, -0.02, 0.06, 0.30, 0.11, (0.10, 0.12, 0.18)),
                 (0, 0.05, -0.10, 0.04, 0.08, 0.13, (0.10, 0.10, 0.10))], (0, 0.78, 0.0)),
}

# Wechselmagazin je Waffe (für die Nachladeanimation der Ego-Ansicht). Gleiche Tupel wie in GUN_PARTS
# werden dort im Ego-Modell weggelassen (das Magazin ist dann ein eigenes, bewegliches Teil).
MAG_PARTS = {
    "Pistole": (0, 0.0, -0.12, 0.04, 0.06, 0.09, (0.10, 0.10, 0.12)),
    "Sturmgewehr": (0, 0.18, -0.12, 0.04, 0.09, 0.16, (0.12, 0.12, 0.12)),
    "Schrotflinte": (0, 0.25, -0.075, 0.04, 0.12, 0.03, (0.75, 0.15, 0.10)),
    "Scharfschütze": (0, 0.10, -0.07, 0.035, 0.08, 0.08, (0.12, 0.12, 0.12)),
    "Revolver": (0, 0.06, -0.075, 0.05, 0.06, 0.04, (0.75, 0.60, 0.25)),
    "Maschinenpistole": (0, 0.08, -0.09, 0.04, 0.06, 0.14, (0.12, 0.12, 0.12)),
    "Raketenwerfer": None,                      # die Rakete wird von vorn eingeschoben
    "Minigun": (0, -0.02, -0.20, 0.09, 0.12, 0.09, (0.25, 0.32, 0.18)),
    "Railgun": (0, 0.05, -0.17, 0.05, 0.08, 0.09, (0.20, 0.70, 0.90)),
}

# Rennhaltung (BF3-artig): (dx, dy, dz, heading, pitch, roll). Pistolen: Lauf nach oben vor der Brust;
# grosse Waffen: quer vor dem Körper.
SPRINT_POSE = {
    "Pistole": (-0.08, -0.03, 0.0, 8.0, 42.0, -6.0),
    "Revolver": (-0.08, -0.03, 0.0, 8.0, 42.0, -6.0),
    "Maschinenpistole": (-0.14, -0.04, 0.02, 38.0, 16.0, -8.0),
    "Raketenwerfer": (-0.22, -0.12, -0.04, 58.0, 8.0, -12.0),
    "Minigun": (-0.22, -0.10, -0.08, 55.0, 6.0, -10.0),
}
SPRINT_POSE_DEFAULT = (-0.16, -0.08, -0.02, 52.0, 10.0, -14.0)


STEEL, DSTEEL = (0.80, 0.82, 0.86), (0.52, 0.54, 0.58)
MELEE_PARTS = {     # Quader (cx, cy, cz, sx, sy, sz, Farbe): Griff im Ursprung, Klinge nach +y
    "Messer": [(0, 0, 0, 0.03, 0.11, 0.035, (0.28, 0.18, 0.1)), (0, 0.135, 0.004, 0.01, 0.16, 0.03, STEEL),
               (0, 0.225, 0.0, 0.008, 0.03, 0.016, STEEL)],
    "Kampfmesser": [(0, 0, 0, 0.034, 0.12, 0.04, (0.08, 0.08, 0.09)), (0, 0.066, 0, 0.05, 0.012, 0.062, (0.3, 0.3, 0.32)),
                    (0, 0.17, 0.006, 0.012, 0.2, 0.042, DSTEEL), (0, 0.28, 0.014, 0.01, 0.03, 0.022, DSTEEL)],
    "Machete": [(0, 0, 0, 0.035, 0.13, 0.04, (0.45, 0.3, 0.15)), (0, 0.27, 0.012, 0.01, 0.4, 0.06, STEEL),
                (0, 0.46, 0.02, 0.01, 0.06, 0.072, STEEL)],
    "Schwert": [(0, -0.09, 0, 0.042, 0.03, 0.042, (0.72, 0.6, 0.3)), (0, 0, 0, 0.035, 0.15, 0.035, (0.35, 0.2, 0.1)),
                (0, 0.088, 0, 0.032, 0.026, 0.2, DSTEEL), (0, 0.42, 0, 0.012, 0.62, 0.05, STEEL),
                (0, 0.75, 0, 0.01, 0.06, 0.024, STEEL)],
    "Katana": [(0, 0, 0, 0.032, 0.22, 0.036, (0.12, 0.1, 0.14)), (0, 0.12, 0, 0.07, 0.012, 0.07, (0.75, 0.62, 0.25)),
               (0, 0.35, 0.0, 0.009, 0.42, 0.034, (0.88, 0.9, 0.94)), (0, 0.67, 0.016, 0.009, 0.24, 0.03, (0.88, 0.9, 0.94)),
               (0, 0.81, 0.028, 0.008, 0.05, 0.018, (0.88, 0.9, 0.94))],
    "Bratpfanne": [(0, 0, 0, 0.03, 0.24, 0.03, (0.1, 0.1, 0.11)), (0, 0.33, 0, 0.03, 0.26, 0.16, (0.2, 0.2, 0.22)),
                   (0, 0.33, 0, 0.03, 0.2, 0.24, (0.2, 0.2, 0.22)), (0, 0.33, 0, 0.032, 0.12, 0.28, (0.2, 0.2, 0.22)),
                   (0.012, 0.33, 0, 0.012, 0.18, 0.2, (0.32, 0.32, 0.35))],
}


def melee_model(mi, scale=1.0):
    """Low-Poly-Modell einer Nahkampfwaffe (Griff im Ursprung, Klinge nach +y)."""
    rng = random.Random(40 + mi)
    m = Mesh()
    for cx, cy, cz, sx, sy, sz, col in MELEE_PARTS[MELEE[mi].name]:
        box(m, cx * scale, cy * scale, cz * scale, sx * scale, sy * scale, sz * scale, col, rng)
    return m


def melee_icon(mi, width=0.24, height=0.13):
    """Seitenansicht der Nahkampfwaffe fürs HUD (wie weapon_icon)."""
    return weapon_icon(None, width, height, MELEE_PARTS[MELEE[mi].name], "icon_" + MELEE[mi].name)


def weapon_icon(wi, width=0.42, height=0.2, parts=None, name=None):
    """Seitenansicht einer Waffe als flaches Bild (x/z-Ebene, Mitte im Ursprung), gezeichnet
    aus denselben Quadern wie das 3D-Modell: erst dunkler Rand, dann die Teile in Farbe."""
    if parts is None:
        parts, _muzzle = GUN_PARTS[WEAPONS[wi].name]
    rects = [(cy - sy / 2, cy + sy / 2, cz - sz / 2, cz + sz / 2, col)
             for _cx, cy, cz, _sx, sy, sz, col in parts]
    y0, y1 = min(r[0] for r in rects), max(r[1] for r in rects)
    z0, z1 = min(r[2] for r in rects), max(r[3] for r in rects)
    pad = 0.03
    k = min(width / (y1 - y0 + 2 * pad), height / (z1 - z0 + 2 * pad))
    my, mz = (y0 + y1) / 2, (z0 + z1) / 2
    m = Mesh(lit=False)

    def quad(a0, a1, b0, b1, col):
        p = [((a - my) * k, 0.0, (b - mz) * k) for a, b in ((a0, b0), (a1, b0), (a1, b1), (a0, b1))]
        m.tri(p[0], p[1], p[2], col)
        m.tri(p[0], p[2], p[3], col)

    o = 0.014
    for a0, a1, b0, b1, _c in rects:
        quad(a0 - o, a1 + o, b0 - o, b1 + o, (0.02, 0.02, 0.03))
    for a0, a1, b0, b1, c in rects:
        quad(a0, a1, b0, b1, tuple(min(1.0, v * 1.5 + 0.28) for v in c))
    np = NodePath(m.node(name or ("icon_" + WEAPONS[wi].name)))
    np.setTwoSided(True)
    return np


def build_rocket(lit=True):
    """Rakete (Spitze bei +y, Länge ~1 m) und ihre Flamme (hinten bei -y) als zwei Modelle."""
    rng = random.Random(21)
    m = Mesh(lit=lit)
    box(m, 0, 0, 0, 0.12, 0.8, 0.12, (0.62, 0.64, 0.58), rng)
    box(m, 0, 0.44, 0, 0.09, 0.14, 0.09, (0.85, 0.2, 0.15), rng)        # Spitze in Stufen
    box(m, 0, 0.54, 0, 0.06, 0.08, 0.06, (0.85, 0.2, 0.15), rng)
    box(m, 0, 0.6, 0, 0.03, 0.06, 0.03, (0.9, 0.3, 0.2), rng)
    box(m, 0, 0.1, 0, 0.135, 0.07, 0.135, (0.25, 0.25, 0.27), rng)      # Band
    for sx, sz in ((1, 0), (-1, 0), (0, 1), (0, -1)):                   # vier Leitflossen
        box(m, sx * 0.09, -0.34, sz * 0.09, 0.02 + 0.08 * abs(sx), 0.16, 0.02 + 0.08 * abs(sz),
            (0.30, 0.30, 0.34), rng)
    f = Mesh(lit=False)
    box(f, 0, -0.65, 0, 0.09, 0.5, 0.09, (1.0, 0.55, 0.1))
    box(f, 0, -0.55, 0, 0.05, 0.35, 0.05, (1.0, 0.95, 0.5))
    box(f, 0, -0.62, 0, 0.14, 0.18, 0.02, (1.0, 0.6, 0.1))
    box(f, 0, -0.62, 0, 0.02, 0.18, 0.14, (1.0, 0.6, 0.1))
    return NodePath(m.node("rocket")), NodePath(f.node("flame"))


def build_vehicle_model():
    """Geländewagen, Front bei +y, Räder bei z=0. Gibt (root, Räder, bar, fg) zurück."""
    rng = random.Random(5)
    body_c, dark, glass = (0.52, 0.22, 0.14), (0.14, 0.14, 0.16), (0.55, 0.75, 0.85)
    root = NodePath("jeep")
    m = Mesh()
    m.mat = "metal"
    box(m, 0, 0, 0.62, 1.7, 3.2, 0.34, body_c, rng)                  # Wanne
    box(m, 0, 1.12, 0.95, 1.5, 0.95, 0.3, body_c, rng)               # Motorhaube
    box(m, 0, 1.62, 0.78, 1.3, 0.08, 0.28, dark)                     # Kühlergrill
    box(m, 0, -1.3, 0.95, 1.5, 0.5, 0.3, body_c, rng)                # Heck
    for sx in (-1, 1):
        box(m, sx * 0.45, -0.2, 0.9, 0.5, 0.55, 0.12, dark, rng)     # Sitze
        box(m, sx * 0.45, -0.5, 1.2, 0.5, 0.1, 0.5, dark, rng)       # Lehnen
        box(m, sx * 0.8, 0.45, 1.4, 0.07, 0.07, 0.95, dark)          # Überrollbügel
        box(m, sx * 0.8, -1.0, 1.4, 0.07, 0.07, 0.95, dark)
        box(m, sx * 0.8, -0.27, 1.88, 0.07, 1.5, 0.07, dark)
        box(m, sx * 0.88, 1.1, 0.72, 0.16, 1.0, 0.1, dark, rng)      # Kotflügel
    box(m, 0, 0.45, 1.88, 1.6, 0.07, 0.07, dark)
    box(m, 0, -1.0, 1.88, 1.6, 0.07, 0.07, dark)
    box(m, 0, 0.55, 1.28, 1.5, 0.05, 0.5, glass)                     # Windschutzscheibe
    box(m, 0, -0.9, 1.3, 0.36, 0.36, 0.5, dark)                      # Sockel fürs Heckgeschütz
    box(m, 0, -0.9, 1.56, 0.8, 0.8, 0.08, (0.46, 0.48, 0.52))        # Drehkranz
    box(m, 0, 1.68, 0.6, 1.8, 0.16, 0.16, dark, rng)                 # Stossstange vorn
    box(m, 0, -1.68, 0.6, 1.8, 0.14, 0.16, dark, rng)                # hinten
    for sx in (-1, 1):
        box(m, sx * 1.0, 0.55, 1.15, 0.06, 0.14, 0.16, dark)         # Aussenspiegel
        box(m, sx * 0.62, 1.66, 0.9, 0.34, 0.1, 0.2, dark)           # Scheinwerfergehäuse
    box(m, 0.55, -1.2, 1.12, 0.3, 0.22, 0.34, (0.30, 0.34, 0.20), rng)   # Kanister
    box(m, -0.62, -1.62, 0.55, 0.08, 0.3, 0.08, (0.35, 0.35, 0.38))  # Auspuff
    root.attachNewNode(m.node("body"))
    lm = Mesh(lit=False)
    for sx in (-1, 1):
        box(lm, sx * 0.55, 1.64, 0.9, 0.28, 0.06, 0.16, (1.0, 0.92, 0.55))
        box(lm, sx * 0.6, -1.56, 0.92, 0.2, 0.05, 0.1, (0.9, 0.1, 0.1))
    root.attachNewNode(lm.node("lights"))
    wheels = []
    for sx, sy in ((-1, 1.05), (1, 1.05), (-1, -1.05), (1, -1.05)):
        piv = root.attachNewNode("wheel")
        piv.setPos(sx * 0.95, sy, 0.4)
        tm = Mesh()
        prism(tm, 0, 0, -0.15, 0.4, 0.3, 8, (0.08, 0.08, 0.09), rng)
        prism(tm, 0, 0, -0.17, 0.2, 0.34, 6, (0.62, 0.62, 0.66), rng)
        tire = piv.attachNewNode(tm.node("tire"))
        tire.setR(90)                                                # Achse = x
        wheels.append(piv)
    bar = root.attachNewNode("bar")
    bar.setPos(0, 0, 2.7)
    bar.setBillboardPointEye()
    bar.setLightOff()
    bar.setTwoSided(True)
    cm = CardMaker("bg")
    cm.setFrame(-0.8, 0.8, -0.07, 0.07)
    bar.attachNewNode(cm.generate()).setColor(0, 0, 0, 1)
    cm = CardMaker("fg")
    cm.setFrame(0, 1, -0.05, 0.05)
    fg = bar.attachNewNode(cm.generate())
    fg.setPos(-0.75, -0.01, 0)
    fg.setScale(1.5, 1, 1)
    fg.setColor(0.95, 0.75, 0.1, 1)
    fg.setDepthOffset(1)
    bar.hide()
    return root, wheels, bar, fg


def build_heli_model():
    """Kampfhubschrauber, Nase bei +y, Kufen bei z=0. Gibt (root, rotor, tail_rotor, bar, fg) zurück."""
    rng = random.Random(31)
    body, dark, red = (0.30, 0.37, 0.27), (0.14, 0.14, 0.16), (0.72, 0.16, 0.1)
    glass, steel = (0.5, 0.72, 0.88), (0.5, 0.52, 0.56)
    root = NodePath("heli")
    m = Mesh()
    m.mat = "metal"
    box(m, 0, 0.0, 1.45, 1.9, 3.6, 1.45, body, rng)                  # Kabine
    blob(m, 0, 2.0, 1.4, 0.95, 1.2, 0.85, body, rng)                 # Bug
    blob(m, 0, 2.55, 1.75, 0.8, 0.7, 0.6, glass, rng, jitter=0.05)   # Cockpitscheibe
    box(m, 0, -3.3, 1.85, 0.5, 4.4, 0.5, body, rng)                  # Heckausleger
    box(m, 0, -5.3, 2.5, 0.12, 0.95, 1.2, red)                       # Seitenleitwerk
    box(m, 0, -4.9, 1.9, 1.7, 0.6, 0.1, body)                        # Höhenleitwerk
    box(m, 0, -0.1, 2.35, 0.9, 1.6, 0.5, dark)                       # Turbinenaufbau
    box(m, 0, -0.1, 2.7, 0.3, 0.3, 0.35, steel)                      # Rotormast
    for sx in (-1, 1):
        box(m, sx * 1.15, 0.1, 0.12, 0.12, 3.8, 0.1, dark)           # Kufen
        box(m, sx * 1.05, 1.0, 0.6, 0.08, 0.1, 1.0, dark)            # Streben
        box(m, sx * 1.05, -0.8, 0.6, 0.08, 0.1, 1.0, dark)
        box(m, sx * 1.55, 0.3, 1.15, 0.55, 1.3, 0.5, dark, rng)      # Raketenbehälter
        box(m, sx * 1.55, 1.0, 1.15, 0.42, 0.1, 0.38, red)           # Raketenspitzen
    box(m, 0, 2.7, 0.8, 0.14, 1.2, 0.14, steel)                      # Minigun am Bug
    box(m, 0, 2.1, 0.85, 0.35, 0.5, 0.3, dark)
    blob(m, 0, 3.0, 0.95, 0.2, 0.26, 0.2, dark, rng, jitter=0.06)    # Sensorkugel
    box(m, 0, -5.4, 3.15, 0.1, 0.1, 0.1, red)                         # Positionslicht
    for sx in (-1, 1):
        box(m, sx * 0.97, 0.3, 1.5, 0.05, 1.3, 0.85, dark, rng)       # Türfeld
        box(m, sx * 0.98, 1.0, 1.5, 0.06, 0.06, 0.8, steel)           # Türgriff / Rahmen
    box(m, 0, -0.1, 3.0, 0.5, 0.5, 0.15, steel)                       # Rotorkopf
    root.attachNewNode(m.node("body"))
    rotor = root.attachNewNode("rotor")
    rotor.setPos(0, -0.1, 2.95)
    rm = Mesh()
    box(rm, 0, 0, 0, 10.0, 0.3, 0.05, dark)
    box(rm, 0, 0, 0, 0.3, 10.0, 0.05, dark)
    rotor.attachNewNode(rm.node("blades"))
    trotor = root.attachNewNode("trotor")
    trotor.setPos(0.25, -5.35, 2.5)
    tm = Mesh()
    box(tm, 0, 0, 0, 0.05, 0.2, 2.0, dark)
    box(tm, 0, 0, 0, 0.05, 2.0, 0.2, dark)
    trotor.attachNewNode(tm.node("tblades"))
    bar = root.attachNewNode("bar")
    bar.setPos(0, 0, 5.2)
    bar.setBillboardPointEye()
    bar.setLightOff()
    bar.setTwoSided(True)
    cm = CardMaker("bg")
    cm.setFrame(-1.1, 1.1, -0.1, 0.1)
    bar.attachNewNode(cm.generate()).setColor(0, 0, 0, 1)
    cm = CardMaker("fg")
    cm.setFrame(0, 1, -0.08, 0.08)
    fg = bar.attachNewNode(cm.generate())
    fg.setPos(-1.05, -0.01, 0)
    fg.setScale(2.1, 1, 1)
    fg.setColor(0.95, 0.75, 0.1, 1)
    fg.setDepthOffset(1)
    bar.hide()
    return root, rotor, trotor, bar, fg


def build_turret_model():
    """Geschütz auf dem Turm. Ursprung = Drehpunkt (Rohrmitte), Rohr zeigt nach +y.
    Gibt (root, head, barrel, glow, lamp) zurück: head dreht sich (Heading), barrel neigt sich (Pitch)."""
    rng = random.Random(8)
    dark, steel, olive = (0.18, 0.19, 0.21), (0.46, 0.48, 0.52), (0.30, 0.36, 0.24)
    root = NodePath("turret")
    pm = Mesh()
    pm.mat = "metal"
    box(pm, 0, 0, -0.27, 0.3, 0.3, 0.46, dark, rng)                   # Standfuss bis zum Sockel
    box(pm, 0, 0, -0.30, 0.9, 0.9, 0.1, steel, rng)                   # Drehkranz
    root.attachNewNode(pm.node("pedestal"))
    head = root.attachNewNode("head")
    hm = Mesh()
    hm.mat = "metal"
    box(hm, 0, 0, 0.0, 0.82, 0.9, 0.5, olive, rng)                    # Gehäuse
    box(hm, 0, -0.62, 0.02, 0.7, 0.34, 0.42, dark, rng)               # Munitionskasten
    for sx in (-1, 1):
        box(hm, sx * 0.46, 0.12, 0.05, 0.08, 0.66, 0.56, steel, rng)  # Seitenpanzer
    box(hm, 0, 0.42, 0.34, 0.5, 0.3, 0.1, steel, rng)                 # Dach vorn
    head.attachNewNode(hm.node("housing"))
    barrel = head.attachNewNode("barrel")
    barrel.setPos(0, 0.4, 0.0)
    bm = Mesh()
    bm.mat = "metal"
    gm = Mesh(lit=False)
    for sx in (-0.2, 0.2):
        box(bm, sx, 0.85, 0, 0.13, 1.5, 0.13, dark, rng)              # Rohre
        box(bm, sx, 1.65, 0, 0.2, 0.2, 0.2, steel, rng)               # Mündungsbremse
        box(gm, sx, 0.9, 0, 0.17, 1.55, 0.17, (1.0, 0.42, 0.08))      # Glühen bei Hitze
    box(bm, 0, 0.0, 0, 0.6, 0.45, 0.3, steel, rng)                    # Waffenblock
    barrel.attachNewNode(bm.node("barrels"))
    glow = barrel.attachNewNode(gm.node("glow"))
    glow.setTransparency(TransparencyAttrib.MAlpha)
    glow.setLightOff()
    glow.setColorScale(1, 1, 1, 0)
    lm = Mesh(lit=False)
    box(lm, 0, 0, 0, 0.14, 0.14, 0.14, (1, 1, 1))
    lamp = head.attachNewNode(lm.node("lamp"))
    lamp.setPos(-0.3, -0.1, 0.32)
    return root, head, barrel, glow, lamp


class TurretView:
    """Darstellung eines Geschützes: dreht sich, Mündungsfeuer beim Schiessen, Rohre glühen mit
    der Hitze, bei Überhitzung bläulich mit Dampf (Cooldown). Lampe: grün bereit, rot feuert, blau Pause."""

    def __init__(self, t):
        self.root, self.head, self.barrel, self.glow, self.lamp = build_turret_model()
        self.root.setPos(t.x, t.y, t.z)
        self.px, self.py, self.pz = t.x, t.y, t.z
        self.flash_t = self.steam_t = 0.0
        if t.kind == "flak":                    # grösseres, bläulich-graues Flakgeschütz
            self.root.setScale(1.5)
            self.root.setColorScale(0.8, 0.88, 1.0, 1)
        elif t.kind == "car":
            self.root.setScale(0.85)

    def muzzle(self, t, dist=2.1):
        h, p = math.radians(t.heading), math.radians(t.pitch)
        return (t.x - math.sin(h) * math.cos(p) * dist, t.y + math.cos(h) * math.cos(p) * dist,
                t.z + math.sin(p) * dist)

    def update(self, t, dt, game):
        if t.kind == "car":                     # fährt mit dem Wagen (weich nachgeführt wie dieser)
            if math.hypot(t.x - self.px, t.y - self.py) > 6.0:
                self.px, self.py, self.pz = t.x, t.y, t.z
            a = min(1.0, 18.0 * dt)
            self.px += (t.x - self.px) * a
            self.py += (t.y - self.py) * a
            self.pz += (t.z - self.pz) * a
            self.root.setPos(self.px, self.py, self.pz)
        self.head.setH(t.heading)
        self.barrel.setP(t.pitch)
        heat = clampf(t.heat, 0.0, 1.0)
        self.glow.setColorScale(1, 1, 1, 0.0 if t.over else heat * 0.9)
        if t.over:
            self.barrel.setColorScale(0.55, 0.75, 1.25, 1)
            self.lamp.setColorScale(0.25, 0.5, 1.0, 1)
            self.steam_t -= dt
            if self.steam_t <= 0:
                self.steam_t = 0.1
                game.smoke_puff(self.muzzle(t), 0.22, 1.3, 0.92)
        else:
            self.barrel.clearColorScale()
            self.lamp.setColorScale(*((1.0, 0.15, 0.1, 1) if t.firing else (0.2, 1.0, 0.3, 1)))
        self.flash_t -= dt
        if t.firing and self.flash_t <= 0:
            self.flash_t = 0.08
            game.fx_spawn(game.sphere_np, self.muzzle(t), 0.07, 0.12, 0.42, (1.0, 0.95, 0.6),
                          (1.0, 0.45, 0.1), p=0.8, fog=False)


class Spring:
    """Gedämpfte Feder x'' = -k x - c x'. kick() gibt einen Geschwindigkeitsimpuls."""

    def __init__(self, k=180.0, c=14.0):
        self.x = self.v = 0.0
        self.k, self.c = k, c

    def step(self, dt):
        n = int(dt / 0.004) + 1          # Teilschritte -> stabil auch bei grossem dt
        h = dt / n
        for _ in range(n):
            self.v += (-self.k * self.x - self.c * self.v) * h
            self.x += self.v * h

    def kick(self, v):
        self.v += v


class Particle:
    def __init__(self, np, pos, vel, life, bounce, spin, shrink):
        self.np = np
        self.x, self.y, self.z = pos
        self.vx, self.vy, self.vz = vel
        self.life, self.age = life, 0.0
        self.bounce, self.spin, self.shrink = bounce, spin, shrink
        self.scale = np.getScale()


class Fx:
    """Animierter Effekt (Feuerball, Druckwelle, Rauch): Grösse und Farbe laufen von Anfang
    bis Ende, die Deckkraft sinkt als (1-t)^p; optional steigt er auf."""

    def __init__(self, np, pos, life, s0, s1, c0, c1, p=1.0, rise=0.0):
        self.np, self.life, self.age = np, life, 0.0
        self.s0, self.s1, self.c0, self.c1, self.p, self.rise = s0, s1, c0, c1, p, rise
        self.x, self.y, self.z = pos

    def update(self, dt):
        """False, wenn der Effekt zu Ende ist."""
        self.age += dt
        if self.age >= self.life:
            return False
        t = self.age / self.life
        s = self.s0 + (self.s1 - self.s0) * (1 - (1 - t) ** 2)
        self.z += self.rise * dt
        self.np.setPos(self.x, self.y, self.z)
        self.np.setScale(max(s, 0.01))
        c = [a + (b - a) * t for a, b in zip(self.c0, self.c1)]
        self.np.setColorScale(c[0], c[1], c[2], (1 - t) ** self.p)
        return True


class Deco:
    """Dekoknoten im Menü, wird wie ein Text mit destroy() entfernt."""
    def __init__(self, np):
        self.np = np

    def destroy(self):
        self.np.removeNode()


class Hot:
    """Anklickbarer Text: Rechteck für die Maus; beim Überfahren wird er gelb hervorgehoben."""
    BASE = (0.86, 0.92, 1.0, 1.0)
    PLAIN = (1.0, 1.0, 1.0, 1.0)
    ON = (1.0, 0.85, 0.2, 1.0)

    def __init__(self, txt, x, z, scale, action=None, text=""):
        self.txt, self.action, self.on, self.label = txt, action, False, text
        w = 0.0
        try:
            w = float(txt.textNode.getWidth()) * scale
        except Exception:
            pass
        if not w > 0:
            w = len(text) * 0.5 * scale
        self.x0, self.x1 = x - w / 2 - 0.05, x + w / 2 + 0.05
        self.z0, self.z1 = z - 0.3 * scale, z + 1.0 * scale

    def hit(self, ax, az):
        return self.action is not None and self.x0 <= ax <= self.x1 and self.z0 <= az <= self.z1

    def set(self, on):
        if on != self.on:
            self.on = on
            self.txt.setFg(self.ON if on else (self.BASE if self.action else self.PLAIN))

    def destroy(self):
        self.txt.destroy()


def gear_model(gi, rng=None, sides=(-1, 1)):
    """Low-Poly-Modell eines Ausrüstungsteils (für Drops und als Anbau an Spielerfiguren). Ursprung: Mitte.
    Schuhe: sides=(-1, 1) = Paar (Drop), sides=(0,) = ein einzelner Schuh (hängt am Bein der Figur)."""
    g = GEAR[gi]
    rng = rng or random.Random(31 + gi)
    m = Mesh()
    c = g.col
    if g.kind == "save_head":                       # Helm: Schale, Kuppe und Rand (sitzt über dem Kopf)
        box(m, 0, 0, 0.1, 0.58, 0.54, 0.2, c, rng)
        box(m, 0, 0, 0.24, 0.42, 0.4, 0.08, c, rng)
        box(m, 0, 0.02, 0.0, 0.64, 0.6, 0.04, tuple(v * 0.7 for v in c), rng)
    elif g.kind == "save_body":                     # Plattenrüstung: Brust- und Rückenplatte, Schulterstücke
        dk = tuple(v * 0.75 for v in c)
        box(m, 0, 0.2, 0.04, 0.56, 0.06, 0.56, c, rng)
        box(m, 0, -0.2, 0.04, 0.56, 0.06, 0.56, dk, rng)
        for sx in (-1, 1):
            box(m, sx * 0.3, 0.0, 0.3, 0.18, 0.42, 0.06, dk, rng)
    elif g.kind == "shield":                        # Schildgenerator: Weste mit leuchtendem Kern
        box(m, 0, 0.2, 0.0, 0.52, 0.06, 0.52, (0.2, 0.25, 0.32), rng)
        box(m, 0, -0.2, 0.0, 0.52, 0.06, 0.52, (0.2, 0.25, 0.32), rng)
        box(m, 0, 0.24, 0.06, 0.18, 0.03, 0.18, c)
    elif g.kind == "jetpack":                       # Jetpack: zwei Tanks auf dem Rücken
        for sx in (-1, 1):
            box(m, sx * 0.11, -0.28, 0.0, 0.18, 0.18, 0.52, c, rng)
            box(m, sx * 0.11, -0.28, -0.31, 0.12, 0.12, 0.1, (0.2, 0.2, 0.22), rng)
    else:                                           # Schuhe (Paar oder einzeln)
        for sx in sides:
            x = sx * 0.15
            box(m, x, 0.04, 0.0, 0.2, 0.32, 0.12, c, rng)
            if g.kind == "dash":                    # Hermes: Flügelchen
                for wx in ((x + sx * 0.12,) if sx else (-0.12, 0.12)):
                    box(m, wx, -0.06, 0.1, 0.04, 0.16, 0.12, (1.0, 1.0, 0.95), rng)
            elif g.kind == "spring":                # Springfedern unter der Sohle
                box(m, x, 0.04, -0.12, 0.12, 0.12, 0.12, (0.6, 0.6, 0.62), rng)
            else:                                   # Jetpack-Schuhe: Düsen an der Ferse
                box(m, x, -0.16, -0.02, 0.1, 0.08, 0.08, (0.25, 0.25, 0.27), rng)
    return m


def slot_symbol(slot):
    """Dezenter Umriss eines Ausrüstungs-Slots fürs HUD (Helm, Oberkörper, Stiefel), Grösse ca. -1..1."""
    m = Mesh(lit=False)
    w = (1, 1, 1)

    def quad(x0, z0, x1, z1):
        m.tri((x0, 0, z0), (x1, 0, z0), (x1, 0, z1), w, ref=(0, -5, 0))
        m.tri((x0, 0, z0), (x1, 0, z1), (x0, 0, z1), w, ref=(0, -5, 0))
    if slot == "head":                                   # Helm: Kuppel + Rand
        n = 16
        for i in range(n):
            a0, a1 = math.pi * i / n, math.pi * (i + 1) / n
            m.tri((0, 0, -0.35), (math.cos(a1) * 0.85, 0, -0.35 + math.sin(a1) * 1.0),
                  (math.cos(a0) * 0.85, 0, -0.35 + math.sin(a0) * 1.0), w, ref=(0, -5, 0))
        quad(-1.05, -0.55, 1.05, -0.35)
    elif slot == "torso":                                # Oberkörper: Schultern, Rumpf, Halsausschnitt
        quad(-1.0, 0.45, -0.25, 0.8)
        quad(0.25, 0.45, 1.0, 0.8)
        quad(-0.7, -0.9, 0.7, 0.45)
        quad(-1.0, 0.0, -0.75, 0.45)
        quad(0.75, 0.0, 1.0, 0.45)
    else:                                                # Stiefel
        quad(-0.55, -0.4, 0.05, 0.85)
        quad(-0.55, -0.85, 0.9, -0.4)
        quad(-0.6, -0.95, 0.95, -0.85)
    return m


class AbilityIcon:
    """HUD-Symbol für Buffs und (später) Ausrüstungs-Fähigkeiten: runde Plakette mit Kürzel; bereit = leuchtet,
    sonst ausgegraut; aussen ein Kreis-Timer (Segmente), der Restzeit bzw. Aufladung zeigt."""
    SEG = 36

    def __init__(self, parent, x, z, label, col, sub=""):
        self.root = parent.attachNewNode("ability")
        self.root.setPos(x, 0, z)
        self.col = col

        def disc(r, c, sort):
            m = Mesh(lit=False)
            for i in range(24):
                a0, a1 = math.tau * i / 24, math.tau * (i + 1) / 24
                m.tri((0, 0, 0), (math.cos(a0) * r, 0, math.sin(a0) * r), (math.cos(a1) * r, 0, math.sin(a1) * r),
                      c, ref=(0, 5, 0))
            n = self.root.attachNewNode(m.node("disc"))
            n.setTwoSided(True)
            n.setTransparency(TransparencyAttrib.MAlpha)
            n.setBin("fixed", sort)
            n.setDepthTest(False)
            n.setDepthWrite(False)
            return n
        disc(0.058, (0.04, 0.05, 0.08, 0.85), 30)
        self.face = disc(0.044, col + (1.0,), 31)
        self.segs = []
        for i in range(self.SEG):                     # Kreis-Timer: im Uhrzeigersinn ab 12 Uhr
            a0 = math.pi / 2 - math.tau * i / self.SEG
            a1 = math.pi / 2 - math.tau * (i + 0.8) / self.SEG
            m = Mesh(lit=False)
            p = lambda r, a: (math.cos(a) * r, 0.0, math.sin(a) * r)       # noqa: E731
            m.tri(p(0.05, a0), p(0.064, a0), p(0.064, a1), (1, 1, 1), ref=(0, 5, 0))
            m.tri(p(0.05, a0), p(0.064, a1), p(0.05, a1), (1, 1, 1), ref=(0, 5, 0))
            n = self.root.attachNewNode(m.node("seg"))
            n.setTwoSided(True)
            n.setBin("fixed", 32)
            n.setDepthTest(False)
            self.segs.append(n)
        self.txt = OnscreenText(text=label, parent=self.root, pos=(0, -0.014), scale=0.042, fg=(0.05, 0.05, 0.08, 1),
                                mayChange=True)
        self.txt.setBin("fixed", 33)
        self.sub = OnscreenText(text=sub, parent=self.root, pos=(0, -0.095), scale=0.03, fg=(1, 1, 1, 0.9),
                                shadow=(0, 0, 0, 0.9), mayChange=True)
        self.sub.setBin("fixed", 33)
        self.root.hide()

    def set(self, ready, frac, label=None, sub=None, col=None):
        """ready: leuchtet; frac 0..1: Anteil des Kreis-Timers (Restzeit oder Ladestand)."""
        if col is not None:
            self.col = col
        if label is not None:
            self.txt.setText(label)
        if sub is not None:
            self.sub.setText(sub)
        k = 1.0 if ready else 0.35                    # ausgegraut: dunkel und entsättigt
        g = sum(self.col) / 3.0
        self.face.setColor(*[(c * k + g * (1 - k)) * (1.0 if ready else 0.6) for c in self.col], 1)
        on = int(round(max(0.0, min(1.0, frac)) * self.SEG))
        for i, n in enumerate(self.segs):
            if i < on:
                n.show()
                n.setColor(*(self.col if ready else (0.75, 0.75, 0.78)), 1)
            else:
                n.hide()
        self.root.show()

    def bar(self, frac):
        """Kleiner Balken unter dem Symbol (Jetpack-Treibstoff)."""
        if not hasattr(self, "bar_fg"):
            cm = CardMaker("bar")
            cm.setFrame(-0.055, 0.055, -0.095, -0.081)
            self.bar_bg = self.root.attachNewNode(cm.generate())
            self.bar_bg.setColor(0.05, 0.05, 0.08, 0.85)
            self.bar_bg.setTransparency(TransparencyAttrib.MAlpha)
            cm.setFrame(0, 0.106, -0.093, -0.083)
            self.bar_fg = self.root.attachNewNode(cm.generate())
            self.bar_fg.setX(-0.053)
            for n, so in ((self.bar_bg, 34), (self.bar_fg, 35)):
                n.setBin("fixed", so)
                n.setDepthTest(False)
        f = max(0.0, min(1.0, frac))
        self.bar_fg.setSx(max(f, 0.0001))
        self.bar_fg.setColor(*(self.col if f > 0.25 else (1.0, 0.3, 0.2)), 1)

    def hide(self):
        self.root.hide()


def over_or_driving(game):
    pl = game.player
    return pl.vehicle >= 0 or pl.heli >= 0 or pl.mount >= 0


class Crosshair:
    """Fadenkreuz aus vier Strichen mit Lücke in der Mitte. Die Striche rücken beim Gehen, Rennen, Drehen,
    in der Luft und nach Schüssen auseinander (ungenauer) und ziehen sich geduckt zusammen."""
    BASE, LEN, TH = 0.014, 0.024, 0.0026

    def __init__(self, parent):
        self.root = parent.attachNewNode("crosshair")
        self.gap = self.BASE
        self.arms = []
        for dx, dz in ((-1, 0), (1, 0), (0, 1), (0, -1)):
            hold = self.root.attachNewNode("arm")
            for grow, col in ((0.0012, (0, 0, 0, 0.7)), (0.0, (1, 1, 1, 0.92))):
                if dx:
                    fr = (0.0 - grow, self.LEN + grow, -self.TH - grow, self.TH + grow)
                else:
                    fr = (-self.TH - grow, self.TH + grow, 0.0 - grow, self.LEN + grow)
                cm = CardMaker("ch")
                cm.setFrame(*fr)
                c = hold.attachNewNode(cm.generate())
                c.setColor(*col)
                c.setTransparency(TransparencyAttrib.MAlpha)
            hold.setH(0)
            self.arms.append((hold, dx, dz))
        self.root.setBin("fixed", 38)
        self.root.setDepthTest(False)
        self.root.setDepthWrite(False)
        self.place(self.gap)

    def place(self, g):
        self.gap = g
        for hold, dx, dz in self.arms:
            # links/unten: Strich beginnt bei -(Lücke+Länge), rechts/oben bei +Lücke
            ox = g if dx > 0 else (-g - self.LEN if dx < 0 else 0.0)
            oz = g if dz > 0 else (-g - self.LEN if dz < 0 else 0.0)
            hold.setPos(ox, 0, oz)

    def target(self, walk, run, turn, air, bloom, crouch):
        return max(0.008, min(0.14, self.BASE + 0.010 * walk + 0.018 * run + 0.026 * turn
                              + 0.022 * air + 0.012 * bloom - 0.004 * crouch))

    def update(self, dt, **k):
        t = self.target(**k)
        a = min(1.0, (22.0 if t > self.gap else 11.0) * dt)         # schnell auf, langsamer zu
        self.place(self.gap + (t - self.gap) * a)

    def show(self):
        self.root.show()

    def hide(self):
        self.root.hide()


class HitMark:
    """Treffermarker wie in Shootern: vier kurze Schrägstriche um das Fadenkreuz (mit dunklem Rand)."""

    def __init__(self, parent):
        self.root = parent.attachNewNode("hitmarker")
        back = self.root.attachNewNode("hm_back")
        self.fg = self.root.attachNewNode("hm_fg")
        for ang in (45, 135, 225, 315):
            for par, fr, col in ((back, (0.016, 0.066, -0.0055, 0.0055), (0, 0, 0, 0.75)),
                                 (self.fg, (0.02, 0.06, -0.0025, 0.0025), (1, 1, 1, 1))):
                h = par.attachNewNode("t")
                h.setR(ang)
                cm = CardMaker("hm")
                cm.setFrame(*fr)
                c = h.attachNewNode(cm.generate())
                c.setColor(*col)
                c.setTransparency(TransparencyAttrib.MAlpha)
        self.root.setBin("fixed", 40)
        self.root.setDepthTest(False)
        self.root.setDepthWrite(False)

    def show(self):
        self.root.show()

    def hide(self):
        self.root.hide()

    def setFg(self, col):
        self.fg.setColorScale(*col)

    def pop(self, k):                  # kurzes Aufploppen beim Treffer
        self.root.setScale(1.0 + 0.5 * max(0.0, min(1.0, k)))


# ------------------------------------------------------------------ Netzwerk
# Alles nur mit der Standardbibliothek (socket, json, threading), nicht blockierend,
# damit das Spiel nie auf das Netz warten muss.
KINDS = ("grunt", "brute", "huntress", "colossus", "drone", "critter", "titan")   # Index in den Snapshots (neue hinten!)
STATES = ("idle", "chase", "attack", "dead")
PLAYER_COLORS = [(0.20, 0.35, 0.80), (0.80, 0.25, 0.25), (0.25, 0.70, 0.35), (0.85, 0.70, 0.15),
                 (0.60, 0.30, 0.75), (0.15, 0.70, 0.75), (0.90, 0.50, 0.15), (0.85, 0.85, 0.85)]


def r1(v):
    return round(v, 1)


def r2(v):
    return round(v, 2)


def finite(*vals):
    """True, wenn alle Werte endliche Zahlen sind (JSON erlaubt auch NaN/Infinity)."""
    return all(isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
               for v in vals)


def local_ip():
    """IP-Adresse dieses Rechners im lokalen Netz (es wird nichts gesendet)."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("10.255.255.255", 1))
        return s.getsockname()[0]
    except OSError:
        return "127.0.0.1"
    finally:
        s.close()


class Conn:
    """Nicht blockierende TCP-Verbindung. Eine JSON-Nachricht pro Zeile."""
    MAX_BUF = 1 << 20

    def __init__(self, sock):
        sock.setblocking(False)
        try:
            sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)   # keine Nagle-Verzögerung
        except OSError:
            pass
        self.sock = sock
        self.rbuf = b""
        self.wbuf = b""
        self.closed = False
        self.error = ""
        self.pid = None              # Spieler-ID (nur beim Host gesetzt, nach "hello")
        self.last_rx = time.time()

    def send(self, msg):
        self.send_line((json.dumps(msg, separators=(",", ":")) + "\n").encode())

    def send_line(self, line):
        if self.closed:
            return
        self.wbuf += line
        if len(self.wbuf) > self.MAX_BUF // 2:     # Gegenseite liest nicht mehr mit
            self.close("Verbindung zu langsam")

    def flush(self):
        if self.closed or not self.wbuf:
            return
        try:
            n = self.sock.send(self.wbuf)
            self.wbuf = self.wbuf[n:]
        except (BlockingIOError, InterruptedError):
            pass
        except OSError as e:
            self.close(str(e))

    def recv(self):
        """Alle inzwischen vollständig eingetroffenen Nachrichten."""
        out = []
        if not self.closed:
            try:
                for _ in range(64):
                    data = self.sock.recv(65536)
                    if not data:
                        self.close("Verbindung geschlossen")
                        break
                    self.rbuf += data
                    self.last_rx = time.time()
            except (BlockingIOError, InterruptedError):
                pass
            except OSError as e:
                self.close(str(e))
        if b"\n" in self.rbuf:
            *lines, self.rbuf = self.rbuf.split(b"\n")
            for ln in lines:
                if ln:
                    try:
                        out.append(json.loads(ln))
                    except ValueError:
                        pass
        if len(self.rbuf) > self.MAX_BUF:
            self.close("Nachricht zu gross")
        return out

    def close(self, reason=""):
        if not self.closed:
            self.closed = True
            self.error = reason
            try:
                self.sock.close()
            except OSError:
                pass


class Connector(threading.Thread):
    """Baut die Verbindung im Hintergrund auf, damit das Fenster nicht einfriert."""

    def __init__(self, host, port):
        super().__init__(daemon=True)
        self.addr = (host, port)
        self.conn = None
        self.error = ""
        self.done = False
        self.start()

    def run(self):
        try:
            self.conn = Conn(socket.create_connection(self.addr, timeout=4.0))
        except (OSError, ValueError) as e:
            self.error = str(e) or "Keine Antwort"
        self.done = True


class JoinAttempt:
    """Verbinden + 'hello' senden + auf 'welcome' des Hosts warten."""

    def __init__(self, host, port, name):
        self.host, self.name = host, name
        self.thread = Connector(host, port)
        self.conn = None
        self.state = "connecting"      # connecting | waiting | ready | failed
        self.msg = ""
        self.t0 = time.time()
        self.my_id = None
        self.seed = SEED
        self.props = 0
        self.mode = "koth"
        self.limit = 600.0
        self.mobs_on = True
        self.map_raw = None            # Kartendatei des Hosts (None = Standardkarte)
        self.extra = []                # Nachrichten, die schon nach dem welcome eintrafen

    def poll(self):
        if self.state == "connecting" and self.thread.done:
            if self.thread.conn is None:
                self.state, self.msg = "failed", "Verbindung fehlgeschlagen: " + self.thread.error
            else:
                self.conn = self.thread.conn
                self.conn.send({"t": "hello", "v": NET_VERSION, "name": self.name})
                self.state, self.t0 = "waiting", time.time()
        if self.state in ("waiting", "ready"):
            self.conn.flush()
            for m in self.conn.recv():
                if not isinstance(m, dict):
                    continue
                if self.state == "ready":
                    self.extra.append(m)
                elif m.get("t") == "welcome":
                    try:
                        self.my_id, self.seed, self.props = int(m["id"]), int(m["seed"]), int(m["props"])
                        self.mode = m.get("mode") if m.get("mode") in MODES else "koth"
                        self.limit = clampf(float(m.get("limit", 600)), 30.0, 7200.0)
                        self.mobs_on = bool(m.get("mobs", 1))
                        self.map_raw = m.get("map") if isinstance(m.get("map"), dict) else None
                        self.state = "ready"
                    except (KeyError, TypeError, ValueError):
                        self.state, self.msg = "failed", "Ungültige Antwort vom Host"
                elif m.get("t") == "refuse":
                    self.state, self.msg = "failed", str(m.get("why", "Abgelehnt"))
                    break
            if self.state == "waiting":
                if self.conn.closed:
                    self.state, self.msg = "failed", "Host hat die Verbindung beendet"
                elif time.time() - self.t0 > 5.0:
                    self.state, self.msg = "failed", "Keine Antwort vom Host"
            if self.state == "failed":
                self.close()
        return self.state

    def close(self):
        if self.conn is not None:
            self.conn.close("abgebrochen")


class NetServer:
    """Nimmt TCP-Verbindungen an (Port NET_PORT). Wirft OSError, wenn der Port belegt ist."""

    def __init__(self, port=NET_PORT):
        self.lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            if os.name != "nt":      # unter Windows würde das Port-Klau erlauben
                self.lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.lsock.bind(("", port))
            self.lsock.listen(8)
            self.lsock.setblocking(False)
        except OSError:
            self.lsock.close()
            raise
        self.conns = []

    def accept(self):
        for _ in range(8):
            try:
                s, _addr = self.lsock.accept()
            except (BlockingIOError, InterruptedError):
                break
            except OSError:
                break
            self.conns.append(Conn(s))

    def close(self):
        for c in self.conns:
            c.close("Host beendet")
        self.conns = []
        try:
            self.lsock.close()
        except OSError:
            pass


class Beacon:
    """Der Host ruft jede Sekunde per UDP-Broadcast 'hier läuft ein Spiel'."""

    def __init__(self, name, ip, port=NET_PORT, mode=""):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.sock.setblocking(False)
        self.name, self.port, self.mode = name, port, mode
        self.targets = [("255.255.255.255", DISCOVERY_PORT),
                        (ip.rsplit(".", 1)[0] + ".255", DISCOVERY_PORT)]   # typisches /24-WLAN
        self.t = 0.0

    def update(self, dt, nplayers):
        self.t -= dt
        if self.t > 0:
            return
        self.t = 1.0
        msg = json.dumps({"spiel": NET_VERSION, "name": self.name, "port": self.port,
                          "n": nplayers, "mode": self.mode}).encode()
        for tg in self.targets:
            try:
                self.sock.sendto(msg, tg)
            except OSError:
                pass

    def close(self):
        self.sock.close()


class Listener:
    """Hört im Menü auf die Broadcasts der Hosts. hosts: IP -> Infos."""

    def __init__(self):
        self.hosts = {}
        self.sock = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            s.bind(("", DISCOVERY_PORT))
            s.setblocking(False)
            self.sock = s
        except OSError:
            self.sock = None           # keine automatische Suche, IP eintippen geht trotzdem

    def poll(self):
        if self.sock is not None:
            for _ in range(32):
                try:
                    data, addr = self.sock.recvfrom(2048)
                except (BlockingIOError, InterruptedError):
                    break
                except OSError:
                    break
                try:
                    m = json.loads(data.decode())
                    if m.get("spiel") != NET_VERSION:
                        continue
                    self.hosts[addr[0]] = dict(name=str(m.get("name", "?"))[:20],
                                               port=int(m.get("port", NET_PORT)),
                                               n=int(m.get("n", 1)), seen=time.time(),
                                               mode=str(m.get("mode", ""))[:8])
                except (ValueError, AttributeError, TypeError):
                    continue
        now = time.time()
        for ip in [ip for ip, h in self.hosts.items() if now - h["seen"] > 3.5]:
            del self.hosts[ip]
        return self.hosts

    def close(self):
        if self.sock is not None:
            self.sock.close()
            self.sock = None


class HostSession:
    """Host-Seite. Der Host ist selbst Spieler 0 und führt die Welt. Er nimmt
    Mitspieler an, übernimmt deren gemeldete Position/Schüsse und verschickt
    Snapshots. Position und Waffenzustand bleiben beim jeweiligen Spieler
    (kein Ruckeln); Monster, Kugeln, Schaden, Lebenspunkte, Punkte und
    Kistenwaffen entscheidet der Host."""

    def __init__(self, world, name):
        self.world = world
        self.server = NetServer()                 # kann OSError werfen (Port belegt)
        self.ip = local_ip()
        try:
            self.beacon = Beacon(name, self.ip, mode=world.mode)
        except OSError:
            self.beacon = None
        self.next_pid = 1
        self.snap_t = 0.0
        self.events = []

    def close(self):
        self.server.close()
        if self.beacon is not None:
            self.beacon.close()

    def queue_events(self, events):
        """Ereignisse (Treffer, Tod, ...) für den nächsten Snapshot vormerken.
        'shot' nicht: den Rückstoss simuliert jeder Schütze selbst."""
        self.events.extend(e for e in events if e[0] != "shot")

    def refuse(self, c, why):
        c.send({"t": "refuse", "why": why})
        c.flush()
        c.close(why)

    def poll(self, dt):
        self.server.accept()
        now = time.time()
        for c in list(self.server.conns):
            for m in c.recv():
                try:
                    self.handle(c, m)
                except (KeyError, IndexError, TypeError, ValueError):
                    pass                          # kaputte Nachricht ignorieren
            if not c.closed and now - c.last_rx > NET_TIMEOUT:
                c.close("Zeitüberschreitung")
            if c.closed:
                self.server.conns.remove(c)
                if c.pid is not None:
                    self.world.players.pop(c.pid, None)    # seine Waffen sind einfach weg
            else:
                c.flush()

    def handle(self, c, m):
        if not isinstance(m, dict):
            return
        t, w = m.get("t"), self.world
        if t == "hello":
            if c.pid is not None:
                return
            if m.get("v") != NET_VERSION:
                return self.refuse(c, "Andere Spielversion")
            if len(w.players) >= MAX_PLAYERS:
                return self.refuse(c, "Das Spiel ist voll")
            pid = self.next_pid
            self.next_pid += 1
            name = str(m.get("name") or f"Spieler{pid}")[:16]
            x, y = w.first_spawn(pid)
            w.players[pid] = Player(x, y, w, pid, name)
            c.pid = pid
            c.send({"t": "welcome", "id": pid, "seed": w.seed, "props": w.prop_count(),
                    "mode": w.mode, "limit": w.limit, "mobs": 1 if w.mobs_on else 0,
                    "map": getattr(w, "map_raw", None)})
            return
        pl = w.players.get(c.pid)
        if pl is None:
            return
        if t == "st":                             # Position/Blickrichtung des Spielers
            x, y, z, h, p = m["p"]
            if not finite(x, y, z, h, p):
                return
            pl.x, pl.y = clampf(x, -5, WORLD + 5), clampf(y, -5, WORLD + 5)
            pl.z = clampf(z, -20, 60)
            pl.heading, pl.pitch = h, clampf(p, -90, 90)
            pl.moving = bool(m.get("mv"))
            cur = m.get("cur")
            if isinstance(cur, int) and 0 <= cur < len(WEAPONS) and pl.hp > 0:
                pl.cur = cur
                note_hand(pl)
            ln = m.get("ln", 0.0)
            pl.lean = clampf(float(ln), -LEAN_MAX, LEAN_MAX) if finite(ln) else 0.0
            cr = m.get("cr", 0.0)
            pl.crouch = clampf(float(cr), 0.0, 1.0) if finite(cr) else 0.0
            pl.running = bool(m.get("rn")) and pl.moving
            pl.jet_on = bool(m.get("jt")) and wears(pl, "jetpack")    # grobe Prüfung: nur mit Jetpack
            pl.melee_out = bool(m.get("mo"))
            pl.trig = bool(m.get("tg")) and (pl.mount >= 0 or pl.heli >= 0)
            pn_m = m.get("hc")                    # Pilot meldet seinen Helikopter
            if isinstance(pn_m, list) and len(pn_m) in (9, 10) and finite(*pn_m):
                hc = w.heli_by_id(int(pn_m[0]))
                if hc is not None and hc.driver == pl.pid and hc.hp > 0:
                    hc.x, hc.y = clampf(pn_m[1], -5, WORLD + 5), clampf(pn_m[2], -5, WORLD + 5)
                    hc.z = clampf(pn_m[3], -5, HELI_CEIL + 20)
                    hc.heading, hc.pitch, hc.roll = pn_m[4], clampf(pn_m[5], -40, 40), clampf(pn_m[6], -60, 60)
                    hc.speed = clampf(pn_m[7], 0, HELI_VMAX * 1.5)
                    hc.ground = bool(pn_m[8])
                    if len(pn_m) > 9 and pn_m[9] > 0:
                        w.heli_crash(hc, pn_m[9])     # Aufprall nach Lahmlegen (Host prüft stall_t)
            vh = m.get("vh")                      # Fahrer meldet sein Fahrzeug
            if isinstance(vh, list) and len(vh) == 6 and finite(*vh):
                v = w.vehicle_by_id(int(vh[0]))
                if v is not None and v.driver == pl.pid and v.hp > 0:
                    v.x, v.y = clampf(vh[1], -5, WORLD + 5), clampf(vh[2], -5, WORLD + 5)
                    v.z, v.heading = clampf(vh[3], -20, 60), vh[4]
                    v.speed = clampf(vh[5], -VEH_REV - 2, VEH_MAX + 2)
        elif t == "melee":                        # Nahkampf-Schlag: Treffer entscheidet der Host
            d = m.get("d")
            mw = MELEE[pl.melee] if 0 <= pl.melee < len(MELEE) else MELEE[START_MELEE]
            now = time.time()
            if (pl.hp > 0 and w.phase == "play" and pl.stun_t <= 0.3 and isinstance(d, list) and len(d) == 3
                    and finite(*d) and now - getattr(pl, "last_swing", 0.0) >= mw.interval * 0.7):
                pl.last_swing = now
                pl.melee_out = True
                w.melee_hit(pl, norm((float(d[0]), float(d[1]), float(d[2]))))
        elif t == "fire":                         # ein Schuss: Kugeln erzeugt der Host
            idx = m.get("w")
            if (pl.hp <= 0 or w.phase != "play" or not isinstance(idx, int)
                    or not 0 <= idx < len(WEAPONS)):
                return
            if pl.stun_t > 0.3:
                return                            # betäubt: kein Schuss (kleine Toleranz für Laufzeit)
            wp = WEAPONS[idx]                     # Schaden/Tempo kommen vom Host, nicht vom Client
            if idx not in pl.slots:
                return                            # nur Waffen, die er laut Host wirklich trägt
            dirs = []
            for d in (m.get("d") or [])[:wp.pellets]:
                if isinstance(d, list) and len(d) == 3 and finite(*d):
                    dirs.append(norm((float(d[0]), float(d[1]), float(d[2]))))
            if not dirs:
                return
            eye = (pl.x, pl.y, pl.z + eye_h(pl))
            o = m.get("o")
            if isinstance(o, list) and len(o) == 3 and finite(*o):
                if math.dist(o, eye) < 3.0:       # gemeldeter Mündungspunkt, wenn plausibel
                    eye = (float(o[0]), float(o[1]), float(o[2]))
            pl.cur = idx
            note_hand(pl)
            w.add_shot(pl, eye, dirs, wp)
        elif t == "gren":                         # Granate geworfen: der Host simuliert sie
            d, o = m.get("d"), m.get("o")
            if (pl.hp > 0 and pl.grenades > 0 and w.phase == "play" and pl.vehicle < 0
                    and isinstance(d, list) and len(d) == 3 and finite(*d)):
                eye = (pl.x, pl.y, pl.z + eye_h(pl))
                if isinstance(o, list) and len(o) == 3 and finite(*o) and math.dist(o, eye) < 3.0:
                    eye = (float(o[0]), float(o[1]), float(o[2]))
                pl.grenades -= 1
                pl.protect = 0.0
                w.spawn_grenade(pl.pid, eye, norm((float(d[0]), float(d[1]), float(d[2]))))
        elif t == "use":                          # F (alt: V) gedrückt: Kiste, Waffe, Fahrzeug, Geschütz, Flugzeug
            w.use_object(pl, bool(m.get("alt")))
        elif t == "strikego":                     # Tomahawk mit gewähltem Einschlagpunkt abfeuern
            b = w.button
            if (finite(m.get("x", float("nan")), m.get("y", float("nan"))) and pl.hp > 0
                    and math.hypot(pl.x - b.x, pl.y - b.y) < 3.5 and abs(pl.z - b.z) < 2.5):
                d = m.get("d")
                w.press_button(pl, float(m["x"]), float(m["y"]), d if isinstance(d, int) else None)
        elif t == "hr":                           # Rakete aus dem Helikopter
            w.heli_rocket(pl)
        elif t == "fall":                         # Fallschaden, vom Mitspieler beim Aufprall gemeldet
            d = m.get("d")
            if finite(d) and pl.hp > 0 and pl.vehicle < 0 and pl.heli < 0:
                w.damage_player(pl, clampf(float(d), 0.0, PLAYER_HP * 2), -1, WI_FALL)
        elif t == "respawn":
            if w.can_respawn(pl):
                w.respawn_player(pl)              # Ereignis 'respawn' sagt dem Client, wohin

    def send(self, dt):
        """Snapshot an alle Mitspieler (mit SNAP_RATE) und Host-Suche rufen."""
        w = self.world
        if self.beacon is not None:
            self.beacon.update(dt, len(w.players))
        clients = [c for c in self.server.conns if c.pid is not None and not c.closed]
        self.snap_t -= dt
        if self.snap_t > 0:
            return
        self.snap_t = 1.0 / SNAP_RATE
        if not clients:
            self.events.clear()
            return
        self.snap_n = getattr(self, "snap_n", 0) + 1
        snap = {"t": "snap", "rd": w.respawn_delay,
                "pl": [[p.pid, r2(p.x), r2(p.y), r2(p.z), r1(p.heading), r1(p.pitch), r1(p.hp),
                        p.cur, 1 if p.moving else 0, p.name, p.kills, p.deaths, r1(p.score),
                        r1(p.protect), r2(p.lean), r2(p.crouch), r1(p.stun_t),
                        BUFF_KINDS.index(p.buff) if p.buff in BUFF_KINDS else -1, r1(p.buff_t),
                        int(p.max_hp), gear_list(p), r1(p.shield_hp), 1 if p.jet_on else 0,
                        p.melee, 1 if p.melee_out else 0]
                       for p in w.players.values()],
                "mb": [[m.id, KINDS.index(m.kind), r2(m.x), r2(m.y), r2(m.z), r1(m.heading),
                        STATES.index(m.state), r1(m.hp), r2(m.speed_now), r2(m.atk_t),
                        r2(m.hurt_t), r2(m.dead_t), m.atk_kind] for m in w.mobs],
                "bl": [[b.bid, r2(b.x), r2(b.y), r2(b.z), r1(b.vx), r1(b.vy), r1(b.vz),
                        r1(b.travel), b.wi, b.owner] for b in w.bullets],
                "cr": [[c.cid, CRATE_KINDS.index(c.kind), r2(c.x), r2(c.y), r2(c.z), 1 if c.bonus else 0]
                       for c in w.crates],
                "ro": [[r.rid, r2(r.x), r2(r.y), r2(r.z), r1(r.vx), r1(r.vy), r1(r.vz)] for r in w.rocks],
                "gr": [[g.gid, r2(g.x), r2(g.y), r2(g.z), r1(g.vx), r1(g.vy), r1(g.vz), r1(g.fuse)]
                       for g in w.grenades],
                "dr": [[d.did, r2(d.x), r2(d.y), r2(d.z), d.wi, d.gear, d.melee] for d in w.drops],
                "vh": [[v.id, r2(v.x), r2(v.y), r2(v.z), r1(v.heading), r1(v.speed), r1(v.hp),
                        v.driver, r1(v.dead_t), r1(v.stall_t)] for v in w.vehicles],
                "gm": [1 if w.phase == "over" else 0, r1(w.time_left), r1(w.over_t)],
                "tu": [[t.id, r1(t.heading), r1(t.pitch), r2(t.heat), 1 if t.over else 0,
                        1 if t.firing else 0, t.op] for t in w.turrets],
                "hc": [[q.id, r2(q.x), r2(q.y), r2(q.z), r1(q.heading), r1(q.pitch), r1(q.roll),
                        r1(q.speed), r1(q.hp), q.driver, r1(q.dead_t), int(q.mg), q.rk, 1 if q.ground else 0,
                        1 if q.firing else 0, r1(q.stall_t)] for q in w.helis],
                "tm": [w.strike, r1(w.strike_t), w.strike_by, w.strike_dur, r1(w.strike_wait),
                       r1(w.strike_ang), r1(w.strike_x), r1(w.strike_y)],   # Ziel nur für den Anflug, nie angezeigt
                "k": w.kills, "ev": self.events}
        if self.snap_n % SB_EVERY == 1:                  # Scoreboard-Werte (Tab) - selten genügt
            snap["sb"] = [[p.pid] + list(stat_summary(p)) for p in w.players.values()]
        line = (json.dumps(snap, separators=(",", ":")) + "\n").encode()
        self.events = []
        for c in clients:
            c.send_line(line)
            self.send_toma(c)
            c.flush()

    def send_toma(self, c):
        """Wo die Tomahawk-Säule steht (bzw. versinkt), erfährt ein Mitspieler nur in Sichtweite (TOMA_SEE_R);
        dazu seine eigene Sperrzeit. Geschickt bei jeder Änderung und sonst etwa jede Sekunde."""
        w = self.world
        pl = w.players.get(c.pid)

        def seen(i):
            if i < 0 or pl is None or pl.hp <= 0:
                return -1
            x, y, _z, _h = w.toma_spots[i]
            return i if math.hypot(pl.x - x, pl.y - y) <= TOMA_SEE_R else -1
        i, si = seen(w.toma_idx), seen(w.toma_sink_idx)
        now = time.time()
        if getattr(c, "tb_last", None) != (i, si) or now - getattr(c, "tb_t", 0.0) > 1.0:
            c.send({"t": "tb", "i": i, "a": r1(w.toma_age), "s": si, "st": r1(w.toma_sink_t),
                    "l": r1(w.toma_lock.get(c.pid, 0.0))})
            c.tb_last, c.tb_t = (i, si), now


class NetMob:
    """Monster-Stellvertreter beim Mitspieler: wird aus den Snapshots gefüttert und
    gleitet weich auf die gemeldete Position. Hat die Felder, die MobView braucht."""

    def __init__(self, mid, kind, x, y, z, heading):
        k = MOB_KINDS[kind]
        self.id, self.kind = mid, kind
        self.scale = k["scale"]
        self.radius = k.get("hit_r", 0.45 * self.scale)
        self.max_hp = self.hp = k["hp"]
        self.x = self.tx = x
        self.y = self.ty = y
        self.z = self.tz = z
        self.heading = self.th = heading
        self.state = "idle"
        self.atk_t = self.dead_t = self.hurt_t = self.speed_now = self.phase = 0.0
        self.atk_kind = 0
        self.height = k.get("hit_h", 1.9 * self.scale)

    def windup(self):
        k = MOB_KINDS[self.kind]
        if self.atk_kind == 2:
            return k["rock_windup"]
        return k["slam_windup"] if self.atk_kind == 1 else k["windup"]

    def recover(self):
        k = MOB_KINDS[self.kind]
        return k.get("rock_recover", 1.0) if self.atk_kind == 2 else k.get("recover", 0.4)

    def apply(self, x, y, z, heading, state, hp, speed, atk, hurt, dead):
        self.tx, self.ty, self.tz, self.th = x, y, z, heading
        if state != self.state:
            self.state, self.atk_t, self.dead_t = state, atk, dead
        else:                                      # sonst läuft die Zeit lokal weiter
            if abs(atk - self.atk_t) > 0.15:
                self.atk_t = atk
            if abs(dead - self.dead_t) > 0.3:
                self.dead_t = dead
        self.hp, self.speed_now = hp, speed
        self.hurt_t = max(self.hurt_t, hurt)

    def smooth(self, dt):
        a = min(1.0, 16.0 * dt)
        self.x += (self.tx - self.x) * a
        self.y += (self.ty - self.y) * a
        self.z += (self.tz - self.z) * a
        self.heading += ((self.th - self.heading + 180.0) % 360.0 - 180.0) * a
        if self.state == "attack":
            self.atk_t += dt
        elif self.state == "dead":
            self.dead_t += dt
        self.hurt_t = max(0.0, self.hurt_t - dt)
        self.phase += self.speed_now * dt * 2.0


class ClientSession:
    """Mitspieler-Seite: schickt eigene Position/Schüsse zum Host und baut aus den
    Snapshots Monster, Kugeln, Kisten, Punkte und die anderen Spieler in der lokalen World auf."""

    def __init__(self, conn, world, my_id, backlog=()):
        self.conn, self.world, self.my_id = conn, world, my_id
        world.set_toma(-1)                      # wo die Kapsel ist, sagt nur der Host (und nur in der Nähe)
        self.mobs = {}               # Monster-ID -> NetMob
        self.bullets = {}            # Kugel-ID -> Bullet (nur zum Anzeigen)
        self.grenades = {}           # Granaten-ID -> Grenade (nur zum Anzeigen)
        self.drops = {}              # Drop-ID -> Drop (fallengelassene Waffen)
        self.events = []             # vom Host gemeldete Ereignisse
        self.hp = None               # Lebenspunkte: entscheidet der Host
        self.lost = ""               # Text, wenn die Verbindung weg ist
        self.send_t = 0.0
        for m in backlog:
            self.handle(m)

    def close(self):
        self.conn.close("beendet")

    def poll(self, dt):
        if self.lost:
            return
        for m in self.conn.recv():
            self.handle(m)
        if not self.conn.closed and time.time() - self.conn.last_rx > NET_TIMEOUT:
            self.conn.close("Zeitüberschreitung")
        if self.conn.closed:
            self.lost = self.conn.error or "Verbindung getrennt"
        else:
            self.conn.flush()

    def handle(self, m):
        if not isinstance(m, dict):
            return
        try:
            if m.get("t") == "snap":
                self.apply_snapshot(m)
            elif m.get("t") == "tb":                 # Tomahawk-Säule in Sichtweite (oder -1 = keine)
                w = self.world
                w.set_toma(int(m.get("i", -1)), float(m.get("a", 0.0)))
                w.toma_sink_idx = int(m.get("s", -1))
                if not 0 <= w.toma_sink_idx < len(w.toma_spots):
                    w.toma_sink_idx = -1
                w.toma_sink_t = float(m.get("st", 0.0))
                lk = float(m.get("l", 0.0))
                if lk > 0:
                    w.toma_lock[self.my_id] = lk
                else:
                    w.toma_lock.pop(self.my_id, None)
        except (KeyError, IndexError, TypeError, ValueError):
            pass

    def apply_snapshot(self, m):
        w = self.world
        try:
            w.respawn_delay = float(m.get("rd", w.respawn_delay))
        except (TypeError, ValueError):
            pass
        seen = set()
        for row in m["pl"]:
            pid, x, y, z, h, p, hp, cur, mv, name, kl, de, sc, prot, ln, cr = row[:16]
            st, bi, bt, mx = (row[16:20] + [0.0, -1, 0.0, PLAYER_HP])[:4] if len(row) < 20 else row[16:20]
            gl = row[20] if len(row) > 20 and isinstance(row[20], list) else [-1, -1, -1]
            gear = {sl: (v if isinstance(v, int) and 0 <= v < len(GEAR) else None) for sl, v in zip(GEAR_SLOTS, gl)}
            shp = row[21] if len(row) > 21 else SHIELD_HP
            jet = bool(row[22]) if len(row) > 22 else False
            mel = row[23] if len(row) > 23 and isinstance(row[23], int) and 0 <= row[23] < len(MELEE) else START_MELEE
            mout = bool(row[24]) if len(row) > 24 else False
            buff = BUFF_KINDS[bi] if isinstance(bi, int) and 0 <= bi < len(BUFF_KINDS) else None
            if pid == self.my_id:
                self.hp = hp                       # Position bestimmt der Spieler selbst
                me = w.players.get(pid)
                if me is not None:
                    me.kills, me.deaths, me.score, me.protect = kl, de, sc, prot
                    me.buff, me.buff_t, me.max_hp = buff, bt, float(mx)
                    me.gear, me.shield_hp = gear, shp      # Ausrüstung und Schild entscheidet der Host
                    me.melee = mel                         # welche Nahkampfwaffe (ziehen tut man selbst)
                    if hp <= 0:                    # Betäubung kommt per Ereignis; tot ist sie vorbei
                        me.stun_t = 0.0
                continue
            pl = w.players.get(pid)
            if pl is None:
                pl = w.players[pid] = Player(x, y, w, pid, str(name))
            pl.x, pl.y, pl.z, pl.heading, pl.pitch = x, y, z, h, p
            pl.hp, pl.cur, pl.moving, pl.lean = hp, cur, bool(mv), ln
            pl.crouch = cr
            pl.kills, pl.deaths, pl.score, pl.protect = kl, de, sc, prot
            pl.stun_t, pl.buff, pl.buff_t, pl.max_hp = st, buff, bt, float(mx)
            pl.gear, pl.shield_hp, pl.jet_on = gear, shp, jet
            pl.melee, pl.melee_out = mel, mout
            seen.add(pid)
        for pid in [pid for pid in w.players if pid != self.my_id and pid not in seen]:
            del w.players[pid]
        for row in m.get("sb", ()):                      # Tab-Scoreboard: Monster, Kisten, Buffs
            q = w.players.get(row[0])
            if q is not None and len(row) >= 4:
                q.sb = tuple(int(v) for v in row[1:4])

        seen = set()
        for row in m["mb"]:
            mid, ki, x, y, z, hd, si, hp, spd, atk, hurt, dead = row[:12]
            if not 0 <= ki < len(KINDS):
                continue
            nm = self.mobs.get(mid)
            if nm is None:
                nm = self.mobs[mid] = NetMob(mid, KINDS[ki], x, y, z, hd)
            nm.apply(x, y, z, hd, STATES[si], hp, spd, atk, hurt, dead)
            nm.atk_kind = row[12] if len(row) > 12 else 0
            seen.add(mid)
        for mid in [i for i in self.mobs if i not in seen]:
            del self.mobs[mid]
        w.mobs = list(self.mobs.values())

        seen = set()
        for row in m["bl"]:
            bid, x, y, z, vx, vy, vz, tr, wi = row[:9]
            b = self.bullets.get(bid)
            if b is None:
                b = self.bullets[bid] = Bullet(x, y, z, vx, vy, vz, 0.0, row[9] if len(row) > 9 else -1, bid, wi)
            b.x, b.y, b.z, b.vx, b.vy, b.vz, b.travel = x, y, z, vx, vy, vz, tr
            seen.add(bid)
        for bid in [i for i in self.bullets if i not in seen]:
            del self.bullets[bid]
        w.bullets = list(self.bullets.values())

        old = {c.cid: c for c in w.crates}
        crates = []
        for row in m.get("cr", ()):
            cid, ki, x, y, z = row[:5]
            c = old.get(cid)
            if c is None:
                c = Crate(cid, x, y, z, CRATE_KINDS[ki] if 0 <= ki < len(CRATE_KINDS) else "common")
                c.bonus = bool(row[5]) if len(row) > 5 else False
            crates.append(c)
        w.crates = crates
        oldr = {r.rid: r for r in w.rocks}
        rocks = []
        for rid, x, y, z, vx, vy, vz in m.get("ro", ()):
            r = oldr.get(rid) or Rock(rid, x, y, z, vx, vy, vz)
            r.x, r.y, r.z, r.vx, r.vy, r.vz = x, y, z, vx, vy, vz
            rocks.append(r)
        w.rocks = rocks

        seen = set()
        for gid, x, y, z, vx, vy, vz, fuse in m.get("gr", ()):
            g = self.grenades.get(gid)
            if g is None:
                g = self.grenades[gid] = Grenade(gid, x, y, z, vx, vy, vz, -1, fuse)
            g.x, g.y, g.z, g.vx, g.vy, g.vz, g.fuse = x, y, z, vx, vy, vz, fuse
            seen.add(gid)
        for gid in [i for i in self.grenades if i not in seen]:
            del self.grenades[gid]
        w.grenades = list(self.grenades.values())

        seen = set()
        for row in m.get("dr", ()):
            did, x, y, z, wi = row[:5]
            d = self.drops.get(did)
            if d is None:
                d = self.drops[did] = Drop(did, x, y, z, wi, row[5] if len(row) > 5 else -1,
                                           row[6] if len(row) > 6 else -1)
            seen.add(did)
        for did in [i for i in self.drops if i not in seen]:
            del self.drops[did]
        w.drops = list(self.drops.values())

        for row in m.get("vh", ()):
            vid, x, y, z, hd, sp, hp, drv, dead = row[:9]
            v = w.vehicle_by_id(vid)
            if v is None:
                continue
            v.hp, v.driver, v.dead_t = hp, drv, dead
            v.stall_t = row[9] if len(row) > 9 else 0.0
            if drv != self.my_id:                  # den eigenen Wagen bestimmt der Fahrer selbst
                v.x, v.y, v.z, v.heading, v.speed = x, y, z, hd, sp
        taken = {v.driver: v.id for v in w.vehicles if v.driver >= 0}
        for pid, pl in w.players.items():          # wer sitzt in welchem Fahrzeug?
            pl.vehicle = taken.get(pid, -1)
        ops = {}
        for tid, hd, pt, heat, over, fr, op in m.get("tu", ()):
            if 0 <= tid < len(w.turrets):
                t = w.turrets[tid]
                t.heat, t.over, t.firing, t.op = heat, bool(over), bool(fr), op
                if op != self.my_id:                 # den eigenen Zielwinkel bestimmt der Schütze selbst
                    t.heading, t.pitch = hd, pt
                if op >= 0:
                    ops[op] = tid
        for pid, pl in w.players.items():
            pl.mount = ops.get(pid, -1)
        for row in m.get("hc", ()):
            qid, x, y, z, hd, pt, rl, sp, hp, drv, dd, mg, rk, gr, fr = row[:15]
            q = w.heli_by_id(qid)
            if q is None:
                continue
            q.hp, q.driver, q.dead_t, q.mg, q.rk, q.firing = hp, drv, dd, mg, rk, bool(fr)
            q.stall_t = row[15] if len(row) > 15 else -1.0
            if drv != self.my_id:                    # den eigenen Helikopter bestimmt der Pilot selbst
                q.x, q.y, q.z, q.heading, q.pitch, q.roll, q.speed, q.ground = x, y, z, hd, pt, rl, sp, bool(gr)
        pil = {q.driver: q.id for q in w.helis if q.driver >= 0}
        for pid, pl in w.players.items():
            pl.heli = pil.get(pid, -1)
        tm = m.get("tm")
        if tm:
            w.strike, w.strike_t, w.strike_by = tm[0], tm[1], tm[2]
            if len(tm) > 3:
                w.strike_dur = tm[3]
            if len(tm) > 4:
                w.strike_wait = tm[4]
            if len(tm) > 7:
                w.strike_ang, w.strike_x, w.strike_y = tm[5], tm[6], tm[7]
        gm = m.get("gm")
        if gm:
            w.phase = "over" if gm[0] else "play"
            w.time_left, w.over_t = gm[1], gm[2]
        w.kills = m.get("k", w.kills)
        for e in m.get("ev", ()):
            self.events.append(tuple(e))

    def advance(self, dt):
        """Zwischen zwei Snapshots weiterrechnen: Kugeln fliegen (nur zur Anzeige),
        Monster gleiten weich."""
        for b in self.bullets.values():
            b.vz -= GRAV_BULLET * b.grav * dt
            b.x += b.vx * dt
            b.y += b.vy * dt
            b.z += b.vz * dt
            b.travel += math.sqrt(b.vx ** 2 + b.vy ** 2 + b.vz ** 2) * dt
        for nm in self.mobs.values():
            nm.smooth(dt)
        w = self.world
        for g in self.grenades.values():           # zwischen zwei Snapshots weiterfliegen
            g.vz -= GREN_G * dt
            g.x += g.vx * dt
            g.y += g.vy * dt
            g.z = max(g.z + g.vz * dt, w.ground_for(g.x, g.y, g.z) + 0.1)
            g.fuse -= dt
        if w.strike == 1:
            w.strike_t = max(0.0, w.strike_t - dt)
        elif w.strike == 2 and w.strike_wait > 0:
            w.strike_wait = max(0.0, w.strike_wait - dt)
        w.toma_age += dt                           # Säule: Hochfahren / Versinken zwischen den Nachrichten
        if w.toma_sink_idx >= 0:
            w.toma_sink_t += dt
        for pid in list(w.toma_lock):
            w.toma_lock[pid] -= dt
            if w.toma_lock[pid] <= 0:
                del w.toma_lock[pid]
        w.sync_turret_pos()

    def send_state(self, dt, pl):
        self.send_t -= dt
        if self.send_t > 0:
            return
        self.send_t = 1.0 / INPUT_RATE
        msg = {"t": "st", "p": [r2(pl.x), r2(pl.y), r2(pl.z), r1(pl.heading), r1(pl.pitch)],
               "mv": 1 if pl.moving else 0, "cur": pl.cur, "ln": r2(pl.lean),
               "cr": r2(pl.crouch), "rn": 1 if getattr(pl, "running", False) else 0,
               "jt": 1 if getattr(pl, "jet_on", False) else 0,
               "mo": 1 if getattr(pl, "melee_out", False) else 0}
        v = self.world.vehicle_by_id(pl.vehicle) if pl.vehicle >= 0 else None
        if v is not None:
            msg["vh"] = [v.id, r2(v.x), r2(v.y), r2(v.z), r1(v.heading), r1(v.speed)]
        if pl.mount >= 0 or pl.heli >= 0:
            msg["tg"] = 1 if pl.trig else 0
        q = self.world.heli_by_id(pl.heli) if pl.heli >= 0 else None
        if q is not None:
            msg["hc"] = [q.id, r2(q.x), r2(q.y), r2(q.z), r1(q.heading), r1(q.pitch), r1(q.roll),
                         r1(q.speed), 1 if q.ground else 0, r1(q.impact)]
            q.impact = 0.0
        self.conn.send(msg)

    def send_grenade(self, pl, eye, d):
        """World.gren_sink: den Wurf dem Host melden (er simuliert die Granate)."""
        self.conn.send({"t": "gren", "o": [r2(c) for c in eye], "d": [round(c, 4) for c in d]})
        self.conn.flush()

    def send_shot(self, pl, eye, dirs, w):
        """World.shot_sink: den Schuss dem Host melden (er erzeugt die Kugeln)."""
        self.conn.send({"t": "fire", "w": pl.cur, "o": [r2(v) for v in eye],
                        "d": [[round(v, 4) for v in d] for d in dirs]})
        self.conn.flush()

    def send_strike(self, x, y, dur=None):
        self.conn.send({"t": "strikego", "x": round(float(x), 1), "y": round(float(y), 1),
                        "d": int(dur) if dur in STRIKE_OPTIONS else None})
        self.conn.flush()

    def send_melee(self, pl, d):
        """World.melee_sink: Nahkampf-Schlag dem Host melden."""
        self.conn.send({"t": "melee", "d": [round(v, 4) for v in d]})
        self.conn.flush()

    def send_use(self, alt=False):
        self.conn.send({"t": "use", "alt": 1} if alt else {"t": "use"})

    def send_rocket(self):
        self.conn.send({"t": "hr"})
        self.conn.flush()

    def send_fall(self, dmg):
        """Fallschaden melden (die eigene Figur bewegt der Mitspieler selbst, Schaden rechnet der Host)."""
        self.conn.send({"t": "fall", "d": round(float(dmg), 1)})
        self.conn.flush()

    def request_respawn(self):
        self.conn.send({"t": "respawn"})


class PlayerView:
    """Darstellung eines Mitspielers: Figur mit Waffe, Namensschild, Lebensbalken."""

    def __init__(self, p):
        look = dict(skin=(0.88, 0.72, 0.58), cloth=PLAYER_COLORS[p.pid % len(PLAYER_COLORS)],
                    eye=(0.1, 0.1, 0.1), w=0.5, horns=False)
        self.root, self.torso, self.legL, self.legR, self.bar, self.fg = build_mob("player", look)
        gm = Mesh()
        box(gm, 0.2, 0.32, 0.4, 0.06, 0.5, 0.09, (0.15, 0.15, 0.17))     # Waffe in der Hand
        self.gun_node = self.torso.attachNewNode(gm.node("gun"))
        self.melee_hand = self.torso.attachNewNode("melee_hand")       # Nahkampfwaffe (gezogen)
        self.melee_hand.setPos(0.24, 0.22, 0.42)
        self.melee_shown, self.melee_node, self.swing_t = None, None, 0.0
        tn = TextNode("name")
        tn.setText(p.name)
        tn.setAlign(TextNode.ACenter)
        tn.setTextColor(1, 1, 1, 1)
        tn.setShadow(0.06, 0.06)
        tn.setShadowColor(0, 0, 0, 1)
        tag = self.root.attachNewNode(tn)
        tag.setPos(0, 0, 2.45)
        tag.setScale(0.32)
        tag.setBillboardPointEye()
        tag.setLightOff()
        tag.setFogOff()
        self.x, self.y, self.z, self.h = p.x, p.y, p.z, p.heading
        self.phase = 0.0
        self.dead_t = 0.0
        self.gear_shown = None
        self.gear_nodes = []
        fl = Mesh(lit=False)
        box(fl, 0, -0.28, -0.32, 0.14, 0.14, 0.35, (1.0, 0.6, 0.15))
        self.jet_flame = self.torso.attachNewNode(fl.node("flamme"))
        self.jet_flame.setFogOff()
        self.jet_flame.hide()

    def show_gear(self, p):
        """Getragene Ausrüstung als einfache Formen an die Figur hängen (Helm, Platte/Weste/Jetpack, Schuhe)."""
        key = tuple(gear_list(p))
        if key == self.gear_shown:
            return
        self.gear_shown = key
        for n in self.gear_nodes:
            n.removeNode()
        self.gear_nodes = []
        for sl, gi in zip(GEAR_SLOTS, key):
            if gi < 0:
                continue
            if sl == "head":
                n = self.torso.attachNewNode(gear_model(gi).node("gear"))
                n.setPos(0, 0.02, 1.07)
            elif sl == "torso":
                n = self.torso.attachNewNode(gear_model(gi).node("gear"))
                n.setPos(0, 0, 0.36)
            else:                                        # je ein Schuh an jedem Bein (läuft mit)
                for leg in (self.legL, self.legR):
                    n = leg.attachNewNode(gear_model(gi, sides=(0,)).node("gear"))
                    n.setPos(0, 0.04, -0.72)
                    self.gear_nodes.append(n)
                continue
            self.gear_nodes.append(n)

    def update(self, p, dt):
        if math.hypot(p.x - self.x, p.y - self.y) > 8.0:                 # Sprung (Respawn)
            self.x, self.y, self.z, self.h = p.x, p.y, p.z, p.heading
        out = bool(getattr(p, "melee_out", False))
        mi = getattr(p, "melee", START_MELEE)
        if out and self.melee_shown != mi:
            if self.melee_node is not None:
                self.melee_node.removeNode()
            self.melee_node = self.melee_hand.attachNewNode(melee_model(mi, 1.4).node("m"))
            self.melee_shown = mi
        (self.gun_node.hide if out else self.gun_node.show)()
        (self.melee_hand.show if out else self.melee_hand.hide)()
        self.swing_t = max(0.0, self.swing_t - dt)
        u = 1.0 - self.swing_t / 0.35 if self.swing_t > 0 else 1.0
        self.melee_hand.setHpr(-70.0 * math.sin(math.pi * u) if self.swing_t > 0 else 0.0,
                               35.0 - 60.0 * math.sin(math.pi * u) if self.swing_t > 0 else 35.0, 0)
        a = min(1.0, 15.0 * dt)
        self.x += (p.x - self.x) * a
        self.y += (p.y - self.y) * a
        self.z += (p.z - self.z) * a
        self.h += ((p.heading - self.h + 180.0) % 360.0 - 180.0) * a
        r = self.root
        r.setPos(self.x, self.y, self.z)
        (r.hide if p.heli >= 0 else r.show)()                           # Piloten sieht man im Cockpit nicht
        if p.hp <= 0:                                                    # umfallen
            self.dead_t += dt
            t = min(1.0, self.dead_t / 0.5)
            r.setHpr(self.h, 90.0 * t * (2 - t), 0)
            r.setSz(1.0)
            r.setColorScale(0.7, 0.7, 0.7, 1)
            self.bar.hide()
            return
        self.dead_t = 0.0
        self.show_gear(p)
        (self.jet_flame.show if getattr(p, "jet_on", False) else self.jet_flame.hide)()
        if getattr(p, "jet_on", False):
            self.jet_flame.setSz(0.8 + 0.4 * math.sin(time.time() * 40.0))
        if getattr(p, "stun_t", 0.0) > 0:                                  # betäubt: blau flackern
            f = 0.5 + 0.5 * math.sin(time.time() * 40.0)
            r.setColorScale(0.5 + 0.4 * f, 0.7 + 0.3 * f, 1.6 + 0.6 * f, 1)
        else:
            r.clearColorScale()
        r.setHpr(self.h, 0, 0)
        r.setSz(1.0 - (1.0 - CROUCH_H / PLAYER_H) * p.crouch)               # geduckt
        self.bar.show()
        self.fg.setSx(max(min(1.0, p.hp / getattr(p, "max_hp", PLAYER_HP)), 0.001))
        mv = 1.0 if p.moving else 0.0
        self.phase += mv * 14.0 * dt
        sw = math.sin(self.phase) * mv
        self.legL.setP(sw * 40)
        self.legR.setP(-sw * 40)
        self.torso.setZ(0.75 + abs(math.sin(self.phase)) * 0.05 * mv)
        self.torso.setR(p.lean / LEAN_MAX * 14.0)          # Lehnen: Oberkörper kippt zur Seite


# --------------------------------------------------------------- Ton
SR = 22050


def synth_sounds():
    """Alle Geräusche werden beim Start errechnet (keine Audiodateien nötig). Gibt {Name: [Samples -1..1]} zurück."""
    rng = random.Random(7)
    tp = 2 * math.pi

    def noise(n):
        return [rng.uniform(-1.0, 1.0) for _ in range(n)]

    def lowpass(x, a):
        y, out = 0.0, []
        for v in x:
            y += a * (v - y)
            out.append(y)
        return out

    def env(n, k):
        return [math.exp(-k * i / SR) for i in range(n)]

    def sweep(n, f0, f1, k):                       # Sinus, dessen Frequenz von f0 nach f1 absinkt
        ph, out = 0.0, []
        for i in range(n):
            t = i / SR
            ph += tp * (f1 + (f0 - f1) * math.exp(-k * t)) / SR
            out.append(math.sin(ph))
        return out

    def mix(*parts):
        n = max(len(p) for p, _g in parts)
        out = [0.0] * n
        for p, g in parts:
            for i, v in enumerate(p):
                out[i] += v * g
        return out

    def mul(a, b):
        return [x * y for x, y in zip(a, b)]

    def delay(x, off, g):                          # Hall: verzögerte, leisere Kopie
        o = int(off * SR)
        out = list(x) + [0.0] * o
        for i, v in enumerate(x):
            out[i + o] += v * g
        return out

    def norm(x, peak):
        m = max(abs(v) for v in x) or 1.0
        return [v * peak / m for v in x]

    def gun(dur, crack_k, body_a, body_k, f0, f1, tk, echo=0.0, peak=0.9):
        n = int(dur * SR)
        s = mix((mul(noise(n), env(n, crack_k)), 1.0),
                (mul(lowpass(noise(n), body_a), env(n, body_k)), 1.1),
                (mul(sweep(n, f0, f1, tk), env(n, tk * 0.7)), 0.9))
        if echo:
            s = delay(s, echo, 0.35)
        return norm(s, peak)

    out = {}
    n = int(0.16 * SR)
    out["step_soft"] = norm(mix((mul(lowpass(noise(n), 0.16), env(n, 30)), 1.0),
                                (mul(sweep(n, 85, 55, 40), env(n, 35)), 0.9)), 0.6)
    n = int(0.14 * SR)                                                     # Stein: hartes Klacken mit hellem "Tock"
    out["step_hard"] = norm(mix((mul(noise(n), env(n, 130)), 0.8),
                                (mul(sweep(n, 950, 480, 40), env(n, 48)), 0.8),
                                (mul(sweep(n, 170, 110, 50), env(n, 40)), 0.5)), 0.7)
    n = int(0.04 * SR)
    out["click"] = norm(mix((mul(sweep(n, 2600, 1600, 80), env(n, 110)), 1.0),
                            (mul(noise(n), env(n, 300)), 0.3)), 0.5)
    # Nachladen: Magazin raus (Klick + Schaben), Magazin rein (Schlag + Klick), Durchladen (Schaben + Klack)
    N = int(1.4 * SR)
    rl = [0.0] * N

    def ev(t0, part, g):
        o = int(t0 * SR)
        for i, v in enumerate(part):
            if o + i < N:
                rl[o + i] += v * g

    def click_part(f, dur=0.03, k=130):
        m = int(dur * SR)
        return mix((mul(sweep(m, f, f * 0.7, 60), env(m, k)), 1.0), (mul(noise(m), env(m, 250)), 0.4))

    def scrape(dur, a):
        m = int(dur * SR)
        return mul(lowpass(noise(m), a), [math.sin(math.pi * i / m) for i in range(m)])

    ev(0.10, click_part(1900), 0.9)
    ev(0.16, scrape(0.14, 0.30), 0.5)
    m = int(0.08 * SR)
    ev(0.62, mix((mul(sweep(m, 210, 90, 50), env(m, 38)), 1.0), (mul(noise(m), env(m, 160)), 0.5)), 1.0)
    ev(0.66, click_part(2300), 0.7)
    ev(0.95, scrape(0.16, 0.35), 0.6)
    ev(1.12, click_part(1400, 0.05, 90), 1.0)
    ev(1.16, mix((mul(sweep(m, 160, 80, 40), env(m, 40)), 1.0),), 0.6)
    out["reload"] = norm(rl, 0.8)
    out["pistol"] = gun(0.30, 70, 0.35, 18, 200, 80, 40)
    out["rifle"] = gun(0.35, 55, 0.25, 14, 140, 60, 30)
    out["shotgun"] = gun(0.70, 40, 0.15, 7, 90, 40, 12)
    out["heavy"] = gun(1.00, 45, 0.20, 5, 70, 35, 8, echo=0.18)
    n = int(0.8 * SR)
    out["railgun"] = norm(mix((mul(sweep(n, 2200, 180, 6), env(n, 6)), 1.0),
                              (mul(lowpass(noise(n), 0.3), env(n, 10)), 0.5),
                              (mul(sweep(n, 90, 40, 10), env(n, 7)), 0.9)), 0.9)
    n = int(1.0 * SR)
    sh = [math.sin(math.pi * i / n) ** 0.6 for i in range(n)]              # Abschuss: anschwellendes Zischen
    out["rocket"] = norm(mix((mul(lowpass(noise(n), 0.12), sh), 1.0),
                             (mul(sweep(n, 120, 70, 3), env(n, 3)), 0.8)), 0.9)
    n = int(2.4 * SR)
    ex, y, a = [], 0.0, 0.5
    for i in range(n):                                                      # Tiefpass, der sich zudreht
        t = i / SR
        y += max(0.03, a * math.exp(-t * 2.2)) * (rng.uniform(-1, 1) - y)
        ex.append(y)
    out["explosion"] = norm(delay(mix((mul(ex, env(n, 2.0)), 1.6),
                                      (mul(sweep(n, 70, 32, 3), env(n, 2.4)), 1.0),
                                      (mul(noise(n), env(n, 60)), 0.8)), 0.22, 0.3), 0.95)
    # Helikopter: Rotorschlag (12 Hz) auf Rauschen und tiefem Brummen, nahtlos wiederholbar
    N, F = SR, int(0.06 * SR)
    base = []
    nz = lowpass(noise(N + F), 0.22)
    for i in range(N + F):
        t = i / SR
        chop = 0.35 + 0.65 * max(0.0, math.sin(tp * 12 * t)) ** 2
        base.append(nz[i] * chop * 1.6 + math.sin(tp * 48 * t) * 0.35 + math.sin(tp * 96 * t) * 0.2 * chop)
    loop = base[:N]
    for i in range(F):                                                      # Naht überblenden
        k = i / F
        loop[i] = loop[i] * k + base[N + i] * (1 - k)
    out["heli"] = norm(loop, 0.8)
    # Tomahawk-Säule: Hydraulik (anschwellendes Brummen mit Schaben), am Ende ein dumpfer Einrast-Schlag
    n = int(2.6 * SR)
    hum = []
    for i in range(n):
        t = i / SR
        f = 55 + 70 * (t / 2.6)
        hum.append(math.sin(tp * f * t) * 0.7 + math.sin(tp * 2 * f * t) * 0.25)
    sh = [min(1.0, i / (0.25 * SR)) * min(1.0, (n - i) / (0.3 * SR)) for i in range(n)]
    sv = mix((mul(hum, sh), 0.8), (mul(lowpass(noise(n), 0.08), sh), 0.6))
    m = int(0.25 * SR)
    clunk = mix((mul(sweep(m, 140, 60, 30), env(m, 22)), 1.0), (mul(noise(m), env(m, 90)), 0.5))
    for i, v in enumerate(clunk):
        sv[n - m + i] += v
    out["servo"] = norm(sv, 0.8)
    # Tomahawk-Anflug: tiefes Triebwerksdröhnen (nahtlos wiederholbar) und Pfeifen kurz vor dem Einschlag
    N, F = SR, int(0.08 * SR)
    nz = lowpass(noise(N + F), 0.05)
    nz2 = lowpass(noise(N + F), 0.25)
    base = [nz[i] * 2.2 + nz2[i] * 0.35 + math.sin(tp * 38 * i / SR) * 0.25 for i in range(N + F)]
    loop = base[:N]
    for i in range(F):
        k = i / F
        loop[i] = loop[i] * k + base[N + i] * (1 - k)
    out["jet"] = norm(loop, 0.85)
    n = int(2.8 * SR)
    wh, ph = [], 0.0
    for i in range(n):
        t = i / SR
        ph += tp * (2400 - 1700 * (t / 2.8) ** 0.7) / SR
        a = min(1.0, t / 0.4) * (0.4 + 0.6 * t / 2.8)
        wh.append(math.sin(ph) * a)
    out["whistle"] = norm(mix((wh, 1.0), (mul(lowpass(noise(n), 0.4), [0.15 + 0.3 * i / n for i in range(n)]), 0.4)), 0.8)
    # Elektroschuss der Drohne: knisterndes Zischen mit hohem Summen
    n = int(0.45 * SR)
    crack = [(rng.uniform(-1, 1) if rng.random() < 0.35 else 0.0) for _ in range(n)]
    buzz = [math.sin(tp * 880 * i / SR) * (0.5 + 0.5 * math.sin(tp * 60 * i / SR)) for i in range(n)]
    out["zap"] = norm(mix((mul(crack, env(n, 7)), 1.0), (mul(buzz, env(n, 9)), 0.6)), 0.8)
    # Vorbeizischende Kugel: kurzes, scharfes Rauschen (hochpass) mit fallendem Pfeifton, an- und abschwellend
    n = int(0.26 * SR)
    hn = noise(n)
    lp = lowpass(hn, 0.25)
    hp = [a - b for a, b in zip(hn, lp)]
    bell = [math.sin(math.pi * min(1.0, i / n)) ** 1.5 * math.exp(-3.0 * i / n) for i in range(n)]
    out["whiz"] = norm(mix((mul(hp, bell), 1.0), (mul(sweep(n, 3400, 1500, 9), bell), 0.35)), 0.85)

    # ----- Monster (5d)
    def tone(n, f, phase_jit=0.0):
        return [math.sin(tp * f * i / SR + phase_jit) for i in range(n)]

    def growl(dur, f0, f1, rough, bright):
        """Knurren: rauer Grundton (Sägezahn-artig) mit unruhiger Amplitude, tiefpassgefiltert."""
        n = int(dur * SR)
        ph, w = 0.0, []
        for i in range(n):
            t = i / n
            f = f0 + (f1 - f0) * t + 6.0 * math.sin(tp * 7.0 * i / SR)
            ph += f / SR
            saw = 2.0 * (ph - math.floor(ph)) - 1.0
            am = 1.0 + rough * math.sin(tp * 23.0 * i / SR + 3.0 * math.sin(tp * 3.1 * i / SR))
            a = min(1.0, t / 0.15) * min(1.0, (1.0 - t) / 0.3)
            w.append(saw * am * a)
        w = lowpass(w, bright)
        breath = mul(lowpass(noise(n), 0.12), [min(1.0, i / (0.2 * n)) * min(1.0, (n - i) / (0.3 * n)) for i in range(n)])
        return norm(mix((w, 1.0), (breath, 0.35)), 0.85)
    out["growl"] = growl(0.75, 105, 80, 0.55, 0.22)                 # Grunt: kurzes Knurren/Grunzen
    out["growl_deep"] = growl(1.0, 62, 48, 0.7, 0.12)               # Brute: tiefer
    out["hiss"] = norm(mix((growl(0.6, 260, 200, 0.4, 0.35), 0.8),   # Jägerin: Fauchen in höherer Stimmlage
                           (mul([a - b for a, b in zip(noise(int(0.6 * SR)), lowpass(noise(int(0.6 * SR)), 0.3))],
                                [math.sin(math.pi * i / int(0.6 * SR)) for i in range(int(0.6 * SR))]), 0.6)), 0.8)
    n = int(0.22 * SR)                                              # Monsterschritt: dumpfer Tritt
    thud = norm(mix((mul(lowpass(noise(n), 0.08), env(n, 22)), 1.0), (mul(sweep(n, 70, 38, 18), env(n, 16)), 1.2)), 0.85)
    out["mstep"] = thud
    out["mstep_heavy"] = list(thud)
    n = int(0.6 * SR)                                               # Riese: Erdstoss mit Nachhall
    out["mstep_giant"] = norm(delay(mix((mul(lowpass(noise(n), 0.05), env(n, 9)), 1.0),
                                        (mul(sweep(n, 48, 26, 7), env(n, 6)), 1.4)), 0.09, 0.35), 0.9)
    n = int(0.06 * SR)                                              # Fluchttier: leises Tapsen
    out["tap"] = norm(mul(lowpass(noise(n), 0.3), env(n, 90)), 0.6)
    n = int(0.2 * SR)                                               # Schreckenslaut
    out["squeak"] = norm(mul(sweep(n, 3300, 1900, 14), [math.sin(math.pi * i / n) for i in range(n)]), 0.7)
    n = SR                                                          # Drohne: Surren (nahtlose 1-s-Schleife)
    out["hum"] = norm(mix((tone(n, 180), 0.6), (tone(n, 361), 0.35), (tone(n, 543), 0.12),
                          (mul(lowpass(noise(n), 0.5), [0.5 + 0.5 * math.sin(tp * 6 * i / SR) for i in range(n)]), 0.08)), 0.7)
    n = int(0.55 * SR)                                              # Drohne erkennt dich: zwei Pieptöne + Scan
    bp = [0.0] * n
    for k, (t0, f) in enumerate(((0.0, 1500), (0.12, 2000))):
        for i in range(int(t0 * SR), int((t0 + 0.08) * SR)):
            bp[i] += math.sin(tp * f * i / SR) * 0.8
    scan = mul(sweep(n, 900, 2600, 6), [(0.0 if i < 0.25 * SR else 0.35 * math.sin(tp * 30 * i / SR) ** 2) for i in range(n)])
    out["scan"] = norm(mix((bp, 1.0), (scan, 1.0)), 0.75)
    n = int(0.6 * SR)                                               # Drohne lädt auf: steigendes Sirren
    ph, ch = 0.0, []
    for i in range(n):
        t = i / n
        ph += (300 + 1500 * t * t) / SR
        ch.append(math.sin(tp * ph) * (0.3 + 0.7 * t) * (0.7 + 0.3 * math.sin(tp * 45 * i / SR)))
    out["charge"] = norm(ch, 0.75)
    n = int(1.3 * SR)                                               # Koloss holt aus: tiefes Brummen
    out["rumble"] = norm(mul(mix((tone(n, 55), 1.0), (tone(n, 82), 0.4), (lowpass(noise(n), 0.03), 0.6)),
                             [min(1.0, i / (0.3 * n)) * min(1.0, (n - i) / (0.15 * n)) for i in range(n)]), 0.85)
    n = int(2.5 * SR)                                               # Bodenschlag baut sich auf: anschwellend
    ph, bd = 0.0, []
    for i in range(n):
        t = i / n
        ph += (36 + 34 * t) / SR
        bd.append(math.sin(tp * ph) * t ** 1.5)
    out["buildup"] = norm(mix((bd, 1.0), (mul(lowpass(noise(n), 0.05), [(i / n) ** 2 for i in range(n)]), 0.7)), 0.9)
    n = int(0.9 * SR)                                               # Titan reisst den Brocken heraus
    crk = [(rng.uniform(-1, 1) if rng.random() < 0.25 else 0.0) for _ in range(n)]
    out["rip"] = norm(mix((mul(lowpass(crk, 0.4), env(n, 3)), 1.0), (mul(lowpass(noise(n), 0.06), env(n, 4)), 1.0),
                          (mul(sweep(n, 70, 30, 5), env(n, 5)), 1.2)), 0.9)
    n = int(0.28 * SR)                                              # Nahkampf: Luftzug beim Schlag
    sw_env = [math.sin(math.pi * i / n) ** 2 for i in range(n)]
    out["swoosh"] = norm(mul(lowpass([a - b for a, b in zip(noise(n), lowpass(noise(n), 0.08))], 0.45), sw_env), 0.6)
    n = int(0.25 * SR)                                              # Treffer: dumpfer, nasser Schlag
    out["slash"] = norm(mix((mul(lowpass(noise(n), 0.2), env(n, 28)), 1.0), (mul(sweep(n, 180, 70, 30), env(n, 20)), 0.8)), 0.8)
    n = int(1.4 * SR)                                               # Bratpfanne: BONG (metallisch, klingt nach)
    out["bong"] = norm(mix(*[(mul(tone(n, f), env(n, k)), a) for f, k, a in
                             ((410, 2.2, 1.0), (1037, 3.0, 0.6), (1712, 4.5, 0.35), (2650, 7.0, 0.2))],
                           (mul(noise(n), env(n, 60)), 0.3)), 0.9)
    n = SR                                                          # fliegender Brocken: Rauschen (Schleife)
    out["whoosh"] = norm(mul(lowpass(noise(n), 0.09), [0.6 + 0.4 * math.sin(tp * 3 * i / SR) for i in range(n)]), 0.7)
    return out


def surface_is_hard(world, x, y, z):
    """Steht man auf Stein (Gebäudeboden, Treppe, Mauerkrone, Deckungsblock, Tunnel) statt auf Erde?"""
    if z < -1.0 or z > world.height(x, y) + 0.12:
        return True
    return any(f[0] <= x <= f[2] and f[1] <= y <= f[3] for f in getattr(world, "floors", ()))


class Sfx:
    """Geräusche: Schüsse, Schritte, Explosionen, Helikopter. Positionsabhängig (Lautstärke und Richtung)
    über OpenAL; fehlt eine Audioausgabe, läuft das Spiel ohne Ton weiter."""

    POOL = {"step_soft": 5, "step_hard": 5, "pistol": 4, "rifle": 8, "shotgun": 3, "heavy": 3,
            "railgun": 3, "rocket": 3, "explosion": 6, "click": 3, "reload": 2, "servo": 2, "whistle": 1, "zap": 3, "whiz": 4,
            "growl": 3, "growl_deep": 2, "hiss": 2, "mstep": 4, "mstep_heavy": 3, "mstep_giant": 3, "tap": 3,
            "squeak": 2, "scan": 2, "charge": 2, "rumble": 2, "buildup": 2, "rip": 1,
            "swoosh": 3, "slash": 3, "bong": 2}
    RANGE = {"step_soft": 28.0, "step_hard": 32.0, "pistol": 160.0, "rifle": 190.0, "shotgun": 170.0,
             "heavy": 260.0, "railgun": 260.0, "rocket": 180.0, "explosion": 320.0, "heli": 260.0,
             "click": 50.0, "reload": 50.0, "servo": 90.0, "whistle": 700.0, "jet": 2500.0, "zap": 80.0, "whiz": 20.0,
             "growl": 34.0, "growl_deep": 45.0, "hiss": 30.0, "mstep": 26.0, "mstep_heavy": 55.0, "mstep_giant": 140.0,
             "tap": 14.0, "squeak": 30.0, "hum": 22.0, "scan": 45.0, "charge": 40.0, "rumble": 70.0, "buildup": 110.0,
             "rip": 150.0, "whoosh": 45.0, "swoosh": 18.0, "slash": 22.0, "bong": 45.0}
    MIN = {"step_soft": 3.0, "step_hard": 3.0, "pistol": 12.0, "rifle": 14.0, "shotgun": 14.0,
           "heavy": 20.0, "railgun": 20.0, "rocket": 14.0, "explosion": 30.0, "heli": 18.0,
           "click": 40.0, "reload": 40.0, "servo": 6.0, "whistle": 120.0, "jet": 150.0, "zap": 8.0, "whiz": 6.0,
           "growl": 4.0, "growl_deep": 6.0, "hiss": 3.0, "mstep": 3.0, "mstep_heavy": 8.0, "mstep_giant": 25.0,
           "tap": 2.0, "squeak": 4.0, "hum": 3.0, "scan": 6.0, "charge": 5.0, "rumble": 12.0, "buildup": 20.0,
           "rip": 30.0, "whoosh": 6.0, "swoosh": 3.0, "slash": 3.0, "bong": 6.0}

    def __init__(self, game):
        self.game = game
        self.ok = False
        self.muted = False
        self.a3d = None
        self.pool, self.rr, self.paths = {}, {}, {}
        self.walk = {}                 # Spieler-ID -> [x, y, zurückgelegte Strecke]
        self.heli_snd = {}             # Heli-ID -> (Sound, Knoten)
        self.heli_mg = {}              # Heli-ID -> (letzter MG-Vorrat, Sperrzeit)
        self.jet = None                # Tomahawk-Anflug: (Sound, Knoten), Dauerschleife
        self.mob_st = {}               # Monster-ID -> [x, y, Schrittstrecke, nächster Laut (s), Zustand, Art, ...]
        self.loops = {}                # Schlüssel -> (Sound, Knoten, Name): Drohnen-Surren, fliegende Brocken
        self.voice_t = []              # Zeitpunkte der letzten Monsterlaute (Begrenzung)
        if not REAL_PANDA:
            return
        try:
            import tempfile
            import wave
            from array import array
            from panda3d.core import Filename
            tmp = tempfile.mkdtemp(prefix="spiel_ton_")
            for name, data in synth_sounds().items():
                p = os.path.join(tmp, name + ".wav")
                with wave.open(p, "wb") as f:
                    f.setnchannels(1)
                    f.setsampwidth(2)
                    f.setframerate(SR)
                    f.writeframes(array("h", [int(max(-1.0, min(1.0, v)) * 32000) for v in data]).tobytes())
                self.paths[name] = Filename.fromOsSpecific(p).getFullpath()
            mgr = game.sfxManagerList[0]
            try:
                from direct.showbase.Audio3DManager import Audio3DManager
                self.a3d = Audio3DManager(mgr, game.camera)
                self.a3d.setDopplerFactor(0.0)
                self.a3d.setDropOffFactor(1.0)
            except Exception as e:
                print("3D-Ton nicht verfügbar:", e)
                self.a3d = None
            for name, n in self.POOL.items():
                self.pool[name] = [self.make(name) for _ in range(n)]
                self.rr[name] = 0
            self.ok = True
        except Exception as e:
            print("Ton nicht verfügbar:", e)
            self.ok = False

    def make(self, name):
        snd = self.a3d.loadSfx(self.paths[name]) if self.a3d else self.game.sfxManagerList[0].getSound(self.paths[name])
        node = self.game.render.attachNewNode("ton")
        if self.a3d:
            self.a3d.attachSoundToObject(snd, node)
            try:
                self.a3d.setSoundMinDistance(snd, self.MIN.get(name, 10.0))
                self.a3d.setSoundMaxDistance(snd, self.RANGE.get(name, 150.0))
            except Exception:
                pass
        return snd, node

    def cam(self):
        p = self.game.camera.getPos(self.game.render)
        return (p[0], p[1], p[2])

    def play(self, name, pos=None, vol=1.0, rate=1.0):
        if not self.ok or self.muted or name not in self.pool:
            return
        try:
            cam = self.cam()
            pos = pos or cam
            d = math.dist(pos, cam)
            if d > self.RANGE.get(name, 150.0):
                return
            snd, node = self.pool[name][self.rr[name]]
            self.rr[name] = (self.rr[name] + 1) % len(self.pool[name])
            if self.a3d is None:
                m = self.MIN.get(name, 10.0)
                vol *= 1.0 if d <= m else max(0.0, 1.0 - (d - m) / (self.RANGE.get(name, 150.0) - m)) ** 1.6
            node.setPos(*pos)
            snd.setVolume(max(0.0, min(1.0, vol)))
            snd.setPlayRate(rate)
            snd.play()
        except Exception:
            pass

    def toggle(self):
        self.muted = not self.muted
        if self.muted:
            self.silence()
        return self.muted

    def jet_sound(self, pos, left=99.0):
        """Dröhnen der anfliegenden Tomahawk-Rakete (pos = None: aus). Im Anflug nur leise im Hintergrund;
        erst in den letzten TOMA_LOUD_T Sekunden dreht es auf TOMA_JET_VOL auf ("gleich knallt's")."""
        if not self.ok:
            return
        try:
            if pos is None or self.muted:
                if self.jet is not None:
                    self.jet[0].stop()
                return
            if self.jet is None:
                self.jet = self.make("jet")
                self.jet[0].setLoop(True)
            snd, node = self.jet
            node.setPos(*pos)
            k = max(0.0, min(1.0, 1.0 - left / TOMA_LOUD_T))          # 0 bis zu den letzten Sekunden, dann bis 1
            vol = TOMA_JET_QUIET + (TOMA_JET_VOL - TOMA_JET_QUIET) * k * k
            snd.setVolume(max(0.0, min(1.0, vol)))
            snd.setPlayRate(0.8 + 0.35 * k)
            if snd.status() != 2:
                snd.play()
        except Exception:
            pass

    def silence(self):
        for snd, node, _n in self.loops.values():
            try:
                snd.stop()
                node.removeNode()
            except Exception:
                pass
        self.loops.clear()
        if self.jet is not None:
            try:
                self.jet[0].stop()
            except Exception:
                pass
        for snd, _node in self.heli_snd.values():
            try:
                snd.stop()
            except Exception:
                pass
        self.walk.clear()

    # ----- Ereignisse
    def shot(self, wi, pid):
        g = self.game
        pl = g.world.players.get(pid)
        own = pid == g.my_id
        if pl is None and not own:
            return
        pos = None if own else (pl.x, pl.y, pl.z + 1.4)
        name = WEAPONS[wi].name if 0 <= wi < len(WEAPONS) else ""
        kind, rate = {"Pistole": ("pistol", 1.0), "Revolver": ("pistol", 0.78), "Sturmgewehr": ("rifle", 1.0),
                      "Maschinenpistole": ("rifle", 1.3), "Minigun": ("rifle", 1.12),
                      "Schrotflinte": ("shotgun", 1.0), "Scharfschütze": ("heavy", 1.0),
                      "Railgun": ("railgun", 1.0), "Raketenwerfer": ("rocket", 1.0)}.get(name, ("rifle", 1.0))
        r = g.prng.uniform(0.96, 1.04)
        self.play(kind, pos, 0.85 if own else 1.0, rate * r)

    def reload(self, wi):
        w = WEAPONS[wi] if 0 <= wi < len(WEAPONS) else None
        rate = max(0.75, min(1.25, 1.3 / w.reload)) if w else 1.0
        self.play("reload", None, 0.7, rate)

    def ui_click(self):
        self.play("click", None, 0.45, self.game.prng.uniform(0.95, 1.08))

    def turret(self, tid):
        ts = self.game.world.turrets
        if not (0 <= tid < len(ts)):
            return
        t = ts[tid]
        pos = (t.x, t.y, t.z)
        if t.kind == "flak":
            self.play("heavy", pos, 1.0, 0.8)
        else:
            self.play("rifle", pos, 1.0, 0.8 * self.game.prng.uniform(0.96, 1.04))

    def explosion(self, pos, r):
        vol = max(0.6, min(1.0, 0.45 + r * 0.09))
        self.play("explosion", tuple(pos), vol, max(0.7, min(1.2, 1.3 - r * 0.05)))

    def heli_rocket(self, pid):
        for hc in self.game.world.helis:
            if hc.driver == pid:
                self.play("rocket", (hc.x, hc.y, hc.z), 1.0, 0.9)
                return

    # ----- pro Bild
    def update(self, dt):
        if not self.ok or self.muted:
            return
        try:
            self.steps(dt)
            self.helis(dt)
            self.monsters(dt)
        except Exception:
            pass

    def steps(self, dt):
        g, world = self.game, self.game.world
        cam = self.cam()
        seen = set()
        for pid, pl in world.players.items():
            seen.add(pid)
            st = self.walk.get(pid)
            if st is None or pl.hp <= 0:
                self.walk[pid] = [pl.x, pl.y, 0.0]
                continue
            d = math.hypot(pl.x - st[0], pl.y - st[1])
            st[0], st[1] = pl.x, pl.y
            if (d > 3.0 or not pl.moving or pl.vehicle >= 0 or pl.heli >= 0 or pl.mount >= 0
                    or not getattr(pl, "on_ground", True)):
                st[2] = 0.0 if d > 3.0 else st[2] * 0.0
                continue
            st[2] += d
            if st[2] >= 1.9:
                st[2] -= 1.9
                if math.hypot(pl.x - cam[0], pl.y - cam[1]) > 34.0:
                    continue
                hard = surface_is_hard(world, pl.x, pl.y, pl.z)
                vol = (0.55 if pid == g.my_id else 0.8) * (1.0 - 0.6 * getattr(pl, "crouch", 0.0))
                pos = None if pid == g.my_id else (pl.x, pl.y, pl.z + 0.1)
                self.play("step_hard" if hard else "step_soft", pos, vol, g.prng.uniform(0.9, 1.12))
        for pid in [p for p in self.walk if p not in seen]:
            del self.walk[pid]

    def voice(self, name, pos, vol, rate=1.0, force=False):
        """Monsterlaut mit Begrenzung: höchstens MOB_SND_MAX Laute je MOB_SND_WINDOW Sekunden (Schritte zählen
        nicht mit, die haben eigene Abstände)."""
        now = time.time()
        self.voice_t = [t for t in self.voice_t if now - t < MOB_SND_WINDOW]
        if not force and len(self.voice_t) >= MOB_SND_MAX:
            return
        self.voice_t.append(now)
        self.play(name, pos, vol, rate)

    def loop_at(self, key, name, pos, vol, rate=1.0):
        """Dauerton (Drohnen-Surren, Brocken im Flug) an pos halten; wird in monsters() aufgeräumt."""
        ent = self.loops.get(key)
        if ent is None:
            snd, node = self.make(name)
            snd.setLoop(True)
            ent = self.loops[key] = [snd, node, name]
        snd, node, _n = ent
        node.setPos(*pos)
        snd.setVolume(max(0.0, min(1.0, vol)))
        snd.setPlayRate(rate)
        if snd.status() != 2:
            snd.play()

    def monsters(self, dt):
        """Monster-Geräusche aus den Monster-Zuständen (Host wie Mitspieler): Schritte nach gelaufener Strecke,
        ab und zu Knurren (nie Dauerschleife), Drohnen-Surren/-Piepen/-Aufladen, Ausholen von Koloss und Titan,
        Brocken. Nur die MOB_SND_NEAREST nächsten Monster in Hörweite werden vertont."""
        g, world = self.game, self.game.world
        cam = self.cam()
        rng = g.prng
        mobs = [m for m in world.mobs if m.state != "dead"]
        mobs.sort(key=lambda m: (m.x - cam[0]) ** 2 + (m.y - cam[1]) ** 2)
        live, loops_on = set(), set()
        hums = 0
        for m in mobs[:MOB_SND_NEAREST]:
            cfg = MOB_SND.get(m.kind)
            if cfg is None:
                continue
            d = math.dist((m.x, m.y, m.z), cam)
            if d > cfg["range"]:
                continue
            live.add(m.id)
            pos = (m.x, m.y, m.z + 0.3)
            st = self.mob_st.get(m.id)
            if st is None:
                st = self.mob_st[m.id] = {"x": m.x, "y": m.y, "walk": 0.0, "voice": rng.uniform(*cfg.get("voice_gap", (5.0, 10.0))),
                                          "state": "idle" if m.kind == "drone" else m.state,   # Drohne, die schon
                                          "atk": False, "fast": False, "fear_t": 0.0}          # jagt: piept einmal
            moved = math.hypot(m.x - st["x"], m.y - st["y"])
            st["x"], st["y"] = m.x, m.y
            if cfg.get("step") and moved < 3.0 * max(1.0, m.scale) and getattr(m, "hover", 0) <= 0:
                st["walk"] += moved
                stride = cfg["stride"] * max(1.0, m.scale ** 0.8)
                if st["walk"] >= stride:
                    st["walk"] -= stride
                    self.play(cfg["step"], (m.x, m.y, m.z + 0.05), cfg["step_vol"], rng.uniform(*cfg["step_rate"]))
            # Laute ab und zu (nicht während eines Angriffs)
            st["voice"] -= dt
            if cfg.get("voice") and st["voice"] <= 0:
                st["voice"] = rng.uniform(*cfg["voice_gap"])
                if m.state != "attack":
                    self.voice(cfg["voice"], pos, cfg["voice_vol"], rng.uniform(*cfg["voice_rate"]))
            # Zustandswechsel
            if m.kind == "drone":
                if hums < MOB_SND_HUMS:                    # Surren der nächsten Drohnen
                    hums += 1
                    loops_on.add(("hum", m.id))
                    self.loop_at(("hum", m.id), "hum", pos, MOB_VOL["drone_hum"], 1.0 + 0.04 * (m.id % 5))
                if st["state"] == "idle" and m.state in ("chase", "attack"):
                    self.voice("scan", pos, MOB_VOL["drone_scan"], 1.0, force=True)
                if m.state == "attack" and not st["atk"]:
                    self.voice("charge", pos, MOB_VOL["drone_charge"], 1.0, force=True)
            elif m.kind in ("colossus", "titan"):
                if m.state == "attack" and not st["atk"]:
                    big = m.kind == "titan"
                    ak = getattr(m, "atk_kind", 0)
                    w = m.windup()
                    if ak == 1:                            # Bodenschlag: anschwellendes Aufbauen bis zum Einschlag
                        self.voice("buildup", pos, MOB_VOL["titan_build" if big else "colossus_build"],
                                   (2.5 / max(w, 0.5)) * (0.8 if big else 1.0), force=True)
                    elif ak == 0:                          # leichter Schlag: tiefes Brummen beim Ausholen
                        self.voice("rumble", pos, MOB_VOL["titan_rumble" if big else "colossus_rumble"],
                                   (1.3 / max(w, 0.4)) * (0.75 if big else 1.0), force=True)
                    else:                                  # Titan-Tritt: Ausholen wie leichter Schlag, tiefer
                        self.voice("rumble", pos, MOB_VOL["titan_rumble"], 0.6, force=True)
            elif m.kind == "critter":
                fast = getattr(m, "speed_now", 0.0) > MOB_KINDS["critter"]["wander"] * 2.5
                st["fear_t"] = max(0.0, st["fear_t"] - dt)
                if fast and not st["fast"] and st["fear_t"] <= 0:
                    self.voice("squeak", pos, MOB_VOL["critter_squeak"], rng.uniform(0.9, 1.15), force=True)
                    st["fear_t"] = 6.0
                st["fast"] = fast
            st["state"] = m.state
            st["atk"] = m.state == "attack"
        for r in world.rocks[:MOB_SND_ROCKS]:              # fliegende Brocken rauschen
            if math.dist((r.x, r.y, r.z), cam) < self.RANGE["whoosh"]:
                key = ("rock", r.rid)
                loops_on.add(key)
                self.loop_at(key, "whoosh", (r.x, r.y, r.z), MOB_VOL["rock_fly"], 1.0)
        for key in [k for k in self.loops if k not in loops_on]:
            snd, node, _n = self.loops.pop(key)
            try:
                snd.stop()
                node.removeNode()
            except Exception:
                pass
        for mid in [i for i in self.mob_st if i not in live]:
            del self.mob_st[mid]

    def helis(self, dt):
        g, world = self.game, self.game.world
        for hc in world.helis:
            on = hc.hp > 0 and hc.driver >= 0
            ent = self.heli_snd.get(hc.id)
            if ent is None and on:
                ent = self.heli_snd[hc.id] = self.make("heli")
                ent[0].setLoop(True)
            if ent is not None:
                snd, node = ent
                if on:
                    sp = min(1.0, hc.speed / HELI_VMAX)
                    own = hc.driver == g.my_id
                    node.setPos(*(self.cam() if own else (hc.x, hc.y, hc.z)))
                    vol = (0.45 if own else 0.9) * (0.65 + 0.35 * sp) * (0.8 if hc.ground else 1.0)
                    if self.a3d is None and not own:
                        d = math.dist((hc.x, hc.y, hc.z), self.cam())
                        vol *= max(0.0, 1.0 - d / self.RANGE["heli"]) ** 1.5
                    snd.setVolume(max(0.0, min(1.0, vol)))
                    snd.setPlayRate(0.85 + 0.3 * sp + (0.0 if hc.ground else 0.08))
                    if snd.status() != 2:                     # 2 = PLAYING
                        snd.play()
                else:
                    snd.stop()
            last, cd = self.heli_mg.get(hc.id, (hc.mg, 0.0))
            cd -= dt
            if hc.mg < last - 0.5 and cd <= 0 and hc.hp > 0:
                self.play("rifle", (hc.x, hc.y, hc.z), 0.9, 1.15)
                cd = 0.07
            self.heli_mg[hc.id] = (hc.mg, cd)


# --------------------------------------------------------------- Das Spiel
class Game(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.disableMouse()
        self.setBackgroundColor(*SKY)
        self.render.setAntialias(AntialiasAttrib.MAuto)      # MSAA (wenn die Grafikkarte es kann)
        st = load_settings()
        self.gfx = st.get("gfx") if st.get("gfx") in GFX_MODES else "standard"
        self.sens_mult = st.get("sens") if st.get("sens") in SENS_CHOICES else 1.0
        self.fps_limit = st.get("fps") if st.get("fps") in FPS_CHOICES else 144
        self.apply_fps()
        self.overlay_kind = self.overlay_yes = None
        self.amb_np = None
        self.sky_root = self.sky_clouds = self.sun_np = self.filters = None
        self.vignette = self.land_np = None
        self.water_nps = []
        self.shadows = {}
        self.camLens.setFov(FOV)
        self.camLens.setNearFar(0.1, 450)
        self.fov_cur = FOV
        self.prng = random.Random()

        # Spielzustand: erst das Startmenü, Welt und HUD entstehen in start_game()
        self.mode = "menu"          # menu | play
        self.net_mode = "single"    # single | host | client
        self.my_id = 0
        self.my_name = str(st.get("name") or (socket.gethostname() or "Spieler"))[:16]
        self.world = None
        self.player = None
        self.host = None            # HostSession (nur beim Host)
        self.client = None          # ClientSession (nur beim Mitspieler)
        self.listener = None        # Host-Suche im Menü
        self.attempt = None         # laufender Verbindungsversuch
        self.menu_items = []
        self.menu_lines = []                  # anklickbare Menüzeilen (Hot)
        self.menu_last = None
        self.menu_state = "name"
        self.menu_msg = ""
        self.ip_text = ""
        self.ip_edited = False
        self.lost_text = None
        self.cfg = dict(mode="koth", limit=10, mobs=True, cd=int(STRIKE_CD), regen=REGEN_RATE,
                        resp=RESPAWN_DEFAULT, map=None)   # Host-Einstellungen
        self.name_back = "main"               # wohin "Weiter" im Namensmenü führt
        self.map_list = []                    # gefundene Kartendateien (Name, Pfad)
        self.dead_since = None                # Zeitpunkt des eigenen Todes (Anzeige der Wartezeit)
        self.menu_cards = []                  # Kacheln hinter den Menüknöpfen (Hot, Knoten)
        self.setup_for = "single"
        self.feed = []                        # Kill-Anzeige: (Text, Zeit)
        self.pings = {}                       # Minimap: Spieler-ID -> (Zeit, x, y) des letzten Schusses
        self.crate_views = {}
        self._txt = {}
        self.quit_box = None                  # Sicherheitsabfrage beim Beenden (Text + Hintergrund)
        self.end = None                       # Endbildschirm nach Rundenende (5f)
        self.fx = []                          # Feuerball, Druckwelle, Rauch
        self.gren_views, self.drop_views, self.veh_views = {}, {}, {}
        self.tur_views = {}
        self.heli_views = {}
        self.heli_ads = True
        self.strike_fx = None                 # Tomahawk: Rakete im Anflug, Warnring
        self.trail_t = {}                     # Rakete -> Zeit bis zur nächsten Rauchwolke
        self.flames = {}                      # Rakete -> Flammen-Knoten
        self.throw_req = False

        self.setFrameRateMeter(False)         # Bildrate nur auf Wunsch (F3)
        self.build_assets()
        self.build_viewmodel()
        self.gun_dr.setActive(False)   # Waffe erst im Spiel zeigen

        # Federn für Rückstoss und Waffenschwingen
        self.sp_back = Spring(180, 14)    # Waffe nach hinten (m)
        self.sp_pitch = Spring(180, 14)   # Waffe nach oben kippen (Grad)
        self.sp_roll = Spring(180, 14)
        self.sp_cam = Spring(120, 12)     # Kamera-Ruck nach oben (Grad)
        self.sp_hurt = Spring(120, 10)    # Kamera-Wackeln bei Treffern (Grad Roll)
        self.sw_h = Spring(90, 12)        # Waffe hinkt der Mausdrehung hinterher
        self.sw_p = Spring(90, 12)
        self.ads_t = 0.0
        self.bob_amp = 0.0
        self.flash_t = 0.0
        self.hit_t = 0.0
        self.hurt_flash = 0.0
        self.death_t = 0.0
        self.parts = []
        self.bullet_nodes = {}
        self.mob_views = {}
        self.player_views = {}

        # Eingabe
        self.sel_req = None
        self.reload_req = False
        self.use_req = False
        self.alt_req = False
        self.prev_trig = False
        try:        # sonst heisst "R" bei gehaltener Shift-Taste "shift-r" und das Nachladen beim Rennen ginge nicht
            from panda3d.core import ModifierButtons
            self.buttonThrowers[0].node().setModifierButtons(ModifierButtons())
        except Exception:
            pass
        self.accept("mouse1", self.on_click)
        self.accept("escape", self.on_escape)
        self.accept("q", self.on_q)          # im Spiel lehnt Q (wird per Tastenabfrage gelesen)
        self.accept("f", self.on_use)
        self.accept("f3", self.toggle_fps)
        self.accept("c", self.toggle_duck)
        self.duck_lock = False
        self.accept("m", self.toggle_sound)
        self._hover_hit = None
        self.sfx = Sfx(self)
        self.accept("v", self.on_alt)
        self.accept("g", self.on_grenade)
        self.accept("j", self.on_confirm, [True])
        self.accept("y", self.on_confirm, [True])
        self.accept("n", self.on_confirm, [False])
        self.accept("arrow_left", self.end_key, [-1])
        self.accept("arrow_right", self.end_key, [1])
        self.accept("tab", self.tab_down)
        self.accept("tab-up", self.tab_up)
        self.accept("r", self.on_r)
        for i in range(10):          # Ziffern: Waffenwahl im Spiel, Auswahl/IP-Eingabe im Menü
            self.accept(str(i), self.on_digit, [i])
        bt = getattr(self, "buttonThrowers", None)
        if bt:                       # Texteingabe (Name, IP) über Tastenanschläge
            bt[0].node().setKeystrokeEvent("keystroke")
            self.accept("keystroke", self.on_keystroke)
        self.accept("backspace", self.menu_backspace)
        self.accept("backspace-repeat", self.menu_backspace)
        self.accept("enter", self.menu_enter)
        self.accept("wheel_up", self.cycle_weapon, [-1])
        self.accept("wheel_down", self.cycle_weapon, [1])

        self.captured = False
        self.mouse_prev = None
        self.warp_pending = False
        self.warp_frames = 0                  # so viele Frames wartet die Maussteuerung schon auf die Fenstermitte
        self.warp_ref = None                  # letzte (schon gezählte) Zeigerposition vor dem Zurücksetzen
        self.taskMgr.add(self.update_task, "update")
        self._keep = []                       # feste Knoten; alles andere gehört zu einem Spiel (leave_game)
        for name in ("render", "aspect2d", "render2d", "a2dTopCenter", "a2dTopLeft", "a2dTopRight",
                     "a2dBottomCenter", "a2dBottomLeft", "a2dBottomRight", "a2dLeftCenter", "a2dRightCenter"):
            node = getattr(self, name, None)
            if node is not None:
                self._keep.append((node, set(node.getChildren())))
        self.show_menu("main" if str(st.get("name") or "").strip() else "name")

    # ------------------------------------------------------------ Start-Menü
    def userExit(self):
        self.shutdown_net()
        ShowBase.userExit(self)

    def shutdown_net(self):
        for obj in (self.host, self.client, self.listener, self.attempt):
            if obj is not None:
                try:
                    obj.close()
                except Exception:      # beim Beenden egal
                    pass

    def clear_menu(self):
        for t in self.menu_items:
            t.destroy()
        self.menu_items = []
        for h in self.menu_lines:
            h.destroy()
        self.menu_lines = []
        for _h, nd in self.menu_cards:
            nd.removeNode()
        self.menu_cards = []
        self.menu_last = None

    def menu_background(self):
        """Verlauf, ein paar Low-Poly-Rauten und der Titel."""
        def card(x0, x1, z0, z1, col, alpha=1.0, rot=0.0):
            cm = CardMaker("bg")
            cm.setFrame(x0, x1, z0, z1)
            nd = self.aspect2d.attachNewNode(cm.generate())
            nd.setColor(col[0], col[1], col[2], alpha)
            if alpha < 1.0:
                nd.setTransparency(TransparencyAttrib.MAlpha)
            if rot:
                nd.setR(rot)
            self.menu_items.append(Deco(nd))
            return nd
        n = 24
        for i in range(n):                                     # senkrechter Farbverlauf
            k = i / (n - 1)
            col = (0.04 + 0.05 * k, 0.07 + 0.17 * k, 0.15 + 0.17 * k)
            card(-4, 4, 1.1 - 2.2 * (i + 1) / n - 0.002, 1.1 - 2.2 * i / n, col)
        for x, z, r, col, a_ in ((-1.15, 0.55, 0.30, (1.0, 0.55, 0.15), 0.10), (1.25, 0.25, 0.42, (0.2, 0.8, 0.9), 0.08),
                                 (-1.0, -0.55, 0.40, (0.2, 0.8, 0.9), 0.07), (1.05, -0.62, 0.26, (1.0, 0.55, 0.15), 0.09),
                                 (0.0, 0.95, 0.22, (1.0, 0.8, 0.3), 0.06)):
            nd = card(-r, r, -r, r, col, a_, 45.0)
            nd.setPos(x, 0, z)
        ti = OnscreenText(text="POLYBASH", pos=(0.012, 0.628), scale=0.2, fg=(0, 0, 0, 0.55), mayChange=False)
        self.menu_items.append(ti)
        self.menu_items.append(OnscreenText(text="POLYBASH", pos=(0, 0.64), scale=0.2, fg=(1.0, 0.62, 0.14, 1),
                                            shadow=(0.35, 0.12, 0.0, 0.9), mayChange=False))
        card(-0.62, 0.62, 0.575, 0.585, (1.0, 0.62, 0.14), 0.9)
        self.menu_items.append(OnscreenText(text="Low-Poly-Shooter für WLAN-Mehrspieler", pos=(0, 0.52),
                                            scale=0.045, fg=(0.75, 0.85, 0.95, 1), mayChange=False))

    def show_menu(self, state="name", msg=""):
        self.clear_menu()
        self.mode, self.menu_state, self.menu_msg = "menu", state, msg
        self.attempt = None
        if state == "join":
            if self.listener is None:
                self.listener = Listener()
        elif self.listener is not None:
            self.listener.close()
            self.listener = None
        self.set_capture(False)
        if getattr(self, "vignette", None) is not None:
            self.vignette.hide()
        self.menu_background()
        self.menu_items.append(OnscreenText(text=f"Spieler: {self.my_name}", pos=(-1.2, -0.94), scale=0.045,
                                            fg=(0.7, 0.8, 0.9, 1), align=TextNode.ALeft, mayChange=False))
        self.menu_items.append(OnscreenText(text="Polybash", pos=(1.2, -0.94), scale=0.045,
                                            fg=(0.7, 0.8, 0.9, 1), align=TextNode.ARight, mayChange=False))
        self.menu_refresh()

    def menu_spec(self):
        """Zeilen des aktuellen Menüs: (Text, Aktion beim Klick oder None). Die erste Zeile ohne Aktion
        ist die Überschrift."""
        st = self.menu_state
        dig = lambda d: (lambda: self.on_digit(d))          # noqa: E731
        back = lambda: self.on_escape()                     # noqa: E731
        if st == "name":
            spec = [("Dein Name", None), (f"{self.my_name}_", None), ("(Namen tippen)", None),
                    ("Weiter   (Enter)", self.menu_enter)]
            if self.name_back == "main":
                spec.append(("Beenden   (Esc)", self.open_quit_box))
        elif st == "main":
            spec = [("1   Spielen", dig(1)), ("2   Einstellungen", dig(2)),
                    ("Beenden   (Esc)", self.open_quit_box)]
        elif st == "multi":
            spec = [("Spielen", None), ("1   Spiel hosten  (auch allein zum Testen)", dig(1)),
                    ("2   Spiel beitreten", dig(2)), ("Zurück   (Esc)", back)]
        elif st == "settings":
            spec = [("Einstellungen", None), (f"1   Name:  {self.my_name}", dig(1)),
                    (f"2   Grafik:  {GFX_NAMES[self.gfx]}", dig(2)),
                    (f"3   Bildrate:  {fps_label(self.fps_limit)}", dig(3)),
                    (f"4   Mausempfindlichkeit:  {int(round(self.sens_mult * 100))} %", dig(4)),
                    ("Zurück   (Esc)", back)]
        elif st == "setup":
            c = self.cfg
            title = "Einzelspieler" if self.setup_for == "single" else "Spiel hosten"
            spec = [(title, None), (f"1   Modus:  {MODE_NAMES[c['mode']]}", dig(1)),
                    (f"2   Zeitlimit:  {c['limit']} Minuten", dig(2)),
                    (f"3   Monster:  {'an' if c['mobs'] else 'aus'}", dig(3)),
                    (f"4   Tomahawk-Abklingzeit:  {strike_cd_label(c['cd'])}", dig(4)),
                    (f"5   Gesundheit regeneriert:  {regen_label(c['regen'])}", dig(5)),
                    (f"6   Respawn-Zeit:  {respawn_label(c['resp'])}", dig(6)),
                    (f"7   Karte:  {self.map_label()}", dig(7)),
                    ("Start   (Enter)", lambda: self.start_game(self.setup_for)),
                    ("Zurück   (Esc)", back)]
        elif st == "join":
            hosts = self.listener.hosts if self.listener is not None else {}
            spec = [("Spiel beitreten", None)]
            if hosts:
                spec.append(("Gefundene Spiele im WLAN (anklicken):", None))
                for ip, h in hosts.items():
                    spec.append((f"{ip}   {h['name']} ({h['n']} Spieler, {MODE_NAMES.get(h['mode'], '?')})",
                                 (lambda ip=ip: self.connect_to(ip))))
            elif self.listener is None:
                spec.append(("(Automatische Suche nicht möglich)", None))
            else:
                spec.append(("Suche Spiele im WLAN" + "." * (int(time.time() * 2) % 4), None))
            spec += [(f"IP-Adresse:  {self.current_ip()}_", None), ("(Zahlen und Punkt tippen)", None),
                     ("Verbinden   (Enter)", self.menu_enter), ("Zurück   (Esc)", self.on_escape)]
        else:                                          # connecting
            host = self.attempt.host if self.attempt is not None else ""
            spec = [(f"Verbinde mit {host} ...", None), ("Abbrechen   (Esc)", self.on_escape)]
        if self.menu_msg:
            spec.append((self.menu_msg, None))
        return spec

    def menu_refresh(self):
        spec = self.menu_spec()
        text = "\n".join(it[0] for it in spec)
        if text != self.menu_last:
            self.menu_last = text
            for h in self.menu_lines:
                h.destroy()
            self.menu_lines = []
            for _h, nd in self.menu_cards:
                nd.removeNode()
            self.menu_cards = []
            big = self.menu_state in ("main", "multi")
            step, scale = (0.16, 0.078) if big else (0.105, 0.06)
            z = 0.36
            for i, it in enumerate(spec):
                label, action = it[0], it[1]
                head = i == 0 and action is None and self.menu_state != "main"
                zz = z
                z -= step * (1.25 if head else 1.0)
                sc = 0.085 if head else scale
                if not label:
                    continue
                card = None
                if action is not None:
                    cm = CardMaker("btn")
                    cm.setFrame(-0.78, 0.78, zz - 0.3 * sc - 0.012, zz + 0.95 * sc + 0.012)
                    card = self.aspect2d.attachNewNode(cm.generate())
                    card.setColor(0.10, 0.17, 0.26, 0.85)
                    card.setTransparency(TransparencyAttrib.MAlpha)
                t = OnscreenText(text=label, pos=(0, zz), scale=sc,
                                 fg=Hot.BASE if action else ((1.0, 0.78, 0.3, 1) if head else (0.82, 0.88, 0.95, 1)),
                                 shadow=(0, 0, 0, 0.8), mayChange=True)
                hot = Hot(t, 0.0, zz, sc, action, label)
                self.menu_lines.append(hot)
                if card is not None:
                    hot.x0, hot.x1 = -0.78, 0.78
                    self.menu_cards.append((hot, card))

    # ------------------------------------------------------------ Maus im Menü
    def mouse_2d(self):
        """Mauszeiger in aspect2d-Koordinaten oder None."""
        try:
            mw = self.mouseWatcherNode
            if mw is None or not mw.hasMouse():
                return None
            return float(mw.getMouseX()) * float(self.getAspectRatio()), float(mw.getMouseY())
        except Exception:
            return None

    def update_hover(self):
        """Hebt die Zeile bzw. Waffenkarte unter der Maus farbig hervor. -> (Zeile, Karte)"""
        m = self.mouse_2d()
        active = self.quit_box[2] if self.quit_box is not None else (
            self.menu_lines if self.mode == "menu" else [])
        hit = None
        if m is not None:
            hit = next((h for h in active if h.hit(m[0], m[1])), None)
        if hit is not self._hover_hit:
            self._hover_hit = hit
            if hit is not None:
                self.sfx.ui_click()
        for h in self.menu_lines:
            h.set(h is hit)
        for h, nd in self.menu_cards:
            nd.setColor(*((0.22, 0.30, 0.42, 0.95) if h is hit else (0.10, 0.17, 0.26, 0.85)))
        if self.quit_box is not None:
            for h in self.quit_box[2]:
                h.set(h is hit)
        return hit, None

    def on_click(self):
        """Linke Maustaste: Menüpunkt, Waffenkarte oder Schaltfläche der Beenden-Abfrage."""
        if getattr(self, "end", None) is not None and self.quit_box is None:
            self.end_click()
            return
        if self.mode != "menu" and self.quit_box is None:
            return
        hit, _card = self.update_hover()
        if hit is None and self.quit_box is not None and self.overlay_kind == "strike":
            self.strike_pick(self.mouse_2d())
        elif hit is not None:
            hit.action()

    def connect_to(self, ip):
        self.ip_text, self.ip_edited = ip, True
        self.menu_enter()

    def current_ip(self):
        """Eingetippte IP, sonst die des ersten gefundenen Hosts."""
        if self.ip_edited:
            return self.ip_text
        hosts = self.listener.hosts if self.listener is not None else {}
        return next(iter(hosts), "")

    def map_label(self):
        p = self.cfg.get("map")
        if not p:
            return "Standard" + ("" if self.map_list else "  (Ordner 'maps' leer)")
        n = next((n for n, q in self.map_list if q == p), os.path.basename(p))
        return n + "  (Minecraft 1:1, Deathmatch)" if p.lower().endswith(".mcmap") else n

    def open_setup(self, for_mode):
        self.map_list = list_maps()
        if self.cfg.get("map") not in [p for _n, p in self.map_list]:
            self.cfg["map"] = None
        self.setup_for = for_mode
        self.show_menu("setup")

    def on_digit(self, d):
        if self.quit_box is not None:
            return
        if getattr(self, "end", None) is not None:      # Endbildschirm: Ziffern wählen den Reiter
            self.show_end_tab(d - 1)
            return
        if self.mode == "menu":
            st = self.menu_state
            if st == "main":
                if d == 1:
                    self.show_menu("multi")
                elif d == 2:
                    self.show_menu("settings")
            elif st == "multi":
                if d == 1:
                    self.open_setup("host")
                elif d == 2:
                    self.ip_text, self.ip_edited = "", False
                    self.show_menu("join")
            elif st == "settings":
                if d == 1:
                    self.name_back = "settings"
                    self.show_menu("name")
                elif d == 2:
                    self.gfx = GFX_MODES[(GFX_MODES.index(self.gfx) + 1) % len(GFX_MODES)]
                    self.save_prefs()
                    self.menu_refresh()
                elif d == 3:
                    self.fps_limit = FPS_CHOICES[(FPS_CHOICES.index(self.fps_limit) + 1) % len(FPS_CHOICES)]
                    self.apply_fps()
                    self.save_prefs()
                    self.menu_refresh()
                elif d == 4:
                    i = SENS_CHOICES.index(self.sens_mult) if self.sens_mult in SENS_CHOICES else 0
                    self.sens_mult = SENS_CHOICES[(i + 1) % len(SENS_CHOICES)]
                    self.save_prefs()
                    self.menu_refresh()
            elif st == "setup":
                c = self.cfg
                if d == 1:
                    c["mode"] = MODES[(MODES.index(c["mode"]) + 1) % len(MODES)]
                elif d == 2:
                    c["limit"] = TIME_CHOICES[(TIME_CHOICES.index(c["limit"]) + 1) % len(TIME_CHOICES)]
                elif d == 3:
                    c["mobs"] = not c["mobs"]
                elif d == 4:
                    i = STRIKE_CD_CHOICES.index(c["cd"]) if c["cd"] in STRIKE_CD_CHOICES else 0
                    c["cd"] = STRIKE_CD_CHOICES[(i + 1) % len(STRIKE_CD_CHOICES)]
                elif d == 5:
                    i = REGEN_CHOICES.index(c["regen"]) if c["regen"] in REGEN_CHOICES else 0
                    c["regen"] = REGEN_CHOICES[(i + 1) % len(REGEN_CHOICES)]
                elif d == 6:
                    i = RESPAWN_CHOICES.index(c["resp"]) if c["resp"] in RESPAWN_CHOICES else 0
                    c["resp"] = RESPAWN_CHOICES[(i + 1) % len(RESPAWN_CHOICES)]
                elif d == 7:
                    paths = [None] + [p for _n, p in self.map_list]
                    i = paths.index(c.get("map")) if c.get("map") in paths else 0
                    c["map"] = paths[(i + 1) % len(paths)]
        elif self.mode == "play":
            if self.player.hp > 0 and 1 <= d <= N_SLOTS:
                self.request_weapon(d - 1)
            elif self.player.hp > 0 and d == N_SLOTS + 1:      # 4 = Nahkampfwaffe
                self.sel_req = MELEE_SEL

    def on_keystroke(self, ch):
        """Texteingabe im Menü (Name, IP-Adresse)."""
        if self.mode != "menu" or not ch or not ch.isprintable() or self.quit_box is not None:
            return
        if self.menu_state == "name" and len(self.my_name) < 16:
            self.my_name += ch
        elif self.menu_state == "join" and (ch.isdigit() or ch == "."):
            if not self.ip_edited:
                self.ip_text, self.ip_edited = "", True
            if len(self.ip_text) < 15:
                self.ip_text += ch
            self.menu_msg = ""

    def menu_backspace(self):
        if self.mode != "menu" or self.quit_box is not None:
            return
        if self.menu_state == "name":
            self.my_name = self.my_name[:-1]
        elif self.menu_state == "join":
            if not self.ip_edited:
                self.ip_text, self.ip_edited = self.current_ip(), True
            self.ip_text = self.ip_text[:-1]
            self.menu_msg = ""

    def menu_enter(self):
        if self.quit_box is not None:
            self.on_confirm(True)
            return
        if self.mode != "menu":
            return
        st = self.menu_state
        if st == "name":
            self.my_name = self.my_name.strip()
            if self.my_name:
                back, self.name_back = self.name_back, "main"
                self.save_prefs()
                self.show_menu(back)
            else:
                self.menu_msg = "Bitte einen Namen eingeben."
        elif st == "setup":
            self.start_game(self.setup_for)
        elif st == "join":
            ip = self.current_ip().strip()
            if not ip:
                self.menu_msg = "Bitte IP-Adresse eingeben."
                return
            found = self.listener.hosts.get(ip) if self.listener is not None else None
            port = found["port"] if found else NET_PORT
            self.show_menu("connecting")
            self.attempt = JoinAttempt(ip, port, self.my_name)

    def on_escape(self):
        if self.quit_box is not None:
            if self.mode == "play" and self.overlay_kind in ("settings", "leave"):
                self.show_pause("main")            # Esc geht eine Ebene zurück
            else:
                self.close_quit_box()              # Pause-Menü bzw. Abfrage schliessen = weiterspielen
        elif self.mode == "menu" and self.menu_state == "setup":
            self.show_menu("main" if self.setup_for == "single" else "multi")
        elif self.mode == "menu" and self.menu_state in ("multi", "settings"):
            self.show_menu("main")
        elif self.mode == "menu" and self.menu_state == "name" and self.name_back != "main":
            self.name_back = "main"
            self.show_menu("settings")
        elif self.mode == "menu" and self.menu_state in ("join", "connecting"):
            if self.attempt is not None:
                self.attempt.close()
            self.show_menu("multi")
        elif self.mode == "play":
            self.show_pause("main")
        else:
            self.open_quit_box()

    def on_q(self):
        """Im Menü fragt Q (wie Esc) nach dem Beenden; im Spiel ist Q das Lehnen nach links."""
        if self.mode == "menu" and self.menu_state not in ("name", "join") and self.quit_box is None:
            self.open_quit_box()

    def open_quit_box(self):
        """Sicherheitsabfrage statt sofort zu beenden. Das Spiel läuft (online) weiter, die
        Eingaben ruhen, die Maus ist frei."""
        if self.quit_box is not None:
            return
        cm = CardMaker("quitbg")
        cm.setFrame(-1.05, 1.05, -0.3, 0.3)
        bg = self.aspect2d.attachNewNode(cm.generate())
        bg.setColor(0, 0, 0, 0.82)
        bg.setTransparency(TransparencyAttrib.MAlpha)
        bg.setBin("fixed", 90)
        bg.setDepthTest(False)
        bg.setDepthWrite(False)
        txt = OnscreenText(text="Spiel wirklich beenden?", pos=(0, 0.13), scale=0.08, fg=(1, 1, 1, 1),
                           shadow=(0, 0, 0, 0.9), mayChange=False)
        txt.setBin("fixed", 95)
        hots = []
        for label, x, yes in (("[ Ja, beenden ]", -0.5, True), ("[ Nein, weiterspielen ]", 0.45, False)):
            t = OnscreenText(text=label, pos=(x, -0.06), scale=0.07, fg=Hot.BASE,
                             shadow=(0, 0, 0, 0.9), mayChange=True)
            t.setBin("fixed", 95)
            hots.append(Hot(t, x, -0.06, 0.07, (lambda y=yes: self.on_confirm(y)), label))
        hint = OnscreenText(text="J / Enter   Ja        N / Esc   Nein", pos=(0, -0.2), scale=0.045,
                            fg=(0.8, 0.8, 0.8, 1), shadow=(0, 0, 0, 0.9), mayChange=False)
        hint.setBin("fixed", 95)
        hots.append(Hot(hint, 0.0, -0.2, 0.045, None, "J / Enter   Ja        N / Esc   Nein"))
        self.quit_box = (bg, txt, hots)
        self.overlay_kind = "quit"
        if self.mode == "play":
            self.set_capture(False)

    def close_quit_box(self, recapture=True):
        if self.quit_box is None:
            return
        bg, txt, hots = self.quit_box
        self.quit_box = None
        self.overlay_kind = self.overlay_yes = None
        bg.removeNode()
        txt.destroy()
        for h in hots:
            h.destroy()
        if recapture and self.mode == "play" and self.player is not None:
            self.set_capture(True)

    def on_confirm(self, yes):
        """J/Y/Enter bzw. N in einer Abfrage (Beenden, Zum Hauptmenü). Im Pause-Menü ohne Wirkung."""
        if self.quit_box is None or self.overlay_kind in ("pause", "settings", "strike"):
            return
        if self.overlay_kind == "leave":
            if yes:
                self.leave_game()
            else:
                self.show_pause("main")
            return
        if yes:
            self.userExit()
        else:
            self.close_quit_box()

    def open_overlay(self, kind, title, items, hint="", width=1.1):
        """Senkrechte Liste (Pause-Menü, Einstellungen, Abfragen) über dem laufenden Spiel.
        items: (Text, Aktion oder None). Das Spiel läuft weiter, die Eingaben ruhen, die Maus ist frei."""
        self.close_quit_box(recapture=False)
        n = len(items)
        z_title = 0.1 + 0.055 * n
        last = z_title - 0.17 - 0.11 * (n - 1)
        bottom = last - (0.2 if hint else 0.12)
        cm = CardMaker("overlaybg")
        cm.setFrame(-width, width, bottom, z_title + 0.14)
        bg = self.aspect2d.attachNewNode(cm.generate())
        bg.setColor(0, 0, 0, 0.82)
        bg.setTransparency(TransparencyAttrib.MAlpha)
        bg.setBin("fixed", 90)
        bg.setDepthTest(False)
        bg.setDepthWrite(False)
        txt = OnscreenText(text=title, pos=(0, z_title), scale=0.075, fg=(1, 1, 1, 1),
                           shadow=(0, 0, 0, 0.9), mayChange=False)
        txt.setBin("fixed", 95)
        hots = []
        for i, (label, action) in enumerate(items):
            z = z_title - 0.17 - 0.11 * i
            t = OnscreenText(text=label, pos=(0, z), scale=0.062, fg=Hot.BASE if action else Hot.PLAIN,
                             shadow=(0, 0, 0, 0.9), mayChange=True)
            t.setBin("fixed", 95)
            hots.append(Hot(t, 0.0, z, 0.062, action, label))
        if hint:
            h = OnscreenText(text=hint, pos=(0, bottom + 0.06), scale=0.042, fg=(0.8, 0.8, 0.8, 1),
                             shadow=(0, 0, 0, 0.9), mayChange=False)
            h.setBin("fixed", 95)
            hots.append(Hot(h, 0.0, bottom + 0.06, 0.042, None, hint))
        self.quit_box = (bg, txt, hots)
        self.overlay_kind = kind
        if self.mode == "play":
            self.set_capture(False)

    STRIKE_MAP_HALF = 0.62          # halbe Kantenlänge der Zielkarte (Bildschirmeinheiten)
    STRIKE_MAP_Z = 0.12             # Höhe der Kartenmitte

    def open_strike_map(self):
        """Tomahawk-Kommandoraum: grosse Karte, auf der man den Einschlagpunkt anklickt. Das Spiel läuft weiter."""
        self.close_quit_box(recapture=False)
        H, cz = self.STRIKE_MAP_HALF, self.STRIKE_MAP_Z
        root = self.aspect2d.attachNewNode("strikemap")
        root.setBin("fixed", 90)
        dim = CardMaker("dim")
        dim.setFrame(-3, 3, -1.2, 1.2)
        d = root.attachNewNode(dim.generate())
        d.setColor(0, 0, 0, 0.85)
        d.setTransparency(TransparencyAttrib.MAlpha)
        d.setBin("fixed", 90)
        d.setDepthTest(False)
        d.setDepthWrite(False)
        mm = CardMaker("map")
        mm.setFrame(-H, H, cz - H, cz + H)
        try:
            M, T = self.MAP_MARGIN, WORLD + 2 * self.MAP_MARGIN
            from panda3d.core import LPoint2f
            mm.setUvRange(LPoint2f(M / T, M / T), LPoint2f((M + WORLD) / T, (M + WORLD) / T))
        except Exception:
            pass
        mp = root.attachNewNode(mm.generate())
        mp.setLightOff()
        if self.map_tex is not None:
            mp.setTexture(self.map_tex)
        else:
            mp.setColor(0.2, 0.34, 0.17, 1)
        mp.setBin("fixed", 91)
        mp.setDepthTest(False)
        mp.setDepthWrite(False)
        # Spieler (grüner Pfeil) und Ziel (rotes Fadenkreuz)
        pl = self.player
        sc = 2 * H / WORLD
        am = Mesh(lit=False)
        for s_, c_ in ((0.034, (0, 0, 0)), (0.025, (1, 1, 1))):
            am.tri((0, 0, s_), (-0.62 * s_, 0, -0.72 * s_), (0, 0, -0.30 * s_), c_)
            am.tri((0, 0, s_), (0, 0, -0.30 * s_), (0.62 * s_, 0, -0.72 * s_), c_)
        me = root.attachNewNode(am.node("me"))
        me.setTwoSided(True)
        me.setColorScale(0.3, 1.0, 0.3, 1)
        me.setPos(-H + pl.x * sc, 0, cz - H + pl.y * sc)
        me.setR(-pl.heading)
        me.setBin("fixed", 92)
        me.setDepthTest(False)
        tgt = root.attachNewNode("target")
        for fr in ((-0.05, -0.012, -0.0025, 0.0025), (0.012, 0.05, -0.0025, 0.0025),
                   (-0.0025, 0.0025, 0.012, 0.05), (-0.0025, 0.0025, -0.05, -0.012)):
            cm = CardMaker("t")
            cm.setFrame(*fr)
            tgt.attachNewNode(cm.generate()).setColor(1, 0.2, 0.15, 1)
        if True:                                           # Wirkungsradius um das Ziel (nur für den Schützen sichtbar)
            ring = Mesh(lit=False)
            rr = H * 2 * STRIKE_R / WORLD
            for i in range(32):
                a0, a1 = 2 * math.pi * i / 32, 2 * math.pi * (i + 1) / 32
                pp = lambda r, a: (math.cos(a) * r, 0.0, math.sin(a) * r)        # noqa: E731
                ring.tri(pp(rr - 0.003, a0), pp(rr + 0.003, a0), pp(rr + 0.003, a1), (1, 0.2, 0.15), ref=(0, 5, 0))
                ring.tri(pp(rr - 0.003, a0), pp(rr + 0.003, a1), pp(rr - 0.003, a1), (1, 0.2, 0.15), ref=(0, 5, 0))
            tgt.attachNewNode(ring.node("radius")).setTwoSided(True)
        tgt.setBin("fixed", 93)
        tgt.setDepthTest(False)
        tgt.setDepthWrite(False)
        tgt.hide()
        self.strike_sel = None
        self.strike_ui = (mp, tgt)
        self.strike_root, self.strike_dots = root, {}
        if self.net_mode != "single" and TOMA_SHOW_PLAYERS:
            cap = OnscreenText(text="Rote Punkte: Gegner (live)", pos=(H + 0.05, cz + H - 0.06), scale=0.04,
                               fg=(1.0, 0.4, 0.35, 1), shadow=(0, 0, 0, 0.9), align=TextNode.ALeft, mayChange=False)
            cap.reparentTo(root)
        # Countdown-Länge (früher die Schalttafel neben dem Knopf): rechts neben der Karte wählbar
        if self.world.strike_dur not in STRIKE_OPTIONS:
            self.world.strike_dur = float(STRIKE_T)
        self.strike_dur_sel = int(self.world.strike_dur)
        ct = OnscreenText(text="Countdown:", pos=(H + 0.2, cz + 0.22), scale=0.05, fg=(1, 0.85, 0.3, 1),
                          shadow=(0, 0, 0, 0.9), mayChange=False)
        ct.reparentTo(root)
        ct.setBin("fixed", 95)
        self.strike_dur_txt = {}
        dur_hots = []
        for k, sec in enumerate(STRIKE_OPTIONS):
            zz = cz + 0.1 - k * 0.1
            t = OnscreenText(text="", pos=(H + 0.2, zz), scale=0.055, fg=Hot.BASE, shadow=(0, 0, 0, 0.9),
                             mayChange=True)
            t.setBin("fixed", 95)
            self.strike_dur_txt[sec] = t
            dur_hots.append(Hot(t, H + 0.2, zz, 0.055, (lambda v=sec: self.strike_pick_dur(v)), f"[ {sec} s ]"))
        self.strike_pick_dur(self.strike_dur_sel, quiet=True)
        title = OnscreenText(text="TOMAHAWK - Einschlagpunkt wählen", pos=(0, 0.88), scale=0.07, fg=(1, 0.85, 0.3, 1),
                             shadow=(0, 0, 0, 0.9), mayChange=False)
        title.setBin("fixed", 95)
        hint = OnscreenText(text="Klick auf die Karte setzt das Ziel. Der Ort wird niemandem verraten.",
                            pos=(0, cz - H - 0.08), scale=0.042, fg=(0.85, 0.85, 0.85, 1),
                            shadow=(0, 0, 0, 0.9), mayChange=True)
        hint.setBin("fixed", 95)
        fire_t = OnscreenText(text="[ Abfeuern ]", pos=(-0.45, cz - H - 0.2), scale=0.065, fg=Hot.BASE,
                              shadow=(0, 0, 0, 0.9), mayChange=True)
        fire_t.setBin("fixed", 95)
        canc_t = OnscreenText(text="[ Abbrechen ]", pos=(0.45, cz - H - 0.2), scale=0.065, fg=Hot.BASE,
                              shadow=(0, 0, 0, 0.9), mayChange=True)
        canc_t.setBin("fixed", 95)
        self.strike_hint = hint
        hots = [Hot(fire_t, -0.45, cz - H - 0.2, 0.065, self.strike_fire, "[ Abfeuern ]"),
                Hot(canc_t, 0.45, cz - H - 0.2, 0.065, self.close_quit_box, "[ Abbrechen ]"),
                Hot(hint, 0.0, cz - H - 0.08, 0.042, None, "")] + dur_hots
        self.quit_box = (root, title, hots)
        self.overlay_kind = "strike"
        if self.mode == "play":
            self.set_capture(False)

    def strike_pick_dur(self, sec, quiet=False):
        """Countdown-Länge auf der Zielkarte wählen (die gewählte steht in Klammern)."""
        if sec not in STRIKE_OPTIONS:
            return
        self.strike_dur_sel = sec
        for v, t in getattr(self, "strike_dur_txt", {}).items():
            t.setText(f"[ {v} s ]" if v == sec else f"  {v} s  ")
        if not quiet:
            self.sfx.ui_click()

    def update_strike_map(self):
        """Zielkarte (nur Mehrspieler, nur mit TOMA_SHOW_PLAYERS): aktuelle Positionen der anderen Spieler."""
        if (self.net_mode == "single" or not TOMA_SHOW_PLAYERS or self.quit_box is None
                or self.overlay_kind != "strike"):
            return
        root, dots = self.strike_root, self.strike_dots
        H, cz = self.STRIKE_MAP_HALF, self.STRIKE_MAP_Z
        me = self.player
        for pid, p in self.world.players.items():
            if p is me or getattr(p, "pid", pid) == me.pid:
                continue
            n = dots.get(pid)
            if n is None:
                cm = CardMaker("enemy")
                cm.setFrame(-0.011, 0.011, -0.011, 0.011)
                n = dots[pid] = root.attachNewNode(cm.generate())
                n.setColor(1.0, 0.15, 0.1, 1)
                n.setBin("fixed", 94)
                n.setDepthTest(False)
                n.setDepthWrite(False)
            if p.hp > 0:
                n.setPos(-H + p.x / WORLD * 2 * H, 0, cz - H + p.y / WORLD * 2 * H)
                n.show()
            else:
                n.hide()

    def strike_pick(self, m):
        """Klick auf die Zielkarte -> Weltkoordinate (oder nichts, wenn daneben)."""
        if m is None or self.quit_box is None or self.overlay_kind != "strike":
            return
        H, cz = self.STRIKE_MAP_HALF, self.STRIKE_MAP_Z
        if abs(m[0]) > H or abs(m[1] - cz) > H:
            return
        x, y = (m[0] + H) / (2 * H) * WORLD, (m[1] - cz + H) / (2 * H) * WORLD
        self.strike_sel = (x, y)
        mp, tgt = self.strike_ui
        tgt.setPos(m[0], 0, m[1])
        tgt.show()
        self.strike_hint.setText("Ziel gesetzt - klicke erneut zum Ändern, dann [ Abfeuern ]")
        self.sfx.ui_click()

    def strike_fire(self):
        if self.strike_sel is None:
            self.strike_hint.setText("Bitte zuerst ein Ziel auf der Karte wählen!")
            return
        x, y = self.strike_sel
        dur = getattr(self, "strike_dur_sel", int(STRIKE_T))
        self.close_quit_box()
        if self.net_mode == "client":
            if self.client is not None and not self.client.lost:
                self.client.send_strike(x, y, dur)
        else:
            self.world.press_button(self.player, x, y, dur)

    def show_pause(self, kind="main"):
        """Pause-Menü (Esc im Spiel): weiterspielen, Einstellungen, zum Hauptmenü, beenden."""
        net = self.net_mode
        if kind == "main":
            leave = {"client": "Verbindung trennen, zum Hauptmenü", "host": "Spiel beenden, zum Hauptmenü"}.get(
                net, "Zum Hauptmenü")
            self.open_overlay("pause", "Pause", [
                ("Weiterspielen   (Esc)", self.close_quit_box),
                ("Einstellungen", lambda: self.show_pause("settings")),
                (leave, lambda: self.show_pause("leave")),
                ("Spiel beenden", self.pause_quit)],
                "Das Spiel läuft im Hintergrund weiter" if net != "single" else "")
        elif kind == "leave":
            msg = {"client": "Die Verbindung zum Host wird getrennt.",
                   "host": "Das Spiel endet für alle Mitspieler."}.get(net, "Der Fortschritt dieser Runde geht verloren.")
            self.open_overlay("leave", "Zum Hauptmenü zurückkehren?", [
                (msg, None),
                ("[ Ja, zum Hauptmenü ]", self.leave_game),
                ("[ Nein, zurück ]", lambda: self.show_pause("main"))],
                "J / Enter   Ja        N / Esc   Nein")
        else:
            w = self.world
            host_side = net != "client" and w is not None

            def cyc(seq, cur):
                return seq[(seq.index(cur) + 1) % len(seq)] if cur in seq else seq[0]

            def do(fn):
                def act():
                    fn()
                    self.show_pause("settings")
                return act

            def set_gfx():
                self.set_gfx(cyc(GFX_MODES, self.gfx))

            def set_sens():
                self.sens_mult = cyc(SENS_CHOICES, self.sens_mult)
                self.save_prefs()

            def set_fps():
                self.fps_limit = cyc(FPS_CHOICES, self.fps_limit)
                self.apply_fps()
                self.save_prefs()

            items = [(f"Grafik:  {GFX_NAMES[self.gfx]}", do(set_gfx)),
                     (f"Bildrate:  {fps_label(self.fps_limit)}", do(set_fps)),
                     (f"Mausempfindlichkeit:  {int(round(self.sens_mult * 100))} %", do(set_sens))]
            if host_side:
                def set_cd():
                    cd = cyc(STRIKE_CD_CHOICES, int(w.strike_cd))
                    w.strike_cd = float(cd)
                    if cd > 0:
                        w.strike_wait = min(w.strike_wait, float(cd))
                    self.cfg["cd"] = cd

                def set_regen():
                    w.regen_rate = float(cyc(REGEN_CHOICES, w.regen_rate))
                    self.cfg["regen"] = w.regen_rate

                def set_mobs():
                    w.mobs_on = not w.mobs_on
                    if w.mobs_on:
                        w.populate_mobs()
                    else:
                        w.mobs.clear()
                    self.cfg["mobs"] = w.mobs_on

                def set_resp():
                    w.respawn_delay = float(cyc(RESPAWN_CHOICES, int(w.respawn_delay)))
                    self.cfg["resp"] = int(w.respawn_delay)

                items += [(f"Respawn-Zeit:  {respawn_label(w.respawn_delay)}", do(set_resp)),
                          (f"Monster:  {'an' if w.mobs_on else 'aus'}", do(set_mobs)),
                          (f"Tomahawk-Abklingzeit:  {strike_cd_label(int(w.strike_cd))}", do(set_cd)),
                          (f"Gesundheit regeneriert:  {regen_label(w.regen_rate)}", do(set_regen))]
            else:
                items.append(("Monster, Tomahawk und Regeneration bestimmt der Host", None))
            items.append(("Zurück   (Esc)", lambda: self.show_pause("main")))
            self.open_overlay("settings", "Einstellungen", items, "Modus und Zeitlimit gelten für die ganze Runde",
                              width=1.45)

    def pause_quit(self):
        self.close_quit_box(recapture=False)
        self.open_quit_box()

    def save_prefs(self):
        save_settings({"gfx": self.gfx, "sens": self.sens_mult, "fps": self.fps_limit, "name": self.my_name})

    def apply_fps(self):
        """Bildraten-Grenze setzen (ohne V-Sync; 0 = unbegrenzt)."""
        try:
            from panda3d.core import ClockObject
            clock = ClockObject.getGlobalClock()
            if self.fps_limit > 0:
                clock.setMode(ClockObject.MLimited)
                clock.setFrameRate(float(self.fps_limit))
            else:
                clock.setMode(ClockObject.MNormal)
        except Exception as e:
            print("FPS-Grenze nicht setzbar:", e)

    def teardown_hq(self):
        """Echtzeit-Schatten und Bloom wieder abschalten."""
        if self.filters is not None:
            try:
                self.filters.cleanup()
            except Exception:
                pass
            self.filters = None
        if self.sun_np is not None:
            try:
                if self.land_np is not None:
                    self.land_np.clearLight()
                    self.land_np.clearShader()
                self.sun_np.removeNode()
                if self.amb_np is not None:
                    self.amb_np.removeNode()
            except Exception:
                pass
        self.sun_np = self.amb_np = None

    def set_gfx(self, mode):
        """Grafikstufe mitten im Spiel wechseln."""
        self.gfx = mode
        self.save_prefs()
        self.teardown_hq()
        if self.land_np is not None:
            self.apply_gfx()

    def cleanup_scene(self):
        """Alles entfernen, was zu einem laufenden Spiel gehört (Szene, HUD, Effekte)."""
        self.sfx.silence()
        self.teardown_hq()
        keepers = [n for n in (self.sky_root, self.vignette) if n is not None]
        for parent, keep in self._keep:
            for ch in list(parent.getChildren()):
                if ch not in keep and ch not in keepers:
                    ch.removeNode()
        try:
            self.render.clearFog()
        except Exception:
            pass
        for v in (self.fx, self.parts):
            v.clear()
        self.bullet_nodes, self.mob_views, self.player_views = {}, {}, {}
        self.close_end_screen()
        self.gren_views, self.drop_views, self.veh_views = {}, {}, {}
        self.tur_views, self.heli_views, self.crate_views = {}, {}, {}
        self.whiz_prev, self.whizzed = {}, set()
        for nd in (getattr(self, "rock_views", None) or {}).values():
            nd.removeNode()
        self.rock_views = None
        self.trail_t, self.flames, self.shadows, self._txt = {}, {}, {}, {}
        self.strike_fx = None
        self.water_nps = []
        self.land_np = None
        self.lost_text = None
        self.feed, self.pings = [], {}
        for sp in (self.sp_back, self.sp_pitch, self.sp_roll, self.sp_cam, self.sp_hurt, self.sw_h, self.sw_p):
            sp.x = sp.v = 0.0
        self.ads_t = self.bob_amp = self.flash_t = self.hit_t = self.hurt_flash = self.death_t = 0.0
        self.fov_cur = FOV
        self.camLens.setFov(FOV)
        self.heli_ads = True
        if self.sky_root is not None:
            self.sky_root.hide()
        if self.vignette is not None:
            self.vignette.hide()
        self.gun_dr.setActive(False)

    def leave_game(self):
        """Verbindung trennen bzw. Host-Spiel beenden und zurück ins Hauptmenü."""
        self.close_quit_box(recapture=False)
        self.shutdown_net()
        self.host = self.client = self.listener = self.attempt = None
        self.cleanup_scene()
        self.mode, self.net_mode = "menu", "single"
        self.world = self.player = None
        self.show_menu("main")

    def menu_task(self, dt):
        self.update_hover()
        st = self.menu_state
        if st == "join":
            if self.listener is not None:
                self.listener.poll()
            self.menu_refresh()
        elif st == "connecting" and self.attempt is not None:
            res = self.attempt.poll()
            if res == "ready":
                self.start_game("client", self.attempt)
            elif res == "failed":
                self.show_menu("join", self.attempt.msg)
            else:
                self.menu_refresh()
        else:
            self.menu_refresh()

    # ------------------------------------------------------------ Spielstart
    def spawn_player(self):
        x, y = self.world.first_spawn(self.my_id)
        pl = Player(x, y, self.world, self.my_id, self.my_name)
        pl.respawn(self.world, x, y)
        self.world.players[self.my_id] = pl
        return pl

    def apply_respawn(self, x, y):
        """Eigene Figur neu aufstellen (Befehl vom Host bzw. der eigenen Welt)."""
        self.player.respawn(self.world, x, y)
        self.death_t = 0.0
        self.hurt_flash = 0.0
        self.fov_cur = FOV

    def start_game(self, mode, attempt=None):
        """mode: 'single' (allein), 'host' (Spiel eröffnen) oder 'client' (beitreten)."""
        self.duck_lock = False
        raw = mapdata = None
        if mode == "client":
            try:
                if attempt.map_raw is not None and attempt.map_raw.get("format") == MC_FORMAT:
                    path = mc_find(attempt.map_raw.get("id"))
                    if path is None:
                        raise ValueError(f"Karte '{attempt.map_raw.get('name')}' fehlt - die Datei (.mcmap) muss im Ordner 'maps' liegen")
                    mapdata, raw = mc_mapdata(path)
                elif attempt.map_raw is not None:
                    raw, mapdata = attempt.map_raw, sanitize_map(attempt.map_raw)
            except (ValueError, OSError, zlib.error, struct.error) as e:
                attempt.close()
                self.show_menu("join", f"Karte des Hosts unlesbar: {e}")
                return
            world = World(attempt.seed, spawn_mobs=False, mode=attempt.mode, limit=attempt.limit, mapdata=mapdata)
            if attempt.props != world.prop_count():
                attempt.close()
                self.show_menu("join", "Die Welt passt nicht zum Host (andere Spielversion?)")
                return
        else:
            path = self.cfg.get("map")
            if path:
                try:
                    if path.lower().endswith(".mcmap"):
                        mapdata, raw = mc_mapdata(path)
                    else:
                        with open(path, encoding="utf-8") as f:
                            raw = json.load(f)
                        mapdata = sanitize_map(raw)
                except (OSError, ValueError, zlib.error, struct.error) as e:
                    self.cfg["map"] = None
                    self.show_menu("setup", f"Karte nicht ladbar: {e}")
                    return
            world = World(SEED, spawn_mobs=self.cfg["mobs"], mode=self.cfg["mode"],
                          limit=self.cfg["limit"] * 60.0, strike_cd=self.cfg["cd"], regen=self.cfg["regen"],
                          respawn=self.cfg["resp"], mapdata=mapdata)
        world.map_raw = raw
        host = None
        if mode == "host":
            try:
                host = HostSession(world, self.my_name)
            except OSError as e:
                self.show_menu("main", f"Hosten nicht möglich: {e}")
                return
        self.clear_menu()
        if self.listener is not None:
            self.listener.close()
            self.listener = None
        self.mode, self.net_mode = "play", mode
        self.world, self.host = world, host
        self.my_id = attempt.my_id if mode == "client" else 0
        self.player = self.spawn_player()
        self.feed, self.pings = [], {}
        if mode == "client":
            self.client = ClientSession(attempt.conn, world, self.my_id, attempt.extra)
            world.shot_sink = self.client.send_shot
            world.gren_sink = self.client.send_grenade
            world.melee_sink = self.client.send_melee
            self.attempt = None

        land, water, zone, extra = build_mc_scene(world) if world.mc else build_scene(world)
        self.land_np = self.render.attachNewNode(land)
        if world.mc:
            self.land_np.setLightOff()                        # die Beleuchtung steckt in den Vertexfarben (wie in Minecraft)
        lamps, grass, decals, water2 = extra
        self.render.attachNewNode(lamps).setTwoSided(True)
        gr = self.render.attachNewNode("grass")
        for gn in grass:
            gr.attachNewNode(gn)
        gr.setTwoSided(True)
        dn = self.render.attachNewNode(decals)                # weiche Schatten am Boden
        dn.setTransparency(TransparencyAttrib.MAlpha)
        dn.setDepthWrite(False)
        dn.setLightOff()
        dn.setBin("transparent", 1)
        self.water_nps = []
        for k, node in enumerate((water, water2)):            # zwei gegenläufige Wellenschichten
            wn = self.render.attachNewNode(node)
            wn.setTransparency(TransparencyAttrib.MAlpha)
            wn.setDepthWrite(False)
            wn.setLightOff()
            wn.setBin("transparent", 10 + k)
            if k:
                wn.setTexScale(TextureStage.getDefault(), 1.7, 1.7)
            self.water_nps.append(wn)
        if self.sky_root is None:
            self.build_sky_nodes()
        self.sky_root.show()
        for zn in zone:
            zp = self.render.attachNewNode(zn)
            zp.setTransparency(TransparencyAttrib.MAlpha)
            zp.setBin("transparent", 5)
            zp.setDepthOffset(2)
            zp.setFogOff()
        fog = Fog("nebel")
        fog.setColor(*SKY)
        fog.setExpDensity(0.004 if world.mc else 0.012)          # Minecraft-Karte: weite Sicht über das Meer
        self.render.setFog(fog)
        self.build_vignette()
        self.apply_gfx()

        self.build_crates()
        self.build_toma()
        self.build_hud()
        if host is not None:
            self.host_ip = host.ip                 # steht in der Tab-Übersicht; zu Beginn kurz als Hinweis
            self.toast_later = (f"Freunde wählen 'Spiel beitreten'  (IP {host.ip})", (0.6, 1, 0.6), 6.0)
        self.lost_text = OnscreenText(text="", pos=(0, 0.35), scale=0.08, fg=(1, 0.3, 0.2, 1),
                                      shadow=(0, 0, 0, 0.9), mayChange=True)
        self.lost_text.hide()
        self.gun_dr.setActive(True)
        self.set_capture(True)

    def tick_client(self, dt):
        """Mitspieler: Snapshots des Hosts einarbeiten, eigenen Zustand melden."""
        cs = self.client
        cs.poll(dt)
        if cs.lost:
            self.lost_text.setText(f"Verbindung zum Host verloren ({cs.lost})\nEsc öffnet das Menü")
            self.lost_text.show()
            return
        pl = self.player
        if cs.hp is not None:
            pl.hp = cs.hp                      # Lebenspunkte entscheidet der Host
        cs.advance(dt)
        cs.send_state(dt, pl)
        self.world.push_player(pl)
        self.world.events.extend(cs.events)
        cs.events.clear()

    # ------------------------------------------------------------ Aufbau
    def build_assets(self):
        """Gemeinsame Geometrie für Tracer, Partikel und Mündungsfeuer (Instanzen)."""
        m = Mesh(lit=False)
        box(m, 0, 0, 0, 0.05, 1.1, 0.05, (1.0, 0.85, 0.35))
        self.tracer_np = NodePath(m.node("tracer"))
        self.rocket_np, self.flame_np = build_rocket()
        m = Mesh()
        box(m, 0, 0, 0, 1, 1, 1, (1, 1, 1))
        self.cube_np = NodePath(m.node("cube"))
        # Effekte: Kugel (Feuerball, Rauch) und flacher Ring (Druckwelle), weiss und ungeleuchtet;
        # Farbe und Deckkraft kommen pro Instanz über setColorScale
        m = Mesh(lit=False)
        m.mat = "fire"                                  # wolkige Struktur für Feuerball und Rauch
        blob(m, 0, 0, 0, 1, 1, 1, (1, 1, 1), random.Random(3), jitter=0.14, subdiv=2)
        self.sphere_np = NodePath(m.node("sphere"))
        self.scorch_np = self.flat_card("brandfleck", "blob")
        m = Mesh(lit=False)
        for i in range(28):
            a0, a1 = 2 * math.pi * i / 28, 2 * math.pi * (i + 1) / 28
            p = [(math.cos(a0) * 0.7, math.sin(a0) * 0.7, 0), (math.cos(a0), math.sin(a0), 0),
                 (math.cos(a1), math.sin(a1), 0), (math.cos(a1) * 0.7, math.sin(a1) * 0.7, 0)]
            m.tri(p[0], p[1], p[2], (1, 1, 1))
            m.tri(p[0], p[2], p[3], (1, 1, 1))
        self.disc_np = NodePath(m.node("ring"))
        self.disc_np.setTwoSided(True)
        m = Mesh()                            # Handgranate
        blob(m, 0, 0, 0, 0.11, 0.11, 0.13, (0.22, 0.30, 0.16), random.Random(4), jitter=0.05)
        box(m, 0, 0, 0.14, 0.05, 0.05, 0.06, (0.7, 0.7, 0.7))
        self.gren_np = NodePath(m.node("grenade"))
        # Waffenbilder (Seitenansicht) für Waffenleiste und Auswahl
        self.weapon_icons = [weapon_icon(i) for i in range(len(WEAPONS))]
        # Waffenmodelle am Boden (fallengelassene Waffen)
        self.drop_models = []
        rng = random.Random(9)
        for w in WEAPONS:
            gm = Mesh()
            for cx, cy, cz, sx, sy, sz, col in GUN_PARTS[w.name][0]:
                box(gm, cx, cy - 0.2, cz, sx, sy, sz, col, rng)
            self.drop_models.append(NodePath(gm.node("drop_" + w.name)))
        self.gear_models = [NodePath(gear_model(gi).node("gear")) for gi in range(len(GEAR))]
        self.melee_drop_models = []
        for mi in range(len(MELEE)):
            nd = NodePath("melee_drop")
            mm = nd.attachNewNode(melee_model(mi, 1.6).node("m"))
            mm.setPos(0, -0.4, 0)
            nd.setR(90)
            self.melee_drop_models.append(nd)
        m = Mesh(lit=False)                   # Granaten-Symbol im HUD
        for i in range(14):
            a0, a1 = 2 * math.pi * i / 14, 2 * math.pi * (i + 1) / 14
            m.tri((0, 0, 0), (math.cos(a0) * 0.05, 0, math.sin(a0) * 0.05),
                  (math.cos(a1) * 0.05, 0, math.sin(a1) * 0.05), (0.45, 0.62, 0.30))
        box(m, 0, 0, 0.055, 0.025, 0.02, 0.03, (0.8, 0.8, 0.8))
        self.gren_icon = NodePath(m.node("gren_icon"))
        self.gren_icon.setTwoSided(True)
        m = Mesh(lit=False)                   # Mündungsfeuer: Stern in der x-z-Ebene
        pts = []
        for i in range(8):
            a = 2 * math.pi * i / 8
            rr = 0.11 if i % 2 == 0 else 0.045
            pts.append((math.cos(a) * rr, 0.0, math.sin(a) * rr))
        for i in range(8):
            m.tri((0, 0, 0), pts[i], pts[(i + 1) % 8], (1.0, 0.85, 0.4))
        self.flash_np = NodePath(m.node("flash"))

    def build_viewmodel(self):
        """Waffe in eigenem Display-Region mit eigener Kamera: wird nie von
        Bäumen oder Felsen verdeckt."""
        self.gun_root = NodePath("gun_root")
        self.gun_lens = PerspectiveLens()
        self.gun_lens.setFov(62)
        self.gun_lens.setNearFar(0.02, 20)
        cam = Camera("gun_cam")
        cam.setLens(self.gun_lens)
        self.gun_cam = self.gun_root.attachNewNode(cam)
        cam.setScene(self.gun_root)
        dr = self.win.makeDisplayRegion()
        dr.setSort(5)
        dr.setClearDepthActive(True)
        dr.setCamera(self.gun_cam)
        self.gun_dr = dr
        self.gun_pivot = self.gun_root.attachNewNode("pivot")
        self.gun_models, self.gun_flash = [], []
        self.vm_mags = []
        rng = random.Random(7)
        for w in WEAPONS:
            parts, muzzle = GUN_PARTS[w.name]
            gm = Mesh()
            magp = MAG_PARTS.get(w.name)
            for part in parts:
                if magp is not None and tuple(part) == tuple(magp):
                    continue                                # wird als bewegliches Magazin gebaut
                cx, cy, cz, sx, sy, sz, col = part
                box(gm, cx, cy, cz, sx, sy, sz, col, rng)
            model = self.gun_pivot.attachNewNode(w.name)
            model.attachNewNode(gm.node("g"))
            mag = ej = None
            if magp is not None:
                for k in range(2):                          # k=0: Magazin an der Waffe, k=1: ausgeworfenes
                    mm_ = Mesh()
                    box(mm_, 0, 0, 0, magp[3], magp[4], magp[5], magp[6], rng)
                    nd = (model if k == 0 else self.gun_pivot).attachNewNode(mm_.node("mag"))
                    nd.setPos(magp[0], magp[1], magp[2])
                    if k == 1:
                        nd.hide()
                        ej = nd
                    else:
                        mag = nd
            self.vm_mags.append((mag, ej, magp))
            fl = model.attachNewNode("flash")
            fl.setPos(*muzzle)
            self.flash_np.instanceTo(fl)
            fl.setTwoSided(True)
            fl.hide()
            self.gun_models.append(model)
            self.gun_flash.append(fl)
        # Nahkampfwaffen in der Hand (Ego-Ansicht), Klinge schräg nach vorn oben
        self.melee_models = []
        for mi in range(len(MELEE)):
            nd = self.gun_pivot.attachNewNode("melee_" + MELEE[mi].name)
            nd.attachNewNode(melee_model(mi, 0.85).node("m"))
            nd.setPos(0.06, 0.08, -0.02)
            nd.setHpr(-20, 30, -25)
            nd.hide()
            self.melee_models.append(nd)
        # linke Hand (Haut + Ärmel) für das Nachladen
        hm = Mesh()
        box(hm, 0, 0, 0, 0.085, 0.11, 0.075, (0.86, 0.66, 0.52), rng)
        box(hm, -0.01, -0.34, -0.10, 0.075, 0.55, 0.07, (0.22, 0.28, 0.20), rng)
        self.vm_hand = self.gun_pivot.attachNewNode(hm.node("hand"))
        self.vm_hand.hide()
        self.vm_hand.setP(18)
        self.spr_t, self.trig_now, self.sprinting, self.hand_pos = 0.0, False, False, None
        # Die Rakete steckt vorn im Rohr des Raketenwerfers (wird beim Nachladen hineingeschoben)
        self.vm_rocket = self.gun_models[ROCKET_WI].attachNewNode("vm_rocket")
        build_rocket(lit=True)[0].copyTo(self.vm_rocket)
        self.vm_rocket.setPos(0, 0.5, 0.02)
        self.vm_rocket.setScale(0.9)

    def build_hud(self):
        self.cross = Crosshair(self.aspect2d)
        self.run_now, self.key_turn = False, 0
        self.hitmark = HitMark(self.aspect2d)
        self.hitmark.hide()
        self.pop_text = OnscreenText(text="", pos=(0, 0), scale=0.055, fg=(1, 1, 1, 1),
                                     shadow=(0, 0, 0, 0.8), align=TextNode.ALeft, mayChange=True)
        self.pop_text.hide()
        self.pop_pct, self.pop_age, self.pop_col = 0, 99.0, (1, 1, 1, 1)

        # Rotes Aufblitzen bei Schaden
        cm = CardMaker("hurt")
        cm.setFrame(-3, 3, -1, 1)
        self.hurt_card = self.aspect2d.attachNewNode(cm.generate())
        self.hurt_card.setTransparency(TransparencyAttrib.MAlpha)
        self.hurt_card.setColor(0.8, 0, 0, 0)

        # Healthbar
        def card(parent, x, z, sx, sz, col):
            c = CardMaker("c")
            c.setFrame(0, 1, 0, 1)
            n = parent.attachNewNode(c.generate())
            n.setPos(x, 0, z)
            n.setScale(sx, 1, sz)
            n.setColor(*col)
            n.setTransparency(TransparencyAttrib.MAlpha)
            return n

        card(self.a2dBottomLeft, 0.07, 0.065, 0.57, 0.052, (0, 0, 0, 0.55))
        self.hp_fg = card(self.a2dBottomLeft, 0.08, 0.075, 0.55, 0.032, (0.2, 0.8, 0.2, 1))
        self.hp_text = OnscreenText(text="100", parent=self.a2dBottomLeft, pos=(0.08, 0.13),
                                    scale=0.07, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.8),
                                    align=TextNode.ALeft, mayChange=True)
        # Schild (Ausrüstung): blauer Balken direkt unter den Lebenspunkten
        self.shield_bg = card(self.a2dBottomLeft, 0.07, 0.035, 0.57, 0.026, (0, 0, 0, 0.55))
        self.shield_fg = card(self.a2dBottomLeft, 0.08, 0.04, 0.55, 0.016, (0.35, 0.75, 1.0, 1))
        self.shield_bg.hide()
        self.shield_fg.hide()
        # Ausrüstung: drei Plaketten (Kopf, Torso, Füsse) rechts neben den Lebenspunkten
        # Ausrüstung: drei Kacheln senkrecht am rechten Rand (oben Kopf, Mitte Torso, unten Füsse). Im
        # Hintergrund ein dezenter Umriss des Slots; darüber das getragene Teil. Jede Kachel hat einen eigenen
        # Knoten "item" - später kann dort statt des Texts ein Symbol pro Teil hängen (GEAR_HUD_*).
        self.gear_tiles = {}
        for i, sl in enumerate(GEAR_SLOTS):
            tile = self.a2dRightCenter.attachNewNode("gear_" + sl)
            tile.setPos(-GEAR_HUD_W / 2 - 0.03, 0, GEAR_HUD_Y0 - i * (GEAR_HUD_H + 0.02))
            cm = CardMaker("bg")
            cm.setFrame(-GEAR_HUD_W / 2, GEAR_HUD_W / 2, -GEAR_HUD_H / 2, GEAR_HUD_H / 2)
            bg = tile.attachNewNode(cm.generate())
            bg.setColor(0.04, 0.05, 0.08, 0.7)
            bg.setTransparency(TransparencyAttrib.MAlpha)
            sym = tile.attachNewNode(slot_symbol(sl).node("sym"))
            sym.setScale(GEAR_HUD_H * 0.42)
            sym.setTransparency(TransparencyAttrib.MAlpha)
            sym.setColorScale(1, 1, 1, 0.16)
            item = tile.attachNewNode("item")                    # Platz für Text oder (später) Symbol
            label = OnscreenText(text="", parent=item, pos=(0, -0.012), scale=GEAR_HUD_TEXT,
                                 fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.9), mayChange=True)
            self.gear_tiles[sl] = {"tile": tile, "bg": bg, "sym": sym, "item": item, "label": label}
        # Munition und Waffenwahl (Slot 1 = Hauptwaffe, 2 = Kleinwaffe, 3 = Kistenwaffe)
        self.ammo_text = OnscreenText(text="", parent=self.a2dBottomRight, pos=(-0.08, 0.08),
                                      scale=0.1, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.8),
                                      align=TextNode.ARight, mayChange=True)
        self.name_text = OnscreenText(text="", parent=self.a2dBottomRight, pos=(-0.08, 0.2),
                                      scale=0.05, fg=(1, 0.9, 0.3, 1), shadow=(0, 0, 0, 0.8),
                                      align=TextNode.ARight, mayChange=True)
        # Waffenleiste unten in der Mitte: drei Karten mit Waffenbild (Haupt-, Klein-, Kistenwaffe)
        # und die Granaten. Bilder liegen in festen Zeichenreihen (fixed-Bins), Text darüber.
        def hud_card(x, w, h, col, sort):
            c = CardMaker("c")
            c.setFrame(-w / 2, w / 2, -h / 2, h / 2)
            n = self.a2dBottomCenter.attachNewNode(c.generate())
            n.setPos(x, 0, 0.115)
            n.setColor(*col)
            n.setTransparency(TransparencyAttrib.MAlpha)
            n.setBin("fixed", sort)
            n.setDepthTest(False)
            n.setDepthWrite(False)
            return n

        self.slot_frames, self.slot_icons, self.slot_labels = [], [], []
        for i in range(N_SLOTS):
            x = (i - N_SLOTS / 2) * 0.34
            self.slot_frames.append(hud_card(x, 0.32, 0.17, (0.4, 0.4, 0.4, 0.6), 19))
            hud_card(x, 0.30, 0.15, (0.05, 0.06, 0.09, 0.78), 20)
            holder = self.a2dBottomCenter.attachNewNode("slot_holder")   # eigener Halter je Karte
            holder.setPos(x, 0, 0.115)
            holder.setScale(0.7)
            icons = {"holder": holder, "cur": None, "nodes": {}}
            self.slot_icons.append(icons)
            lab = OnscreenText(
                text=str(i + 1) + (" Spezial" if i == SPECIAL_SLOT else ""), parent=self.a2dBottomCenter, pos=(x - 0.135, 0.165), scale=0.04,
                fg=(1, 1, 1, 0.8), shadow=(0, 0, 0, 0.8), align=TextNode.ALeft, mayChange=True)
            lab.setBin("fixed", 25)
            self.slot_labels.append(lab)
        # Fähigkeiten/Buffs: Symbole links über der Minimap (Buff vom Fluchttier; Ausrüstung kommt dazu)
        self.ability_icons = {"buff": AbilityIcon(self.a2dBottomLeft, 0.13, 0.78, "B", (1.0, 0.8, 0.2)),
                              "dash": AbilityIcon(self.a2dBottomLeft, 0.29, 0.78, "D", GEAR[GEAR_IDX["Hermes-Schuhe"]].col),
                              "jet": AbilityIcon(self.a2dBottomLeft, 0.45, 0.78, "J", GEAR[GEAR_IDX["Jetpack"]].col)}
        # Nahkampf-Slot (eigener Slot: Taste 4 oder F ohne etwas Benutzbares in der Nähe)
        mx_ = (N_SLOTS / 2) * 0.34 - 0.03
        self.melee_frame = hud_card(mx_, 0.26, 0.17, (0.4, 0.4, 0.4, 0.6), 19)
        hud_card(mx_, 0.24, 0.15, (0.05, 0.06, 0.09, 0.78), 20)
        self.melee_holder = self.a2dBottomCenter.attachNewNode("melee_holder")
        self.melee_holder.setPos(mx_, 0, 0.11)
        self.melee_icons, self.melee_icon_cur = {}, None
        self.melee_label = OnscreenText(text="4 Nahkampf", parent=self.a2dBottomCenter, pos=(mx_ - 0.115, 0.165),
                                        scale=0.034, fg=(1, 1, 1, 0.8), shadow=(0, 0, 0, 0.8), align=TextNode.ALeft,
                                        mayChange=True)
        self.melee_label.setBin("fixed", 25)
        gx_ = mx_ + 0.25
        self.gren_frame = hud_card(gx_, 0.2, 0.17, (0.4, 0.4, 0.4, 0.6), 19)
        hud_card(gx_, 0.18, 0.15, (0.05, 0.06, 0.09, 0.78), 20)
        gi = self.gren_icon.instanceTo(self.a2dBottomCenter)
        gi.setPos(gx_ - 0.03, 0, 0.115)
        gi.setBin("fixed", 21)
        gi.setDepthTest(False)
        gi.setDepthWrite(False)
        self.gren_text = OnscreenText(text="", parent=self.a2dBottomCenter, pos=(gx_ + 0.05, 0.1),
                                      scale=0.06, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.8),
                                      align=TextNode.ACenter, mayChange=True)
        self.gren_text.setBin("fixed", 25)
        gk = OnscreenText(text="G", parent=self.a2dBottomCenter, pos=(gx_ - 0.085, 0.165), scale=0.04,
                          fg=(1, 1, 1, 0.8), shadow=(0, 0, 0, 0.8), align=TextNode.ALeft, mayChange=False)
        gk.setBin("fixed", 25)
        self.speed_text = OnscreenText(text="", pos=(0, -0.7), scale=0.08, fg=(1, 0.9, 0.3, 1),
                                       shadow=(0, 0, 0, 0.9), mayChange=True)
        self.dead_hint = OnscreenText(text="", pos=(0, -0.72), scale=0.06, fg=(0.95, 0.8, 0.8, 1),
                                      shadow=(0, 0, 0, 0.9), mayChange=True)
        self.reload_text = OnscreenText(text="NACHLADEN", pos=(0, -0.35), scale=0.06,
                                        fg=(1, 0.9, 0.3, 1), shadow=(0, 0, 0, 0.8), mayChange=True)
        self.reload_text.hide()
        self.kill_text = OnscreenText(text="", parent=self.a2dTopRight, pos=(-0.05, -0.08),   # nicht mehr im HUD
                                      scale=0.05, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.8),
                                      align=TextNode.ARight, mayChange=True)
        self.kill_text.hide()
        self.timer_text = OnscreenText(text="", parent=self.a2dTopCenter, pos=(0, -0.09),
                                       scale=0.06, fg=(1, 0.9, 0.3, 1), shadow=(0, 0, 0, 0.9),
                                       mayChange=True)
        self.score_text = OnscreenText(text="", parent=self.a2dTopRight, pos=(-0.05, -0.28),   # -> Tab
                                       scale=0.042, fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.8),
                                       align=TextNode.ARight, mayChange=True)
        self.score_text.hide()
        self.feed_text = OnscreenText(text="", parent=self.a2dTopLeft, pos=(HUD_MARGIN, -0.08),   # Killfeed
                                      scale=HUD_TEXT, fg=(1, 0.92, 0.78, 1), shadow=(0, 0, 0, 0.8),
                                      align=TextNode.ALeft, mayChange=True)
        self.prompt_text = OnscreenText(text="", pos=(0, -0.55), scale=0.055, fg=(1, 0.95, 0.5, 1),
                                        shadow=(0, 0, 0, 0.9), mayChange=True)
        self.toast_text = OnscreenText(text="", pos=(0, 0.42), scale=0.052, fg=(1, 0.85, 0.3, 1),
                                       shadow=(0, 0, 0, 0.9), mayChange=True)   # kurzer Hinweis, verschwindet
        self.toast_t = 0.0
        self.dead_text = OnscreenText(text="", pos=(0, 0.62), scale=0.07, fg=(0.95, 0.8, 0.8, 1),
                                      shadow=(0, 0, 0, 0.9), mayChange=True)
        self.over_text = OnscreenText(text="", pos=(0, 0.55), scale=0.065, fg=(1, 0.95, 0.6, 1),
                                      shadow=(0, 0, 0, 0.9), mayChange=True)
        self.strike_text = OnscreenText(text="", parent=self.a2dTopCenter, pos=(0, -0.2), scale=0.065,
                                        fg=(1, 0.25, 0.15, 1), shadow=(0, 0, 0, 0.95), mayChange=True)
        self._txt = {}

        # Zielfernrohr (nur Scharfschütze/Railgun beim Zielen)
        sm = Mesh(lit=False)
        n, r0, r1 = 64, 0.92, 4.0

        def pt(r, a):
            return (math.cos(a) * r, 0.0, math.sin(a) * r)

        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            sm.tri(pt(r0, a0), pt(r1, a0), pt(r1, a1), (0, 0, 0), ref=(0, 5, 0))
            sm.tri(pt(r0, a0), pt(r1, a1), pt(r0, a1), (0, 0, 0), ref=(0, 5, 0))
        self.scope = self.aspect2d.attachNewNode(sm.node("scope"))
        for fr in ((-0.92, 0.92, -0.0015, 0.0015), (-0.0015, 0.0015, -0.92, 0.92)):
            cm = CardMaker("lines")
            cm.setFrame(*fr)
            self.scope.attachNewNode(cm.generate()).setColor(0, 0, 0, 1)
        self.scope.hide()
        # Visier des Raketenwerfers: Sichtfeld mit Vignette, Strichkreuz, Vorhaltmarken, Entfernungsmesser
        rs = self.aspect2d.attachNewNode("rocket_sight")
        vm = Mesh(lit=False)
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            vm.tri(pt(0.86, a0), pt(r1, a0), pt(r1, a1), (0, 0, 0), ref=(0, 5, 0))
            vm.tri(pt(0.86, a0), pt(r1, a1), pt(0.86, a1), (0, 0, 0), ref=(0, 5, 0))
        rs.attachNewNode(vm.node("vignette"))
        amber = (1.0, 0.85, 0.2, 1)
        for fr in ((-0.86, -0.07, -0.0018, 0.0018), (0.07, 0.86, -0.0018, 0.0018),
                   (-0.0018, 0.0018, 0.07, 0.55), (-0.0018, 0.0018, -0.86, -0.07),
                   (-0.012, 0.012, -0.0018, 0.0018)):
            cm = CardMaker("rs_line")
            cm.setFrame(*fr)
            rs.attachNewNode(cm.generate()).setColor(*amber)
        self.rs_ticks = []
        for rng_m in (100, 200, 300, 400):
            hold = rs.attachNewNode("rs_tick")
            cm = CardMaker("rs_t")
            cm.setFrame(-0.045, 0.045, -0.002, 0.002)
            hold.attachNewNode(cm.generate()).setColor(*amber)
            OnscreenText(text=str(rng_m), parent=hold, pos=(0.07, -0.012), scale=0.032, fg=amber,
                         align=TextNode.ALeft, mayChange=False)
            self.rs_ticks.append((rng_m, hold))
        self.rs_range = OnscreenText(text="", parent=rs, pos=(0, -0.66), scale=0.07, fg=amber,
                                     shadow=(0, 0, 0, 0.9), mayChange=True)
        self.rs_tag = OnscreenText(text="", parent=rs, pos=(0, 0.66), scale=0.05, fg=amber,
                                   shadow=(0, 0, 0, 0.9), mayChange=True)
        self.rscope = rs
        rs.hide()
        self.show_fps = False
        self.fps_text = OnscreenText(text="", parent=self.a2dTopRight, pos=(-HUD_MARGIN, -0.08), scale=0.04,
                                     fg=(0.7, 1, 0.7, 1), shadow=(0, 0, 0, 0.8), align=TextNode.ARight,
                                     mayChange=True)
        self.fps_text.hide()
        self.build_turret_sight()
        self.build_minimap()
        self.build_tab_overlay()

    def damage_popup(self, pct, head):
        """Zahl '+NN%' neben dem Treffermarker: Schaden in Prozent der Lebenspunkte des Ziels."""
        pct = max(1, int(pct))
        if self.pop_age < 0.35:                       # Schrotschrot / Feuerstoss: Zahlen addieren
            self.pop_pct += pct
        else:
            self.pop_pct = pct
        self.pop_age = 0.0
        self.pop_col = (1.0, 0.85, 0.2, 1) if head else (1, 1, 1, 1)

    def update_popup(self, dt):
        self.pop_age += dt
        life = 0.75
        if self.pop_age >= life or self.pop_pct <= 0:
            self.pop_text.hide()
            return
        k = self.pop_age / life
        self.set_text(self.pop_text, f"+{self.pop_pct}%")
        self.pop_text.setFg(self.pop_col)
        self.pop_text.setPos(0.075, 0.015 + 0.09 * k)       # gleitet nach oben
        self.pop_text.setColorScale(1, 1, 1, max(0.0, 1.0 - k * k * k))
        self.pop_text.show()

    def toggle_duck(self):
        """C: Ducken ein-/ausschalten (man bleibt geduckt, bis man C erneut drückt)."""
        if self.mode != "menu" and self.quit_box is None:
            self.duck_lock = not self.duck_lock

    def toggle_sound(self):
        if self.mode == "menu":
            return
        muted = self.sfx.toggle()
        self.toast("Ton aus  (M)" if muted else "Ton an  (M)", (0.9, 0.9, 0.95), 1.5)

    def toggle_fps(self):
        self.show_fps = not getattr(self, "show_fps", False)
        (self.fps_text.show if self.show_fps else self.fps_text.hide)()

    def set_text(self, t, s):
        """Text nur neu erzeugen, wenn er sich geändert hat (spart Rechenzeit)."""
        if self._txt.get(id(t)) != s:
            self._txt[id(t)] = s
            t.setText(s)

    # ------------------------------------------------------------ Eingabe
    def request_weapon(self, slot):
        """Slot 0 = Hauptwaffe, 1 = Kleinwaffe, 2 = Kistenwaffe (falls vorhanden)."""
        wi = self.player.slots[slot]
        if wi is not None:
            self.sel_req = wi

    def cycle_weapon(self, d):
        if self.mode != "play" or self.player.hp <= 0 or self.quit_box is not None:
            return
        pl = self.player
        cur = self.sel_req if self.sel_req is not None else (
            pl.switch_to if pl.switch_t > 0 else (MELEE_SEL if pl.melee_out else pl.cur))
        have = [wi for wi in pl.slots if wi is not None] + [MELEE_SEL]
        if not have:
            return
        i = have.index(cur) if cur in have else 0
        self.sel_req = have[(i + d) % len(have)]

    def on_r(self):
        if self.mode != "play" or self.quit_box is not None:
            return
        pl = self.player
        if pl.hp > 0:
            self.reload_req = True
        elif self.world.phase == "play":
            if self.net_mode == "client":
                waited = time.time() - self.dead_since if self.dead_since is not None else 0.0
                if self.client is not None and not self.client.lost and waited >= self.world.respawn_delay:
                    self.client.request_respawn()   # der Host sucht den Startpunkt aus
            elif self.world.can_respawn(pl):
                self.world.respawn_player(pl)       # Einzelspiel/Host: Ereignis 'respawn' folgt

    def on_use(self):
        if self.mode == "play" and self.quit_box is None:
            self.use_req = True

    def on_alt(self):
        if self.mode == "play" and self.quit_box is None:
            self.alt_req = True

    def on_grenade(self):
        if self.mode == "play" and self.quit_box is None:
            self.throw_req = True

    def use_object(self, alt=False):
        """F: Kiste öffnen, Waffe aufheben, Fahrzeug/Geschütz/Flugzeug benutzen; V: Schützensitz am Wagen
        (der Host entscheidet)."""
        pl, world = self.player, self.world
        if not alt and pl.hp > 0 and world.phase == "play":
            r = world.nearest_use(pl)
            if r is None:                                   # nichts Benutzbares in der Nähe: Nahkampfwaffe ziehen
                if pl.vehicle < 0 and pl.heli < 0 and pl.mount < 0 and not pl.melee_out:
                    self.sel_req = MELEE_SEL
                return
        if not alt and pl.hp > 0 and world.phase == "play" and world.strike == 0:
            r = world.nearest_use(pl)
            if r is not None and r[0] == "button":          # Tomahawk: erst Ziel auf der Karte wählen
                if world.toma_ready() and world.toma_lock.get(self.my_id, 0.0) <= 0:
                    self.open_strike_map()
                return
        if self.net_mode == "client":
            if self.client is not None and not self.client.lost:
                self.client.send_use(alt)
        else:
            self.world.use_object(self.player, alt)

    @staticmethod
    def is_rocket(b):
        return b.blast_r > 0 and b.wi != WI_FLAK

    def my_heli(self):
        pl = self.player
        return self.world.heli_by_id(pl.heli) if pl.heli >= 0 else None

    def my_turret(self):
        pl, ts = self.player, self.world.turrets
        return ts[pl.mount] if 0 <= pl.mount < len(ts) else None

    def operate_turret(self, t, trigger, ads):
        """Am Geschütz: die Figur sitzt fest, Maus zielt (Nick begrenzt), Linke Maus feuert, Rechte zoomt."""
        pl = self.player
        pl.x, pl.y, pl.z = t.x, t.y, t.z - t.seat
        pl.vz, pl.on_ground, pl.moving, pl.ads = 0.0, True, False, bool(ads)
        pl.pitch = clampf(pl.pitch, t.pmin, t.pmax)
        pl.trig = bool(trigger) and not t.over
        pl.lean = pl.lean_x = pl.lean_y = 0.0
        pl.duck, pl.crouch = False, 0.0
        t.heading, t.pitch = pl.heading % 360.0, pl.pitch

    def fly_heli_ctl(self, hc, inp, dt, trigger, ads):
        """Helikopter steuern: WASD fliegen, Leertaste steigen, Shift sinken, Maus zielt (der Rumpf dreht nach),
        Linke Maus Minigun, Rechte Maus Rakete."""
        pl, world = self.player, self.world
        up = (1 if inp.jump else 0) - (1 if inp.run else 0)
        pl.pitch = clampf(pl.pitch, -75.0, 25.0)
        fly_heli(hc, inp.forward, inp.strafe, up, pl.heading, dt, world, stall=hc.stall_t > 0)
        if self.net_mode != "client" and hc.impact > 0:       # Einzelspiel/Host: Aufprall gleich auswerten
            world.heli_crash(hc, hc.impact)
            hc.impact = 0.0
        pl.x, pl.y, pl.z, pl.vz = hc.x, hc.y, hc.z + 0.4, 0.0
        pl.moving = pl.ads = False
        pl.on_ground = hc.ground
        pl.lean = pl.lean_x = pl.lean_y = 0.0
        pl.duck, pl.crouch = False, 0.0
        pl.trig = bool(trigger)
        if ads and not self.heli_ads:                        # Rakete (nur beim Drücken)
            if self.net_mode == "client":
                if self.client is not None and not self.client.lost:
                    self.client.send_rocket()
            else:
                world.heli_rocket(pl)
        self.heli_ads = bool(ads)

    def apply_gain(self, wi, slots, dup):
        """Eigene Waffe aus Kiste oder vom Boden erhalten (Ereignis 'loot'/'pickup'). Beim Host und im Einzelspiel
        hat die Welt die Slots schon umgestellt (take_weapon); als Mitspieler übernimmt man die Belegung des Hosts."""
        pl = self.player
        if not 0 <= wi < len(WEAPONS):
            return
        if self.net_mode == "client":
            new = [None] * N_SLOTS
            for i, v in enumerate(list(slots or ())[:N_SLOTS]):
                if isinstance(v, int) and 0 <= v < len(WEAPONS):
                    new[i] = v
            pl.slots = new
            if dup:
                stock_ammo(pl, wi)
            else:
                pl.guns[wi] = GunState(WEAPONS[wi])
            if pl.cur not in pl.slots:               # die Waffe in der Hand wurde getauscht
                pl.cur = pl.switch_to = wi
                pl.switch_t, pl.reload_t = SWITCH_T * 0.5, 0.0
            note_hand(pl)
        if not dup:
            self.sel_req = wi                        # gleich zur neuen Waffe wechseln

    def my_vehicle(self):
        pl = self.player
        return self.world.vehicle_by_id(pl.vehicle) if pl.vehicle >= 0 else None

    def throw_grenade(self):
        pl = self.player
        if pl.gren_cd > 0 or pl.grenades <= 0:
            return
        hr, pr = math.radians(pl.heading), math.radians(pl.pitch)
        d = (-math.sin(hr) * math.cos(pr), math.cos(hr) * math.cos(pr), math.sin(pr))
        eye = (pl.x + d[0] * 0.4, pl.y + d[1] * 0.4, pl.z + eye_h(pl) - 0.1 + d[2] * 0.4)
        if self.world.throw_grenade(pl, eye, d):
            pl.gren_cd = GREN_COOLDOWN
            self.sp_back.kick(2.5)                 # kleiner Ruck der Waffe beim Wurf
            self.sp_pitch.kick(-90)

    def set_capture(self, on):
        self.captured = on
        self.mouse_prev = None
        self.warp_ref = None
        if not hasattr(self.win, "requestProperties"):   # z.B. Offscreen-Test
            return
        props = WindowProperties()
        props.setCursorHidden(on)
        props.setMouseMode(WindowProperties.M_confined if on else WindowProperties.M_absolute)
        self.win.requestProperties(props)
        if on:
            self.recenter()

    def toggle_capture(self):
        if self.mode == "play":
            self.set_capture(not self.captured)

    # ------------------------------------------------------------------ Endbildschirm (5f)
    def open_end_screen(self, data):
        """Nach Rundenende: eigener Bildschirm im Stil des Hauptmenüs - Siegerpodest, Reiter mit Statistik
        (Maus oder Pfeiltasten / 1-6), Countdown bis zur nächsten Runde. Das Spiel steht so lange still."""
        self.close_end_screen()
        if self.tab_held:
            self.tab_up()
        if not isinstance(data, list):
            return
        a2 = self.aspect2d
        hidden = [c for c in a2.getChildren() if not c.isHidden()]
        for c in hidden:                                  # HUD aus
            c.hide()
        root = a2.attachNewNode("endscreen")
        root.setBin("gui-popup", 0)                       # über allem, was das HUD noch einblendet
        koth = bool(data) and data[0].get("mode") == "koth"
        cm = CardMaker("endbg")
        cm.setFrame(-3, 3, -1, 1)
        bg = root.attachNewNode(cm.generate())
        bg.setColor(0.05, 0.07, 0.11, 1.0)
        bg.setTransparency(TransparencyAttrib.MAlpha)
        OnscreenText(text="RUNDE VORBEI", parent=root, pos=(0, 0.86), scale=0.09, fg=(1.0, 0.62, 0.14, 1),
                     shadow=(0.35, 0.12, 0.0, 0.9), mayChange=False)
        cm.setFrame(-0.62, 0.62, 0.83, 0.838)
        root.attachNewNode(cm.generate()).setColor(1.0, 0.62, 0.14, 0.9)
        # Siegerpodest: 2. links, 1. Mitte, 3. rechts
        for place, x, h, col in ((1, 0.0, 0.26, (1.0, 0.78, 0.2)), (2, -0.5, 0.19, (0.78, 0.8, 0.85)),
                                 (3, 0.5, 0.13, (0.8, 0.5, 0.25))):
            if place > len(data):
                continue
            e = data[place - 1]
            cm.setFrame(x - 0.21, x + 0.21, 0.3, 0.3 + h)
            blk = root.attachNewNode(cm.generate())
            blk.setColor(col[0] * 0.55, col[1] * 0.55, col[2] * 0.55, 1)
            OnscreenText(text=str(place), parent=root, pos=(x, 0.3 + h * 0.35), scale=0.09, fg=col + (1,),
                         shadow=(0, 0, 0, 0.9), mayChange=False)
            val = f"{int(e['score'])} Punkte" if koth else f"K/D {e['kills'] / max(1, e['deaths']):.2f}"
            OnscreenText(text=e["name"][:14], parent=root, pos=(x, 0.3 + h + 0.07), scale=0.06 if place == 1 else 0.05,
                         fg=(1, 1, 1, 1), shadow=(0, 0, 0, 0.9), mayChange=False)
            OnscreenText(text=val, parent=root, pos=(x, 0.3 + h + 0.025), scale=0.035, fg=col + (1,),
                         mayChange=False)
        tabs = end_tabs(koth)
        self.end = {"root": root, "data": data, "tabs": tabs, "tab": 0, "cells": [], "hidden": hidden,
                    "koth": koth, "rects": []}
        labels = [f"{i + 1} {t[0]}" for i, t in enumerate(tabs)]
        widths = [len(lb) * 0.042 * 0.52 + 0.09 for lb in labels]   # Reiter nebeneinander, nach Textlänge
        x = -sum(widths) / 2
        for lb, wd in zip(labels, widths):
            cx = x + wd / 2
            t = OnscreenText(text=lb, parent=root, pos=(cx, 0.19), scale=0.042, fg=Hot.BASE, mayChange=True)
            self.end["rects"].append((x, x + wd, 0.16, 0.24, t))
            x += wd
        self.end["best"] = OnscreenText(text="", parent=root, pos=(0, -0.76), scale=0.05, fg=(1.0, 0.8, 0.3, 1),
                                        shadow=(0, 0, 0, 0.9), mayChange=True)
        self.end["count"] = OnscreenText(text="", parent=root, pos=(0, -0.9), scale=0.045, fg=(0.75, 0.85, 0.95, 1),
                                         mayChange=True)
        self.show_end_tab(0)
        self.set_capture(False)

    def show_end_tab(self, i):
        e = self.end
        if e is None:
            return
        i %= len(e["tabs"])
        e["tab"] = i
        for x0, x1, z0, z1, t in e["rects"]:
            t.setFg(Hot.ON if t is e["rects"][i][4] else Hot.BASE)
        for c in e["cells"]:
            c.destroy()
        e["cells"] = []
        title, cols, best_name, best_f = e["tabs"][i]
        data = e["data"][:8]
        root = e["root"]
        heads = ["Spieler"] + [c[0] for c in cols]
        n = len(cols)
        xs = [-0.95] + [-0.3 + (j + 0.5) * (1.3 / max(1, n)) for j in range(n)]
        z = 0.07
        for j, h in enumerate(heads):
            e["cells"].append(OnscreenText(text=h, parent=root, pos=(xs[j], z), scale=0.038, fg=(0.7, 0.8, 0.9, 1),
                                           align=TextNode.ALeft if j == 0 else TextNode.ACenter, mayChange=False))
        vals = [[c[1](row) for c in cols] for row in data]
        bests = []
        for j, c in enumerate(cols):                      # bester Wert je Spalte wird gold hervorgehoben
            nums = [v[j] for v in vals if isinstance(v[j], (int, float))]
            bests.append(max(nums) if c[2] and nums and max(nums) > 0 else None)
        for r, row in enumerate(data):
            z = -0.02 - r * 0.075
            me = row["pid"] == self.my_id
            e["cells"].append(OnscreenText(text=f"{r + 1}. {row['name'][:14]}" + ("  (du)" if me else ""), parent=root,
                                           pos=(xs[0], z), scale=0.042, fg=(1, 0.95, 0.75, 1) if me else (1, 1, 1, 1),
                                           align=TextNode.ALeft, mayChange=False))
            for j, v in enumerate(vals[r]):
                gold = bests[j] is not None and v == bests[j]
                e["cells"].append(OnscreenText(text=str(v), parent=root, pos=(xs[j + 1], z), scale=0.042,
                                               fg=(1.0, 0.78, 0.2, 1) if gold else (0.92, 0.94, 1, 1),
                                               mayChange=False))
        if best_f is None:                                # Übersicht: Sieger
            txt = f"Sieger: {data[0]['name']}" if data else ""
        else:
            top = max(data, key=best_f) if data else None
            txt = f"{best_name}: {top['name']}" if top is not None and best_f(top) > 0 else f"{best_name}: -"
        self.set_text(e["best"], txt)

    def end_click(self):
        p = self.mouse_2d()
        if p is None or self.end is None:
            return
        for i, (x0, x1, z0, z1, _t) in enumerate(self.end["rects"]):
            if x0 <= p[0] <= x1 and z0 <= p[1] <= z1:
                self.show_end_tab(i)
                return

    def end_key(self, d):
        if self.end is not None:
            self.show_end_tab(self.end["tab"] + d)

    def update_end_screen(self):
        e, world = self.end, self.world
        if e is None:
            return
        if world.phase == "play":                         # neue Runde hat begonnen
            self.close_end_screen()
            return
        left = int(math.ceil(max(0.0, world.over_t)))
        self.set_text(e["count"], f"Nächste Runde in {left} s" + ("   (Esc: Menü)" if left > 0 else ""))
        p = self.mouse_2d()
        for i, (x0, x1, z0, z1, t) in enumerate(e["rects"]):   # Hover wie im Hauptmenü
            if i != e["tab"]:
                on = p is not None and x0 <= p[0] <= x1 and z0 <= p[1] <= z1
                t.setFg(Hot.ON if on else Hot.BASE)

    def close_end_screen(self):
        e = getattr(self, "end", None)
        self.end = None
        if e is None:
            return
        for c in e["cells"]:
            c.destroy()
        e["root"].removeNode()
        for c in e["hidden"]:
            if not c.isEmpty():
                c.show()
        if self.mode == "play" and self.quit_box is None:
            self.set_capture(True)

    # ------------------------------------------------------------------ Tab: Scoreboard, Legende, Infos
    def tab_down(self):
        if getattr(self, "end", None) is not None:      # Endbildschirm: Tab blättert durch die Reiter
            self.end_key(1)
            return
        """Tab gedrückt halten: Scoreboard + Tasten-Legende; die Maus ist frei (Kamera steht), Mausover über
        Waffen, Ausrüstung und Buff zeigt Infos. Loslassen: weg, Maus wieder eingefangen."""
        if self.mode != "play" or self.quit_box is not None or self.tab_held:
            return
        self.tab_held = True
        self.tab_root.show()
        self.update_tab_overlay()
        if self.captured:
            self.set_capture(False)

    def tab_up(self):
        if not self.tab_held:
            return
        self.tab_held = False
        self.tab_root.hide()
        self.tip_root.hide()
        if self.mode == "play" and self.quit_box is None:
            self.set_capture(True)

    def build_tab_overlay(self):
        self.tab_held = False
        root = self.aspect2d.attachNewNode("tab")
        root.setBin("fixed", 70)
        root.setDepthTest(False)
        root.setDepthWrite(False)
        cm = CardMaker("tabbg")
        cm.setFrame(-TAB_W, TAB_W, -0.62, 0.78)
        bg = root.attachNewNode(cm.generate())
        bg.setColor(0.03, 0.04, 0.07, 0.82)
        bg.setTransparency(TransparencyAttrib.MAlpha)
        cm.setFrame(-TAB_W, TAB_W, 0.776, 0.784)
        root.attachNewNode(cm.generate()).setColor(1.0, 0.62, 0.14, 0.9)
        self.tab_title = OnscreenText(text="", parent=root, pos=(0, 0.69), scale=0.06, fg=(1.0, 0.75, 0.3, 1),
                                      shadow=(0, 0, 0, 0.9), mayChange=True)
        self.tab_cols = []                       # Spalten: (Kopf, Zeilen) - je Spalte ein Text, sauber ausgerichtet
        for x, al in TAB_COLS:
            a = TextNode.ALeft if al == "l" else TextNode.ARight
            hd = OnscreenText(text="", parent=root, pos=(x, 0.6), scale=HUD_TEXT, fg=(0.7, 0.8, 0.9, 1),
                              align=a, mayChange=True)
            rw = OnscreenText(text="", parent=root, pos=(x, 0.52), scale=HUD_TEXT, fg=(1, 1, 1, 1),
                              shadow=(0, 0, 0, 0.8), align=a, mayChange=True)
            self.tab_cols.append((hd, rw))
        self.tab_ip = OnscreenText(text="", parent=root, pos=(TAB_W - 0.05, 0.69), scale=0.03, fg=(0.6, 0.9, 0.6, 1),
                                   align=TextNode.ARight, mayChange=True)
        cm.setFrame(-TAB_W + 0.04, TAB_W - 0.04, 0.0, 0.004)
        sep = root.attachNewNode(cm.generate())
        sep.setColor(1, 1, 1, 0.25)
        sep.setTransparency(TransparencyAttrib.MAlpha)
        sep.setZ(0.06)
        OnscreenText(text="Steuerung", parent=root, pos=(0, -0.01), scale=0.048, fg=(1.0, 0.75, 0.3, 1),
                     shadow=(0, 0, 0, 0.9), mayChange=False)
        n3 = (len(KEY_LEGEND) + 2) // 3
        for c in range(3):
            part = KEY_LEGEND[c * n3:(c + 1) * n3]
            x0 = -TAB_W + 0.08 + c * (2 * TAB_W - 0.1) / 3
            OnscreenText(text="\n".join(k for k, _w in part), parent=root, pos=(x0, -0.1), scale=0.036,
                         fg=(1.0, 0.8, 0.4, 1), align=TextNode.ALeft, mayChange=False)
            OnscreenText(text="\n".join(w for _k, w in part), parent=root, pos=(x0 + 0.2, -0.1), scale=0.036,
                         fg=(0.88, 0.9, 0.95, 1), align=TextNode.ALeft, mayChange=False)
        OnscreenText(text="Maus über Waffen, Ausrüstung oder Buff: Infos", parent=root, pos=(0, -0.59), scale=0.032,
                     fg=(0.65, 0.7, 0.8, 1), mayChange=False)
        root.hide()
        self.tab_root = root
        tip = self.aspect2d.attachNewNode("tip")
        tip.setBin("fixed", 80)
        tip.setDepthTest(False)
        cm = CardMaker("tipbg")
        cm.setFrame(0, 1, -1, 0)
        self.tip_bg = tip.attachNewNode(cm.generate())
        self.tip_bg.setColor(0.02, 0.03, 0.05, 0.9)
        self.tip_bg.setTransparency(TransparencyAttrib.MAlpha)
        self.tip_text = OnscreenText(text="", parent=tip, pos=(0.025, -0.05), scale=0.036, fg=(1, 1, 1, 1),
                                     align=TextNode.ALeft, mayChange=True)
        tip.hide()
        self.tip_root = tip

    def mono_font(self):
        """Gleichbreite Schrift für Tabellen (fällt auf die Standardschrift zurück)."""
        if not hasattr(self, "_mono"):
            self._mono = None
            for path in ("C:\\Windows\\Fonts\\consola.ttf", "C:\\Windows\\Fonts\\cour.ttf",
                         "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"):
                try:
                    if os.path.exists(path):
                        from panda3d.core import Filename as _Fn
                        f = self.loader.loadFont(_Fn.fromOsSpecific(path))
                        if f is not None and f.isValid():
                            self._mono = f
                            break
                except Exception:
                    pass
        return self._mono

    def update_tab_overlay(self):
        mw = self.mouseWatcherNode                   # Tab-Loslassen verpasst (Fenster gewechselt)? dann zu
        if mw is not None and hasattr(mw, "is_button_down") and not getattr(self, "tab_test", False):
            if not mw.is_button_down(KeyboardButton.tab()):
                self.tab_up()
                return
        world = self.world
        t = max(0.0, world.time_left)
        self.set_text(self.tab_title, f"{MODE_NAMES[world.mode]}   {int(t) // 60:02d}:{int(t) % 60:02d}")
        koth = world.mode == "koth"
        heads = ["#", "Spieler", "Punkte" if koth else "K/D", "Kills", "Tode", "Monster", "Kisten", "Buffs"]
        cols = [[] for _ in heads]
        for i, p in enumerate(world.ranking()[:8]):
            mk, cr, bf = stat_summary(p)
            val = f"{int(p.score)}" if koth else f"{p.kills / max(1, p.deaths):.2f}"
            for c, v in enumerate((f"{i + 1}.", (p.name[:14] + ("  (du)" if p.pid == self.my_id else "")), val,
                                   p.kills, p.deaths, mk, cr, bf)):
                cols[c].append(str(v))
        for (hd, rw), h, vals in zip(self.tab_cols, heads, cols):
            self.set_text(hd, h)
            self.set_text(rw, "\n".join(vals))
        ip = getattr(self, "host_ip", None)
        self.set_text(self.tab_ip, f"Host-IP {ip}" if ip and self.net_mode == "host" else "")
        self.update_tooltip()

    def hover_targets(self):
        """(Mitte x, Mitte z, halbe Breite, halbe Höhe, Infotext) der HUD-Elemente mit Mausover-Info."""
        pl, out = self.player, []
        a2 = self.aspect2d
        for i, fr in enumerate(self.slot_frames):
            wi = pl.slots[i] if i < len(pl.slots) else None
            if wi is not None:
                p = fr.getPos(a2)
                out.append((p[0], p[2], 0.16, 0.085, weapon_info(wi, pl.guns[wi])))
        for sl, tl in self.gear_tiles.items():
            gi = pl.gear.get(sl)
            if gi is not None:
                p = tl["tile"].getPos(a2)
                out.append((p[0], p[2], GEAR_HUD_W / 2, GEAR_HUD_H / 2, gear_info(gi)))
        p = self.melee_frame.getPos(a2)
        out.append((p[0], p[2], 0.13, 0.085, melee_info(pl.melee)))
        b = getattr(pl, "buff", None)
        ic = self.ability_icons.get("buff")
        if b in BUFF_T and pl.buff_t > 0 and ic is not None:
            p = ic.root.getPos(a2)
            out.append((p[0], p[2], 0.065, 0.065, buff_info(b, pl)))
        for key, gk in (("dash", "dash"), ("jet", "jetpack")):
            gi = next((g for g in pl.gear.values() if g is not None and GEAR[g].kind == gk), None)
            ic = self.ability_icons.get(key)
            if gi is not None and ic is not None:
                p = ic.root.getPos(a2)
                out.append((p[0], p[2], 0.065, 0.065, gear_info(gi)))
        return out

    def update_tooltip(self):
        mw = self.mouseWatcherNode
        if not self.tab_held or mw is None or not mw.hasMouse():
            self.tip_root.hide()
            return
        mx, mz = mw.getMouseX() * self.getAspectRatio(), mw.getMouseY()
        for cx, cz, hw, hh, text in self.hover_targets():
            if abs(mx - cx) <= hw and abs(mz - cz) <= hh:
                self.set_text(self.tip_text, text)
                lines = text.split("\n")
                w = 0.05 + 0.036 * 0.6 * max(len(ln) for ln in lines)
                h = 0.03 + 0.036 * 1.2 * len(lines)
                ar = self.getAspectRatio()
                x = mx + 0.04 if mx < 0 else mx - w - 0.04       # zur Bildmitte hin aufklappen
                x = min(max(x, -ar + 0.02), ar - w - 0.02)
                z = min(max(mz + h + 0.04, -1 + h + 0.02), 0.98)
                self.tip_root.setPos(x, 0, z)
                self.tip_bg.setScale(w, 1, h)
                self.tip_root.show()
                return
        self.tip_root.hide()

    def recenter(self):
        self.warp_ref = None
        if self.win.movePointer(0, self.win.getXSize() // 2, self.win.getYSize() // 2):
            self.warp_pending = True
            self.warp_frames = 0

    def mouse_look(self):
        """Liest die Mausbewegung als Differenz zur letzten Position und wendet sie an. Verlässt der Zeiger den
        mittleren Bereich, wird er zur Fenstermitte zurückgesetzt. Das Zurücksetzen kommt beim System oft erst
        ein paar Frames später an (vor allem bei niedriger Bildrate) - bis dahin meldet es weiter die alte
        Position. Jede Meldung danach wird deshalb auf zwei Arten gedeutet: "noch nicht zurückgesetzt"
        (Bewegung ab der letzten gezählten Position) oder "schon zurückgesetzt" (Bewegung ab der Mitte). Die
        kleinere Bewegung ist die echte - so wird jede Mausbewegung genau einmal gezählt: kein Einfrieren
        (frühere Version) und kein Überdrehen (doppelt gezählte Bewegung). Rückgabe: (dx, dy) in Pixeln."""
        if not self.captured or not hasattr(self.win, "getPointer"):
            return 0, 0
        if not self.win.getProperties().getForeground():
            self.mouse_prev, self.warp_ref = None, None
            return 0, 0
        p = self.win.getPointer(0)
        x, y = p.getX(), p.getY()
        sx, sy = self.win.getXSize(), self.win.getYSize()
        cx, cy = sx // 2, sy // 2
        outside = abs(x - cx) > sx * 0.25 or abs(y - cy) > sy * 0.25
        if self.warp_pending and self.warp_ref is None:     # Maus gerade eingefangen: auf die Mitte warten
            self.warp_frames += 1
            if outside and self.warp_frames <= MOUSE_WARP_GRACE:
                return 0, 0
            self.warp_pending = False
            self.mouse_prev = (x, y)
            return 0, 0
        if self.warp_ref is not None:                        # Zurücksetzen unterwegs
            rx, ry = self.warp_ref
            m1 = (x - rx, y - ry)                            # noch alte Zeigerposition
            m2 = (x - cx, y - cy)                            # schon in der Mitte angekommen
            self.warp_frames += 1
            if m2[0] * m2[0] + m2[1] * m2[1] <= m1[0] * m1[0] + m1[1] * m1[1]:
                dx, dy = m2
                self.warp_ref = None
                self.warp_pending = False
            else:
                dx, dy = m1
                self.warp_ref = (x, y)
                if self.warp_frames >= MOUSE_WARP_RETRY and self.win.movePointer(0, cx, cy):
                    self.warp_frames = 0                     # kam nicht an: nochmal
        else:
            if self.mouse_prev is None:
                self.mouse_prev = (x, y)
                return 0, 0
            dx, dy = x - self.mouse_prev[0], y - self.mouse_prev[1]
        self.mouse_prev = (x, y)
        if self.warp_ref is None and outside and self.win.movePointer(0, cx, cy):
            self.warp_ref = (x, y)                           # bis hierher ist alles gezählt
            self.warp_pending = True
            self.warp_frames = 0
        if dx or dy:
            pl = self.player
            sens = MOUSE_SENS * self.sens_mult * self.fov_cur / FOV      # beim Zoomen feinfühliger
            pl.heading -= dx * sens
            pl.pitch = clampf(pl.pitch - dy * sens, -85.0, 85.0)
        return dx, dy

    def build_turret_sight(self):
        """Visier für Wagengeschütz, MG-Turm und Flak: Strichkreuz mit Lücke, Streukreis (zeigt, wo die
        Schüsse landen), Vorhaltmarken (Flak), Entfernung zum Treffpunkt, Zielanzeige und Hitzebalken."""
        ts = self.aspect2d.attachNewNode("turret_sight")
        self.ts_cards, self.ts_texts = [], []                 # alles, was die Farbe wechselt

        def bar(parent, fr, store=True):
            cm = CardMaker("ts_l")
            cm.setFrame(*fr)
            n = parent.attachNewNode(cm.generate())
            n.setTransparency(TransparencyAttrib.MAlpha)
            if store:
                self.ts_cards.append(n)
            return n

        g, t = 0.025, 0.0016                                   # Lücke in der Mitte, halbe Strichdicke
        for fr in ((-0.20, -g, -t, t), (g, 0.20, -t, t), (-t, t, g, 0.14), (-t, t, -0.20, -g),
                   (-0.004, 0.004, -0.004, 0.004)):
            bar(ts, fr)
        for sgn in (-1, 1):                                    # kleine Querstriche auf den Schenkeln
            for d in (0.08, 0.14):
                bar(ts, (sgn * d - t, sgn * d + t, -0.012, 0.012))
        ring = Mesh(lit=False)
        n = 48

        def pt(r, a):
            return (math.cos(a) * r, 0.0, math.sin(a) * r)

        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            ring.tri(pt(0.9, a0), pt(1.0, a0), pt(1.0, a1), (1, 1, 1), ref=(0, 5, 0))
            ring.tri(pt(0.9, a0), pt(1.0, a1), pt(0.9, a1), (1, 1, 1), ref=(0, 5, 0))
        self.ts_ring = ts.attachNewNode(ring.node("ts_ring"))
        self.ts_ring.setTwoSided(True)
        self.ts_ring.setTransparency(TransparencyAttrib.MAlpha)
        self.ts_marks = []
        for rng_m in (200, 400, 600):
            hold = ts.attachNewNode("ts_tick")
            bar(hold, (-0.06, 0.06, -0.0016, 0.0016))
            self.ts_texts.append(OnscreenText(text=str(rng_m), parent=hold, pos=(0.085, -0.012), scale=0.032,
                                              fg=(1, 0.85, 0.2, 1), align=TextNode.ALeft, mayChange=True))
            self.ts_marks.append((rng_m, hold))
        amber = (1.0, 0.85, 0.2, 1)
        self.ts_range = OnscreenText(text="", parent=ts, pos=(0, -0.30), scale=0.06, fg=amber,
                                     shadow=(0, 0, 0, 0.9), mayChange=True)
        self.ts_tag = OnscreenText(text="", parent=ts, pos=(0, 0.30), scale=0.045, fg=amber,
                                   shadow=(0, 0, 0, 0.9), mayChange=True)
        self.ts_texts += [self.ts_range, self.ts_tag]
        bg = bar(ts, (-0.15, 0.15, -0.40, -0.375), store=False)
        bg.setColor(0, 0, 0, 0.55)
        self.ts_heat = bar(ts, (0, 1, -0.396, -0.379), store=False)
        self.ts_heat.setPos(-0.145, 0, 0)
        self.ts_col = None
        self.tsight = ts
        ts.hide()

    def update_turret_sight(self, t):
        """Visier am Geschütz t nachführen (Streukreis, Vorhalt, Entfernung, Ziel, Hitze)."""
        pl, world = self.player, self.world
        flak = t.kind == "flak"
        try:
            asp = float(self.getAspectRatio())
        except (TypeError, ValueError):
            asp = 1.6
        tv = max(math.tan(math.radians(self.fov_cur) / 2.0) / max(asp, 0.5), 1e-4)
        spread = 0.5 if flak else TUR_SPREAD * 0.7
        self.ts_ring.setScale(max(0.03, math.tan(math.radians(spread)) / tv))
        spd = FLAK_SPEED if flak else TUR_SPEED
        for rng_m, hold in self.ts_marks:
            drop = 0.5 * GRAV_BULLET * (rng_m / spd) ** 2
            z = -math.tan(math.atan2(drop, rng_m)) / tv
            if flak and 0.05 < abs(z) < 0.8:
                hold.setZ(z)
                hold.show()
            else:
                hold.hide()
        hr, pr = math.radians(t.heading), math.radians(t.pitch)
        f = (-math.sin(hr) * math.cos(pr), math.cos(hr) * math.cos(pr), math.sin(pr))
        ex, ey, ez = t.x, t.y, t.z
        dist, target = None, False
        for i in range(1, 201):
            d = i * 2.0
            x, y, z = ex + f[0] * d, ey + f[1] * d, ez + f[2] * d
            if not target:
                for m in world.mobs:
                    if m.state != "dead" and math.hypot(m.x - x, m.y - y) < m.radius + 0.8 \
                            and m.z - 0.5 < z < m.z + m.height + 0.5:
                        target = True
                        break
                else:
                    for o in world.players.values():
                        if (o.pid != pl.pid and o.hp > 0 and math.hypot(o.x - x, o.y - y) < PLAYER_HIT_R + 0.8
                                and o.z - 0.5 < z < o.z + 2.2):
                            target = True
                            break
                if target:
                    dist = d
                    break
            if z <= world.ground_for(x, y, z + 0.5) or world.in_solid(x, y, 0.05, z):
                dist = d
                break
        col = (1.0, 0.25, 0.2, 1) if target else ((0.45, 0.8, 1.0, 1) if t.over else (1.0, 0.85, 0.2, 1))
        if col != self.ts_col:
            self.ts_col = col
            for c in self.ts_cards:
                c.setColor(*col)
            for tx in self.ts_texts:
                tx.setFg(col)
            self.ts_ring.setColorScale(*col)
        self.set_text(self.ts_range, ("ZIEL  " if target else "") + (f"{int(dist)} m" if dist else "-- m"))
        self.set_text(self.ts_tag, f"{TURRET_NAMES.get(t.kind, 'Geschütz')}   x{FOV / max(self.fov_cur, 1.0):.1f}")
        heat = clampf(t.heat, 0.0, 1.0)
        self.ts_heat.setScale(max(0.001, 0.29 * heat), 1, 1)
        self.ts_heat.setColor(*((0.45, 0.8, 1.0, 1) if t.over else
                                (1.0, 0.3, 0.15, 1) if heat > 0.7 else (1.0, 0.8, 0.2, 1)))

    def update_rocket_sight(self):
        """Visier des Raketenwerfers: Vorhaltmarken für die Flugbahn (Raketen fallen) und Entfernungsmesser."""
        pl, world = self.player, self.world
        w = WEAPONS[pl.cur]
        try:
            asp = float(self.getAspectRatio())
        except (TypeError, ValueError):
            asp = 1.6
        tv = math.tan(math.radians(self.fov_cur) / 2.0) / max(asp, 0.5)
        for rng_m, holder in self.rs_ticks:
            t = rng_m / w.speed
            drop = 0.5 * GRAV_BULLET * w.grav * t * t
            z = -math.tan(math.atan2(drop, rng_m)) / max(tv, 1e-4)
            if abs(z) < 0.88:
                holder.setZ(z)
                holder.show()
            else:
                holder.hide()
        hr, pr = math.radians(pl.heading), math.radians(pl.pitch)
        f = (-math.sin(hr) * math.cos(pr), math.cos(hr) * math.cos(pr), math.sin(pr))
        ex, ey, ez = pl.x, pl.y, pl.z + eye_h(pl)
        dist = None
        for i in range(1, 161):
            d = i * 2.5
            x, y, z = ex + f[0] * d, ey + f[1] * d, ez + f[2] * d
            if z <= world.ground_for(x, y, z + 0.5) or world.in_solid(x, y, 0.05, z):
                dist = d
                break
        self.set_text(self.rs_range, f"{int(dist)} m" if dist else "-- m")
        self.set_text(self.rs_tag, f"RAKETENWERFER   x{FOV / max(self.fov_cur, 1.0):.1f}")

    # ------------------------------------------------------- Kamera / Schleife
    # ------------------------------------------------------------ Grafik
    def flat_card(self, name, tex):
        """Quadrat (Kantenlänge 2) flach auf dem Boden, mit Textur; Schatten und Brandflecken."""
        root = NodePath(name)
        cm = CardMaker(name)
        cm.setFrame(-1, 1, -1, 1)
        card = root.attachNewNode(cm.generate())
        card.setP(-90)
        card.setTwoSided(True)
        t = get_tex(tex)
        if t is not None:
            card.setTexture(t)
        return root

    def build_sky_nodes(self):
        """Himmelskuppel mit Farbverlauf, Wolkenschicht und Sonne; folgt der Kamera."""
        dome, clouds = build_sky()
        root = self.render.attachNewNode("himmel")
        d = root.attachNewNode(dome)
        d.setBin("background", 0)
        d.setTwoSided(True)
        c = root.attachNewNode(clouds)
        c.setBin("background", 1)
        c.setTwoSided(True)
        c.setTransparency(TransparencyAttrib.MAlpha)
        c.setColorScale(1.0, 0.98, 0.95, 1)
        t = get_tex("cloud")
        if t is not None:
            c.setTexture(t)
        for scale, k in ((120.0, 0), (26.0, 1)):                  # Sonnenschein + heller Kern
            cm = CardMaker("sonne")
            cm.setFrame(-1, 1, -1, 1)
            card = root.attachNewNode(cm.generate())
            card.setPos(*(v * SKY_RADIUS * 0.9 for v in SUN))
            card.setScale(scale)
            card.setBillboardPointEye()
            tg = get_tex("glow")
            if tg is not None:
                card.setTexture(tg)
            card.setTransparency(TransparencyAttrib.MAlpha)
            try:
                card.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha,
                                                     ColorBlendAttrib.OOne))
            except Exception:
                pass
            card.setBin("background", 2 + k)
        root.setLightOff()
        root.setFogOff()
        root.setDepthWrite(False)
        root.setDepthTest(False)
        self.sky_root, self.sky_clouds = root, c

    def build_vignette(self):
        """Dunkle Ränder wie bei einer Kamera - lenkt den Blick zur Bildmitte."""
        if self.vignette is None:
            cm = CardMaker("vignette")
            cm.setFrame(-1, 1, -1, 1)
            self.vignette = self.render2d.attachNewNode(cm.generate())
            t = get_tex("vignette")
            if t is not None:
                self.vignette.setTexture(t)
            self.vignette.setTransparency(TransparencyAttrib.MAlpha)
            self.vignette.setBin("fixed", 1)
            self.vignette.setDepthTest(False)
            self.vignette.setDepthWrite(False)
        self.vignette.show()

    def apply_gfx(self):
        """Grafik 'Hoch': echte Schatten der Sonne (Gelände, Gebäude, Bäume) und Bloom (Glühen).
        Alles in try/except: scheitert es, bleibt es bei Standard."""
        if self.gfx != "hoch":
            return
        try:
            sun = DirectionalLight("sonne")
            sun.setColor((0.36, 0.34, 0.30, 1))
            sun.setShadowCaster(True, 2048, 2048)
            lens = sun.getLens()
            lens.setFilmSize(90, 90)
            lens.setNearFar(20, 220)
            self.sun_np = self.render.attachNewNode(sun)
            amb = AmbientLight("umgebung")
            amb.setColor((0.72, 0.72, 0.74, 1))
            self.amb_np = amb_np = self.render.attachNewNode(amb)
            if not getattr(getattr(self, "world", None), "mc", None):      # Minecraft-Karte: Licht steckt schon in den Vertexfarben
                self.land_np.setLight(self.sun_np)
                self.land_np.setLight(amb_np)
                self.land_np.setShaderAuto()
        except Exception as e:
            print("Schatten nicht verfügbar:", e)
            self.sun_np = None
        try:
            from direct.filter.CommonFilters import CommonFilters
            self.filters = CommonFilters(self.win, self.cam)
            self.filters.setBloom(blend=(0.3, 0.4, 0.3, 0.0), mintrigger=0.62, maxtrigger=1.0,
                                  desat=0.6, intensity=0.9, size="medium")
        except Exception as e:
            print("Bloom nicht verfügbar:", e)
            self.filters = None

    def update_gfx(self, dt):
        """Pro Bild: Himmel folgt der Kamera, Wolken ziehen, Wasser plätschert, Blob-Schatten, Sonnenlicht."""
        t = time.time()
        cp = self.camera.getPos(self.render)
        if self.sky_root is not None:
            self.sky_root.setPos(cp)
            self.sky_clouds.setTexOffset(TextureStage.getDefault(), cp[0] / TILE["cloud"],
                                         cp[1] / TILE["cloud"])               # Wolken stehen fest am Himmel
        for i, wn in enumerate(self.water_nps):
            wn.setTexOffset(TextureStage.getDefault(), t * (0.021 if i == 0 else -0.016),
                            t * (0.012 if i == 0 else 0.019))
        self.update_shadows()
        if self.sun_np is not None:
            pl = self.player
            self.sun_np.setPos(pl.x + SUN[0] * 100, pl.y + SUN[1] * 100, pl.z + SUN[2] * 100)
            self.sun_np.lookAt(pl.x, pl.y, pl.z)

    def update_shadows(self):
        """Runde bzw. längliche weiche Schatten unter Figuren, Fahrzeugen und Helikoptern."""
        world = self.world
        if not hasattr(self, "shadow_tpl"):
            self.shadow_tpl = self.flat_card("schatten", "blob")
            self.shadow_tpl.setTransparency(TransparencyAttrib.MAlpha)
            self.shadow_tpl.setDepthWrite(False)
            self.shadow_tpl.setLightOff()
            self.shadow_tpl.setBin("transparent", 2)
            self.shadow_tpl.setDepthOffset(2)
        seen = set()

        def put(key, x, y, z, rx, ry, heading, alpha, fly=False):
            gz = world.floor_at(x, y, z + (0.3 if not fly else 0.0))
            if fly:
                gz = max(gz, world.ground_for(x, y, z))
                alpha *= max(0.0, 1.0 - (z - gz) / 28.0)
                rx *= 1.0 + (z - gz) * 0.03
                ry *= 1.0 + (z - gz) * 0.03
            if alpha < 0.03:
                return
            np = self.shadows.get(key)
            if np is None:
                np = self.shadows[key] = self.shadow_tpl.copyTo(self.render)
            seen.add(key)
            np.show()
            np.setPos(x - SUN[0] * 0.25, y - SUN[1] * 0.25, gz + 0.09)
            np.setScale(rx, ry, 1)
            np.setH(heading)
            np.setColor(0, 0, 0, alpha)

        for m in self.mob_views:
            if m.state != "dead":
                put(("m", id(m)), m.x, m.y, m.z, 0.62 * m.scale, 0.62 * m.scale, 0.0, 0.5)
        for pid in self.player_views:
            p = world.players.get(pid)
            if p is not None and p.hp > 0 and p.heli < 0 and p.vehicle < 0:
                put(("p", pid), p.x, p.y, p.z, 0.6, 0.6, 0.0, 0.5)
        for v in self.veh_views:
            put(("v", id(v)), v.x, v.y, v.z, 1.25, 2.1, v.heading, 0.55)
        for q in self.heli_views:
            put(("h", id(q)), q.x, q.y, q.z, 1.8, 3.2, q.heading, 0.5, fly=True)
        for k in [k for k in self.shadows if k not in seen]:
            self.shadows.pop(k).removeNode()

    def place_camera(self):
        pl = self.player
        bob = math.sin(pl.phase) * 0.045 if pl.moving and pl.on_ground else 0.0
        t = self.death_t if hasattr(self, "death_t") else 0.0
        eye = pl.z + (eye_h(pl) + bob) * (1 - t) + 0.35 * t
        pitch = pl.pitch * (1 - t) + (self.sp_cam.x if hasattr(self, "sp_cam") else 0.0)
        roll = (self.sp_hurt.x if hasattr(self, "sp_hurt") else 0.0) + 70.0 * t
        roll += pl.lean / LEAN_MAX * LEAN_ROLL * (1 - t)          # Lehnen: Kopf kippt zur Seite
        hc = self.my_heli() if pl.hp > 0 else None
        if hc is not None:                                        # Verfolgerkamera: Blick = Zielrichtung, Waffen schiessen entlang der Sichtlinie
            hr, pr = math.radians(pl.heading), math.radians(pitch)
            fx, fy, fz = -math.sin(hr) * math.cos(pr), math.cos(hr) * math.cos(pr), math.sin(pr)
            cx, cy, cz = hc.x - fx * 14.0, hc.y - fy * 14.0, hc.z + 2.5 - fz * 14.0
            cz = max(cz, self.world.height(cx, cy) + 0.8)
            self.camera.setPos(cx, cy, cz)
            self.camera.setHpr(pl.heading, pitch, roll + hc.roll * 0.2)
            return
        tur = self.my_turret() if pl.hp > 0 else None
        if tur is not None:                                       # hinter dem Rohr
            hr, pr = math.radians(pl.heading), math.radians(pitch)
            fx, fy = -math.sin(hr) * math.cos(pr), math.cos(hr) * math.cos(pr)
            dn = clampf(-pitch, 0.0, 65.0) / 65.0               # beim Blick nach unten höher und weiter hinten
            self.camera.setPos(tur.x - fx * (0.15 + 0.6 * dn), tur.y - fy * (0.15 + 0.6 * dn), tur.z + 0.55 + 0.6 * dn)
            self.camera.setHpr(pl.heading, pitch, roll * 0.3)
            return
        veh = self.my_vehicle() if pl.hp > 0 else None
        if veh is not None:                                       # Verfolgerkamera hinter dem Wagen
            hr, pr = math.radians(pl.heading), math.radians(pitch)
            fx, fy, fz = -math.sin(hr) * math.cos(pr), math.cos(hr) * math.cos(pr), math.sin(pr)
            cx, cy, cz = veh.x - fx * 7.0, veh.y - fy * 7.0, veh.z + 2.2 - fz * 7.0
            cz = max(cz, self.world.height(cx, cy) + 0.6)
            self.camera.setPos(cx, cy, cz)
            self.camera.setHpr(pl.heading, pitch, roll)
            return
        self.camera.setPos(pl.x, pl.y, eye)
        self.camera.setHpr(pl.heading, pitch, roll)

    def update_task(self, task):
        dt = min(globalClock.getDt(), 0.1)  # noqa: F821  (von Panda3D bereitgestellt)
        if self.mode == "menu":
            self.menu_task(dt)
            return task.cont
        mw = self.mouseWatcherNode
        if mw is None:
            return task.cont
        if self.quit_box is not None:
            self.update_hover()

        def down(btn):
            return mw.is_button_down(btn)

        k = KeyboardButton.ascii_key

        def key(name):                                 # zentrale Tastenzuordnung (KEYS)
            b = KEYS.get(name, "")
            if b == "shift":
                return down(KeyboardButton.shift())
            if b == "space":
                return down(KeyboardButton.space())
            if b == "control":
                return down(KeyboardButton.control())
            return down(k(b)) if len(b) == 1 else False
        trig = down(MouseButton.one())
        edge = trig and not self.prev_trig
        self.prev_trig = trig
        if (self.quit_box is not None or getattr(self, "tab_held", False)
                or getattr(self, "end", None) is not None):       # Abfrage/Tab/Endbildschirm: kein Schuss
            trig = edge = False
        elif not self.captured and edge:      # Klick fängt die Maus wieder ein
            self.set_capture(True)
            trig = edge = False
        elif not self.captured:
            trig = edge = False
        inp = SimpleNamespace(
            forward=key("forward") - key("back"), strafe=key("right") - key("left"),
            run=key("sprint"), jump=key("jump"),
            turn=down(KeyboardButton.left()) - down(KeyboardButton.right()),
            look=down(KeyboardButton.up()) - down(KeyboardButton.down()),
            lean=key("lean_right") - key("lean_left"),
            duck=key("duck") or self.duck_lock,
            trigger=trig, edge=edge, ads=down(MouseButton.three()) and not getattr(self, "tab_held", False),
            reload=self.reload_req, select=self.sel_req, use=self.use_req, alt=self.alt_req,
            throw=self.throw_req, mdx=0, mdy=0)
        if self.quit_box is not None:
            inp = SimpleNamespace(forward=0, strafe=0, run=False, jump=False, turn=0, look=0, lean=0,
                                  duck=False, trigger=False, edge=False, ads=False, reload=False, select=None,
                                  use=False, alt=False, throw=False, mdx=0, mdy=0)
        self.reload_req = False
        self.use_req = False
        self.alt_req = False
        self.throw_req = False
        self.sel_req = None
        inp.mdx, inp.mdy = self.mouse_look()
        self.tick(dt, inp)
        return task.cont

    def tick(self, dt, inp):
        """Ein Spielschritt (Logik + Darstellung). Getrennt von der Eingabe,
        damit man ihn auch ohne Fenster testen kann."""
        pl, world = self.player, self.world
        nsub = max(1, int(math.ceil(dt / 0.034)))
        dead = pl.hp <= 0
        if getattr(pl, "stun_t", 0.0) > 0 and not dead:   # betäubt (Drohne): nicht bewegen, schiessen, steuern;
            if self.net_mode == "client":                 # umschauen (Maus/Pfeiltasten) geht
                pl.stun_t = max(0.0, pl.stun_t - dt)
            inp = SimpleNamespace(**vars(inp))
            inp.forward = inp.strafe = inp.lean = 0
            inp.run = inp.jump = inp.trigger = inp.edge = inp.ads = inp.reload = False
            inp.use = inp.alt = inp.throw = False
            inp.select = None
        over = world.phase != "play"              # Rundenende: Rangliste, kein Schiessen mehr
        if dead:
            forward = strafe = 0
            run = jump = trigger = edge = reload_req = ads = False
            select = None
        else:
            forward, strafe, run, jump = inp.forward, inp.strafe, inp.run, inp.jump
            trigger, edge, reload_req, ads, select = inp.trigger, inp.edge, inp.reload, inp.ads, inp.select
            if over:                              # Rundenende: alles steht still (Endbildschirm)
                trigger = edge = reload_req = ads = False
                forward = strafe = 0
                run = jump = False
        if not dead:                                  # Tastenflanken für Dash (Shift) und Doppelsprung (Leertaste)
            pl.run_edge = pl.run_edge or (bool(run) and not getattr(self, "prev_run", False))
            pl.jump_edge = pl.jump_edge or (bool(jump) and not getattr(self, "prev_jump", False))
        self.prev_run, self.prev_jump = bool(run), bool(jump)
        self.run_now, self.key_turn = bool(run), inp.turn
        self.trig_now = bool(trigger)
        if dead or over_or_driving(self):
            self.duck_lock = False
        pl.heading += inp.turn * KEY_TURN * dt
        pl.pitch = clampf(pl.pitch + inp.look * KEY_TURN * 0.6 * dt, -85.0, 85.0)
        pl.gren_cd = max(0.0, pl.gren_cd - dt)
        world.sync_turret_pos()
        veh = None if dead else self.my_vehicle()
        hc = None if dead else self.my_heli()
        tur = None if dead else self.my_turret()
        if tur is None:
            pl.trig = False
        pl.duck = bool(getattr(inp, "duck", False)) and not dead and veh is None and hc is None and tur is None
        update_crouch(pl, dt, world)
        if hc is None:
            self.heli_ads = True               # erst nach neuem Drücken der rechten Maustaste feuert die Rakete
        if hc is not None:                     # im Cockpit
            self.fly_heli_ctl(hc, inp, dt, trigger and not over, ads and not over)
        elif tur is not None:                  # am Geschütz (Turm, Flak, Wagen-Heck)
            self.operate_turret(tur, trigger and not over, ads)
        elif veh is not None:                  # am Steuer: das Fahrzeug bewegt die Figur
            for _ in range(nsub):              # bei niedriger Bildrate in kleinen Schritten (keine Tunnel, kein Zeitlupen-Auto)
                if veh.stall_t > 0:            # Drohne hat den Motor lahmgelegt: kein Gas, Lenkung schwach
                    drive(veh, 0, strafe * VEH_STALL_STEER, jump, dt / nsub, world)
                else:
                    drive(veh, forward, strafe, jump, dt / nsub, world)
            pl.x, pl.y, pl.z, pl.vz, pl.on_ground = veh.x, veh.y, veh.z + 0.3, 0.0, True
            pl.moving, pl.ads = False, False
            update_lean(pl, 0, dt * 4, world)  # Lehnen beenden
        else:
            for _ in range(nsub):
                step(pl, forward, strafe, run, jump, dt / nsub, world)
            self.apply_fall(pl)
            if not dead:
                update_lean(pl, getattr(inp, "lean", 0) if not over else 0, dt, world)
            elif pl.lean:
                update_lean(pl, 0, dt, world)
        if not dead:
            if veh is None and hc is None and tur is None:
                update_weapon(pl, world, dt, trigger, edge, reload_req, ads, select)
                if getattr(inp, "throw", False) and not over:
                    self.throw_grenade()
            if pl.swing_t > getattr(self, "prev_swing", 0.0) + 0.01:     # eigener Schlag: Ton
                self.sfx.play("swoosh", None, 0.7, self.prng.uniform(0.9, 1.1) * (0.85 if pl.melee >= 3 else 1.0))
                self.noise_wave(pl.x, pl.y, NOISE_MELEE)
            self.prev_swing = pl.swing_t
            if getattr(inp, "use", False) and not over:
                self.use_object()
            if getattr(inp, "alt", False) and not over:
                self.use_object(True)
        if self.net_mode == "client":
            self.tick_client(dt)
        else:                              # Einzelspiel oder Host: die Welt läuft hier
            if self.host is not None:
                self.host.poll(dt)         # Eingaben und Schüsse der Mitspieler
            for _ in range(nsub):
                world.update(dt / nsub)
            if self.host is not None:
                self.host.queue_events(world.events)
                self.host.send(dt)         # Snapshot an alle Mitspieler
        self.handle_events()
        self.update_views(dt, inp.mdx, inp.mdy)

    def apply_fall(self, pl):
        """Fallschaden aus step() verrechnen: im Einzelspiel/als Host direkt, als Mitspieler beim Host melden."""
        dmg = getattr(pl, "fall_dmg", 0.0)
        if dmg <= 0.0:
            return
        pl.fall_dmg = 0.0
        if pl.hp <= 0 or self.world.phase != "play" or pl.protect > 0:
            return
        sfx = getattr(self, "sfx", None)
        if sfx is not None:
            sfx.play("step_hard", None, 1.0, 0.5)              # dumpfer Aufprall
        if self.net_mode == "client":
            if self.client is not None:
                self.client.send_fall(dmg)
        else:
            self.world.damage_player(pl, dmg, -1, WI_FALL)

    # ------------------------------------------------------------ Effekte
    def add_particle(self, pos, vel, col, size, life, bounce=0.3, spin=0.0, shrink=True):
        if len(self.parts) > 320:
            self.parts.pop(0).np.removeNode()
        np = self.cube_np.instanceTo(self.render)
        np.setScale(*size) if isinstance(size, tuple) else np.setScale(size)
        np.setColorScale(col[0], col[1], col[2], 1)
        np.setPos(*pos)
        np.setHpr(self.prng.uniform(0, 360), self.prng.uniform(0, 360), self.prng.uniform(0, 360))
        self.parts.append(Particle(np, pos, vel, life, bounce, spin, shrink))

    def burst(self, pos, kind, d=None):
        col, n, spd, size = {
            "ground": ((0.45, 0.36, 0.22), 6, 2.5, 0.05),
            "rock": ((0.8, 0.8, 0.85), 7, 4.0, 0.035),
            "tree": ((0.55, 0.38, 0.22), 6, 3.0, 0.05),
            "water": ((0.75, 0.88, 1.0), 10, 3.5, 0.045),
            "blood": ((0.75, 0.05, 0.05), 8, 3.0, 0.05),
            "kill": ((0.7, 0.05, 0.05), 22, 4.0, 0.06),
            "boom": ((1.0, 0.55, 0.12), 46, 9.0, 0.13),
        }[kind]
        r = self.prng
        for _ in range(n):
            v = [r.uniform(-1, 1) * spd * 0.6, r.uniform(-1, 1) * spd * 0.6, r.uniform(0.4, 1.0) * spd]
            if d is not None and kind in ("blood", "kill"):
                v[0] += d[0] * spd * 0.7
                v[1] += d[1] * spd * 0.7
            self.add_particle(pos, v, col, size, r.uniform(0.5, 1.0), bounce=0.3)
        if kind in ("ground", "rock", "tree") and r.random() < 0.4:
            self.smoke_puff(pos, 0.12, 0.7, 0.62 if kind != "tree" else 0.45)     # Staubwölkchen

    def fx_spawn(self, model, pos, life, s0, s1, c0, c1, p=1.0, rise=0.0, fog=True):
        """Animierten Effekt (Fx) anlegen: Instanz eines Effektmodells, transparent."""
        if len(self.fx) > 90:
            self.fx.pop(0).np.removeNode()
        np = model.instanceTo(self.render)
        np.setTransparency(TransparencyAttrib.MAlpha)
        np.setDepthWrite(False)
        np.setLightOff()
        if not fog:
            np.setFogOff()
        f = Fx(np, pos, life, s0, s1, c0, c1, p, rise)
        f.update(0.0)
        self.fx.append(f)
        return f

    def update_fx(self, dt):
        keep = []
        for f in self.fx:
            if f.update(dt):
                keep.append(f)
            else:
                f.np.removeNode()
        self.fx = keep

    def smoke_puff(self, pos, size=0.3, life=1.4, grey=0.55):
        r = self.prng
        self.fx_spawn(self.sphere_np, (pos[0] + r.uniform(-0.1, 0.1), pos[1] + r.uniform(-0.1, 0.1), pos[2]),
                      life, size * 0.5, size * 1.8, (grey, grey, grey), (grey * 0.5,) * 3,
                      p=1.0, rise=r.uniform(0.3, 0.9))

    def explosion_fx(self, pos, rad):
        """Explosionsanimation: weisser Blitz, Feuerball (gelb -> rot -> schwarz), Druckwelle am Boden,
        aufsteigender Rauch, Funken und Trümmer."""
        x, y, z = pos
        r = self.prng
        self.fx_spawn(self.sphere_np, pos, 0.16, rad * 0.12, rad * 0.42, (1.0, 1.0, 0.9), (1.0, 0.9, 0.5),
                      p=0.5, fog=False)
        self.fx_spawn(self.sphere_np, pos, 0.65, rad * 0.15, rad * 0.62, (1.0, 0.78, 0.22), (0.55, 0.08, 0.03),
                      p=0.9, fog=False)
        self.fx_spawn(self.sphere_np, (x, y, z + rad * 0.15), 0.9, rad * 0.1, rad * 0.45,
                      (0.95, 0.45, 0.1), (0.15, 0.05, 0.04), p=0.8, rise=rad * 0.35, fog=False)
        gz = self.world.ground_for(x, y, z + 0.5)
        self.fx_spawn(self.disc_np, (x, y, max(gz, z - 1.5) + 0.12), 0.5, rad * 0.15, rad * 1.25,
                      (1.0, 0.85, 0.6), (0.7, 0.55, 0.4), p=1.3, fog=False)
        for _ in range(6):
            off = (x + r.uniform(-0.3, 0.3) * rad, y + r.uniform(-0.3, 0.3) * rad, z + r.uniform(0, 0.3) * rad)
            self.fx_spawn(self.sphere_np, off, r.uniform(1.4, 2.4), rad * 0.12, rad * r.uniform(0.35, 0.55),
                          (0.30, 0.28, 0.27), (0.08, 0.08, 0.08), p=0.8, rise=r.uniform(1.0, 2.2))
        if z - gz < rad * 1.5:                                        # Brandfleck, der langsam verblasst
            self.fx_spawn(self.scorch_np, (x, y, gz + 0.1), 16.0, rad * 0.9, rad * 1.0,
                          (0.04, 0.035, 0.03), (0.04, 0.035, 0.03), p=0.7)
        self.burst(pos, "boom")
        for _ in range(10):                                           # Trümmer
            v = [r.uniform(-1, 1) * 5.0, r.uniform(-1, 1) * 5.0, r.uniform(4.0, 9.0)]
            self.add_particle(pos, v, (0.2, 0.18, 0.16), r.uniform(0.07, 0.16), r.uniform(0.8, 1.6), 0.35, 1.0)

    def rocket_launch_fx(self):
        """Rückstrahl hinten und Qualm vorn beim Abfeuern der Rakete (eigene Waffe)."""
        pl = self.player
        hr, pr = math.radians(pl.heading), math.radians(pl.pitch)
        f = (-math.sin(hr) * math.cos(pr), math.cos(hr) * math.cos(pr), math.sin(pr))
        base = (pl.x, pl.y, pl.z + eye_h(pl) - 0.15)
        for i in range(7):
            k = self.prng.uniform(0.2, 1.6)
            self.smoke_puff((base[0] + f[0] * k, base[1] + f[1] * k, base[2] + f[2] * k), 0.35, 1.2, 0.7)
        for i in range(5):
            k = self.prng.uniform(0.6, 1.4)
            self.smoke_puff((base[0] - f[0] * k, base[1] - f[1] * k, base[2] - f[2] * k + 0.1), 0.3, 1.0, 0.6)

    def eject_shell(self, w):
        pl = self.player
        hr, pr = math.radians(pl.heading), math.radians(pl.pitch)
        f = (-math.sin(hr) * math.cos(pr), math.cos(hr) * math.cos(pr), math.sin(pr))
        r = (math.cos(hr), math.sin(hr), 0.0)
        rr = self.prng
        pos = (pl.x + f[0] * 0.35 + r[0] * 0.15, pl.y + f[1] * 0.35 + r[1] * 0.15,
               pl.z + eye_h(pl) - 0.12 + f[2] * 0.35)
        sr, su, sf = rr.uniform(1.3, 2.4), rr.uniform(1.4, 2.4), rr.uniform(-0.3, 0.5)
        vel = (r[0] * sr + f[0] * sf, r[1] * sr + f[1] * sf, su)
        if w.pellets > 1:
            self.add_particle(pos, vel, (0.8, 0.12, 0.1), (0.03, 0.03, 0.07), 6.0, 0.35, 1.0, False)
        else:
            self.add_particle(pos, vel, (0.95, 0.72, 0.2), (0.015, 0.015, 0.05), 6.0, 0.4, 1.0, False)

    def pname(self, pid):
        p = self.world.players.get(pid)
        return p.name if p is not None else "?"

    def bullet_whiz(self, bullets):
        """Vorbeizischende Kugeln: fliegt eine fremde Kugel nah am eigenen Kopf vorbei, zischt es - aus der
        Richtung des Vorbeiflugs, je näher, desto lauter (WHIZ_FULL voll, bis WHIZ_MAX leiser, dann nichts).
        Geprüft wird die Strecke seit dem letzten Bild (jeder Rechner für die Kugeln, die er ohnehin zeigt)."""
        prev = getattr(self, "whiz_prev", {})
        if not hasattr(self, "whizzed"):
            self.whizzed = set()
        me = self.player
        nxt = {}
        if me.hp > 0:
            head = (me.x, me.y, me.z + eye_h(me))
            for b in bullets:
                cur = (b.x, b.y, b.z)
                nxt[b] = cur
                if b.owner == self.my_id or self.is_rocket(b) or b in self.whizzed:
                    continue
                p0 = prev.get(b)
                if p0 is None:                               # neu: ein kurzes Stück zurück (Mündung)
                    p0 = (b.x - b.vx * 0.04, b.y - b.vy * 0.04, b.z - b.vz * 0.04)
                ab = (cur[0] - p0[0], cur[1] - p0[1], cur[2] - p0[2])
                l2 = ab[0] * ab[0] + ab[1] * ab[1] + ab[2] * ab[2]
                if l2 < 1e-9:
                    continue
                t = ((head[0] - p0[0]) * ab[0] + (head[1] - p0[1]) * ab[1] + (head[2] - p0[2]) * ab[2]) / l2
                if not 0.0 <= t < 1.0:                       # noch nicht am Kopf vorbei (oder schon lange)
                    continue
                c = (p0[0] + ab[0] * t, p0[1] + ab[1] * t, p0[2] + ab[2] * t)
                d = math.dist(c, head)
                if d >= WHIZ_MAX:
                    continue
                self.whizzed.add(b)
                vol = 1.0 if d <= WHIZ_FULL else 1.0 - (d - WHIZ_FULL) / (WHIZ_MAX - WHIZ_FULL)
                self.sfx.play("whiz", c, WHIZ_VOL * vol, self.prng.uniform(0.9, 1.15))
        self.whiz_prev = nxt
        alive = set(bullets)
        self.whizzed = {b for b in self.whizzed if b in alive}

    def stall_flicker(self, root, pos):
        """Lahmgelegtes Fahrzeug: blau flackern (für alle sichtbar), ab und zu ein Blitz-Funke."""
        k = 0.5 + 0.5 * math.sin(time.time() * 38.0)
        root.setColorScale(0.6 + 0.2 * k, 0.75 + 0.2 * k, 1.3 + 0.5 * k, 1)
        if self.prng.random() < 0.12:
            p = (pos[0] + self.prng.uniform(-1, 1), pos[1] + self.prng.uniform(-1, 1), pos[2] + self.prng.uniform(-0.3, 0.6))
            self.zap_fx(p, (p[0] + self.prng.uniform(-0.8, 0.8), p[1] + self.prng.uniform(-0.8, 0.8), p[2] + 0.5),
                        False, sound=self.prng.random() < 0.25)

    def toast(self, text, col=(1, 0.85, 0.3), dur=TOAST_T):
        """Kurzer, deutlicher Hinweis in der Bildmitte (Buff erhalten, "Hast du schon" ...)."""
        self.toast_text.setText(text)
        self.toast_text.setFg(tuple(col) + (1,))
        self.toast_text.setAlphaScale(1.0)
        self.toast_text.setTransparency(TransparencyAttrib.MAlpha)
        self.toast_t = dur

    def feed_add(self, text):
        self.feed.append((text, time.time()))

    def handle_events(self):
        for e in self.world.events:
            kind = e[0]
            if kind == "shot":
                if e[2] == self.my_id:
                    self.sfx.shot(e[1], e[2])
                    if 0 <= e[1] < len(WEAPONS):
                        self.noise_wave(self.player.x, self.player.y, NOISE_SHOT * WEAPONS[e[1]].loud)
                if e[2] != self.my_id:      # nur eigene Schüsse: Rückstoss, Feuer, Hülse
                    continue
                w = WEAPONS[e[1]]
                rr = self.prng
                self.sp_back.kick(w.kick_back * 0.2)
                self.sp_pitch.kick(w.kick_back * 18)
                self.sp_roll.kick(rr.uniform(-1, 1) * w.kick_back * 6)
                self.sp_cam.kick(w.kick * 22)
                self.flash_t = 0.05
                self.gun_flash[e[1]].setR(rr.uniform(0, 360))
                self.gun_flash[e[1]].setScale(rr.uniform(0.8, 1.4) * (1.6 if w.pellets > 1 else 1.0))
                if w.blast_r <= 0:
                    self.eject_shell(w)
                else:
                    self.rocket_launch_fx()
            elif kind == "impact":
                self.burst(e[1], e[2])
            elif kind == "explosion":
                if len(e) > 3 and e[3] == self.my_id:
                    self.noise_wave(e[1][0], e[1][1], NOISE_EXPLOSION)
                self.explosion_fx(e[1], e[2])
                self.sfx.explosion(e[1], e[2])
                pl = self.player
                d = math.dist(e[1], (pl.x, pl.y, pl.z + 1.0))
                if d < 25:                  # Kamera wackelt bei Explosionen in der Nähe
                    self.sp_hurt.kick(self.prng.choice((-1, 1)) * (60 - d * 2))
            elif kind == "mob_hit":
                self.burst(e[1], "blood", e[2])
                if e[5] == self.my_id:      # Treffermarker nur für den eigenen Treffer
                    self.hit_t = 0.14
                    self.hitmark.setFg((1, 0.85, 0.2, 1) if e[4] else (1, 1, 1, 1))
                    self.damage_popup(e[6] if len(e) > 6 else 0, e[4])
            elif kind == "pl_hit":          # Spieler trifft Spieler
                self.burst(e[1], "blood", e[2])
                if e[5] == self.my_id:
                    self.hit_t = 0.14
                    self.hitmark.setFg((1, 0.85, 0.2, 1) if e[4] else (1, 1, 1, 1))
                    self.damage_popup(e[6] if len(e) > 6 else 0, e[4])
            elif kind == "mob_kill":
                self.burst(e[1], "kill")
                if e[2] == self.my_id:
                    self.hit_t = 0.3
                    self.hitmark.setFg((1, 0.15, 0.1, 1))
            elif kind == "reward":          # Munition für den Schützen des Todesschusses
                if e[1] == self.my_id:
                    for g, w in zip(self.player.guns, WEAPONS):
                        g.reserve = min(w.max_reserve, g.reserve + w.pickup)
            elif kind == "player_hurt":
                if e[2] == self.my_id:
                    self.hurt_flash = min(0.75, self.hurt_flash + 0.25 + e[1] * 0.012)
                    self.sp_hurt.kick(self.prng.choice((-1, 1)) * (25 + e[1] * 1.5))
            elif kind == "kill":            # (Killer oder -1 = Monster, Opfer, Waffe)
                victim = self.pname(e[2])
                wn = weapon_name(e[3])
                if e[1] < 0 and e[3] == WI_TURRET:
                    self.feed_add(f"{victim} wurde vom Geschütz erledigt")
                elif e[1] < 0 and e[3] == WI_TOMAHAWK:
                    self.feed_add(f"{victim} starb im Tomahawk-Angriff")
                elif e[1] < 0 and e[3] == WI_FALL:
                    self.feed_add(f"{victim} ist in den Tod gestürzt")
                elif e[1] < 0 and e[3] == WI_SLAM:
                    self.feed_add(f"{victim} wurde zerstampft")
                elif e[1] < 0 and e[3] == WI_ROCK:
                    self.feed_add(f"{victim} wurde vom Titan mit einem Felsbrocken erschlagen")
                elif e[1] < 0 and e[3] != -1:
                    self.feed_add(f"{victim} hat sich selbst erledigt  [{wn}]")
                elif e[1] < 0:
                    self.feed_add(f"{victim} wurde von einem Monster erledigt")
                else:
                    self.feed_add(f"{self.pname(e[1])}  [{wn}]  {victim}")
                if e[1] == self.my_id:
                    self.hit_t = 0.3
                    self.hitmark.setFg((1, 0.15, 0.1, 1))
            elif kind == "wreload":
                if e[1] == self.my_id:
                    self.sfx.reload(e[2])
            elif kind == "shotpos":         # fremder Schuss -> Punkt auf der Minimap
                if e[1] != self.my_id:
                    op = self.world.players.get(e[1])
                    if op is not None:
                        self.sfx.shot(op.cur, e[1])
                    self.pings[e[1]] = (time.time(), e[2], e[3])
            elif kind == "lootdbg":            # LOOT_DEBUG: Chancen nach dem Öffnen (nur für den Spieler selbst)
                if e[1] == self.my_id:
                    for ln in str(e[2]).split("\n"):
                        self.feed_add(ln)
            elif kind in ("loot", "pickup"):   # (Art, Spieler, Waffe, neue Slots, schon_vorhanden, Kistenart)
                wi, slots = e[2], e[3] if len(e) > 3 else None
                dup = len(e) > 4 and bool(e[4])
                if e[1] == self.my_id:
                    self.apply_gain(wi, slots, dup)
                wn = WEAPONS[wi].name if 0 <= wi < len(WEAPONS) else "?"
                if kind == "loot":
                    ck = e[5] if len(e) > 5 and isinstance(e[5], int) and 0 <= e[5] < len(CRATE_KINDS) else 0
                    what = CRATE_NAMES[CRATE_KINDS[ck]]
                    if e[1] == self.my_id:
                        self.toast(f"{CRATE_NAMES[CRATE_KINDS[ck]].capitalize()}: {wn}" + ("  (+Munition)" if dup else ""),
                                   (1, 1, 1), 1.8)
                elif e[1] == self.my_id and dup:
                    self.toast(f"{wn}: +Munition", (1, 1, 1), 1.5)
            elif kind == "venter":
                if e[1] == self.my_id:
                    v = self.world.vehicle_by_id(e[2])
                    if v is not None:
                        self.player.vehicle = v.id
                        self.player.heading = v.heading
                        self.player.pitch = -8.0
                        v.driver, v.speed = self.my_id, 0.0
            elif kind == "vexit":
                if e[1] == self.my_id:
                    pl = self.player
                    pl.vehicle = -1
                    pl.x, pl.y, pl.z, pl.vz = e[2], e[3], e[4], 0.0
                    pl.lean = pl.lean_x = pl.lean_y = 0.0
                    pl.duck, pl.crouch = False, 0.0
                    pl.pitch = 0.0
            elif kind == "tmount":
                if e[1] == self.my_id and 0 <= e[2] < len(self.world.turrets):
                    t = self.world.turrets[e[2]]
                    pl = self.player
                    pl.mount = t.id
                    pl.heading, pl.pitch = t.heading, clampf(t.pitch, t.pmin, t.pmax)
            elif kind == "tshot":
                self.sfx.turret(e[1])
                if self.player.mount == e[1]:
                    self.sp_cam.kick(0.9)
                    self.sp_hurt.kick(self.prng.choice((-1, 1)) * 4.0)
            elif kind == "henter":
                if e[1] == self.my_id:
                    q = self.world.heli_by_id(e[2])
                    if q is not None:
                        pl = self.player
                        pl.heli, pl.heading, pl.pitch = q.id, q.heading, 0.0
                        q.driver, q.speed = self.my_id, 0.0
            elif kind == "hrk":
                self.sfx.heli_rocket(e[1])
                if e[1] == self.my_id:
                    self.sp_cam.kick(8.0)
                    self.sp_back.kick(2.0)
            elif kind in ("hboom", "hreset"):
                pass
            elif kind == "reload":
                pass
            elif kind == "strikeready":
                self.toast("Tomahawk ist wieder verfügbar - irgendwo fährt eine Säule hoch", (1, 0.45, 0.35), 3.5)
            elif kind == "timer":
                pass
            elif kind == "respawn":
                if e[1] == self.my_id:
                    self.apply_respawn(e[2], e[3])
            elif kind == "strike":
                self.feed_add(f"{self.pname(e[1])} hat den TOMAHAWK-ANGRIFF gestartet - Rakete im Anflug!")
            elif kind == "tomahawk":
                tx, ty = (e[1], e[2]) if len(e) >= 3 else (CENTER, CENTER)
                if self.world.strike_by == self.my_id:
                    self.noise_wave(tx, ty, NOISE_TOMAHAWK)
                self.sfx.play("explosion", (tx, ty, 20.0), 1.0, 0.6)
                pl = self.player
                d = math.dist((tx, ty), (pl.x, pl.y))
                if d < 120:                 # gewaltiges Beben
                    self.sp_hurt.kick(self.prng.choice((-1, 1)) * (160 - d))
                    self.sp_cam.kick(10)
                    self.hurt_flash = min(0.75, self.hurt_flash + 0.4)
            elif kind == "zap":                # Drohne schiesst: Blitz von der Drohne zum Ziel
                self.zap_fx(e[1], e[2], bool(e[3]))
            elif kind == "stun":
                if e[1] == self.my_id:
                    pl = self.player
                    pl.stun_t = max(pl.stun_t, float(e[2]))
                    pl.ads = False
                    self.toast(f"BETÄUBT  {float(e[2]):.1f} s", (0.5, 0.75, 1.0), 1.5)
            elif kind == "stall":              # Drohne hat ein Fahrzeug lahmgelegt
                mine = (self.world.own_vehicle_id(self.my_id) == e[2] if e[1] == "car"
                        else self.my_heli() is not None and self.my_heli().id == e[2])
                if mine:
                    what = "Motor" if e[1] == "car" else "Antrieb"
                    self.toast(f"Drohne: {what} ausgefallen!  {float(e[3]):.1f} s", (0.5, 0.75, 1.0), 2.0)
            elif kind == "hcrash":
                if self.my_heli() is not None and self.my_heli().id == e[1]:
                    self.toast(f"Harte Landung! ({e[2]} m/s)", (1, 0.6, 0.4), 2.0)
                    self.hurt_flash = max(self.hurt_flash, 0.5)
            elif kind == "slam":               # Koloss-Bodenschlag: Staubwelle, Beben, dumpfer Knall
                self.slam_fx(e[1], e[2])
            elif kind == "rockkick":           # Titan reisst einen Brocken aus dem Boden
                x, y, z = e[1]
                for _ in range(16):
                    self.add_particle((x, y, z + 0.3), (self.prng.uniform(-3, 3), self.prng.uniform(-3, 3),
                                                        self.prng.uniform(3, 8)), (0.42, 0.36, 0.28), 0.14, 1.2, 0.3)
                for _ in range(4):
                    self.smoke_puff((x + self.prng.uniform(-1, 1), y + self.prng.uniform(-1, 1), z + 0.4), 0.9, 1.6, 0.5)
                self.sfx.play("rip", (x, y, z), MOB_VOL["titan_rip"], self.prng.uniform(0.85, 1.0))
            elif kind == "rockhit":            # Brocken schlägt ein: Staubwelle, Splitter, Beben
                self.slam_fx(e[1], e[2] * 0.7)
                for _ in range(14):
                    self.add_particle(e[1], (self.prng.uniform(-6, 6), self.prng.uniform(-6, 6), self.prng.uniform(2, 7)),
                                      (0.45, 0.42, 0.38), 0.12, 1.2, 0.3)
            elif kind == "titanloot":          # Titan erlegt: goldene Kiste mit Lichtsäule
                self.feed_add("Der Titan ist gefallen!")
                self.toast("TITAN BESIEGT - eine goldene Kiste liegt an seiner Stelle", (1.0, 0.82, 0.25), 3.5)
            elif kind == "buff":
                if e[1] == self.my_id:
                    pl = self.player
                    pl.buff, pl.buff_t = e[2], float(e[3])
                    if len(e) > 4:
                        pl.max_hp = float(e[4])
                    self.toast(f"Buff: {buff_text(e[2], pl.max_hp)}  -  {int(e[3])} s",
                               self.BUFF_LOOK.get(e[2], ("", (1, 0.85, 0.3)))[1])
                    self.sfx.ui_click()
            elif kind in ("gear", "gearbreak"):    # Ausrüstung angelegt / Helm bzw. Platte hat gerettet
                gi = e[2] if 0 <= e[2] < len(GEAR) else None
                if e[1] == self.my_id:
                    pl = self.player
                    gl = e[3] if len(e) > 3 and isinstance(e[3], list) else gear_list(pl)
                    pl.gear = {sl: (v if isinstance(v, int) and 0 <= v < len(GEAR) else None)
                               for sl, v in zip(GEAR_SLOTS, gl)}
                    if kind == "gearbreak":
                        self.toast(f"{'Helm' if GEAR[gi].slot == 'head' else 'Rüstung'} zerstört - hat dich gerettet!",
                                   (1, 0.55, 0.4), 2.5)
                        self.hurt_flash = 0.75
                        self.sp_hurt.kick(80)
                        self.sfx.play("railgun", None, 0.8, 1.6)
                if kind == "gear" and gi is not None and e[1] == self.my_id:
                    self.toast(f"Angelegt: {GEAR[gi].name}", tuple(c * 0.6 + 0.4 for c in GEAR[gi].col), 1.8)
            elif kind == "mswing":             # fremder Nahkampf-Schlag: Ton + Animation
                if e[1] != self.my_id:
                    op = self.world.players.get(e[1])
                    if op is not None:
                        self.sfx.play("swoosh", (op.x, op.y, op.z + 1.2), 0.6, self.prng.uniform(0.9, 1.1))
                    v = self.player_views.get(e[1])
                    if v is not None:
                        v.swing_t = 0.35
            elif kind == "mhit":               # Nahkampf-Treffer: Ton (Pfanne: BONG) + Spritzer
                pos = tuple(e[1])
                self.sfx.play(e[2] if e[2] in ("slash", "bong") else "slash", pos, 1.0, self.prng.uniform(0.92, 1.08))
                self.burst(pos, "blood")
                if len(e) > 3 and e[3] == self.my_id:
                    self.sp_cam.kick(1.5)
            elif kind == "melee":              # neue Nahkampfwaffe aus Kiste / vom Boden
                if e[1] == self.my_id and 0 <= e[2] < len(MELEE):
                    self.player.melee = e[2]
                    self.toast(f"Nahkampf: {MELEE[e[2]].name}", (1.0, 0.85, 0.5), 1.8)
            elif kind == "hasmelee":
                if e[1] == self.my_id:
                    self.toast("Hast du schon", (0.9, 0.9, 0.95), 1.5)
            elif kind == "hasgear":
                if e[1] == self.my_id:
                    self.toast("Hast du schon", (0.9, 0.9, 0.95), 1.5)
            elif kind == "shieldhit":
                if e[1] == self.my_id:
                    self.hurt_flash = max(0.0, self.hurt_flash - 0.2)
                    self.shield_flash = 0.4
            elif kind == "buffend":
                if e[1] == self.my_id:
                    self.toast("Buff abgelaufen", (0.85, 0.85, 0.9), 1.5)
            elif kind == "stats":              # Rundenende: Statistik vom Host -> Endbildschirm
                self.open_end_screen(e[1])
            elif kind == "newmatch":
                self.feed.clear()
                self.close_end_screen()
                self.pings.clear()
        self.world.events.clear()

    def reload_pose(self, u, magp, mag, ej):
        """Handposition (im Waffenraum) und Magazinteile für den Nachladefortschritt u = 0..1."""
        def lp(a, b, k):
            return (a[0] + (b[0] - a[0]) * k, a[1] + (b[1] - a[1]) * k, a[2] + (b[2] - a[2]) * k)
        rest = (-0.30, 0.10, -0.40)
        if magp is None:                                   # Raketenwerfer: Hand schiebt die Rakete hinein
            slide = smoothstep(0.35, 0.85, u)
            tgt = (0.0, 0.5 + 1.1 * (1 - slide), -0.07 + 0.25 * (1 - slide))
            if u < 0.35:
                return lp(rest, (0.0, 1.6, 0.18), smoothstep(0.0, 0.3, u))
            if u > 0.9:
                return lp(tgt, rest, smoothstep(0.9, 1.0, u))
            return tgt
        sx, sy, sz = magp[0], magp[1], magp[2]
        slot = (sx, sy, sz - 0.02)
        pulled = (sx - 0.03, sy, sz - 0.12)
        fetch = (-0.14, sy, sz - 0.15)
        up = (0.0, 0.0, 0.02)
        if u < 0.18:
            pos = lp(rest, slot, smoothstep(0.0, 0.18, u))
        elif u < 0.38:
            pos = lp(slot, pulled, smoothstep(0.18, 0.38, u))
        elif u < 0.58:
            pos = lp(pulled, fetch, smoothstep(0.38, 0.58, u))
        elif u < 0.66:
            pos = fetch
        elif u < 0.88:
            pos = lp(fetch, slot, smoothstep(0.66, 0.88, u))
        else:
            pos = lp(slot, rest, smoothstep(0.88, 1.0, u))
        # altes Magazin: in der Hand, dann im Bogen weggeworfen
        if mag is not None and 0.18 <= u < 0.66:
            mag.hide()
        if ej is not None and 0.18 <= u < 0.62:
            if u < 0.38:
                p0 = (pos[0], pos[1], pos[2] + up[2])
                ej.setR(0)
            else:
                t = (u - 0.38) / 0.24
                p0 = (pulled[0] - 0.12 * t, pulled[1] + 0.05 * t, pulled[2] + 0.02 - 1.1 * t * t)
                ej.setR(220 * t)
            ej.setPos(*p0)
            ej.show()
        # neues Magazin folgt der Hand, bis es sitzt
        if mag is not None and 0.58 <= u < 0.88:
            mag.setPos(pos[0], pos[1], pos[2] + up[2])
            mag.show()
        return pos

    # ------------------------------------------------------------ Darstellung
    def update_views(self, dt, mdx, mdy):
        pl, world = self.player, self.world
        w = WEAPONS[pl.cur]
        g = pl.guns[pl.cur]

        # Zoom
        target = (38.0 if pl.mount >= 0 else w.ads_fov) if pl.ads else FOV
        self.fov_cur += (target - self.fov_cur) * min(1.0, 14 * dt)
        self.camLens.setFov(self.fov_cur)
        self.gun_lens.setAspectRatio(self.getAspectRatio())
        self.ads_t += ((1.0 if pl.ads else 0.0) - self.ads_t) * min(1.0, 14 * dt)
        self.death_t = min(1.0, self.death_t + dt * 1.5) if pl.hp <= 0 else 0.0

        # Federn
        for s in (self.sp_back, self.sp_pitch, self.sp_roll, self.sp_cam, self.sp_hurt,
                  self.sw_h, self.sw_p):
            s.step(dt)
        self.sw_h.kick(mdx * 0.9)
        self.sw_p.kick(mdy * 0.9)
        self.sw_h.x = clampf(self.sw_h.x, -8, 8)
        self.sw_p.x = clampf(self.sw_p.x, -8, 8)

        # Waffenmodell
        a = self.ads_t
        self.bob_amp += ((1.0 if pl.moving and pl.on_ground else 0.0) - self.bob_amp) * min(1.0, 8 * dt)
        bob = self.bob_amp * (1 - 0.7 * a)
        px = 0.16 * (1 - a) + 0.0 * a + math.sin(pl.phase) * 0.012 * bob
        py = 0.55 * (1 - a) + 0.50 * a - self.sp_back.x
        pz = -0.16 * (1 - a) - ADS_Z.get(w.name, ADS_Z_DEFAULT) * a + abs(math.cos(pl.phase)) * 0.014 * bob
        pitch = self.sp_pitch.x + self.sw_p.x
        roll = self.sp_roll.x + pl.lean / LEAN_MAX * LEAN_ROLL
        px += pl.lean / LEAN_MAX * 0.03
        driving = pl.vehicle >= 0 or pl.heli >= 0 or pl.mount >= 0
        # Raketenwerfer: die Rakete steckt im Rohr; nach dem Schuss fehlt sie, beim Nachladen wird
        # sie von vorn ins Rohr geschoben
        if pl.cur == ROCKET_WI:
            if pl.reload_t > 0:
                u = 1.0 - pl.reload_t / w.reload
                slide = smoothstep(0.35, 0.85, u)
                self.vm_rocket.setPos(0, 0.5 + 1.1 * (1 - slide), 0.02 + 0.25 * (1 - slide))
                (self.vm_rocket.show if u > 0.3 else self.vm_rocket.hide)()
            elif g.mag > 0:
                self.vm_rocket.setPos(0, 0.5, 0.02)
                self.vm_rocket.show()
            else:
                self.vm_rocket.hide()
        # Rennhaltung: Pistolen mit hochgehaltenem Lauf, grosse Waffen quer vor dem Körper
        self.sprinting = bool(self.run_now and pl.moving and pl.on_ground and pl.crouch < 0.3
                              and not driving and pl.hp > 0)
        want = 1.0 if (self.sprinting and not pl.ads and pl.reload_t <= 0 and pl.switch_t <= 0
                       and not self.trig_now) else 0.0
        self.spr_t += (want - self.spr_t) * min(1.0, 9 * dt)
        e = self.spr_t
        hdg_add = 0.0
        if e > 0.001:
            sd = SPRINT_POSE.get(w.name, SPRINT_POSE_DEFAULT)
            sw_ = math.sin(pl.phase)
            px += (sd[0] + sw_ * 0.035) * e
            py += sd[1] * e
            pz += (sd[2] + abs(math.cos(pl.phase)) * 0.03) * e
            hdg_add = (sd[3] + sw_ * 2.5) * e
            pitch += sd[4] * e
            roll += (sd[5] + sw_ * 3.0) * e
        # Nachladen: linke Hand zieht das Magazin heraus, wirft es weg, holt ein neues und schiebt es hinein
        self.hand_pos = None
        mag_n, ej_n, magp = self.vm_mags[pl.cur]
        if mag_n is not None:
            mag_n.setPos(magp[0], magp[1], magp[2])
            mag_n.show()
        for _m, e_, _p in self.vm_mags:
            if e_ is not None:
                e_.hide()
        if pl.reload_t > 0:
            u = 1.0 - pl.reload_t / w.reload
            dip = smoothstep(0.0, 0.15, u) * (1.0 - smoothstep(0.85, 1.0, u))
            pz += 0.16 * dip                    # Waffe wird angehoben und nach oben geneigt, damit man
            py += 0.08 * dip                    # die Hand am Magazin sieht
            pitch += 20 * dip
            roll += 10 * dip
            if magp is not None and 0.88 <= u < 0.95:           # Magazin einrasten: kleiner Ruck
                pitch -= 5.0 * math.sin(math.pi * (u - 0.88) / 0.07)
            self.hand_pos = self.reload_pose(u, magp, mag_n, ej_n)
        if pl.switch_t > 0:                       # Wechsel: Waffe senken, tauschen, heben
            dip = math.sin(math.pi * (1 - pl.switch_t / SWITCH_T))
            pz -= 0.45 * dip
            pitch -= 50 * dip
        if pl.melee_out and pl.swing_t > 0:       # Nahkampf: ausholen (rechts oben), Hieb nach links unten
            mw = MELEE[pl.melee] if 0 <= pl.melee < len(MELEE) else MELEE[START_MELEE]
            u = 1.0 - pl.swing_t / max(mw.interval, 0.05)
            if u < 0.22:
                k = u / 0.22
                hdg_add -= 30 * k
                pitch += 22 * k
                px += 0.06 * k
                pz += 0.05 * k
            elif u < 0.5:
                k = (u - 0.22) / 0.28
                hdg_add += -30 + 100 * k
                pitch += 22 - 50 * k
                roll += 35 * k
                px += 0.06 - 0.2 * k
                pz += 0.05 - 0.1 * k
            else:
                k = 1.0 - (u - 0.5) / 0.5
                hdg_add += 70 * k
                pitch -= 28 * k
                roll += 35 * k
                px -= 0.14 * k
                pz -= 0.05 * k
        self.gun_pivot.setPos(px, py, pz)
        self.gun_pivot.setHpr(self.sw_h.x + hdg_add, pitch, roll)
        scoped = w.scope and self.ads_t > 0.85
        rsc = w.sight == "rocket" and self.ads_t > 0.6 and pl.hp > 0 and not driving
        hidden = scoped or rsc
        for i, m in enumerate(self.gun_models):
            (m.show if i == pl.cur and not pl.melee_out and not hidden and pl.hp > 0 and not driving else m.hide)()
        for i, m in enumerate(self.melee_models):
            (m.show if pl.melee_out and i == pl.melee and pl.hp > 0 and not driving else m.hide)()
        if self.hand_pos is not None and not hidden and pl.hp > 0 and not driving:
            self.vm_hand.setPos(*self.hand_pos)
            self.vm_hand.show()
        else:
            self.vm_hand.hide()
            if ej_n is not None:
                ej_n.hide()
        self.flash_t = max(0.0, self.flash_t - dt)
        self.sfx.update(dt)
        for i, f in enumerate(self.gun_flash):
            (f.show if self.flash_t > 0 and i == pl.cur and not hidden and not driving else f.hide)()
        (self.scope.show if scoped and pl.hp > 0 and not driving else self.scope.hide)()
        if rsc:
            self.rscope.show()
            self.update_rocket_sight()
        else:
            self.rscope.hide()
        tur_now = self.my_turret() if pl.hp > 0 else None
        if tur_now is not None:
            self.tsight.show()
            self.update_turret_sight(tur_now)
        else:
            self.tsight.hide()

        # Kugeln als Leuchtspur; Raketen mit Flamme und Rauchspur
        current = set(world.bullets)
        for b in world.bullets:
            np = self.bullet_nodes.get(b)
            if np is None:
                if self.is_rocket(b):      # Rakete: eigener Halter mit Rakete und Flamme als Kindern
                    np = self.render.attachNewNode("rocket")
                    self.rocket_np.instanceTo(np)
                    fl = self.flame_np.instanceTo(np)
                    fl.setTwoSided(True)
                    self.flames[b] = fl
                else:
                    np = self.tracer_np.instanceTo(self.render)
                    if b.blast_r > 0:      # Flak-Granate: dicker Leuchtstrich
                        np.setScale(2.6, 1.8, 2.6)
                np.setFogOff()
                self.bullet_nodes[b] = np
            np.setPos(b.x, b.y, b.z)
            np.lookAt(b.x + b.vx, b.y + b.vy, b.z + b.vz)
            rk = self.is_rocket(b)
            shown = b.travel > (1.0 if rk else 5.0)
            (np.show if shown else np.hide)()
            if rk and shown:
                fl = self.flames.get(b)
                if fl is not None:
                    fl.setScale(self.prng.uniform(0.8, 1.2), self.prng.uniform(0.7, 1.5), self.prng.uniform(0.8, 1.2))
                sp = math.sqrt(b.vx ** 2 + b.vy ** 2 + b.vz ** 2) or 1.0
                self.trail_t[b] = self.trail_t.get(b, 0.0) - dt
                if self.trail_t[b] <= 0:                  # Rauchspur hinter der Rakete
                    self.trail_t[b] = 0.025
                    self.smoke_puff((b.x - b.vx / sp * 0.8, b.y - b.vy / sp * 0.8, b.z - b.vz / sp * 0.8),
                                    0.22, 1.5, 0.75)
        self.bullet_whiz(world.bullets)
        for b in [b for b in self.bullet_nodes if b not in current]:
            self.bullet_nodes.pop(b).removeNode()
            self.trail_t.pop(b, None)
            self.flames.pop(b, None)

        # Granaten, Waffen am Boden, Fahrzeuge, Effekte
        self.update_objects(dt)

        # Mobs
        current = set(world.mobs)
        for m in world.mobs:
            v = self.mob_views.get(m)
            if v is None:
                v = self.mob_views[m] = MobView(m, getattr(world, "mtn", True))
                v.root.reparentTo(self.render)
            v.update(m)
        for m in [m for m in self.mob_views if m not in current]:
            self.mob_views.pop(m).root.removeNode()

        # Mitspieler
        others = {pid for pid in world.players if pid != self.my_id}
        for pid in others:
            p = world.players[pid]
            v = self.player_views.get(pid)
            if v is None:
                v = self.player_views[pid] = PlayerView(p)
                v.root.reparentTo(self.render)
            v.update(p, dt)
        for pid in [pid for pid in self.player_views if pid not in others]:
            self.player_views.pop(pid).root.removeNode()

        # Partikel (Hülsen, Splitter, Blut): Wurfparabel + Abprallen am Gelände
        keep = []
        for p in self.parts:
            p.age += dt
            if p.age >= p.life:
                p.np.removeNode()
                continue
            p.vz -= 9.81 * dt
            p.x += p.vx * dt
            p.y += p.vy * dt
            p.z += p.vz * dt
            gz = world.ground_for(p.x, p.y, p.z + 0.3)
            if p.z < gz + 0.01:
                p.z = gz + 0.01
                if p.bounce > 0 and p.vz < -0.6:
                    p.vz = -p.vz * p.bounce
                    p.vx *= 0.6
                    p.vy *= 0.6
                else:
                    p.vz = 0.0
                    fr = math.exp(-8 * dt)
                    p.vx *= fr
                    p.vy *= fr
                    p.spin = 0.0
            p.np.setPos(p.x, p.y, p.z)
            if p.spin:
                p.np.setH(p.np.getH() + 700 * dt)
                p.np.setP(p.np.getP() + 500 * dt)
            if p.shrink and p.life - p.age < 0.25:
                s = (p.life - p.age) / 0.25
                p.np.setScale(p.scale * max(s, 0.01))
            keep.append(p)
        self.parts = keep

        self.update_crates()
        self.update_toma(dt)
        if NOISE_DEBUG:
            self.update_noise_debug()
        self.update_gfx(dt)
        self.update_hud(dt)
        self.place_camera()

    def update_rocks_view(self, dt):
        """Steinbrocken des Titans: Felsmodell, dreht sich im Flug; zwischen den Snapshots weiter geflogen."""
        views = getattr(self, "rock_views", None)
        if views is None:
            views = self.rock_views = {}
            m = Mesh()
            blob(m, 0, 0, 0, ROCK_SIZE * 0.5, ROCK_SIZE * 0.45, ROCK_SIZE * 0.42, (0.42, 0.39, 0.35), random.Random(9),
                 jitter=0.18)
            box(m, 0.1, 0.0, -ROCK_SIZE * 0.35, ROCK_SIZE * 0.5, ROCK_SIZE * 0.4, 0.2, (0.33, 0.27, 0.2))   # Erde dran
            self.rock_np = NodePath(m.node("rock"))
        live = {}
        for r in self.world.rocks:
            nd = views.get(r.rid)
            if nd is None:
                nd = self.rock_np.copyTo(self.render)
                nd.setPos(r.x, r.y, r.z)
            live[r.rid] = nd
            if self.net_mode == "client":               # zwischen den Snapshots selbst weiterfliegen
                r.vz -= ROCK_GRAV * dt
                r.x += r.vx * dt
                r.y += r.vy * dt
                r.z += r.vz * dt
            nd.setPos(r.x, r.y, r.z)
            nd.setHpr(nd.getH() + 200 * dt, nd.getP() + 340 * dt, 0)
        for rid, nd in views.items():
            if rid not in live:
                nd.removeNode()
        self.rock_views = live

    def update_objects(self, dt):
        """Granaten, am Boden liegende Waffen, Fahrzeuge und Effekte darstellen."""
        world, now = self.world, time.time()
        self.update_rocks_view(dt)
        cur = set(world.grenades)
        for g in world.grenades:
            np = self.gren_views.get(g)
            if np is None:
                np = self.gren_views[g] = self.gren_np.instanceTo(self.render)
            np.setPos(g.x, g.y, g.z)
            np.setHpr(now * 420.0 + g.gid * 40, now * 300.0, 0)
            if g.fuse < 1.0 and int(now * 10) % 2 == 0:       # kurz vor der Explosion blinkt sie rot
                np.setColorScale(2.2, 0.5, 0.4, 1)
            else:
                np.clearColorScale()
        for g in [g for g in self.gren_views if g not in cur]:
            self.gren_views.pop(g).removeNode()

        cur = set(world.drops)
        for d in world.drops:
            v = self.drop_views.get(d)
            if v is None:
                v = self.drop_views[d] = self.render.attachNewNode(f"drop{d.did}")
                if d.melee >= 0:
                    mdl = self.melee_drop_models[d.melee].copyTo(v)
                else:
                    mdl = (self.gear_models[d.gear] if d.gear >= 0 else self.drop_models[d.wi]).copyTo(v)
                    mdl.setScale(1.4 if d.gear < 0 else 1.0)
                beam = Mesh(lit=False)
                box(beam, 0, 0, 0.9, 0.05, 0.05, 1.8, (1.0, 0.9, 0.3))
                bn = v.attachNewNode(beam.node("beam"))
                bn.setTransparency(TransparencyAttrib.MAlpha)
                bn.setColorScale(1, 1, 1, 0.45)
                bn.setFogOff()
                v.setPythonTag("model", mdl)
                v.setPythonTag("beam", bn)
            v.setPos(d.x, d.y, d.z)
            mdl = v.getPythonTag("model")
            mdl.setPos(0, 0, 0.6 + 0.1 * math.sin(now * 2.2 + d.did))
            mdl.setH(now * 80.0)
            if d.life < 8.0:                                   # läuft gleich ab: blinkt
                (mdl.show if int(now * 6) % 2 == 0 else mdl.hide)()
            else:
                mdl.show()
        for d in [d for d in self.drop_views if d not in cur]:
            self.drop_views.pop(d).removeNode()

        for v in world.vehicles:
            vv = self.veh_views.get(v)
            if vv is None:
                vv = self.veh_views[v] = VehicleView(v)
                vv.root.reparentTo(self.render)
            vv.update(v, dt, world, self)
            if v.hp > 0 and v.stall_t > 0:     # von der Drohne lahmgelegt: blaues Flackern
                self.stall_flicker(vv.root, (v.x, v.y, v.z + 1.0))
        for q in world.helis:
            pv = self.heli_views.get(q)
            if pv is None:
                pv = self.heli_views[q] = HeliView(q)
                pv.root.reparentTo(self.render)
            pv.update(q, dt, world, self, q is self.my_heli())
            if q.hp > 0 and q.stall_t > 0:
                self.stall_flicker(pv.root, (q.x, q.y, q.z + 1.5))
        for t in world.turrets:
            tv = self.tur_views.get(t)
            if tv is None:
                tv = self.tur_views[t] = TurretView(t)
                tv.root.reparentTo(self.render)
            tv.update(t, dt, self)
        self.update_fx(dt)

    def rank_line(self, i, p):
        mark = ">" if p.pid == self.my_id else " "
        if self.world.mode == "koth":
            return f"{mark}{i + 1}. {p.name[:12]}   {int(p.score)} P   {p.kills}/{p.deaths}"
        return f"{mark}{i + 1}. {p.name[:12]}   K/D {p.kills / max(1, p.deaths):.2f}   ({p.kills}/{p.deaths})"

    def set_slot_icon(self, i, wi):
        """Zeigt in Karte i das Bild der Waffe wi (None = leer). Jede Karte besitzt eigene,
        unabhängige Bildknoten, gezeigt wird durch Ein-/Aushängen statt hide()/show()."""
        d = self.slot_icons[i]
        if d["cur"] == wi:
            return
        if d["cur"] is not None:
            d["nodes"][d["cur"]].detachNode()
        d["cur"] = wi
        if wi is None:
            return
        nd = d["nodes"].get(wi)
        if nd is None:
            nd = weapon_icon(wi)                      # frisch erzeugt, mit niemandem geteilt
            nd.setBin("fixed", 21)
            nd.setDepthTest(False)
            nd.setDepthWrite(False)
            d["nodes"][wi] = nd
        nd.reparentTo(d["holder"])

    def update_hud(self, dt):
        pl, world = self.player, self.world
        w = WEAPONS[pl.cur]
        g = pl.guns[pl.cur]
        now = time.time()
        mx = getattr(pl, "max_hp", PLAYER_HP)
        ratio = max(0.0, min(1.0, pl.hp / mx))
        self.hp_fg.setSx(max(0.55 * ratio, 0.0001))
        if mx > PLAYER_HP:                                 # Tank-Buff: goldener Balken, "180 / 200"
            self.hp_fg.setColor(0.95, 0.8, 0.25, 1)
            self.set_text(self.hp_text, f"{int(math.ceil(pl.hp))} / {int(mx)}")
        else:
            self.hp_fg.setColor(*((0.2, 0.8, 0.2, 1) if ratio > 0.5 else
                                  (0.95, 0.75, 0.1, 1) if ratio > 0.25 else (0.9, 0.15, 0.1, 1)))
            self.set_text(self.hp_text, f"{int(math.ceil(pl.hp))}")
        self.update_ability_icons()
        if getattr(self, "toast_later", None):             # Hinweis vom Spielstart (nach dem Aufbau zeigen)
            self.toast(*self.toast_later)
            self.toast_later = None
        (self.toast_text.hide if self.tab_held else self.toast_text.show)()
        if self.toast_t > 0:                               # Hinweis in der Bildmitte: am Ende ausblenden
            self.toast_t = max(0.0, self.toast_t - dt)
            self.toast_text.setAlphaScale(min(1.0, self.toast_t / 0.6))
            if self.toast_t <= 0:
                self.toast_text.setText("")
        tur, hc = self.my_turret(), self.my_heli()
        if pl.hp <= 0:
            tur = hc = None
        if hc is not None:
            self.set_text(self.ammo_text, f"MG {int(hc.mg)}   Raketen {hc.rk}")
            self.set_text(self.name_text, "Helikopter")
        elif tur is not None:
            self.set_text(self.ammo_text, "")                      # Hitze zeigt nur der Balken im Visier
            self.set_text(self.name_text, TURRET_NAMES.get(tur.kind, "Geschütz"))
        elif pl.melee_out and not (pl.switch_t > 0 and pl.switch_to != MELEE_SEL):
            self.set_text(self.ammo_text, "")
            self.set_text(self.name_text, MELEE[pl.melee].name)
        else:
            self.set_text(self.ammo_text, f"{g.mag} / {g.reserve}")
            self.set_text(self.name_text, w.name)
        want = pl.switch_to if pl.switch_t > 0 else (MELEE_SEL if pl.melee_out else pl.cur)
        if self.melee_icon_cur != pl.melee:                 # Nahkampf-Karte: Bild der getragenen Waffe
            for nd in self.melee_icons.values():
                nd.detachNode()
            nd = self.melee_icons.get(pl.melee)
            if nd is None:
                nd = self.melee_icons[pl.melee] = melee_icon(pl.melee)
                nd.setBin("fixed", 21)
                nd.setDepthTest(False)
                nd.setDepthWrite(False)
            nd.reparentTo(self.melee_holder)
            self.melee_icon_cur = pl.melee
        mact = want == MELEE_SEL and pl.vehicle < 0 and pl.mount < 0 and pl.heli < 0
        self.melee_frame.setColor(*((1.0, 0.85, 0.2, 1.0) if mact else (0.4, 0.4, 0.4, 0.6)))
        self.melee_label.setFg((1, 0.9, 0.3, 1) if mact else (1, 1, 1, 0.8))
        for i in range(N_SLOTS):                     # Waffenleiste mit Bildern (letzter Slot: Spezialwaffe)
            wi = pl.slots[i]
            self.set_slot_icon(i, wi)
            active = wi is not None and wi == want and pl.vehicle < 0 and pl.mount < 0 and pl.heli < 0
            self.slot_frames[i].setColor(*((1.0, 0.85, 0.2, 1.0) if active else (0.4, 0.4, 0.4, 0.6)))
            self.slot_labels[i].setFg((1, 0.9, 0.3, 1) if active else (1, 1, 1, 0.8))
        self.set_text(self.gren_text, f"x{pl.grenades}")
        self.gren_frame.setColor(*((0.4, 0.4, 0.4, 0.6) if pl.grenades > 0 else (0.7, 0.15, 0.1, 0.6)))
        veh = self.my_vehicle() if pl.hp > 0 else None
        txt = ""
        if hc is not None:
            alt = max(0.0, hc.z - world.ground_for(hc.x, hc.y, hc.z))
            txt = (f"{int(hc.speed * 3.6)} km/h    Höhe {int(alt)} m    Helikopter {int(max(0, hc.hp))}/{int(HELI_HP)}")
            if hc.ground and world.on_pad(hc.x, hc.y) and (hc.rk < HELI_RK_MAX or hc.mg < HELI_MG_MAX - 1):
                txt += "\nMunition wird aufgeladen ..."
            elif hc.ground and not world.on_pad(hc.x, hc.y) and (hc.rk < HELI_RK_MAX or hc.mg < HELI_MG_MAX * 0.5):
                txt += "\nMunition nachladen: auf dem Helipad landen"
        elif veh is not None:
            txt = f"{int(abs(veh.speed) * 3.6)} km/h    Wagen {int(max(0, veh.hp))}/{int(VEH_HP)}"
        self.set_text(self.speed_text, txt)
        (self.reload_text.show if pl.reload_t > 0 else self.reload_text.hide)()
        if self.tab_held:
            self.update_tab_overlay()
        if self.show_fps:
            try:
                self.set_text(self.fps_text, f"{int(globalClock.getAverageFrameRate())} FPS")  # noqa: F821
            except NameError:
                pass
        self.hit_t = max(0.0, self.hit_t - dt)
        (self.hitmark.show if self.hit_t > 0 else self.hitmark.hide)()
        self.hitmark.pop(self.hit_t / 0.3)
        self.update_popup(dt)
        scoped = w.scope and self.ads_t > 0.85
        scoped = scoped and pl.vehicle < 0 and pl.mount < 0 and pl.heli < 0
        rocket_view = w.sight == "rocket" and self.ads_t > 0.6 and pl.vehicle < 0 and pl.mount < 0 and pl.heli < 0
        (self.cross.hide if scoped or rocket_view or pl.hp <= 0 or pl.mount >= 0 or self.sprinting or pl.ads else self.cross.show)()
        spin = min(1.0, (abs(self.sw_h.x) + abs(self.sw_p.x)) / 5.0 + (0.6 if self.key_turn else 0.0))
        mv = 1.0 if pl.moving and pl.on_ground else 0.0
        self.cross.update(dt, walk=mv, run=mv if self.run_now and pl.crouch < 0.5 else 0.0, turn=spin,
                          air=0.0 if pl.on_ground else 1.0, bloom=min(2.0, pl.bloom), crouch=pl.crouch)
        self.hurt_flash = max(0.0, self.hurt_flash - 1.5 * dt)
        low = 0.35 * max(0.0, 1 - pl.hp / 40.0) if pl.hp > 0 else 0.5
        if getattr(pl, "stun_t", 0.0) > 0 and pl.hp > 0:    # betäubt: blaues Flackern über dem Bild
            f = 0.5 + 0.5 * math.sin(time.time() * 35.0)
            self.hurt_card.setColor(0.25, 0.55, 1.0, 0.18 + 0.22 * f)
            if self.prng.random() < 0.3:
                h = math.radians(pl.heading)
                self.add_particle((pl.x - math.sin(h) * 0.6, pl.y + math.cos(h) * 0.6, pl.z + 1.4),
                                  (self.prng.uniform(-2, 2), self.prng.uniform(-2, 2), self.prng.uniform(0, 3)),
                                  (0.6, 0.9, 1.0), 0.015, 0.25, 0.0)
        elif getattr(self, "shield_flash", 0.0) > 0:      # Schild hat abgefangen: kurz blau
            self.shield_flash = max(0.0, self.shield_flash - dt)
            self.hurt_card.setColor(0.3, 0.6, 1.0, self.shield_flash * 0.5)
        else:
            self.hurt_card.setColor(0.8, 0, 0, min(0.8, self.hurt_flash + low))

        # Zeit, Modus, Rangliste
        t = max(0.0, world.time_left)
        zone = ""
        if world.mode == "koth" and pl.hp > 0 and world.in_zone(pl):
            zone = "   IN DER BURG  +1/s"
        self.set_text(self.timer_text, f"{MODE_NAMES[world.mode]}   {int(t) // 60:02d}:{int(t) % 60:02d}{zone}")
        # Killfeed (oben links)
        self.feed = [f for f in self.feed if now - f[1] < FEED_T][-FEED_N:]
        self.set_text(self.feed_text, "\n".join(f[0] for f in self.feed))

        # Hinweis: Spawnschutz oder etwas in Reichweite, das F benutzen kann
        prompt = ""
        if pl.hp > 0 and world.phase == "play":
            if pl.protect > 0:
                prompt = "Spawnschutz"
            if world.in_tunnel(pl.x, pl.y) and pl.z < -1.0:
                prompt = "Tunnel"
            use = world.nearest_use(pl)
            if use is not None:
                kind, o = use
                if kind == "crate":
                    prompt = f"F   {CRATE_NAMES.get(o.kind, 'Kiste')[0].upper()}{CRATE_NAMES.get(o.kind, 'Kiste')[1:]} öffnen"
                elif kind == "drop":
                    if o.melee >= 0:
                        prompt = f"F   Aufheben: {MELEE[o.melee].name}"
                        if pl.melee == o.melee:
                            prompt += "   (Hast du schon)"
                        elif pl.melee != START_MELEE:
                            prompt += f"   (tauscht gegen {MELEE[pl.melee].name})"
                    elif o.gear >= 0:
                        g = GEAR[o.gear]
                        prompt = f"F   Aufheben: {g.name}"
                        cur = pl.gear.get(g.slot)
                        if cur == o.gear:
                            prompt += "   (Hast du schon)"
                        elif cur is not None:
                            prompt += f"   (tauscht gegen {GEAR[cur].name})"
                    elif o.wi in pl.slots:
                        prompt = f"F   Waffe aufheben: {WEAPONS[o.wi].name}"
                        prompt += "   (Munition)"
                    else:
                        prompt = f"F   Waffe aufheben: {WEAPONS[o.wi].name}"
                        out = pl.slots[target_slot(pl, o.wi)]
                        if out is not None:
                            prompt += f"   (tauscht gegen {WEAPONS[out].name})"
                elif kind == "vehicle":
                    ct = world.car_turret(o)
                    if o.driver < 0:
                        prompt = "F   Geländewagen fahren" + ("      V   als Schütze aufsteigen" if ct is not None and ct.op < 0 else "")
                    else:
                        prompt = "F   als Schütze aufsteigen"
                elif kind == "turret":
                    prompt = "F   Flak-Geschütz bedienen" if o.kind == "flak" else "F   Geschütz bedienen"
                elif kind == "heli":
                    prompt = "F   Helikopter fliegen"
                elif kind == "exit_heli":
                    prompt = ("F   aussteigen" if o.ground and o.speed < 4.0 else
                              "WASD fliegen   Leertaste hoch   Shift runter   Linke Maus Minigun   Rechte Maus Rakete")
                elif kind == "exit_turret":
                    prompt = "F   Geschütz verlassen      Linke Maus schiessen   Rechte Maus Zoom"
                elif kind == "button":
                    lock = world.toma_lock.get(self.my_id, 0.0)
                    if lock > 0:
                        prompt = f"Tomahawk: für dich noch {int(math.ceil(lock))} s gesperrt (du hast ihn zuletzt ausgelöst)"
                    elif not world.toma_ready():
                        prompt = "Tomahawk-Säule fährt hoch ..."
                    else:
                        prompt = "F   Tomahawk: Ziel und Countdown wählen"
                else:
                    prompt = "F   aussteigen"
        self.set_text(self.prompt_text, prompt)
        if world.strike == 1 and world.phase == "play":
            left = int(math.ceil(max(0.0, world.strike_t)))
            self.set_text(self.strike_text, f"ACHTUNG: TOMAHAWK-ANGRIFF IN {left} s")      # Ziel bleibt unbekannt
            self.strike_text.setFg((1, 1, 0.3, 1) if (left <= 5 and int(now * 4) % 2 == 0) else (1, 0.25, 0.15, 1))
        else:
            self.set_text(self.strike_text, "")

        # Todes-Bildschirm mit Waffenwahl (Bilder) / Rundenende mit Rangliste
        dead_screen = pl.hp <= 0 and world.phase == "play"
        self.set_text(self.dead_text, "DU BIST GESTORBEN\n\nDu startest wieder mit der Pistole."
                      if dead_screen else "")
        if dead_screen:
            if self.dead_since is None:
                self.dead_since = now
            wait = world.respawn_delay - (now - self.dead_since)
            hint = "R   Respawn" if wait <= 0 else f"Respawn in {int(math.ceil(wait))} s"
        else:
            self.dead_since = None
            hint = ""
        self.set_text(self.dead_hint, hint)
        self.set_text(self.over_text, "")             # (Banner ersetzt durch den Endbildschirm)
        self.update_end_screen()
        self.update_minimap()
        self.update_strike_map()
        if self.quit_box is not None and self.overlay_kind == "strike" and (world.strike != 0 or pl.hp <= 0):
            self.close_quit_box()                      # jemand war schneller / du bist tot

    # ------------------------------------------------------------ Minimap
    MM_S = 0.42           # Durchmesser der runden Minimap (Bildschirmeinheiten)
    MM_VIS = 50.0         # sichtbarer Radius in Metern
    MAP_MARGIN, MAP_PPM = 50.0, 3.0      # Rand um die Karte (m) und Auflösung der Kartentextur (Pixel/m)

    def build_map_texture(self):
        """Karte als Textur (Burg, Gebäude, Teiche, Tunneleingänge, Raster). Gemeinsam für die Minimap
        und die Tomahawk-Zielkarte. None, wenn Panda3D (Tests) fehlt."""
        if not REAL_PANDA:
            return None
        world, M, ppm = self.world, self.MAP_MARGIN, self.MAP_PPM
        size = int((WORLD + 2 * M) * ppm)
        img = PNMImage(size, size, 3)
        img.fill(0.07, 0.09, 0.12)

        def px(x):
            return int((x + M) * ppm)

        def py(y):
            return size - 1 - int((y + M) * ppm)

        def rect(x0, y0, x1, y1, col):
            xa, xb = max(0, px(x0)), min(size - 1, px(x1))
            ya, yb = max(0, py(y1)), min(size - 1, py(y0))
            for yy in range(ya, yb + 1):
                for xx in range(xa, xb + 1):
                    img.setXel(xx, yy, *col)

        def disc(cx, cy, r, col):
            for yy in range(max(0, py(cy + r)), min(size - 1, py(cy - r)) + 1):
                wy = (size - 1 - yy) / ppm - M
                dx2 = r * r - (wy - cy) ** 2
                if dx2 < 0:
                    continue
                dx = math.sqrt(dx2)
                for xx in range(max(0, px(cx - dx)), min(size - 1, px(cx + dx)) + 1):
                    img.setXel(xx, yy, *col)

        rect(0, 0, WORLD, WORLD, (0.20, 0.34, 0.17))
        if getattr(world, "mtn", False):                            # Gebirge: grob (2 m) berechnen, dann hochskalieren
            n = int((WORLD + 2 * M) / 2.0)
            sm = PNMImage(n, n, 3)
            for j in range(n):
                wy = (n - 1 - j + 0.5) * 2.0 - M
                for i in range(n):
                    wx = (i + 0.5) * 2.0 - M
                    inside = 0.0 <= wx <= WORLD and 0.0 <= wy <= WORLD
                    col = (0.20, 0.34, 0.17) if inside else (0.11, 0.15, 0.11)
                    hm = mountain(wx, wy)
                    if hm > 0.3:
                        k = min(1.0, hm / 8.0)
                        b = 0.30 + 0.38 * min(1.0, hm / 50.0)
                        rock = (b * 1.02, b * 0.98, b * 0.90) if inside else (b * 0.7, b * 0.68, b * 0.63)
                        col = tuple(cc + (rr - cc) * k for cc, rr in zip(col, rock))
                    sm.setXel(i, j, *col)
            img.quickFilterFrom(sm)
        if world.mc:                                                # Minecraft-Karte: Draufsicht aus der Kartendatei
            mm, n = world.mc["minimap"], world.mc["meta"]["mm"]
            for yy in range(size):
                j = int((size - 1 - yy) / ppm - M)
                if not 0 <= j < n:
                    continue
                row = (n - 1 - j) * n * 3
                for xx in range(size):
                    i = int(xx / ppm - M)
                    if 0 <= i < n:
                        k = row + i * 3
                        img.setXel(xx, yy, mm[k] / 255.0, mm[k + 1] / 255.0, mm[k + 2] / 255.0)
        grid = (0.24, 0.39, 0.21)
        for g in range(25, int(WORLD), 25):                         # Raster alle 25 m
            if not world.mc:
                rect(g - 0.15, 0, g + 0.15, WORLD, grid)
                rect(0, g - 0.15, WORLD, g + 0.15, grid)
        for ppx, ppy, r in world.ponds:
            disc(ppx, ppy, r * 1.3, (0.20, 0.42, 0.70))
        if world.mode == "koth":
            disc(CENTER, CENTER, ZONE_R, (0.62, 0.55, 0.15))
            disc(CENTER, CENTER, ZONE_R - 0.6, (0.28, 0.36, 0.16))
        if world.runway is not None:
            rect(*world.runway, (0.30, 0.30, 0.34))
        for ppx, ppy in world.pads:
            rect(ppx - 8, ppy - 8, ppx + 8, ppy + 8, (0.45, 0.45, 0.5))
        for b in world.boxes:
            if b.mm:
                rect(b.x0, b.y0, b.x1, b.y1, (0.72, 0.70, 0.66))
        for x0, y0, x1, y1 in world.voids:                      # Tunneleingänge: orange Quadrate
            rect(x0 - 2.0, y0 - 2.0, x1 + 2.0, y1 + 2.0, (0.95, 0.55, 0.10))
        tex = Texture("karte")
        tex.load(img)
        tex.setWrapU(Texture.WMClamp)
        tex.setWrapV(Texture.WMClamp)
        tex.setMinfilter(Texture.FTLinear)
        tex.setMagfilter(Texture.FTLinear)
        return tex

    def build_minimap(self):
        """Runde Karte, die sich mit dir dreht: dein Pfeil zeigt immer nach oben. Gegner erscheinen nur kurz,
        wenn sie schiessen."""
        world = self.world
        R = self.MM_S / 2.0
        self.mm_R = R
        self.mm_root = self.a2dBottomLeft.attachNewNode("minimap")
        self.mm_root.setPos(0.07 + R, 0, 0.24 + R)
        self.map_tex = self.build_map_texture()

        def marker(n, sort):
            n.setTransparency(TransparencyAttrib.MAlpha)
            n.setBin("fixed", sort)
            n.setDepthTest(False)
            n.setDepthWrite(False)
            return n

        # Scheibe mit Kartentextur; die Texturkoordinaten werden pro Bild neu gesetzt (Drehung)
        self.mm_n = 64
        self.mm_disc = None
        try:
            fmt = GeomVertexFormat.getV3t2()
            vd = GeomVertexData("mmdisc", fmt, Geom.UHDynamic)
            vd.setNumRows(self.mm_n + 1)
            vw = GeomVertexWriter(vd, "vertex")
            vw.addData3(0.0, 0.0, 0.0)
            for i in range(self.mm_n):
                a = 2 * math.pi * i / self.mm_n
                vw.addData3(math.cos(a) * R, 0.0, math.sin(a) * R)
            tw = GeomVertexWriter(vd, "texcoord")
            for _ in range(self.mm_n + 1):
                tw.addData2(0.0, 0.0)
            prim = GeomTriangles(Geom.UHStatic)
            for i in range(self.mm_n):
                prim.addVertices(0, 1 + i, 1 + (i + 1) % self.mm_n)
            geom = Geom(vd)
            geom.addPrimitive(prim)
            gn = GeomNode("mmdisc")
            gn.addGeom(geom)
            disc = self.mm_root.attachNewNode(gn)
            disc.setLightOff()
            disc.setTwoSided(True)
            if self.map_tex is not None:
                disc.setTexture(self.map_tex)
            disc.setTransparency(TransparencyAttrib.MAlpha)
            disc.setColorScale(1, 1, 1, 0.92)
            marker(disc, 21)
            self.mm_disc = (disc, vd)
        except Exception as e:
            print("Minimap-Scheibe nicht verfügbar:", e)
        ring = Mesh(lit=False)                       # Rahmen: dunkler Rand mit hellem Innenring

        def band(r0, r1, col, n=64):
            for i in range(n):
                a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
                p = lambda r, a: (math.cos(a) * r, 0.0, math.sin(a) * r)       # noqa: E731
                ring.tri(p(r0, a0), p(r1, a0), p(r1, a1), col, ref=(0, 5, 0))
                ring.tri(p(r0, a0), p(r1, a1), p(r0, a1), col, ref=(0, 5, 0))

        band(R - 0.002, R + 0.012, (0.05, 0.06, 0.08))
        band(R - 0.002, R + 0.003, (0.85, 0.88, 0.92))
        rn = self.mm_root.attachNewNode(ring.node("mmring"))
        rn.setTwoSided(True)
        marker(rn, 24)

        def dot(size, col):
            c = CardMaker("dot")
            c.setFrame(-size, size, -size, size)
            n = self.mm_root.attachNewNode(c.generate())
            n.setColor(*col)
            return marker(n, 22)

        def arrow(size, col):
            """Pfeil mit dunklem Rand, Spitze nach oben; gedreht wird per setR."""
            am = Mesh(lit=False)
            for s, c in ((size * 1.35, (0, 0, 0)), (size, (1, 1, 1))):
                tip, l, nt, r = (0, 0, s), (-0.62 * s, 0, -0.72 * s), (0, 0, -0.30 * s), (0.62 * s, 0, -0.72 * s)
                am.tri(tip, l, nt, c)
                am.tri(tip, nt, r, c)
            n = self.mm_root.attachNewNode(am.node("arrow"))
            n.setTwoSided(True)
            n.setColorScale(*col)
            return marker(n, 23)

        self.mm_me = arrow(0.022, (0.3, 1.0, 0.3, 1))
        self.mm_dots = {}                          # Spieler-ID -> Pfeil (nur kurz nach einem Schuss)
        self.mm_arrow_factory = arrow
        self.mm_vehs = {v.id: dot(0.009, (1.0, 0.85, 0.2, 1)) for v in world.vehicles}
        self.mm_helis = {q.id: dot(0.012, (0.45, 0.85, 1.0, 1)) for q in world.helis}
        ring = Mesh(lit=False)                     # Tomahawk-Zielkreis (nur für den, der ausgelöst hat)
        rr = STRIKE_R * self.mm_R / self.MM_VIS
        for i in range(48):
            a0, a1 = 2 * math.pi * i / 48, 2 * math.pi * (i + 1) / 48
            p = lambda r, a: (math.cos(a) * r, 0.0, math.sin(a) * r)        # noqa: E731
            ring.tri(p(rr - 0.003, a0), p(rr + 0.003, a0), p(rr + 0.003, a1), (1, 0.2, 0.15), ref=(0, 5, 0))
            ring.tri(p(rr - 0.003, a0), p(rr + 0.003, a1), p(rr - 0.003, a1), (1, 0.2, 0.15), ref=(0, 5, 0))
            ring.tri(p(0, a0), p(rr - 0.003, a0), p(rr - 0.003, a1), (1, 0.2, 0.15, 0.18), ref=(0, 5, 0))
        self.mm_strike = marker(self.mm_root.attachNewNode(ring.node("mmstrike")), 22)
        self.mm_strike.setTwoSided(True)
        self.mm_strike.hide()
        self.mm_strike_edge = dot(0.011, (1.0, 0.2, 0.15, 1))
        # eigener Lärm: Fläche + Rand (Einheitskreis, skaliert); Wellen bei Schuss/Explosion
        self.mm_vis, self.mm_zoom_hold = self.MM_VIS, 0.0
        nm = Mesh(lit=False)
        for i in range(48):
            a0, a1 = 2 * math.pi * i / 48, 2 * math.pi * (i + 1) / 48
            p = lambda r, a: (math.cos(a) * r, 0.0, math.sin(a) * r)        # noqa: E731
            nm.tri((0, 0, 0), p(0.97, a0), p(0.97, a1), (1, 1, 1, NOISE_MM_ALPHA), ref=(0, 5, 0))
            nm.tri(p(0.97, a0), p(1.0, a0), p(1.0, a1), (1, 1, 1, NOISE_MM_ALPHA * 3), ref=(0, 5, 0))
            nm.tri(p(0.97, a0), p(1.0, a1), p(0.97, a1), (1, 1, 1, NOISE_MM_ALPHA * 3), ref=(0, 5, 0))
        self.mm_noise = marker(self.mm_root.attachNewNode(nm.node("mmnoise")), 22)
        self.mm_noise.setTwoSided(True)
        self.mm_noise.hide()
        wm = Mesh(lit=False)
        for i in range(48):
            a0, a1 = 2 * math.pi * i / 48, 2 * math.pi * (i + 1) / 48
            p = lambda r, a: (math.cos(a) * r, 0.0, math.sin(a) * r)        # noqa: E731
            wm.tri(p(0.93, a0), p(1.0, a0), p(1.0, a1), (1, 1, 1), ref=(0, 5, 0))
            wm.tri(p(0.93, a0), p(1.0, a1), p(0.93, a1), (1, 1, 1), ref=(0, 5, 0))
        self.mm_wave_tpl = wm
        self.mm_waves = []                         # [Knoten, Start, Radius (m), x, y]
        self.mm_strike_edge.hide()
        self.mm_north = OnscreenText(text="N", parent=self.mm_root, pos=(0, 0), scale=0.04,
                                     fg=(1.0, 0.35, 0.3, 1), shadow=(0, 0, 0, 0.9), mayChange=True)
        self.mm_north.setBin("fixed", 25)

    PING_T = 1.0          # so lange bleibt ein schiessender Spieler auf der Minimap sichtbar

    def mm_xy(self, x, y, clamp=True):
        """Weltpunkt -> Position auf der runden Karte (relativ zu dir und deiner Blickrichtung).
        Ausserhalb des Kreises wird der Punkt an den Rand gesetzt (clamp) bzw. None geliefert."""
        pl = self.player
        h = math.radians(pl.heading)
        dx, dy = x - pl.x, y - pl.y
        sx = dx * math.cos(h) + dy * math.sin(h)            # nach rechts
        sy = -dx * math.sin(h) + dy * math.cos(h)           # nach vorn = oben
        k = self.mm_R / self.mm_vis
        sx, sy = sx * k, sy * k
        d = math.hypot(sx, sy)
        lim = self.mm_R * 0.94
        if d > lim:
            if not clamp:
                return None
            sx, sy = sx / d * lim, sy / d * lim
        return sx, sy

    def noise_wave(self, x, y, r):
        """Eigener Lärm (Schuss, Explosion, Schlag): Ring breitet sich auf der Minimap bis r m aus."""
        if not NOISE_MINIMAP or r <= 0 or not hasattr(self, "mm_waves"):
            return
        now = time.time()
        if self.mm_waves and now - self.mm_waves[-1][1] < 0.04 and abs(self.mm_waves[-1][2] - r) < 1.0:
            return                                 # dieselbe Welle doppelt (Ereignis lokal + vom Host)
        n = self.mm_root.attachNewNode(self.mm_wave_tpl.node("wave"))
        n.setTwoSided(True)
        n.setTransparency(TransparencyAttrib.MAlpha)
        n.setBin("fixed", 22)
        n.setDepthTest(False)
        n.setDepthWrite(False)
        self.mm_waves.append([n, now, r, x, y])
        if len(self.mm_waves) > 8:
            self.mm_waves.pop(0)[0].removeNode()
        if NOISE_MINIMAP_ZOOM and r > self.MM_VIS * 0.92:          # zu gross für den Ausschnitt: herauszoomen
            self.mm_zoom_hold = max(self.mm_zoom_hold, min(NOISE_ZOOM_MAX, r * 1.1))
            self.mm_zoom_until = now + self.wave_t(r) + 0.5

    @staticmethod
    def wave_t(r):
        return NOISE_WAVE_T * max(0.6, min(2.2, math.sqrt(r / NOISE_SHOT)))

    def update_noise_map(self, dt):
        """Eigener Lärmkreis (Laufen/Rennen/Ducken/Fahren) und die Wellen; Zoom der Minimap."""
        pl, now = self.player, time.time()
        # Zoom: bei grosser Welle weich heraus, danach wieder zurück
        want = self.mm_zoom_hold if now < getattr(self, "mm_zoom_until", 0.0) else self.MM_VIS
        if now >= getattr(self, "mm_zoom_until", 0.0):
            self.mm_zoom_hold = 0.0
        self.mm_vis += (max(want, self.MM_VIS) - self.mm_vis) * min(1.0, dt * (6.0 if want > self.mm_vis else 2.5))
        k = self.mm_R / self.mm_vis
        self.mm_strike.setScale(self.MM_VIS / self.mm_vis)
        r = self.world.player_noise(pl) if NOISE_MINIMAP and pl.hp > 0 else 0.0
        if r > 0:
            self.mm_noise.setScale(min(r * k, self.mm_R * 0.97))
            self.mm_noise.show()
        else:
            self.mm_noise.hide()
        keep = []
        for w in self.mm_waves:
            n, t0, rmax, x, y = w
            u = (now - t0) / self.wave_t(rmax)
            if u >= 1.0:
                n.removeNode()
                continue
            keep.append(w)
            p = self.mm_xy(x, y)
            n.setPos(p[0], 0, p[1])
            rad = rmax * (1.0 - (1.0 - u) ** 2) * k
            n.setScale(max(0.002, min(rad, self.mm_R * 0.98)))
            n.setColorScale(1, 1, 1, 0.55 * (1.0 - u) ** 1.3)
        self.mm_waves = keep

    def update_minimap(self):
        pl = self.player
        R = self.mm_R
        now_ = time.time()
        self.update_noise_map(min(0.1, max(0.0, now_ - getattr(self, "mm_last_t", now_))))
        self.mm_last_t = now_
        h = math.radians(pl.heading)
        ch, sh = math.cos(h), math.sin(h)
        if self.mm_disc is not None:
            _disc, vd = self.mm_disc
            T = WORLD + 2 * self.MAP_MARGIN
            vis = self.mm_vis / R
            try:
                tw = GeomVertexWriter(vd, "texcoord")
                for i in range(self.mm_n + 1):
                    if i == 0:
                        sx = sy = 0.0
                    else:
                        a = 2 * math.pi * (i - 1) / self.mm_n
                        sx, sy = math.cos(a) * R * vis, math.sin(a) * R * vis    # in Metern
                    wx = pl.x + sx * ch - sy * sh
                    wy = pl.y + sx * sh + sy * ch
                    tw.addData2((wx + self.MAP_MARGIN) / T, (wy + self.MAP_MARGIN) / T)
            except Exception:
                pass
        self.mm_me.setPos(0, 0, 0)
        self.mm_me.setR(0)                          # eigener Pfeil zeigt immer nach oben
        self.mm_north.setPos(sh * R * 0.84, ch * R * 0.84 - 0.014)
        now = time.time()
        for pid, (t0, _x, _y) in list(self.pings.items()):
            age = now - t0
            n = self.mm_dots.get(pid)
            if n is None:
                n = self.mm_dots[pid] = self.mm_arrow_factory(0.019, (1.0, 0.25, 0.2, 1))
            other = self.world.players.get(pid)
            p = self.mm_xy(other.x, other.y, False) if other is not None else None
            if age > self.PING_T or other is None or other.hp <= 0 or p is None:
                n.hide()
                continue
            n.show()                               # folgt dem Spieler, solange er sichtbar ist
            n.setPos(p[0], 0, p[1])
            n.setR(-(other.heading - pl.heading))
            n.setColorScale(1.0, 0.25, 0.2, 1.0 - smoothstep(0.15, self.PING_T, age))
        w = self.world
        if w.strike == 1 and w.strike_by == self.my_id and w.phase == "play":
            p = self.mm_xy(w.strike_x, w.strike_y, False)
            if p is not None:                      # Zielkreis (Zielpunkt + STRIKE_R) bis zum Einschlag
                self.mm_strike.setPos(p[0], 0, p[1])
                self.mm_strike.show()
                self.mm_strike_edge.hide()
            else:                                  # ausserhalb des Ausschnitts: Punkt am Rand in Zielrichtung
                q = self.mm_xy(w.strike_x, w.strike_y)
                self.mm_strike_edge.setPos(q[0], 0, q[1])
                self.mm_strike_edge.show()
                self.mm_strike.hide()
        else:
            self.mm_strike.hide()
            self.mm_strike_edge.hide()
        for v in self.world.vehicles:
            n = self.mm_vehs.get(v.id)
            if n is not None:
                p = self.mm_xy(v.x, v.y)
                n.setPos(p[0], 0, p[1])
                (n.show if v.hp > 0 else n.hide)()
        for q in self.world.helis:
            n = self.mm_helis.get(q.id)
            if n is not None:
                p = self.mm_xy(q.x, q.y)
                n.setPos(p[0], 0, p[1])
                (n.show if q.hp > 0 else n.hide)()

    # ------------------------------------------------------------ Lootkisten
    def build_crates(self):
        """Vorlagen für die drei Kistenarten (die Kisten selbst kommen und gehen, siehe update_crates):
        gewöhnlich = kleine braune Holzkiste mit blassem Schwebewürfel,
        selten = grössere Metallkiste mit blau leuchtenden Bändern, Leuchtwürfel und blauer Lichtsäule,
        gold = grösste Kiste, golden, mit rotem Rubin vorne, schwebendem Rubin und goldener Lichtsäule."""
        rng = random.Random(11)
        wood, cmark = Mesh(), Mesh(lit=False)
        wood.mat = "wood"
        box(wood, 0, 0, 0.4, 1.1, 0.8, 0.8, (0.78, 0.56, 0.22), rng)
        box(wood, 0, 0, 0.84, 1.16, 0.86, 0.08, (0.50, 0.34, 0.10))
        for sx in (-0.42, 0.42):                                          # Latten
            box(wood, sx, 0, 0.4, 0.08, 0.84, 0.82, (0.45, 0.30, 0.10))
        box(cmark, 0, 0, 0, 0.22, 0.22, 0.22, (0.95, 0.88, 0.65))
        metal, glow, rmark, beam = Mesh(), Mesh(lit=False), Mesh(lit=False), Mesh(alpha=0.22, lit=False)
        metal.mat = "metal"
        box(metal, 0, 0, 0.5, 1.45, 1.0, 1.0, (0.20, 0.24, 0.38), rng)
        box(metal, 0, 0, 1.05, 1.52, 1.07, 0.12, (0.14, 0.16, 0.26))
        for sx in (-0.6, 0.6):                                            # Eckverstärkungen
            box(metal, sx, 0, 0.5, 0.12, 1.06, 1.02, (0.32, 0.34, 0.42))
        for z in (0.3, 0.75):                                             # leuchtende Bänder
            box(glow, 0, 0, z, 1.47, 1.02, 0.07, (0.35, 0.85, 1.0))
        box(rmark, 0, 0, 0, 0.36, 0.36, 0.36, (0.45, 0.9, 1.0))
        box(beam, 0, 0, 4.6, 0.5, 0.5, 4.0, (0.4, 0.85, 1.0))
        gold, gglow, gmark, gbeam = Mesh(), Mesh(lit=False), Mesh(lit=False), Mesh(alpha=0.13, lit=False)
        gold.mat = "metal"
        box(gold, 0, 0, 0.58, 1.75, 1.18, 1.16, (1.0, 0.76, 0.20), rng)
        box(gold, 0, 0, 1.2, 1.84, 1.26, 0.14, (0.80, 0.55, 0.10))          # Deckel
        box(gold, 0, 0, 0.06, 1.84, 1.26, 0.12, (0.80, 0.55, 0.10))         # Sockel
        for sx in (-0.78, 0.78):
            box(gold, sx, 0, 0.6, 0.14, 1.24, 1.12, (0.86, 0.62, 0.14))
        box(gglow, 0, -0.62, 0.68, 0.34, 0.08, 0.34, (1.0, 0.08, 0.12))    # Rubin vorne
        box(gglow, 0, 0.62, 0.68, 0.34, 0.08, 0.34, (1.0, 0.08, 0.12))     # und hinten
        box(gglow, 0, -0.6, 0.68, 0.5, 0.05, 0.5, (1.0, 0.85, 0.35))       # goldene Fassung
        box(gglow, 0, 0.6, 0.68, 0.5, 0.05, 0.5, (1.0, 0.85, 0.35))
        box(gmark, 0, 0, 0, 0.42, 0.42, 0.42, (1.0, 0.1, 0.15))
        box(gbeam, 0, 0, 6.0, 0.6, 0.6, 6.0, (1.0, 0.62, 0.15))            # Lichtsäule über dem Rubin
        self.crate_tpl = {}
        for kind, parts in (("common", ((wood, "body", True), (cmark, "mark", False))),
                            ("rare", ((metal, "body", True), (glow, "glow", False), (rmark, "mark", False),
                                      (beam, "beam", False))),
                            ("gold", ((gold, "body", True), (gglow, "glow", False), (gmark, "mark", False),
                                      (gbeam, "beam", False)))):
            tpl = NodePath(f"crate_{kind}")
            for mesh, name, lit in parts:
                n = tpl.attachNewNode(mesh.node(name))
                if not lit:
                    n.setFogOff()
                if name == "beam":
                    n.setTransparency(TransparencyAttrib.MAlpha)
                    n.setDepthWrite(False)
                    n.setBin("transparent", 4)
                    n.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
                if name == "mark" and kind == "gold":
                    n.setP(45)
                    n.setR(35)                                            # auf der Spitze: wie ein Edelstein
            self.crate_tpl[kind] = tpl
        self.crate_views = {}
        self.update_crates()

    def build_toma(self):
        """Tomahawk: Säule (ein Modell, das zum gerade aktiven bzw. versinkenden Ort springt) und die Rakete
        für den sichtbaren Anflug."""
        self.toma_np = None
        self.toma_rk = None
        self.toma_trail, self.toma_trail_t, self.toma_whistled = [], 0.0, False
        self.toma_seen = (-2, -2)
        if not self.world.toma_spots:
            return
        root, col, knob, beam = build_column_model()
        root.reparentTo(self.render)
        root.hide()
        self.toma_np, self.toma_col, self.toma_knob, self.toma_beam = root, col, knob, beam
        rk, fl = build_rocket(False)
        rr = self.render.attachNewNode("tomahawk_rocket")
        rk.reparentTo(rr)
        fl.reparentTo(rr)
        glow = Mesh(alpha=0.45, lit=False)
        box(glow, 0, -0.85, 0, 0.28, 0.6, 0.28, (1.0, 0.45, 0.1))          # Triebwerksglühen
        gn = rr.attachNewNode(glow.node("glow"))
        gn.setTransparency(TransparencyAttrib.MAlpha)
        gn.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd))
        gn.setDepthWrite(False)
        rr.setScale(10.0)                                 # gross genug, um sie am Himmel zu sehen
        rr.setFogOff()
        rr.setLightOff()
        rr.hide()
        self.toma_rk = rr

    def zap_fx(self, src, dst, hit, sound=True):
        """Elektroblitz: gezackte blaue Linie aus kurzen Stücken, Funken am Ziel, Knistern."""
        r = self.prng
        n = 7
        pts = [src]
        for i in range(1, n):
            t = i / n
            pts.append((src[0] + (dst[0] - src[0]) * t + r.uniform(-0.25, 0.25),
                        src[1] + (dst[1] - src[1]) * t + r.uniform(-0.25, 0.25),
                        src[2] + (dst[2] - src[2]) * t + r.uniform(-0.25, 0.25)))
        pts.append(dst)
        for a, b in zip(pts, pts[1:]):
            ln = math.dist(a, b)
            np_ = self.cube_np.copyTo(self.render)
            np_.setPos((a[0] + b[0]) / 2, (a[1] + b[1]) / 2, (a[2] + b[2]) / 2)
            np_.lookAt(*b)
            np_.setScale(0.05, ln, 0.05)
            np_.setColorScale(0.6, 0.9, 1.0, 1)
            np_.setLightOff()
            np_.setFogOff()
            self.parts.append(Particle(np_, np_.getPos(), (0.0, 0.0, 0.0), 0.16, 0.0, 0.0, False))
            self.parts[-1].x, self.parts[-1].y, self.parts[-1].z = np_.getX(), np_.getY(), np_.getZ()
        if hit:
            for _ in range(10):
                self.add_particle(dst, (r.uniform(-3, 3), r.uniform(-3, 3), r.uniform(1, 4)), (0.6, 0.9, 1.0),
                                  0.04, 0.4, 0.2)
        if sound:
            self.sfx.play("zap", tuple(src), 1.0, self.prng.uniform(0.95, 1.05))

    def slam_fx(self, pos, rad):
        """Koloss-Bodenschlag: flache Staubwelle bis zum Radius, Brocken, dumpfer Knall, Beben in der Nähe."""
        x, y, z = pos
        r = self.prng
        self.fx_spawn(self.disc_np, (x, y, z + 0.2), 0.7,
                      0.5, rad, (0.75, 0.68, 0.55), (0.5, 0.45, 0.38), p=1.0)
        for i in range(14):
            a = i * math.tau / 14
            self.smoke_puff((x + math.cos(a) * rad * 0.6, y + math.sin(a) * rad * 0.6, z + 0.3), 0.9, 1.4, 0.6)
            self.add_particle((x, y, z + 0.4), (math.cos(a) * r.uniform(3, 7), math.sin(a) * r.uniform(3, 7),
                                                r.uniform(2, 5)), (0.45, 0.4, 0.32), 0.12, 1.2, 0.3, 4.0)
        self.sfx.play("explosion", (x, y, z), 1.0, 0.55)
        pl = self.player
        d = math.hypot(pl.x - x, pl.y - y)
        if d < rad * 3:                                  # Beben: je näher, desto stärker
            self.sp_cam.kick((1.0 - d / (rad * 3)) * 9.0)
            self.sp_hurt.kick(self.prng.choice((-1, 1)) * (1.0 - d / (rad * 3)) * 60.0)

    BUFF_LOOK = {"speed": ("T", (0.3, 1.0, 0.6)), "damage": ("S", (1.0, 0.35, 0.25)), "tank": ("HP", (1.0, 0.8, 0.25))}

    def update_ability_icons(self):
        """Buff-Symbol (Kreis-Timer = Restzeit), Dash (leuchtet bereit, sonst grau mit ablaufender Abklingzeit),
        Jetpack (Kreis = Treibstoff), Schildbalken und Ausrüstungs-Übersicht."""
        pl = self.player
        ic = self.ability_icons.get("buff")
        if ic is None:
            return
        alive = pl.hp > 0
        dash, jet = self.ability_icons["dash"], self.ability_icons["jet"]
        if alive and wears(pl, "dash"):
            rdy = pl.dash_cd <= 0
            dash.set(rdy, 1.0 if rdy else 1.0 - pl.dash_cd / DASH_CD, None,
                     "Dash" if rdy else f"{int(math.ceil(pl.dash_cd))} s")
        else:
            dash.hide()
        if alive and wears(pl, "jetpack"):
            jet.set(pl.jet_fuel > 0.3, pl.jet_fuel / JET_FUEL, None, "")
            jet.bar(pl.jet_fuel / JET_FUEL)
        else:
            jet.hide()
        if alive and wears(pl, "shield"):
            self.shield_bg.show()
            self.shield_fg.show()
            self.shield_fg.setSx(max(0.55 * pl.shield_hp / SHIELD_HP, 0.0001))
        else:
            self.shield_bg.hide()
            self.shield_fg.hide()
        for sl, tl in self.gear_tiles.items():
            gi = pl.gear.get(sl) if alive else None
            self.set_text(tl["label"], (GEAR[gi].hud or GEAR[gi].name) if gi is not None else "")
            if gi is not None:
                tl["label"].setFg(tuple(c * 0.65 + 0.35 for c in GEAR[gi].col) + (1,))   # aufgehellt: lesbar
            tl["sym"].setColorScale(1, 1, 1, 0.1 if gi is not None else 0.2)   # leer: Umriss etwas deutlicher
        b = getattr(pl, "buff", None)
        if b in BUFF_T and pl.buff_t > 0 and pl.hp > 0:
            lab, col = self.BUFF_LOOK.get(b, ("B", (1, 1, 1)))
            ic.set(True, pl.buff_t / BUFF_T[b], lab, f"{BUFF_NAMES[b]} {int(math.ceil(pl.buff_t))} s", col)
        else:
            ic.hide()

    def update_noise_debug(self):
        """NOISE_DEBUG: Lärmradien der letzten Geräusche als Ringe am Boden (nur wo die Welt simuliert wird)."""
        if not hasattr(self, "noise_rings"):
            m = Mesh(lit=False)
            for i in range(40):
                a0, a1 = math.tau * i / 40, math.tau * (i + 1) / 40
                pp = lambda r, a: (math.cos(a) * r, math.sin(a) * r, 0.0)      # noqa: E731
                m.tri(pp(0.97, a0), pp(1.0, a0), pp(1.0, a1), (1.0, 0.9, 0.2), ref=(0, 0, -5))
                m.tri(pp(0.97, a0), pp(1.0, a1), pp(0.97, a1), (1.0, 0.9, 0.2), ref=(0, 0, -5))
            self.noise_ring_np = NodePath(m.node("laerm"))
            self.noise_rings = []
        log = self.world.noise_log[-30:]
        while len(self.noise_rings) < len(log):
            n = self.noise_ring_np.copyTo(self.render)
            n.setTwoSided(True)
            n.setFogOff()
            n.setLightOff()
            self.noise_rings.append(n)
        for i, n in enumerate(self.noise_rings):
            if i < len(log):
                x, y, r, _t = log[i]
                n.setPos(x, y, self.world.height(x, y) + 0.15)
                n.setScale(r)
                n.show()
            else:
                n.hide()

    def toma_rocket_pos(self, u):
        """Flugbahn der Tomahawk-Rakete (u = 0 Start .. 1 Einschlag): von weit hinter dem Gebirge aus der
        Richtung strike_ang in einem hohen Bogen genau auf den Zielpunkt. Jeder rechnet sie selbst aus."""
        w = self.world
        tx, ty = w.strike_x, w.strike_y
        tz = w.height(tx, ty)
        dist = max(TOMA_ROCKET_MIN, TOMA_ROCKET_SPEED * max(1.0, w.strike_dur))
        a = math.radians(w.strike_ang)
        sx, sy = tx + math.cos(a) * dist, ty + math.sin(a) * dist
        u = max(0.0, min(1.0, u))
        x, y = sx + (tx - sx) * u, sy + (ty - sy) * u
        z = tz + TOMA_ROCKET_ALT * (1.0 - u ** 5) + 40.0 * math.sin(math.pi * u) * (1.0 - u)   # hoch, dann Sturzflug
        return x, y, z

    def update_toma(self, dt):
        """Säule am aktiven Ort zeigen (fährt hoch, Knopf leuchtet) bzw. die benutzte versinken lassen;
        Rakete im Anflug mit Rauchschweif und Ton. Sichtbar nur in Sichtweite (TOMA_SEE_R) - auch beim Host."""
        if getattr(self, "toma_np", None) is None:
            return
        w, pl = self.world, self.player
        cam = (pl.x, pl.y)

        def visible(i):
            if not 0 <= i < len(w.toma_spots):
                return False
            x, y, _z, _h = w.toma_spots[i]
            return math.hypot(cam[0] - x, cam[1] - y) <= TOMA_SEE_R

        i_up = w.toma_idx if visible(w.toma_idx) else -1
        i_sink = w.toma_sink_idx if (i_up < 0 and visible(w.toma_sink_idx)) else -1
        shown = i_up if i_up >= 0 else i_sink
        if (i_up, i_sink) != self.toma_seen:
            prev = self.toma_seen
            self.toma_seen = (i_up, i_sink)
            if shown >= 0:
                x, y, z, h = w.toma_spots[shown]
                self.toma_np.setPos(x, y, z)
                self.toma_np.setH(h)
                self.toma_np.show()
                if i_up >= 0 and w.toma_age < 1.0:
                    self.sfx.play("servo", (x, y, z + 1.0), 1.0, 1.0)        # fährt hoch
                elif i_sink >= 0 and prev[0] == i_sink:
                    self.sfx.play("servo", (x, y, z + 1.0), 0.9, 0.6)        # versinkt (tiefer, langsamer)
            else:
                self.toma_np.hide()
        if shown >= 0:
            if i_up >= 0:
                u = max(0.0, min(1.0, w.toma_age / TOMA_RISE_T))
                hgt = u * u * (3 - 2 * u)
                ready = w.toma_age >= TOMA_RISE_T
                blink = 0.6 + 0.4 * math.sin(time.time() * 6.0)
                self.toma_knob.setColorScale(1.0, 1.0, 1.0, 1.0) if ready else self.toma_knob.setColorScale(
                    0.5, 0.5, 0.5, 1.0)
                self.toma_beam.show()
                self.toma_beam.setColorScale(1, 1, 1, (0.3 + 0.7 * blink) * hgt if ready else 0.0)
            else:
                u = max(0.0, min(1.0, w.toma_sink_t / TOMA_SINK_T))
                hgt = 1.0 - u * u * (3 - 2 * u)
                self.toma_knob.setColorScale(0.25, 0.25, 0.25, 1.0)              # unbrauchbar: Knopf aus
                self.toma_beam.hide()
            self.toma_col.setSz(max(0.02, hgt))
        self.update_toma_rocket(dt)

    def update_toma_rocket(self, dt):
        """Anflug der Tomahawk-Rakete während des Countdowns - für alle sichtbar, der Zielort wird nirgends
        angezeigt; man sieht nur, wohin sie fliegt."""
        w = self.world
        rr = self.toma_rk
        flying = rr is not None and w.strike == 1 and w.strike_dur > 0 and w.phase == "play"
        if not flying:
            if rr is not None:
                rr.hide()
            self.sfx.jet_sound(None)
            self.toma_whistled = False
        else:
            u = 1.0 - max(0.0, w.strike_t) / w.strike_dur
            p = self.toma_rocket_pos(u)
            q = self.toma_rocket_pos(min(1.0, u + 0.002)) if u < 0.998 else self.toma_rocket_pos(u)
            if q == p:
                q2 = self.toma_rocket_pos(u - 0.002)
                q = (2 * p[0] - q2[0], 2 * p[1] - q2[1], 2 * p[2] - q2[2])
            rr.setPos(*p)
            rr.lookAt(*q)                                    # Spitze (+y) in Flugrichtung
            rr.setScale(10.0)
            self.toma_far(rr, p, 10.0)
            rr.show()
            self.sfx.jet_sound(p, w.strike_t)
            if w.strike_t <= TOMA_LOUD_T and not self.toma_whistled:
                self.toma_whistled = True
                self.sfx.play("whistle", None, TOMA_WHISTLE_VOL, 2.8 / max(0.5, TOMA_LOUD_T))   # passt in die Zeit
            self.toma_trail_t -= dt
            if self.toma_trail_t <= 0:                       # Rauchschweif hinter dem Triebwerk
                self.toma_trail_t = 0.05
                d = (p[0] - q[0], p[1] - q[1], p[2] - q[2])
                ln = math.sqrt(d[0] ** 2 + d[1] ** 2 + d[2] ** 2) or 1.0
                tail = (p[0] + d[0] / ln * 9.0, p[1] + d[1] / ln * 9.0, p[2] + d[2] / ln * 9.0)
                np_ = self.sphere_np.copyTo(self.render)        # Kopie: jede Wolke hat eigene Position/Grösse
                np_.setTransparency(TransparencyAttrib.MAlpha)
                np_.setDepthWrite(False)
                np_.setLightOff()
                np_.setFogOff()
                f = Fx(np_, tail, 7.0, 3.0, 12.0, (0.62, 0.6, 0.58), (0.4, 0.4, 0.42), p=1.1, rise=0.6)
                f.update(0.0)
                self.toma_trail.append(f)
                if len(self.toma_trail) > 140:
                    self.toma_trail.pop(0).np.removeNode()
        keep = []
        for f in self.toma_trail:
            if f.update(dt):
                self.toma_far(f.np, (f.x, f.y, f.z), f.np.getScale()[0])
                keep.append(f)
            else:
                f.np.removeNode()
        self.toma_trail = keep

    TOMA_FAR = 420.0      # Kamera-Sichtweite ist 450 m: weiter weg wird verkleinert näher gezeichnet (gleiche Richtung)

    def toma_far(self, np_, pos, scale):
        """Rakete und Rauchschweif auch hinter der Sichtweite der Kamera zeigen: in derselben Richtung auf
        TOMA_FAR heranziehen und im gleichen Verhältnis verkleinern - sieht gleich aus, wird nicht abgeschnitten."""
        c = self.camera.getPos(self.render)
        d = math.dist(pos, (c[0], c[1], c[2]))
        if d > self.TOMA_FAR:
            k = self.TOMA_FAR / d
            np_.setPos(c[0] + (pos[0] - c[0]) * k, c[1] + (pos[1] - c[1]) * k, c[2] + (pos[2] - c[2]) * k)
            np_.setScale(max(0.01, scale * k))

    def update_crates(self):
        """Kisten-Darstellung an die Liste der Welt angleichen (neue zeigen, geöffnete entfernen)."""
        t = time.time()
        live = {}
        for c in self.world.crates:
            v = self.crate_views.get(c.cid)
            if v is None:
                root = self.render.attachNewNode(f"crate{c.cid}")
                root.setPos(c.x, c.y, c.z)
                root.setH((c.cid * 47) % 360)
                self.crate_tpl.get(c.kind, self.crate_tpl["common"]).copyTo(root)      # eigene Kopie: der Schwebewürfel bewegt sich je Kiste
                mark = root.find("**/mark")
                if getattr(c, "bonus", False):         # Titan-Belohnung: goldene Lichtsäule, weithin sichtbar
                    bm = Mesh(lit=False)
                    for k in range(6):
                        a0, a1 = math.tau * k / 6, math.tau * (k + 1) / 6
                        p0 = (math.cos(a0) * 0.35, math.sin(a0) * 0.35)
                        p1 = (math.cos(a1) * 0.35, math.sin(a1) * 0.35)
                        gc = (1.0, 0.62, 0.08)
                        bm.tri((p0[0], p0[1], 0.5), (p1[0], p1[1], 0.5), (p1[0], p1[1], TITAN_BEAM_H), gc, (0, 0, 10))
                        bm.tri((p0[0], p0[1], 0.5), (p1[0], p1[1], TITAN_BEAM_H), (p0[0], p0[1], TITAN_BEAM_H), gc, (0, 0, 10))
                    bn = root.attachNewNode(bm.node("beam"))
                    bn.setTwoSided(True)
                    bn.setTransparency(TransparencyAttrib.MAlpha)
                    bn.setDepthWrite(False)
                    bn.setBin("transparent", 4)
                    bn.setColorScale(1, 1, 1, 0.45)          # normal durchscheinend: bleibt auch vor Himmel gold
                    bn.setLightOff()
                    bn.setFogOff()                     # sonst färbt der Nebel sie weiss
                v = (root, mark)
            live[c.cid] = v
            root, mark = v
            if not mark.isEmpty():
                hz, spin = {"rare": (1.9, 160.0), "gold": (2.3, 120.0)}.get(c.kind, (1.45, 90.0))
                mark.setPos(0, 0, hz + 0.2 * math.sin(t * 2.0 + c.cid))
                mark.setH(t * spin - root.getH())
        for cid, (root, _m) in self.crate_views.items():
            if cid not in live:
                root.removeNode()
        self.crate_views = live


def build_column_model():
    """Tomahawk-Säule: zylinderförmiges Gerät (achteckig) mit Warnstreifen, oben eine Plattform mit dem roten
    Knopf im gelben Ring, darüber eine rote Lichtsäule (von weitem sichtbar). Die Säule fährt durch Strecken in
    der Höhe (setSz) aus dem Boden. Ein schwacher roter Schein über dem Knopf pulsiert - man muss die Säule
    trotzdem suchen. -> (Wurzel, Säule, Knopf, Schein)"""
    def cyl(m, z0, r, h, col, sides=10):
        """Geschlossener Zylinder (Mantel + Deckel oben und unten) um die Achse."""
        pts = [(math.cos(math.tau * k / sides) * r, math.sin(math.tau * k / sides) * r) for k in range(sides)]
        ref = (0.0, 0.0, z0 + h / 2)
        for k in range(sides):
            (ax, ay), (bx, by) = pts[k], pts[(k + 1) % sides]
            m.tri((ax, ay, z0), (bx, by, z0), (bx, by, z0 + h), col, ref)
            m.tri((ax, ay, z0), (bx, by, z0 + h), (ax, ay, z0 + h), col, ref)
            m.tri((0, 0, z0 + h), (ax, ay, z0 + h), (bx, by, z0 + h), col, ref)
            m.tri((0, 0, z0), (ax, ay, z0), (bx, by, z0), col, ref)
    body, glow = Mesh(), Mesh(lit=False)
    body.mat = "metal"
    cyl(body, 0.0, 0.42, 1.25, (0.30, 0.32, 0.36))
    cyl(body, 1.25, 0.5, 0.12, (0.18, 0.19, 0.22))
    cyl(body, 0.0, 0.52, 0.12, (0.18, 0.19, 0.22))
    for k in range(4):                                                   # gelb-schwarze Warnringe
        cyl(glow, 0.3 + k * 0.12, 0.43, 0.06, (0.95, 0.75, 0.1) if k % 2 == 0 else (0.08, 0.08, 0.08))
    cyl(glow, 1.37, 0.3, 0.03, (0.95, 0.75, 0.1))                        # gelber Ring um den Knopf
    knob = Mesh(lit=False)
    cyl(knob, 1.37, 0.2, 0.13, (1.0, 0.08, 0.06))                        # der rote Knopf
    beam = Mesh(alpha=0.35, lit=False)                                   # dezenter roter Schein über dem Knopf
    box(beam, 0, 0, 1.95, 0.3, 0.3, 0.9, (1.0, 0.15, 0.08))
    root = NodePath("toma_column")
    col = root.attachNewNode("column")
    col.attachNewNode(body.node("body"))
    g = col.attachNewNode(glow.node("glow"))
    g.setFogOff()
    kn = col.attachNewNode(knob.node("knob"))
    kn.setFogOff()
    bm = root.attachNewNode(beam.node("beam"))
    bm.setTransparency(TransparencyAttrib.MAlpha)
    bm.setDepthWrite(False)
    bm.setBin("transparent", 4)
    bm.setAttrib(ColorBlendAttrib.make(ColorBlendAttrib.MAdd, ColorBlendAttrib.OIncomingAlpha,
                                       ColorBlendAttrib.OOne))           # mit Nebel: aus der Ferne kaum zu sehen
    return root, col, kn, bm


class VehicleView:
    """Darstellung des Geländewagens: gleitet weich auf die gemeldete Position, neigt sich
    mit dem Gelände, Räder drehen sich, Lebensbalken, brennendes Wrack nach der Zerstörung."""

    def __init__(self, v):
        self.root, self.wheels, self.bar, self.fg = build_vehicle_model()
        self.x, self.y, self.z, self.h = v.x, v.y, v.z, v.heading
        self.pitch = self.roll = self.spin = self.smoke_t = 0.0

    def update(self, v, dt, world, game):
        if math.hypot(v.x - self.x, v.y - self.y) > 6.0:               # Sprung (neu aufgestellt)
            self.x, self.y, self.z, self.h = v.x, v.y, v.z, v.heading
        a = min(1.0, 18.0 * dt)
        self.x += (v.x - self.x) * a
        self.y += (v.y - self.y) * a
        self.z += (v.z - self.z) * a
        self.h += ((v.heading - self.h + 180.0) % 360.0 - 180.0) * a
        hr = math.radians(self.h)
        fx, fy, rx, ry = -math.sin(hr), math.cos(hr), math.cos(hr), math.sin(hr)
        gf = world.height(self.x + fx * 1.3, self.y + fy * 1.3)
        gb = world.height(self.x - fx * 1.3, self.y - fy * 1.3)
        gr = world.height(self.x + rx * 0.9, self.y + ry * 0.9)
        gl = world.height(self.x - rx * 0.9, self.y - ry * 0.9)
        tp = math.degrees(math.atan2(clampf(gf - gb, -1.5, 1.5), 2.6))
        tr = -math.degrees(math.atan2(clampf(gr - gl, -1.5, 1.5), 1.8))
        self.pitch += (tp - self.pitch) * min(1.0, 8.0 * dt)
        self.roll += (tr - self.roll) * min(1.0, 8.0 * dt)
        r = self.root
        r.setPos(self.x, self.y, self.z)
        r.setHpr(self.h, self.pitch, self.roll)
        if v.hp <= 0:                                                   # Wrack
            r.setColorScale(0.22, 0.2, 0.18, 1)
            self.bar.hide()
            self.smoke_t -= dt
            if self.smoke_t <= 0 and v.dead_t < 25.0:
                self.smoke_t = 0.12
                game.smoke_puff((self.x, self.y, self.z + 1.0), 0.5, 2.0, 0.25)
            return
        r.clearColorScale()
        self.spin += v.speed * dt / 0.4
        for w in self.wheels:
            w.setP(-math.degrees(self.spin))
        if v.hp < VEH_HP:
            self.bar.show()
            self.fg.setSx(max(1.5 * v.hp / VEH_HP, 0.001))
        else:
            self.bar.hide()


class HeliView:
    """Darstellung des Helikopters: gleitet auf die gemeldete Lage, Rotoren drehen sich, Mündungsfeuer,
    Lebensbalken, Rauch bei Schaden, brennendes Wrack bis zum Respawn."""

    def __init__(self, q):
        self.root, self.rotor, self.trotor, self.bar, self.fg = build_heli_model()
        self.x, self.y, self.z, self.h, self.p, self.r = q.x, q.y, q.z, q.heading, q.pitch, q.roll
        self.spin = self.smoke_t = self.flash_t = 0.0

    def update(self, q, dt, world, game, own=False):
        if own or math.hypot(q.x - self.x, q.y - self.y) > 25.0 or abs(q.z - self.z) > 25.0:
            self.x, self.y, self.z, self.h, self.p, self.r = q.x, q.y, q.z, q.heading, q.pitch, q.roll
        else:
            a = min(1.0, 16.0 * dt)
            self.x += (q.x - self.x) * a
            self.y += (q.y - self.y) * a
            self.z += (q.z - self.z) * a
            self.h += ((q.heading - self.h + 180.0) % 360.0 - 180.0) * a
            self.p += (q.pitch - self.p) * a
            self.r += (q.roll - self.r) * a
        r = self.root
        r.setPos(self.x, self.y, self.z)
        r.setHpr(self.h, self.p, self.r)
        if q.hp <= 0:                                                   # Wrack
            r.setColorScale(0.2, 0.18, 0.16, 1)
            self.bar.hide()
            self.smoke_t -= dt
            if self.smoke_t <= 0 and q.dead_t < 30.0:
                self.smoke_t = 0.1
                game.smoke_puff((self.x, self.y, self.z + 1.5), 0.8, 2.2, 0.2)
            return
        r.clearColorScale()
        if q.driver >= 0 and q.stall_t <= 0:
            self.spin += 1500.0 * dt
        elif q.driver >= 0:                                  # lahmgelegt: Rotor dreht nur noch langsam nach
            self.spin += 260.0 * dt
        else:
            self.spin += 90.0 * dt
        self.rotor.setH(self.spin)
        self.trotor.setP(self.spin * 1.7)
        if q.firing:
            self.flash_t -= dt
            pl = world.players.get(q.driver)
            if self.flash_t <= 0 and pl is not None:
                self.flash_t = 0.06
                d = world.heli_dir(pl)
                game.fx_spawn(game.sphere_np, (q.x + d[0] * 2.0, q.y + d[1] * 2.0, q.z + 2.5 + d[2] * 2.0), 0.06,
                              0.1, 0.4, (1.0, 0.95, 0.6), (1.0, 0.45, 0.1), p=0.8, fog=False)
        if q.hp < HELI_HP:
            self.bar.show()
            self.fg.setSx(max(2.1 * q.hp / HELI_HP, 0.001))
            if q.hp < HELI_HP * 0.35:                                   # qualmt
                self.smoke_t -= dt
                if self.smoke_t <= 0:
                    self.smoke_t = 0.12
                    game.smoke_puff((self.x, self.y, self.z + 1.8), 0.5, 1.8, 0.25)
        else:
            self.bar.hide()


class MobView:
    """Darstellung eines Mobs: Modell, Lauf-/Angriffsanimation, Trefferblitz, Lebensbalken."""

    def __init__(self, mob, mtn=True):
        look = None
        if mob.kind == "critter":                            # Fellfarbe passend zur Karte (alle gleich)
            look = {"fur": CRITTER_COLORS["standard" if mtn else "karte"]}
        parts = build_mob(mob.kind, look)
        self.root, self.torso, self.legL, self.legR, self.bar, self.fg = parts[:6]
        self.rotors = parts[6] if len(parts) > 6 else []
        self.root.setScale(mob.scale)
        self.spark_t = 0.0

    def update(self, m):
        r = self.root
        r.setPos(m.x, m.y, m.z)
        if m.state == "dead":                              # nach hinten umfallen
            t = min(1.0, m.dead_t / 0.5)
            fall = 90.0 * t * (2 - t)
            sink = max(0.0, m.dead_t - 3.0) * 0.4
            r.setPos(m.x, m.y, m.z - sink)
            r.setHpr(m.heading, fall, 0)
            r.setColorScale(0.7, 0.7, 0.7, 1)
            self.bar.hide()
            return
        r.setHpr(m.heading, 0, 0)
        if self.rotors:                                    # Drohne: Rotoren drehen, leicht nach vorn geneigt
            for i, rn in enumerate(self.rotors):
                rn.setH(m.phase * 400.0 * (1 if i % 2 else -1))
            tilt = 12.0 if m.speed_now > 0 else 0.0
            if m.state == "attack":                        # lädt auf: Auge zittert, Körper bebt
                tilt = 4.0 * math.sin(m.atk_t * 60.0)
            self.torso.setP(-tilt)
        else:
            hop = m.kind == "critter"
            sw = math.sin(m.phase) * (1.0 if m.speed_now > 0 else 0.0)
            self.legL.setP(sw * (60 if hop else 40))
            self.legR.setP((sw if hop else -sw) * (60 if hop else 40))   # Fluchttier hoppelt (beide Beine)
            if not hop:
                self.legR.setZ(0.75)
            lean = 0.0
            if m.state == "attack":                        # ausholen, dann zuschlagen
                w = m.windup()
                rec = MOB_KINDS[m.kind].get("recover", 0.4)
                if getattr(m, "atk_kind", 0) == 2:           # Titan-Tritt: Bein weit zurück, Fuss fährt in den Boden,
                    rec = m.recover()                        # dann reisst er den Brocken nach vorn heraus
                    if m.atk_t < w * 0.7:
                        u = m.atk_t / (w * 0.7)
                        self.legR.setP(-55.0 * u)
                        self.legR.setZ(0.75)
                        lean = -12.0 * u
                    elif m.atk_t < w:
                        u = (m.atk_t - w * 0.7) / (w * 0.3)
                        self.legR.setP(-55.0 + 70.0 * u)
                        self.legR.setZ(0.75 - 0.22 * math.sin(u * math.pi))   # Fuss gräbt sich ein
                        lean = -12.0 + 6.0 * u
                    else:
                        u = min(1.0, (m.atk_t - w) / max(rec, 0.01))
                        self.legR.setP(80.0 * (1 - u) + 15.0 * u * (1 - u))
                        self.legR.setZ(0.75)
                        lean = 10.0 * (1 - u)
                elif getattr(m, "atk_kind", 0) == 1:         # Bodenschlag: weit nach hinten, dann voll nach vorn
                    lean = -35.0 * min(1.0, m.atk_t / w) if m.atk_t < w else 70.0 * max(0.0, 1 - (m.atk_t - w) / rec)
                elif m.atk_t < w:
                    lean = 25.0 * m.atk_t / w
                else:
                    u = (m.atk_t - w) / rec
                    lean = -45.0 * (1 - u) if u < 1 else 0.0
            self.torso.setP(lean)
            bob = abs(math.sin(m.phase)) * (0.25 if hop else 0.05) * (1 if m.speed_now > 0 else 0)
            self.torso.setZ((0.45 if hop else 0.75) + bob)
        if m.hurt_t > 0:
            r.setColorScale(2.0, 0.6, 0.6, 1)
        else:
            r.clearColorScale()
        if m.hp < m.max_hp:
            self.bar.show()
            self.fg.setSx(max(m.hp / m.max_hp, 0.001))
        else:
            self.bar.hide()


def _log_path():
    """Fehlerprotokoll neben der Executable (bzw. neben dem Skript)."""
    base = os.path.dirname(sys.executable if getattr(sys, "frozen", False)
                           else os.path.abspath(__file__))
    return os.path.join(base, "spiel_fehler_experimental.log")


SENS_CHOICES = (0.5, 0.75, 1.0, 1.5, 2.0)         # Mausempfindlichkeit (Faktor)
FPS_CHOICES = (60, 90, 120, 144, 165, 240, 0)      # Bildraten-Grenze (0 = unbegrenzt)


def fps_label(n):
    return "unbegrenzt" if n == 0 else f"{n} FPS"

GFX_MODES = ("standard", "hoch")
GFX_NAMES = {"standard": "Standard", "hoch": "Hoch (Schatten + Bloom, braucht mehr Leistung)"}


def _settings_path():
    base = os.path.dirname(sys.executable if getattr(sys, "frozen", False)
                           else os.path.abspath(__file__))
    return os.path.join(base, "spiel_einstellungen_experimental.json")


def load_settings():
    try:
        with open(_settings_path(), encoding="utf-8") as f:
            d = json.load(f)
        return d if isinstance(d, dict) else {}
    except (OSError, ValueError):
        return {}


def save_settings(d):
    try:
        with open(_settings_path(), "w", encoding="utf-8") as f:
            json.dump(d, f)
    except OSError:
        pass



def _exp_autostart(g):
    """Experimental: direkt in den vom Hauptprogramm gewählten Bereich starten (POLYBASH_EXP_SPEC)."""
    try:
        spec = json.loads(os.environ.get("POLYBASH_EXP_SPEC") or "{}")
    except ValueError:
        spec = {}
    if not isinstance(spec, dict):
        spec = {}
    name = str(spec.get("name") or "").strip()[:16]
    if name:
        g.my_name = name
    if not os.path.exists(_settings_path()):          # erster Start: Grafik, Empfindlichkeit, Bildrate übernehmen
        if spec.get("gfx") in GFX_MODES:
            g.gfx = spec["gfx"]
        if spec.get("sens") in SENS_CHOICES:
            g.sens_mult = spec["sens"]
        if spec.get("fps") in FPS_CHOICES:
            g.fps_limit = spec["fps"]
        g.apply_fps()
    do = spec.get("do")
    if do == "host":
        cfg = spec.get("cfg") if isinstance(spec.get("cfg"), dict) else {}
        for k in ("mode", "limit", "mobs", "cd", "regen", "resp", "map"):
            if k in cfg:
                g.cfg[k] = cfg[k]
        if g.cfg.get("mode") not in ("koth", "dm"):
            g.cfg["mode"] = "koth"
        g.start_game("host")
    elif do == "join":
        g.show_menu("join")


if __name__ == "__main__":
    if sys.stdout is None:   # Windows ohne Konsole
        sys.stdout = sys.stderr = open(os.devnull, "w")
    try:
        _g = Game()
        _exp_autostart(_g)
        _g.run()
    except KeyboardInterrupt:
        sys.exit(0)
    except Exception:                      # Absturz: Ursache in eine Datei schreiben
        import traceback
        try:
            with open(_log_path(), "a", encoding="utf-8") as f:
                f.write(time.strftime("%Y-%m-%d %H:%M:%S") + "\n" + traceback.format_exc() + "\n")
        except OSError:
            pass
        raise
