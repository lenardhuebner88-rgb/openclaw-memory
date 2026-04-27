#!/usr/bin/env python3
"""session-rotation-watchdog.py — Sprint-Q Phase 2b (2026-04-23)

Reads /home/piet/.openclaw/workspace/memory/memory-budget.log. When Atlas-main
session enters 70-95% token budget band, emits /tmp/atlas-rotation-signal.json
so a future auto-pickup extension can graceful-rotate before R49 hallucination
kicks in at 99%.

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

Idempotency: skips if signal already exists for same session_id.
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

WARN_THRESHOLD = 70   # pct at which rotation is recommended
UPPER_LIMIT = 95      # above this it's too late — session effectively dead
DROP_THRESHOLD = 60   # pct below which signal can be cleared

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


def write_signal(payload: dict, dry_run: bool) -> None:
    if dry_run:
        print(f"{now_iso()} DRY-RUN would-write-signal session={payload['session_id']} pct={payload['pct']}")
        return
    SIGNAL_FILE.write_text(json.dumps(payload, indent=2))
    print(f"{now_iso()} WROTE signal session={payload['session_id']} pct={payload['pct']} file={SIGNAL_FILE}")


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

    # Case 1: current session in warning band and no signal yet (or signal for different session)
    if WARN_THRESHOLD <= pct < UPPER_LIMIT:
        if existing and existing.get("session_id") == sid:
            if args.verbose:
                print(f"{now_iso()} SKIP already-signaled session={sid}")
        else:
            payload = {
                "session_id": sid,
                "pct": pct,
                "tokens_est": tok,
                "triggered_at": now_iso(),
                "source": "session-rotation-watchdog",
                "recommended_action": "graceful-rotate-with-summary",
                "budget_log_ts": current["ts"],
            }
            write_signal(payload, dry_run)

    # Case 2: signal exists but session has dropped or changed
    elif existing:
        if existing.get("session_id") != sid:
            clear_signal(reason="session-id-changed", dry_run=dry_run)
        elif pct < DROP_THRESHOLD:
            clear_signal(reason=f"pct-dropped-to-{pct}", dry_run=dry_run)
        elif pct >= UPPER_LIMIT:
            # Too late — session is effectively dead. Keep signal for audit but log escalation
            print(f"{now_iso()} ESCALATE session={sid} pct={pct}% — rotation too late, manual /reset needed")

    # No action if pct < WARN and no existing signal
    return 0


if __name__ == "__main__":
    sys.exit(main())
