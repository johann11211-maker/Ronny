# Bitcoin-Ereignis-Watch — Meldekriterien

Grundlage: `referenz/Bitcoin-Kurs-Fallbeispiele.pdf` (Stand 21.09.2026).
Dieses Dokument uebersetzt die dort beschriebenen Muster in pruefbare Kriterien.

**Keine Anlageberatung.** Die Meldungen beschreiben, was geschehen ist — nicht,
was als Naechstes passiert und erst recht keine Handlungsempfehlung.

---

## Grundregel

Gemeldet wird nur, wenn seit der letzten Pruefung **mindestens ein Kriterium aus
Teil A, Teil B oder Teil C** erfuellt ist. Ist nichts erfuellt, erfolgt **keine
Benachrichtigung** — kein "heute nichts"-Signal, keine Zusammenfassung.

Die drei Teile decken drei verschiedene Faelle ab:

| Teil | Frage |
|---|---|
| A | Hat sich der **Kurs** deutlich bewegt? |
| B | Ist ein **Ereignis** eingetreten, das den Kurs bewegt hat? |
| C | Ist ein Ereignis eingetreten oder fest terminiert, das den Kurs bewegen **kann** — waehrend der Kurs noch stillhaelt? |

Im Zweifel gilt: lieber nicht melden. Eine Meldung, die nichts Neues sagt,
macht die naechste echte Meldung wertlos.

---

## Teil A — Kursbewegung (quantitativ)

Reicht allein schon aus. Zahlen aus `scripts/marktdaten.sh`.

| Kriterium | Schwelle |
|---|---|
| BTC 24-Stunden-Bewegung | **± 5 %** oder mehr |
| BTC 7-Tage-Bewegung | **± 10 %** oder mehr |
| Neues Allzeithoch | jedes |
| Neues 52-Wochen-Tief | jedes |
| Runde Marke durchbrochen | volle 10.000er-Schritte (z. B. 80.000 / 90.000 / 100.000) |
| Angst-und-Gier-Index | **≤ 20** (extreme Angst) oder **≥ 80** (extreme Gier) |
| Gesamter Kryptomarkt | ± 7 % in 24 h |

Das PDF zeigt, warum diese Schwellen sinnvoll sind: Die dokumentierten Einbrueche
lagen bei 11 – 50 %, die Anstiege oft bei 5 – 18 % in 24 – 48 Stunden. Alles
darunter ist normales Rauschen.

---

## Teil B — Ereignisse (qualitativ)

Die acht Ereignisarten aus dem Abschnitt „Muster und Lehren" des PDFs.
Ein Ereignis zaehlt nur, wenn es **neu** ist (seit der letzten Pruefung) und
**Bitcoin direkt oder den Gesamtmarkt** betrifft.

### 1. Pleiten, Hacks und Betrug bei Boersen
*Typische Wirkung laut PDF: Einbrueche 20 – 50 %, Erholung erst nach Monaten oder Jahren.*
- Insolvenz, Zahlungsstopp oder eingefrorene Auszahlungen bei einer Boerse,
  einem Kreditgeber oder einem grossen Krypto-Fonds
- Hack oder Diebstahl ab **100 Mio. USD**
- Zusammenbruch eines Stablecoins oder ernsthafter Verlust der Bindung an den Dollar
- Vorbilder: Mt. Gox 2014, Bitfinex 2016, Terra/Luna und FTX 2022

### 2. Verbote und strengere Regeln
*Typische Wirkung: kurzfristig fallend, oft schnelle Erholung.*
- Handels- oder Mining-Verbot in einem Land mit nennenswertem Marktanteil
- Wichtiges Krypto-Gesetz scheitert oder wird verabschiedet (US-Kongress, EU)
- Grosses Verfahren einer Aufsichtsbehoerde gegen eine bedeutende Boerse
- Vorbilder: China 2013 / 2017 / 2021, Suedkorea 2018, CLARITY Act 2026

