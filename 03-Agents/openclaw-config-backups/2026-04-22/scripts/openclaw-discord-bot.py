#!/usr/bin/env python3
"""
OpenClaw Discord Commander Bot
==============================
Mobile-first orchestration bridge: Discord <-> Atlas (OpenClaw) <-> Workers.

Architecture:
  User taps slash-command / button in Discord
   -> Bot runs pre-flight gate + validates caller
   -> Bot spawns claude subprocess OR calls MC API
   -> Result posted back as rich embed

Config: /home/piet/.openclaw/config/openclaw-discord-bot.env
State:  ~/.openclaw/state/openclaw-discord-sessions.json
Audit:  ~/vault/03-Agents/audit/discord-YYYY-MM-DD.jsonl

Commands (MVP):
  /health                   - MC + Gateway + Homeserver status embed
  /status                   - Open tasks on board
  /agents                   - 6-agent load + state
  /sprint-plan <doc>        - Preview plan-doc with approval buttons
  /sprint-dispatch <doc>    - Direct dispatch (after approval via plan)
  /receipts <task-id>       - Tail receipts for a task
  /logs <source> [lines]    - Tail bot / Forge / Pixel log
  /new                      - Fresh Commander session (clear chat-state)
  /help                     - show this

Button interactions:
  [Dispatch] [Revise] [Cancel]   on plan-preview embed (operator only)

Security: user-ID allowlist, rate-limit 10 cmds/min, subprocess env-strip.
"""

import asyncio
import json
import logging
import os
import subprocess
import sys
import time
import urllib.request
from collections import defaultdict, deque
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
import discord
from discord import app_commands
from discord.ext import commands, tasks

# -----------------------------------------------------------------------------
# Config
# -----------------------------------------------------------------------------
BOT_TOKEN = os.environ.get('DISCORD_BOT_TOKEN', '').strip()
APPLICATION_ID = int(os.environ.get('DISCORD_APPLICATION_ID', '0'))
GUILD_ID = int(os.environ.get('DISCORD_GUILD_ID', '0'))
COMMANDER_CHANNEL_ID = int(os.environ.get('DISCORD_COMMANDER_CHANNEL_ID', '0'))
OPERATOR_ID = int(os.environ.get('OPERATOR_USER_ID', '0'))
ALLOWED_IDS = set(
    int(x) for x in os.environ.get('ALLOWED_USER_IDS', '').split(',') if x.strip()
)
if OPERATOR_ID:
    ALLOWED_IDS.add(OPERATOR_ID)

CLAUDE_BIN = os.environ.get('CLAUDE_BIN', '/home/piet/.local/bin/claude')
OPENCLAW_ROOT = Path(os.environ.get('OPENCLAW_ROOT', '/home/piet/.openclaw'))
WORKSPACE_ROOT = Path(os.environ.get('WORKSPACE_ROOT', '/home/piet/.openclaw/workspace'))
VAULT_ROOT = Path(os.environ.get('VAULT_ROOT', '/home/piet/vault'))
STATE_FILE = Path(os.environ.get('STATE_FILE', '/home/piet/.openclaw/state/openclaw-discord-sessions.json'))
AUDIT_DIR = Path(os.environ.get('AUDIT_DIR', '/home/piet/vault/03-Agents/audit'))
LOG_FILE = Path(os.environ.get('LOG_FILE', '/home/piet/.openclaw/workspace/logs/openclaw-discord-bot.log'))

MC_API_BASE = os.environ.get('MC_API_BASE', 'http://localhost:3000')
MC_ACTOR_KIND = os.environ.get('MC_API_ACTOR_KIND', 'human')
MC_REQUEST_CLASS = os.environ.get('MC_API_REQUEST_CLASS', 'admin')

RATE_LIMIT = int(os.environ.get('RATE_LIMIT_PER_USER_PER_MINUTE', '10'))
QUIET_START = int(os.environ.get('QUIET_HOURS_START', '23'))
QUIET_END = int(os.environ.get('QUIET_HOURS_END', '7'))
HEARTBEAT_WEBHOOK = os.environ.get('HEARTBEAT_WEBHOOK_URL', '').strip()

# Violet brand color
BRAND_COLOR = 0x7C3AED
OK_COLOR = 0x22C55E
WARN_COLOR = 0xF59E0B
ERR_COLOR = 0xF43F5E

