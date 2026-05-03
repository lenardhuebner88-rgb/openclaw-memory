#!/usr/bin/env python3
"""session-rotation-watchdog.py — Sprint-Q Phase 2b (2026-04-23)

Reads /home/piet/.openclaw/workspace/memory/memory-budget.log. When Atlas-main
session enters warning/critical token budget bands, emits
/tmp/atlas-rotation-signal.json so a future auto-pickup extension can rotate
before R49 hallucination kicks in at 99%.

Modes:
- --dry-run (default): log detection, do NOT write signal-file
- --live: write signal-file when threshold crossed

Cron (add after validation):
  */2 * * * * /home/piet/.openclaw/scripts/session-rotation-watchdog.py \
      >> /tmp/session-rotation-watchdog.log 2>&1

Signal-file format (contract for auto-pickup consumer):
  {
    "session_id": "...",
    "pct": 72,
    "tokens_est": 108000,
    "triggered_at": "2026-04-23T17:46:00Z",
    "source": "session-rotation-watchdog",
    "recommended_action": "graceful-rotate-with-summary"
  }

Idempotency: skips if signal already exists for same session/action-level.
Only graceful->emergency upgrade rewrites the same session.
Self-cleanup: removes signal-file if session drops below 60% or session-id changes.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

BUDGET_LOG = Path(os.environ.get("SRW_BUDGET_LOG", "/home/piet/.openclaw/workspace/memory/memory-budget.log"))
SIGNAL_FILE = Path(os.environ.get("SRW_SIGNAL_FILE", "/tmp/atlas-rotation-signal.json"))
STATE_FILE = Path(os.environ.get("SRW_STATE_FILE", "/tmp/session-rotation-watchdog-state.json"))
HISTORY_FILE = Path(os.environ.get("SRW_HISTORY_FILE", "/home/piet/.openclaw/workspace/logs/session-rotation-signal-history.jsonl"))
ALERT_FILE = Path(os.environ.get("SRW_ALERT_FILE", "/home/piet/.openclaw/state/session-rotation-watchdog-alert.json"))
REPEAT_ALERT_THRESHOLD = int(os.environ.get("SRW_REPEAT_ALERT_THRESHOLD", "3"))
MIN_SIGNAL_INTERVAL_SECONDS = int(os.environ.get("SRW_MIN_SIGNAL_INTERVAL_SECONDS", "1200"))

WARN_THRESHOLD = int(os.environ.get("SRW_WARN_THRESHOLD", "85"))       # pct at which rotation is recommended
CRITICAL_THRESHOLD = int(os.environ.get("SRW_CRITICAL_THRESHOLD", "98"))   # pct at which emergency rotation is recommended
DROP_THRESHOLD = 60       # pct below which signal can be cleared

GRACEFUL_ACTION = "graceful-rotate-with-summary"
EMERGENCY_ACTION = "emergency-rotate-too-late"

ENTRY_RE = re.compile(
    r"\[(?P<ts>[^\]]+)\]\s+(?P<status>\w+)\s+session=(?P<sid>[\w-]+)\s+"
    r"size=(?P<size>\d+)\s+tokens_est=(?P<tok>\d+)\s+pct=(?P<pct>\d+)%"
)


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def tail_lines(path: Path, n: int = 30) -> list[str]:
    if not path.exists():
        return []
    with path.open() as f:
        return f.readlines()[-n:]


def parse_entries(lines: list[str]) -> list[dict]:
    out = []
    for ln in lines:
        m = ENTRY_RE.search(ln)
        if not m:
            continue
        d = m.groupdict()
        d["size"] = int(d["size"])
        d["tok"] = int(d["tok"])
        d["pct"] = int(d["pct"])
        out.append(d)
    return out


def latest_per_session(entries: list[dict]) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for e in entries:
        sid = e["sid"]
        if sid not in out or e["ts"] > out[sid]["ts"]:
            out[sid] = e
    return out


def load_signal() -> dict | None:
    if not SIGNAL_FILE.exists():
        return None
    try:
        return json.loads(SIGNAL_FILE.read_text())
    except Exception:
        return None


def load_state() -> dict:
    if not STATE_FILE.exists():
        return {}
    try:
        data = json.loads(STATE_FILE.read_text())
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def write_state_patch(patch: dict, dry_run: bool) -> None:
    if dry_run:
        return
    state = load_state()
    state.update(patch)
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


def parse_iso_utc(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except Exception:
        return None


def rotation_cooldown_remaining(now_value: str) -> int:
    if MIN_SIGNAL_INTERVAL_SECONDS <= 0:
        return 0
    last = parse_iso_utc(load_state().get("last_signal_at"))
    current = parse_iso_utc(now_value)
    if not last or not current:
        return 0
    elapsed = max(0, int((current - last).total_seconds()))
    return max(0, MIN_SIGNAL_INTERVAL_SECONDS - elapsed)


def action_for_pct(pct: int) -> str | None:
    if pct >= CRITICAL_THRESHOLD:
        return EMERGENCY_ACTION
    if pct >= WARN_THRESHOLD:
        return GRACEFUL_ACTION
    return None



def append_history(event: dict, dry_run: bool) -> None:
    payload = {"event_at": now_iso(), "dry_run": dry_run, **event}
    if dry_run:
        return
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_FILE.open("a") as f:
        f.write(json.dumps(payload, sort_keys=True) + "\n")


def recent_repeats(session_id: str, action: str) -> int:
    if not HISTORY_FILE.exists():
        return 0
    count = 0
    try:
        lines = HISTORY_FILE.read_text().splitlines()[-20:]
    except Exception:
        return 0
    for line in reversed(lines):
        try:
            item = json.loads(line)
        except Exception:
            continue
        if item.get("session_id") == session_id and item.get("recommended_action") == action:
            count += 1
            continue
        if count:
            break
    return count


def maybe_write_operator_alert(payload: dict, repeats: int, dry_run: bool) -> None:
    if dry_run or repeats < REPEAT_ALERT_THRESHOLD:
        return
    alert = {
        "alert_type": "session-rotation-signal-repeated",
        "session_id": payload["session_id"],
        "pct": payload["pct"],
        "tokens_est": payload["tokens_est"],
        "recommended_action": payload["recommended_action"],
        "repeat_count": repeats,
        "updated_at": now_iso(),
        "source": "session-rotation-watchdog",
        "human_required": True,
        "auto_rotate": False,
        "runbook": "/home/piet/.openclaw/workspace/docs/operations/session-rotation-watchdog-runbook.md",
    }
    existing = None
    if ALERT_FILE.exists():
        try:
            existing = json.loads(ALERT_FILE.read_text())
        except Exception:
            existing = None
    if existing and existing.get("session_id") == alert["session_id"] and existing.get("recommended_action") == alert["recommended_action"] and existing.get("repeat_count") == alert["repeat_count"]:
        return
    ALERT_FILE.parent.mkdir(parents=True, exist_ok=True)
    ALERT_FILE.write_text(json.dumps(alert, indent=2, sort_keys=True) + "\n")
    print(f"{now_iso()} ALERT repeated-signal session={alert['session_id']} repeats={repeats} action={alert['recommended_action']} file={ALERT_FILE}")

def write_signal(payload: dict, dry_run: bool) -> None:
    append_history({**payload, "signal_event": "would-write" if dry_run else "write"}, dry_run)
    if dry_run:
        print(f"{now_iso()} DRY-RUN would-write-signal session={payload['session_id']} pct={payload['pct']}")
        return
    SIGNAL_FILE.write_text(json.dumps(payload, indent=2))
    write_state_patch({
        "last_signal_at": payload.get("triggered_at") or now_iso(),
        "last_signal_session_id": payload.get("session_id"),
        "last_signal_action": payload.get("recommended_action"),
        "last_signal_pct": payload.get("pct"),
    }, dry_run)
    print(
        f"{now_iso()} WROTE signal session={payload['session_id']} "
        f"pct={payload['pct']} action={payload['recommended_action']} file={SIGNAL_FILE}"
    )


def clear_signal(reason: str, dry_run: bool) -> None:
    if not SIGNAL_FILE.exists():
        return
    if dry_run:
        print(f"{now_iso()} DRY-RUN would-clear-signal reason={reason}")
        return
    try:
        SIGNAL_FILE.unlink()
        print(f"{now_iso()} CLEARED signal reason={reason}")
    except FileNotFoundError:
        pass
    clear_alert(reason=reason, dry_run=dry_run)


def clear_alert(reason: str, dry_run: bool) -> None:
    if not ALERT_FILE.exists():
        return
    if dry_run:
        print(f"{now_iso()} DRY-RUN would-clear-alert reason={reason}")
        return
    try:
        ALERT_FILE.unlink()
        print(f"{now_iso()} CLEARED alert reason={reason}")
    except FileNotFoundError:
        pass


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--live", action="store_true", help="Actually write signal-file (default = dry-run)")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    dry_run = not args.live

    if not BUDGET_LOG.exists():
        print(f"{now_iso()} SKIP budget-log-missing path={BUDGET_LOG}")
        return 0

    lines = tail_lines(BUDGET_LOG, n=30)
    entries = parse_entries(lines)
    if not entries:
        print(f"{now_iso()} SKIP no-parsable-entries")
        return 0

    per_session = latest_per_session(entries)
    # Latest session overall (by timestamp) = the one atlas is currently using
    current = sorted(per_session.values(), key=lambda e: e["ts"])[-1]
    sid = current["sid"]
    pct = current["pct"]
    tok = current["tok"]

    if args.verbose:
        print(f"{now_iso()} SCAN current_session={sid} pct={pct}% tok={tok} status={current['status']}")

    existing = load_signal()
    desired_action = action_for_pct(pct)

    # Case 1: current session is in warning/critical band
    if desired_action is not None:
        current_time = now_iso()
        cooldown_remaining = rotation_cooldown_remaining(current_time)
        if cooldown_remaining > 0 and not (existing and existing.get("session_id") == sid):
            event_payload = {
                "session_id": sid,
                "pct": pct,
                "tokens_est": tok,
                "source": "session-rotation-watchdog",
                "recommended_action": desired_action,
                "budget_log_ts": current["ts"],
                "signal_event": "cooldown-skip",
                "cooldown_remaining_s": cooldown_remaining,
            }
            append_history(event_payload, dry_run)
            maybe_write_operator_alert(event_payload, REPEAT_ALERT_THRESHOLD, dry_run)
            if args.verbose:
                print(f"{now_iso()} SKIP cooldown session={sid} action={desired_action} remaining_s={cooldown_remaining}")
            return 0

        rewrite_reason = None
        if existing and existing.get("session_id") == sid:
            existing_action = existing.get("recommended_action")
            if existing_action == desired_action:
                event_payload = {
                    "session_id": sid,
                    "pct": pct,
                    "tokens_est": tok,
                    "source": "session-rotation-watchdog",
                    "recommended_action": desired_action,
                    "budget_log_ts": current["ts"],
                    "signal_event": "already-signaled",
                }
                append_history(event_payload, dry_run)
                repeats = recent_repeats(sid, desired_action)
                maybe_write_operator_alert(event_payload, repeats, dry_run)
                if args.verbose:
                    print(f"{now_iso()} SKIP already-signaled session={sid} action={desired_action} repeats={repeats}")
                return 0
            if existing_action == GRACEFUL_ACTION and desired_action == EMERGENCY_ACTION:
                rewrite_reason = "upgrade-graceful-to-emergency"
            else:
                # Keep idempotence strict: no downgrade or same-level rewrite loop.
                if args.verbose:
                    print(
                        f"{now_iso()} SKIP keep-existing session={sid} "
                        f"existing_action={existing_action} desired_action={desired_action}"
                    )
                return 0

        payload = {
            "session_id": sid,
            "pct": pct,
            "tokens_est": tok,
            "triggered_at": current_time,
            "source": "session-rotation-watchdog",
            "recommended_action": desired_action,
            "budget_log_ts": current["ts"],
        }
        if rewrite_reason:
            payload["rewrite_reason"] = rewrite_reason
        write_signal(payload, dry_run)
        repeats = recent_repeats(sid, desired_action)
        maybe_write_operator_alert(payload, repeats, dry_run)

    # Case 2: signal exists but session has dropped or changed
    elif existing:
        if existing.get("session_id") != sid:
            clear_signal(reason="session-id-changed", dry_run=dry_run)
        elif pct < DROP_THRESHOLD:
            clear_signal(reason=f"pct-dropped-to-{pct}", dry_run=dry_run)
    elif pct < DROP_THRESHOLD:
        clear_alert(reason=f"pct-dropped-to-{pct}", dry_run=dry_run)

    # No action if pct < WARN and no existing signal
    return 0


if __name__ == "__main__":
    sys.exit(main())
