#!/usr/bin/env python3
"""OpenClaw long-term stability smoketest.

Use after OpenClaw/Discord maintenance. Produces a JSON report and exits non-zero
on failed gates. This intentionally tests more than /health: rich health,
Discord transport recency, plugin inventory, config drift, real agent turns,
optional Discord delivery, soak, and journal signals.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any

OPENCLAW = os.environ.get("OPENCLAW_BIN", "/home/piet/bin/openclaw")
GATEWAY_HEALTH = os.environ.get("OPENCLAW_GATEWAY_HEALTH", "http://127.0.0.1:18789/health")
MC_HEALTH = os.environ.get("MISSION_CONTROL_HEALTH", "http://127.0.0.1:3000/api/health")
LIVE_OPENCLAW_CONFIG_PATH = os.environ.get("OPENCLAW_CONFIG_PATH", "/home/piet/.openclaw/openclaw.json")
LIVE_OPENCLAW_HOME = os.environ.get("OPENCLAW_HOME", "/home/piet")
REPORT_DIR = Path(os.environ.get("OPENCLAW_STABILITY_REPORT_DIR", "/home/piet/.openclaw/workspace/logs/stability"))
CONFIG_PATHS = [
    Path("/home/piet/.openclaw/openclaw.json"),
    Path("/home/piet/.openclaw/openclaw.json.last-good"),
    Path("/home/piet/.openclaw/backups/openclaw-config-guard/openclaw.json.last-good"),
]
HERMES_HOME_CHANNEL_ID = "1486480293153214515"
GUILD_ID = "1486464140246520068"
MONITOR_SERVICE = Path("/home/piet/.config/systemd/user/gateway-memory-monitor.service")
MONITOR_SCRIPT = Path("/home/piet/.openclaw/scripts/gateway-memory-monitor.py")
ERROR_PATTERNS = [
    "ERROR",
    "Error:",
    "FailoverError",
    "fetch-timeout",
    "provider not found",
    "Model provider 'minimax' not found",
    "web_search provider is not available",
    "ERR_MODULE_NOT_FOUND",
    "TypeError",
    "Unhandled",
]
WARNING_PATTERNS = [
    "restartPending",
    "rate limit",
    r"\\b401\\b",
    r"\\b403\\b",
    r"\\b429\\b",
    "ECONNRESET",
    "GatewayIntent",
    "Invalid Form Body",
]
ATLAS_USE_CASES = [
    {
        "id": "atlas_status_pern",
        "expected": "STABILITY_ATLAS_1",
        "prompt": "Stabilitaets-Smoke 1: Antworte exakt mit STABILITY_ATLAS_1 und sonst nichts.",
    },
    {
        "id": "atlas_runbook_choice",
        "expected": "STABILITY_ATLAS_2",
        "prompt": "Stabilitaets-Smoke 2: Szenario Gateway live aber Discord still. Antworte exakt mit STABILITY_ATLAS_2 und sonst nichts.",
    },
    {
        "id": "atlas_config_reasoning",
        "expected": "STABILITY_ATLAS_3",
        "prompt": "Stabilitaets-Smoke 3: Szenario Model provider minimax not found. Antworte exakt mit STABILITY_ATLAS_3 und sonst nichts.",
    },
]


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat()


def epoch_ms() -> int:
    return int(time.time() * 1000)


def stability_env(extra: dict[str, str] | None = None) -> dict[str, str]:
    env = os.environ.copy()
    env["HOME"] = LIVE_OPENCLAW_HOME
    env["OPENCLAW_CONFIG_PATH"] = LIVE_OPENCLAW_CONFIG_PATH
    if extra:
        env.update(extra)
    return env


def run(cmd: list[str], timeout: int = 60, env: dict[str, str] | None = None) -> dict[str, Any]:
    t0 = time.time()
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout, env=env)
        return {
            "cmd": cmd,
            "ok": p.returncode == 0,
            "rc": p.returncode,
            "durationMs": int((time.time() - t0) * 1000),
            "stdout": p.stdout,
            "stderr": p.stderr,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "cmd": cmd,
            "ok": False,
            "rc": 124,
            "durationMs": int((time.time() - t0) * 1000),
            "stdout": e.stdout or "",
            "stderr": (e.stderr or "") + "\nTIMEOUT",
        }


def get_json_url(url: str, timeout: int = 10) -> dict[str, Any]:
    t0 = time.time()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            data = json.loads(body)
            return {"ok": 200 <= resp.status < 300, "status": resp.status, "durationMs": int((time.time() - t0) * 1000), "json": data}
    except Exception as e:
        return {"ok": False, "status": None, "durationMs": int((time.time() - t0) * 1000), "error": repr(e)}


def parse_json_result(res: dict[str, Any]) -> object | None:
    try:
        return json.loads(res.get("stdout") or "")
    except Exception:
        return None


def gate(name: str, ok: bool, evidence: dict[str, Any] | None = None) -> dict[str, Any]:
    return {"name": name, "ok": bool(ok), "evidence": evidence or {}}


def extract_agent_result(res: dict[str, Any]) -> dict[str, Any]:
    data = parse_json_result(res)
    text = ""
    meta: dict[str, Any] = {}
    if isinstance(data, dict):
        payloads = ((data.get("result") or {}).get("payloads") or [])
        if payloads and isinstance(payloads[0], dict):
            text = payloads[0].get("text") or ""
        meta = ((data.get("result") or {}).get("meta") or {})
    trace = meta.get("executionTrace") or {}
    agent_meta = meta.get("agentMeta") or {}
    return {
        "ok": bool(res.get("ok") and isinstance(data, dict) and data.get("status") == "ok"),
        "rc": res.get("rc"),
        "durationMs": res.get("durationMs"),
        "text": text.strip(),
        "agentMeta": agent_meta,
        "executionTrace": trace,
        "fallbackUsed": trace.get("fallbackUsed"),
        "winnerProvider": trace.get("winnerProvider"),
        "winnerModel": trace.get("winnerModel"),
        "attemptCount": len(trace.get("attempts") or []),
        "stderrTail": (res.get("stderr") or "")[-1000:],
        "rawStatus": data.get("status") if isinstance(data, dict) else None,
    }


def rich_health_summary(max_age_sec: int) -> dict[str, Any]:
    rich = run([OPENCLAW, "health", "--json"], timeout=60, env=stability_env())
    rich_json = parse_json_result(rich)
    out: dict[str, Any] = {k: v for k, v in rich.items() if k != "stdout"}
    if not isinstance(rich_json, dict):
        out["parseOk"] = False
        return out
    discord = (rich_json.get("channels") or {}).get("discord") or {}
    plugins = rich_json.get("plugins") or {}
    last_transport = discord.get("lastTransportActivityAt")
    age_sec = None
    if isinstance(last_transport, (int, float)) and last_transport > 0:
        age_sec = max(0, int((epoch_ms() - int(last_transport)) / 1000))
    out["parseOk"] = True
    out["pluginsLoaded"] = plugins.get("loaded")
    out["pluginErrors"] = plugins.get("errors")
    out["discord"] = {k: discord.get(k) for k in ["enabled", "configured", "running", "connected", "restartPending", "lastTransportActivityAt", "lastError"]}
    out["discord"]["transportAgeSec"] = age_sec
    out["discord"]["maxAgeSec"] = max_age_sec
    return out


def read_json(path: Path) -> tuple[dict[str, Any] | None, str | None]:
    try:
        return json.loads(path.read_text()), None
    except Exception as e:
        return None, repr(e)


def config_gates() -> list[dict[str, Any]]:
    gates: list[dict[str, Any]] = []
    isolation: dict[str, Any] = {}
    forbidden: dict[str, Any] = {}
    for path in CONFIG_PATHS:
        d, err = read_json(path)
        if d is None:
            isolation[str(path)] = {"ok": False, "error": err}
            forbidden[str(path)] = {"ok": False, "error": err}
            continue
        ch = (((d.get("channels") or {}).get("discord") or {}).get("guilds") or {}).get(GUILD_ID, {}).get("channels", {}).get(HERMES_HOME_CHANNEL_ID, {})
        isolation[str(path)] = {"enabled": ch.get("enabled"), "ok": ch.get("enabled") is False}
        raw = json.dumps(d)
        web_provider = (((d.get("tools") or {}).get("web") or {}).get("search") or {}).get("provider")
        forbidden[str(path)] = {
            "openaiCodexGptRefs": raw.count("openai-codex/gpt-"),
            "activeBraveWebProvider": web_provider == "brave",
        }
        # MiniMax and openai-codex/gpt-* refs are intentional in the live config;
        # this gate is only about accidental Brave-web leakage.
        forbidden[str(path)]["ok"] = not forbidden[str(path)]["activeBraveWebProvider"]
    gates.append(gate("discord_channel_isolation_config", all(v.get("ok") for v in isolation.values()), isolation))
    gates.append(gate("config_forbidden_provider_refs_absent", all(v.get("ok") for v in forbidden.values()), forbidden))
    return gates


def binary_consistency_gate() -> dict[str, Any]:
    evidence: dict[str, Any] = {"expected": "/home/piet/bin/openclaw", "openclawBin": OPENCLAW}
    svc = MONITOR_SERVICE.read_text(errors="replace") if MONITOR_SERVICE.exists() else ""
    scr = MONITOR_SCRIPT.read_text(errors="replace") if MONITOR_SCRIPT.exists() else ""
    evidence["monitorServiceHasExpectedEnv"] = "OPENCLAW_BIN=/home/piet/bin/openclaw" in svc
    evidence["monitorScriptDefaultExpected"] = '"/home/piet/bin/openclaw"' in scr
    evidence["openclawBinExpected"] = OPENCLAW == "/home/piet/bin/openclaw"
    return gate("openclaw_binary_consistency", all(evidence[k] for k in ["monitorServiceHasExpectedEnv", "monitorScriptDefaultExpected", "openclawBinExpected"]), evidence)


def live_agent_known(agent_id: str) -> bool:
    config, err = read_json(Path(LIVE_OPENCLAW_CONFIG_PATH))
    if config is None:
        return False
    agents = ((config.get("agents") or {}).get("list") or [])
    return any(isinstance(entry, dict) and entry.get("id") == agent_id for entry in agents)


def systemd_gate() -> dict[str, Any]:
    res = run(["systemctl", "--user", "show", "openclaw-gateway.service", "openclaw-discord-bot.service", "gateway-memory-monitor.timer", "-p", "Id", "-p", "ActiveState", "-p", "SubState", "-p", "Result", "-p", "NRestarts", "--no-pager"], timeout=30)
    txt = res.get("stdout") or ""
    evidence = {"rc": res.get("rc"), "stdout": txt}
    blocks = [b for b in txt.split("\n\n") if b.strip()]
    parsed: dict[str, dict[str, str]] = {}
    for block in blocks:
        kv: dict[str, str] = {}
        for line in block.splitlines():
            if "=" not in line:
                continue
            k, v = line.split("=", 1)
            kv[k.strip()] = v.strip()
        sid = kv.get("Id")
        if sid:
            parsed[sid] = kv
    gw = parsed.get("openclaw-gateway.service", {})
    bot = parsed.get("openclaw-discord-bot.service", {})
    timer = parsed.get("gateway-memory-monitor.timer", {})
    gateway_ok = gw.get("ActiveState") == "active" and gw.get("SubState") == "running" and gw.get("Result", "success") != "failed"
    # Commander bot is intentionally deactivated after collision mitigation.
    bot_ok = (
        (bot.get("ActiveState") == "active" and bot.get("SubState") == "running")
        or (bot.get("ActiveState") == "inactive" and bot.get("SubState") in {"dead", "exited"} and bot.get("Result", "success") != "failed")
    )
    timer_ok = timer.get("ActiveState") == "active" and timer.get("SubState") == "waiting" and timer.get("Result", "success") != "failed"
    ok = (
        res.get("ok")
        and "Id=openclaw-gateway.service" in txt
        and "Id=openclaw-discord-bot.service" in txt
        and "Id=gateway-memory-monitor.timer" in txt
        and gateway_ok
        and bot_ok
        and timer_ok
    )
    evidence["parsed"] = {
        "openclaw-gateway.service": gw,
        "openclaw-discord-bot.service": bot,
        "gateway-memory-monitor.timer": timer,
    }
    evidence["policy"] = {
        "gateway_required": "active/running",
        "discord_bot_allowed": ["active/running", "inactive/dead|exited"],
        "timer_required": "active/waiting",
    }
    return gate("systemd_services_expected", bool(ok), evidence)


def run_agent_case(case: dict[str, str], agent_timeout: int, session_key: str | None = None, deliver_channel_id: str | None = None) -> dict[str, Any]:
    cmd = [OPENCLAW, "agent", "--agent", "main", "--message", case["prompt"], "--json", "--timeout", str(agent_timeout)]
    if session_key:
        cmd.extend(["--session-key", session_key])
    if deliver_channel_id:
        target = deliver_channel_id if deliver_channel_id.startswith(("channel:", "#", "@")) else f"channel:{deliver_channel_id}"
        cmd.extend(["--channel", "discord", "--deliver", "--reply-channel", "discord", "--reply-to", target])
    res = run(cmd, timeout=agent_timeout + 30, env=stability_env())
    out = extract_agent_result(res)
    out["caseId"] = case["id"]
    out["expected"] = case["expected"]
    out["deliveredTo"] = deliver_channel_id
    out["command"] = cmd
    out["caseOk"] = out["ok"] and out["text"] == case["expected"] and out.get("fallbackUsed") is False and out.get("winnerProvider") == "openai"
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--soak-minutes", type=float, default=0.0, help="Optional health soak duration")
    ap.add_argument("--agent-timeout", type=int, default=240)
    ap.add_argument("--atlas-rounds", type=int, default=1, help="Number of Atlas real-use-case rounds")
    ap.add_argument("--real-use-cases", action="store_true", help="Run multiple Atlas stability use cases instead of one tiny OK prompt")
    ap.add_argument("--max-discord-transport-age-sec", type=int, default=300)
    ap.add_argument("--discord-deliver-channel-id", default="", help="Optional explicit Discord channel id for one visible Atlas delivery smoke")
    args = ap.parse_args()

    started = now_utc()
    gates: list[dict[str, Any]] = []
    details: dict[str, Any] = {"started": started, "openclawBin": OPENCLAW}

    gw = get_json_url(GATEWAY_HEALTH)
    details["gatewayHealth"] = gw
    gates.append(gate("gateway_http_health_live", gw.get("ok") and gw.get("json", {}).get("ok") is True, gw))

    mc = get_json_url(MC_HEALTH)
    details["missionControlHealth"] = mc
    gates.append(gate("mission_control_ok", mc.get("ok") and mc.get("json", {}).get("status") == "ok", mc))

    rich_summary = rich_health_summary(args.max_discord_transport_age_sec)
    details["openclawHealth"] = rich_summary
    discord = rich_summary.get("discord") or {}
    gates.append(gate("rich_health_plugins_clean", rich_summary.get("ok") and rich_summary.get("parseOk") and not rich_summary.get("pluginErrors"), rich_summary))
    gates.append(gate("discord_transport_connected", discord.get("enabled") and discord.get("configured") and discord.get("running") and discord.get("connected") and not discord.get("restartPending"), discord))
    gates.append(gate("discord_transport_recent", isinstance(discord.get("transportAgeSec"), int) and discord.get("transportAgeSec") <= args.max_discord_transport_age_sec, discord))

    plugins_res = run([OPENCLAW, "plugins", "list", "--json"], timeout=180)
    plugins_json = parse_json_result(plugins_res)
    details["pluginsList"] = {k: v for k, v in plugins_res.items() if k != "stdout"}
    if isinstance(plugins_json, dict):
        by_id = {p.get("id"): p for p in plugins_json.get("plugins", []) if isinstance(p, dict)}
        details["pluginsList"]["summary"] = {k: {"status": by_id.get(k, {}).get("status"), "origin": by_id.get(k, {}).get("origin"), "channelIds": by_id.get(k, {}).get("channelIds"), "providerIds": by_id.get(k, {}).get("providerIds")} for k in ["discord", "codex", "openai", "openrouter"]}
        gates.append(gate("discord_plugin_loaded", by_id.get("discord", {}).get("status") == "loaded" and "discord" in (by_id.get("discord", {}).get("channelIds") or []), details["pluginsList"]["summary"].get("discord")))
        gates.append(gate("codex_plugin_loaded", by_id.get("codex", {}).get("status") == "loaded" and "codex" in (by_id.get("codex", {}).get("providerIds") or []), details["pluginsList"]["summary"].get("codex")))
    else:
        gates.append(gate("plugins_list_json_parse", False, {"stderr": plugins_res.get("stderr", "")[-1000:]}))

    gates.extend(config_gates())
    gates.append(binary_consistency_gate())
    gates.append(systemd_gate())

    cases = ATLAS_USE_CASES if args.real_use_cases else [ATLAS_USE_CASES[0]]
    atlas_results: list[dict[str, Any]] = []
    for round_no in range(max(1, args.atlas_rounds)):
        for case in cases:
            c = dict(case)
            # Avoid accidental cache illusions by making each prompt unique while keeping exact expected output.
            c["prompt"] = f"{case['prompt']} Run={round_no+1}/{args.atlas_rounds} nonce={int(time.time()*1000)}."
            atlas_results.append(run_agent_case(c, args.agent_timeout, session_key=f"stability-atlas-{dt.datetime.now().strftime('%Y%m%d')}"))
    details["atlasUseCases"] = atlas_results
    gates.append(gate("atlas_real_use_cases_clean", all(r.get("caseOk") for r in atlas_results), {"count": len(atlas_results), "results": atlas_results}))
    gates.append(gate("atlas_no_unexpected_fallback", all(r.get("fallbackUsed") is False and r.get("attemptCount") == 1 for r in atlas_results), {"results": [{k: r.get(k) for k in ["caseId", "fallbackUsed", "attemptCount", "winnerProvider", "winnerModel", "durationMs"]} for r in atlas_results]}))

    if live_agent_known("system-bot"):
        sys_res = run([OPENCLAW, "agent", "--agent", "system-bot", "--message", "System-bot Stabilitaets-Smoke: Antworte exakt mit OK_SYSTEM.", "--json", "--timeout", str(args.agent_timeout)], timeout=args.agent_timeout + 30, env=stability_env())
        sys_out = extract_agent_result(sys_res)
        details["agent_system-bot"] = sys_out
        gates.append(gate("agent_system-bot_reply", sys_out["ok"] and sys_out["text"] == "OK_SYSTEM" and sys_out.get("fallbackUsed") is False and sys_out.get("winnerProvider") == "openai", sys_out))
    else:
        details["agent_system-bot"] = {"skipped": True, "reason": "system-bot agent id not present in live config"}
        gates.append(gate("agent_system-bot_reply", True, details["agent_system-bot"]))

    if args.discord_deliver_channel_id:
        deliver_case = {
            "id": "atlas_discord_visible_delivery",
            "expected": "STABILITY_DISCORD_VISIBLE",
            "prompt": f"Sichtbarer Discord-Stability-Smoke fuer Piet. Antworte exakt mit STABILITY_DISCORD_VISIBLE und sonst nichts. nonce={int(time.time()*1000)}",
        }
        delivered = run_agent_case(deliver_case, args.agent_timeout, session_key=f"stability-discord-visible-{dt.datetime.now().strftime('%Y%m%d')}", deliver_channel_id=args.discord_deliver_channel_id)
        details["discordVisibleDelivery"] = delivered
        gates.append(gate("discord_visible_agent_delivery", delivered.get("caseOk"), delivered))

    soak = {"requestedMinutes": args.soak_minutes, "checks": []}
    if args.soak_minutes > 0:
        count = max(1, int(args.soak_minutes * 2))
        for i in range(count):
            h = get_json_url(GATEWAY_HEALTH)
            r = rich_health_summary(args.max_discord_transport_age_sec)
            d = r.get("discord") or {}
            ok = bool(h.get("ok") and h.get("json", {}).get("ok") is True and r.get("parseOk") and not r.get("pluginErrors") and d.get("connected") and not d.get("restartPending") and isinstance(d.get("transportAgeSec"), int) and d.get("transportAgeSec") <= args.max_discord_transport_age_sec)
            soak["checks"].append({"i": i + 1, "ok": ok, "gatewayDurationMs": h.get("durationMs"), "gateway": h.get("json") or h.get("error"), "discord": d})
            if i < count - 1:
                time.sleep(30)
    details["soak"] = soak
    gates.append(gate("soak_health_and_discord_clean", all(x.get("ok") for x in soak["checks"]), {"checks": soak["checks"][-5:], "count": len(soak["checks"])}))

    ended = now_utc()
    logs = run(["journalctl", "--user", "-u", "openclaw-gateway.service", "-u", "openclaw-discord-bot.service", "--since", started, "--until", ended, "--no-pager"], timeout=45)
    log_text = logs.get("stdout") or ""
    counts = {pat: log_text.count(pat) for pat in ERROR_PATTERNS}
    warning_counts = {pat: len(re.findall(pat, log_text)) for pat in WARNING_PATTERNS}
    details["journalScan"] = {"since": started, "until": ended, "counts": counts, "warningCounts": warning_counts, "lineCount": len(log_text.splitlines())}
    gates.append(gate("journal_known_errors_zero", all(v == 0 for v in counts.values()), details["journalScan"]))
    gates.append(gate("journal_warning_budget_clean", all(v == 0 for v in warning_counts.values()), details["journalScan"]))

    ok = all(g["ok"] for g in gates)
    report = {"ok": ok, "started": started, "ended": ended, "gates": gates, "details": details}
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    path = REPORT_DIR / f"openclaw-longterm-stability-smoketest-{stamp}.json"
    path.write_text(json.dumps(report, indent=2) + "\n")
    print(json.dumps({"ok": ok, "report": str(path), "gates": [{"name": g["name"], "ok": g["ok"]} for g in gates]}, indent=2))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
