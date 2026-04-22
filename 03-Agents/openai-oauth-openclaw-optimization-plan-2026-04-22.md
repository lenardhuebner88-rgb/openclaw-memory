# OpenClaw x OpenAI OAuth Optimierungsplan

Datum: 2026-04-22
Status: Planungsstand auf Basis verifizierter lokaler Ist-Lage + aktueller OpenAI/OpenClaw-Dokumentation
Scope: Maximaler Nutzen aus dem bestehenden OpenAI Pro OAuth Setup, saubere Modernisierung des OpenClaw-Stacks, stabile Rollout-Reihenfolge

## 1. Executive Summary

Das System ist nicht "alt", aber es ist inkonsistent modernisiert:

- OpenClaw selbst ist bereits auf `2026.4.21`.
- Die produktiv genutzte Modellstrategie hängt aber noch an einem `2026.4.15`-artigen Setup.
- Das OpenAI Pro OAuth Setup ist vorhanden und gültig.
- Die wichtigsten 2026er OpenAI-/OpenClaw-Vorteile sind technisch verfügbar, werden aber noch nicht konsequent genutzt.

Der größte konkrete Hebel ist nicht "noch ein Update", sondern die Betriebsarchitektur:

- `openai-codex/gpt-5.4` sauber als Primärpfad nutzen
- `openai-codex/gpt-5.4-mini` als ersten echten Arbeits-Fallback etablieren
- Thinking/Reasoning explizit steuern statt implizite Defaults zu tolerieren
- Long-context und schwere Research-Arbeit auf eigene Agent-/Policy-Lane legen
- Bild-/Medien-Funktionen bewusst modernisieren, statt im Codex-Pfad implizit darauf zu hoffen
- Gateway-/Health-/Session-Lage operational sauber ziehen

## 2. Verifizierte Ist-Analyse

### 2.1 Plattform- und Runtime-Stand

Verifiziert über `openclaw --version` und `openclaw status --all` am 2026-04-22:

- OpenClaw: `2026.4.21`
- Node: `22.22.0`
- OS: `linux 6.17.0-20-generic`
- Dashboard-Ziel: `http://127.0.0.1:18789/`
- Gateway-Ziel: `ws://127.0.0.1:18789`

Relevante Befunde:

- CLI sieht den Gateway aktuell als `unreachable (connect EPERM 127.0.0.1:18789)`.
- `systemctl --user` ist in der aktuellen Shell-Konstellation nicht verfügbar.
- Die Service-Lage ist damit operativ nicht sauber observierbar.
- `249` Sessions liegen im System, davon `119` allein auf `main (Atlas)`.

Interpretation:

- Das LLM-/Provider-Setup ist nicht der einzige Engpass.
- Das System braucht neben Modelloptimierung auch eine kleine Ops-Bereinigung.

### 2.2 Auth- und OpenAI-Lage

Verifiziert über `openclaw models status` am 2026-04-22:

- `openai-codex` OAuth ist aktiv
- `openai-codex:default` gültig, Ablauf in `8d`
- `openai-codex:lenardhuebner88@gmail.com` gültig, Ablauf in `3d`
- Zusätzlich ist lokal auch ein `openai` API-Key konfiguriert

Wichtig:

- Der produktive Primärpfad ist OAuth/Codex, nicht der direkte OpenAI-API-Pfad.
- Ein API-Key ist aber zusätzlich vorhanden und kann optional für Spezialfälle genutzt werden.

### 2.3 Modellkonfiguration

Verifiziert in `~/.openclaw/openclaw.json` Backup vom 2026-04-22:

- Globaler Default:
  - Primary: `openai-codex/gpt-5.4`
  - Fallback 1: `openai-codex/gpt-5.4-mini`
  - Fallback 2: `minimax/MiniMax-M2.7-highspeed`
- Allowlist enthält:
  - `openai-codex/gpt-5.4`
  - `openai-codex/gpt-5.4-mini`
  - `openai-codex/gpt-5.4-pro`
  - diverse ältere Codex-Modelle
  - `minimax/MiniMax-M2.7-highspeed`

Aber auf Agent-Ebene ist das inkonsistent:

