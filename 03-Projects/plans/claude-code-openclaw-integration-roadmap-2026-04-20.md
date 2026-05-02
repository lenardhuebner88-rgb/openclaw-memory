---
title: "Claude Code × OpenClaw Integration Roadmap"
date: 2026-04-20
status: DRAFT
author: Assistant (Claude Sonnet 4.5) + 3 research-agents (claude-code-guide, general-purpose×2)
priority: P1-STRATEGIC
---

# Claude Code × OpenClaw Integration Roadmap

> [!important] Override 2026-05-02
> Die Entscheidung "Do NOT adopt Hermes" ist historisch.
> Aktuelle Entscheidung: Hermes wird nicht als OpenClaw-Ersatz adoptiert, aber als separater Shadow-Debug-Assistant / Break-Glass Companion betrieben.
> Lead-System bleibt OpenClaw/Atlas.
> Siehe: `/home/piet/vault/03-Agents/Hermes/system-overview.md`

**Session context:** User (pieter_pan) runs Claude Code on Windows laptop, operates OpenClaw multi-agent orchestration on a Linux homeserver via SSH. Current pattern introduces ~25 min production-outage risk per week due to friction points (today 2026-04-20 06:00–06:34 UTC incident: config-invalid not detected because no schema-validation feedback loop between laptop and server).

---

## 1. Current Friction Inventory (observed this session)

| # | Friction | Live-Evidence | Cost |
|---|---|---|---|
| 1 | SSH-wrapped heredoc quoting issues | Heute 08:45 UTC: `'` in morning-recovery-report broke bash heredoc | 5 min per incident, low-frequency |
| 2 | No Read/Edit on remote files | Must use `ssh homeserver "cat"` → Claude-tooling limit on output parsing | Medium, every remote-file-inspection |
| 3 | No persistent memory-layer bridge | Facts.jsonl/rules.jsonl/graph.jsonl require SSH+grep to query | Medium-high, every rules-lookup |
| 4 | Config-writes unaudited | 2026-04-20 06:00 UTC: Atlas wrote schema-invalid keys → 25 min outage | 🔴 HIGH (blocks all agent-spawns) |
| 5 | Slash-commands / Skills unused | No `/sprint-dispatch`, `/atlas-status`, `/forge-status` → manual verification each time | Medium, every dispatch |
| 6 | Cron logs require SSH-tail | Session-health, R49-validator, auto-pickup logs — each check = SSH round-trip | Low-medium, continuous |
| 7 | Claude Code context loss at /compact | Session state on laptop, Vault on server, cross-refs break | 🔴 HIGH at every /compact |

---

## 2. Architecture Decision Matrix

### Option A: Hybrid — Claude Code Local + MCP Filesystem + Custom Memory-MCP

**Decision: SELECTED** ✅

```
Laptop (Windows)                          Homeserver (Linux)
├── Claude Code                           ├── OpenClaw runtime
├── ~/.claude/MEMORY.md (compressed)      ├── workspace/ (vault, memory, mission-control)
├── .claude/settings.json                 ├── vault/03-Agents/
├── MCP: fs-homeserver (SSHFS-backed) ────┼──► /mnt/homeserver or direct
├── MCP: vault-memory (custom Python) ────┼──► queries facts/rules/graph
├── Bash tool (SSH) ──────────────────────┼──► raw orchestration commands
└── Hooks: PreBash, PostBash ────────────┴──► pre-flight-sprint-dispatch.sh, audit-loggers
```

**Pros:**
- Keeps laptop as control point
- Read/Edit on remote files = native
- No Anthropic-subscription migration needed
- Hooks enforce gates automatically

**Cons:**
- SSHFS adds one moving part
- Custom vault-memory-MCP requires maintenance

### Option B: Claude Code directly on homeserver

**Decision: REJECTED** ❌ — Anthropic docs don't recommend; breaks IDE integration; tmux-session-management fragile.

### Option C: Full-custom SSH-bridge MCP

**Decision: REJECTED** ❌ — Reinvents MCP registry's existing ssh-filesystem; maintenance burden.

