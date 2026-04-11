# OpenClaw Memory-System — Audit Report
**Datum:** 2026-04-09, 12:35
**Auditor:** James (Researcher)
**Workspace:** huebners

---

## 1. Memory-Dateien Inventar

### 1.1 Primary Memory Files

| Datei | Zweck | Aktiv | Aktuell | Letzte Änderung | Nutzer |
|-------|-------|-------|---------|-----------------|--------|
| `MEMORY.md` | Langzeitgedächtnis: Fakten, Entscheidungen, Routing, Modelle | ✅ Ja | ✅ Ja | 2026-04-09 | Alle Agents (Main Session) |
| `memory/YYYY-MM-DD.md` | Append-only Tagesjournal | ✅ Ja | ✅ Ja (2026-04-09) | täglich | Alle Agents |
| `memory/GOVERNANCE.md` | Memory-Layer-Definition | ✅ Ja | ✅ Ja | 2026-04-01 | Alle (Referenz) |
| `memory/readme.md` | Daily Memory Format-Regeln | ✅ Ja | ✅ Ja | 2026-03-28 | Alle (Referenz) |
| `memory/learnings.md` | Rolling Learnings Log | ✅ Ja | ✅ Ja | 2026-04-09 | nightly-self-improvement, learns-to-tasks |
| `memory/nightly-builds.md` | Nightly Build Protokoll | ✅ Ja | ✅ Ja | 2026-04-09 | nightly-self-improvement |
| `memory/evening-debrief-*.md` | Strukturierte Tagesrückblicke | ✅ Ja | ⚠️ 2026-04-08 (heute fehlt noch) | 2026-04-09 | evening-debrief Cron |

### 1.2 Secondary / Archive Files

| Datei | Zweck | Status |
|-------|-------|--------|
| `.learnings/LEARNINGS.md` | Self-Improving-Agent Learnings | ⚠️ **VERALTET** — nur 1 Eintrag (2026-03-22), dupliziert Inhalt von `memory/learnings.md` |
| `.learnings/ERRORS.md` | Fehlerlog | ✅ Aktiv — wird beschrieben von auto-fix, learns-to-tasks, agents |
| `.learnings/FEATURE_REQUESTS.md` | Feature Requests | ⚠️ Stub (nur Header) |
| `memory/OPEN-LOOPS.md` | Interim offene Punkte | ⚠️ **STALE** — nur 1 Entry (Google Calendar), widerspricht GOVERNANCE |
| `memory/learning-log.json` | Legacy single-entry artifact | ❌ Obsolete |
| `memory/MEMORY-backup-2026-03-30.md` | Backup | 📦 Archiv |
| `memory/dashboard-roadmap.md` | Projektspezifisch | 📦 Sekundär |
| `memory/.dreams/short-term-recall.json` | Memory-Suchindex | ⚠️ **PROBLEMATISCH** — 45KB JSON, wächst unkontrolliert |

### 1.3 Context-Injection Files (AGENTS.md Startup Chain)

| Datei | Wann geladen | Zweck |
|-------|-------------|-------|
| `SOUL.md` | Jede Session (erstes) | Persona, Verhaltensregeln |
| `USER.md` | Jede Session (zweites) | Über den Menschen |
| `memory/YYYY-MM-DD.md` (heute + gestern) | Jede Session (drittes) | Kontext |
| `MEMORY.md` | Nur Main Session | Langzeitgedächtnis |
| `HEARTBEAT.md` | Bei Heartbeat-Polling | Worker-Contract |

---

## 2. Skills Analyse

### 2.1 evening-debrief Skill
**Pfad:** `skills/evening-debrief/SKILL.md`
**Schedule:** Täglich 21:00 (Europe/Berlin)
**Datenquellen:**
- Liest `memory/YYYY-MM-DD.md` (heutiger Tag)
- Sucht Morning Brief (Discord oder ATLAS_BRIEFING Dateien)
**Output:**
- Speichert `memory/evening-debrief-YYYY-MM-DD.md`
- Sendet an `#atlas-main` (1486480128576983070)

