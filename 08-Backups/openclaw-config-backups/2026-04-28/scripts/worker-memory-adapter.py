#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

ISO_FMT_HINT = "ISO-8601 timestamp"

ALLOWED_WORKER = re.compile(r"^[a-z0-9][a-z0-9\-]{0,63}$")
ALLOWED_FILE = re.compile(r"^[a-zA-Z0-9_\-]+\.(md|jsonl)$")

FILE_POLICY = {
    "progress.md": {"cap": 8 * 1024, "ttl_hours": 48},
    "open-tasks.jsonl": {"cap": 32 * 1024, "ttl_hours": 72},
    "architecture.md": {"cap": 16 * 1024, "ttl_hours": 168},
}

TASK_STATUS = {"pending", "done"}


@dataclass
class Adapter:
    agents_root: Path

    @classmethod
    def from_env(cls) -> "Adapter":
        root = Path(os.environ.get("OPENCLAW_AGENTS_ROOT", "/home/piet/.openclaw/agents")).resolve()
        return cls(root)

    def _validate_worker(self, worker: str) -> str:
        if not ALLOWED_WORKER.match(worker):
            raise ValueError(f"Invalid worker name: {worker}")
        return worker

    def memory_dir(self, worker: str) -> Path:
        worker = self._validate_worker(worker)
        return (self.agents_root / worker / "memory").resolve()

    def safe_memory_path(self, worker: str, filename: str) -> Path:
        if not ALLOWED_FILE.match(filename):
            raise ValueError(f"Invalid filename pattern: {filename}")
        if filename not in FILE_POLICY:
            raise ValueError(f"Filename not allowed: {filename}")
        base = self.memory_dir(worker)
        target = (base / filename).resolve()
        target.relative_to(base)
        return target

    def ensure_memory_dir(self, worker: str) -> Path:
        d = self.memory_dir(worker)
        d.mkdir(parents=True, exist_ok=True)
        try:
            d.chmod(0o700)
        except Exception:
            pass
        return d

    def _write_text_capped(self, worker: str, filename: str, content: str) -> Path:
        path = self.safe_memory_path(worker, filename)
        cap = FILE_POLICY[filename]["cap"]
        self.ensure_memory_dir(worker)
        encoded = content.encode("utf-8")
        if len(encoded) > cap:
            tail = encoded[-cap:]
            content = "[truncated-to-cap]\n" + tail.decode("utf-8", errors="ignore")
        tmp = path.with_suffix(path.suffix + ".tmp")
        tmp.write_text(content, encoding="utf-8")
        try:
            tmp.chmod(0o600)
        except Exception:
            pass
        tmp.replace(path)
        return path

    def write_progress(self, worker: str, content: str) -> Path:
        return self._write_text_capped(worker, "progress.md", content)

    def read_progress(self, worker: str) -> str | None:
        path = self.safe_memory_path(worker, "progress.md")
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8", errors="ignore")

    def write_architecture(self, worker: str, content: str) -> Path:
        return self._write_text_capped(worker, "architecture.md", content)

    def read_architecture(self, worker: str) -> str | None:
        path = self.safe_memory_path(worker, "architecture.md")
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8", errors="ignore")

    def _validate_task_item(self, item: dict[str, Any]) -> dict[str, Any]:
        if set(item.keys()) - {"id", "label", "status", "created", "updated"}:
            raise ValueError("open-task entry contains unsupported fields")
        tid = item.get("id")
        label = item.get("label")
        status = item.get("status")
        created = item.get("created")
        updated = item.get("updated")
        if not isinstance(tid, str) or not tid or len(tid) > 64:
            raise ValueError("open-task entry id invalid")
        if not isinstance(label, str) or not label or len(label) > 256:
            raise ValueError("open-task entry label invalid")
        if status not in TASK_STATUS:
            raise ValueError("open-task entry status invalid")
        for key, val in (("created", created), ("updated", updated)):
            if not isinstance(val, str) or not val:
                raise ValueError(f"open-task entry {key} invalid ({ISO_FMT_HINT})")
        return {"id": tid, "label": label, "status": status, "created": created, "updated": updated}

    def read_task_queue(self, worker: str) -> list[dict[str, Any]]:
        path = self.safe_memory_path(worker, "open-tasks.jsonl")
        if not path.exists():
            return []
        out: list[dict[str, Any]] = []
        for line in path.read_text(encoding="utf-8", errors="ignore").splitlines():
            if not line.strip():
                continue
            raw = json.loads(line)
            if not isinstance(raw, dict):
                raise ValueError("open-task entry must be object")
            out.append(self._validate_task_item(raw))
        return out

    def _queue_to_jsonl(self, tasks: list[dict[str, Any]]) -> str:
        return "\n".join(json.dumps(self._validate_task_item(t), ensure_ascii=False) for t in tasks) + ("\n" if tasks else "")

    def write_task_queue(self, worker: str, tasks: list[dict[str, Any]]) -> Path:
        jsonl = self._queue_to_jsonl(tasks)
        cap = FILE_POLICY["open-tasks.jsonl"]["cap"]
        encoded = jsonl.encode("utf-8")
        if len(encoded) <= cap:
            return self._write_text_capped(worker, "open-tasks.jsonl", jsonl)

        # cap policy: drop done tasks older than 24h first, then oldest pending.
        parsed = [self._validate_task_item(t) for t in tasks]
        cutoff = datetime.now(timezone.utc) - timedelta(hours=24)

        def ts(v: str) -> datetime:
            return datetime.fromisoformat(v.replace("Z", "+00:00"))

        filtered = [
            t for t in parsed
            if not (t["status"] == "done" and ts(t["updated"]) < cutoff)
        ]

        while True:
            jsonl = self._queue_to_jsonl(filtered)
            if len(jsonl.encode("utf-8")) <= cap or not filtered:
                break
            pending_idx = next((i for i, t in enumerate(filtered) if t["status"] == "pending"), None)
            if pending_idx is not None:
                filtered.pop(pending_idx)
            else:
                filtered.pop(0)
        return self._write_text_capped(worker, "open-tasks.jsonl", jsonl)

    def read_resume_bundle(self, worker: str) -> dict[str, Any]:
        return {
            "worker": worker,
            "progress": self.read_progress(worker),
            "tasks": self.read_task_queue(worker),
            "architecture": self.read_architecture(worker),
        }

    def cleanup(self, worker: str | None = None, now: datetime | None = None) -> list[str]:
        now = now or datetime.now(timezone.utc)
        workers: list[str]
        if worker:
            workers = [self._validate_worker(worker)]
        else:
            workers = [p.name for p in self.agents_root.iterdir() if p.is_dir() and ALLOWED_WORKER.match(p.name)]
        removed: list[str] = []
        for w in workers:
            for filename, policy in FILE_POLICY.items():
                p = self.safe_memory_path(w, filename)
                if not p.exists():
                    continue
                age = now - datetime.fromtimestamp(p.stat().st_mtime, tz=timezone.utc)
                if age > timedelta(hours=policy["ttl_hours"]):
                    p.unlink(missing_ok=True)
                    removed.append(str(p))
        return removed