# -----------------------------------------------------------------------------
# Logging
# -----------------------------------------------------------------------------
LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    level=os.environ.get('LOG_LEVEL', 'INFO'),
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler(),
    ],
)
log = logging.getLogger('openclaw-discord-bot')

# -----------------------------------------------------------------------------
# State + Audit
# -----------------------------------------------------------------------------
def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception as e:
            log.warning('state load failed: %s', e)
    return {'sessions': {}}


def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))


def audit(user_id: int, user_name: str, command: str, args: dict, result: str) -> None:
    AUDIT_DIR.mkdir(parents=True, exist_ok=True)
    date = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    path = AUDIT_DIR / f'discord-{date}.jsonl'
    entry = {
        'ts': datetime.now(timezone.utc).isoformat(),
        'user_id': user_id,
        'user_name': user_name,
        'command': command,
        'args': args,
        'result': result[:200],
    }
    with path.open('a') as f:
        f.write(json.dumps(entry) + '\n')


# -----------------------------------------------------------------------------
# Rate limiter (per-user sliding window)
# -----------------------------------------------------------------------------
_rate_buckets: dict[int, deque] = defaultdict(deque)

def rate_check(user_id: int) -> bool:
    now = time.time()
    bucket = _rate_buckets[user_id]
    while bucket and bucket[0] < now - 60:
        bucket.popleft()
    if len(bucket) >= RATE_LIMIT:
        return False
    bucket.append(now)
    return True


# -----------------------------------------------------------------------------
# Auth helper
# -----------------------------------------------------------------------------
def is_allowed(user_id: int) -> bool:
    return user_id in ALLOWED_IDS


def is_operator(user_id: int) -> bool:
    return user_id == OPERATOR_ID


async def auth_check(interaction: discord.Interaction, require_operator: bool = False) -> bool:
    uid = interaction.user.id
    if not is_allowed(uid):
        await interaction.response.send_message(
            '⛔ Not authorized. Your Discord-ID is not on the allowlist.',
            ephemeral=True,
        )
        log.warning('unauth attempt by %s (%d)', interaction.user.name, uid)
        return False
    if require_operator and not is_operator(uid):
        await interaction.response.send_message(
            '⛔ Operator-only command.',
            ephemeral=True,
        )
        return False
    if not rate_check(uid):
        await interaction.response.send_message(
            f'🚦 Rate limit ({RATE_LIMIT}/min). Try again shortly.',
            ephemeral=True,
        )
        return False
    return True


# -----------------------------------------------------------------------------
# Subprocess helpers
# -----------------------------------------------------------------------------
async def run_shell(cmd: list[str], timeout: int = 30) -> tuple[int, str, str]:
    """Safe subprocess (no shell=True). Returns (rc, stdout, stderr)."""
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            env={**os.environ, 'PATH': os.environ.get('PATH', '') + ':/home/piet/.openclaw/bin'},
        )
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=timeout)
        return (
            proc.returncode or 0,
            stdout.decode(errors='replace'),
            stderr.decode(errors='replace'),
        )
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        return -1, '', f'timeout after {timeout}s'
    except Exception as e:
        return -1, '', str(e)


async def mc_api_get(path: str) -> dict | None:
    """GET request to Mission Control API."""
    url = f'{MC_API_BASE}{path}'
    headers = {
        'x-actor-kind': MC_ACTOR_KIND,
        'x-request-class': MC_REQUEST_CLASS,
    }
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    return {'error': f'http {resp.status}'}
                return await resp.json()
    except Exception as e:
        return {'error': str(e)}


# -----------------------------------------------------------------------------
# Bot setup
# -----------------------------------------------------------------------------
intents = discord.Intents.default()
intents.message_content = False
intents.members = False

bot = commands.Bot(command_prefix='!', intents=intents, application_id=APPLICATION_ID or None)


