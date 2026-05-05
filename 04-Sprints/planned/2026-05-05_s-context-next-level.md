---
title: "2026-05-05 S-Context — Session/Context Management auf die nächste Stufe"
date: 2026-05-05
status: adjusted-live-verified
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

### T3 — L2 Auto-Sweep reaktivieren + Monitor
**Owner:** Forge  
**Estimate:** 2–3 h  
**Priority:** P2 (herabgestuft nach Live-Check)  
**Scope:**
- Live-Befund: `memory/working` hat 36 Dateien, davon 0 aelter als 14 Tage. Kein akuter Cleanup-Backlog.
- Nur Scriptaudit/Monitor pruefen; Cron nur anlegen, wenn Sweep wirklich fehlt.
- Files older than 14d archivieren oder löschen
- Guard: nie L1 (invariants) oder aktuelle 48h löschen
- Monitoring: `memory-sweep.log` trackt gelöschte Files
**Verify:** `find memory/working -name "*.md" -mtime +14` → leer nach 14 Tagen

---

### T4 — `maxActiveTranscriptBytes` senken (3 MB → 1 MB)
**Owner:** Forge  
**Estimate:** 15 min  
**Priority:** P1  
**Scope:**
- `agents.defaults.compaction.maxActiveTranscriptBytes`: 3000000 → 1000000
- Kein Hard-Restart nötig (Hot-Reload)
- Effekt: Compaction triggert früher, weniger massiv pro Event
**Verify:** Nach 48h: Compaction-Frequenz dokumentiert, pro Event weniger Daten

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

## Risks
- **R1:** QMD-Sync mit 3000+ Vault-Dateien könnte Latenz addieren → erst mit kleinem Scope testen
- **R2:** L2-Sweep löscht unbeabsichtigt wichtige Notes → Dry-Run Guard mandatory
- **R3:** `maxActiveTranscriptBytes` senken = häufigere Compaction → monitor 7 Tage

## Schnellster Gewinn
T1 (QMD-Sync) + T2 (Bootstrap-Budget) zusammen = ~1h, sofort messbarer Effekt. Zuerst diese beiden.

---

*Erstellt: 2026-05-05 | Atlas | Auf Basis: Deep-Dive Session-Management-Analyse*


## Live-Adjustments 2026-05-05 19:35
- MC live gesund: `status=ok`, `openTasks=0`, `failed=0`, `issueCount=0`.
- Board-Anpassung nötig: S-Context-Drafts wurden mehrfach angelegt; je Task nur die neueste Draft behalten, aeltere Duplikate canceln.
- P0 bleibt T1 + T2. T3 wird P2, T5 P3, T7 faktisch erledigt/Watchlist, weil Live-Daten keinen akuten Altbestand zeigen.
- Kein Code-/Config-Write im Sprint-Review ausgefuehrt; nur Plan/Board-Hygiene.
