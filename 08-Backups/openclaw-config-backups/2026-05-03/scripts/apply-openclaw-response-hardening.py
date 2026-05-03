#!/usr/bin/env python3
"""Re-apply local OpenClaw response hardening after package updates.

OpenClaw 2026.4.27/4.29 keeps Discord typing alive with a fixed default TTL.
Long Atlas/Forge turns can legitimately run longer than that timeout, which
looks like "typing vanished" to the operator. This patch makes the TTL follow
the configured agent timeout while staying idempotent.

OpenClaw 2026.4.29 derives the session-store lock max-hold from the 10s lock
acquire timeout, so live Atlas turns can have their sessions.json lock released
after only 15s while the turn is still valid. Keep the watchdog fast enough to
notice stale locks, but raise the store-lock hold window so legitimate slow
Atlas/Forge turns are not unlocked mid-flight.
"""

from __future__ import annotations

import datetime
import pathlib
import shutil
import sys


DIST_DIR = pathlib.Path("/home/piet/.npm-global/lib/node_modules/openclaw/dist")
BACKUP_DIR = pathlib.Path("/home/piet/backups/2026-05-01-atlas-response-rca")
PATCH_LINE = "\t\ttypingTtlMs: Math.max(timeoutMs + 3e4, 12e4),"
ANCHOR_LINE = "\t\ttypingIntervalSeconds,"
LOCK_WATCHDOG_FROM = "const DEFAULT_WATCHDOG_INTERVAL_MS = 6e4;"
LOCK_WATCHDOG_PREVIOUS_LOCAL = "const DEFAULT_WATCHDOG_INTERVAL_MS = 5e3;"
LOCK_WATCHDOG_TO = "const DEFAULT_WATCHDOG_INTERVAL_MS = 1e3;"
STORE_LOCK_MIN_FROM = "const SESSION_STORE_LOCK_MIN_HOLD_MS = 5e3;"
STORE_LOCK_GRACE_FROM = "const SESSION_STORE_LOCK_TIMEOUT_GRACE_MS = 5e3;"
STORE_LOCK_MIN_TO = "const SESSION_STORE_LOCK_MIN_HOLD_MS = 120e3;"
STORE_LOCK_GRACE_TO = "const SESSION_STORE_LOCK_TIMEOUT_GRACE_MS = 120e3;"


def find_get_reply_files() -> list[pathlib.Path]:
    return sorted(DIST_DIR.glob("get-reply-*.js"))


def backup_file(path: pathlib.Path, suffix: str) -> pathlib.Path:
    stamp = datetime.datetime.now(datetime.UTC).strftime("%Y%m%d-%H%M%S")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    backup = BACKUP_DIR / f"{path.name}.bak-{suffix}-{stamp}"
    shutil.copy2(path, backup)
    return backup


def patch_file(path: pathlib.Path) -> str:
    text = path.read_text()
    if "createTypingController({" not in text:
        return f"skipped-non-controller {path}"
    if PATCH_LINE in text:
        return f"already-patched {path}"
    if ANCHOR_LINE not in text:
        raise RuntimeError(f"anchor not found in {path}")

    backup = backup_file(path, "response-hardening")

    patched = text.replace(ANCHOR_LINE, f"{ANCHOR_LINE}\n{PATCH_LINE}", 1)
    path.write_text(patched)
    return f"patched {path} backup={backup}"


def patch_lock_watchdog() -> str:
    candidates = sorted(DIST_DIR.glob("session-write-lock-*.js"))
    if not candidates:
        raise RuntimeError(f"no session-write-lock bundle found under {DIST_DIR}")
    patched_results = []
    for path in candidates:
        text = path.read_text()
        if LOCK_WATCHDOG_TO in text:
            patched_results.append(f"already-patched {path}")
            continue
        if LOCK_WATCHDOG_FROM in text:
            anchor = LOCK_WATCHDOG_FROM
        elif LOCK_WATCHDOG_PREVIOUS_LOCAL in text:
            anchor = LOCK_WATCHDOG_PREVIOUS_LOCAL
        else:
            patched_results.append(f"skipped-anchor-missing {path}")
            continue
        backup = backup_file(path, "lock-watchdog")
        path.write_text(text.replace(anchor, LOCK_WATCHDOG_TO, 1))
        patched_results.append(f"patched {path} backup={backup}")
    if not any(result.startswith(("patched ", "already-patched ")) for result in patched_results):
        raise RuntimeError("no session-write-lock bundle with watchdog anchor found")
    return "\n".join(patched_results)


def patch_store_lock_hold() -> str:
    candidates = sorted(DIST_DIR.glob("store-*.js"))
    patched_results = []
    for path in candidates:
        text = path.read_text()
        if "SESSION_STORE_LOCK_MIN_HOLD_MS" not in text:
            continue
        if STORE_LOCK_MIN_TO in text and STORE_LOCK_GRACE_TO in text:
            patched_results.append(f"already-patched {path}")
            continue
        if STORE_LOCK_MIN_FROM not in text or STORE_LOCK_GRACE_FROM not in text:
            patched_results.append(f"skipped-store-lock-anchor-missing {path}")
            continue
        backup = backup_file(path, "store-lock-hold")
        patched = text.replace(STORE_LOCK_MIN_FROM, STORE_LOCK_MIN_TO, 1)
        patched = patched.replace(STORE_LOCK_GRACE_FROM, STORE_LOCK_GRACE_TO, 1)
        path.write_text(patched)
        patched_results.append(f"patched {path} backup={backup}")
    if not any(result.startswith(("patched ", "already-patched ")) for result in patched_results):
        raise RuntimeError("no session store bundle with store-lock hold anchors found")
    return "\n".join(patched_results)


def main() -> int:
    files = find_get_reply_files()
    if not files:
        print(f"no get-reply bundle found under {DIST_DIR}", file=sys.stderr)
        return 1

    failed = False
    seen_controller = False
    for path in files:
        try:
            result = patch_file(path)
            if "non-controller" not in result:
                seen_controller = True
            print(result)
        except Exception as exc:
            failed = True
            print(f"failed {path}: {exc}", file=sys.stderr)
    try:
        print(patch_lock_watchdog())
    except Exception as exc:
        failed = True
        print(f"failed session-write-lock watchdog patch: {exc}", file=sys.stderr)
    try:
        print(patch_store_lock_hold())
    except Exception as exc:
        failed = True
        print(f"failed session-store lock hold patch: {exc}", file=sys.stderr)
    if not seen_controller:
        print("no get-reply bundle with createTypingController found", file=sys.stderr)
        return 1
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