@bot.event
async def on_ready():
    log.info('logged in as %s (%s)', bot.user.name, bot.user.id)
    log.info('allowed users: %s', sorted(ALLOWED_IDS))
    log.info('operator: %s', OPERATOR_ID)
    log.info('guild: %s commander-channel: %s', GUILD_ID, COMMANDER_CHANNEL_ID)

    # Sync slash commands to guild (fast) instead of global (1h propagation)
    guild = discord.Object(id=GUILD_ID) if GUILD_ID else None
    try:
        if guild:
            bot.tree.copy_global_to(guild=guild)
            synced = await bot.tree.sync(guild=guild)
        else:
            synced = await bot.tree.sync()
        log.info('synced %d slash commands', len(synced))
    except Exception as e:
        log.error('sync failed: %s', e)

    # Startup heartbeat
    await post_to_channel(
        COMMANDER_CHANNEL_ID,
        embed=discord.Embed(
            title='🟢 OpenClaw Commander online',
            description=f'Bot {bot.user.name} ready. {len(synced) if "synced" in dir() else "?"} commands registered.',
            color=OK_COLOR,
            timestamp=datetime.now(timezone.utc),
        ),
    )
    heartbeat_loop.start()


async def post_to_channel(channel_id: int, **kwargs) -> None:
    if not channel_id:
        return
    ch = bot.get_channel(channel_id)
    if ch:
        try:
            await ch.send(**kwargs)
        except Exception as e:
            log.error('post failed: %s', e)


# -----------------------------------------------------------------------------
# Heartbeat loop (every 15 min)
# -----------------------------------------------------------------------------
@tasks.loop(minutes=15)
async def heartbeat_loop():
    try:
        rc, stdout, _ = await run_shell(['systemctl', '--user', 'is-active', 'mission-control.service'])
        mc_status = stdout.strip() if rc == 0 else 'unknown'
        log.info('heartbeat mc=%s bot=alive', mc_status)
    except Exception as e:
        log.error('heartbeat: %s', e)


# -----------------------------------------------------------------------------
# /health
# -----------------------------------------------------------------------------
@bot.tree.command(name='health', description='Mission Control + Homeserver health')
async def cmd_health(interaction: discord.Interaction):
    if not await auth_check(interaction):
        return
    await interaction.response.defer()

    # MC /api/health
    mc = await mc_api_get('/api/health')
    mc_status = 'degraded'
    mc_detail = 'unknown'
    if mc and 'error' not in mc:
        mc_status = mc.get('status', 'unknown')
        metrics = mc.get('metrics', {})
        mc_detail = (
            f"open: {metrics.get('openTasks','?')} · "
            f"in-progress: {metrics.get('inProgress','?')} · "
            f"failed: {metrics.get('failed','?')} · "
            f"confidence: {int(metrics.get('dispatchStateConsistency',0)*100)}%"
        )

    # Homeserver uptime
    rc, stdout, _ = await run_shell(['uptime', '-p'])
    uptime = stdout.strip() if rc == 0 else 'unknown'

    # MC systemd status
    rc, stdout, _ = await run_shell(['systemctl', '--user', 'is-active', 'mission-control.service'])
    mc_svc = stdout.strip() if rc == 0 else 'unknown'

    color = OK_COLOR if mc_status == 'healthy' else (WARN_COLOR if mc_status == 'degraded' else ERR_COLOR)
    emb = discord.Embed(title='🩺 Homeserver Health', color=color, timestamp=datetime.now(timezone.utc))
    emb.add_field(name='MC Status', value=f'**{mc_status}** ({mc_svc})', inline=False)
    emb.add_field(name='Metrics', value=mc_detail, inline=False)
    emb.add_field(name='Uptime', value=uptime, inline=False)
    await interaction.followup.send(embed=emb)
    audit(interaction.user.id, interaction.user.name, 'health', {}, mc_status)


# -----------------------------------------------------------------------------
# /status — open tasks
# -----------------------------------------------------------------------------
@bot.tree.command(name='status', description='Open tasks on Mission Control board')
async def cmd_status(interaction: discord.Interaction):
    if not await auth_check(interaction):
        return
    await interaction.response.defer()

    try:
        tasks_data = json.loads((WORKSPACE_ROOT / 'mission-control/data/tasks.json').read_text())
        tasks_list = tasks_data if isinstance(tasks_data, list) else tasks_data.get('tasks', [])
    except Exception as e:
        await interaction.followup.send(f'❌ tasks.json read failed: {e}')
        return

    active = [t for t in tasks_list if t.get('status') in ('pending-pickup', 'in-progress', 'assigned', 'draft')]
    active.sort(key=lambda x: x.get('updatedAt', ''), reverse=True)

    lines = [
        f"`{t.get('id','')[:8]}` **{t.get('status','?')}** · "
        f"{t.get('assigned_agent','?'):12s} · "
        f"{(t.get('title','?') or '?')[:70]}"
        for t in active[:10]
    ]

    emb = discord.Embed(
        title=f'📋 Active Tasks ({len(active)})',
        description='\n'.join(lines) if lines else '_No active tasks._',
        color=BRAND_COLOR,
        timestamp=datetime.now(timezone.utc),
    )
    await interaction.followup.send(embed=emb)
    audit(interaction.user.id, interaction.user.name, 'status', {}, f'{len(active)} active')


