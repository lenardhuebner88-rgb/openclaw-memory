#!/usr/bin/env python3
"""per-tool-byte-meter.py — Sprint-Q Phase 3a (2026-04-23)

Scans agent session jsonl files and aggregates bytes per toolName. Alerts on
R51 violations (single tool-call > 20 KB).

Outputs:
- /home/piet/.openclaw/workspace/memory/per-tool-bytes.log — aggregated per session/tool
- /home/piet/.openclaw/workspace/memory/per-tool-bytes-alerts.log — R51 violations only

Cron (add after validation):
  */5 * * * * /home/piet/.openclaw/scripts/per-tool-byte-meter.py \
      >> /tmp/per-tool-byte-meter.log 2>&1

Only processes session files modified in the last 15 minutes to keep runtime low.
Env overrides: PTBM_SESSIONS_GLOB, PTBM_LOG, PTBM_ALERT_LOG, PTBM_THRESHOLD_BYTES,
PTBM_MTIME_WINDOW_SEC.
"""
from __future__ import annotations

import collections
import glob as glob_mod
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

SESSIONS_GLOB = os.environ.get(
    "PTBM_SESSIONS_GLOB",
    "/home/piet/.openclaw/agents/*/sessions/*.jsonl",
)
LOG = Path(os.environ.get(
    "PTBM_LOG",
    "/home/piet/.openclaw/workspace/memory/per-tool-bytes.log",
))
ALERT_LOG = Path(os.environ.get(
    "PTBM_ALERT_LOG",
    "/home/piet/.openclaw/workspace/memory/per-tool-bytes-alerts.log",
))
ALERT_THRESHOLD_BYTES = int(os.environ.get("PTBM_THRESHOLD_BYTES", "20480"))
MTIME_WINDOW_SEC = int(os.environ.get("PTBM_MTIME_WINDOW_SEC", "900"))  # 15 min


def now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def process_session(path: str) -> tuple[dict, dict, dict, list]:
    per_bytes: dict[str, int] = collections.Counter()
    per_calls: dict[str, int] = collections.Counter()
    per_max: dict[str, int] = collections.defaultdict(int)
    violations: list[tuple[str, int, str]] = []
    try:
        with open(path, errors="ignore") as fh:
            for ln in fh:
                try:
                    e = json.loads(ln)
                    m = e.get("message", {})
                    if m.get("role") != "toolResult":
                        continue
                    tn = m.get("toolName", "?")
                    sz = len(ln)
                    per_bytes[tn] += sz
                    per_calls[tn] += 1
                    if sz > per_max[tn]:
                        per_max[tn] = sz
                    if sz > ALERT_THRESHOLD_BYTES:
                        violations.append((tn, sz, e.get("timestamp", "?")))
                except Exception:
                    continue
    except Exception:
        pass
    return dict(per_bytes), dict(per_calls), dict(per_max), violations


def main() -> int:
    ts = now_iso()
    sessions = glob_mod.glob(SESSIONS_GLOB)
    if not sessions:
        print(f"{ts} SKIP no-sessions-found glob={SESSIONS_GLOB}")
        return 0

    now_epoch = datetime.now(timezone.utc).timestamp()
    agg_lines: list[str] = []
    alert_lines: list[str] = []
    processed = 0
    skipped_stale = 0

    for path in sessions:
        try:
            mtime = os.path.getmtime(path)
        except FileNotFoundError:
            continue
        if (now_epoch - mtime) > MTIME_WINDOW_SEC:
            skipped_stale += 1
            continue
        processed += 1

        sid = Path(path).stem[:12]
        agent = Path(path).parent.parent.name  # .openclaw/agents/<agent>/sessions/*.jsonl
        per_bytes, per_calls, per_max, viols = process_session(path)

        for tool, total in sorted(per_bytes.items(), key=lambda x: -x[1]):
            calls = per_calls[tool]
            avg = total // max(calls, 1)
            mx = per_max[tool]
            agg_lines.append(
                f"[{ts}] agent={agent} session={sid} tool={tool} calls={calls} "
                f"total={total} avg={avg} max={mx}"
            )

        for tool, sz, event_ts in viols:
            alert_lines.append(
                f"[{ts}] VIOLATION agent={agent} session={sid} tool={tool} "
                f"call_bytes={sz} event_ts={event_ts} threshold={ALERT_THRESHOLD_BYTES}"
            )

    if agg_lines:
        LOG.parent.mkdir(parents=True, exist_ok=True)
        with LOG.open("a") as f:
            f.write("\n".join(agg_lines) + "\n")

    if alert_lines:
        ALERT_LOG.parent.mkdir(parents=True, exist_ok=True)
        with ALERT_LOG.open("a") as f:
            f.write("\n".join(alert_lines) + "\n")

    print(f"{ts} SUMMARY processed={processed} skipped_stale={skipped_stale} "
          f"agg_lines={len(agg_lines)} alerts={len(alert_lines)}")

    # Print top alerts for cron visibility (max 5)
    for ln in alert_lines[:5]:
        print(ln)

    return 0


if __name__ == "__main__":
    sys.exit(main())
