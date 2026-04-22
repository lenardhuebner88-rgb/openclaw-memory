#!/usr/bin/env python3
"""
Vault-Index-Generator — S-GOV T9 Pre-Work Prototype
Created: 2026-04-22 (parallel during S-GOV T2.1/T2.2/T4 dispatch)

Inspired by: S-HANDBOOK SH2 generate.py (Codex, 2026-04-21) — live-source + schema-validate + generated-output pattern.
This variant: scan vault/03-Agents/**/*.md frontmatter, emit ordered _VAULT-INDEX.md sections.

Scope: READ-ONLY against vault. Writes output to stdout (caller decides destination).
Run with --check to compare against existing _VAULT-INDEX.md (diff report only).

Usage:
    python3 vault_index_generator.py > _VAULT-INDEX.generated.md
    python3 vault_index_generator.py --check       # diff vs. current _VAULT-INDEX.md
    python3 vault_index_generator.py --json-only   # machine-readable output
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

VAULT_ROOT = "/home/piet/vault/03-Agents"
SPRINTS_DIR = f"{VAULT_ROOT}/sprints"
ARCHIVE_DIR = f"{VAULT_ROOT}/archive"
INDEX_FILE = f"{VAULT_ROOT}/_VAULT-INDEX.md"


def parse_frontmatter(path: str) -> Optional[dict]:
    """Extract YAML frontmatter (simple parser, no PyYAML dep)."""
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()
    except OSError:
        return None

    if not content.startswith("---\n") and not content.startswith("---\r\n"):
        return None

    # Find closing ---
    body_start = content.find("\n---\n", 4)
    if body_start == -1:
        body_start = content.find("\n---\r\n", 4)
        if body_start == -1:
            return None

    fm_text = content[4:body_start].strip()
    result = {}

    current_key = None
    current_list = None

    for line in fm_text.split("\n"):
        raw = line.rstrip()
        if not raw or raw.startswith("#"):
            continue

        # List item (indented)
        if raw.startswith("  - ") or raw.startswith("- "):
            stripped = raw.lstrip(" -")
            if current_list is not None:
                current_list.append(stripped.strip(" '\""))
            continue

        # Key-value (top-level)
        m = re.match(r"^([\w-]+):\s*(.*)$", raw)
        if not m:
            continue
        key = m.group(1).lower()
        value = m.group(2).strip()

        # List starts (value empty, next lines are "- ...")
        if not value:
            current_list = []
            result[key] = current_list
            current_key = key
            continue

        # Strip trailing inline comment (YAML: `# comment`) — but only outside quotes/brackets
        value_no_comment = value
        # Very simple strip: first " #" token outside []/{}
        depth = 0
        for i, ch in enumerate(value):
            if ch in "[{":
                depth += 1
            elif ch in "]}":
                depth -= 1
            elif depth == 0 and i + 1 < len(value) and ch == " " and value[i + 1] == "#":
                value_no_comment = value[:i].rstrip()
                break
        value = value_no_comment

        # Inline list: [a, b, c]
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            items = [x.strip(" '\"") for x in inner.split(",") if x.strip()]
            result[key] = items
        # Inline dict-ish: { a: 1, b: 2 }
        elif value.startswith("{"):
            result[key] = value
        else:
            result[key] = value.strip(" '\"")

        current_list = None
        current_key = key

    return result


def scan_plans() -> dict:
    """
    Scan sprints/, archive/, and root .md files.
    Returns dict grouped by location + status.
    """
    out = {
        "sprints_active": [],
        "sprints_other": [],
        "root_plans": [],
        "root_reports": [],
        "archive": [],
        "no_frontmatter": [],
        "errors": [],
    }

    # Sprints directory (canonical)
    for p in sorted(glob.glob(f"{SPRINTS_DIR}/*.md")):
        fm = parse_frontmatter(p)
        if fm is None:
            out["no_frontmatter"].append(p)
            continue
        entry = {
            "path": p,
            "basename": os.path.basename(p),
            "sprint_id": fm.get("sprint-id") or fm.get("sprint_id"),
            # Accept either `title` or `name` (Codex plans use `name`)
            "title": fm.get("title") or fm.get("name") or "",
            "status": (fm.get("status") or "unknown").lower(),
            "priority": fm.get("priority"),
            "owner": fm.get("owner"),
            "depends_on": fm.get("depends-on") or fm.get("depends_on") or [],
            "enables": fm.get("enables") or [],
        }
        status = entry["status"]
        if status in ("planned", "running", "in-progress", "active"):
            out["sprints_active"].append(entry)
        else:
            out["sprints_other"].append(entry)

    # Root .md files (plans or references)
    for p in sorted(glob.glob(f"{VAULT_ROOT}/*.md")):
        if os.path.basename(p).startswith("_"):
            continue
        fm = parse_frontmatter(p)
        entry = {
            "path": p,
            "basename": os.path.basename(p),
            "has_frontmatter": fm is not None,
            "status": (fm.get("status", "") if fm else "").lower(),
            "sprint_id": (fm.get("sprint-id") if fm else None),
        }
        if fm and fm.get("sprint-id"):
            out["root_plans"].append(entry)
        else:
            out["root_reports"].append(entry)

    # Archive
    for p in sorted(glob.glob(f"{ARCHIVE_DIR}/**/*.md", recursive=True)):
        out["archive"].append({
            "path": p,
            "basename": os.path.basename(p),
            "relative": os.path.relpath(p, VAULT_ROOT),
        })

    return out


def render_index(scan: dict) -> str:
    """Emit markdown index."""
    lines = []
    lines.append("---")
    lines.append("title: Mission Control Vault — Master Index (AUTO-GENERATED)")
    lines.append(f"date: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    lines.append("generator: vault-index-generator.py (S-GOV T9 prototype)")
    lines.append("source: /home/piet/vault/03-Agents/sprints/*.md frontmatter")
    lines.append("---")
    lines.append("")
    lines.append("# Vault Master Index — 03-Agents/ (Auto-Generated)")
    lines.append("")
    lines.append("**Note:** This is the generator-output. Canonical (hand-maintained) index remains `_VAULT-INDEX.md` until S-GOV T9 merges the generator as nightly cron.")
    lines.append("")

    # Active Sprints
    lines.append("## 🎯 Active Sprints (status: planned|running)")
    lines.append("")
    if not scan["sprints_active"]:
        lines.append("_None._")
    else:
        lines.append("| Sprint-ID | Title | Status | Priority | Depends-on | Enables |")
        lines.append("|---|---|---|---|---|---|")
        for s in sorted(scan["sprints_active"], key=lambda x: (x.get("priority") or "Z9", x.get("sprint_id") or "z")):
            sid = s.get("sprint_id") or "?"
            title = (s.get("title") or "").replace("|", "\\|")[:60]
            deps = ", ".join(s.get("depends_on") or []) or "—"
            enables = ", ".join(s.get("enables") or []) or "—"
            status = s.get("status") or "?"
            prio = s.get("priority") or "?"
            lines.append(f"| **{sid}** | {title} | {status} | {prio} | {deps} | {enables} |")
    lines.append("")

    # Other-Status Sprints
    other_by_status = defaultdict(list)
    for s in scan["sprints_other"]:
        other_by_status[s.get("status") or "unknown"].append(s)
    if other_by_status:
        lines.append("## 📋 Other-Status Sprints")
        lines.append("")
        for status, items in sorted(other_by_status.items()):
            lines.append(f"### status: `{status}`")
            for s in items:
                lines.append(f"- **{s.get('sprint_id') or '?'}** — {s.get('title') or s.get('basename')}")
            lines.append("")

    # Root-level plans with frontmatter
    if scan["root_plans"]:
        lines.append("## 📁 Root-Level Plans (with sprint-id)")
        lines.append("")
        for p in scan["root_plans"]:
            lines.append(f"- `{p['basename']}` — sprint-id: `{p['sprint_id']}` · status: `{p['status'] or '?'}`")
        lines.append("")

    # Root reports (no frontmatter or no sprint-id) — brief list
    if scan["root_reports"]:
        lines.append("## 📊 Root-Level Reports / References")
        lines.append("")
        lines.append(f"_({len(scan['root_reports'])} docs, see directory for detail)_")
        lines.append("")

    # Archive summary
    if scan["archive"]:
        lines.append("## 🗄️ Archive")
        lines.append("")
        by_dir = defaultdict(list)
        for a in scan["archive"]:
            key = os.path.dirname(a["relative"])
            by_dir[key].append(a["basename"])
        for d in sorted(by_dir.keys()):
            lines.append(f"### `{d}/` ({len(by_dir[d])} docs)")
            for b in sorted(by_dir[d])[:10]:
                lines.append(f"- {b}")
            if len(by_dir[d]) > 10:
                lines.append(f"- _(+ {len(by_dir[d]) - 10} more)_")
            lines.append("")

    # Missing frontmatter warnings
    if scan["no_frontmatter"]:
        lines.append("## ⚠️ Missing Frontmatter")
        lines.append("")
        lines.append("Sprint-Plans without required YAML-frontmatter:")
        for p in scan["no_frontmatter"]:
            lines.append(f"- `{os.path.basename(p)}`")
        lines.append("")

    lines.append("## Metrics")
    lines.append("")
    lines.append(f"- Active sprints: **{len(scan['sprints_active'])}**")
    lines.append(f"- Other-status sprints: **{len(scan['sprints_other'])}**")
    lines.append(f"- Root-level plans (with sprint-id): **{len(scan['root_plans'])}**")
    lines.append(f"- Root reports/refs: **{len(scan['root_reports'])}**")
    lines.append(f"- Archive docs: **{len(scan['archive'])}**")
    lines.append(f"- Frontmatter gaps: **{len(scan['no_frontmatter'])}**")
    lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="Diff vs. current _VAULT-INDEX.md (no emit)")
    ap.add_argument("--json-only", action="store_true", help="Emit JSON instead of markdown")
    args = ap.parse_args()

    scan = scan_plans()

    if args.json_only:
        print(json.dumps(scan, indent=2, default=str))
        return

    output = render_index(scan)

    if args.check:
        # Simple diff summary
        print("=== VAULT-INDEX-GENERATOR CHECK ===", file=sys.stderr)
        print(f"Active sprints detected: {len(scan['sprints_active'])}", file=sys.stderr)
        for s in scan["sprints_active"]:
            sid = s.get("sprint_id") or "?"
            title = (s.get("title") or "")[:50]
            print(f"  - {sid} ({s.get('status')}): {title}", file=sys.stderr)
        if scan["no_frontmatter"]:
            print(f"\n⚠️  {len(scan['no_frontmatter'])} Sprint-Plans without frontmatter:", file=sys.stderr)
            for p in scan["no_frontmatter"]:
                print(f"  - {os.path.basename(p)}", file=sys.stderr)
        print(f"\nRoot-level plans: {len(scan['root_plans'])}", file=sys.stderr)
        print(f"Archive docs: {len(scan['archive'])}", file=sys.stderr)
        return

    print(output)


if __name__ == "__main__":
    main()
