# Ronny — Bitcoin-Ereignis-Watch

Automatische Benachrichtigung, wenn am Bitcoin-Markt ein Ereignis der Art
eintritt, die in `referenz/Bitcoin-Kurs-Fallbeispiele.pdf` beschrieben wird.

**Keine Anlageberatung.**

## Zeitplan

| Wann | Berlin | UTC (Sommerzeit) | UTC (Winterzeit) |
|---|---|---|---|
| Montag bis Freitag | 19:30 Uhr | `30 17 * * 1-5` | `30 18 * * 1-5` |
| Sonntag | 20:00 Uhr | `0 18 * * 0` | `0 19 * * 0` |

Die Zeitplaene laufen als Routines (Scheduled Triggers). Sie sind in UTC
hinterlegt, deshalb gibt es zwei Varianten. Eine eigene Routine stellt zur
Zeitumstellung um — Naeheres unten.

**Samstag findet keine Pruefung statt.** Die Sonntagspruefung um 20 Uhr
schaut deshalb ueber 48 Stunden zurueck und deckt den Samstag mit ab.

## Was gemeldet wird

Die pruefbaren Kriterien stehen in **[`bitcoin-ereignis-watch.md`](bitcoin-ereignis-watch.md)**.
Kurz gefasst:

- **Kursbewegung:** ± 5 % in 24 h, ± 10 % in 7 Tagen, neues Allzeithoch oder
  52-Wochen-Tief, runde 10.000er-Marke, Angst-und-Gier-Index unter 20 oder
  ueber 80
- **Ereignisse:** die acht Arten aus dem PDF — Pleiten und Hacks, Verbote,
  neue Anlageprodukte, grosse Kaeufer, Zinsen und Geldmenge, weltpolitische
  Schocks, Halving und Angebot, Stimmung und Kredithebel

Ist nichts davon eingetreten, **kommt keine Benachrichtigung**. Kein
"heute nichts"-Signal.

## Schwellen aendern

Alle Schwellen stehen in `bitcoin-ereignis-watch.md`, Teil A und Teil B.
Wer weniger Meldungen will, setzt die Prozentwerte in Teil A hoeher
(z. B. 24 h auf ± 7 %); wer mehr will, entsprechend niedriger. Die Pruefung
liest die Datei bei jedem Lauf neu, eine Aenderung wirkt also sofort.

## Marktdaten pruefen

```bash
scripts/marktdaten.sh
```

Gibt Preis, 24-Stunden- und 7-Tage-Bewegung, Allzeithoch samt Abstand,
Marktkapitalisierung, BTC-Dominanz und den Angst-und-Gier-Index aus.
Braucht nur `curl` und `python3`.

Die Datenquellen (CoinGecko, alternative.me) drosseln haeufige Anfragen.
Das Skript wiederholt darum bis zu viermal mit wachsender Wartezeit und
meldet einen nicht erreichbaren Wert als `n/v`, statt abzubrechen.

## Die drei Routines

| Name | Trigger-ID | Zeitplan |
|---|---|---|
| Bitcoin-Ereignis-Check (Mo-Fr 19:30 Berlin) | `trig_01H3iBaizMRurLuoo2JZU2uH` | `30 17 * * 1-5` |
| Bitcoin-Ereignis-Check (So 20:00 Berlin) | `trig_01Dpym8tMtfhGD3gNYhkvoLf` | `0 18 * * 0` |
| Zeitumstellung auf Winterzeit (einmalig) | `trig_0191yW1GBs7ztU5tgH7BjR9p` | 25.10.2026, 10:00 UTC |

Die Kriterien stecken vollstaendig im Prompt der beiden Pruef-Routines, nicht
in diesem Repository. Sie laufen also auch dann, wenn die Sitzung das Repo
nicht ausgecheckt hat. Liegt `bitcoin-ereignis-watch.md` im Arbeitsverzeichnis,
hat diese Datei Vorrang — so lassen sich Schwellen aendern, ohne den Prompt
anzufassen.

Der Zeitpunkt streut um einige Minuten: der Planer weckt die Sitzung nicht
sekundengenau. In der Praxis kommt die Meldung gegen 19:35 bzw. 20:05.

## Zeitumstellung

Routines laufen nach UTC, Berlin wechselt zweimal im Jahr zwischen CET und
CEST. Eine Routine kann ihren eigenen Zeitplan nicht korrigieren — die
Sitzungen, die sie startet, haben keinen Zugriff auf die Trigger-Verwaltung.

Darum gibt es eine dritte, einmalige Routine: Sie meldet sich am
**25.10.2026** in der urspruenglichen Sitzung, stellt beide Zeitplaene auf
Winterzeit und legt danach denselben Termin fuer die naechste Umstellung an
(**28.03.2027**). So haelt sich die Kette selbst am Laufen.

Falls die Kette einmal reisst, ist es von Hand schnell erledigt — in den
Routine-Einstellungen die Cron-Ausdruecke tauschen:

| | Sommerzeit (CEST) | Winterzeit (CET) |
|---|---|---|
| Mo-Fr 19:30 | `30 17 * * 1-5` | `30 18 * * 1-5` |
| So 20:00 | `0 18 * * 0` | `0 19 * * 0` |

## Aufbau

```
bitcoin-ereignis-watch.md   Meldekriterien — die eigentliche Logik
scripts/marktdaten.sh       Marktdaten-Schnappschuss
referenz/                   Das zugrunde liegende PDF
```