- `Atlas`:
  - Primary: `openai-codex/gpt-5.4`
  - Fallbacks: `minimax/MiniMax-M2.7-highspeed`, `minimax/MiniMax-M2.7`, `openrouter/auto`
- `Pixel`:
  - Primary: `openai-codex/gpt-5.4`
  - Fallbacks: `minimax/MiniMax-M2.7-highspeed`, `minimax/MiniMax-M2.7`, `openrouter/auto`
- `Forge`:
  - Primary: `openai-codex/gpt-5.3-codex`
- `Spark`:
  - Primary: `openai-codex/gpt-5.3-codex-spark`

Interpretation:

- Das globale Default-Design ist moderner als die tatsächlich genutzten Agent-Overrides.
- Genau dort geht aktuell der Nutzen von `gpt-5.4-mini` verloren.

### 2.4 Thinking, Reasoning, Fast Mode, Context

Aktuell nicht explizit gesetzt:

- kein `thinkingDefault`
- kein `reasoningDefault`
- kein `fastMode`
- kein explizites `transport`
- kein `serviceTier`
- kein `contextTokens` Override für `openai-codex/gpt-5.4`

Folge:

- Das System verlässt sich auf Runtime-Defaults und Mappings, die sich in den letzten OpenClaw-Releases mehrfach geändert haben.
- Das ist unnötig fragil.

### 2.5 Prompt-/Overlay-/Personality-Lage

Positiv:

- `plugins.entries.openai.config.personality = "friendly"` ist gesetzt.

Das ist gut und sollte erhalten bleiben.

### 2.6 Bild-/Medien-Lage

Aktuell:

- Default-Image-Modell ist nicht OpenAI, sondern `openrouter/google/gemini-2.0-flash-001`.
- In OpenClaw `2026.4.21` wurde das gebündelte OpenAI-Bildmodell auf `gpt-image-2` umgestellt.

Wichtig:

- Die Bild-/Medien-Vorteile von OpenAI sind nicht gleichbedeutend mit dem Codex-OAuth-Pfad.
- Wenn OpenAI-Bildgenerierung und moderne OpenAI-Bildfeatures stabil genutzt werden sollen, ist der direkte `openai/*`-Pfad bzw. das dedizierte OpenAI-Image-Provider-Setup die robustere Lane.

### 2.7 Was das Update technisch bereits gebracht hat

Verifiziert im installierten `CHANGELOG.md`:

- `2026.4.20`
  - stärkeres OpenAI GPT-5 Overlay
  - Codex-Responses-Normalisierung
  - Fix für `/backend-api/codex`
  - bessere `/think`-Level-Auflösung
  - korrektes Verhalten bei `/think off`
- `2026.4.21`
  - OpenAI-Bildgeneration standardmäßig auf `gpt-image-2`

Das heißt:

- Der Unterbau ist modern genug.
- Die Konfiguration und Betriebsweise hinken hinterher.

## 3. Soll-Zielbild

### 3.1 Leitprinzip

Das Ziel ist nicht "ein Modell für alles", sondern ein sauberes Mehr-Lane-Setup:

- Lane A: stärkste OAuth-Standardarbeit
- Lane B: günstige, schnelle OAuth-Nebenarbeit
- Lane C: schwere Long-context-/Research-Arbeit
- Lane D: Bild-/Medien-Funktionen
- Lane E: Fallback außerhalb OpenAI nur dann, wenn OpenAI wirklich scheitert

### 3.2 Zielarchitektur

#### Lane A: Hauptpfad

- Modell: `openai-codex/gpt-5.4`
- Einsatz: Hauptagent, komplexe Coding-/Planungs-/Operator-Arbeit
- Thinking: explizit gesteuert, nicht implizit

#### Lane B: günstige OAuth-Arbeit

- Modell: `openai-codex/gpt-5.4-mini`
- Einsatz:
  - erster Fallback
  - schnelle Subtasks
  - Hilfsagenten
  - Routine-Umsetzung

#### Lane C: Heavy Duty / Long Context

- Modell: `openai-codex/gpt-5.4`
- eigener Agent oder eigene Modell-Policy
- höheres `contextTokens`
- höheres Thinking-Level nur dort, nicht global

