# Security-Check-Failed — Diagnose-Leitfaden für Forge

**Erstellt:** Lens, 2026-04-12  
**Zweck:** Strukturierter Diagnose-Pfad damit Forge gezielt sucht statt frei zu explorieren  
**Scope:** Nur Diagnose + Root-Cause — Fix-Entscheidung danach durch Atlas

---

## Was bekannt ist

| Fakt | Quelle |
|------|--------|
| Erste Blockierung: 2026-04-11T02:07 UTC | OpenClaw daily log |
| Alle Agenten betroffen: Atlas, Forge, James, Lens | Daily log 2026-04-11 |
| Fehlermeldung: `Security check failed (critical)` | Task notes |
| Betrifft: Task-Terminierungen (complete/fail/done) | Pattern aus Logs |
| Ein Task (2e89fa6f) ist fachlich fertig (commit 150cbad) aber nicht terminierbar | Daily log |
| 8+ Tasks seither in BLOCKED hängen | Daily log |
| Dispatch-Gate-Tests (commit 150cbad) wurden am 2026-04-11 gemergt: 9/9 grün | Task summary |
| Nightly Build 2026-04-11 (04:02 UTC): Heartbeat-Guardrails hinzugefügt, Smoke passed | Daily log |

---

## Hypothesen (absteigend nach Wahrscheinlichkeit)

### H1 — Commit 150cbad hat Security-Validierung auf Terminierungspfad eingebaut
**Wahrscheinlichkeit: Hoch**

Commit 150cbad war ein "dispatch-gate" Fix. Dispatch-Gates validieren den Zustand vor State-Transitions. Es ist möglich dass dabei eine Security-Prüfung auf den complete/fail-Pfad hinzugekommen ist, die zu strikt ist oder eine Voraussetzung hat die nie erfüllt wird.

**Prüfen:**
```bash
git log --oneline | grep -A3 -B3 "150cbad"
git show 150cbad --stat
git show 150cbad | grep -i "security\|check\|guard\|validate"
```

### H2 — exec.security=allowlist blockiert Agent-Callbacks
**Wahrscheinlichkeit: Mittel**

Seit 2026-04-08 ist `tools.exec.security = allowlist` für main, sre-expert, sre-expert-fresh gesetzt. Wenn die Task-Completion-Callbacks als `exec`-Aktion gewertet werden und nicht auf der Allowlist stehen, würden sie geblockt.

**Prüfen:**
```bash
cat ~/.openclaw/openclaw.json | grep -A10 "exec"
# Ist /api/tasks/*/complete auf der exec-Allowlist?
# Ist /api/tasks/*/fail auf der exec-Allowlist?
```

### H3 — Security-Middleware in Mission Control wurde durch Nightly Build geändert
**Wahrscheinlichkeit: Mittel**

Der Nightly Build 2026-04-11 fügte Guardrails zu `api/heartbeat/[agentId]/route.ts` hinzu. Wenn dabei eine globale Security-Middleware oder ein Middleware-Manifest geändert wurde, könnten alle Routes betroffen sein.

**Prüfen:**
```bash
git log --oneline --since="2026-04-10" -- src/middleware.ts
git log --oneline --since="2026-04-10" -- src/app/api/tasks/
git diff HEAD~5 -- src/middleware.ts
```

### H4 — PATCH-Route Security-Validierung zu strikt
**Wahrscheinlichkeit: Mittel**

Der WORKER-SPRINT identifizierte dass die PATCH-Route keine Transition-Gates hat. Wenn als Fix eine zu strikte Security-Prüfung eingebaut wurde, blockt sie alle Terminierungen.

**Prüfen:**
```bash
cat src/app/api/tasks/\[id\]/route.ts | grep -i "security\|check\|auth\|guard"
```

### H5 — Token/Auth-Problem im Agent-Callback
**Wahrscheinlichkeit: Niedrig**

Agenten rufen `/api/tasks/{id}/complete` mit einem Auth-Token auf. Wenn der Token abgelaufen ist oder rotiert wurde, schlägt die Security-Prüfung fehl.

**Prüfen:**
```bash
cat ~/.openclaw/openclaw.json | grep -i "token\|secret\|apiKey" | grep -v "password"
# Wann wurde das Token zuletzt rotiert?
```

---

## Diagnose-Reihenfolge für Forge

```
1. git log --oneline --since="2026-04-10" --until="2026-04-11T03:00" -- src/
   → Zeigt alle Commits direkt vor dem ersten security-check-failed (02:07 UTC)

2. git show <verdächtiger-commit> | grep -i "security\|check\|guard\|critical"
   → Findet den genauen Code der "security check failed (critical)" wirft

3. grep -r "security check failed" /home/piet/.openclaw/workspace/mission-control/src/
   → Findet wo der String definiert ist → das ist der genaue Codepfad

4. Wenn in MC-Code: Was löst den Check aus? Welche Bedingung ist nicht erfüllt?
5. Wenn in Gateway: cat ~/.openclaw/openclaw.json | grep -i security
```

**Der schnellste Weg:** Schritt 3 direkt zuerst — `grep -r "security check failed"` findet sofort wo der String herkommt.

---

## Was Forge danach liefert

- Name der Datei + Zeile wo "security check failed (critical)" geworfen wird
- Die Bedingung die nicht erfüllt ist
- Warum sie seit 2026-04-11 nicht mehr erfüllt ist (was hat sich geändert)
- Vorgeschlagener Fix-Pfad (1-2 Optionen)

**Fix-Entscheidung trifft Atlas** — Forge liefert nur Befund + Optionen.

---

## Bekannte betroffene Tasks (für Forge zur Verifikation nach Fix)

| Task-ID | Agent | Beschreibung |
|---------|-------|-------------|
| 2e89fa6f | Forge | Dispatch UX → Contract-Fix (fachlich DONE, commit 150cbad) |
| 4a7bbc73 | Forge | Obsidian Memory System Layer 3 |
| 4cc89b06 | Atlas | Vault stage blocked test |
| 939e95b5 | James | Sprint Brain Retrieval Smoke-Pack |
| 377a6912 | Atlas | Forge Dispatch Contract härten |
| ff4d92ba | Atlas | RCA Forge Kontext |
| 0339bc12 | Lens | Daily/Event Compression |
| 9673093b | Forge | Brain Shared-State Promotion |

Nach dem Fix: alle auf `done` setzen oder neu dispatchen je nach Status.
