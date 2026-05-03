# OpenClaw Discord Commander Collision Fix Implementation Plan

> **For Hermes:** Use systematic-debugging and openclaw-operator. Execute only after Piet confirms this plan or has explicitly granted implementation approval in the current thread. Do not touch Hermes tokens.

**Goal:** Remove the legacy Commander Bot as an application-command consumer for the shared OpenClaw/Piet Discord application, while preserving Gateway global slash commands and retaining Commander safety gates for any remaining non-slash functionality.

**Architecture:** The root cause is not only stale guild command registration. `discord.py` processes every `INTERACTION_CREATE` of type application command whenever `ConnectionState._command_tree` exists. Because `openclaw-discord-bot.service` uses the same Discord application/token as the OpenClaw Gateway, its local `CommandTree` tries to resolve `/reset`, `/status`, `/new`, etc. even when guild commands are cleared. Sustainable fix: make the legacy Commander a non-slash Discord client by removing/guarding its `CommandTree` and slash decorators, then let the OpenClaw Gateway own 100% of application commands for app `1486895358725460069`.

**Tech Stack:** Python 3.11, discord.py 2.7.1, user systemd, OpenClaw Gateway 2026.5.2, Discord REST application commands.

---

## Live Evidence Captured

- Service unit: `/home/piet/.config/systemd/user/openclaw-discord-bot.service`
  - `ExecStart=/usr/bin/python3 /home/piet/.openclaw/scripts/openclaw-discord-bot.py`
- Shared app config in `/home/piet/.openclaw/config/openclaw-discord-bot.env`:
  - `DISCORD_APPLICATION_ID=1486895358725460069`
  - `DISCORD_GUILD_ID=1486464140246520068`
  - `DISCORD_COMMANDER_CHANNEL_ID=1495737862522405088`
- Commander source: `/home/piet/.openclaw/scripts/openclaw-discord-bot.py`
  - line 457: `bot = discord.Client(...)`
  - line 458: `bot.tree = app_commands.CommandTree(bot)`
  - 14 local slash decorators: `/health`, `/status`, `/agents`, `/sprint-plan`, `/meeting-*`, `/receipts`, `/logs`, `/new`, `/help`
  - line 1036: `@bot.tree.error`
- discord.py 2.7.1 behavior confirmed from installed source:
  - `ConnectionState.parse_interaction_create()` calls `self._command_tree._from_interaction(interaction)` for application command/autocomplete events whenever `_command_tree` exists.
  - Therefore clearing Discord API guild commands does not stop the local bot process from processing incoming app-command interactions.
- Recent journal symptoms:
  - `Application command 'reset' not found`
  - `ignored command outside commander channel: command=status ...`

## Root Cause

`openclaw-discord-bot.service` and the OpenClaw Gateway share one Discord application. A second process with a `discord.py` `CommandTree` is connected to the same app. Discord sends application-command interactions to the bot session; discord.py routes them through the local tree before any custom `on_interaction` can safely ignore them. Commands owned by the Gateway but unknown to the legacy tree produce `CommandNotFound`; commands known to both trigger the Commander off-channel guard.

## Sustainability Decision

Preferred long-term design:

1. **Single owner for app `1486895358725460069` application commands:** OpenClaw Gateway only.
2. **Legacy Commander must not create a `CommandTree` when sharing that app/token.**
3. **If Commander slash UX is needed later, create a separate Discord Application/Bot token** for Commander with command names prefixed or scoped to Commander (`/commander-*`), not the shared Piet/OpenClaw app.

---

### Task 1: Backup the Commander Bot script

**Objective:** Create a timestamped rollback point before changing code.

**Files:**
- Backup: `/home/piet/.openclaw/backups/openclaw-discord-bot-before-disable-commandtree-YYYYMMDD-HHMMSS.py`
- Source: `/home/piet/.openclaw/scripts/openclaw-discord-bot.py`

**Command:**
```bash
ts=$(date +%Y%m%d-%H%M%S)
cp -a /home/piet/.openclaw/scripts/openclaw-discord-bot.py \
  /home/piet/.openclaw/backups/openclaw-discord-bot-before-disable-commandtree-$ts.py
```

**Expected:** Backup file exists and has same byte size as source.

---

### Task 2: Add a slash-mode gate with safe default `disabled`

**Objective:** Make shared-app slash handling opt-in only; default must prevent local `CommandTree` creation.