#### Lane D: OpenAI Bildgenerierung

- Modell: `openai/gpt-image-2`
- getrennt vom Haupt-Chatmodell behandeln
- nicht über Codex-OAuth "mitdenken", sondern bewusst als Feature-Lane konfigurieren

#### Lane E: Nicht-OpenAI Fallback

- MiniMax/OpenRouter bleiben erhalten
- aber erst nach `gpt-5.4-mini`, nicht davor

### 3.3 Zielzustand pro Agent

- `Atlas`
  - Primary: `openai-codex/gpt-5.4`
  - Fallback 1: `openai-codex/gpt-5.4-mini`
  - Fallback 2: `minimax/MiniMax-M2.7-highspeed`
  - Fallback 3: `openrouter/auto`

- `Pixel`
  - Primary: `openai-codex/gpt-5.4`
  - Fallback 1: `openai-codex/gpt-5.4-mini`
  - Fallback 2: `minimax/MiniMax-M2.7-highspeed`
  - Fallback 3: `openrouter/auto`

- `Forge`
  - Primary: `openai-codex/gpt-5.4-mini`
  - Fallback 1: `openai-codex/gpt-5.4`
  - Fallback 2: `minimax/MiniMax-M2.7-highspeed`

- `Spark`
  - Entweder beibehalten als experimentelle Spezial-Lane
  - oder auf `openai-codex/gpt-5.4-mini` umstellen

Empfehlung:

- `gpt-5.3-codex-spark` nicht mehr als zentrale Lane betrachten.
- Nur behalten, wenn es im Alltag nachweislich schneller und stabiler für einen engen Spezialzweck ist.

## 4. Klare Entscheidungen

### 4.1 Was wir bewusst nicht tun

- Nicht sofort auf `openai-codex/gpt-5.4-pro` umstellen
  - dafür gibt es noch offene OpenClaw-Probleme im OAuth-Pfad
- Nicht global `thinking = off`
  - das spart zwar Tokens, nimmt dem System aber genau die Stärken von GPT‑5.4
- Nicht global den Context brutal hochdrehen
  - das verschlechtert Kosten, Latenz und Session-Stabilität

### 4.2 Was wir bewusst tun

- Thinking explizit steuern
- `gpt-5.4-mini` als echte erste Arbeits-Lane nutzen
- OpenAI-Bildfeatures separat modernisieren
- OAuth als Hauptpfad belassen
- optional einen API-Key-Pfad nur ergänzend einsetzen

## 5. Umsetzungsplan

## Phase 0: Backup und Guardrails

Ziel:

- Konfig-Sicherheit vor jedem Umbau

Schritte:

1. Vollbackup von:
   - `~/.openclaw/openclaw.json`
   - `~/.openclaw/agents/*/agent/auth-profiles.json`
   - `~/.openclaw/agents/*/sessions/`
2. Backup-Timestamp im Dateinamen
3. Vorher/Nachher-Diff sichern

Gate:

- Es gibt einen vollständigen Rücksprungpunkt.

## Phase 1: Ops-Basis wieder sauber ziehen

Ziel:

- Gateway-/Service-/Health-Lage operational klar machen

Schritte:

1. Ursache für `Gateway unreachable (EPERM)` klären
2. User-systemd bzw. Service-Steuerung verifizieren
3. `openclaw status`, `openclaw models status`, `openclaw health --verbose` auf grün bringen
4. Prüfen, ob Gateway wirklich läuft, aber nur aus der aktuellen Shell nicht erreichbar ist
5. Logs auf echte OpenAI/Codex-Fehler prüfen, nicht nur auf alte historische Zeilen

Gate:

- `openclaw status --all` meldet Gateway erreichbar
- Health-Snapshot funktioniert

## Phase 2: Modellstrategie konsolidieren

Ziel:

- Globalen und realen Agent-Zustand synchronisieren

Schritte:

1. `Atlas`-Fallbacks auf:
   - `openai-codex/gpt-5.4-mini`
   - `minimax/MiniMax-M2.7-highspeed`
   - `openrouter/auto`
