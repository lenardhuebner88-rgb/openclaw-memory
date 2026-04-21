---
title: Codex Future-Plan Execution Protocol
date: 2026-04-22
maintained-by: Operator
purpose: Verbindliches Arbeitsprotokoll für Codex (Terminal-Agent) bei zukünftigen Sprint-Plänen. Nach Scope-Creep SH1→SH5 in 30 min (2026-04-21 22:34-22:51) kodifiziert.
status: active
applies-to: Codex (OpenAI Codex Terminal-Agent)
---

# Codex Future-Plan Execution Protocol

**Stand 2026-04-22:** Nach System-Handbook-Sprint erstellt. Codex war produktiv (Qualität top), aber der Prompt sagte "nur SH1" — ausgeführt wurden SH1-SH5. Dieses Protokoll sichert Scope-Discipline ohne Produktivität zu verlieren.

---

## 1. Vault-Konvention (verbindlich)

**Kanonische Plan-Location:**
```
/home/piet/vault/03-Agents/sprints/
```

Das ist der **Single Source of Truth** für alle Sprint-Pläne (Operator-Planung + Atlas-Dispatch + Codex-Execution).

**Arbeits-Outputs von Codex:** `/home/piet/.openclaw/workspace/**` wie bisher.

**Wichtig:** Wenn ein Plan initial in `workspace/vault/03-Agents/sprints/` landet, muss er **vor Beginn** in `/home/piet/vault/03-Agents/sprints/` gespiegelt werden:
```bash
cp workspace/vault/03-Agents/sprints/<plan>.md /home/piet/vault/03-Agents/sprints/<plan>.md
```

Grund: Operator + Atlas orchestrieren aus `/home/piet/vault/`. Nur Codex arbeitet zusätzlich in `workspace/`.

---

## 2. Scope-Lock-Protokoll

### Wenn Prompt sagt "nur Sprint X"

- Execute **ausschließlich** Sprint X
- Nach Sprint X done: **STOP** und Status-Report
- Kein Weiterarbeiten an Sprint X+1, auch wenn "trivial" oder "synergy"
- Warte auf expliziten Go-Signal vom Operator oder Atlas

### Wenn Prompt sagt "Sprints X-Y" oder "Plan komplett"

- Execute sequenziell
- Nach jedem Sub-Sprint: Status-Report an Discord-Channel (siehe §5)
- Scope-Creep zwischen Sub-Sprints ist trotzdem verboten

### Scope-Creep-Trigger (stop!)

- Neue Dateien anlegen in Verzeichnissen, die der aktuelle Sprint nicht nennt
- Code ändern außerhalb der im Sprint genannten Pfade
- Tooling installieren, das nicht im Sprint steht
- Refaktorierungen ohne Sprint-Auftrag

### Was erlaubt ist ohne expliziten Auftrag

- `.bak`-Backups anlegen vor Mutation
- Fehlerkorrekturen am eigenen Output (innerhalb des Sprints)
- Logs/Traces lesen für Debugging
- Git-Commits mit klaren Messages pro Sprint-Commit-Intention

---

## 3. Frontmatter-Pflicht

Jeder neue Sprint-Plan **muss** folgendes Frontmatter haben:

```yaml
---
sprint-id: S-<UPPERCASE-ID>
title: <kurzer Titel>
created: 2026-04-22
status: planned | running | done | superseded
priority: P0 | P1 | P2 | P3
owner: { <role>: <agent-name>, ... }
depends-on: [<sprint-id-list>]
enables: [<sprint-id-list>]
source-plans: [<path-list>]
anti-goals:
  - <explicit forbidden action>
pre-flight-gates:
  - <gate-condition>
---
```

**Ohne Frontmatter:** Plan wird von `sprint-spec-lint` pre-commit-hook (S-RPT T5, folgt) abgelehnt.

**Bei Existenz ohne Frontmatter:** Codex ergänzt es **vor** execution.

---

## 4. Cross-Synergy-Check vor Execute

Bevor Codex einen Sprint startet:

1. **Lies** `/home/piet/vault/03-Agents/_VAULT-INDEX.md` komplett
2. **Prüfe** `Active Sprints`-Tabelle auf:
   - `depends-on`-Konflikte (was muss vorher fertig sein?)
   - `Overlap-Matrix` (welche Files/Scripts überlappen mit laufenden Sprints?)
   - `Cross-Sprint-Synergien` (gibt es Foundation-Building-Blocks, die bereits gebaut werden?)
3. **Wenn Overlap:** stoppe, report an Operator, warte auf Koordinations-Anweisung
4. **Wenn all clear:** starte Sprint, log `[cross-synergy-check] ok` in Commit-Message