**Status:** ✅ Skill existiert und läuft. Debriefs für 2026-04-07 und 2026-04-08 vorhanden.

### 2.2 nightly-self-improvement Skill
**Pfad:** `skills/nightly-self-improvement/SKILL.md`
**Schedule:** Täglich 04:00 (Europe/Berlin)
**Scannt 6 Quellen:**
1. Learnings API + heutige Fehler
2. Board-Hygiene (stale/in-progress >24h)
3. Code-Qualität (Duplikate, Type errors)
4. Config-Hygiene (tote Models, nie gelaufene Jobs)
5. Performance/Kosten
6. Autonomie-Verbesserungen

**Output:**
- Log nach `memory/nightly-builds.md`
- Notification an `#atlas-main`

**Status:** ✅ Läuft, aber **heute failed**:
- Reason: npm run build schlägt fehl weil MC läuft (clean step exit 1)
- Fix: Skill muss MC-Binding erkennen oder Build-Validierung anpassen

### 2.3 self-improving-agent Skill
**Pfad:** `skills/self-improving-agent/SKILL.md`
**Workflow:** Error → ERRORS.md, Correction → LEARNINGS.md, Feature Request → FEATURE_REQUESTS.md
**Promotion:** Learnings → AGENTS.md/SOUL.md/TOOLS.md bei breiter Anwendbarkeit

**Status:** ✅ Skill existiert, aber **PROMOTION FUNKTIONIERT NICHT EFFEKTIV**:
- Viele Learnings in `memory/learnings.md` haben nie den Weg nach MEMORY.md/AGENTS.md gefunden
- Das duale `.learnings/` + `memory/learnings.md` System verwirrt

---

## 3. Cron-Jobs Audit

### 3.1 Memory-relevante Crons (22 total, 18 ON, 4 OFF)

| Cron | Schedule | Agent | Memory-Relevanz | Status |
|------|----------|-------|-----------------|--------|
| evening-debrief | 0 21 * * * | main | ✅ Schreibt evening-debrief-*.md | ⚠️ Wartet auf 21h |
| nightly-self-improvement | 0 4 * * * | main | ✅ Liest learnings.md, schreibt nightly-builds.md | ✅ Läuft |
| learnings-to-tasks | 55 6 * * * | main | ✅ Liest learnings.md + evening-debriefs | ❌ **BROKEN** |
| validate-models | 0 8 * * * | main | ✅ Prüft Modelle | ⚠️ Keine permanente Speicherung |
| json-backup | every 24h | main | ✅ Workspace Backup | ✅ Läuft |
| workspace-backup | 0 2 * * * | main | ✅ Backup | ✅ Läuft |

### 3.2 learnings-to-tasks — CRITICAL FAILURE

**Schedule:** 06:55 (BEFORE evening-debrief 21h des Vortages!)

**Problem Kette:**
```
06:55 Cron startet → liest evening-debriefs (VORTAG!) → liest learnings.md
→ Ollama timeout → Fallback: MINIMAX_API_KEY not set → RuntimeError → FAIL
```

**History:**
- 2026-04-09 05:45: Erster Versuch — Ollama timeout → MINIMAX fallback failed
- 2026-04-09 05:50: Manueller Rerun — MINIMAX_API_KEY not set
- 2026-04-09 06:08: Dritter Versuch — Pipeline ok aber 0 actionables + Discord HTTP 403

**Root Causes:**
1. Ollama timeout (qwen3.5:4b) → kein sauberer Fallback
2. MINIMAX_API_KEY nicht in environment (Key-Lookup aus openclaw.json war temporär broken, jetzt fixed aber ungetestet)
3. Discord HTTP 403 — Channel permissions oder Token

**Timing-Problem:** learns-to-tasks läuft 06:55 aber evening-debrief um 21h. Debriefs von DO sind erst am FR morgen verfügbar. Das ist korrekt aber: Learnings vom DO die um 22h entstehen, werden erst FR 06:55 verarbeitet (~8.5h delay).