2. `Pixel` identisch umstellen
3. `Forge` modernisieren:
   - bevorzugt `gpt-5.4-mini` statt `gpt-5.3-codex`
4. `Spark` evaluieren:
   - behalten oder durch `gpt-5.4-mini` ersetzen

Gate:

- Kein Kernagent fällt mehr vor `gpt-5.4-mini` auf Fremdprovider zurück.

## Phase 3: Thinking- und Reasoning-Policy explizit machen

Ziel:

- Keine impliziten Defaults mehr

Empfohlene Zielwerte:

- `thinkingDefault: "low"` für Atlas/Pixel
- `reasoningDefault: "off"` global
- optional für Heavy-Research-Agent:
  - `thinkingDefault: "medium"`

Begründung:

- `low` nutzt GPT‑5.4 sinnvoll aus
- `reasoningDefault: off` verhindert sichtbare Reasoning-Nachrichten
- Heavy-Reasoning bleibt bewusst auf bestimmte Lanes begrenzt

Gate:

- Keine Überraschungen mehr durch Default-Mapping-Änderungen zwischen Releases

## Phase 4: Context- und Long-Run-Strategie

Ziel:

- GPT‑5.4-Long-Context bewusst und kontrolliert nutzen

Empfehlung:

- Standard-Lane bleibt konservativ
- separater Heavy-Agent mit erhöhtem `contextTokens`

Startwerte:

- Standard Atlas/Pixel:
  - kein aggressiver Raise
- Heavy-Agent:
  - `contextTokens` testweise auf `320000` oder `384000`
  - nur für echte Langläufer

Gate:

- Keine globale Kosten-/Latenzexplosion
- Long-context nur dort, wo es realen Nutzen bringt

## Phase 5: OAuth optimal nutzen

Ziel:

- Maximaler Nutzen aus dem `200 €` Pro-Plan

Schritte:

1. `gpt-5.4` als Flaggschiff-Lane
2. `gpt-5.4-mini` für billigeres Scale-out
3. `/fast` nur gezielt einsetzen
4. `gpt-5.4-pro` vorerst nicht in produktive Hauptpfade nehmen
5. Tokenablauf-Monitoring aktiv nutzen

Operative Policy:

- Komplexe Arbeit: `gpt-5.4`
- Routine/Subtasks: `gpt-5.4-mini`
- Externer Fallback erst danach

## Phase 6: OpenAI-Bild-/Medien-Lane modernisieren

Ziel:

- Neues OpenAI-Bildmodell real nutzbar machen

Ist:

- Default-Image-Lane läuft aktuell nicht über OpenAI

Soll:

- dedizierte OpenAI-Image-Lane auf `openai/gpt-image-2`

Hinweis:

- Das ist kein reines OAuth-Thema.
- Für stabile OpenAI-Bildfeatures sollte die direkte OpenAI-Provider-Lane bewusst genutzt werden.

Umsetzung:

1. `imageModel.primary` auf OpenAI umstellen, wenn API-Key-Lane erlaubt ist
2. Failover bewusst definieren
3. Testen:
   - einfache Generierung
   - Edit/Referenzbild
   - Logging bei Provider-Fallback

Gate:

- OpenAI-Bildgeneration läuft bewusst, nicht versehentlich

## Phase 7: Optionaler Hybrid-Pfad mit OpenAI API

Ziel:

- Vorteile ergänzen, die Codex-OAuth allein nicht sauber abdeckt

Nur optional, aber stark empfohlen, weil lokal bereits ein OpenAI-API-Key vorhanden ist:

- `openai/gpt-5.4`
- `openai/gpt-5.4-mini`
- `openai/gpt-5.4-nano`
- `openai/gpt-image-2`

Nutzen:

- Responses-native Features
- klare API-Lane
- kompaktere Automations-/Cron-/Batch-Strategien
- bessere Trennung zwischen "Pro-OAuth Arbeit" und "API-gestützte Spezialläufe"

Wichtig:

- Wenn dieser Pfad aktiviert wird, muss die Allowlist erweitert werden.

## Phase 8: Session- und Wartungsstrategie

Ziel:

- Sessionmasse und Compaction sauber beherrschen

Ist:

- Sehr hohe Session-Anzahl

Schritte:

