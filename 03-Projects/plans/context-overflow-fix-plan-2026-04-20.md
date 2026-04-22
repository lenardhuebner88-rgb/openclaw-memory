---
title: Context-Overflow Fix — AGENTS.md + Memory-Layer Hygiene
created: 2026-04-20
author: Commander (Claudebridge)
status: awaiting-atlas-review
operatorLock: false
priority: P0-urgent
---

# Context-Overflow Fix Plan

## Problem-Statement (Commander-Analyse 2026-04-20)

Atlas antwortet sporadisch nicht ("Agent couldn't generate a response", `payloads=0`).
Root-Cause: AGENTS.md ist bei **jedem** Session-Start über dem Gateway-Limit → Truncation → Regel-Loss → leere oder fehlerhafte Turns.

```
AGENTS.md aktuell: 27,130 chars
Gateway-Limit:     24,576 chars
Überschuss:        +2,554 chars (10.4%)
Truncation-Rate:   100% aller Agent-Sessions
```

Sekundäre Ursachen verschlimmern das Problem:
- Invariants-Layer 88 KB (Ziel: 30 KB) — 48 KB Fremd-Content (Pricing-YAMLs, Research-Docs)
- Working-Memory 204 KB, Session-Reports akkumulieren unkontrolliert
- R42–R53 Volltext in AGENTS.md dupliziert was bereits in `feedback_system_rules.md` steht

---

## Atlas: Bitte prüfe zuerst (Review-Gate)

Bevor irgendwas umgesetzt wird, verifiziere bitte:

1. Stimmt die Diagnose? Prüfe: `wc -c /home/piet/.openclaw/workspace/AGENTS.md` → sollte ~27130 zeigen
2. Sind die Fremd-Files in invariants/ tatsächlich nicht nötig beim Bootstrap?
   - `billing-modes-reference.yaml` (17 KB)
   - `budget-thresholds.yaml` (13 KB)
   - `provider-pricing.yaml` (9.4 KB)
   - `research-report-costs-v2-phase1-2026-04-17.md` (9 KB)
3. Sind R42–R53 vollständig in `feedback_system_rules.md` dokumentiert? (`grep -c "^## R4" memory/rules.jsonl` o.ä.)
4. Wenn Diagnose bestätigt: Status dieses Plans auf `atlas-approved` setzen und Phasen starten.

---

## Phase 0 — AGENTS.md Trim (P0, sofort)

**Ziel:** AGENTS.md auf <22,000 chars bringen. Kein Informationsverlust.

**Methode:** R42–R53 Volltext-Sektionen in AGENTS.md durch 1-Liner-Summaries + Pointer ersetzen.
Alle Details sind bereits in `feedback_system_rules.md` — AGENTS.md soll nur die Preamble + kurze Rule-Index sein.

**Umsetzung:** Commander (ich) — habe Write-Rechte, kann direkt Edit ausführen.
**Atlas-Approval:** Pflicht vor Ausführung. Atlas bestätigt welche Sektionen komprimiert werden dürfen.

**Acceptance Criteria:**
- [ ] `wc -c AGENTS.md` < 22,000
- [ ] Gateway-Log zeigt keine Truncation-Warnung mehr bei nächster Session
- [ ] Alle Rules R1–R53 weiterhin via `feedback_system_rules.md` erreichbar
- [ ] Git-Commit mit klarem Message im workspace-Repo

**Rollback:** `git checkout HEAD -- AGENTS.md` im workspace

---

## Phase 1 — Invariants-Layer Bereinigung (P1, Atlas-Task → Lens + Forge)

**Ziel:** Invariants-Layer auf <30 KB bringen, nur echte Architektur-Invariants behalten.

### 1a — Audit (Lens)
- Prüfe alle 10 Dateien in `memory/invariants/` auf: "Ist das ein Architektur-Invariant der in 6 Monaten noch gilt?"
- Kandidaten für Archivierung: `billing-modes-reference.yaml`, `budget-thresholds.yaml`, `provider-pricing.yaml`, `research-report-costs-v2.md`
- Output: Liste mit Empfehlung (behalten / nach working/ / nach archive/)

