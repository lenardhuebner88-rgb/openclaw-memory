---
title: "2026-05-05 S-Context — Session/Context Management auf die nächste Stufe"
date: 2026-05-05
status: active-partial-dispatch
owner: Atlas
priority: P0
---

# Sprint: S-Context — Session/Context Management next level

## Ziel
Unser Session/Context-Management systematisch härten: QMD-Sync aktivieren, L2-Sweep reaktivieren, Bootstrap-Budget einhalten, Compaction smarter machen, Session-Hygiene sicherstellen.

## Warum P0
Live-Check 2026-05-05 19:35: MC ist gesund (`/api/health`: open=0, failed=0, issues=0); Sprint-Board hat 9 S-Context-Drafts, davon 5 Duplikate. QMD Session-Start-Sync ist live deaktiviert (`agents.defaults.memorySearch.sync.onSessionStart=false`). Aktueller Atlas-Bootstrap liegt bei 18.654 Bytes und damit ueber dem 16-KB-Ziel. L2-Working hat live 36 Dateien und 0 Dateien aelter als 14 Tage; der alte Claim "186 Transcripts / 137 MB wachsen ungebremst" ist fuer den aktuellen Live-Befund nicht belegt und wird aus dem P0-Argument entfernt.

## Anti-Scope
- Keine Änderungen an Mission-Control Code
- Keine Änderungen an Provider/Model-Routing
- Keine destruktiven Operationen ohne explizite Verify-After-Write

---

## Current Dispatch Decision — 2026-05-05

Operator approved T1 + T2 for execution. Atlas dispatched:

- T1 `a633ff1e-c2b6-4029-9e37-3e88d32a2770` → Forge / `sre-expert`, `pending-pickup`
- T2 `b0da1870-18f5-4b12-844a-55c99bcb1f8d` → Atlas / `main`, `pending-pickup`

T3/T4 remain held for plan refinement. T3 is not an implementation task right now because live data shows 0 Working files older than 14d. T4 is useful only as a measured pilot with rollback criteria, not as a guaranteed root fix.

## Clean Execution Plan

### Phase 1 — Approved P0 execution
1. **T2 Bootstrap budget first**
   - Measure section sizes of the session-start cache output.
   - Trim the smallest high-noise source until Atlas bootstrap is ≤16 KB.
   - Preserve operational usefulness; do not remove human-critical handoff context blindly.
2. **T1 QMD session-start sync**
   - Enable `agents.defaults.memorySearch.sync.onSessionStart=true` safely.
   - Verify QMD session-start update/warmup and first Memory Search against current Vault content.
   - Confirm Gateway/MC health stays ok.

### Phase 2 — Refine, do not dispatch yet
3. **T3 becomes Audit/Monitor only**
   - Check whether sweep automation exists and is healthy.
   - No cron or delete/archive action unless dry-run shows real stale L2 files.
4. **T4 becomes controlled compaction pilot**
   - Compare current context/cache trajectory before change.
   - If changed, use 1 MB for 48h/7d with rollback criteria.
   - Roll back if compaction frequency, continuity loss, or token use worsens.

### Phase 3 — New missing “next-level” work
5. **T9 Discord metadata budget / dedupe design**
   - Root-cause target: repeated inbound context/sender/conversation metadata.
   - Produce a design before implementation.
6. **T10 Session lifecycle policy**
   - Define thresholds for safe rotation/compaction: context, cacheRead, idle time, active lock.
   - Must preserve active Discord operator session safety.

## Tasks

### T1 — QMD OnSessionStart Sync aktivieren ⚡
**Owner:** Forge  
**Estimate:** 15 min (Config) + 10 min Verify  
**Priority:** P0  
**Scope:**
- `agents.defaults.memorySearch.sync.onSessionStart: true` in `openclaw.json`
- Warmup-Call nach Gateway-Restart verifizieren (R55 beachten)
- Test: neue Discord-Session → QMD-Suche liefert Vault-Treffer
**Verify:** Frische Session kann Vault-Wissen ohne manual `memory_search` abrufen

---

