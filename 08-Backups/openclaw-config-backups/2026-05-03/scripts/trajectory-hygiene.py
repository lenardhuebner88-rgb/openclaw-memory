#!/usr/bin/env python3
"""Rotate oversized OpenClaw trajectory logs out of active session context."""

from __future__ import annotations

import argparse
import subprocess
import time
from pathlib import Path


DEFAULT_ROOT = Path("/home/piet/.openclaw/agents")
DEFAULT_THRESHOLD = 5 * 1024 * 1024
DEFAULT_MIN_AGE_SEC = 120


def file_is_open(path: Path) -> bool:
    try:
        result = subprocess.run(
            ["lsof", "--", str(path)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    except FileNotFoundError:
        return False
    return result.returncode == 0


def iter_trajectory_files(root: Path):
    for path in root.glob("*/sessions/*.trajectory.jsonl"):
        if path.is_file():
            yield path


def archive_target(path: Path) -> Path:
    agent_dir = path.parents[1]
    archive_dir = agent_dir / "sessions-archive"
    stamp = time.strftime("%Y%m%d-%H%M%S")
    return archive_dir / f"{path.name}.archived-{stamp}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    parser.add_argument("--threshold-bytes", type=int, default=DEFAULT_THRESHOLD)
    parser.add_argument("--min-age-sec", type=int, default=DEFAULT_MIN_AGE_SEC)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    now = time.time()
    rotated = 0
    skipped = 0

    for path in sorted(iter_trajectory_files(args.root)):
        stat = path.stat()
        if stat.st_size <= args.threshold_bytes:
            continue

        age_sec = now - stat.st_mtime
        if age_sec < args.min_age_sec:
            print(
                f"SKIP recent size={stat.st_size} ageSec={age_sec:.0f} path={path}"
            )
            skipped += 1
            continue

        if file_is_open(path):
            print(f"SKIP open size={stat.st_size} path={path}")
            skipped += 1
            continue

        target = archive_target(path)
        print(f"ARCHIVE size={stat.st_size} path={path} -> {target}")
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            path.rename(target)
        rotated += 1

    print(f"SUMMARY rotated={rotated} skipped={skipped} dryRun={args.dry_run}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