### 1b — Move (Forge)
- Auf Basis Lens-Audit: Fremd-Files nach `memory/archive/2026-Q2/` verschieben (mv, nicht rm)
- Ziel: invariants/ unter 30 KB gesamt
- Verify: `du -sh memory/invariants/` < 30K

**Acceptance Criteria:**
- [ ] `du -sh memory/invariants/` ≤ 30 KB
- [ ] Kein File >3 KB in invariants/
- [ ] Archivierte Files in `memory/archive/2026-Q2/` erreichbar

---

## Phase 2 — Working Memory Archivierung (P1b, Atlas-Task → Atlas selbst)

**Ziel:** Working/ von 204 KB auf ~40 KB aktive Files reduzieren.

**Regel:** Files mit `updatedAt > 14 Tage` → `memory/archive/2026-Q2/`

**Konkrete Kandidaten (Stand 2026-04-20):**
- `atlas-session-report-2026-04-17-evening.md` (8.5 KB)
- `atlas-session-report-2026-04-18-morning.md` (16 KB)
- `atlas-session-report-2026-04-18-evening.md` (8.4 KB)
- `atlas-weakness-audit-2026-04-17.md` (16 KB)
- `atlas-mc-board-tab-expansion-2026-04-18-evening.md` (14 KB)
→ ~63 KB archivierbar

**Acceptance Criteria:**
- [ ] `du -sh memory/working/` < 60 KB
- [ ] Aktive Plans/WIP-Files bleiben erhalten
- [ ] Archive-Pfad `memory/archive/2026-Q2/` existiert und enthält die archivierten Files

---

## Phase 3 — Strukturelle Absicherung (P2, Forge-Task)

**Ziel:** Das Problem kommt nicht wieder.

### 3a — AGENTS.md Size-Guard (Cron)
- Script: `scripts/agents-md-size-check.sh`
- Cron: täglich 06:00 UTC
- Logic: wenn `wc -c AGENTS.md > 23000` → Discord-Alert an Operator + Atlas
- Output-Format: `[WARN] AGENTS.md: 25432 chars > 23000 limit — trim required`

### 3b — Write-Gate für AGENTS.md
- Vor jedem Append an AGENTS.md: pre-check auf Ziel-Größe
- Wenn Append AGENTS.md über 23,000 chars bringt → Schreiben blockieren, Operator-Alert

### 3c — MEMORY.md Index neu anlegen
- `/home/piet/.openclaw/workspace/memory/MEMORY.md` existiert nicht mehr (gelöscht oder nie angelegt)
- Forge legt MEMORY.md als Index-File an: Pointer auf invariants/, working/, archive/
- Max 100 Zeilen, nur Pointer und kurze Descriptions

**Acceptance Criteria:**
- [ ] `scripts/agents-md-size-check.sh` existiert, ist ausführbar, Cron-Eintrag aktiv
- [ ] MEMORY.md existiert, ist <5 KB, enthält Pointer auf alle Layer
- [ ] Test: AGENTS.md manuell um 1000 chars erweitern → Alert wird ausgelöst

---

## Assignments Summary

| Phase | Was | Wer | Abhängigkeit |
|---|---|---|---|
| Review-Gate | Diagnose verifizieren | Atlas | — |
| Phase 0 | AGENTS.md trimmen | Commander | Atlas-Approval |
| Phase 1a | Invariants-Audit | Lens | Atlas-Approval |
| Phase 1b | Files archivieren | Forge | Lens-Output |
| Phase 2 | WM archivieren | Atlas | Atlas-Approval |
| Phase 3a+b | Size-Guard Cron + Gate | Forge | Phase 0 done |
| Phase 3c | MEMORY.md anlegen | Forge | Phase 1 done |

---

## Erwartetes Ergebnis

Nach Abschluss aller Phasen:
- AGENTS.md: ~20,000 chars, kein Truncation mehr
- Invariants: <30 KB, nur stabile Architektur-Invariants
- Working: <60 KB, aktive Files only
- Cron-Guard: verhindert Regression
- Atlas-Sessions: kein `payloads=0` mehr durch Bootstrap-Truncation

---

*Plan erstellt von Commander (Claudebridge) 2026-04-20 auf Basis Live-Diagnose.*
*Atlas soll diesen Plan reviewen und ggf. korrigieren bevor Umsetzung startet.*
