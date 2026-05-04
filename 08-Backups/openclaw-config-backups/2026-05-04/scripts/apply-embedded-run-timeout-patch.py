#!/usr/bin/env python3
"""Re-apply local OpenClaw embedded-run timeout budget patch after package updates.

This keeps huebners' hotfix persistent across OpenClaw npm bundle rewrites:
- embedded run outer command-lane timeout grace: 30s -> 10min
- stuck-session active embedded-run abort/drain eligibility: 15min

Idempotent and startup-safe: if anchors are missing it logs WARN and exits 0 so
the gateway can still start; the regression checker remains the hard verification
gate.
"""

from __future__ import annotations

import datetime as _dt
import pathlib
import shutil

DIST_DIR = pathlib.Path("/home/piet/.npm-global/lib/node_modules/openclaw/dist")
BACKUP_DIR = pathlib.Path("/home/piet/backups/openclaw-embedded-run-timeout-patch")

OLD_GRACE = "const EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS = 3e4;"
NEW_GRACE = (
    "// Keep the outer command-lane cap comfortably above the inner per-attempt\n"
    "// model timeout. Timeout-compaction and fallback/retry happen *after* an\n"
    "// inner attempt has already consumed params.timeoutMs; a 30s grace killed\n"
    "// healthy recovery paths with CommandLaneTaskTimeoutError at 330s.\n"
    "const EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS = 10 * 60 * 1e3;"
)
NEW_GRACE_MARKERS = (
    "const EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS = 10 * 60 * 1e3;",
    "const EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS = 6e5;",
)

ACTIVE_ABORT_CONST = "const ACTIVE_EMBEDDED_RUN_ABORT_ELIGIBLE_MS = 15 * 60 * 1e3;"
ACTIVE_ABORT_COMMENT = (
    "// Do not abort legitimate long Codex turns at the first stuck warning. If the\n"
    "// diagnostic state still looks stuck after the full embedded lane budget, allow\n"
    "// the recovery runtime to abort/drain and force-clear stale embedded handles."
)
DIAG_INSERT_ANCHOR = "const RECENT_DIAGNOSTIC_ACTIVITY_MS = 12e4;"
OLD_ACTIVE_CHECKS = (
    "allowActiveAbort: true",
    "allowActiveAbort: ageMs > stuckSessionWarnMs",
)
NEW_ACTIVE_CHECK = "allowActiveAbort: ageMs >= ACTIVE_EMBEDDED_RUN_ABORT_ELIGIBLE_MS"


def backup(path: pathlib.Path, suffix: str) -> pathlib.Path:
    stamp = _dt.datetime.now(_dt.UTC).strftime("%Y%m%dT%H%M%SZ")
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    dest = BACKUP_DIR / f"{path.name}.bak-{suffix}-{stamp}"
    shutil.copy2(path, dest)
    return dest


def patch_embedded_bundle() -> list[str]:
    results: list[str] = []
    candidates = sorted(DIST_DIR.glob("pi-embedded-*.js"))
    if not candidates:
        return [f"WARN no pi-embedded bundle found under {DIST_DIR}"]
    for path in candidates:
        text = path.read_text()
        if "EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS" not in text:
            results.append(f"skip no-grace-symbol {path}")
            continue
        if any(marker in text for marker in NEW_GRACE_MARKERS):
            results.append(f"already-patched embedded-grace {path}")
            continue
        if OLD_GRACE not in text:
            results.append(f"WARN embedded-grace-anchor-missing {path}")
            continue
        b = backup(path, "embedded-lane-timeout")
        path.write_text(text.replace(OLD_GRACE, NEW_GRACE, 1))
        results.append(f"patched embedded-grace {path} backup={b}")
    return results


def patch_diagnostic_bundle() -> list[str]:
    results: list[str] = []
    candidates = sorted(DIST_DIR.glob("diagnostic-*.js"))
    if not candidates:
        return [f"WARN no diagnostic bundle found under {DIST_DIR}"]
    for path in candidates:
        text = path.read_text()
        if "allowActiveAbort" not in text:
            results.append(f"skip no-active-abort-call {path}")
            continue
        changed = False
        if ACTIVE_ABORT_CONST not in text:
            if DIAG_INSERT_ANCHOR not in text:
                results.append(f"WARN diagnostic-const-anchor-missing {path}")
                continue
            text = text.replace(
                DIAG_INSERT_ANCHOR,
                f"{ACTIVE_ABORT_COMMENT}\n{ACTIVE_ABORT_CONST}\n{DIAG_INSERT_ANCHOR}",
                1,
            )
            changed = True
        if NEW_ACTIVE_CHECK not in text:
            old = next((candidate for candidate in OLD_ACTIVE_CHECKS if candidate in text), None)
            if old is None:
                results.append(f"WARN diagnostic-active-check-anchor-missing {path}")
                continue
            text = text.replace(old, NEW_ACTIVE_CHECK, 1)
            changed = True
        if not changed:
            results.append(f"already-patched active-abort-drain {path}")
            continue
        b = backup(path, "active-embedded-recovery")
        path.write_text(text)
        results.append(f"patched active-abort-drain {path} backup={b}")
    return results


def main() -> int:
    if not DIST_DIR.exists():
        print(f"WARN dist dir missing: {DIST_DIR}")
        return 0
    for line in patch_embedded_bundle() + patch_diagnostic_bundle():
        print(line)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
