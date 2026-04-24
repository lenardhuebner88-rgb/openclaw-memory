---
status: ready-for-operator
owner: codex
created: 2026-04-24T21:28:00Z
scope: agent-team-meetings-phase2
---

# Phase 2 Install-Anleitung: codex-plugin-cc

Diese Schritte werden in **Claude Code / Claude Main** ausgefuehrt, nicht in Codex CLI.

## Operator-Commands in Claude Code

```text
/plugin marketplace add openai/codex-plugin-cc
/plugin install codex@openai-codex
/reload-plugins
/codex:setup
```

Danach Codex-Auth pruefen:

```text
!codex login
/codex:status
```

## Smoke-Test

```text
/codex:review
/codex:status
/codex:result
```

Optional fuer echte adversarial reviews:

```text
/codex:adversarial-review
```

## Trigger-Phrase-Mapping

| Trigger | Ziel | Flow |
|---|---|---|
| `Team-Meeting Debate zu <topic>` | Debate | Claude Main/Claude Bot vs Codex, Atlas moderiert |
| `Team-Meeting Council zu <topic>` | Council | Atlas Chairman, Forge/Pixel/Lens/James + Claude Bot + Codex |
| `Team-Meeting Review fuer <target>` | Review | Codex Chairman/Reviewer, Autor als Teilnehmer |
| `/meeting-debate <topic>` | Discord | queued Meeting-File; Claude Bot ersetzt Claude Main |
| `/meeting-council <topic>` | Discord | queued Meeting-File; Runner nach separatem Go |
| `/meeting-review <target>` | Discord | queued Review-File |

## Config-Snippets

### CLAUDE.md / Claude Main

```markdown
Wenn der Operator "Team-Meeting ..." sagt:
1. Meeting-File unter `/home/piet/vault/03-Agents/_coordination/meetings/` anlegen.
2. HANDSHAKE §6 lesen.
3. Bei Debate/Council Cross-Provider-Heterogenitaet sichern: Claude-Seite + Codex.
4. R49: alle Pfad-/SHA-/Session-ID-Claims ins CoVe-Verify-Log.
5. R50: keine aktive Main-Session per Resume kapern; serverseitig Claude Bot per Taskboard-Task einbinden.
```

### AGENTS.md / Codex

```markdown
Bei Meeting-Review:
- Nie das Claude-owned Plan-Doc ueberschreiben; Amendments separat schreiben.
- Review-Modus: Codex ist Chairman nur fuer Review/Audit; Debate/Council wird von Atlas moderiert.
- Keine Cron-/Runner-Aktivierung ohne explizites Operator-Go.
```

## Failure-Modes

| Failure | Symptom | Fix/Rollback |
|---|---|---|
| Plugin nicht installiert | `/codex:*` unbekannt | Marketplace/Add/Install erneut ausfuehren |
| Auth fehlt | `/codex:status` zeigt nicht eingeloggt | `!codex login` in Claude Code |
| Usage-Limit | Jobs bleiben pending/blocked | Meeting abbrechen, status `aborted`, kleineres Budget |
| Workspace nicht trusted | Plugin liest Projektkontext nicht | Claude-Code Workspace/Permissions pruefen |
| Review-Loop | Codex Job laeuft zu lange | `/codex:cancel`, Meeting `aborted` |
| Discord queued ohne Runner | File bleibt `status: queued` | Erwartet bei Option A; Runner erst nach Go aktivieren |

## Rollback

```text
/codex:cancel
/plugin uninstall codex@openai-codex
/reload-plugins
```

Vault-Artefakte bleiben als Audit-Trail erhalten und werden nicht geloescht.