**File:**
- Modify: `/home/piet/.openclaw/scripts/openclaw-discord-bot.py:98-105`

**Implementation:**
Add after existing `COMMANDER_SLASH_SYNC_MODE` / `COMMANDER_SILENT_OUTSIDE_CHANNEL` config:

```python
# The Commander shares a Discord application with OpenClaw Gateway. In shared-app
# mode it must not create a discord.py CommandTree, otherwise it consumes or logs
# Gateway-owned slash interactions before the Gateway can own the UX cleanly.
COMMANDER_APPLICATION_COMMANDS = os.environ.get(
    'COMMANDER_APPLICATION_COMMANDS', 'disabled'
).strip().lower() in ('1', 'true', 'yes', 'enabled')
```

**Expected:** Default environment disables Commander application commands without needing an env-file edit.

---

### Task 3: Construct `CommandTree` only when explicitly enabled

**Objective:** Prevent discord.py from routing `INTERACTION_CREATE` application commands to the legacy bot in default mode.

**File:**
- Modify: `/home/piet/.openclaw/scripts/openclaw-discord-bot.py:457-458`

**Current:**
```python
bot = discord.Client(intents=intents, application_id=APPLICATION_ID or None)
bot.tree = app_commands.CommandTree(bot)
```

**Target:**
```python
bot = discord.Client(intents=intents, application_id=APPLICATION_ID or None)
if COMMANDER_APPLICATION_COMMANDS:
    bot.tree = app_commands.CommandTree(bot)
else:
    bot.tree = None
    log.warning(
        'commander application commands disabled; OpenClaw Gateway owns slash commands for shared app %s',
        APPLICATION_ID,
    )
```

**Important:** If `bot.tree` is `None`, all `@bot.tree.command` decorators must not execute. Task 4 handles that.

---

### Task 4: Move all slash command registrations behind a single registrar

**Objective:** Avoid import-time decorator execution when `bot.tree is None`.

**File:**
- Modify: `/home/piet/.openclaw/scripts/openclaw-discord-bot.py:526-1046`

**Approach:**
Replace each `@bot.tree.command(...)` decorator with runtime registration guarded by `if COMMANDER_APPLICATION_COMMANDS and bot.tree:`.

Minimal pattern:

```python
async def cmd_health(interaction: discord.Interaction):
    ...existing body...

# repeat for all cmd_* functions

def register_application_commands() -> None:
    if not COMMANDER_APPLICATION_COMMANDS or bot.tree is None:
        log.info('commander slash command registration skipped')
        return
    bot.tree.command(name='health', description='Mission Control + Homeserver health')(cmd_health)
    bot.tree.command(name='status', description='Open tasks on Mission Control board')(cmd_status)
    bot.tree.command(name='agents', description='Agent load + state (6 agents)')(cmd_agents)
    bot.tree.command(name='sprint-plan', description='Preview a sprint plan-doc with approval buttons')(cmd_sprint_plan)
    bot.tree.command(name='meeting-debate', description='Queue a cross-provider debate meeting')(cmd_meeting_debate)
    bot.tree.command(name='meeting-council', description='Queue a multi-agent council meeting')(cmd_meeting_council)
    bot.tree.command(name='meeting-review', description='Queue a focused review meeting')(cmd_meeting_review)
    bot.tree.command(name='meeting-run-once', description='Dispatch one queued meeting after a read-only preflight')(cmd_meeting_run_once)
    bot.tree.command(name='meeting-status', description='Read-only status for one meeting oder Liste offener Meetings')(cmd_meeting_status)
    bot.tree.command(name='meeting-turn-next', description='Advance exactly one bounded meeting turn after dry-run preflight')(cmd_meeting_turn_next)
    bot.tree.command(name='receipts', description='Tail receipts for a task')(cmd_receipts)
    bot.tree.command(name='logs', description='Tail a log file')(cmd_logs)
    bot.tree.command(name='new', description='Fresh Commander session (clear bot-side state for your user)')(cmd_new)
    bot.tree.command(name='help', description='Show OpenClaw commander commands')(cmd_help)
    bot.tree.error(on_app_error)
```

Then call once before `bot.run(...)`:

```python
register_application_commands()
```

**Expected:** `python3 -m py_compile` passes, and with default env there are zero registered local app commands.

---

### Task 5: Harden `on_ready()` for no-tree mode

**Objective:** Avoid `NoneType` errors and still clear stale guild commands once if possible.

**File:**
- Modify: `/home/piet/.openclaw/scripts/openclaw-discord-bot.py:461-488`

