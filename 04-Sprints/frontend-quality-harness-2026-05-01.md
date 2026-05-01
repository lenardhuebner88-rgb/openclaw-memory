---
title: Sprint FE-QA-01 — Frontend Quality Harness
status: planned
owner: Pixel (frontend-guru)
created: 2026-05-01
priority: P2
risk: low
scope: Mission Control Frontend tooling, validation gates, UI quality baseline
---

# Sprint FE-QA-01 — Frontend Quality Harness

## Ziel
Pixel soll für Mission Control Frontend-Arbeit optimaler aufgestellt werden: schneller isoliert bauen, reproduzierbar visuell prüfen, Accessibility/Responsive-Probleme früh finden und UI-Änderungen mit klaren Gates abschließen.

## Ausgangslage im Repo
Geprüft am 2026-05-01:

- Stack vorhanden: Next.js 15, React 18, Tailwind 4, Radix UI, Framer Motion, Recharts.
- Quality-Gates vorhanden: `npm run build`, `npm run typecheck`, `npm run lint`, Vitest, Playwright E2E/Smoke.
- Playwright vorhanden mit E2E-Setup und Fixtures.
- Canvas/Snapshot-Tool im OpenClaw-Runtime-Kontext vorhanden.
- Es gibt viele produktive UI-Komponenten unter `mission-control/src/components`, u. a. Taskboard, V3, Ops, Monitoring, Agents.

## Externe Recherche — Kurzbefund

### Playwright Visual Comparisons
Quelle: Playwright Docs, `https://playwright.dev/docs/test-snapshots`

- Playwright unterstützt native Screenshot-Vergleiche via `expect(page).toHaveScreenshot()`.
- Baselines werden als Golden Screenshots im Repo abgelegt.
- Wichtig: visuelle Tests sind host-/browser-/OS-sensitiv; Baselines müssen in stabiler Umgebung erzeugt und geprüft werden.

Implikation für uns:
- Gut geeignet für 5–8 kritische Mission-Control-Screens.
- Nicht als breite Pixel-Perfektion für alle Seiten starten, sondern gezielt für Taskboard/Modals/Mobile.

### Storybook
Quellen: Storybook Docs + GitHub, `https://storybook.js.org/docs`, `https://github.com/storybookjs/storybook`

- Storybook ist ein isolierter UI-Workshop für Komponenten, Pages, Edge Cases und Dokumentation.
- Unterstützt Next.js/React.
- Hoher Nutzen für wiederkehrende UI-Bausteine und schwer erreichbare States.

Implikation für uns:
- Sinnvoll für `src/components/ui/*` und ausgewählte Taskboard-Komponenten.
- Nicht sofort die ganze App storybooken; erst Button, Badge, Card, StatusPill, Dialog, TaskCard, TaskDetailModal.

### Accessibility / axe-core
Quelle: GitHub, `https://github.com/dequelabs/axe-core`

- axe-core ist etablierter Accessibility-Engine-Standard für automatisierte Web-UI-Prüfung.
- Passt gut in Playwright-basierte E2E-Checks.

Implikation für uns:
- Ein kleines `test:a11y` für Taskboard, Modals und Navigation bringt hohen Wert.
- Muss nicht jeden WCAG-Fall manuell abdecken; automatisierte Checks + manuelle Touch-Target-Prüfung reichen für Sprint 1.

### Lighthouse / Performance
Quelle: GitHub, `https://github.com/GoogleChrome/lighthouse`

- Lighthouse prüft Performance, Accessibility, Best Practices und SEO/PWA-Aspekte.

Implikation für uns:
- Für Mission Control genügt ein internes Performance-/UX-Proof-Script statt SEO-Fokus.
- Ziel: mobile first render, CLS/layout shift, große JS-/Render-Probleme früh erkennen.

### Reddit / Community-Signal
Quelle: Reddit r/reactjs Suchtreffer zu Playwright Visual Regression.

