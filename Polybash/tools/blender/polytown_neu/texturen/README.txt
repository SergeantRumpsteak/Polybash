Texturen fuer die Karte (Poly Haven o. ae., CC0)

Jeder Texturensatz kommt in einen eigenen Unterordner. Das Skript erkennt die Dateien am Namen (Poly-Haven-Schema):
  <name>_diff_2k.jpg      Farbe
  <name>_nor_gl_2k.png    Normal-Map (OpenGL)  - nicht die "dx"-Variante
  <name>_rough_2k.jpg     Rauheit
  <name>_ao_2k.jpg        Ambient Occlusion (optional)
  <name>_arm_2k.jpg       AO/Rauheit/Metall in einer Datei (wird benutzt, falls ao/rough fehlen)
Displacement/Height wird nicht benutzt. Pro Ordner nur EINE Aufloesung ablegen (2k reicht).

Aktuell erwartet:
  festung_boden/ -> Materialien "Hof" (Pflaster) und "Stufen" (nur Boden, nicht die Waende)

Zuordnung und Kachelgroesse (Meter je Wiederholung) stehen in texturen.py (TEXTUREN).
Fehlt ein Ordner, bleibt das Material einfarbig.
  festung_wand/  -> Materialien "Mauerwerk" und "Mauerwerk dunkel" (Mauern, Tuerme, Wachhaeuser, Wehrgang)
  festung_treppe/      -> Material "Stufen" (Trittbleche, Wangen, Podest der Feuerwehrtreppen); auch <name>_metal_2k wird erkannt
  festung_treppenseule/-> Material "Treppensaeule" (Stuetzsaeulen unter den Treppen); solange der Ordner leer ist, bleibt die Saeule einfarbig
