#!/usr/bin/env python3
"""
Claude Code Telegram Bridge — Enhanced
=======================================
Supports switching between Ollama (qwen2.5:1.5b) and Anthropic models per chat.

Commands:
  /new        — fresh session (clear context + model stays)
  /model      — show current model + available models
  /model <id> — switch model for this chat
  /session    — show current Claude session ID
  /help       — show this message
"""

import asyncio
import json
import logging
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Optional

from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ─── Logging ────────────────────────────────────────────────────────────────
logging.basicConfig(
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger("claude-tg-bridge")

# ─── Config via environment ─────────────────────────────────────────────────
BOT_TOKEN = os.environ.get("CLAUDE_TG_BOT_TOKEN", "")
STATE_FILE = Path(os.environ.get(
    "CLAUDE_TG_STATE_FILE",
    os.path.expanduser("~/.openclaw/state/claude-telegram-sessions.json"),
))
CLAUDE_BIN = os.environ.get("CLAUDE_BIN", os.path.expanduser("~/.local/bin/claude"))

# ─── Available Models ───────────────────────────────────────────────────────
MODELS = {
    "qwen": {
        "label": "Qwen 3.5 (Ollama)",
        "description": "🟢 Lokales Ollama-Modell, kostenlos, 4B params",
        "available": True,
        "model_cli": "qwen3.5:4b",
        "model_id": "qwen3.5:4b",
        "env": {
            "ANTHROPIC_AUTH_TOKEN": "ollama",
            "ANTHROPIC_API_KEY": "ollama",
            "ANTHROPIC_BASE_URL": "http://localhost:11434",
        },
    },
    "sonnet": {
        "label": "Claude Sonnet 4.6",
        "description": "🔵 Anthropic Sonnet 4.6 — gutes Reasoning",
        "available": True,
        "model_cli": "claude-sonnet-4-6",
        "env": {},  # OAuth aus Claude Code Config
    },
    "opus": {
        "label": "Claude Opus 4.6",
        "description": "🟣 Anthropic Opus 4.6 — bestes Reasoning",
        "available": True,
        "model_cli": "claude-opus-4-6",
        "env": {},  # OAuth aus Claude Code Config
    },
}

DEFAULT_MODEL = "qwen"  # qwen is free + fast, good default

# ─── Session state helpers ───────────────────────────────────────────────────
def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception as e:
            logger.warning("Failed to load state: %s", e)
    return {"sessions": {}, "models": {}}  # sessions: {chat_id: claude_session_id}, models: {chat_id: model_key}

def save_state(state: dict) -> None:
    STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    STATE_FILE.write_text(json.dumps(state, indent=2))

def get_session(state: dict, chat_id: str) -> tuple[Optional[str], str]:
    """Returns (claude_session_id, current_model_key)."""
    session_id = state.get("sessions", {}).get(chat_id) or state.get(str(chat_id))
    model_key = state.get("models", {}).get(chat_id, DEFAULT_MODEL)
    return session_id, model_key

def save_session(state: dict, chat_id: str, session_id: str) -> None:
    state.setdefault("sessions", {})[chat_id] = session_id
    save_state(state)

def save_model(state: dict, chat_id: str, model_key: str) -> None:
    state.setdefault("models", {})[chat_id] = model_key
    save_state(state)

# ─── Claude runner ───────────────────────────────────────────────────────────
async def run_claude(
    message: str,
    session_id: Optional[str],
    model_key: str,
) -> tuple[str, Optional[str]]:
    """
    Run claude --print with the specified model + environment.
    Returns (response_text, new_session_id).
    Raises on timeout or error.
    """
    prompt = (message or "").strip()
    if not prompt:
        raise ValueError("Prompt is required for claude --print")

    model_cfg = MODELS.get(model_key, MODELS[DEFAULT_MODEL])
    model_cli = model_cfg["model_cli"]
    extra_env = model_cfg["env"]

    cmd = [
        CLAUDE_BIN,
        "--print",
        "--output-format", "json",
        "--dangerously-skip-permissions",
        "--model", model_cli,
        "--prompt", prompt,
    ]
    if session_id:
        cmd += ["--resume", session_id]

    env = os.environ.copy()
    for k, v in extra_env.items():
        # Override parent env vars even when v is empty string
        if k in env:
            del env[k]
        if v is not None:  # set even empty string to override parent
            env[k] = v

    logger.info("Running claude model=%s session=%s msg_len=%d", model_key, session_id, len(message))

    proc = await asyncio.create_subprocess_exec(
        *cmd,
        env=env,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    try:
        stdout, stderr = await asyncio.wait_for(proc.communicate(), timeout=600)
    except asyncio.TimeoutError:
        proc.kill()
        await proc.wait()
        raise TimeoutError("Claude took longer than 10 minutes")

    if proc.returncode != 0:
        err = stderr.decode(errors="replace")[:1500] if stderr else "(no stderr)"
        logger.error("claude exit %d: %s", proc.returncode, err)
        return f"❌ Claude exited with code {proc.returncode}:\n{err}", None

    try:
        data = json.loads(stdout.decode(errors="replace"))
        text = data.get("result", "(no result field)")
        new_sid = data.get("session_id")
        logger.info("Got response len=%d new_session=%s", len(text), new_sid)
        return text, new_sid
    except json.JSONDecodeError:
        raw = stdout.decode(errors="replace")[:4000]
        return raw, None


# ─── Auth ───────────────────────────────────────────────────────────────────
async def check_auth(update: Update) -> bool:
    user_id = update.effective_user.id
    raw_allowed = os.environ.get("CLAUDE_TG_ALLOWED_USERS", "").strip()
    allowed = set(int(x) for x in raw_allowed.split(",") if x.strip().isdigit())
    if allowed and user_id not in allowed:
        logger.warning("Unauthorized: user_id=%d", user_id)
        await update.message.reply_text(
            f"❌ Nicht autorisiert.\nDeine Telegram ID: `{user_id}`",
            parse_mode="Markdown",
        )
        return False
    return True


# ─── Message handler ────────────────────────────────────────────────────────
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return

    chat_id = str(update.effective_chat.id)
    text = update.message.text.strip()
    logger.info("MSG chat=%s len=%d", chat_id, len(text))

    await context.bot.send_chat_action(chat_id=chat_id, action="typing")

    state = load_state()
    session_id, model_key = get_session(state, chat_id)

    async def _keep_typing():
        while True:
            try:
                await context.bot.send_chat_action(chat_id=chat_id, action="typing")
                await asyncio.sleep(4)
            except Exception:
                break

    typing_task = asyncio.create_task(_keep_typing())
    try:
        response, new_sid = await run_claude(text, session_id, model_key)
    except TimeoutError:
        await update.message.reply_text("⏰ Timeout nach 10 Minuten.")
        return
    except Exception as exc:
        logger.exception("Bridge error")
        await update.message.reply_text(f"❌ Bridge error: {type(exc).__name__}: {str(exc)[:200]}")
        return
    finally:
        typing_task.cancel()

    if new_sid:
        save_session(state, chat_id, new_sid)

    if not response.strip():
        await update.message.reply_text("(leere Antwort)")
        return

    # Split at Telegram's 4096 char limit
    for i in range(0, len(response), 4096):
        await update.message.reply_text(response[i : i + 4096])


# ─── Commands ────────────────────────────────────────────────────────────────
async def cmd_new(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Start a fresh Claude session (clear context, keep model)."""
    if not await check_auth(update):
        return
    chat_id = str(update.effective_chat.id)
    state = load_state()
    old = state.get("sessions", {}).pop(chat_id, None)
    model_key = state.get("models", {}).get(chat_id, DEFAULT_MODEL)
    save_state(state)
    model_label = MODELS[model_key]["label"]
    msg = f"🔄 **New session started**\nModel: {model_label}"
    if old:
        msg += f"\nOld session: `{old[:8]}...` cleared"
    await update.message.reply_text(msg, parse_mode="Markdown")


async def cmd_session(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show current Claude session ID and model."""
    if not await check_auth(update):
        return
    chat_id = str(update.effective_chat.id)
    state = load_state()
    session_id, model_key = get_session(state, chat_id)
    model_label = MODELS[model_key]["label"]
    sid = session_id or "none"
    await update.message.reply_text(
        f"**Current Session**\n\n"
        f"Model: {model_label}\n"
        f"Session: `{sid}`",
        parse_mode="Markdown",
    )


async def cmd_model(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show or switch model."""
    if not await check_auth(update):
        return
    chat_id = str(update.effective_chat.id)
    state = load_state()
    _, current = get_session(state, chat_id)

    if not context.args:
        # Show available models
        lines = ["**🔀 Verfügbare Modelle**\n"]
        for key, cfg in MODELS.items():
            marker = "✅" if key == current else ("⏳" if not cfg.get("available") else "  ")
            avail_note = " (deaktiviert)" if not cfg.get("available") else ""
            lines.append(f"{marker} `/model {key}` — {cfg['description']}{avail_note}")
        lines.append("\n⚠️ _Model-Wechsel setzt die Session zurück (neue Konversation)._")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
        return

    # Switch model
    target = context.args[0].lower()
    if target not in MODELS:
        await update.message.reply_text(
            f"❌ Unbekanntes Modell: `{target}`\nVerwende /model ohne Argument für eine Liste.",
            parse_mode="Markdown",
        )
        return

    if not MODELS[target].get("available"):
        await update.message.reply_text(
            f"⏳ Modell `{target}` ist derzeit deaktiviert (Usage Limit)."
            "\nVerfügbar: `/model qwen`",
            parse_mode="Markdown",
        )
        return

    old_model = current
    save_model(state, chat_id, target)
    # Clear session on model switch so new model starts fresh
    old_session = state.get("sessions", {}).pop(chat_id, None)
    save_state(state)

    cfg = MODELS[target]
    await update.message.reply_text(
        f"✅ **Model gewechselt**\n\n"
        f"Old: {MODELS[old_model]['label']}\n"
        f"New: {cfg['label']}\n"
        f"{cfg['description']}"
        + (f"\nOld session cleared." if old_session else ""),
        parse_mode="Markdown",
    )


async def cmd_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "**🤖 Claude Code Telegram Bridge**\n\n"
        "Schreib einfach eine Nachricht — Claude antwortet.\n\n"
        "**🤖 Claude:**\n"
        "/model          — Zeige aktuelles Modell + Auswahl\n"
        "/model qwen     — Wechsle zu Qwen 3.5 (Ollama, lokal)\n"
        "/new            — Neue Session (Kontext löschen)\n"
        "/session        — Zeige aktuelle Session-ID\n\n"
        "**🔧 System:**\n"
        "/status         — Gateway + Services Status\n"
        "/health         — Health-Check\n"
        "/agents         — Alle Agents + Modelle\n"
        "/crons          — Cron-Job Status\n"
        "/tasks          — Task-Board Zusammenfassung\n"
        "/logs [n]       — Letzte n Log-Zeilen (default 20)\n"
        "/restart        — Gateway neustarten\n\n"
        "**📱 Handy-Debug:**\n"
        "/ping            — Pong! System alive?\n"
        "/disk            — Speicherplatz\n"
        "/uptime          — Uptime aller Services\n"
        "/fail [n]        — Letzte n Errors\n"
        "/task <title>    — Task auf Board erstellen\n"
        "/alert <msg>     — Alert senden\n\n"
        "⚠️ Model-Wechsel setzt die Session zurück.",
        parse_mode="Markdown",
    )


# ─── New Commands ───────────────────────────────────────────────────────────

async def cmd_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    await update.message.reply_text("🏓 Pong! System lebt.\nUptime: ` check...`", parse_mode="Markdown")
    out = run_cmd("uptime -p 2>/dev/null || uptime", timeout=5)
    await update.message.reply_text(f"Uptime: `{out}`", parse_mode="Markdown")


async def cmd_disk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    out = run_cmd("df -h / /home 2>/dev/null | awk 'NR==1 || /\/$|home$/' | awk '{print $1 \" \" $2 \" \" $3 \" \" $5 \" \" $6}'", timeout=5)
    await update.message.reply_text(f"**💾 Disk**\n\n`{out}`", parse_mode="Markdown")


async def cmd_uptime_sys(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    lines = []
    gw_up = run_cmd("systemctl --user show openclaw-gateway -p ActiveEnterTimestamp --value 2>/dev/null", timeout=5)
    bridge_up = run_cmd("systemctl --user show claude-telegram-bridge -p ActiveEnterTimestamp --value 2>/dev/null", timeout=5)
    ollama_up = run_cmd("ps -o lstart= -p $(pgrep -f 'ollama serve') 2>/dev/null", timeout=5)
    lines.append(f"**🕐 Uptime**\n")
    lines.append(f"Gateway: `{gw_up.strip() or 'unbekannt'}`")
    lines.append(f"Bridge:  `{bridge_up.strip() or 'unbekannt'}`")
    lines.append(f"Ollama:  `{ollama_up.strip() or 'unbekannt'}`")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cmd_fail(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    n = 15
    if context.args and context.args[0].isdigit():
        n = min(int(context.args[0]), 50)
    out = run_cmd(f"journalctl --user -u claude-telegram-bridge -n {n} --no-pager -p err 2>/dev/null | grep -i 'error\\|fail\\|exception\\|traceback' | tail -{n}", timeout=10)
    if not out or out == "(no output)":
        await update.message.reply_text(f"✅ Keine Errors in den letzten {n} Zeilen.")
    else:
        await update.message.reply_text(f"**❌ Errors (letzte {n} Zeilen)**\n\n`{out[:3500]}`", parse_mode="Markdown")


async def cmd_task_create(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: `/task Titel der Aufgabe`\nErstellt eine Task auf dem Board.", parse_mode="Markdown")
        return
    title = " ".join(context.args)
    try:
        import urllib.request, urllib.parse
        body = json.dumps({"title": title, "status": "draft", "createdAt": __import__("datetime").datetime.now().isoformat()}).encode()
        req = urllib.request.Request("http://127.0.0.1:3000/api/tasks", data=body, headers={"Content-Type": "application/json"}, method="POST")
        with urllib.request.urlopen(req, timeout=10) as r:
            data = json.loads(r.read())
            task_id = data.get("id", "?")
            await update.message.reply_text(f"✅ **Task erstellt**\n\n`{title}`\nID: `{task_id}`\n\n→ [Board öffnen](http://127.0.0.1:3000)", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ Task-Erstellung fehlgeschlagen: {e}")


async def cmd_alert(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    if not context.args:
        await update.message.reply_text("Usage: `/alert Deine Nachricht`\nSendet eine Alert-Nachricht an Discord.", parse_mode="Markdown")
        return
    msg = " ".join(context.args)
    try:
        import urllib.request
        body = json.dumps({"content": f"🚨 **Alert von Telegram**\n\n{msg}"}).encode()
        # Discord webhook oder OpenClaw message? Use OpenClaw gateway
        req = urllib.request.Request(
            "http://127.0.0.1:18789/api/messages",
            data=body,
            headers={"Content-Type": "application/json", "Authorization": "Bearer " + os.environ.get("OPENCLAW_GW_TOKEN", "")},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            await update.message.reply_text(f"✅ Alert gesendet: `{msg}`")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Konnte Alert nicht senden: {e}")


# ─── Admin Commands ──────────────────────────────────────────────────────────
import urllib.request

def run_cmd(cmd: str, timeout: int = 10) -> str:
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        out = (result.stdout or "") + (result.stderr or "")
        return out.strip()[:2000] or "(no output)"
    except subprocess.TimeoutExpired:
        return "⏰ Timeout"
    except Exception as e:
        return f"❌ {e}"


async def cmd_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    try:
        with urllib.request.urlopen("http://127.0.0.1:18789/health", timeout=5) as r:
            gw = "✅ live" if r.status == 200 else f"⚠️ {r.status}"
    except:
        gw = "❌ down"
    try:
        with urllib.request.urlopen("http://127.0.0.1:3000/api/tasks?limit=1", timeout=5) as r:
            mc = "✅ OK" if r.status == 200 else f"⚠️ {r.status}"
    except:
        mc = "❌ down"
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5) as r:
            data = json.loads(r.read())
            models = [m["name"] for m in data.get("models", [])]
            ollama = "✅ " + ", ".join(models)
    except:
        ollama = "❌ down"
    await update.message.reply_text(
        f"**🔧 OpenClaw Status**\n\n"
        f"Gateway:  {gw}\n"
        f"MC:       {mc}\n"
        f"Ollama:   {ollama}",
        parse_mode="Markdown",
    )


async def cmd_agents(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    try:
        with open("/home/piet/.openclaw/openclaw.json") as f:
            cfg = json.load(f)
        lines = ["**🤖 Agents + Modelle**\n"]
        for a in cfg.get("agents", {}).get("list", []):
            mid = a.get("id", "?")
            model = a.get("model", {}).get("primary", "?")
            fbs = a.get("model", {}).get("fallbacks", [])
            fb = f" → {fbs[0]}" if fbs else ""
            lines.append(f"• `{mid}` → `{model}`{fb}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def cmd_crons(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    try:
        out = run_cmd("openclaw cron list 2>/dev/null || echo 'CLI nicht verfügbar'", timeout=10)
        # Shorten output
        lines = out.split("\n")[:30]
        text = "\n".join(lines)
        await update.message.reply_text(f"**⏰ Cron Jobs**\n\n`{text}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def cmd_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    try:
        with urllib.request.urlopen("http://127.0.0.1:3000/api/tasks?limit=100", timeout=5) as r:
            data = json.loads(r.read())
        tasks = data.get("tasks", [])
        by_status = {}
        for t in tasks:
            s = t.get("status", "unknown")
            by_status[s] = by_status.get(s, 0) + 1
        lines = ["**📋 Task Board**", f"\n`{len(tasks)}` Tasks gesamt\n"]
        for s, c in sorted(by_status.items()):
            lines.append(f"• `{s}`: {c}")
        await update.message.reply_text("\n".join(lines), parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def cmd_logs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    n = 20
    if context.args and context.args[0].isdigit():
        n = min(int(context.args[0]), 100)
    try:
        out = run_cmd(f"journalctl --user -u claude-telegram-bridge -n {n} --no-pager 2>/dev/null | tail -{n}", timeout=10)
        await update.message.reply_text(f"**📜 Logs (letzte {n})**\n\n`{out[:3500]}`", parse_mode="Markdown")
    except Exception as e:
        await update.message.reply_text(f"❌ {e}")


async def cmd_restart(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    await update.message.reply_text("🔄 Gateway-Restart wird eingeleitet...")
    import urllib.request
    try:
        req = urllib.request.Request(
            "http://127.0.0.1:18789/restart",
            method="POST",
            headers={"Authorization": "Bearer " + os.environ.get("OPENCLAW_GW_TOKEN", "")},
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            await update.message.reply_text(f"✅ Gateway-Restart initiiert ({r.status})")
    except Exception as e:
        await update.message.reply_text(f"⚠️ Restart via API fehlgeschlagen: {e}\nVersuche systemd...")
        try:
            subprocess.run(["systemctl", "--user", "restart", "openclaw-gateway"], timeout=10)
            await update.message.reply_text("✅ Gateway via systemd neugestartet")
        except Exception as e2:
            await update.message.reply_text(f"❌ Auch systemd fehlgeschlagen: {e2}")


async def cmd_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not await check_auth(update):
        return
    checks = []
    try:
        with urllib.request.urlopen("http://127.0.0.1:18789/health", timeout=5) as r:
            checks.append(f"Gateway: {'✅' if r.status == 200 else '⚠️ ' + str(r.status)}")
    except:
        checks.append("Gateway: ❌ down")
    try:
        with urllib.request.urlopen("http://127.0.0.1:3000/api/tasks?limit=1", timeout=5) as r:
            checks.append(f"MC:      {'✅' if r.status == 200 else '⚠️ ' + str(r.status)}")
    except:
        checks.append("MC:      ❌ down")
    try:
        with urllib.request.urlopen("http://localhost:11434/api/tags", timeout=5):
            checks.append("Ollama:  ✅ OK")
    except:
        checks.append("Ollama:  ❌ down")
    await update.message.reply_text("**🏥 Health Check**\n\n" + "\n".join(checks), parse_mode="Markdown")


# ─── Main ───────────────────────────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        logger.error("CLAUDE_TG_BOT_TOKEN not set. Exiting.")
        sys.exit(1)

    logger.info("=== Claude Code Telegram Bridge (Enhanced) ===")
    logger.info("Available models: %s", list(MODELS.keys()))
    logger.info("Default model: %s", DEFAULT_MODEL)
    logger.info("State file: %s", STATE_FILE)

    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start",    cmd_help))
    app.add_handler(CommandHandler("help",    cmd_help))
    app.add_handler(CommandHandler("new",     cmd_new))
    app.add_handler(CommandHandler("model",   cmd_model))
    app.add_handler(CommandHandler("session", cmd_session))
    app.add_handler(CommandHandler("status",  cmd_status))
    app.add_handler(CommandHandler("agents",   cmd_agents))
    app.add_handler(CommandHandler("crons",   cmd_crons))
    app.add_handler(CommandHandler("tasks",   cmd_tasks))
    app.add_handler(CommandHandler("logs",    cmd_logs))
    app.add_handler(CommandHandler("restart", cmd_restart))
    app.add_handler(CommandHandler("health",    cmd_health))
    app.add_handler(CommandHandler("ping",      cmd_ping))
    app.add_handler(CommandHandler("disk",      cmd_disk))
    app.add_handler(CommandHandler("uptime",    cmd_uptime_sys))
    app.add_handler(CommandHandler("fail",      cmd_fail))
    app.add_handler(CommandHandler("task",      cmd_task_create))
    app.add_handler(CommandHandler("alert",     cmd_alert))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Polling...")
    app.run_polling(drop_pending_updates=True)


if __name__ == "__main__":
    main()
