# Sprint-CE: Context-Efficiency

**Owner:** Atlas
**Created:** 2026-04-21
**Governance:** R50 Session-Lock aktiv
**Scope-Abgrenzung:** Rein Kontext-/Token-Effizienz der Atlas-Sessions. **Kein Überlapp** mit Sprint-M (Audit-Integrity-Scheduler-Consolidation). Kein Re-Open von Sprint-L (Memory-KB). Sprint-K H12/H13 bleiben separat.

---

## Problem

Atlas-Sessions wachsen in Minuten auf Warning/Rotation. Dominanter Treiber: `toolResult`-Blöcke (~85 % des JSONL, belegt in Session `fb60fb36-8d9a-4354-9666-728842371884.jsonl` am 2026-04-21). Größte Einzelblöcke 224 KB / 71 KB / 51 KB — überwiegend breite `grep`s, JSON-Volldumps, Session-Start-Autoread.

## Root Cause

1. Kein automatisches Tool-Result-Clearing server-seitig aktiv.
2. Keine server-side Compaction (Claude-API-Feature ungenutzt).
3. Tool-Wrapper erzwingen keine Größenlimits.
4. Default-JSON-Reader dumpen Volldaten statt Projektion.
5. Session-Start-Autoread lädt ~52 KB eager statt just-in-time.
6. Guard misst File-Size (KB), nicht Modell-Kontext (Tokens).

## Ziel

- `input_tokens` < 80 k nach Normalzyklus
- kein aktives `tool_result` > 10 k Tokens
- cache-hit-rate Atlas-Prefix > 60 %
- Rotation = Ausnahmefall
- **Keine Diagnosequalitäts-Regression** (10-Stichproben-Vergleich vor/nach)

## Primärquellen

- https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents
- https://platform.claude.com/docs/en/build-with-claude/context-editing
- https://platform.claude.com/docs/en/build-with-claude/compaction

---

## Sub-Sprints CE1–CE10 (strikt sequentiell)

### CE1 — Baseline messen (1–2 h)
**Scope:** 5 aktuelle Atlas-Sessions Token-basiert auswerten.
**Deliverable:** `vault/03-Agents/context-baseline-2026-04-21.md` mit:
- `input_tokens` gesamt + `toolResult`-Anteil pro Session
- Top-10 Einzelblöcke mit Tool-Typ
- cache-hit-rate-Snapshot
**DoD:** Report in Discord, Zahlen reproduzierbar.
**Rollback:** N/A (read-only).

### CE2 — `clear_tool_uses_20250919` aktivieren (2–4 h)
**Scope:** Beta-Header `context-management-2025-06-27` + Config in Atlas' API-Wrapper.
**Config-Startpunkt:**
```json
{
  "edits": [{
    "type": "clear_tool_uses_20250919",
    "trigger": {"type": "input_tokens", "value": 30000},
    "keep":    {"type": "tool_uses", "value": 3},
    "clear_at_least": {"type": "input_tokens", "value": 5000},
    "exclude_tools": ["memory_search", "todoread"]
  }]
}
```
**Deliverable:** Patch openclaw-Runtime, Feature-Flag `CTX_EDIT_ENABLED`.
**DoD:** 24 h Live-Lauf, Session-Wachstumsrate −40 % vs. CE1-Baseline.
**Rollback:** Feature-Flag off.

### CE3 — Server-side Compaction (2–3 h)
**Scope:** `compaction_control` aktivieren, Threshold Start = 80 k `input_tokens`.
**Deliverable:** Patch + Runbook für Threshold-Tuning.
**DoD:** Input-Token-Kurve flacht ab, 10 Stichproben ohne Qualitäts-Regression.
**Rollback:** Compaction off, zurück auf manual rotation.

### CE4 — Guard auf Token-Basis (1–2 h)
**Scope:** `session-size-guard.py` liest `usage.input_tokens` aus API-Response. Neue Schwellen:
- Warn 60 k
- Hard 90 k
- Rotation 110 k
**Deliverable:** Patch + neue Schwellen dokumentiert.
**DoD:** KB-Fallback bleibt, Token-Modus primär.
**Rollback:** Revert Patch, KB-Schwellen zurück.

