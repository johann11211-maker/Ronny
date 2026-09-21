# Ronny — Bitcoin-Ereignis-Watch

Automatische Benachrichtigung, wenn am Bitcoin-Markt ein Ereignis der Art
eintritt, die in `referenz/Bitcoin-Kurs-Fallbeispiele.pdf` beschrieben wird.

**Keine Anlageberatung.**

## Zeitplan

| Wann | Berlin | UTC (Sommerzeit) | UTC (Winterzeit) |
|---|---|---|---|
| Montag bis Freitag | 05:30 Uhr | `30 3 * * 1-5` | `30 4 * * 1-5` |
| Sonntag | 05:30 Uhr | `30 3 * * 0` | `30 4 * * 0` |

Die Zeitplaene laufen als Routines (Scheduled Triggers). Sie sind in UTC
hinterlegt, deshalb gibt es zwei Varianten. Eine eigene Routine stellt zur
Zeitumstellung um — Naeheres unten.

**Samstag findet keine Pruefung statt.** Die Sonntagspruefung schaut deshalb
ueber 48 Stunden zurueck: bis Freitagfrueh. Damit ist der letzte Handelstag
der Woche und das ganze Wochenende abgedeckt, ohne Luecke zur Montagspruefung.

Die Pruefung am fruehen Morgen hat eine Folge, die man kennen sollte: Die
wichtigen US-Termine liegen am europaeischen Nachmittag und Abend — ein
Zinsentscheid der Fed um 20 Uhr, US-Inflationsdaten um 14:30 Berliner Zeit.
Diese Ereignisse fallen in das 24-Stunden-Fenster und gehen nicht verloren,
sind bei der Meldung aber schon einige Stunden alt. Dafuer liegt die gesamte
US-Sitzung und die Nacht vollstaendig im Rueckblick, und die Meldung kommt vor
Tagesbeginn.

## Was gemeldet wird

Die pruefbaren Kriterien stehen in **[`bitcoin-ereignis-watch.md`](bitcoin-ereignis-watch.md)**.
Kurz gefasst:

| Teil | Frage | Beispiel |
|---|---|---|
| **A** Kursbewegung | Hat sich der Kurs deutlich bewegt? | ± 5 % in 24 h, ± 10 % in 7 Tagen, neues Allzeithoch, runde 10.000er-Marke |
| **B** Ereignis mit Kurswirkung | Ist etwas geschehen, das den Kurs bewegt hat? | die acht Arten aus dem PDF — Pleiten und Hacks, Verbote, neue Anlageprodukte, grosse Kaeufer, Zinsen, weltpolitische Schocks, Angebot, Kredithebel |
| **C** Ereignis mit offener Kurswirkung | Ist etwas geschehen oder fest terminiert, das den Kurs bewegen *kann*, waehrend er noch stillhaelt? | Zinsentscheid uebermorgen, ablaufende SEC-Frist, vierter Tag ETF-Abfluesse, fallende Hashrate |

**Teil C ist die Frueherkennung.** Er greift, wenn ein Ereignis der acht Arten
vorliegt, der Kurs sich aber um weniger als 3 % bewegt hat (sonntags 4 %).
Solche Meldungen sind mit `[VORLAUF]` gekennzeichnet und nennen die Richtung,
in die der Kurs in vergleichbaren historischen Faellen lief — als Einordnung,
nicht als Prognose.

Die Grenze zu Spekulation ist hart gezogen: Gemeldet wird nur, was
**nachpruefbar geschehen oder fest terminiert** ist. Offen ist allein die
Kursreaktion, nie das Ereignis selbst.

| Geht hinaus | Bleibt draussen |
|---|---|
| „Die Fed entscheidet uebermorgen." | „Analysten erwarten eine Zinserhoehung." |
| „Die SEC-Frist laeuft am Freitag ab." | „Der ETF wird wahrscheinlich zugelassen." |
| „Vierter Tag Abfluesse, zusammen 1,2 Mrd. $." | „Das Geld koennte weiter abfliessen." |

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
| Bitcoin-Ereignis-Check (Mo-Fr 05:30 Berlin) | `trig_01H3iBaizMRurLuoo2JZU2uH` | `30 3 * * 1-5` |
| Bitcoin-Ereignis-Check (So 05:30 Berlin) | `trig_01Dpym8tMtfhGD3gNYhkvoLf` | `30 3 * * 0` |
| Zeitumstellung auf Winterzeit (einmalig) | `trig_0191yW1GBs7ztU5tgH7BjR9p` | 25.10.2026, 10:00 UTC |

Die Kriterien stecken vollstaendig im Prompt der beiden Pruef-Routines, nicht
in diesem Repository. Sie laufen also auch dann, wenn die Sitzung das Repo
nicht ausgecheckt hat. Liegt `bitcoin-ereignis-watch.md` im Arbeitsverzeichnis,
hat diese Datei Vorrang — so lassen sich Schwellen aendern, ohne den Prompt
anzufassen.

Der Zeitpunkt streut um einige Minuten: der Planer weckt die Sitzung nicht
sekundengenau. In der Praxis kommt die Meldung gegen 05:35.

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
| Mo-Fr 05:30 | `30 3 * * 1-5` | `30 4 * * 1-5` |
| So 05:30 | `30 3 * * 0` | `30 4 * * 0` |

## Aufbau

```
bitcoin-ereignis-watch.md   Meldekriterien — die eigentliche Logik
scripts/marktdaten.sh       Marktdaten-Schnappschuss
referenz/                   Das zugrunde liegende PDF
```