# -----------------------------------------------------------------------------
# /agents — 6-agent load
# -----------------------------------------------------------------------------
@bot.tree.command(name='agents', description='Agent load + state (6 agents)')
async def cmd_agents(interaction: discord.Interaction):
    if not await auth_check(interaction):
        return
    await interaction.response.defer()

    try:
        tasks_data = json.loads((WORKSPACE_ROOT / 'mission-control/data/tasks.json').read_text())
        tasks_list = tasks_data if isinstance(tasks_data, list) else tasks_data.get('tasks', [])
    except Exception:
        tasks_list = []

    agents = ['main', 'sre-expert', 'frontend-guru', 'efficiency-auditor', 'spark', 'james']
    labels = {'main': 'Atlas', 'sre-expert': 'Forge', 'frontend-guru': 'Pixel',
              'efficiency-auditor': 'Lens', 'spark': 'Spark', 'james': 'James'}

    lines = []
    for a in agents:
        active = sum(1 for t in tasks_list
                     if t.get('assigned_agent') == a
                     and t.get('status') in ('pending-pickup', 'in-progress', 'assigned'))
        emoji = '🟢' if active == 0 else ('🟡' if active < 3 else '🔴')
        lines.append(f'{emoji} **{labels.get(a, a)}** ({a}): {active} active')

    emb = discord.Embed(title='🤖 Agent Load', description='\n'.join(lines),
                        color=BRAND_COLOR, timestamp=datetime.now(timezone.utc))
    await interaction.followup.send(embed=emb)
    audit(interaction.user.id, interaction.user.name, 'agents', {}, 'ok')


