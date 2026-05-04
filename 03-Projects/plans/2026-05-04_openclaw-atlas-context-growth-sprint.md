# Sprint: Atlas/OpenClaw Context-Growth Root Fix

Datum: 2026-05-04
Owner: Codex
Scope: Atlas/main, spaeter alle produktiven Discord-Agenten
Status: Sprint geplant auf Basis Live-Daten + OpenClaw-Recherche

## Ziel

Nicht weiter nur Symptome absichern, sondern die Ursache fuer hohen `cacheRead`/`totalTokens` und schwache `/compact`-Wirkung beheben.

Leitziel: Stabilitaet vor Kosten.

## Live-Artefakte

- Analyzer Script: `/home/piet/.openclaw/scripts/atlas-context-growth-analyzer.py`
- Analyzer Test: `/home/piet/.openclaw/scripts/tests/test_atlas_context_growth_analyzer.py`
- Live JSON Report: `/home/piet/.openclaw/workspace/logs/atlas-context-growth-analysis-20260504.json`
- Voranalyse `/compact`: `/home/piet/vault/03-Projects/plans/2026-05-04_openclaw-compact-rootcause-atlas.md`

Validation:

- `python3 -m py_compile /home/piet/.openclaw/scripts/atlas-context-growth-analyzer.py`
- `python3 /home/piet/.openclaw/scripts/tests/test_atlas_context_growth_analyzer.py` -> OK
- Live Analyzer gegen Atlas Discord Session ausgefuehrt

## Live-Befund Atlas

Aktive produktive Session:

- sessionKey: `agent:main:discord:channel:1486480128576983070`
- sessionId: `29e5f70f-809f-442d-8f9c-0517500352f9`
- status: `running`
- Modell laut Session: `gpt-5.3-codex`
- `modelOverride`: `gpt-5.3-codex`
- `modelOverrideSource`: `auto`
- `providerOverride`: `openai`
- `cacheRead`: `143232`
- `totalTokens`: `145847`
- `compactionCount`: `1`

Trajectory:

- Runs: `42`
- echte Timeout-Runs: `2`
- echte Aborted-Runs: `2`
- `cacheRead.max`: `220032`
- `cacheRead.median`: `110464`
- `cacheRead.last`: `143232`
- `totalTokens.max`: `223675`
- `totalTokens.median`: `128988`
- `totalTokens.last`: `145857`

Session JSONL:

- lines: `90`
- fileBytes: `240820`
- user message bytes: `152915`
- assistant message bytes: `81564`
- compaction entry bytes: `5731`
- approximierte Metadatenbytes: `132054`
- approximierter Metadatenanteil am JSONL: `54.84%`
- inbound media refs: `12`
- unique media refs: `5`
- wiederholte media refs:
  - `message---2dac34f2...txt` x4
  - vier weitere media text files x2

Kritische Findings:

1. `fallback-session-pin`: `modelOverrideSource=auto`
2. `high-cache-read`: `143232`
3. `high-total-tokens`: `145847`
4. `metadata-growth`: ca. `132054` Bytes / `54.84%`
5. `inbound-media-text-growth`: repeated inbound media refs
6. `timeout-runs`: `2`

## Root Cause

Die OpenClaw-Compaction ist nicht komplett defekt, aber fuer unseren produktiven Discord-Hotpath falsch ausgerichtet.

Mechanismus:

1. Jeder Discord-Turn fuegt grosse Metadatenbloecke ein:
   - `Inbound Context`
   - `Conversation info`
   - `Sender`
   - Reply-/Thread-/Forward-Kontext
2. Operator-Prompts und Bot-Reports enthalten grosse Textdumps/Attachments.
3. Die gleiche Discord-Session bleibt lange aktiv.
4. Prompt-Cache/Context wachsen in kurzer Zeit auf 120k-220k.
5. OpenClaw compacted standardmaessig erst nahe Context-Limit oder nach Timeout.
6. Timeout/Fallback kann `modelOverrideSource=auto` persistieren.
7. `/compact` reduziert ggf. den Kontext, verhindert aber nicht erneutes Wachstum und bereinigt keinen Fallback-Pin.

