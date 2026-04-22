# Claude Code × OpenClaw MCP Setup — Ready-to-Run Skeletons

**Generated:** 2026-04-20 — covers Week 1 of integration roadmap

## Directory Contents

```
mcp-setup-skeletons-2026-04-20/
├── README.md                              ← THIS FILE
├── 01-sshfs-install.md                    ← Mount /home/piet on Windows
├── 02-settings.local.json                 ← Claude Code MCP registrations
├── 03-vault-memory-mcp/
│   ├── server.py                          ← 250-LOC MCP server, Python
│   ├── pyproject.toml                     ← deps (mcp SDK)
│   └── install.sh                         ← one-shot installer
├── 04-hooks/
│   ├── pre-dispatch-gate.sh               ← blocks dispatch if pre-flight RED
│   └── post-config-write-verify.sh        ← validates openclaw.json after any write
└── 05-validation.md                       ← smoke-tests to confirm working
```

## Installation Order

1. **01**: SSHFS mount (30 min, requires sshfs-win download + WinFsp)
2. **02**: Copy `.claude/settings.local.json` into project root, replace paths
3. **03**: `bash 03-vault-memory-mcp/install.sh` (creates venv, installs mcp SDK)
4. **04**: Copy hooks to `.claude/hooks/`, chmod +x
5. **05**: Run smoke-tests — verify all 4 Claude-Code tools work end-to-end

## Estimated Time

- Happy path: 90 min
- With troubleshooting (SSH keys, WinFsp permissions, MCP protocol debugging): 3-4 hours

## Preconditions

- Anthropic Claude Code installed on Windows
- SSH key-based auth to `homeserver` working (no password prompts)
- Python 3.11+ on Windows (for the MCP server)
- WinFsp + sshfs-win installed for native Windows SSHFS

## Success Criteria

After setup, these should work from Claude Code:

| Claude Code Action | Before | After |
|---|---|---|
| `Read /mnt/homeserver/vault/03-Agents/xxx.md` | Error (Windows path) | ✅ Works via SSHFS |
| `Edit vault/03-Agents/plan-2026-04-20.md` | Must use SSH+sed | ✅ Native Edit tool |
| `mcp__vault-memory__query_rule('R50')` | Doesn't exist | ✅ Returns full rule JSON |
| `mcp__vault-memory__query_facts('session-lock', 10)` | Doesn't exist | ✅ Top-10 relevant facts |
| Bash `ssh homeserver "systemctl restart mc"` | Raw exec | ✅ Pre-flight-gate hook intercepts, validates |
| Bash that writes openclaw.json | Raw exec | ✅ Post-hook runs `openclaw doctor`, reverts if invalid |
