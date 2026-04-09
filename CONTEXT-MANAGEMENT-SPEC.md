# Context Management System — Komplett-Redesign
**Sprint:** 2026-04-09 | **Owner:** Atlas | **Model:** GPT-5.4 (Codex)

---

## Ausgangslage

### Was James gefunden hat (Research)
- **Bestes Pattern:** Hybrid — Files + strukturierte Profiles + leichtgewichtige Embeddings
- **Tiered Memory:** Working → Episodic → Semantic → Archive
- **Extract, don't dump:** Nur wichtige Infos, nicht ganzen Chat
- **Consolidation/Decay:** Regelmäßig aufräumen
- **Importance-aware:** Nicht alles gleich wichtig

### Was der Audit gefunden hat (B1-B8)
- B1: learnings-to-tasks BROKEN
- B2: nightly-self-improvement FAILING
- B3: Learnings-Duplikation (.learnings/ vs memory/learnings.md)
- B4: OPEN-LOOPS.md verwaist
- B5: validate-models keine permanente Speicherung
- B6: short-term-recall.json unbounded growth
- B7: learning-log.json veraltet
- B8: MEMORY.md enthält operative TODOs

---

## Inventory (Stand: 2026-04-09)

### Primary Memory (444KB total in memory/)
- `MEMORY.md` (162L) — Langzeitgedächtnis, langlebige Fakten
- `memory/YYYY-MM-DD.md` (19 files) — Daily Journals
- `memory/learnings.md` (33L) — Rolling Learnings
- `memory/evening-debrief-*.md` (2 files) — Strukturierte Tagesrückblicke
- `memory/GOVERNANCE.md` (42L) — Memory-Layer-Definition
- `memory/readme.md` (59L) — Format-Regeln

### Secondary/Archive
- `memory/.dreams/short-term-recall.json` (124KB) — ⚠️ Problem
- `memory/.dreams/rem-backfill-last.json`
- `.learnings/LEARNINGS.md` — ⚠️ Veraltet
- `.learnings/ERRORS.md` — Aktiv

### Skills
- `skills/evening-debrief/` ✅
- `skills/nightly-self-improvement/` ✅ (broken)
- `skills/self-improving-agent/` ✅
- `skills/blogwatcher/` (neu)
- `skills/github/` (neu)

### Board
- `tasks.json` (1817L, 92KB) — 79 Tasks

---

## Sprint-Ziele

### Ziel 1: Context Loading definieren (WER ladet WAS WANNE)
```
Startup Chain:
  SOUL.md → USER.md → MEMORY.md (heute+gestern) → HEARTBEAT.md

Heartbeat Chain:
  SOUL.md → USER.md → HEARTBEAT.md

Subagent Chain:
  SOUL.md → USER.md → HEARTBEAT.md → (task-specific context)

Regeln:
- HEARTBEAT.md NUR bei Heartbeat-Polling, nicht in normalen Sessions
- MEMORY.md NUR in Main Session laden
- memory/YYYY-MM-DD.md: heute + gestern (max 2 files)
```

### Ziel 2: Tiered Memory Architecture
```
Tier 0 — Working Memory (Kontext)
  Was: Aktuelle Session, aktive Tasks, aktuelle Diskussion
  Wo: Prompt/Context Window
  Lebensdauer: Session

Tier 1 — Episodic Memory (Ereignisse)
  Was: Tages-Journals (memory/YYYY-MM-DD.md)
  Wo: memory/*.md
  Lebensdauer: 14 Tage, dann archivieren
  Wer: evening-debrief (schreibt), agents (append)

Tier 2 — Semantic Memory (Wissen)
  Was: MEMORY.md, GOVERNANCE.md, Entscheidungen
  Wo: workspace/*.md
  Lebensdauer: Permanent bis zur Änderung
  Wer: Atlas (pflegt), Learnings-Pipeline (promoted)

Tier 3 — Archive (Historie)
  Was: Alte memory/YYYY-MM-DD.md (>14 Tage)
  Wo: memory/archive-YYYY-MM-DD.md
  Wer: Automatisch (14-Tage-Rotation)

Tier 4 — Learnings (Muster)
  Was: memory/learnings.md
  Wo: memory/learnings.md
  Lebensdauer: Permanent
  Wer: Alle Agents (schreiben), learnings-to-tasks (liest)
```

### Ziel 3: Learnings Pipeline reparieren
```
Input:  memory/learnings.md + evening-debriefs
Filter: Importance > 7 → Task-Kandidat
Output: Board-Task
Schedule: 06:55 (vor morning-kickoff)

Fallback-Chain:
  Ollama (lokal) → MiniMax (API) → OpenRouter (Fallback)
```

### Ziel 4: Skills integrieren
```
evening-debrief:
  Input: memory/YYYY-MM-DD.md + morning-brief
  Output: memory/evening-debrief-YYYY-MM-DD.md
  Schedule: 21:00

self-improving-agent:
  Error → memory/learnings.md (NICHT .learnings/)
  Correction → memory/learnings.md
  Promotion → MEMORY.md (bei importance)

nightly-self-improvement:
  Input: learnings.md + board + code
  Output: memory/nightly-builds.md
  Schedule: 04:00
```

### Ziel 5: Aufräumen
```
Zu Löschen:
  - .learnings/LEARNINGS.md (veraltet, duplikat)
  - memory/learning-log.json (veraltet)
  - OPEN-LOOPS.md (verwaist)

Zu Archivieren:
  - Alte memory/YYYY-MM-DD.md (>14 Tage)

Zu Schließen:
  - Alle operativen TODOs aus MEMORY.md → Board-Tasks
```

### Ziel 6: memory_search optimieren
```
short-term-recall.json:
  Max-Size: 100KB
  Prune: oldest entries when >100KB
  Retention: 7 days max
```

---

## Deliverables

1. **SPEC.md** — Diese Datei, finalisiert
2. **memory/CONTEXT-MANAGEMENT-PLAN.md** — Detaillierter Implementierungsplan
3. **memory/GOVERNANCE.md** — Aktualisiert mit Tiered Memory
4. **memory/memory-rotation.py** — Automatische Archivierung (14-Tage-Regel)
5. **memory/learnings-cleanup.py** — Learnings dedup
6. **.learnings/LEARNINGS.md** — Gelöscht
7. **memory/OPEN-LOOPS.md** — Archiviert/geschlossen
8. **memory/learning-log.json** — Gelöscht

---

## Nicht in diesem Sprint
- Graph Memory (zweite Ausbaustufe)
- Embeddings/Vector DB (nicht jetzt nötig)
- Neue Skills außer den geplanten
