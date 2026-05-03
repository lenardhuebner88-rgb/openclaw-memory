#!/usr/bin/env python3
from __future__ import annotations

import argparse
import hashlib
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

STATUS_ORDER = {
    "running": 0,
    "planned": 1,
    "done": 2,
    "superseded": 3,
    "archived": 4,
    "unknown": 5,
}

MANUAL_START = "<!-- VAULT-INDEX:MANUAL-OVERRIDES:START -->"
MANUAL_END = "<!-- VAULT-INDEX:MANUAL-OVERRIDES:END -->"


@dataclass
class DocEntry:
    path: str
    title: str
    sprint_id: str | None
    status: str
    owner: str
    supersedes: str


def _parse_frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}
    blob = text[4:end]
    try:
        data = yaml.safe_load(blob) or {}
    except Exception:
        return {}
    return data if isinstance(data, dict) else {}


def _owner_to_text(owner: Any) -> str:
    if owner is None:
        return "-"
    if isinstance(owner, str):
        return owner
    if isinstance(owner, list):
        return ", ".join(str(x) for x in owner)
    if isinstance(owner, dict):
        return ", ".join(f"{k}:{v}" for k, v in owner.items())
    return str(owner)


def _supersedes_to_text(value: Any) -> str:
    if value is None:
        return "-"
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return ", ".join(str(x) for x in value)
    return str(value)


def load_entries(vault_root: Path) -> list[DocEntry]:
    entries: list[DocEntry] = []
    for p in sorted(vault_root.rglob("*.md")):
        if p.name == "_VAULT-INDEX.md":
            continue
        if p.name == "vault-index.override.md":
            continue
        rel = p.relative_to(vault_root).as_posix()
        text = p.read_text(encoding="utf-8", errors="replace")
        fm = _parse_frontmatter(text)
        status = str(fm.get("status", "unknown")).strip().lower() or "unknown"
        if status not in STATUS_ORDER:
            status = "unknown"
        title = str(fm.get("title") or fm.get("name") or p.stem)
        sprint_id = fm.get("sprint-id")
        entries.append(
            DocEntry(
                path=rel,
                title=title,
                sprint_id=str(sprint_id) if sprint_id is not None else None,
                status=status,
                owner=_owner_to_text(fm.get("owner")),
                supersedes=_supersedes_to_text(fm.get("supersedes")),
            )
        )
    entries.sort(key=lambda e: (STATUS_ORDER.get(e.status, 99), (e.sprint_id or "ZZZ"), e.path))
    return entries


def extract_manual(existing_index: Path, override_file: Path) -> str:
    if override_file.exists():
        return override_file.read_text(encoding="utf-8", errors="replace").rstrip()
    if not existing_index.exists():
        return ""
    body = existing_index.read_text(encoding="utf-8", errors="replace")
    s = body.find(MANUAL_START)
    e = body.find(MANUAL_END)
    if s == -1 or e == -1 or e < s:
        return ""
    return body[s + len(MANUAL_START) : e].strip("\n")


def render(entries: list[DocEntry], manual: str) -> str:
    lines: list[str] = []
    lines.append("---")
    lines.append("title: Mission Control Vault — Auto Index")
    lines.append("generator: /home/piet/.openclaw/scripts/vault-index-generator.py")
    lines.append("source_root: /home/piet/vault/_agents")
    lines.append("mode: generated")
    lines.append("---")
    lines.append("")
    lines.append("# Vault Index — 03-Agents")
    lines.append("")
    lines.append("Dieses Dokument ist generated aus YAML-Frontmatter (`sprint-id`, `status`, `owner`, `supersedes`).")
    lines.append("")

    by_status: dict[str, list[DocEntry]] = {}
    for entry in entries:
        by_status.setdefault(entry.status, []).append(entry)

    for status in ["running", "planned", "done", "superseded", "archived", "unknown"]:
        items = by_status.get(status, [])
        if not items:
            continue
        lines.append(f"## {status.upper()} ({len(items)})")
        lines.append("")
        lines.append("| Sprint-ID | Title | Owner | Supersedes | Path |")
        lines.append("|---|---|---|---|---|")
        for e in items:
            sid = e.sprint_id or "-"
            title = e.title.replace("|", "\\|")
            owner = e.owner.replace("|", "\\|")
            supersedes = e.supersedes.replace("|", "\\|")
            path = f"`{e.path}`"
            lines.append(f"| {sid} | {title} | {owner} | {supersedes} | {path} |")
        lines.append("")

    lines.append(MANUAL_START)
    if manual.strip():
        lines.append(manual.rstrip())
    else:
        lines.append("_Keine manuellen Overrides gesetzt. Optional: `vault-index.override.md` anlegen._")
    lines.append(MANUAL_END)
    lines.append("")
    return "\n".join(lines)


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser(description="Generate /home/piet/vault/_agents/_VAULT-INDEX.md from frontmatter.")
    ap.add_argument("--vault-root", default="/home/piet/vault/_agents")
    ap.add_argument("--output", default="_VAULT-INDEX.md")
    ap.add_argument("--override", default="vault-index.override.md")
    ap.add_argument("--check-idempotence", type=int, default=0)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    root = Path(args.vault_root)
    out = root / args.output
    override = root / args.override

    entries = load_entries(root)
    manual = extract_manual(out, override)
    rendered = render(entries, manual)

    if args.dry_run:
        print(rendered)
        return 0

    out.write_text(rendered, encoding="utf-8")

    idempotent = True
    baseline = sha256_text(rendered)
    runs = max(args.check_idempotence, 0)
    for _ in range(runs):
        entries_n = load_entries(root)
        manual_n = extract_manual(out, override)
        text_n = render(entries_n, manual_n)
        out.write_text(text_n, encoding="utf-8")
        if sha256_text(text_n) != baseline:
            idempotent = False

    print(
        {
            "output": str(out),
            "docs_total": len(entries),
            "idempotence_runs": runs,
            "idempotent": idempotent,
            "sha256": baseline,
        }
    )
    return 0 if idempotent else 2


if __name__ == "__main__":
    raise SystemExit(main())
