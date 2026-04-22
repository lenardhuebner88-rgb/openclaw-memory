#!/usr/bin/env python3
"""
vault-memory-mcp: Model Context Protocol server exposing OpenClaw memory layer.

Tools:
  - query_rule(r_id)          → full rule JSON from rules.jsonl
  - query_facts(topic, k=10)  → top-k facts by importance for a topic substring
  - graph_edges(source)        → edges originating from source_node in graph.jsonl
  - sprint_status()            → Sprint-K completion matrix from MC tasks.json
  - search_kb(query, k=5)     → top-k KB-articles matching query
  - recent_facts(since_iso, k=20) → facts appended since timestamp
  - r49_violations(hours=24)  → recent R49 claim-validator warnings

Config via env:
  VAULT_MEMORY_WORKSPACE  → path to workspace/ (default: /home/piet/.openclaw/workspace)

Tested against: mcp==1.0.0 on Python 3.11+
"""

import json
import os
import pathlib
import subprocess
from datetime import datetime, timedelta, timezone

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

server = Server("vault-memory")

WORKSPACE = pathlib.Path(os.environ.get(
    "VAULT_MEMORY_WORKSPACE",
    "/home/piet/.openclaw/workspace"
))
FACTS_DIR = WORKSPACE / "memory" / "facts"
RULES_FILE = WORKSPACE / "memory" / "rules.jsonl"
GRAPH_FILE = WORKSPACE / "memory" / "graph.jsonl"
KB_DIR = pathlib.Path("/home/piet/vault/03-Agents/kb")
MC_TASKS = WORKSPACE / "mission-control" / "data" / "tasks.json"


# ----- helpers -----

def _read_jsonl(path: pathlib.Path):
    if not path.exists():
        return []
    items = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return items


# ----- tools -----

@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="query_rule", description="Return full rule definition from rules.jsonl",
             inputSchema={"type": "object", "properties": {"r_id": {"type": "string"}}, "required": ["r_id"]}),
        Tool(name="query_facts", description="Top-k facts for a topic substring, ranked by importance",
             inputSchema={"type": "object", "properties": {"topic": {"type": "string"}, "k": {"type": "integer", "default": 10}}, "required": ["topic"]}),
        Tool(name="graph_edges", description="Find all graph edges for source_node",
             inputSchema={"type": "object", "properties": {"source_node": {"type": "string"}}, "required": ["source_node"]}),
        Tool(name="sprint_status", description="Summarize current Sprint-K completion matrix",
             inputSchema={"type": "object", "properties": {}}),
        Tool(name="search_kb", description="Top-k KB-articles matching query substring",
             inputSchema={"type": "object", "properties": {"query": {"type": "string"}, "k": {"type": "integer", "default": 5}}, "required": ["query"]}),
        Tool(name="recent_facts", description="Facts appended since iso-timestamp",
             inputSchema={"type": "object", "properties": {"since_iso": {"type": "string"}, "k": {"type": "integer", "default": 20}}, "required": ["since_iso"]}),
        Tool(name="r49_violations", description="R49 claim-validator warnings in last N hours",
             inputSchema={"type": "object", "properties": {"hours": {"type": "integer", "default": 24}}}),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        if name == "query_rule":
            r_id = arguments["r_id"]
            for rule in _read_jsonl(RULES_FILE):
                if rule.get("id") == r_id:
                    return [TextContent(type="text", text=json.dumps(rule, indent=2))]
            return [TextContent(type="text", text=f"Rule {r_id} not found")]

        if name == "query_facts":
            topic = arguments["topic"].lower()
            k = arguments.get("k", 10)
            hits = []
            for jsonl in FACTS_DIR.glob("*.jsonl"):
                for fact in _read_jsonl(jsonl):
                    if topic in json.dumps(fact).lower():
                        hits.append((fact.get("importance", 0), fact))
            hits.sort(reverse=True, key=lambda x: x[0])
            return [TextContent(type="text", text=json.dumps([h[1] for h in hits[:k]], indent=2))]

        if name == "graph_edges":
            source = arguments["source_node"].lower()
            edges = [e for e in _read_jsonl(GRAPH_FILE)
                     if source in json.dumps(e).lower()]
            return [TextContent(type="text", text=json.dumps(edges, indent=2))]

        if name == "sprint_status":
            tasks_data = json.loads(MC_TASKS.read_text(encoding="utf-8"))
            tasks = tasks_data if isinstance(tasks_data, list) else tasks_data.get("tasks", [])
            active_sprints = {}
            for t in tasks:
                title = t.get("title", "")
                if "Sprint-" in title:
                    sprint = title.split(":", 1)[0].strip()
                    active_sprints.setdefault(sprint, {"done": 0, "active": 0, "failed": 0})
                    s = t.get("status")
                    if s == "done":
                        active_sprints[sprint]["done"] += 1
                    elif s in ("in-progress", "pending-pickup", "assigned"):
                        active_sprints[sprint]["active"] += 1
                    elif s in ("failed", "canceled"):
                        active_sprints[sprint]["failed"] += 1
            return [TextContent(type="text", text=json.dumps(active_sprints, indent=2))]

        if name == "search_kb":
            query = arguments["query"].lower()
            k = arguments.get("k", 5)
            hits = []
            for md in KB_DIR.glob("*.md"):
                txt = md.read_text(encoding="utf-8").lower()
                score = txt.count(query)
                if score > 0:
                    hits.append((score, md.name, md.read_text(encoding="utf-8")[:1500]))
            hits.sort(reverse=True, key=lambda x: x[0])
            return [TextContent(type="text", text=json.dumps(
                [{"file": h[1], "score": h[0], "preview": h[2]} for h in hits[:k]],
                indent=2))]

        if name == "recent_facts":
            since = datetime.fromisoformat(arguments["since_iso"].replace("Z", "+00:00"))
            k = arguments.get("k", 20)
            hits = []
            for jsonl in FACTS_DIR.glob("*.jsonl"):
                for fact in _read_jsonl(jsonl):
                    ts_str = fact.get("timestamp", "")
                    try:
                        ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
                        if ts >= since:
                            hits.append((ts, fact))
                    except ValueError:
                        continue
            hits.sort(reverse=True, key=lambda x: x[0])
            return [TextContent(type="text", text=json.dumps([h[1] for h in hits[:k]], indent=2))]

        if name == "r49_violations":
            hours = arguments.get("hours", 24)
            cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
            log_path = WORKSPACE / "memory" / "r49-validator.log"
            if not log_path.exists():
                return [TextContent(type="text", text="[]")]
            violations = []
            for line in log_path.read_text(encoding="utf-8").splitlines()[-500:]:
                if "WARNING" in line or "CRITICAL" in line:
                    violations.append(line)
            return [TextContent(type="text", text=json.dumps(violations[-20:], indent=2))]

        return [TextContent(type="text", text=f"Unknown tool: {name}")]

    except Exception as e:
        return [TextContent(type="text", text=f"Error: {type(e).__name__}: {e}")]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