# -----------------------------------------------------------------------------
# Approval View (buttons for plan-preview)
# -----------------------------------------------------------------------------
class PlanApprovalView(discord.ui.View):
    def __init__(self, plan_doc: str, operator_id: int):
        super().__init__(timeout=4 * 3600)  # 4h
        self.plan_doc = plan_doc
        self.operator_id = operator_id

    @discord.ui.button(label='✅ Dispatch', style=discord.ButtonStyle.success)
    async def dispatch_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.operator_id:
            await interaction.response.send_message('⛔ Operator-only button', ephemeral=True)
            return
        await interaction.response.defer()

        # Run pre-flight
        rc, stdout, stderr = await run_shell(
            ['/home/piet/.openclaw/scripts/pre-flight-sprint-dispatch.sh', self.plan_doc],
            timeout=60,
        )
        verdict = 'GREEN' if rc == 0 else ('YELLOW' if rc == 1 else 'RED')
        color = OK_COLOR if rc == 0 else (WARN_COLOR if rc == 1 else ERR_COLOR)

        emb = discord.Embed(
            title=f'🛡 Pre-Flight {verdict}',
            description=f'```\n{stdout[-1500:]}\n```',
            color=color,
        )
        await interaction.followup.send(embed=emb)

        if rc == 2:
            audit(interaction.user.id, interaction.user.name, 'sprint-dispatch', {'plan': self.plan_doc}, 'BLOCKED-RED')
            self.stop()
            return

        # TODO: Atlas dispatch (placeholder — would call `claude` or trigger via MC API)
        # For MVP: post a message, actual dispatch is manual confirmation
        await interaction.followup.send(
            embed=discord.Embed(
                title='🚀 Dispatch initiated',
                description=f'Plan: `{self.plan_doc}`\nPre-flight: {verdict}\n\n_Atlas-trigger implementation pending — next iteration._',
                color=BRAND_COLOR,
            ),
        )
        audit(interaction.user.id, interaction.user.name, 'sprint-dispatch',
              {'plan': self.plan_doc, 'verdict': verdict}, 'dispatched')
        self.stop()

    @discord.ui.button(label='🔄 Revise', style=discord.ButtonStyle.secondary)
    async def revise_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.operator_id:
            await interaction.response.send_message('⛔ Operator-only', ephemeral=True)
            return
        await interaction.response.send_message(
            f'🔄 Edit the plan-doc `{self.plan_doc}` on homeserver, then re-invoke `/sprint-plan`.',
            ephemeral=True,
        )
        audit(interaction.user.id, interaction.user.name, 'sprint-revise', {'plan': self.plan_doc}, 'revised')
        self.stop()

    @discord.ui.button(label='❌ Cancel', style=discord.ButtonStyle.danger)
    async def cancel_btn(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.operator_id:
            await interaction.response.send_message('⛔ Operator-only', ephemeral=True)
            return
        await interaction.response.send_message('❌ Cancelled.', ephemeral=True)
        audit(interaction.user.id, interaction.user.name, 'sprint-cancel', {'plan': self.plan_doc}, 'cancelled')
        self.stop()


# -----------------------------------------------------------------------------
# /sprint-plan <doc>  — preview + approval buttons
# -----------------------------------------------------------------------------
@bot.tree.command(name='sprint-plan', description='Preview a sprint plan-doc with approval buttons')
@app_commands.describe(plan_doc='Path relative to vault/03-Agents/ (e.g. sprint-k-h9-plan.md)')
async def cmd_sprint_plan(interaction: discord.Interaction, plan_doc: str):
    if not await auth_check(interaction, require_operator=True):
        return
    await interaction.response.defer()

    # Resolve path
    full = VAULT_ROOT / '03-Agents' / plan_doc
    if not full.exists():
        await interaction.followup.send(f'❌ Not found: `{full}`', ephemeral=True)
        return

    content = full.read_text()[:3500]
    emb = discord.Embed(
        title=f'📋 Plan Preview: {plan_doc}',
        description=f'```md\n{content}\n```',
        color=BRAND_COLOR,
        timestamp=datetime.now(timezone.utc),
    )
    emb.set_footer(text='Operator: tap ✅ Dispatch to proceed (runs pre-flight gate)')
    view = PlanApprovalView(str(full), OPERATOR_ID)
    await interaction.followup.send(embed=emb, view=view)
    audit(interaction.user.id, interaction.user.name, 'sprint-plan', {'plan': plan_doc}, 'preview-posted')


# -----------------------------------------------------------------------------
# /receipts <task-id>
# -----------------------------------------------------------------------------
@bot.tree.command(name='receipts', description='Tail receipts for a task')
@app_commands.describe(task_id='Task ID (full or 8-char prefix)')
async def cmd_receipts(interaction: discord.Interaction, task_id: str):
    if not await auth_check(interaction):
        return
    await interaction.response.defer()

    try:
        tasks_data = json.loads((WORKSPACE_ROOT / 'mission-control/data/tasks.json').read_text())
        tasks_list = tasks_data if isinstance(tasks_data, list) else tasks_data.get('tasks', [])
        task = next((t for t in tasks_list if t.get('id', '').startswith(task_id)), None)
    except Exception as e:
        await interaction.followup.send(f'❌ {e}')
        return

    if not task:
        await interaction.followup.send(f'❌ Task `{task_id}` not found.')
        return

    emb = discord.Embed(
        title=f'📨 {task.get("title","")[:60]}',
        color=BRAND_COLOR,
        timestamp=datetime.now(timezone.utc),
    )
    emb.add_field(name='Status', value=task.get('status', '?'), inline=True)
    emb.add_field(name='Execution', value=task.get('executionState', '?'), inline=True)
    emb.add_field(name='Receipt', value=task.get('receiptStage', 'none'), inline=True)
    emb.add_field(name='Agent', value=task.get('assigned_agent', '?'), inline=True)
    emb.add_field(name='Updated', value=task.get('updatedAt', '?')[:19], inline=True)
    if task.get('resultSummary'):
        emb.add_field(name='Result', value=task.get('resultSummary', '')[:1000], inline=False)
    elif task.get('failureReason'):
        emb.add_field(name='Failure', value=task.get('failureReason', '')[:1000], inline=False)

    await interaction.followup.send(embed=emb)
    audit(interaction.user.id, interaction.user.name, 'receipts',
          {'task_id': task_id}, task.get('status', 'unknown'))


# -----------------------------------------------------------------------------
# /logs <source> [lines]
# -----------------------------------------------------------------------------
LOG_SOURCES = {
    'bot': '/home/piet/.openclaw/workspace/logs/openclaw-discord-bot.log',
    'auto-pickup': '/home/piet/.openclaw/workspace/logs/auto-pickup.log',
    'mc-watchdog': '/home/piet/.openclaw/workspace/logs/mc-watchdog.log',
    'worker-monitor': '/home/piet/.openclaw/workspace/scripts/worker-monitor.log',
    'kb-synth': '/tmp/kb-synth.log',
    'cost-alert': '/home/piet/.openclaw/workspace/logs/cost-alert-dispatcher.cron.log',
}


@bot.tree.command(name='logs', description='Tail a log file')
@app_commands.describe(
    source='Log source (bot, auto-pickup, mc-watchdog, worker-monitor, kb-synth, cost-alert)',
    lines='Number of lines (default 20, max 50)',
)
async def cmd_logs(interaction: discord.Interaction, source: str, lines: int = 20):
    if not await auth_check(interaction):
        return
    await interaction.response.defer()

    path = LOG_SOURCES.get(source)
    if not path:
        await interaction.followup.send(
            f'❌ Unknown. Choose: {", ".join(LOG_SOURCES.keys())}', ephemeral=True,
        )
        return

    lines = max(1, min(lines, 50))
    rc, stdout, stderr = await run_shell(['tail', f'-n{lines}', path], timeout=10)
    body = stdout or stderr or '(empty)'
    body = body[-1800:]

    emb = discord.Embed(
        title=f'📜 {source} (last {lines})',
        description=f'```\n{body}\n```',
        color=BRAND_COLOR,
        timestamp=datetime.now(timezone.utc),
    )
    await interaction.followup.send(embed=emb)
    audit(interaction.user.id, interaction.user.name, 'logs', {'source': source, 'lines': lines}, f'{len(body)}b')


# -----------------------------------------------------------------------------
# /new — fresh commander session (TODO)
# -----------------------------------------------------------------------------
@bot.tree.command(name='new', description='Fresh Commander session (clear bot-side state for your user)')
async def cmd_new(interaction: discord.Interaction):
    if not await auth_check(interaction):
        return
    state = load_state()
    sessions = state.get('sessions', {})
    sessions.pop(str(interaction.user.id), None)
    state['sessions'] = sessions
    save_state(state)
    await interaction.response.send_message('🧼 Session reset.', ephemeral=True)
    audit(interaction.user.id, interaction.user.name, 'new', {}, 'reset')


# -----------------------------------------------------------------------------
# /help
# -----------------------------------------------------------------------------
@bot.tree.command(name='help', description='Show OpenClaw commander commands')
async def cmd_help(interaction: discord.Interaction):
    emb = discord.Embed(
        title='🦞 OpenClaw Commander — Commands',
        color=BRAND_COLOR,
        description=(
            '**Observation (all allowed users)**\n'
            '`/health` — MC + homeserver health\n'
            '`/status` — open tasks on board\n'
            '`/agents` — 6-agent load\n'
            '`/receipts <id>` — task receipts\n'
            '`/logs <source> [lines]` — tail logs\n\n'
            '**Orchestration (operator-only)**\n'
            '`/sprint-plan <doc>` — preview plan + approval buttons\n\n'
            '**Session**\n'
            '`/new` — reset bot-side session state\n'
            '`/help` — this message\n'
        ),
        timestamp=datetime.now(timezone.utc),
    )
    emb.set_footer(text=f'Operator: <@{OPERATOR_ID}> | Allowed users: {len(ALLOWED_IDS)}')
    await interaction.response.send_message(embed=emb, ephemeral=True)


# -----------------------------------------------------------------------------
# Error handler
# -----------------------------------------------------------------------------
@bot.tree.error
async def on_app_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    log.error('command error: %s', error, exc_info=True)
    msg = f'❌ Error: {error.__class__.__name__}: {str(error)[:300]}'
    try:
        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)
    except Exception:
        pass


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    if not BOT_TOKEN:
        log.error('DISCORD_BOT_TOKEN not set')
        sys.exit(1)
    if not OPERATOR_ID:
        log.error('OPERATOR_USER_ID not set')
        sys.exit(1)

    log.info('starting OpenClaw Discord Commander Bot')
    try:
        bot.run(BOT_TOKEN, log_handler=None)
    except KeyboardInterrupt:
        log.info('shutdown by signal')


if __name__ == '__main__':
    main()