1. Session-Archivierungsstrategie prüfen
2. `sessions.json`-Größen und Ladezeiten prüfen
3. Alte Sessions gezielt aus dem Hot-Set herausnehmen
4. Compaction-/Maintenance-Verhalten nach Umbau beobachten

Gate:

- Kein unnötiger Druck auf Gateway-Start und Session-I/O

## Phase 9: Validierungsmatrix

Nach Umsetzung müssen diese Tests grün sein:

1. Modellrouting
   - Atlas nutzt `openai-codex/gpt-5.4`
   - Ausfall testet sauber auf `gpt-5.4-mini`

2. Thinking
   - Standardturn ohne sichtbare Reasoning-Nachrichten
   - `/think low`, `/think medium`, `/think off` verhalten sich korrekt

3. Fast mode
   - `/fast on` und `/fast off` funktionieren sauber

4. Long-context
   - Heavy-Agent kann längere Kontexte fahren, ohne Standardpfad zu belasten

5. Bilder
   - OpenAI-Bildgenerierung testweise mit `gpt-image-2`

6. Ops
   - `openclaw status --all`
   - `openclaw models status`
   - `openclaw health --verbose`
   - alle ohne rote Kernfehler

## Phase 10: Rollout-Reihenfolge

Empfohlene Reihenfolge:

1. Backup
2. Gateway-/Health-Basis reparieren
3. Agent-Fallbacks modernisieren
4. Thinking/Reasoning explizit setzen
5. Heavy-Agent für Long-context anlegen
6. Bild-Lane modernisieren
7. Optional API-Hybridlane ergänzen
8. Validierungslauf
9. 48h Beobachtung
10. Erst danach weitere Optimierung

## 6. Konkretes Ziel-Config-Bild

### Pflicht

- `Atlas` und `Pixel` mit `gpt-5.4-mini` als erstem Fallback
- explizites `thinkingDefault`
- explizites `reasoningDefault`
- `friendly` Personality behalten
- Health/Gateway wieder grün

### Stark empfohlen

- Heavy-Agent mit eigener Context-Policy
- `gpt-image-2` als moderne OpenAI-Image-Lane
- optional `openai/*`-Allowlist ergänzen

### Vorerst nicht produktiv priorisieren

- `openai-codex/gpt-5.4-pro`

## 6.1 Konkretes Config-Update

Ja: Die Config-Aktualisierung ist integraler Teil des Plans.

Wichtig ist die Unterscheidung:

- Der Plan enthält bereits die inhaltlichen Config-Ziele.
- Diese Sektion übersetzt sie jetzt in konkrete `openclaw.json`-Änderungen.
- Sie ist bewusst noch kein "blind ausrollen"-Patch, sondern die freizugebende Zielkonfiguration.

### A. Globaler Modellpfad

Aktueller Zustand:

- global bereits gut:
  - primary `openai-codex/gpt-5.4`
  - fallback 1 `openai-codex/gpt-5.4-mini`
  - fallback 2 `minimax/MiniMax-M2.7-highspeed`

Ziel:

- globalen Default im Kern beibehalten
- globale Allowlist aber perspektivisch modernisieren

Konkrete Änderung:

- `agents.defaults.model.primary`
  - bleibt `openai-codex/gpt-5.4`
- `agents.defaults.model.fallbacks`
  - bleibt:
    - `openai-codex/gpt-5.4-mini`
    - `minimax/MiniMax-M2.7-highspeed`

Warum:

- Der globale Default ist bereits richtig.
- Das eigentliche Problem liegt in den Agent-Overrides.

### B. Atlas-Config

Aktueller Zustand:

- `Atlas` fällt aktuell auf MiniMax/OpenRouter zurück, bevor `gpt-5.4-mini` genutzt wird.

Ziel:

- `gpt-5.4-mini` muss erster produktiver Arbeits-Fallback werden.

Konkrete Änderung:

- `agents.list[main].model.primary`
  - bleibt `openai-codex/gpt-5.4`
- `agents.list[main].model.fallbacks`
  - neu:
    - `openai-codex/gpt-5.4-mini`
    - `minimax/MiniMax-M2.7-highspeed`
    - `openrouter/auto`

