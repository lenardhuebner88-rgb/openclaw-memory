---
status: active
owner: codex
created: 2026-04-26T13:43:00Z
scope: worker-system-6h-audit
---

# Worker/System 6h Audit + Hardening Plan

## Ziel
Mission Control und den normalen Taskboard-Prozess wieder auf einen belastbaren 9/10-Zustand bringen: Live-Wahrheit zuerst, nur kleine reversible Fixes, danach drei echte Board-Sprints als Gate.

## Live-Startzustand
- `/api/health`: `ok`
- `/api/ops/worker-reconciler-proof?limit=100`: `criticalIssues=0`, `openRuns=0`, `proposedActions=0`
- `/api/ops/pickup-proof?limit=100`: `criticalFindings=0`, `pendingPickup=0`, `activeLocks=0`
- Board: 650 Tasks, aktiv keine; 547 done, 47 failed, 51 canceled, 5 draft
- `mission-control.service`: active, aber Journal zeigt sehr hohe Budget-Alert-Frequenz
- `openclaw-discord-bot.service`: active

## Befunde
1. **Worker-Stop-Timeout kann Auto-Pickup crashen**
   - Evidence: `auto-pickup-cron.log` enthält `subprocess.TimeoutExpired: systemctl --user stop ... timed out after 10s`.
   - Ursache: `_terminate_spawned_worker_meta()` fängt `TimeoutExpired` nicht ab.
   - Fix: Timeout catchen und Prozessgruppen-Fallback nutzen.

2. **Discord-Alert-Payloads können ungültiges JSON erzeugen**
   - Evidence: `mission-control.service` Journal enthält wiederholt `Bad control character in string literal in JSON`.
   - Ursache: `alert-dispatcher.sh` baut JSON per Shell-String-Escape; Newlines/Control-Zeichen werden nicht sauber serialisiert.
   - Fix: Payloads per Python `json.dumps` erzeugen.

3. **Cost/Budget-Noise ist systemisch laut**
   - Evidence: `mission-control.service` Journal zeigt viele `Budget-Alert: $... heute (Limit: $3.00)`.
   - Kontext: MiniMax/Codex sind Tokenplan/Pro-OAuth-Lanes; harte $3-Tagesbudget-Warnungen sind fuer diese Lage nicht die richtige Betriebswahrheit.
   - Fix: direkte `console.warn` im Raw-Cost-Read entfernen/rate-limiten und die bestehende Cost-Governance/Dispatcher-Schicht als Alert-Quelle lassen.

4. **Aktuelle fehlgeschlagene Autonomie-Task braucht Abschluss-Hygiene**
   - Evidence: Task `3db85d86-b5a2-4cb7-b2cc-187b22acbab3` ist failed/result mit Orphaned-Gateway-Placeholder, aber `sprintOutcome=null`.
   - Fix/Gate: nach Code-Fix prüfen, ob Receipt-Persistenz den Zustand sauber abbildet; keine breite historische Backfill-Aktion.

## Umsetzungsschritte
1. Backups unter `/home/piet/.openclaw/backup/audit-2026-04-26/` schreiben.
2. Fix Worker-Stop-Timeout + Unit-Test.
3. Fix Alert-Dispatcher JSON-Erzeugung + Shell-Syntaxcheck.
4. Fix Budget-Alert-Noise in Mission Control + Typecheck.
5. Mission Control Build/Restart nur falls TypeScript-Code geaendert.
6. Live-Gates: health, worker-proof, pickup-proof, Journals.
7. Abschlussgate: drei sequentielle Board-Sprints durch Atlas begleiten.

## Drei Sprint-Gates
- **Sprint 1:** Worker Shutdown/Receipt Gate: Auto-Pickup-Timeout-Fallback und Worker-Proofs verifizieren.
- **Sprint 2:** Reporting/Discord Gate: Alert-Payloads und Cost-Noise live pruefen, kein malformed JSON.
- **Sprint 3:** Autonomie-Hygiene Gate: Draft-/Failed-Task-Hygiene, Follow-up-Regeln, keine stille Auto-Finalisierung.

## Stop-Kriterien
- Neue `criticalIssues` im Worker-Proof.
- Neue `criticalFindings` im Pickup-Proof.
- Mission Control Typecheck/Build failed.
- Systemd-Service nicht active.
- Unklare fremde Live-Arbeit auf denselben Dateien.