### 3. Neue Anlageprodukte und freundliche Regeln
*Typische Wirkung: meist steigend — direkt nach dem Start aber oft „Sell the news".*
- Zulassung oder Ablehnung eines bedeutenden Krypto-ETF
- Neue Freigabe oder Erleichterung durch SEC, CFTC oder eine EU-Behoerde
- Start eines grossen neuen Anlageprodukts auf Bitcoin
- Vorbilder: Futures 2017, Futures-ETF 2021, Spot-ETFs 2024, SEC-Erleichterung 2026

### 4. Grosse Kaeufer und Unternehmen
*Typische Wirkung: steigend beim Einstieg, fallend beim Rueckzug.*
- Zu- oder Abfluesse der Bitcoin-ETFs ab **500 Mio. USD an einem Tag**
- Unternehmenskauf oder -verkauf ab **500 Mio. USD**
- Ein Staat oder Staatsfonds kauft, verkauft oder kuendigt eine Reserve an
- Vorbilder: Tesla 2021, PayPal 2020, ETF-Zufluesse 2024 und 2026

### 5. Zinsen und Geldmenge
*Typische Wirkung: mehr Geld treibt den Kurs, hoehere Zinsen druecken ihn.*
- Zinsentscheid der US-Notenbank oder der EZB
- US-Inflationsdaten (CPI/PCE), die deutlich von der Erwartung abweichen
- Aenderung bei Anleihekaeufen oder -rueckkaeufen, Wechsel der geldpolitischen Richtung
- Deutliche Aeusserung eines Notenbankchefs, die die Zinserwartung verschiebt
- Vorbilder: Corona-Geld 2020, Zinswende 2022, Zinserhoehung September 2026
- **Besonders beachten:** Laut PDF erwarten die Terminmaerkte weitere
  0,75 Prozentpunkte Zinserhoehung binnen sechs Monaten. Jeder Fed-Termin
  ist damit ein Pflichttermin fuer die Pruefung.

### 6. Weltpolitische und wirtschaftliche Schocks
*Typische Wirkung: zuerst Panikverkaeufe, bei Bankenkrisen teils Anstieg.*
- Neue Zoelle, Handelskrieg, Eskalation eines Kriegs
- Bankenkrise oder Zusammenbruch einer bedeutenden Bank
- Einbruch an den Aktienmaerkten (S&P 500 oder Nasdaq ab −3 % an einem Tag)
- Sprung beim Oelpreis oder bei den Anleiherenditen
- Vorbilder: Corona 2020, Yen-Crash 2024, Zoelle 2025, Iran-Krieg 2026, Zypern 2013

### 7. Halving und Angebot
*Typische Wirkung: langfristig steigend, Hoch bisher ein bis zwei Jahre danach.*
- Das naechste Halving wird fuer **2028** erwartet — im Alltag selten relevant
- Trotzdem melden: starker Einbruch der Hashrate, Zusammenbruch eines grossen
  Miners, grosse Bewegung lang ruhender Bestaende

### 8. Stimmung und Kredithebel
*Typische Wirkung: verstaerkt Bewegungen in beide Richtungen.*
- Zwangsliquidationen ab **1 Mrd. USD in 24 Stunden**
- Short Squeeze oder Long Squeeze mit deutlicher Kurswirkung
- Vorbilder: Crash Oktober 2025 (19 Mrd. USD), Short-Squeeze September 2026

---

## Teil C — Ereignisse mit noch offener Kurswirkung

Der wichtigste Teil fuer die Frueherkennung. Hier geht es um Ereignisse, die
**bereits eingetreten oder fest terminiert** sind, bei denen der Kurs aber
**noch nicht reagiert hat**. Das PDF beschreibt genau diese Luecke: „oft ist
eine Nachricht schon im Kurs enthalten, bevor sie offiziell wird" — und
umgekehrt gibt es Nachrichten, die der Markt noch nicht verarbeitet hat.