## OpenClaw-Recherche

Relevante externe Belege:

- OpenClaw Docs `compaction.md`: Auto-compaction laeuft, wenn die Session nahe am Context-Limit ist oder ein Context-Overflow-Fehler kommt; `/compact` erzwingt manuelle Compaction; recent messages bleiben intakt.
- Issue `#29906`: fordert konfigurierbare proactive compaction thresholds, weil aktuelles Verhalten reaktiv ist und erst spaet triggert.
- Issue `#57410`: berichtet, dass `/compact`/Auto-Compaction teilweise eher Reset als sinnvolle Kompression erzeugt und Kontextkontinuitaet verliert.
- Issue `#7477`: beschreibt `safeguard`-Compaction, die bei grossen Contexts schlecht/silent versagt; Workaround dort: frueher triggern, z. B. hoeheres `reserveTokensFloor`.
- Issue `#38233`: dokumentiert Compaction Timeouts in manuellen und automatischen Pfaden.

Abgleich mit Live-Daten:

- Unsere Live-Compaction reduzierte zwar `207546 -> 21673`, aber Summary-Inhalt war schwach: `No prior history`, `Open TODOs None`, waehrend preserved tail wieder grosse Discord-Metadaten enthielt.
- Unser Problem beginnt deutlich vor Modell-Overflow: aktuell `143k/145k`, max `220k/223k`, waehrend OpenClaw mit grossem Context Window spaeter triggert.
- Der aktuelle Schaden ist nicht nur hoher Kontext, sondern auch ein persistenter Auto-Fallback-Pin.

## Sprint-Plan

### Phase 0 - Akut-Gate fuer produktive Stabilitaet

Ziel: Atlas aus dem aktuellen Auto-Fallback-Pin holen, ohne aktive Runs zu stoeren.

Gates:

- Atlas `status != running`
- updatedAt idle > 10 Minuten
- Gateway health live

Aktion:

- scoped nur `agent:main:discord:channel:1486480128576983070` rotieren oder Auto-Pin surgical entfernen.
- Kein unscoped Cleanup.
- Kein JSONL loeschen.

Validation:

- `modelOverride` leer
- `providerOverride` leer
- naechster Atlas-Turn requested/completed `openai/gpt-5.5`
- `cacheRead` niedrig
- keine Timeout-/Fallback-Events

### Phase 1 - Analyzer produktiv machen

Ziel: Context-Wachstum dauerhaft messbar machen.

Umsetzen:

- Analyzer erweitert fuer alle produktiven Discord-Agents:
  - `main`
  - `sre-expert`
  - weitere Agent-IDs aus `openclaw.json`
- Aggregation:
  - top metadata-heavy turns
  - top attachment-heavy turns
  - duplicate media/text refs
  - cache growth per run
  - timeout/fallback correlation

DoD:

- JSON Report pro Agent
- kompakter Markdown Report in Vault
- kein Secret-/Token-Output
- Tests fuer Parser

### Phase 2 - Discord Prompt-Metadata Slimming

Ziel: groesster Root-Hebel. Weniger Prompt-Masse pro Turn.

Live-Begruendung:

- ca. `132054` approximierte Metadata Bytes
- ca. `54.84%` der aktiven Atlas JSONL

Umsetzen:

- Patch/Config im Prompt Builder:
  - pro Turn nur minimale Felder:
    - channel/session
    - message id
    - sender id/label
    - timestamp
  - `group_subject`, `group_space`, `group_channel`, lange Sender-Details nur bei Bedarf
  - Reply/Forward/Thread-Kontext nur wenn wirklich vorhanden
- Sicherheitsanforderung:
  - Untrusted-Metadata-Semantik beibehalten
  - keine Rollen-/Prompt-Injection-Regeln entfernen

Validation:

