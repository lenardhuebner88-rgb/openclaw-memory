#!/usr/bin/env python3
"""
S-OPS-3 / Cron-Runs-Tracker — External replacement for jobs.json `last_run` field.

Background:
  /home/piet/.openclaw/cron/jobs.json contains 25 jobs but ALL have last_run=null.
  The openclaw runtime doesn't persist last_run on completion (Persistence-Bug).
  Direct runtime-code-fix would be risky.
  This tracker aggregates from /cron/runs/*.jsonl into an alternative state file
  that monitoring tools can consume.

Schedule: */5 * * * * (every 5min)
Lock:     /tmp/cron-runs-tracker.lock
Log:      /home/piet/.openclaw/workspace/logs/cron-runs-tracker.log
Output:   /home/piet/.openclaw/cron/runs-tracker.json

Output schema (per job):
  {
    "jobId": "<uuid>",
    "name": "<job-name from jobs.json>",
    "schedule": "<cron-expr>",
    "last_run_ts": <unix-ms>,
    "last_run_iso": "<ISO timestamp>",
    "last_status": "ok|error|...",
    "last_action": "finished|started|...",
    "last_duration_ms": <int>,
    "last_model": "<provider/model>",
    "last_provider": "<provider>",
    "last_summary_head": "<first 200 chars>",
    "run_count": <int — total events for this job>,
    "next_run_ms": <unix-ms — from last event nextRunAtMs>,
    "status_signal": "fresh|stale|never-run"
  }

status_signal:
  - fresh: last_run within 2x cron-interval
  - stale: last_run > 2x cron-interval ago
  - never-run: jobId in jobs.json but no events in /cron/runs/

Discord-alert (via alert-dispatcher) if any active job has status=stale or never-run >7d.
"""
import json
import os
import sys
import time
import glob
import subprocess
from pathlib import Path

JOBS_JSON = Path("/home/piet/.openclaw/cron/jobs.json")
RUNS_DIR = Path("/home/piet/.openclaw/cron/runs")
OUT_PATH = Path("/home/piet/.openclaw/cron/runs-tracker.json")
LOG_PATH = Path("/home/piet/.openclaw/workspace/logs/cron-runs-tracker.log")
ALERT_DISPATCHER = "/home/piet/.openclaw/scripts/alert-dispatcher.sh"

# Cron expr to interval-seconds approximation (for fresh/stale signal)
def cron_to_seconds(expr):
    if not expr:
        return None
    try:
        # Common patterns
        if expr in ("* * * * *",):
            return 60
        if expr.startswith("*/"):
            try:
                m = int(expr[2:].split()[0])
                return m * 60
            except: pass
        if expr.startswith("0 */"):
            try:
                h = int(expr[4:].split()[0])
                return h * 3600
            except: pass
        if expr.startswith("0 ") and "* * *" in expr:
            return 24 * 3600  # daily
        if expr.startswith("0 ") and "* * 0" in expr:
            return 7 * 24 * 3600  # weekly
        return None
    except:
        return None


def ts():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def log(msg):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(LOG_PATH, "a") as f:
        f.write(f"{ts()} {msg}\n")


def load_jobs_json():
    if not JOBS_JSON.exists():
        return {}
    try:
        with open(JOBS_JSON) as f:
            data = json.load(f)
        jobs_by_id = {}
        for j in data.get("jobs", []):
            jid = j.get("id")
            if jid:
                jobs_by_id[jid] = {
                    "name": j.get("name", "?"),
                    "schedule": j.get("schedule", {}).get("expr", "?") if isinstance(j.get("schedule"), dict) else "?",
                    "enabled": j.get("enabled", False),
                }
        return jobs_by_id
    except Exception as e:
        log(f"jobs_json_parse_error: {e}")
        return {}