---

## 3. Four-Week Implementation Plan

### Week 1 — Remote Filesystem + Memory Bridge

**Goal:** End of SSH-`cat` era. Read/Edit tools work on `/home/piet/vault/` and `/home/piet/.openclaw/workspace/` directly.

**W1.1 SSHFS Mount (30 min)**
```bash
# Ubuntu on WSL or Windows 11 native
# Option 1: WSL2 mount
sudo apt install sshfs
mkdir -p ~/homeserver
sshfs homeserver:/home/piet ~/homeserver -o IdentityFile=~/.ssh/id_ed25519,reconnect,ServerAliveInterval=15

# Option 2: Windows native via sshfs-win + WinFsp
# https://github.com/winfsp/sshfs-win
# Creates \\sshfs\piet@homeserver\ in Explorer
```

**W1.2 Filesystem-MCP Setup (20 min)**
```json
// C:\Users\Lenar\Neuer Ordner\.claude\settings.local.json
{
  "mcp": {
    "servers": {
      "fs-homeserver": {
        "command": "npx",
        "args": [
          "-y",
          "@modelcontextprotocol/server-filesystem",
          "\\\\sshfs\\piet@homeserver\\home\\piet\\vault",
          "\\\\sshfs\\piet@homeserver\\home\\piet\\.openclaw\\workspace"
        ]
      }
    }
  }
}
```

**W1.3 Custom vault-memory-MCP (3h)**

Skeleton Python server:

```python
#!/usr/bin/env python3
"""vault-memory-mcp: MCP server exposing OpenClaw memory layer to Claude Code."""
import json
import pathlib
import sys
from mcp.server import Server, Tool
from mcp.types import TextContent

server = Server("vault-memory")

WORKSPACE = pathlib.Path("/home/piet/.openclaw/workspace")
FACTS = WORKSPACE / "memory/facts"
RULES = WORKSPACE / "memory/rules.jsonl"
GRAPH = WORKSPACE / "memory/graph.jsonl"

@server.tool()
def query_rule(r_id: str) -> str:
    """Return full rule definition from rules.jsonl (e.g. r_id='R50')."""
    for line in RULES.read_text().splitlines():
        rule = json.loads(line)
        if rule.get("id") == r_id:
            return json.dumps(rule, indent=2)
    return f"Rule {r_id} not found"

@server.tool()
def query_facts(topic: str, top_k: int = 10) -> str:
    """Top-k facts for a topic keyword (simple substring match, ranked by importance)."""
    hits = []
    for jsonl in FACTS.glob("*.jsonl"):
        for line in jsonl.read_text().splitlines():
            f = json.loads(line)
            if topic.lower() in json.dumps(f).lower():
                hits.append((f.get("importance", 0), f))
    hits.sort(reverse=True)
    return json.dumps([h[1] for h in hits[:top_k]], indent=2)

@server.tool()
def graph_edges(source_node: str) -> str:
    """Find all edges originating from source_node in graph.jsonl."""
    edges = [json.loads(l) for l in GRAPH.read_text().splitlines() 
             if source_node.lower() in l.lower()]
    return json.dumps(edges, indent=2)

@server.tool()
def sprint_status() -> str:
    """Summarize current Sprint-K status by scanning the MC tasks.json."""
    tasks = json.load(open(WORKSPACE / "mission-control/data/tasks.json"))
    sprint_k = [t for t in tasks if 'Sprint-K' in t.get('title', '')]
    summary = {'done': 0, 'active': 0, 'failed': 0, 'pending': 0}
    for t in sprint_k:
        s = t.get('status')
        if s == 'done': summary['done'] += 1
        elif s in ('in-progress', 'pending-pickup', 'assigned'): summary['active'] += 1
        elif s in ('failed', 'canceled'): summary['failed'] += 1
        else: summary['pending'] += 1
    return json.dumps(summary)

if __name__ == "__main__":
    server.run()
```