### 3.3 nightly-self-improvement — FAILING

**Letzte Runs (aus cron/runs/):**
- 2026-04-09 04:06: Status=failed
  - Reason: npm run build failed (clean step exits 1 when MC running)
  - Files changed: API routes (route.ts, [id]/route.ts) — wurden korrekt implementiert
  - Validation: Manual endpoint check passed, aber build script schlägt fehl

**Impact:** Route hardening wurde implementiert aber nicht deployed (Skill bricht bei build-fail ab)

### 3.4 validate-models — Keine permanente Speicherung

**Schedule:** 08:00 täglich
**Output:** CLI output (stdout) + Discord summary
**Problem:** Keine Ergebnisse in Memory-Dateien. Bei Fehlern nur Discord, bei OK nur Log. Sollte Resultate nach `memory/` oder als Task speichern.

---

## 4. Context Management

### 4.1 HEARTBEAT Loading (laut AGENTS.md)

```
1. SOUL.md
2. USER.md
3. memory/YYYY-MM-DD.md (heute + gestern)
4. MEMORY.md (nur Main Session)
```

**HEARTBEAT.md** selbst wird nur bei Heartbeat-Polling geladen, nicht in normalen Sessions.

### 4.2 memory_search Tool

- Semantische Suche in MEMORY.md + memory/*.md
- Nutzt `memory/.dreams/short-term-recall.json` als Index
- **Problem:** `short-term-recall.json` ist 45KB und wächst
- Keine maximale Größe definiert — potentielll unbounded growth

### 4.3 MEMORY.md vs memory/*.md

| | MEMORY.md | memory/*.md |
|---|---|---|
| **Zweck** | Langzeit, langlebige Fakten | Daily, operativ |
| **Scope** |了整个 System | Pro Tag |
| **Retention** | Permanent | Keep but rotate/archive |
| **Updater** | Agents (manuell nach LRN) | evening-debrief, agents (append) |
| **Leser** | Main Session | Alle Sessions |

**Duplikat-Gefahr:** Wenn ein Learning in `memory/learnings.md` steht UND in MEMORY.md promoted werden sollte, aber nie promoted wird → Information verrottet

### 4.4 HEARTBEAT.md Storage/Retrieval

**HEARTBEAT.md** wird bei Heartbeat-Polling gelesen. Der Inhalt ist der Worker-Contract. Er funktioniert aber:
- State-Machine Regeln sind klar definiert
- 3-State Konsistenz ist dokumentiert
- Race-Prevention Mechanisms vorhanden

**Aber:** HEARTBEAT.md ist ein MONUMENTALES Dokument (1000+ Zeilen) das alle Aspekte des Heartbeats abdeckt. Es fehlt ein dediziertes `HEARTBEAT.md` im workspace das nur die Heartbeat-Logik enthält (statt es in AGENTS.md zu treiben).

---

## 5. Baustellen (Priorisiert)

### 🔴 CRITICAL

#### B1: learnings-to-tasks Pipeline BROKEN
**Severity:** High
**Symptom:** Cron läuft seit 2026-04-09 mehrfach, produziert keine Tasks
**Root Causes:**
1. Ollama timeout → kein sauberer Fallback (broken fallback chain)
2. Discord HTTP 403 bei Erfolg-Posting
3. 0 actionable items aus recent learnings (Pipeline zu strikt oder keine echten Actionables)

**Impact:** Adaptive Learning Loop ist unterbrochen — Learnings werden nicht zu Tasks

#### B2: nightly-self-improvement FAILING (Build-Validierung)
**Severity:** High
**Symptom:** Skill implementiert korrekt aber bricht bei npm run build ab
**Root Cause:** MC läuft als Production Server, `npm run build` clean step erkennt es und exit 1
**Impact:** Code-Änderungen werden nicht deployed, Route hardening liegt brach

### 🟡 MEDIUM

#### B3: Duplikat-Learnings-System (.learnings/ vs memory/learnings.md)
**Severity:** Medium
**Symptom:** Zwei Learnings-Dateien mit unterschiedlichem Inhalt
- `.learnings/LEARNINGS.md`: 1 Eintrag (LRN-20260322-001, veraltet)
- `memory/learnings.md`: 30+ Einträge (aktive Datei)
**Root Cause:** Self-improving-agent Skill nutzt `.learnings/` aber Agents schreiben nach `memory/learnings.md`
**Impact:** Verwirrung, veraltete Promotion-Workflows

#### B4: OPEN-LOOPS.md verwaist
**Severity:** Medium
**Symptom:** 1 Entry (Google Calendar Integration) — seit GOVERNANCE Update veraltet
**Root Cause:** GOVERNANCE empfiehlt offene Punkte ins Board, aber Google Calendar Loop wurde nie migriert
**Impact:** Operative Punkte werden nicht verfolgt

#### B5: validate-models keine permanente Speicherung
**Severity:** Medium
**Symptom:** Model-Validation läuft täglich, Output nur in Discord/stdout
**Root Cause:** Kein Speicher-Pfad für Results
**Impact:** Historische Model-Status nicht nachvollziehbar

### 🟢 LOW

#### B6: short-term-recall.json unbounded growth
**Severity:** Low
**Symptom:** 45KB JSON, keine Max-Size definiert
**Impact:** Performance bei memory_search

#### B7: learning-log.json veraltet
**Severity:** Low
**Symptom:** Single-entry legacy artifact (2026-03-31)
**Impact:** none, aber sollte archiviert/gelöscht werden

#### B8: MEMORY.md ist zu groß
**Severity:** Low
**Symptom:** MEMORY.md enthält operative TODOs (MC Stability, MC Mobile Opt.)
**Root Cause:** GOVERNANCE verbietet operative TODOs in MEMORY.md, aber alte Einträge wurden nicht migriert
**Impact:** MEMORY.md wird unnötig groß, Board nicht genutzt

---

## 6. Redundanzen & Inkonsistenzen

### 6.1 Learnings-Duplikation
```
workspace/.learnings/LEARNINGS.md  ← Self-Improving-Agent Skill Template
workspace/memory/learnings.md      ← tatsächlich genutzt von Agents
```
**Resolution:** `.learnings/` aufräumen, Agents an `memory/learnings.md` festnageln

### 6.2 Evening-Debrief Timing
```
learnings-to-tasks: 06:55 (FR)
evening-debrief: 21:00 (DO)
→ DO Learnings werden FR 06:55 verarbeitet (korrekt, aber 8.5h delay)
```
**Issue:**learnings-to-tasks läuft BEVOR morning-kickoff (07:00). Debrief-Input ist vom Vortag.

### 6.3 3 Learnings-Silos
```
memory/learnings.md      ← Aktive Datei (30+ Einträge)
memory/learnings.md (backup) ← MEMORY-backup-2026-03-30
.learnings/LEARNINGS.md ← Veraltete Kopie (1 Eintrag)
```

---

## 7. Recommendations

### Immediate Fixes (dieser Audit)

1. **learnings-to-tasks.py**: Fallback-Chain reparieren (Ollama→MiniMax sauber), MINIMAX_API_KEY sicherstellen, Discord 403 debuggen
2. **nightly-self-improvement**: Build-Script ändern um MC-running zu tolerieren ODER Validation anpassen
3. **.learnings/LEARNINGS.md**: Inhalt nach memory/learnings.md migrieren, dann löschen

### Short-term (dieser Sprint)

4. **OPEN-LOOPS.md**: Google Calendar Entry → Board-Task oder als "won't do" schließen
5. **MEMORY.md operativen Content**: MC Stability + MC Mobile Opt. → Board-Tasks
6. **validate-models**: Ergebnis-Speicherung nach memory/ implementieren

### Medium-term

7. **short-term-recall.json**: Max-Size Limit definieren (z.B. 100KB), oldest entries prune
8. **learning-log.json**: Archivieren oder löschen
9. **HEARTBEAT.md**: Aus AGENTS.md extrahieren, eigenständiges Dokument