- Community-Schmerzpunkt: visuelle Tests werden schnell flaky durch Cookie-Banner, dynamische Daten, wechselnde Notices, Dates und CI-Umgebung.
- Lokale/Zero-Cloud-Ansätze werden diskutiert, gerade bei regulierten Umgebungen.

Implikation für uns:
- Screenshot-Gates müssen dynamische Bereiche maskieren oder mit stabilen Fixtures laufen.
- Keine Cloud-Abhängigkeit für Baselines als Default.
- E2E-Fixtures sind dafür bereits ein Vorteil.

## Sprint-These
Mission Control braucht nicht zuerst mehr UI-Features, sondern einen kleinen Frontend-Quality-Harness. Danach kann Pixel schneller und sicherer liefern.

## Deliverables

### D1 — UI Audit Script
Ein Script/Package-Script, z. B. `npm run ui:audit`, das lokal in einer sinnvollen Reihenfolge prüft:

1. `npm run typecheck`
2. `npm run lint`
3. Playwright Smoke/E2E relevante UI-Gates
4. optional Visual Snapshot Gate, wenn Baselines existieren

Akzeptanz:
- Ein Befehl liefert klares grün/rot für Frontend-Änderungen.
- Ergebnis ist kurz dokumentiert.

### D2 — Visual Baseline Pack
Playwright Screenshot-Tests für ausgewählte Screens:

- `/taskboard` Desktop 1440x900
- `/taskboard` Mobile 390x844
- Task Detail Modal/Sheet
- New Task Modal
- Ops Dashboard
- Agents/Live Agents View, falls stabil erreichbar

Akzeptanz:
- Tests nutzen stabile Fixtures.
- Dynamische Bereiche werden maskiert oder deterministisch gemacht.
- Baseline-Dateien sind im Repo oder bewusst separat dokumentiert.

### D3 — Accessibility Gate
Playwright + axe-basierte Prüfung für:

- Taskboard initial render
- Task Detail Modal
- New Task Modal
- Navigation/Shell

Akzeptanz:
- Kein kritischer axe-Verstoß auf den geprüften Screens.
- Bekannte Ausnahmen werden dokumentiert, nicht ignoriert.

### D4 — Storybook Minimal Setup
Storybook für erste Komponenten:

- `Button`
- `Badge`
- `Card`
- `StatusPill`
- `Dialog`
- `TaskCard`
- `TaskDetailModal` oder vereinfachter Shell-State

Akzeptanz:
- Storybook startet lokal.
- Mindestens Loading/Empty/Error/Normal/Disabled bzw. relevante States sind für Kernkomponenten sichtbar.
- Keine große App-Abhängigkeit nötig.

### D5 — Design Token & State Matrix
Vault-/Repo-Dokumentation für:

- Farben / Statusfarben
- Spacing / Radius / Shadows
- Typografie
- Breakpoints
- Touch targets
- Component states: loading, empty, error, success, disabled, mobile, dark

Akzeptanz:
- Pixel kann neue UI-Arbeit gegen ein kurzes Referenzdokument prüfen.
- Keine Figma-Abhängigkeit nötig, aber Figma kann später ergänzt werden.

## Nicht-Ziele
- Kein komplettes Redesign von Mission Control.
- Kein vollflächiger Screenshot-Test für jede Route.
- Keine Cloud-Visual-Testing-Abhängigkeit als Pflicht.
- Keine CI-/Deployment-Änderung ohne separaten Forge-Review, falls Infrastruktur betroffen ist.
- Kein Ersatz der bestehenden Playwright-/Vitest-Struktur ohne klaren Grund.

## Empfohlene Reihenfolge

### Phase 1 — Repo-Audit & Harness Design
Owner: Pixel, optional Forge-Review

- bestehende Playwright-Konfiguration prüfen
- stabile Fixture-Daten für UI-Gates bestimmen
- Dateistruktur für Visual/A11y Tests festlegen
- `ui:audit` Zielbefehl definieren