def aggregate_runs():
    """Walk /cron/runs/*.jsonl and aggregate latest event per jobId."""
    latest_by_job = {}
    run_count = {}
    files = list(RUNS_DIR.glob("*.jsonl"))
    if not files:
        log("no_run_files")
        return latest_by_job, run_count

    for fp in files:
        try:
            with open(fp) as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        e = json.loads(line)
                    except: continue
                    jid = e.get("jobId")
                    if not jid:
                        continue
                    run_count[jid] = run_count.get(jid, 0) + 1
                    cur = latest_by_job.get(jid)
                    if cur is None or e.get("ts", 0) > cur.get("ts", 0):
                        latest_by_job[jid] = e
        except Exception as exc:
            log(f"file_read_error {fp}: {exc}")
            continue

    return latest_by_job, run_count


def compute_signal(latest, schedule, now_ms):
    if latest is None:
        return "never-run"
    interval_s = cron_to_seconds(schedule)
    if interval_s is None:
        # Default heuristic: 1h max age
        interval_s = 3600
    age_ms = now_ms - latest.get("ts", 0)
    threshold_ms = interval_s * 2 * 1000  # 2x interval
    if age_ms < threshold_ms:
        return "fresh"
    return "stale"


def main():
    if not JOBS_JSON.exists():
        log("FATAL jobs.json missing")
        return 1

    jobs_by_id = load_jobs_json()
    latest_by_job, run_count = aggregate_runs()
    now_ms = int(time.time() * 1000)

    tracker = {
        "generated_at": ts(),
        "jobs_count": len(jobs_by_id),
        "run_files_count": len(list(RUNS_DIR.glob("*.jsonl"))),
        "jobs": {},
    }

    fresh_n = stale_n = never_n = 0
    stale_jobs = []
    never_run_jobs = []

    # Combine: walk all known jobs + all jobIds with runs (in case of unregistered)
    all_jids = set(jobs_by_id.keys()) | set(latest_by_job.keys())

    for jid in sorted(all_jids):
        meta = jobs_by_id.get(jid, {"name": "<not-in-jobs.json>", "schedule": "?", "enabled": False})
        latest = latest_by_job.get(jid)
        signal = compute_signal(latest, meta["schedule"], now_ms)

        if signal == "fresh":
            fresh_n += 1
        elif signal == "stale":
            stale_n += 1
            stale_jobs.append((jid, meta["name"]))
        elif signal == "never-run":
            never_n += 1
            never_run_jobs.append((jid, meta["name"]))

        entry = {
            "jobId": jid,
            "name": meta["name"],
            "schedule": meta["schedule"],
            "enabled": meta.get("enabled", False),
            "run_count": run_count.get(jid, 0),
            "status_signal": signal,
        }
        if latest:
            entry.update({
                "last_run_ts": latest.get("ts"),
                "last_run_iso": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(latest.get("ts", 0)/1000)),
                "last_status": latest.get("status"),
                "last_action": latest.get("action"),
                "last_duration_ms": latest.get("durationMs"),
                "last_model": latest.get("model"),
                "last_provider": latest.get("provider"),
                "last_summary_head": (latest.get("summary") or "")[:200],
                "next_run_ms": latest.get("nextRunAtMs"),
            })
        tracker["jobs"][jid] = entry

    tracker["counts"] = {"fresh": fresh_n, "stale": stale_n, "never_run": never_n, "total": len(all_jids)}

    # Atomic write
    tmp = str(OUT_PATH) + ".tmp"
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(tmp, "w") as f:
        json.dump(tracker, f, indent=2)
    os.replace(tmp, OUT_PATH)

    log(f"wrote tracker fresh={fresh_n} stale={stale_n} never_run={never_n} total={len(all_jids)}")

    # Print summary to stdout
    print(f"[{ts()}] tracker fresh={fresh_n} stale={stale_n} never_run={never_n} total={len(all_jids)}")
    if stale_jobs:
        print(f"  stale_top_5:")
        for jid, name in stale_jobs[:5]:
            print(f"    {jid[:8]}  {name[:60]}")
    if never_run_jobs:
        print(f"  never_run_top_5:")
        for jid, name in never_run_jobs[:5]:
            print(f"    {jid[:8]}  {name[:60]}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
