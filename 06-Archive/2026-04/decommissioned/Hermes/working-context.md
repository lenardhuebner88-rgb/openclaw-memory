# Working Context (Hermes)

## Current Focus
- Run Atlas operations with clear routing and low-noise communication.
- Keep OpenClaw stable: worker reliability, timeout handling, model fallback sanity.
- Maintain Mission Control in production mode and continue mobile optimization scope.

## Active Constraints
- Prefer deterministic fixes over speculative changes.
- One decision per cycle, avoid parallel strategic branches.
- Preserve sensitive data boundaries (local-first, no unnecessary external exposure).

## Immediate Watchpoints
- Subagent completion delivery path (`expectsCompletionMessage`) still under verification.
- Long-running cron/worker tasks that repeatedly timeout require redesign, not only timeout inflation.