### CE5 — Tool-Wrapper Hard-Truncate (3–5 h)
**Scope:** `exec` / `grep` / `read` / `cat`-Wrapper truncaten bei 8 k Tokens. Rest → `/tmp/<hash>.txt`, Pointer im Output.
**Header-Format:** `[TRUNCATED: N lines total, M bytes, full at /tmp/<hash>.txt]`
**Deliverable:** Patch Tool-Layer + 3 Tests.
**DoD:** Kein `tool_result` > 10 k Tokens in 24 h messbar.
**Rollback:** Wrapper-Patch revert.

### CE6 — JSON-Dump Discipline (2–3 h)
**Scope:** Task/Event/Run-Reader Default-Projektion:
`id, status, dispatchState, executionState, updatedAt, lastActivityAt`.
Volldump nur bei `--full`-Flag.
**Deliverable:** Helper + Call-Site-Migration.
**DoD:** Volldumps < 5 % aller API-Reads, gemessen via Guard-Log.
**Rollback:** Default zurück auf full.

### CE7 — Autoread → Just-in-Time (3–4 h)
**Scope:** Session-Start-Autoread liefert nur Pointer (Pfade/IDs). Lazy-Loader für Vault-Docs.
**Deliverable:** Patch `session-start-hook` + Lazy-Loader-Tool.
**DoD:** Session-Start-Kosten −80 % vs. CE1-Baseline.
**Rollback:** Autoread-Patch revert.

### CE8 — Sub-Agent-Isolation formalisieren (4–6 h)
**Scope:** Pattern "Heavy-Analysis-Delegation" — separate Session, Hard-Cap 2 k Tokens Rückgabe.
**Deliverable:** Wrapper + Runbook für Atlas (wann delegieren, wann inline).
**DoD:** 1 Referenz-Analyse als Proof, Atlas bleibt Orchestrator.
**Rollback:** Sub-Sessions deaktivieren, zurück zu Inline.

### CE9 — Guard zeigt Top-3 Ursache (2–3 h)
**Scope:** Bei Warning Top-3 Verursacher (Tool-Typ, Tokens, Pointer) direkt im Discord-Alert.
**Deliverable:** Patch Guard-Reporter.
**DoD:** Jede Warning enthält Ursachenblock.
**Rollback:** Report-Format zurück auf alt.

### CE10 — Regression-Check automatisieren (2–3 h)
**Scope:** Nach jedem Deploy 5 synthetische Atlas-Zyklen, Token-Report, Alert bei Drift > 20 %.
**Deliverable:** Cron + Alert-Hook.
**DoD:** Ein induzierter Regression-Fall wird erkannt.
**Rollback:** Cron deaktivieren.

---

## Rollout-Regeln

- Je Sub-Sprint eigener MC-Commit, feature-flagged wo möglich.
- Nach CE2, CE3, CE5: je 24 h Observation vor nächstem Schritt.
- Bei Regression > 20 %: Rollback + Incident-Doc in `vault/03-Agents/`.
- R50 Session-Lock durchgängig aktiv.
- Pre-Flight-Gate vor jedem Sub-Sprint:
  ```sh
  ssh homeserver "/home/piet/.openclaw/scripts/pre-flight-sprint-dispatch.sh vault/03-Agents/sprint-ce-context-efficiency-2026-04-21.md"
  ```

## Exit-Criteria

- Alle 10 DoDs grün.
- 7-Tage-Post-Deploy-Baseline bestätigt Zielwerte.
- Neue Regel **R51 "Context-Diet"** dokumentiert in `feedback_system_rules.md`.

## Abgrenzung

- Sprint-M (Audit-Integrity-Scheduler-Consolidation) bleibt unberührt.
- Sprint-L (Memory-KB): L1-Finalize läuft, nicht anfassen.
- Sprint-K H9/H10/H12/H13 bleiben eigener Scope.
- Kein Schema-Change an bestehender Atlas-Session-Struktur ohne eigenes Plan-Doc.