- neuer Atlas Turn zeigt deutlich kleineren Prompt-Metadata-Anteil
- keine Discord-Routing-Regression
- `/api/discord/send` smoke OK
- Atlas E2E auf gpt-5.5 ohne Fallback

### Phase 3 - Attachment/Textdump Dedupe

Ziel: wiederholte grosse Inbound-Media-Texte nicht mehrfach in den aktiven Kontext tragen.

Live-Begruendung:

- 12 media refs, 5 unique
- ein media file x4, weitere x2

Umsetzen:

- Dedupe nach media path + content hash
- Bei Wiederholung nur:
  - hash
  - kurzer Titel/Preview
  - Pfadreferenz
  - Hinweis "already supplied in this session"

Validation:

- repeated media refs bleiben im Speicher sichtbar, aber nicht mehr voll im Prompt
- grosses pasted report replay erzeugt keinen proportionalen cacheRead-Sprung

### Phase 4 - Stabilitaets-Compaction vor Timeout

Ziel: Low-watermark fuer produktive Discord-Lanes.

Umsetzen:

- Agent-lokal fuer `main`:
  - `recentTurnsPreserve`: `2` oder `3`
  - `reserveTokensFloor`: hoeher als aktuell, damit Compaction frueher triggert
  - ggf. `truncateAfterCompaction: true`
  - `maxActiveTranscriptBytes` mit realistischem Wert
- Guard:
  - nach Run-Ende, nicht waehrend `running`
  - `cacheRead > 100000` oder `totalTokens > 120000` -> scoped rotate/compact recommendation

Validation:

- nach 5 produktiven Atlas-Turns bleibt `cacheRead` unter Zielbereich
- kein Auto-Fallback-Pin
- keine 600s Timeouts

### Phase 5 - Compaction Summary Qualitaet

Ziel: Compaction muss operative Wahrheit retten, nicht nur Token schrumpfen.

Umsetzen:

- Atlas-spezifische `compaction.customInstructions`:
  - aktuelle Entscheidungen
  - offene Tasks
  - exakte IDs
  - aktive Stopps/Verbote
  - Modell-/Routingstatus
  - letzte valide Systemverifikation
- `identifierPolicy` auf streng lassen.
- `maxHistoryShare` ggf. konservativer setzen.

Validation:

- Compaction checkpoint enthaelt echte Decisions/TODOs/IDs
- kein "No prior history" bei nachweislich langer produktiver Session

### Phase 6 - Upstream Evidence Pack

Ziel: Falls lokale Patches notwendig bleiben, upstream-kompatibel dokumentieren.

Inhalt:

- Analyzer JSON
- Log-Auszug 14:56 Timeout/Fallback
- Compaction Checkpoint `207546 -> 21673`, schlechte Summary
- Metadatenanteil 54.84%
- vorgeschlagene Fixes:
  - configurable proactive threshold
  - Discord metadata slimming
  - manual `/compact` should clear/avoid auto fallback pin coupling

## Erste groesste Hebel

Prioritaet 1: Discord Prompt-Metadata Slimming.

Warum: groesster gemessener Anteil und betrifft jeden Turn.

Prioritaet 2: Attachment/Textdump Dedupe.

Warum: wiederholte grosse Reports/Attachments sind klar sichtbar und erzeugen grosse Spruenge.

Prioritaet 3: Low-watermark Stabilitaets-Compaction/Rotation.

Warum: OpenClaw default triggert zu spaet fuer unseren Hotpath.

Prioritaet 4: Compaction Summary Custom Instructions.

Warum: vorhandene Compaction reduziert Tokens, aber bewahrt operative Wahrheit schlecht.

## Stop Conditions

- Keine Rotation waehrend `status=running`.
- Kein unscoped Session-Cleanup.
- Kein Entfernen von Sicherheits-Metadaten ohne Ersatz.
- Kein Gateway-Restart ohne Backup und Post-Health.
- Kein Patch an OpenClaw Bundle ohne versionierte Script-/Drop-in-Dokumentation.