### T2 — Bootstrap 16 KB Budget einhalten
**Owner:** Atlas  
**Estimate:** 30 min (Analyse + Config)  
**Priority:** P0  
**Scope:**
- Live-Befund: Cache-Datei `.cache/session-start-vault-context-atlas.md` = 18.654 Bytes; `agents.defaults.bootstrapMaxChars=16000`, `bootstrapTotalMaxChars=42000`.
- Primaer: Auto-Read kuerzen, besonders Daily-/Working-Context Output budgetieren; nicht blind `bootstrapMaxChars` erhoehen.
- Optional: `layer3-vault-bootstrap.py --max-chars` oder Daily-Include gezielt senken, bis Gesamtoutput ≤ 16 KB ist.
- Verifizieren: Bootstrap-Output ≤ 16000 Zeichen
**Verify:** `wc -c .cache/session-start-vault-context-atlas.md` zeigt ≤ 16000

---

### T3 — L2 Auto-Sweep Audit + Monitor (hold)
**Owner:** Forge  
**Estimate:** 45–60 min  
**Priority:** P2 / HOLD  
**Scope:**
- Live-Befund: `memory/working` hat 36 Dateien, davon 0 aelter als 14 Tage. Kein akuter Cleanup-Backlog.
- Nur Scriptaudit/Monitor pruefen; Cron nur anlegen, wenn Sweep wirklich fehlt und Operator freigibt.
- Kein Delete/Archivieren im ersten Schritt; maximal Dry-Run + Report.
- Guard: nie L1 (invariants) oder aktuelle 48h löschen
- Monitoring: `memory-sweep.log` trackt gelöschte Files
**Verify:** Dry-run report zeigt Sweep-Status, aktuelle stale count, geplante Aktion = none unless stale files exist

---

### T4 — `maxActiveTranscriptBytes` kontrollierter Pilot (hold)
**Owner:** Forge  
**Estimate:** 15 min  
**Priority:** P1 / HOLD  
**Scope:**
- Nicht blind senken; zuerst Baseline aus Analyzer + Session-Status dokumentieren.
- Pilot-Vorschlag: `agents.defaults.compaction.maxActiveTranscriptBytes`: 3000000 → 1000000 für 48h/7d.
- Rollback, wenn Compaction-Frequenz, Antwortqualität/Kontinuität oder Tokenverbrauch schlechter werden.
- Effekt-Hypothese: Compaction triggert früher, weniger massiv pro Event; löst aber Discord-Metadatenwachstum nicht ursächlich.
**Verify:** Baseline + Pilot-Metriken + klare Rollback-Entscheidung dokumentiert

---

### T5 — Session-Maintenance Report + OpenAI-Session-Cleanup
**Owner:** Lens  
**Estimate:** 2 h  
**Priority:** P3 (vorerst Analyse-only)  
**Scope:**
- Audit: Wie viele Sessions werden tatsächlich nach 2d gepruned?
- `sessions.json` aufräumen: 12 OpenAI-Sessions prüfen, tote Entries entfernen
- Checkpoints (`*.checkpoint.*.jsonl`) nach Compaction automatisch löschen
- Maintenance-Report: Disk-Usage, Session-Count, Archive-Count
**Verify:** sessions.json zeigt ≤ 30 Einträge, 0 orphaned checkpoint-Files

---

### T6 — Operational-State live statt statisch
**Owner:** Atlas  
**Estimate:** 1–2 h  
**Priority:** P2  
**Scope:**
- Bootstrap-Script erweitert: MC-API-Call auf `/api/health`
- Ergebnis in Bootstrap-Output einbetten (frisches "Current" statt manuelles Update)
- Nicht mehr als 500 Zeichen extra overhead
**Verify:** Nach Gateway-Restart: Bootstrap-Output enthält live MC-Status

---

### T7 — Billing-Modes + Budget-Thresholds aus L1 verschieben
**Owner:** Atlas  
**Estimate:** 1 h  
**Priority:** P3  
**Scope:**
- Live-Befund: groesste L1-Datei aktuell 1.846 Bytes; alle geprueften L1-Dateien unter 3 KB.
- Kein P3-Aufraeumtask noetig, solange keine grossen YAML-Dateien in `memory/invariants/` auftauchen.
- L1 Dateien ≤ 3 KB pro File einhalten (eigene Regel)
- QMD-Index updaten
**Verify:** `memory/invariants/` zeigt max 3 KB pro File

---

### T8 — Sprint-Dokumentation + Retro
**Owner:** Atlas  
**Estimate:** 1 h  
**Priority:** P2  
**Scope:**
- Alle Tasks mit Receipts dokumentieren
- Sprint schließen mit Lessons-Learned
- DoD-Checkliste durchgehen
**Verify:** Sprint-Status → closed, Lessons archiviert

