# Südafrika, Oktober 2026

Reisebegleiter für unsere Selbstfahrer-Reise mit einem 4-jährigen Kind:
**4.–26. Oktober 2026, Kapstadt bis Lalibela.**

👉 **[Seite öffnen](https://salsafever21.github.io/southafrica/)**

## Was drin ist

| Reiter | Inhalt |
|---|---|
| **Tagesplan** | Zwei Ansichten: **Liste** (alle 23 Tage untereinander) und **Wochenkalender** (Zeitraster mit farbigen Balken, Abfahrtszeiten und Fahrtdauer). Check-in/out, fixe Buchungen und je ein Vorschlag pro Tag. Das Fenster 12:30–15:00 bleibt für den Mittagsschlaf frei. |
| **Restaurants** | 104 kinderfreundliche Lokale, alle mit Bewertung ab 4,2 (Google bzw. TripAdvisor, Stand 22.08.2026). |
| **Aktivitäten** | 76 Aktivitäten, geprüft auf Eignung für 0- bis 5-Jährige: Dauer, Kinderwagentauglichkeit, Mindestalter, Preis, beste Tageszeit. |
| **Checkliste** | 21 datierte Aufgaben zum Abhaken – dieselben stecken als Termine mit Erinnerung im Kalender. |
| **Infos & Sicherheit** | Notrufnummern, Einreise, Auto & Verkehr, Sicherheit, Strand- und Wildtierregeln, Schlechtwetterideen – auf Deutsch zusammengefasst aus den Reiseunterlagen. |
| **Kalender & Karten** | Abonnierbarer Ferienkalender (`reise.ics`), Ein-Klick-Routen pro Etappe und die Anleitung für den Google-My-Maps-Import. |

### Weitere Funktionen

- **Offline-fähig.** Nach dem ersten Besuch läuft die Seite ohne Internet weiter (Service Worker). Über *Teilen → Zum Home-Bildschirm* wird sie zur App mit eigenem Icon.
- **Heute-Ansicht.** Vor der Reise ein Countdown mit den nächsten offenen Vorbereitungspunkten, während der Reise der aktuelle Tag mit den nächsten Terminen.
- **Bearbeiten.** Termine ausblenden, verschieben, umbenennen, eigene ergänzen; ganze Kategorien per Häkchen abschalten. Daraus lässt sich eine neue `reise.ics` erzeugen.
- **Handschuhfach-Seite.** Ein Klick auf *Drucken* gibt eine A4-Seite mit Notrufnummern, Unterkunftsadressen, Fahrzeiten und Buchungen aus.
- **Sonnenauf- und -untergang** pro Tag und Ort, offline berechnet.
- **Hell / Dunkel / Automatisch** oben rechts umschaltbar.
- **Vollständig responsiv.** Der Kalender zeigt auf breiten Bildschirmen die ganze Woche, auf dem Handy einen Tag – kein seitliches Scrollen.
- **Einstellungen sichern/laden** überträgt Favoriten und Kalenderänderungen zwischen Geräten.

Die Seite passt sich hellem und dunklem Systemdesign an und funktioniert auf dem Handy.

## Ferienkalender abonnieren

```
https://salsafever21.github.io/southafrica/reise.ics
```

Abonnieren statt importieren – dann kommen Änderungen automatisch an. Google Kalender aktualisiert alle 8–24 h, Apple je nach Einstellung stündlich.

- **Google Kalender**: Weitere Kalender **+** → Per URL → Adresse einfügen
- **iPhone/iPad**: Einstellungen → Kalender → Accounts → Andere → Kalenderabo hinzufügen

Enthält: Unterkünfte als mehrtägige Balken, Fahrten mit realistischer Dauer, die festen Buchungen (Erinnerung 30 Min vorher), Check-in/out und die Tagesvorschläge (mit „Idee:" markiert). Zeitzone Africa/Johannesburg.

## Route

| # | Etappe | Datum | Unterkunft |
|---|---|---|---|
| 1 | Kapstadt | 4.–8.10. | Adamsgarth Guesthouse, Hout Bay |
| 2 | Paarl & Winelands | 8.–11.10. | Adara Palmiet Valley Estate |
| 3 | Whale Coast | 11.–14.10. | Rivergate Guest Farm, Stanford |
| 4 | Melozhori & Route 62 | 14.–16.10. | Melozhori Private Game Reserve |
| 5 | Fahrtag an die Garden Route | 16.10. | – |
| 6 | Plettenberg Bay | 16.–20.10. | Emily Moon River Lodge |
| 7 | Sundays River Valley | 20.–23.10. | Woodall Country House & Spa |
| 8 | Lalibela & Gqeberha | 23.–26.10. | Lalibela Mark's Camp |

## Dateien

```
index.html                                   fertige Seite (alles inline, keine Abhängigkeiten)
reise.ics                                    abonnierbarer Ferienkalender (142 Termine)
sw.js                                        Service Worker für den Offline-Betrieb
manifest.webmanifest                         App-Manifest (Home-Bildschirm)
icon-192.png / icon-512.png / icon-maskable.png   App-Icons
data/Suedafrika_Restaurants_und_Aktivitaeten.csv   180 Orte für den Google-My-Maps-Import
data/nur-restaurants.csv                     nur die 104 Restaurants
src/                                         Quelldaten und Generator
robots.txt                                   verhindert Indexierung durch Suchmaschinen
```

## Seite neu bauen

```bash
cd src
python3 build.py     # erzeugt die Restaurant-CSV
python3 gen2.py      # erzeugt index.html und die kombinierte CSV
python3 ics.py ../reise.ics   # erzeugt den Kalender
```

`gen2.py` schreibt auch `sw.js` neu – die Cache-Version darin hängt am Inhalt von `index.html`, damit Besucher nach einem Update nicht auf der alten Fassung sitzenbleiben.

Inhalte ändern: `src/plan.py` (Tagesplan **und** Kalender), `src/akt.py` (Aktivitäten), `src/build.py` (Restaurants), `src/info.py` (Infotexte), `src/prep.py` (Vorbereitungs-Checkliste), `src/tpl.html` (Layout). `src/sun.py` rechnet die Sonnenzeiten, `src/events.py` führt Tagesplan und Kalender zusammen.

Wochenkalender und ICS werden beide aus `src/plan.py` über `src/events.py` erzeugt – eine Zeitangabe dort landet in beiden. Der Kalender wird aus `src/plan.py` erzeugt – eine Änderung dort landet nach dem Push automatisch bei allen, die den Kalender abonniert haben.

## Hinweise

- Bewertungen und Öffnungszeiten sind vom 22.08.2026 und ändern sich. Vor Ort kurz prüfen.
- „Ungeprüft“ heisst: der Ort stammt aus den Reiseunterlagen, ohne belastbare Bewertung.
- `robots.txt` und ein `noindex`-Meta-Tag halten Suchmaschinen fern. Wer den Link hat, kann die Seite trotzdem öffnen.