### C. Pixel-Config

Aktueller Zustand:

- `Pixel` hat denselben Altzustand wie `Atlas`.

Ziel:

- identische OpenAI-zentrierte Priorisierung wie beim Hauptagenten

Konkrete Änderung:

- `agents.list[frontend-guru].model.primary`
  - bleibt `openai-codex/gpt-5.4`
- `agents.list[frontend-guru].model.fallbacks`
  - neu:
    - `openai-codex/gpt-5.4-mini`
    - `minimax/MiniMax-M2.7-highspeed`
    - `openrouter/auto`

### D. Forge-Config

Aktueller Zustand:

- `Forge` läuft noch auf `openai-codex/gpt-5.3-codex`.

Ziel:

- als effizienter SRE-/Ops-Agent modernisiert auf die 5.4-Linie

Empfohlene Änderung:

- `agents.list[sre-expert].model.primary`
  - von `openai-codex/gpt-5.3-codex`
  - auf `openai-codex/gpt-5.4-mini`
- `agents.list[sre-expert].model.fallbacks`
  - neu:
    - `openai-codex/gpt-5.4`
    - `minimax/MiniMax-M2.7-highspeed`
    - `openrouter/auto`

Warum:

- `Forge` ist ein guter Kandidat für die schnellere, günstigere Lane.
- Bei schwereren Fällen kann sauber auf `gpt-5.4` hochgefallen werden.

### E. Spark-Config

Aktueller Zustand:

- `Spark` läuft auf `openai-codex/gpt-5.3-codex-spark`.

Ziel:

- nur behalten, wenn es in einem realen Spezialfall nachweislich besser ist

Planentscheidung:

- kurzfristig: unverändert lassen
- nach Stabilisierung evaluieren:
  - entweder behalten als Spezial-Lane
  - oder umstellen auf `openai-codex/gpt-5.4-mini`

Warum:

- Das ist kein P0-Thema.
- Erst Hauptpfade modernisieren, dann Spezialpfade bereinigen.

### F. Thinking-Defaults

Aktueller Zustand:

- kein explizites `thinkingDefault`

Risiko:

- OpenClaw-Defaults und Provider-Mappings haben sich in den letzten Releases mehrfach verändert.

Ziel:

- deterministisches, nachvollziehbares Verhalten

Konkrete Änderung:

- global:
  - `agents.defaults.thinkingDefault = "low"`
- optional zusätzlich pro Heavy-Agent:
  - `agents.list[<heavy-agent>].thinkingDefault = "medium"`

Warum:

- `low` nutzt GPT‑5.4 sinnvoll, ohne überall maximale Kosten/Latenz auszulösen.
- `medium` gehört nur auf bewusst schwere Research-/Long-Run-Lanes.

### G. Reasoning-Sichtbarkeit

Aktueller Zustand:

- kein explizites `reasoningDefault`

Ziel:

- keine sichtbaren Reasoning-Blöcke für normale Nutzer

Konkrete Änderung:

- global:
  - `agents.defaults.reasoningDefault = "off"`

Warum:

- GPT‑5.4 darf intern denken
- sichtbare Reasoning-Nachrichten sollen aber standardmäßig aus bleiben

### H. OpenAI-Overlay

Aktueller Zustand:

- bereits korrekt gesetzt

Konkrete Entscheidung:

- `plugins.entries.openai.config.personality = "friendly"` bleibt unverändert

Warum:

- Das ist bereits modern und gewünscht.

### I. Modell-Params für GPT-5.4

Aktueller Zustand:

- keine expliziten `params` für `openai-codex/gpt-5.4`

Ziel:

- kritische Dinge, die wir wirklich steuern wollen, explizit machen

Empfohlene Zielkonfiguration:

- `agents.defaults.models["openai-codex/gpt-5.4"].params.transport = "auto"`
- `agents.defaults.models["openai-codex/gpt-5.4"].params.fastMode = false`

Optional später:

- `agents.defaults.models["openai-codex/gpt-5.4"].params.serviceTier = "priority"`
  - nur wenn bewusst gewünscht

Warum:

