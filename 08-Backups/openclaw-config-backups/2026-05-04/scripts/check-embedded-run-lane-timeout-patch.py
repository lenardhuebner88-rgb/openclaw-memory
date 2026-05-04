#!/usr/bin/env python3
"""Regression checks for OpenClaw embedded-run timeout/stuck-recovery patches."""
from pathlib import Path
import sys

PI = Path('/home/piet/.npm-global/lib/node_modules/openclaw/dist/pi-embedded-rWtLEwl7.js')
DIAG = Path('/home/piet/.npm-global/lib/node_modules/openclaw/dist/diagnostic-oEUVZa4J.js')
pi = PI.read_text(errors='replace')
diag = DIAG.read_text(errors='replace')

checks = {
    'old_30s_constant_absent': 'const EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS = 3e4;' not in pi,
    'new_10min_constant_present': 'const EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS = 10 * 60 * 1e3;' in pi,
    'resolver_still_adds_grace': 'return Math.floor(timeoutMs) + EMBEDDED_RUN_LANE_TIMEOUT_GRACE_MS;' in pi,
    'lane_timeout_still_applied': 'taskTimeoutMs: laneTaskTimeoutMs' in pi,
    'active_abort_threshold_present': 'const ACTIVE_EMBEDDED_RUN_ABORT_ELIGIBLE_MS = 15 * 60 * 1e3;' in diag,
    'active_abort_passed_to_recovery': 'allowActiveAbort: ageMs >= ACTIVE_EMBEDDED_RUN_ABORT_ELIGIBLE_MS' in diag,
}

for name, ok in checks.items():
    print(f'{name}={ok}')

if not all(checks.values()):
    sys.exit(1)

inner_ms = 300_000
outer_ms = inner_ms + 10 * 60 * 1000
active_abort_ms = 15 * 60 * 1000
print(f'inner_ms={inner_ms}')
print(f'outer_ms={outer_ms}')
print(f'outer_minutes={outer_ms/60000:.1f}')
print(f'active_abort_ms={active_abort_ms}')
print(f'active_abort_minutes={active_abort_ms/60000:.1f}')
assert outer_ms == 900_000
assert active_abort_ms == outer_ms