**W1.4 .claude/settings.json Hooks (45 min)**

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash(ssh.*dispatch.*)",
        "hooks": [{
          "type": "command",
          "command": ".claude/hooks/pre-dispatch-gate.sh"
        }]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Bash(ssh.*openclaw.json.*)",
        "hooks": [{
          "type": "command",
          "command": ".claude/hooks/post-config-write-verify.sh"
        }]
      }
    ]
  }
}
```

`pre-dispatch-gate.sh` pipes `pre-flight-sprint-dispatch.sh` output to stdin of the tool, blocks dispatch if YELLOW/RED.
`post-config-write-verify.sh` triggers `openclaw doctor` on server and blocks commit if invalid (this would have caught today's incident).

**W1 Deliverables:**
- [ ] SSHFS mount active
- [ ] fs-homeserver MCP registered
- [ ] vault-memory MCP deployed at ~/.claude/mcp-servers/vault-memory-mcp/
- [ ] 2 hooks in `.claude/settings.json`
- [ ] Can use `Read /mnt/homeserver/vault/03-Agents/xxx.md` natively
- [ ] Tool `mcp__vault-memory__query_rule('R50')` returns full rule

---

### Week 2 — Slash Commands + Skills + Automation

**Goal:** Sprint-dispatch from 5-step-manual to 1-click.

**W2.1 `/sprint-dispatch` slash command**
```
.claude/commands/sprint-dispatch.md
---
description: Atlas Sprint-Dispatch with pre-flight gate + board-task-create + verify
---

$ARGUMENTS format: "sprint-X sub-Y agent-Z"

