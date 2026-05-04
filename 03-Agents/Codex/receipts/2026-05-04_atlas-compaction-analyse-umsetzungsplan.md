# Atlas: Compaction-Problem (2026-05-04)

## Kontext
- Kanal: `#atlas-main` (`agent:main:discord:channel:1486480128576983070`)
- Ziel: Verstehen, warum die letzte Atlas-Compaction nicht sauber lief, und ein belastbarer Umsetzungsplan.

## Gesicherte Befunde (Live-Stand)
1. Session ist aktuell in Auto-Fallback-Pin gelandet:
   - `modelOverride="gpt-5.3-codex"`
   - `modelOverrideSource="auto"`
   - `providerOverride="openai"`
2. Token-/Cache-Last ist hoch:
   - `cacheRead=169344`
   - `totalTokens=169598`
3. Compaction wurde für diese Session nicht als erfolgt markiert:
   - `lastCompactionAt=null`
4. Zeitkritische Fehlerkette im Runtime-Pfad ist belegbar:
   - `FailoverError: LLM request timed out` bei ~`300.7s`
   - `candidate_failed requested=openai/gpt-5.5 ... reason=timeout`
   - danach Fallback-Erfolg auf `gpt-5.3-codex` (`candidate_succeeded`)

## Interpretation (Ursache vs. Symptom)
- Das beobachtete Verhalten ist primär **Timeout-/Fallback-getrieben**, nicht „Compaction hat aktiv kaputt gemacht“.
- Der Ablauf deutet auf ein zu knappes/inkonsistentes Budget für lange Runs hin:
  - Inneres Run-/Provider-Timeout ~300s
  - Lane-Limit mit kurzer Grace (effektiv ~330s)
- Ergebnis: Fallback-Kette startet unter Zeitdruck; Session endet im Auto-Override-Pin, während Compaction nicht sauber als abgeschlossen markiert wird (`lastCompactionAt=null`).

## Warum die letzte Compaction „nicht sauber“ wirkte
- Nicht primär wegen fehlerhafter Flush-Anweisung, sondern weil der Run bereits in einer Timeout/Fallback-Kette hing.
- Die Pre-compaction-Flush-Nachricht wurde formal beantwortet (`NO_REPLY`), aber es gab **keinen robusten Abschlussindikator** für eine erfolgreiche, verwertbare Compaction auf Session-Ebene (`lastCompactionAt` blieb `null`).

## Umsetzungsplan (sauber, risikoarm, verifizierbar)

### Phase 1 — Sofortstabilisierung (ohne Risky Changes)
1. Nach jedem Atlas-Run-Ende einmal Stability-Guard live ausführen (nur wenn Session nicht `running`).
2. Danach Dry-Run-Check dokumentieren (`modelOverride*`, `providerOverride`, `cacheRead`, `totalTokens`).
3. Canary-Watcher weiterlaufen lassen, um Timeout-/Fallback-Ketten früh zu sehen.

**Gate A (muss grün):**
- Session ohne `modelOverrideSource=auto`
- Kein aktiver Run gestört
- Keine Writes an `openclaw.json`

### Phase 2 — Timeout-Budget sauber machen (Root Cause)
1. Aktive Runtime-Budgets vereinheitlichen:
   - `agents.defaults.timeoutSeconds`
   - Lane-Grace-Timeout
2. Sicherstellen, dass ein vollständiger Fallback-Versuch inkl. Compaction-Fenster nicht am Lane-Cap abgeschnitten wird.
3. Patch-Drift schließen (Patch muss garantiert im laufenden Bundle-Pfad angewendet sein oder durch stabile Konfiguration ersetzt werden).

**Gate B (muss grün):**
- Keine `FailoverError timeout`-Cluster im 10-Min-Fenster bei normalen Atlas-Läufen
- Kein erneuter Auto-Pin nach 3 aufeinanderfolgenden Atlas-Runs

### Phase 3 — Messbare Verifikation (24h)
1. Pro Run erfassen:
   - `provider latency`
   - `lane duration`
   - `time to first provider call`
   - `fallback depth`
2. Klassifikation pro Incident:
   - Provider-Spike vs. eigener Budget-/Orchestrierungsengpass
3. Entscheidungsmatrix pflegen:
   - `watch`
   - `rotate-after-run`
   - `inspect-compaction`

**Gate C (muss grün):**
- `lastCompactionAt` nicht dauerhaft `null` bei langen Sessions
- Reduktion der Timeout/Fallback-Inzidenz über 24h
- Keine ungeplanten Modell-Pins

## Konkreter nächster Schritt
- Direkt nach Ende des aktuellen Atlas-Runs:
  1. Stability-Guard `--live`
  2. Watcher-Report sichern
  3. Session-Feldwerte (`modelOverride*`, `cacheRead`, `totalTokens`, `lastCompactionAt`) als Vorher/Nachher-Beleg in Receipt ergänzen.
