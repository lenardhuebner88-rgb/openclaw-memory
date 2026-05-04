# Pixel UI Tooling Bedarf — Plan für Atlas

Datum: 2026-05-04
Owner: Pixel / frontend-guru
Ziel: UI-Arbeit schneller, prüfbarer und weniger subjektiv machen. Aktuell kann Pixel Screenshots über Canvas erfassen und per JS eval prüfen, aber saubere UI-Qualität braucht bessere Prüf- und Vergleichswerkzeuge.

## Kurzfassung
Pixel benötigt keinen großen Tool-Zoo, sondern drei priorisierte Fähigkeiten:

1. DOM/A11y Inspector
2. Visual Diff / Screenshot Baselines
3. Component Preview / Storybook-ähnliche isolierte Zustände

Danach sinnvoll: Playwright Flow Checks, Design-Token Zugriff, Screenshot History.

## P0 — DOM-/Accessibility-Inspector

### Bedarf
Ein First-Class-Werkzeug, das für eine gerenderte Seite strukturiert ausgibt:
- DOM-Struktur für relevante Bereiche
- computed styles für ausgewählte Elemente
- Accessibility Tree / Rollen / Labels
- Focus-Reihenfolge und Tab-Stops
- Kontrastwerte und Touch-Target-Größen
- erkannte Overflow-/Clipping-Probleme

### Warum
Screenshots zeigen, dass etwas falsch aussieht, aber nicht zuverlässig warum. Für schnelle UI-Fixes braucht Pixel direkte Fakten: welches Element, welche CSS-Regel, welcher Kontrast, welcher Fokuspfad.

### Akzeptanzkriterien
- Tool kann URL + Selector/Viewport annehmen.
- Liefert JSON/Markdown mit DOM, computed styles, a11y findings und Fokuspfad.
- Funktioniert für Desktop und Mobile Viewports.
- Erkennt mindestens: fehlende Labels, zu kleine Touch Targets, niedrigen Kontrast, horizontales Overflow.

## P1 — Visual Diff / Screenshot Baselines

### Bedarf
Automatisierter Vorher/Nachher-Vergleich für Screenshots:
- Desktop + Mobile Viewports
- pro Route/State gespeicherte Baseline
- Pixel-Diff mit Schwellenwert
- Markierung betroffener Bereiche
- Artefakt-Ausgabe als diff image + summary

### Warum
Aktuell ist visuelle Regression manuell. Bei Mission-Control-UI mit vielen Karten, Drawern und Statuszuständen ist das fehleranfällig. Visual Diff macht Layoutänderungen beweisbar.

### Akzeptanzkriterien
- Baseline erfassen: route + viewport + state-name.
- Compare gegen neue Aufnahme.
- Ergebnis enthält Diff-Prozent, Bildartefakt und Liste auffälliger Regionen.
- Threshold konfigurierbar, z. B. 0.1% / 1% / 5%.

## P1 — Component Preview / Storybook-ähnliche Zustände

### Bedarf
Eine isolierte Preview-Schicht für UI-Komponenten mit definierten States:
- loading
- empty
- error
- success
- long text
- many items
- mobile cramped
- operator-needed / stuck / at-risk Statuskarten

### Warum
Viele UI-Probleme entstehen nicht auf der Happy-Path-Seite, sondern in Randzuständen. Pixel braucht schnelle reproduzierbare Komponentenzustände, ohne Live-Daten im Board manipulieren zu müssen.

### Akzeptanzkriterien
- Mindestens Kernkomponenten aus Mission Control isoliert previewbar.
- States sind deterministisch über URL oder Fixture auswählbar.
- Canvas kann direkt Screenshots dieser States machen.
- Keine Mutation von Live-Daten nötig.

## P2 — Browser Flow Checks

### Bedarf
Playwright-artige Checks für echte Interaktion:
- click / hover / keyboard tab
- drawer öffnen/schließen
- dialog appears
- button enabled/disabled states
- route navigation
- mobile resize