Steps:
1. Run /mnt/homeserver/home/piet/.openclaw/scripts/pre-flight-sprint-dispatch.sh $PLAN
2. If RED → abort, show reasons
3. If YELLOW → ask operator confirmation
4. If GREEN → POST to MC /api/tasks with full handoff-template
5. PATCH status=assigned, POST /dispatch with agentId
6. Verify receipt=accepted within 60s
```

**W2.2 `/atlas-status` + `/forge-status` + `/board-status`**
Each ~20 LOC slash command. Query via vault-memory MCP's sprint_status() + tasks.json scan.

**W2.3 Skills migration (4h)**
Convert your 3-most-used Atlas workflows to Skills:
- `Atlas-Sprint-Kickoff` (reads plan, creates board task, dispatches, monitors)
- `Atlas-Sprint-Debrief` (generates end-of-sprint report, updates MEMORY.md)  
- `Forge-Task-Retry` (detects failed Forge task, generates retry with lessons-learned)

---

### Week 3 — Claude Design Integration (First Pass, design-only)

**Precondition:** Claude Design is 3 days old (released 2026-04-17). Has NO API/SDK/MCP yet. Anthropic says "integrations in the coming weeks."

**W3.1 Manual design-iteration pipeline:**
1. Feed Mission Control repo to Claude Design (web UI, one-time setup)
2. Design-system auto-extracted (tokens, components)
3. Iterate new dashboard designs in Claude Design
4. Export handoff bundle (HTML/tokens/components)
5. Drop handoff bundle in `vault/03-Agents/design-handoffs/YYYY-MM-DD-NAME/`
6. Claude Code + Pixel agent pick up handoff, generate Next.js components

**W3.2 Target artifacts:**
- Pipeline-Tab v4 visual prototype (→ Pixel implements)
- Mobile-optimization revision (→ Pixel implements)
- Dashboard customization concept (future Sprint)

**NOT YET:**
- Automated token-sync
- MCP-based design queries
- CI integration

**Re-evaluate W4** when Anthropic ships Claude Design API/MCP.

---

### Week 4 — Governance + Observability

**W4.1 Dashboard: .claude/ tooling health**
Simple TUI or markdown-dashboard tracking:
- MCP-servers uptime
- Hook invocations per hour
- Average dispatch→accepted-receipt time
- /sprint-dispatch success rate

**W4.2 R51/R52/R53 deploy (from today's incident)**
Via H13 Sprint-K-Sub once Atlas/Forge are available.

**W4.3 Claude Design re-evaluation**
Check Anthropic status page weekly for MCP/API release.

---

## 4. Rejected Options (with reasoning)

### ❌ Hermes Agent (Nous Research)

**Research findings (agent-verified):**
- Real product, v0.10.0 (2026-04-16)
- Features: 3-layer persistent memory, skill-library, subagent-isolation, cost-routing, 6 messaging integrations, git-worktree-snapshots

**Why not adopt:**

| Hermes Feature | OpenClaw Equivalent | Overlap |
|---|---|---|
| 3-layer memory | Memory-Level-1/2/3 (active) | 95% |
| Skill-library | AGENTS.md Preamble + agent templates | 80% |
| Subagent isolation | Forge/James/Pixel separate sessions | 100% |
| Cost-routing | openclaw.json allowed + fallback-chain | 90% |
| Git-worktree-snapshots | mc-restart-safe + deploy-lock | 70% |
| 6 messaging channels | Discord only | ⚠️ Hermes +5 |

**Deal-breakers:**
- Requires WSL2 (user is primary-Windows); Windows native not supported
- Would duplicate R45/R46/R47/R50 governance → conflict risk
- 1000+ LOC installation vs. 15-LOC OpenRouter-MCP that gives you same cost-routing

**Alternative for debugging-model cost savings:**
Custom 30-LOC OpenRouter-MCP that routes `mcp__debug__analyze(problem)` to DeepSeek/Kimi, returns structured output. Zero governance overlap, Windows-native.

---

## 5. Budget & Effort Estimate

| Task | LOC | Effort | Dependencies |
|---|---|---|---|
| SSHFS mount + test | 0 (config) | 30 min | sshfs-win install on Windows |
| fs-homeserver MCP registration | ~10 LOC JSON | 20 min | W1.1 done |
| vault-memory-MCP Python server | ~200 LOC | 3h | MCP SDK installed |
| 2 hooks (pre-dispatch-gate, post-config-verify) | ~50 LOC bash | 45 min | SSH-config |
| 4 slash-commands | ~300 LOC markdown + shell | 2-3h | W1 done |
| 3 skills migration | ~500 LOC | 4h | W2 done |
| Claude Design first-pass | 0 (UI only) | 2-3h | Claude Pro/Max active |
| Monitoring dashboard | ~150 LOC | 2h | W1-W2 done |
| **Total W1-W4** | **~1200 LOC** | **~18-22h** | — |

---

## 6. Success Metrics

After 30 days, measure:
- [ ] Zero SSH-heredoc quoting incidents (vs. today: 1)
- [ ] <5s median latency for rule/fact lookups (vs. today: ~10s via SSH+grep)
- [ ] Sprint-dispatch end-to-end time: <2 min (vs. today: ~15 min manual)
- [ ] Config-invalid incidents caught by hooks: 100% (vs. today: 0% — 25 min outage)
- [ ] /compact context-loss: reduced (via vault-memory-MCP queries filling gaps)
- [ ] L1-Finalize / H11-style tasks: dispatchable in 1 slash-command

---

## 7. Decision Log

| Date | Decision | Rationale | Rejected alternatives |
|---|---|---|---|
| 2026-04-20 | Hybrid MCP + SSH pattern | Keeps local control, enables remote-native Read/Edit | Full remote Claude Code, custom SSH-bridge |
| 2026-04-20 | Do NOT adopt Hermes | 90%+ feature-overlap with OpenClaw, WSL2-only | Custom OpenRouter-MCP for cost-routing instead |
| 2026-04-20 | Defer Claude Design automation | No API/SDK/MCP yet (3 days old) | Use Claude Design manually W3, re-eval W4 |
| 2026-04-20 | Deploy W1 fixes urgent | Today's 25-min outage proves current friction-cost | Incremental over 2 months |

---

*Related docs:*
- `morning-recovery-report-2026-04-20.md` — incident that motivated W1 urgency
- `sprint-k-h11-session-lock-governance-report-2026-04-20.md` — H11 deploy as positive model for governance additions
- `_VAULT-INDEX.md` — master plan index
