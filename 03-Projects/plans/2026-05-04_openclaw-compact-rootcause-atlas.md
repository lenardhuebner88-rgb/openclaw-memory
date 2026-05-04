# OpenClaw /compact Root-Cause - Atlas/Main

Datum: 2026-05-04
Scope: Atlas/main Discord-Lane nach OpenClaw 2026.5.3-beta.4 Stabilisierung
Status: Read-only RCA, keine Mutation in diesem Schritt

## Kurzfazit

`/compact` funktioniert technisch, aber nicht so, wie wir es fuer produktive Atlas-Stabilitaet brauchen.

Der Befehl reduziert eine Session erst auf Anforderung und schreibt einen Compaction-Checkpoint. Er verhindert aber nicht, dass die Discord-Lane direkt danach wieder stark anwächst. In unserem Live-Fall ist das Kernproblem nicht ein komplett defektes `/compact`, sondern eine falsche Betriebssemantik:

- OpenClaw compacted spaet, primär bei Overflow/Timeout oder manueller Anforderung.
- Die produktive Discord-Lane baut pro Turn viel Prompt-Masse auf.
- Die Compaction-Summary ist inhaltlich zu schwach und konserviert im Checkpoint zu viel aktuelle Discord-Metadaten.
- Der Codex-App-Server-Pfad hat eine zweite native Thread-Compaction, die Erfolg melden kann, ohne dass sie als sauberes `tokensAfter`/Session-Store-Reset sichtbar genug ist.
- Nach Timeout/Fallback kann wieder ein `modelOverrideSource=auto` persistieren; `/compact` bereinigt diesen Pin nicht.

## Live-Evidenz

Aktiver Atlas Discord Key:

- sessionKey: `agent:main:discord:channel:1486480128576983070`
- sessionId: `29e5f70f-809f-442d-8f9c-0517500352f9`
- status: `running`
- Modell laut Session nach Fallback: `gpt-5.3-codex`
- `modelOverride`: `gpt-5.3-codex`
- `modelOverrideSource`: `auto`
- `providerOverride`: `openai`
- `cacheRead`: ca. `143232`
- `totalTokens`: ca. `145847`
- `compactionCount`: `1`
- `memoryFlushCompactionCount`: `1`
- `compactionCheckpoints`: `1`

Journal seit Gateway-Restart:

- 13:18 CEST: `[timeout-compaction] LLM timed out with high prompt token usage (82%); attempting compaction`
- 13:19 CEST: `[timeout-compaction] compaction succeeded for openai/gpt-5.5; retrying prompt`
- 14:56 CEST: Atlas Discord `openai/gpt-5.5` timeout nach ca. 600s
- 14:56 CEST: fallback von `openai/gpt-5.5` zu `openai/gpt-5.3-codex`
- 14:56/14:59 CEST: Fallback succeeded, danach Session-Pin auf `gpt-5.3-codex`

Aktive Session-Datei:

- User Messages: 43, ca. 153 KB JSONL
- Assistant Messages: 43, ca. 82 KB JSONL
- Compaction Entry: 1, ca. 5.7 KB
- Grobe Conversation-Metadata in User Messages: ca. 27 KB
- Mehrere grosse inbound Text-Attachments/Reports zwischen ca. 6-10 KB pro Eintrag

## Was /compact im Code tut

Discord/OpenClaw Slash Command:

- Datei: `/home/piet/.npm-global/lib/node_modules/openclaw/dist/commands-handlers.runtime-CTIVsAkM.js`
- Relevante Stelle: `handleCompactCommand`
- Der Command:
  - nimmt die aktuelle `params.sessionKey`
  - nutzt `targetSessionEntry.sessionId`
  - abortet ggf. aktiven embedded Run
  - ruft `runtime.compactEmbeddedPiSession(...)`
  - setzt `trigger: "manual"`
  - erhoeht bei Erfolg `compactionCount`
  - schreibt nur eine System-Event-Antwort

Codex-App-Server Pfad:

- Datei: `/home/piet/.openclaw/npm/node_modules/@openclaw/codex/dist/compact-C0_rGlHZ.js`
- `maybeCompactCodexAppServerSession(...)` ruft zuerst die aktive Context-Engine-Compaction auf.
- Danach wird zusaetzlich native Codex-Thread-Compaction gestartet:
  - `client.request("thread/compact/start", { threadId })`
  - Erfolgssignal: `thread/compacted` oder `item/completed` mit `contextCompaction`
- Native Codex-Compaction liefert im Ergebnis aber oft nur `tokensBefore/currentTokenCount`, nicht zwingend ein belastbares `tokensAfter` fuer unseren Session-Store.

## Warum /compact nicht den erwarteten Effekt hat

### 1. /compact ist nicht proaktiv

Automatische Preflight-Compaction triggert erst nahe am Modell-Context-Budget.

Bei Atlas:

- Context Window ca. 272k
- Reserve ca. 16k
- effektiver Preflight-Bereich also grob erst nahe 256k

Unsere Instabilitaet beginnt aber praktisch schon viel frueher, z. B. bei 120k-220k Cache/Total. Das ist fuer OpenClaw noch "passt ins Fenster", fuer den Codex-App-Server/Discord-Hotpath aber bereits latenz- und timeout-anfaellig.

### 2. Timeout-Compaction ist reaktiv

Der Codepfad `timeout-compaction` startet erst nach einem Timeout, wenn die Prompt-Nutzung hoch war.

Das bedeutet:

