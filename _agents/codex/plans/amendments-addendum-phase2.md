---
status: active
owner: codex
created: 2026-04-24T21:43:00Z
---

# Amendments Addendum Phase 2

## P2-A1 - Aktiver Discord-Bot ist nicht eindeutig derselbe wie `openclaw-discord-bot.py`

Evidence:
- Operator meldet ClaudeBridge Bot im Channel `1495737862522405088` mit User-ID `1495736716227510402` und Commands `/opus`, `/quality`.
- Lokal ist `openclaw-discord-bot.service` inactive.
- Andere Discord-Services laufen: `atlas-autonomy-discord.service`, `commander-bot.service`.

Impact:
- Slash-Commands in `openclaw-discord-bot.py` sind Code-seitig implementiert, aber ohne Zielservice-Restart nicht live im Discord.

Empfehlung:
- Naechster Operator-Go muss klaeren, ob Meeting-Commands in `openclaw-discord-bot.py` live geschaltet oder in den aktiven ClaudeBridge/Commander-Bot portiert werden.

## P2-A2 - Runner darf Codex nicht rekursiv aus der laufenden Codex-Session spawnen

Evidence:
- Verbot: keine rekursiven Sub-Spawns.
- Codex-Plugin-Install lebt in Claude Main und ist noch Operator-Schritt.

Impact:
- `meeting-runner.sh --once` startet fuer Debate die Claude-Bot-Seite via Taskboard, markiert Codex-Seite aber als manual/plugin-driven bis Phase 2A erledigt ist.

Empfehlung:
- Nach Plugin-Install `/codex:adversarial-review` fuer Meeting-File nutzen oder einen separaten, explizit freigegebenen Codex-CLI Workerpfad definieren.

## P2-A3 - Dogfood-Debate ist bewiesen, aber noch nicht vollstaendig Discord-live

Evidence:
- Simulierter Discord-Command-Pfad hat ein queued Meeting erzeugt:
  `/home/piet/vault/03-Agents/_coordination/meetings/2026-04-24_2137_debate_meeting-runner-architektur-review.md`
- `meeting-runner.sh --once` hat den Main/Claude-Bot-Task `da2a8228-e4ce-41eb-81c9-322af25bd164` erzeugt.
- Task endete mit `status=done`, `receiptStage=result`.
- Meeting-File enthaelt signierte Beitraege von `[claude-bot 2026-04-24T21:43Z]` und `[codex 2026-04-24T21:44Z]`.
- Token-Log schreibt `status=done`, `budget=30000`, `tracked=2100`.

Impact:
- Der sichere Runner-/Spawn-Pfad ist bewiesen.
- Nicht bewiesen ist nur der echte Discord-Slash-Command ueber den aktiven Bot-Prozess, weil kein Bot-Restart/Service-Switch ohne Operator-Go erfolgt ist.

Empfehlung:
- Naechstes Gate: aktiven ClaudeBridge/Commander-Bot-Prozess mit den Meeting-Commands verbinden oder `openclaw-discord-bot.service` explizit live schalten, danach denselben Debate-Test per echter Discord-Interaction wiederholen.

## P2-A4 - Token-Tracking ist vorhanden, aber noch nicht automatisch robust

Evidence:
- Meeting-Frontmatter enthaelt `token-budget` und `tracked-tokens`.
- `/home/piet/.openclaw/scripts/meeting-tokens-log.sh` schreibt die Werte nach `/home/piet/.openclaw/workspace/memory/meeting-tokens.log`.
- Im Dogfood-Test musste `tracked-tokens` nach Beitraegen explizit fortgeschrieben werden.

Impact:
- Budget-Caps sind auditierbar, aber noch nicht hart durchgesetzt.
- Ein Teilnehmer, der `tracked-tokens` nicht aktualisiert, kann das Budget-Monitoring verfälschen.

Empfehlung:
- Vor Cron-/Loop-Aktivierung muss der Runner entweder vor/nach jedem Append eine Schaetzung aktualisieren oder jedes Teilnehmer-Script muss ein verbindliches Token-Log-Update schreiben.