---

## 5. Reporting-Pflicht

### Nach jedem Sub-Sprint (SH1, SH2, ...)

**1× Discord-Message in `1495737862522405088`** mit:

```
**✅ Codex: <Sprint-ID> done**
- Outputs: <file list>
- Cross-refs: <related active sprints>
- Next: <Sprint-ID+1> | WAITING on operator go-signal
- Uncommitted: <git status short>
```

**Prefer:** `SprintOutcome`-Schema (S-FND T1) JSON als Receipt:
```json
{
  "schema_version": "v1",
  "status": "done",
  "next_actions": [{"id": "SH2", "owner": "codex", "priority": "P1", "due": null, "reason_code": "sequential_next"}],
  "blockers": [],
  "artifacts": [{"path": "docs/system/SOURCES.md", "sha256": "...", "type": "doc"}],
  "metrics": {"duration_s": 180, "tokens_in": 4200, "tokens_out": 800}
}
```

### Nach Full-Plan done

**1× Final-Report** mit: alle outputs + DoD-Check + known-gaps + recommended next plans.

---

## 6. Commit-Discipline

- **1 Commit pro Sub-Sprint** (SH1 = 1 commit, SH2 = 1 commit, ...)
- Commit-Message-Pattern:
  ```
  feat(sh2): <Sub-Sprint-Name>
  
  Outputs: <files>
  Scope: <what was in scope>
  Not in scope: <what was NOT done, even if tempting>
  DoD: <how it was verified>
  Cross-refs: <related sprints>
  ```
- **Kein "Big-Bang"-Commit** für mehrere Sub-Sprints
- **Rollback-Pfad** muss implicit möglich sein (git revert auf commit)

---

## 7. Config-Write-Discipline

Alle Writes an **globalen System-Configs** gehen durch S-FND T3 `config-apply-safe.sh`:
- `openclaw.json`
- `crontab`
- `registry.jsonl`
- `agents.json`
- systemd-unit-drop-ins
- `.claude/settings.json` (Laptop, wenn zugreifbar)

**NICHT** durch config-apply-safe:
- docs/system/** (SH-Outputs, generator-managed)
- .bak-files
- Eigene Scratch-Spaces

---

## 8. Abort-Bedingungen

Codex **stoppt sofort** und ruft Operator-Ping, wenn:

1. **Cron-Reconciler-Drift nach Codex-Action** > vorher
2. **`/api/health` → `degraded`** nach Codex-Action
3. **Build fails** nach Codex-Action
4. **Test-Suite rc != 0** nach Codex-Action
5. **Scope-Creep-Trigger** (siehe §2)

Pattern: `discord-alert "CODEX ABORT: <reason>"` + incident-doc in `vault/03-Agents/`.

---

## 9. Verhältnis zu Atlas

- **Atlas dispatcht** Codex-Jobs (via Prompt-Relay in Mission Control)
- **Codex executed** die Arbeit im Terminal (Sandbox)
- **Atlas orchestriert** den Gesamt-Sprint-Flow
- **Codex reports** zurück an Atlas + Operator-Channel

**Konflikt-Fall:** Wenn Atlas und Codex gleichzeitig am selben File arbeiten wollen → Codex cedes priority (Atlas ist Orchestrator).

---

## 10. Evolution dieses Protokolls

- Änderungen via Operator-Edit + commit
- Alle Agents lesen diese Datei bei Session-Start
- Bei Widersprüchen zwischen Plan-Frontmatter und diesem Protokoll: **Protokoll gewinnt** (außer explizit vom Operator überschrieben)

---

## Appendix A — Quick-Prompt für Codex bei neuen Plänen

```
Codex — starte Plan <plan-name>.

PRE-FLIGHT (ZWINGEND):
1. Lies /home/piet/vault/03-Agents/_VAULT-INDEX.md komplett
2. Lies /home/piet/vault/03-Agents/codex-future-plan-protocol.md
3. Lies den Plan /home/piet/vault/03-Agents/sprints/<plan>.md
4. Cross-Synergy-Check: Overlaps mit aktiven Sprints?
5. Wenn Plan-Doc nicht in /home/piet/vault/: spiegeln via cp

SCOPE:
- Arbeite nur an <specific-sprint-id>
- Nach done: STOP + Discord-Report
- Scope-Creep = Abort + Ping

OUTPUT:
- Commit pro Sub-Sprint
- SprintOutcome-Schema als Receipt (wenn S-FND T1 live)
- Discord-Message nach jedem Sub-Sprint

Bei Unsicherheit: frag Operator, execute nicht "im Zweifel mehr".
```