**Bedingung:** Das Ereignis erfuellt eine der acht Arten aus Teil B, der Kurs
hat sich aber in 24 Stunden um weniger als 3 % bewegt. Bewegt er sich staerker,
greift ohnehin schon Teil A.

**Harte Grenze:** Gemeldet wird nur, was **nachpruefbar geschehen oder fest
terminiert** ist. Offen ist allein die Kursreaktion — niemals das Ereignis
selbst. Vermutungen, Geruechte und Meinungen bleiben draussen (siehe „Nicht
melden").

### C1 — Fest terminierte Termine

Kalenderfakten, kein Raten. Melden, wenn der Termin **in den naechsten
48 Stunden** liegt:

- Zinsentscheid der US-Notenbank oder der EZB, Protokolle, Anhoerungen
- Veroeffentlichung von US-Inflationsdaten (CPI, PCE) und Arbeitsmarktdaten
- Fristen von SEC oder anderen Aufsichtsbehoerden fuer ETF-Entscheidungen
- Abstimmungen ueber Krypto-Gesetze, Gerichtsurteile mit Termin
- Auslaufende Fristen bei Zoellen oder Handelsabkommen
- Grosse Optionsverfalltermine, Quartalszahlen wichtiger Krypto-Unternehmen

### C2 — Beschlossen, aber noch nicht wirksam

- Ein Gesetz oder eine Regel ist verabschiedet, tritt aber spaeter in Kraft
- Eine Uebergangsfrist laeuft ab
- Ein angekuendigter Kauf oder Verkauf ist noch nicht ausgefuehrt
- Eine Boerse oder ein Anbieter hat eine Aenderung angekuendigt

### C3 — Eingetreten, aber noch nicht eingepreist

- Ein Hack oder eine Insolvenz ist gerade gemeldet, der Markt reagiert noch nicht
- ETF-Abfluesse oder -Zufluesse bauen sich ueber mehrere Tage auf
- Eine Bank, ein Kreditgeber oder ein Miner steht erkennbar unter Druck
- Ein Stablecoin weicht leicht, aber anhaltend von seiner Bindung ab
- Eine Aufsichtsbehoerde hat ein Verfahren eroeffnet, ohne Entscheidung

### C4 — Aufziehende Risiken mit belegbaren Zahlen

Nur mit konkreter Zahl und Quelle, nie als Stimmungsbild:

- Anleiherenditen oder Oelpreis mit deutlicher Bewegung (Teil B, Punkt 6)
- Kredithebel baut sich auf: hohe Finanzierungsraten, steigendes Open Interest
- Bestaende auf Boersen verschieben sich auffaellig
- Hashrate faellt spuerbar
- Angst-und-Gier-Index laeuft mehrere Tage in eine Richtung, ohne die
  Extremwerte aus Teil A zu erreichen

### Wiederholungen vermeiden

Die Pruefungen haben kein Gedaechtnis — jeder Lauf startet neu. Damit ein
Termin nicht taeglich gemeldet wird, gilt stateless:

- **C1:** nur melden, wenn der Termin in den naechsten 48 Stunden liegt.
  Das ergibt hoechstens ein bis zwei Hinweise vor dem Termin.
- **C2 bis C4:** nur melden, wenn die Nachricht **innerhalb des Rueckblick-
  fensters** neu aufgekommen ist (24 h werktags, 48 h sonntags) oder wenn sich
  ihr Stand seitdem messbar geaendert hat — etwa Abfluesse, die sich
  fortsetzen, oder eine Abweichung, die groesser wird.

Ein reiner Kalenderhinweis ohne Neuigkeit bleibt **einzeilig**.

### Kennzeichnung

Meldungen aus Teil C werden klar als solche markiert, damit sie nicht mit einer
tatsaechlichen Kursbewegung verwechselt werden:

```
[VORLAUF | Ereignisart] Was steht an oder ist geschehen — mit Datum und Zahl
Stand:        Was der Kurs bisher gemacht hat (meist: keine klare Reaktion)
Moegliche Richtung: nach oben oder nach unten, mit dem Vergleichsfall aus dem
              PDF begruendet — ausdruecklich keine Prognose, sondern die
              Richtung, in die der Kurs in vergleichbaren Faellen lief
Quelle:       Name und Link
```

Die Zeile „Moegliche Richtung" beschreibt ausschliesslich, wie der Kurs in den
historischen Vergleichsfaellen reagiert hat. Sie sagt nicht, was diesmal
passieren wird, und enthaelt nie eine Handlungsempfehlung.

---

## „Buy the rumor, sell the news"

Das PDF widmet diesem Muster einen eigenen Abschnitt. Wenn ein lange erwartetes
Ereignis eintritt und der Kurs **entgegen** der Erwartung reagiert, ist das
ausdruecklich meldenswert — gerade weil es der Intuition widerspricht.

Belege aus dem PDF: Futures Dezember 2017, Coinbase-Boersengang April 2021,
El Salvador September 2021, ETF-Zulassung Januar 2024, Staatsreserve Maerz 2025,
Zinserhoehung September 2026.

---

## Nicht melden

- Kursprognosen, Kursziele und Analystenmeinungen
- „Whale bewegt Coins", ohne erkennbare Kurswirkung
- Routineberichte ohne neue Tatsache
- Ein Ereignis, das bereits in einer frueheren Meldung stand
- Bewegungen unterhalb der Schwellen aus Teil A
- Alles, was nach Werbung oder nach einem bezahlten Beitrag aussieht

**Besonders wichtig seit Teil C.** Die Frueherkennung ist keine Einladung zum
Spekulieren. Der Unterschied:

| Meldenswert (Teil C) | Nicht meldenswert |
|---|---|
| „Die Fed entscheidet uebermorgen ueber den Leitzins." | „Analysten erwarten eine Zinserhoehung." |
| „Die SEC-Frist fuer diesen ETF laeuft am Freitag ab." | „Der ETF wird wahrscheinlich zugelassen." |
| „Die ETFs verzeichnen den vierten Tag in Folge Abfluesse, zusammen 1,2 Mrd. Dollar." | „Das Geld koennte weiter abfliessen." |
| „Die Hashrate ist in zwei Wochen um 15 % gefallen." | „Minern droht Druck." |

Links steht jeweils eine **nachpruefbare Tatsache oder ein Kalendertermin**.
Rechts steht eine Erwartung. Nur die linke Spalte geht hinaus.

---

## Quellen fuer die Pruefung

1. `scripts/marktdaten.sh` — Preis, 24h/7d, Allzeithoch, Marktkapitalisierung,
   Angst-und-Gier-Index (CoinGecko und alternative.me)
2. Websuche zu Bitcoin-Nachrichten der letzten 24 Stunden
   (bei der Sonntagspruefung: der letzten 48 Stunden, also ab Freitagfrueh)
3. Fuer Teil C zusaetzlich: anstehende Termine der naechsten 48 Stunden —
   Sitzungstermine der Notenbanken, Veroeffentlichungstermine von Konjunktur-
   daten, Fristen von Aufsichtsbehoerden, angesetzte Abstimmungen und Urteile
4. Gegenpruefung jeder Meldung an einer **zweiten, unabhaengigen Quelle**,
   bevor sie hinausgeht

Alle Zahlen in US-Dollar.

---

## Form der Meldung

Kurz, deutsch, ohne Vorrede. Pro Ereignis:

```
[Ereignisart] Was ist geschehen — mit Zahl und Datum
Kurswirkung:  Was der Kurs tatsaechlich gemacht hat
Muster:       Vergleichsfall aus dem PDF, falls einer passt
Quelle:       Name und Link
```

Danach eine Zeile mit dem Kursstand: Preis, 24-Stunden-Bewegung, Abstand zum
Allzeithoch.

Das Muster ist eine Einordnung, keine Prognose. Die Formulierung darf nie
nahelegen, was als Naechstes passiert oder was zu tun ist.
