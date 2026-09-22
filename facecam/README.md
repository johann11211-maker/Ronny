# Facecam-Rahmen "AwenHD"

Ein 16:9-Rahmen zum Ueberlegen ueber die Webcam: schwarz-grau gemischter
Rand, unten eine schwarze Leiste mit eingraviertem Schriftzug. Der Schriftzug
leuchtet alle 10 Sekunden langsam hell-orange auf und blendet wieder aus --
die Gravur selbst bleibt dabei immer sichtbar, sodass in der dunklen Phase
der Abdruck im Material stehen bleibt.

Das Video ist eine geschlossene Schleife: der letzte Frame ist Bit fuer Bit
derselbe wie der erste, und beide liegen mitten in der 4,2 Sekunden langen
dunklen Phase. Beim Zuruecksetzen ist also kein Sprung zu sehen.

## Fertige Dateien

Alles unter `out/`:

| Datei | Wofuer |
|---|---|
| `awenhd-facecam-frame.webm` | **Das Overlay.** VP9 verlustfrei mit Alphakanal, 1920×1080, 30 fps, 10 s. Fuer OBS, Streamlabs, Browser. |
| `awenhd-facecam-frame-vorschau.mp4` | Nur zum Anschauen: derselbe Rahmen ueber einem Platzhalter statt der Kamera, ohne Transparenz. |
| `awenhd-facecam-frame-an.png` | Standbild mit voll leuchtendem Schriftzug, mit Alphakanal. |
| `awenhd-facecam-frame-aus.png` | Standbild in der dunklen Phase -- zeigt die Gravur ohne Leuchten. |
| `awenhd-facecam-frame-vorschau-*.png` | Dieselben Standbilder ueber dem Platzhalter-Hintergrund. |

Eine ProRes-4444-Fassung fuer Schnittprogramme erzeugt `--mov`. Sie liegt
nicht im Repository, weil sie rund 400 MB gross ist.

## In OBS einbinden

1. **Quelle hinzufuegen → Medienquelle**, Datei `awenhd-facecam-frame.webm`.
2. **Schleife** anhaken, **Wiedergabe beenden wenn nicht sichtbar** abwaehlen.
3. Die Quelle ueber die Kameraquelle ziehen, beide auf 1920×1080.
4. Die Kamera bildfuellend dahinter legen -- der Rand deckt aussen rund 3 %
   ab, die Leiste unten etwas mehr.

Der Alphakanal bleibt erhalten, es braucht keinen Chroma-Key und keinen
Farbfilter. Falls die Kamera exakt und ohne Beschnitt in die Oeffnung passen
soll, siehe `--side`, `--top` und `--bar` weiter unten.

## Neu erzeugen und anpassen

Gebraucht werden Python 3, `numpy`, `Pillow` und `ffmpeg`:

```bash
pip install numpy pillow imageio-ffmpeg
python3 render_facecam_frame.py --out-dir out
```

Findet das Skript kein `ffmpeg` im Pfad, nutzt es das von `imageio-ffmpeg`
mitgelieferte; `FFMPEG_BINARY` setzt einen eigenen Pfad.

Nuetzliche Schalter:

| Schalter | Standard | Wirkung |
|---|---|---|
| `--text` | `AwenHD` | Schriftzug in der Leiste |
| `--cycle` | `10` | Sekunden pro Durchlauf |
| `--fps` | `30` | Bildrate |
| `--width` / `--height` | `1920` / `1080` | Aussenmass |
| `--side` / `--top` / `--bar` | `34` / `34` / `104` | Randbreiten und Hoehe der Leiste |
| `--text-height` | `0.36` | Versalhoehe, als Anteil der Leistenhoehe |
| `--tracking` | `0.30` | Sperrung zwischen den Buchstaben |
| `--frame-dark` / `--frame-light` | `0.04` / `0.345` | Hell-Dunkel-Spanne des Randes |
| `--bar-dark` / `--bar-light` | `0.016` / `0.098` | dasselbe fuer die schwarze Leiste |
| `--engrave-depth` / `--engrave-catch` | `0.10` / `0.08` | Tiefe und Lichtkante der Gravur |
| `--dark-lead` / `--fade-in` / `--hold` / `--fade-out` | `2.0` / `1.8` / `1.6` / `2.4` | Zeiten des Leucht-Zyklus in Sekunden |
| `--seed` | `7` | anderer Wert = andere Maserung im Rand |
| `--still-only` | | nur Standbilder, keine Videos (schnell zum Ausprobieren) |
| `--webm-crf` | | verlustbehaftet kodieren, z. B. `20` fuer knapp 0,5 MB |

Die Zeiten des Zyklus muessen zusammen in `--cycle` passen; was uebrig
bleibt, ist die dunkle Phase am Ende. Beide dunklen Phasen umschliessen den
Schleifenpunkt, deshalb bleibt die Naht unsichtbar, solange etwas uebrig
bleibt. Das Skript bricht ab, wenn die Phasen laenger sind als der Zyklus.

## Wie es gebaut ist

- **Form**: Aussenkontur und Kamerafenster sind abgerundete Rechtecke, als
  vorzeichenbehaftete Distanzfelder gerechnet. Daraus kommen in einem Zug die
  weichen Kanten, die Abschraegung und der Alphakanal. Gerendert wird mit
  zweifachem Supersampling.
- **Material**: fuenf Oktaven Rauschen, im Kontrast angehoben und mit einem
  diagonalen Verlauf gemischt -- daher die schwarz-graue Maserung. Die untere
  Leiste nutzt dieselbe Struktur in einer deutlich dunkleren Spanne.
- **Licht**: aus dem Hoehenprofil der Abschraegung werden Normalen abgeleitet
  und mit einer Lichtquelle von oben links beleuchtet. Das gibt die helle
  Kante oben und die Schattenkante unten.
- **Gravur**: der Schriftzug wird zweifach versetzt weichgezeichnet und
  voneinander abgezogen. Die obere linke Kante wird abgedunkelt, die untere
  rechte aufgehellt -- so liegt der Zug sichtbar im Material, auch ohne
  Leuchten.
- **Leuchten**: zwei Ebenen, warmes Orange linear und ein heisserer Kern
  quadratisch zur Intensitaet, dazu vier Weichzeichner-Stufen als Schein.
  Beides ist auf die Rahmenflaeche maskiert, damit nichts ins Kamerabild
  blutet. Der Alphakanal bleibt ueber den ganzen Zyklus unveraendert.
- **Blende**: `smootherstep`, also an beiden Enden mit Steigung und Kruemmung
  null. Deshalb setzt das Leuchten weich ein und laeuft weich aus, statt
  sichtbar umzuschalten.

Der Rahmen selbst wird einmal berechnet, pro Frame kommt nur das Leuchten
dazu. Die Frames der dunklen Phase sind identisch und werden nur einmal
erzeugt. Ein kompletter Durchlauf dauert rund 40 Sekunden.