DoD:
- kurzer Implementierungsplan im Repo oder Vault
- kein Code-Umbau ohne klare Zielstruktur

### Phase 2 — Playwright Visual + Mobile Baselines
Owner: Pixel

- Screenshot-Tests für Taskboard Desktop/Mobile
- 1–2 Modalzustände
- Masking/deterministische Daten

DoD:
- `npm run test:e2e` oder dediziertes `test:visual` läuft stabil lokal
- Baselines dokumentiert

### Phase 3 — Accessibility Gate
Owner: Pixel

- axe integrieren
- kritische Screens prüfen
- Findings in kleine UI-Fixes oder Follow-ups trennen

DoD:
- automatisierter A11y-Test vorhanden
- keine kritischen ungelösten Verstöße im Sprint-Scope

### Phase 4 — Storybook Minimal
Owner: Pixel

- Storybook installieren/konfigurieren
- Stories für Kern-UI und TaskCard
- State Matrix sichtbar machen

DoD:
- Storybook startbar
- mindestens 6 Kern-Stories mit relevanten States

### Phase 5 — Dokumentation & Abschluss
Owner: Pixel

- `docs/frontend-quality-harness.md` oder Vault-Spiegel ergänzen
- Abschlussbericht mit Screenshots, Commands und offenen Follow-ups

DoD:
- Pixel kann neue Frontend-Tasks mit reproduzierbarem Gate abschließen

## Risiken und Gegenmaßnahmen

- Flaky Visual Tests durch dynamische Daten → stabile Fixtures, Masking, nur wenige kritische Screens.
- Storybook-Aufwand eskaliert → nur Minimal-Komponenten, keine Vollmigration.
- Accessibility-Findings werden zu groß → kritische Verstöße fixen, Rest als Follow-up.
- Build-/CI-Zeit steigt → Visual/A11y zunächst dedizierte Scripts, nicht sofort Pflicht in jedem Build.

## Aufwandsschätzung

- Phase 1: 0.5 Tag
- Phase 2: 1 Tag
- Phase 3: 0.5–1 Tag
- Phase 4: 1–1.5 Tage
- Phase 5: 0.5 Tag

Gesamt: ca. 3.5–4.5 Arbeitstage, abhängig von Storybook-Reibung und A11y-Findings.

## Entscheidungsempfehlung
Starten als P2-Sprint mit Pixel als Owner.

Erstlieferung sollte nicht „perfekte Design-System-Plattform“ sein, sondern ein pragmatischer Harness:

1. `ui:audit`
2. 5–8 Visual Baselines
3. axe Gate für kritische Screens
4. Storybook Minimal für Kernkomponenten
5. Token-/State-Doku

Damit wird Pixel deutlich besser aufgestellt, ohne das Frontend in Tooling-Arbeit zu versenken.

## Mögliche Board-Tasks

1. `FE-QA-01-T1 Repo-Audit + Harness-Design`
   - Agent: Pixel
   - Priority: P2
   - DoD: Zielstruktur und Scriptspezifikation stehen.

2. `FE-QA-01-T2 Playwright Visual Baselines`
   - Agent: Pixel
   - Priority: P2
   - DoD: Taskboard Desktop/Mobile + Modal Screenshots stabil.

3. `FE-QA-01-T3 Accessibility Gate`
   - Agent: Pixel
   - Priority: P2
   - DoD: axe-basierter Playwright-Test für Kernflows.

4. `FE-QA-01-T4 Storybook Minimal Setup`
   - Agent: Pixel
   - Priority: P2
   - DoD: Kernkomponenten isoliert sichtbar.

5. `FE-QA-01-T5 Token & State Matrix Documentation`
   - Agent: Pixel
   - Priority: P3
   - DoD: Doku nutzbar für künftige UI-Tasks.
