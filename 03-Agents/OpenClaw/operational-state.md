# Operational State

## Current
- 2026-05-05 19:32 CEST: Sprint S-Context geplant (Session/Context Management next level).
- Sprint Plan: vault/04-Sprints/planned/2026-05-05_s-context-next-level.md
- Tasks dispatched (P0/P1):
  - T1 (Forge): a633ff1e — QMD OnSessionStart Sync
  - T2 (Atlas): b0da1870 — Bootstrap 16KB Budget
  - T3 (Forge): 4ed8145f — L2 Auto-Sweep
  - T4 (Forge): 91756557 — maxActiveTranscriptBytes 3MB→1MB
- MC/Gateway: healthy (baseline unchanged)

## T10 Session Lifecycle Policy — 2026-05-05 20:30 CEST

Status: draft accepted for operations docs; no runtime/config change made.

Decision matrix:
- NORMAL: context <35%, cacheRead <=250k, totalTokens <=300k, idle irrelevant, no timeout trend -> continue normal work.
- WATCH: context >=35% OR cacheRead >250k OR totalTokens >300k -> keep session; reduce tool-output verbosity, checkpoint concise state, avoid heavy history reads.
- COMPACT-CANDIDATE: context >=50% OR cacheRead >500k OR totalTokens >500k OR cacheRead spike repeats twice within 30min -> prefer explicit checkpoint + measured compaction pilot; no forced compaction during active operator work.
- ROTATE-CANDIDATE: context >=65% OR totalTokens >900k OR cacheRead >900k AND idle >10min AND no active task/operator lock -> write handoff, then rotate only the scoped session.
- STOP/REPORT: repeated timeout/abort (2 in 30min or 3/day), ambiguous session lock, active lock conflict, or compaction causes continuity loss -> stop and report evidence before further lifecycle action.

No-go rules:
- Never rotate active Discord/operator work.
- Never rotate while a task has active workerSessionId/operatorLock/session lock or while a response/run is active.
- Never use rotation as a fix for model, gateway, cron, config, or board-health incidents.
- Never delete sessions/transcripts/checkpoints as part of lifecycle policy without separate explicit approval.

T4 interaction:
- T4 maxActiveTranscriptBytes pilot remains HOLD until this matrix is used as baseline.
- If T4 runs, use 1MB pilot only with before/after metrics: context %, cacheRead, totalTokens, compaction count, timeout/abort count, and operator continuity notes.
- Roll back if compaction frequency, token use, or answer continuity worsens.

Current evaluation:
- Atlas Discord session `agent:main:discord:channel:1486480128576983070`: 96k/272k = 35%, compactions=0, cache currently 95k cached; last visible run done, no abort.
- Policy state: WATCH. No compact, no rotate. Keep session, checkpoint if work continues, reassess after idle >10min or if cache/token spike repeats.