def _self_test() -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="worker-memory-adapter-") as td:
        root = Path(td)
        a = Adapter(root)
        worker = "sre-expert"
        a.ensure_memory_dir(worker)

        # traversal / filename guards
        blocked = []
        for bad in ["../progress.md", "evil.txt", "foo.md", "open-tasks.json"]:
            try:
                a.safe_memory_path(worker, bad)
            except Exception:
                blocked.append(bad)

        a.write_progress(worker, "hello\n" + ("x" * 10000))
        prog = a.read_progress(worker) or ""
        assert "truncated-to-cap" in prog

        now = datetime.now(timezone.utc)
        tasks = [
            {"id": "a", "label": "pending one", "status": "pending", "created": now.isoformat(), "updated": now.isoformat()},
            {"id": "b", "label": "done old", "status": "done", "created": (now - timedelta(days=2)).isoformat(), "updated": (now - timedelta(days=2)).isoformat()},
        ]
        a.write_task_queue(worker, tasks)
        rtasks = a.read_task_queue(worker)
        assert any(t["id"] == "a" for t in rtasks)

        arch = "# Decisions\n\n## One\nDate: now"
        a.write_architecture(worker, arch)

        # TTL cleanup fixture: touch old file
        p = a.safe_memory_path(worker, "progress.md")
        old = (now - timedelta(hours=49)).timestamp()
        os.utime(p, (old, old))
        removed = a.cleanup(worker=worker, now=now)

        return {
            "ok": True,
            "blocked_bad_filenames": blocked,
            "resume_bundle_keys": sorted(a.read_resume_bundle(worker).keys()),
            "removed_count": len(removed),
        }


def main() -> int:
    parser = argparse.ArgumentParser(description="Worker memory adapter (guarded MVP).")
    parser.add_argument("--worker")
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--read-resume", action="store_true")
    parser.add_argument("--cleanup", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        print(json.dumps(_self_test(), ensure_ascii=False, indent=2))
        return 0

    adapter = Adapter.from_env()
    if args.read_resume:
        if not args.worker:
            raise SystemExit("--worker required for --read-resume")
        print(json.dumps(adapter.read_resume_bundle(args.worker), ensure_ascii=False, indent=2))
        return 0
    if args.cleanup:
        removed = adapter.cleanup(worker=args.worker)
        print(json.dumps({"removed": removed, "count": len(removed)}, ensure_ascii=False, indent=2))
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
