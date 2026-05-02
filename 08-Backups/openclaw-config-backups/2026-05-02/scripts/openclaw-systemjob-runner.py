#!/usr/bin/env python3
"""Run migrated OpenClaw cron jobs as deterministic shell jobs.

The native OpenClaw 2026.4.24 cron payload kinds are systemEvent and
agentTurn. This runner handles jobs that were intentionally disabled in
jobs.json and annotated with a top-level systemJob object.
"""

from __future__ import annotations

import argparse
import fcntl
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path
from typing import Any


JOBS_JSON = Path(os.environ.get("OPENCLAW_CRON_JOBS_JSON", "/home/piet/.openclaw/cron/jobs.json"))
RUNS_DIR = Path(os.environ.get("OPENCLAW_CRON_RUNS_DIR", "/home/piet/.openclaw/cron/runs"))
LOCK_FILE = Path(os.environ.get("OPENCLAW_SYSTEMJOB_LOCK", "/tmp/openclaw-systemjob-runner.lock"))


def now_ms() -> int:
    return int(time.time() * 1000)


def load_jobs() -> tuple[dict[str, Any] | list[Any], list[dict[str, Any]]]:
    data = json.loads(JOBS_JSON.read_text(encoding="utf-8"))
    jobs = data if isinstance(data, list) else data.get("jobs", [])
    if not isinstance(jobs, list):
        raise RuntimeError("jobs.json has no jobs list")
    return data, jobs


def save_jobs(data: dict[str, Any] | list[Any]) -> None:
    proposed = JOBS_JSON.with_name(f"{JOBS_JSON.name}.proposed")
    proposed.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    proposed.replace(JOBS_JSON)


def find_job(jobs: list[dict[str, Any]], job_id: str) -> dict[str, Any]:
    for job in jobs:
        if isinstance(job, dict) and str(job.get("id") or "") == job_id:
            return job
    raise RuntimeError(f"job not found: {job_id}")


def command_from_config(system_job: dict[str, Any]) -> list[str]:
    command = system_job.get("command")
    if isinstance(command, list) and all(isinstance(item, str) and item for item in command):
        return command
    if isinstance(command, str) and command.strip():
        return [command.strip()]
    script = system_job.get("script")
    if isinstance(script, str) and script.strip():
        return [script.strip()]
    raise RuntimeError("systemJob.command or systemJob.script required")


def first_lines(text: str, limit: int) -> str:
    lines = text.splitlines()
    return "\n".join(lines[: max(1, limit)])


def matches(pattern: str | None, text: str) -> bool:
    return bool(pattern and re.search(pattern, text, re.MULTILINE))


def append_run_log(job_id: str, event: dict[str, Any]) -> None:
    RUNS_DIR.mkdir(parents=True, exist_ok=True)
    path = RUNS_DIR / f"{job_id}.jsonl"
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, sort_keys=True) + "\n")


def run_system_job(job: dict[str, Any]) -> dict[str, Any]:
    job_id = str(job.get("id") or "")
    system_job = job.get("systemJob")
    if not isinstance(system_job, dict) or system_job.get("enabled") is not True:
        raise RuntimeError(f"job {job_id} has no enabled systemJob config")

    command = command_from_config(system_job)
    cwd = str(system_job.get("cwd") or "/home/piet")
    timeout_seconds = int(system_job.get("timeoutSeconds") or 120)
    output_lines = int(system_job.get("summaryMaxLines") or 10)
    started = now_ms()
    stdout = ""
    stderr = ""
    error = None
    exit_code: int | None = None

    try:
        proc = subprocess.run(
            command,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        stdout = proc.stdout or ""
        stderr = proc.stderr or ""
        exit_code = proc.returncode
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout if isinstance(exc.stdout, str) else ""
        stderr = exc.stderr if isinstance(exc.stderr, str) else ""
        exit_code = 124
        error = f"timeout after {timeout_seconds}s"
    except Exception as exc:
        exit_code = 127
        error = str(exc)

    ended = now_ms()
    combined = "\n".join(part for part in [stdout.strip(), stderr.strip()] if part)
    success_pattern = system_job.get("successPattern")
    failure_pattern = system_job.get("failurePattern")
    status = "ok" if exit_code == 0 else "error"
    if isinstance(failure_pattern, str) and matches(failure_pattern, combined):
        status = "error"
        error = error or f"matched failurePattern: {failure_pattern}"
    if status == "ok" and isinstance(success_pattern, str) and not matches(success_pattern, combined):
        status = "error"
        error = f"missing successPattern: {success_pattern}"

    summary = first_lines(combined.strip() or f"exit_code={exit_code}", output_lines)
    event: dict[str, Any] = {
        "ts": ended,
        "jobId": job_id,
        "action": "finished",
        "status": status,
        "summary": summary,
        "runAtMs": started,
        "durationMs": max(0, ended - started),
        "exitCode": exit_code,
        "systemJob": True,
        "command": command,
        "cwd": cwd,
        "delivered": False,
        "deliveryStatus": "not-requested",
        "model": "shell",
        "provider": "system",
        "usage": {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        },
    }
    if error:
        event["error"] = error
    append_run_log(job_id, event)
    return event


def update_job_state(job: dict[str, Any], event: dict[str, Any]) -> None:
    state = job.setdefault("state", {})
    if not isinstance(state, dict):
        state = {}
        job["state"] = state
    state["lastRunAtMs"] = event["runAtMs"]
    state["lastStatus"] = event["status"]
    state["lastRunStatus"] = event["status"]
    state["lastDurationMs"] = event["durationMs"]
    state["lastError"] = event.get("error")
    job["updatedAtMs"] = event["ts"]
    system_job = job.setdefault("systemJob", {})
    if isinstance(system_job, dict):
        system_job["lastRunAtMs"] = event["runAtMs"]
        system_job["lastStatus"] = event["status"]
        system_job["lastDurationMs"] = event["durationMs"]
        system_job["lastError"] = event.get("error")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("job_id")
    parser.add_argument(
        "--non-strict-exit",
        action="store_true",
        help="Always exit 0 after writing the cron run log; status remains in JSONL.",
    )
    args = parser.parse_args()

    LOCK_FILE.parent.mkdir(parents=True, exist_ok=True)
    with LOCK_FILE.open("w", encoding="utf-8") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        data, jobs = load_jobs()
        job = find_job(jobs, args.job_id)
        event = run_system_job(job)
        update_job_state(job, event)
        save_jobs(data)

    print(event["summary"])
    if args.non_strict_exit:
        return 0
    return 0 if event["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