**Implementation:**
```python
if not COMMANDER_APPLICATION_COMMANDS or bot.tree is None:
    log.info('commander slash tree disabled; skipping local sync')
    # Optional one-time cleanup can use a temporary CommandTree only if needed,
    # but current REST verification already showed guild command count = 0.
else:
    ...existing clear/sync logic...
```

**Preferred:** Do not create any temporary `CommandTree` in steady state. Guild command cleanup has already been done and can be verified via REST.

---

### Task 6: Static verification before restart

**Objective:** Prove the file is syntactically valid and local tree processing is disabled by default.

**Commands:**
```bash
python3 -m py_compile /home/piet/.openclaw/scripts/openclaw-discord-bot.py
python3 - <<'PY'
from pathlib import Path
p = Path('/home/piet/.openclaw/scripts/openclaw-discord-bot.py')
text = p.read_text()
print('decorators:', text.count('@bot.tree.command'))
print('tree_assignments:', text.count('app_commands.CommandTree(bot)'))
print('mode_gate:', 'COMMANDER_APPLICATION_COMMANDS' in text)
PY
```

**Expected:**
- py_compile exits 0
- `decorators: 0`
- `mode_gate: True`
- Any remaining `app_commands.CommandTree(bot)` is inside the explicit enabled branch only.

---

### Task 7: Restart only the Commander Bot service

**Objective:** Apply the code change without touching Gateway/Hermes.

**Command:**
```bash
systemctl --user restart openclaw-discord-bot.service
systemctl --user show openclaw-discord-bot.service -p ActiveState -p SubState -p NRestarts -p Result --value --no-pager
```

**Expected:**
```text
active running ... Result=success ... NRestarts unchanged or 0 after restart window
```

---

### Task 8: Post-change verification

**Objective:** Confirm slash ownership belongs to Gateway only and Commander logs are clean.

**Commands:**
```bash
curl -s --max-time 3 http://127.0.0.1:18789/health
journalctl --user -u openclaw-discord-bot.service --since '2 minutes ago' --no-pager \
  | grep -Ei 'Application command|CommandNotFound|ignored command outside commander|error|warning|disabled|ready|logged in' || true
```

**Expected:**
- Gateway health: `{"ok":true,"status":"live"}`
- Commander logs include `commander application commands disabled` / `slash tree disabled`
- No new `CommandNotFound`
- No new `ignored command outside commander channel` during Piet's slash tests in agent channels.

---

### Task 9: Discord REST registry verification

**Objective:** Ensure command registry remains exactly the intended shape.

**Expected registry:**
- OpenClaw/Piet app global commands: populated (~50)
- OpenClaw/Piet app guild commands: `0`
- Hermes global commands: populated (~37)
- Hermes guild commands: `0`

**Important:** Do not print tokens. Use existing token extraction scripts only with redacted output.

---

### Task 10: Manual E2E by Piet

**Objective:** Verify Discord client behavior where only Piet can see interaction responses.

**Test Channels:**
- Agent channel: `<#1486480146524410028>`
- Test channel: `<#1486480128576983070>`
- Commander channel: `<#1495737862522405088>`

**Prompts:**
- In agent/test channel: `/status`, `/new`, `/reset`
- Expected: Gateway/Piet-Bot response, no Commander warning/error.
- In Commander channel: legacy slash commands are intentionally absent unless a separate Commander application is introduced later.

---

## Rollback

```bash
systemctl --user stop openclaw-discord-bot.service
cp -a /home/piet/.openclaw/backups/openclaw-discord-bot-before-disable-commandtree-YYYYMMDD-HHMMSS.py \
  /home/piet/.openclaw/scripts/openclaw-discord-bot.py
python3 -m py_compile /home/piet/.openclaw/scripts/openclaw-discord-bot.py
systemctl --user start openclaw-discord-bot.service
```

Expected rollback risk: old warnings/errors return, but Gateway remains live.

## Future Sustainable Option

If Commander slash UX is still desired, create a **separate Discord Application/Bot** for Commander:

- distinct token from OpenClaw Gateway
- commands prefixed or uniquely named (`/commander-health`, `/commander-meeting-status`, etc.)
- guild-scoped only to commander channel/guild if desired
- no shared `APPLICATION_ID=1486895358725460069`

This is the clean architecture for two slash-command surfaces. Until then, the shared app must have only one application-command owner: OpenClaw Gateway.