---

---

### T9 — Discord Metadata Budget / Dedupe Design
**Owner:** Forge + Atlas  
**Estimate:** 1–2 h analysis  
**Priority:** P1 design / HOLD  
**Scope:**
- Analysieren, welche Discord inbound metadata blocks pro Turn in Session JSONL landen.
- Design fuer Trimming/Dedupe: Sender/Conversation info nur bei Änderung oder kompakte Hash-/Reference-Form.
- Keine Runtime-Änderung ohne separaten Implementierungs-Task.
**Verify:** Design nennt konkrete Felder, erwartete Einsparung, Safety-Risiken und Testpfad.

---

### T10 — Session Lifecycle Policy
**Owner:** Atlas  
**Estimate:** 1 h  
**Priority:** P2 design / HOLD  
**Scope:**
- Schwellen definieren fuer rotate/compact/watch: Context %, cacheRead, totalTokens, idle time, active lock.
- Discord operator session darf nicht waehrend aktiver Arbeit rotiert werden.
- Policy in operational-state/ops doc verankern.
**Verify:** Entscheidungsmatrix + no-go conditions dokumentiert.

## Team-Assignment

| Task | Owner | Assistenz | Priority |
|------|-------|-----------|----------|
| T1 QMD-Sync | **Forge** | Atlas | P0 |
| T2 Bootstrap-Budget | **Atlas** | Forge | P0 |
| T3 L2-Sweep | **Forge** | Spark | P2 |
| T4 Compaction-Tuning | **Forge** | Atlas | P1 |
| T5 Session-Hygiene | **Lens** | Forge | P3 |
| T6 Op-State live | **Atlas** | — | P2 |
| T7 L1 Aufräumen | **Atlas** | — | P3 |
| T8 Doku | **Atlas** | — | P2 |
| T9 Discord Metadata Budget | **Forge + Atlas** | — | P1 design / HOLD |
| T10 Session Lifecycle Policy | **Atlas** | Forge | P2 design / HOLD |

**Spark** kann bei T3 (Sweep-Script) und T5 (Cleanup-Automation) als Assistenz herangezogen werden.

---

## Definition of Done

- [ ] T1: QMD-Suche liefert Vault-Treffer in frischer Session (verified)
- [ ] T2: Bootstrap-Output ≤ 16000 Zeichen (verified)
- [x] T3 Live-Baseline: 0 Working-Files älter als 14 Tage (Monitor/Scriptaudit bleibt offen)
- [ ] T4: Compaction-Granularität dokumentiert und stabil
- [ ] T5: sessions.json ≤ 30 Einträge, 0 orphaned checkpoints
- [ ] T6: Op-State zeigt live MC-API-Daten im Bootstrap
- [ ] T7: L1 invariants ≤ 30 KB gesamt, ≤ 3 KB pro File
- [ ] T8: Sprint geschlossen, Lessons archiviert
- [ ] T9: Discord metadata budget design erstellt
- [ ] T10: Session lifecycle policy dokumentiert

## Risks
- **R1:** QMD-Sync mit 3000+ Vault-Dateien könnte Latenz addieren → erst mit kleinem Scope testen
- **R2:** L2-Sweep löscht unbeabsichtigt wichtige Notes → Dry-Run Guard mandatory
- **R3:** `maxActiveTranscriptBytes` senken = häufigere Compaction → monitor 7 Tage

## Schnellster Gewinn
T2 (Bootstrap-Budget) + T1 (QMD-Sync) zusammen = schnellster messbarer Effekt. T3/T4 erst nach Plan-Refinement/Operator-Freigabe.

---

*Erstellt: 2026-05-05 | Atlas | Auf Basis: Deep-Dive Session-Management-Analyse*


## Live-Adjustments 2026-05-05 19:35
- MC live gesund: `status=ok`, `openTasks=0`, `failed=0`, `issueCount=0`.
- Board-Anpassung nötig: S-Context-Drafts wurden mehrfach angelegt; je Task nur die neueste Draft behalten, aeltere Duplikate canceln.
- P0 bleibt T1 + T2. T3 wird P2, T5 P3, T7 faktisch erledigt/Watchlist, weil Live-Daten keinen akuten Altbestand zeigen.
- Kein Code-/Config-Write im Sprint-Review ausgefuehrt; nur Plan/Board-Hygiene.