- Der User merkt den 600s Stall bereits.
- Erst danach wird compacted.
- Danach kann die Fallback-Kette trotzdem einen Auto-Pin setzen.

### 3. Manual /compact bereinigt keine Modell-/Provider-Pins

Der aktuelle Live-Schaden ist nicht nur hohe Tokenzahl, sondern:

- `modelOverrideSource=auto`
- `modelOverride=gpt-5.3-codex`
- `providerOverride=openai`

`/compact` ist kein Session-Store-Repair. Es compacted Transcript/Thread, entfernt aber nicht automatisch Fallback-Pins aus `sessions.json`.

### 4. Recent Turns Preserve ist fuer unsere Discord-Turns zu gross

Config:

- `recentTurnsPreserve=6`

Bei Atlas sind "6 recent turns" nicht klein. Ein Turn enthaelt oft:

- Discord Metadata Blocks
- lange Operator-Prompts
- grosse pasted Reports
- lange Assistant-Reports
- Attachment Text

Dadurch bleibt nach Compaction ein grosser Tail erhalten.

### 5. Die Summary-Qualitaet ist unzureichend

Der aktuelle Compaction-Checkpoint hat:

- `tokensBefore=207546`
- `tokensAfter=21673`
- Summary beginnt mit:
  - `## Decisions`
  - `No prior history.`
  - `## Open TODOs`
  - `None.`

Gleichzeitig enthaelt derselbe Checkpoint im preserved tail sehr viel Discord-Metadaten und operative Guard-Implementierungsdetails.

Das heisst: Die Tokenzahl wurde reduziert, aber die semantische Verdichtung ist nicht gut genug fuer produktive Fortsetzung. Genau dadurch brauchen wir danach wieder viele Kontextdetails im Live-Dialog, und der Cache waechst erneut.

### 6. Discord-Metadaten werden in jeden User-Kontext geschrieben

Quelle:

- `/home/piet/.npm-global/lib/node_modules/openclaw/dist/get-reply-BQ4hxDzS.js`
- `buildInboundMetaSystemPrompt`
- `buildInboundUserContextPrefix`

Jede eingehende Discord-Nachricht bekommt wiederkehrende Metadaten:

- `Conversation info`
- `Sender`
- Channel/Group/Thread/Message IDs
- Sender IDs/Namen
- Reply-/Forward-/Thread-Hinweise

Das ist sicherheitlich nachvollziehbar, aber fuer eine lange Operator-Session ein permanenter Kontext-Multiplikator.

## Root Cause

`/compact` arbeitet als spaete Kompression eines bereits zu gross gewordenen Transcripts. Unser produktives Problem ist aber ein laufender Discord-Hotpath mit hoher Context-Zufuhr pro Turn und einem Stabilitaetsziel deutlich unterhalb des Modell-Context-Limits.

Der Mechanismus ist:

1. Discord Prompt Compiler fuegt pro Nachricht Metadaten + Usertext + Attachments ein.
2. Atlas arbeitet lange in derselben Discord-Session.
3. Cache/Total steigen auf 120k+.
4. OpenClaw compacted noch nicht, weil das Modellfenster nominell gross genug ist.
5. Bei Timeout compacted OpenClaw reaktiv.
6. Fallback kann danach `modelOverrideSource=auto` persistieren.
7. `/compact` reduziert ggf. Transcript, repariert aber nicht Routing-Pins und verhindert kein erneutes schnelles Wachstum.

## Handlungsempfehlung

### Primaerer Fix

Nicht zuerst noch mehr Timeout-Budget oder manuelle `/compact`-Routinen. Stattdessen:

1. Discord Prompt-Metadata slimming:
   - nur minimale Identitaets-/Routingdaten pro Turn
   - lange Group/Sender/Thread-Felder nur bei Bedarf
   - keine wiederholten grossen JSON-Bloecke in jedem User-Turn

2. Atlas-spezifische Compaction-Policy:
   - `recentTurnsPreserve` fuer `main` auf 2-3 senken
   - Compaction-Summary-Instructions fuer operative Wahrheit:
     - aktuelle Entscheidungen
     - offene Tasks
     - relevante IDs
     - aktive Verbote/Stopps
     - Modell-/Routingstatus

3. Low-watermark Stabilitaets-Gate:
   - nach Run-Ende, nicht waehrend `running`
   - wenn `cacheRead > 100000` oder `totalTokens > 120000`: scoped Rotation/Compaction
   - wenn Auto-Pin vorhanden: Pin bereinigen oder Session rotieren

### Sofortiger Betriebszustand

Atlas ist aktuell nicht clean, weil die Discord-Session wieder auf `gpt-5.3-codex` auto-gepinnt ist. Kein Live-Cleanup waehrend `running`; nach Idle-Gate muss scoped nur Atlas repariert/rotiert werden.

## Naechste Pruefschritte

1. Read-only Analyzer fuer aktive Atlas-Session:
   - Metadata Bytes pro User-Turn
   - Attachment/Textdump Bytes
   - Duplicate Attachment Hashes
   - Usage Wachstum pro Run aus Trajectory

2. Danach gezielter Patch-Plan:
   - Prompt-Metadata Slimming im Discord/OpenClaw Prompt Builder
   - agent-lokale Compaction-Policy fuer main
   - systemd/Guard Validierung

3. Erst danach produktive E2E:
   - Atlas neuer Discord-Turn
   - kein Fallback
   - kein Auto-Pin
   - Cache bleibt nach mehreren Turns unter Zielschwelle