- `transport: "auto"` entspricht der aktuellen empfohlenen OpenClaw-Strategie
- `fastMode` soll bewusst als Session- oder gezielte Default-Entscheidung genutzt werden, nicht versehentlich

### J. Context-Strategie

Aktueller Zustand:

- kein explizites `contextTokens`-Override

Planentscheidung:

- Standardpfad zunächst unverändert lassen
- nicht global sofort hochziehen

Spätere gezielte Änderung für Heavy-Lane:

- `models.providers["openai-codex"].models[]`
  - Override für `gpt-5.4`
  - `contextTokens` testweise im Bereich `320000` bis `384000`

Wichtig:

- Das ist bewusst Phase 4.
- Kein P0-Config-Change.

### K. Image-Lane

Aktueller Zustand:

- `imageModel.primary` zeigt aktuell auf OpenRouter/Gemini

Planentscheidung:

- nicht im ersten Stabilisierungsschritt umstellen
- danach bewusst entscheiden:
  - OpenAI-Bildlane aktivieren
  - oder Gemini als Bildlane behalten

Wenn OpenAI-Bildlane aktiviert wird:

- `imageModel.primary`
  - auf OpenAI-Bildmodell umstellen
- mit dediziertem Funktionstest absichern

Wichtig:

- Das ist eine bewusste Produktentscheidung, kein Automatismus des OAuth-Upgrades.

### L. Allowlist-Erweiterung für optionalen API-Hybridpfad

Nur falls zusätzlich der direkte OpenAI-API-Pfad aktiv genutzt werden soll:

- in `agents.defaults.models` ergänzen:
  - `openai/gpt-5.4`
  - `openai/gpt-5.4-mini`
  - optional `openai/gpt-5.4-nano`

Warum:

- Sonst blockiert die Allowlist spätere API-Lane-Umschaltungen.

## 6.2 Reihenfolge für das Config-Update

Die Config wird nicht "in einem Wurf" modernisiert, sondern in dieser Reihenfolge:

1. Backup der bestehenden `openclaw.json`
2. `Atlas`-Fallbacks
3. `Pixel`-Fallbacks
4. `thinkingDefault`
5. `reasoningDefault`
6. `Forge`-Modernisierung
7. erst danach optionale Themen:
   - `Spark`
   - `contextTokens`
   - Image-Lane
   - API-Hybridlane

## 6.3 Was im ersten Config-Sprint explizit nicht geändert wird

- kein produktiver Wechsel auf `openai-codex/gpt-5.4-pro`
- kein global aggressives `contextTokens`-Raise
- keine sofortige Umstellung der Image-Lane
- keine gleichzeitige Einführung aller `openai/*` API-Modelle

Warum:

- Erst Stabilität und saubere Lane-Trennung
- dann Ausbau

## 7. Priorisierung

### P0

- Gateway-/Health-Lage reparieren
- Agent-Fallbacks auf `gpt-5.4-mini` modernisieren
- Thinking/Reasoning explizit setzen

### P1

- Long-context-Heavy-Agent
- Session-/Maintenance-Bereinigung
- Bild-Lane auf `gpt-image-2`

### P2

- Hybridlane mit `openai/*`
- Spark-Rolle neu bewerten
- weitere Kosten-/Latenzfeinsteuerung

## 8. Ergebnisbild nach Umsetzung

Wenn der Plan sauber umgesetzt ist, sieht das Soll-System so aus:

- stabiler OpenClaw-`2026.4.21`-Betrieb
- Pro-OAuth maximal genutzt
- `gpt-5.4` als Qualitätsanker
- `gpt-5.4-mini` als günstige Arbeits-Lane
- explizite Thinking-Policy
- bewusste Long-context-Lane
- moderne OpenAI-Bildgeneration
- saubere Health-/Ops-Sicht
- weniger implizite Magie, mehr kontrollierte Architektur

## 9. Nächster sinnvoller Arbeitsschritt

Nicht direkt alles auf einmal umbauen.

Empfohlener nächster konkreter Sprint:

1. Phase 0
2. Phase 1
3. Phase 2
4. Phase 3

Erst wenn diese vier Phasen grün sind:

5. Phase 4
6. Phase 6
7. optional Phase 7
