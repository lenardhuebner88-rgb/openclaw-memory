# Agent Coordination Board

Every AI coding agent that starts work on this vault creates one file here for the duration of its session. See `/AGENTS.md` §3 at the repo root for the schema.

## Live sessions

```dataview
TABLE started, ended, task, file.link AS session
FROM "03-Agents/_coordination"
WHERE agent AND ended = null
SORT started DESC
```

## Last 20 completed sessions

```dataview
TABLE started, ended, agent, task
FROM "03-Agents/_coordination"
WHERE agent AND ended != null
SORT ended DESC
LIMIT 20
```

Dataview required. Without Dataview, just `ls 03-Agents/_coordination/ | grep -E '^2026-.*\.md$'` and grep for `ended: null`.
