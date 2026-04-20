# Smoke-Tests to Validate MCP Setup

After running all install-steps (01–04), these 5 tests should pass:

## Test 1: SSHFS Mount Reachable

```powershell
# Windows:
dir \\sshfs\piet@homeserver\home\piet\vault\03-Agents\*.md | select-object -First 3

# Expected output: 3 recent vault markdown files
```

## Test 2: Filesystem-MCP via Claude Code

In Claude Code prompt:
```
Read \\sshfs\piet@homeserver\home\piet\vault\03-Agents\morning-recovery-report-2026-04-20.md (first 20 lines)
```

**Expected:** Native `Read` tool returns the file's first 20 lines. No SSH wrapping needed.

## Test 3: vault-memory-MCP Server Runs Standalone

```bash
cd ~/.claude/mcp-servers/vault-memory-mcp
source .venv/bin/activate
VAULT_MEMORY_WORKSPACE=/home/piet/.openclaw/workspace python server.py
```

**Expected:** Server starts, listens on stdin/stdout. Send JSON-RPC request:

```json
{"jsonrpc":"2.0","id":1,"method":"tools/list"}
```

**Expected:** Returns list with 7 tools (query_rule, query_facts, graph_edges, sprint_status, search_kb, recent_facts, r49_violations).

## Test 4: vault-memory-MCP via Claude Code

In Claude Code prompt:
```
Use mcp__vault-memory__query_rule with r_id="R50"
```

**Expected:** Returns full R50 JSON (Session-Lock-Governance rule from workspace/memory/rules.jsonl).

## Test 5: Pre-Dispatch Hook Fires

In Claude Code, trigger a Bash command that matches pattern:
```
Bash: echo "simulating curl POST http://localhost:3000/api/tasks/fake/dispatch"
```

**Expected:** Hook runs, `pre-flight-sprint-dispatch.sh` executes on server, returns exit code. Claude Code shows the hook's message (GREEN/YELLOW/RED verdict).

## Test 6: Post-Config-Write Hook Fires

In Claude Code:
```
Bash: ssh homeserver "touch /home/piet/.openclaw/openclaw.json"  # no-op but matches pattern
```

**Expected:** Hook runs, triggers `openclaw doctor` on server, reports current config health.

## Troubleshooting

| Symptom | Likely Cause | Fix |
|---|---|---|
| `Read` gives "file not found" on SSHFS path | Mount not active | Re-run `net use` or `sshfs` mount |
| `mcp__vault-memory__*` tools don't appear | Server not registered or crashed | Check `.claude/settings.local.json`, run server standalone |
| Hook doesn't fire | Matcher pattern doesn't match | Check `jq` query against tool_input shape |
| Hook says "pre-flight error" | SSH auth failed from hook | Ensure `ssh homeserver` works without password |
| MCP server says `mcp` module missing | venv not activated | Re-run `install.sh` |

## Rollback

If anything breaks:

1. Remove `.claude/settings.local.json` (keep `.claude/settings.json`)
2. Unmount SSHFS: `net use \\sshfs\piet@homeserver\home\piet /delete` (Windows)
3. Back to old SSH-heredoc pattern — zero data loss since all operations use native filesystem

## Success Metric

After setup, the next `/sprint-dispatch` command should:

- Take < 2 min end-to-end (vs. current ~15 min)
- Zero quote-escaping failures
- Pre-flight gate runs automatically
- Config-invalid catches automatic