### Warum
Screenshots prüfen Optik, aber nicht Bedienbarkeit. Gerade Drawer, Buttons und Dialoge müssen beweisbar funktionieren.

### Akzeptanzkriterien
- Kleine Scripts pro Flow ausführbar.
- Ergebnis: pass/fail + Screenshot bei Fehler.
- Läuft lokal gegen Mission Control.
- Keine destruktiven Aktionen ohne explizite Safe-Mode Guards.

## P2 — Design Token Zugriff

### Bedarf
Zentral abrufbare Design-Fakten:
- Farben
- Typography scale
- spacing scale
- radii/shadows
- breakpoints
- semantic status colors

### Warum
Ohne Token-Quelle entscheidet Pixel optisch nach Gefühl. Das führt zu Drift und uneinheitlichen Fixes.

### Akzeptanzkriterien
- Tokens als JSON/TS exportierbar.
- UI-Komponenten nutzen semantische Tokens statt ad-hoc Werte.
- Tool/Script kann Token-Diff anzeigen.

## P3 — Screenshot History / Gallery

### Bedarf
Eine kleine Galerie der wichtigsten Routen und Komponenten:
- latest desktop/mobile screenshots
- baseline screenshots
- diffs
- Link zu Commit/Task/Datum

### Warum
Hilft Atlas, Pixel und Operator schnell zu sehen, was sich verändert hat, ohne Dateien manuell suchen zu müssen.

### Akzeptanzkriterien
- Automatisch gespeicherte Artefakte unter nachvollziehbarem Pfad.
- Index-Datei oder einfache statische Galerie.
- Pro Eintrag: Route, Viewport, Zeitpunkt, Task-ID optional.

## Empfohlene Umsetzung in Sprints

### Sprint 1 — Proof-of-Value
Owner: Forge + Pixel
- DOM/A11y Inspector als Script oder Tool-Wrapper bauen.
- Visual Diff minimal mit Playwright screenshots + pixelmatch einführen.
- 3 Mission-Control-Routen als Baseline: /kanban, /agents, /automations.

DoD:
- Desktop und Mobile Snapshots möglich.
- Ein absichtlich veränderter Screenshot erzeugt einen brauchbaren Diff.
- Inspector findet mindestens einen Testfall für Fokus, Kontrast oder Touch Target.

### Sprint 2 — Component States
Owner: Pixel
- Preview-Route oder Storybook-Setup für Kernkomponenten.
- Fixtures für Statuskarten, Drawer, Empty/Error/Loading.
- Canvas-Aufnahmen pro State dokumentieren.

DoD:
- Mindestens 8 relevante UI States isoliert prüfbar.
- Keine Live-Datenmutation erforderlich.

### Sprint 3 — CI/Gate Integration
Owner: Forge + Pixel
- Nicht-blockierende Visual-Diff-Reports zunächst als Artefakt.
- Später optional harte Gates nur für stabile Komponenten.
- Screenshot-Gallery/Index erzeugen.

DoD:
- Reports sind reproduzierbar.
- Atlas kann Ergebnis in Task-Verifikation zitieren.

## Anti-Scope
- Keine produktiven Live-Daten mutieren, nur um UI States herzustellen.
- Keine harten Visual-Diff-Gates auf dynamische/live-lastige Seiten im ersten Schritt.
- Kein großes Design-System-Projekt starten, bevor Inspector + Diff funktionieren.
- Keine destruktiven Button-Flows automatisch ausführen.

## Atlas-Auftrag
Bitte daraus Mission-Control-Tasks schneiden:
1. Forge: technische Grundlage für DOM/A11y Inspector + Visual Diff PoV.
2. Pixel: UI-State-Katalog und Component Preview Bedarf konkretisieren/umsetzen.
3. Optional danach: Gallery/CI-Gates.
