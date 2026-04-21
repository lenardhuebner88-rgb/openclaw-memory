#!/usr/bin/env python3
"""Context-Baseline measurement for Atlas sessions.

Reads the 5 most recently modified Atlas session JSONL files under
/home/piet/.openclaw/agents/main/sessions/, extracts token usage &
toolResult metrics, and emits a Markdown report.
"""
import json
import os
import glob
import sys
import statistics
from collections import defaultdict

SESSION_DIR = "/home/piet/.openclaw/agents/main/sessions/"
OUT_PATH = "/home/piet/vault/03-Agents/context-baseline-2026-04-22.md"


def is_primary_session(path: str) -> bool:
    name = os.path.basename(path)
    if not name.endswith(".jsonl"):
        return False
    if ".checkpoint." in name or ".archived." in name:
        return False
    if name.endswith(".lock"):
        return False
    return True


def pick_sessions(n: int = 5):
    files = [
        p
        for p in glob.glob(os.path.join(SESSION_DIR, "*.jsonl"))
        if is_primary_session(p)
    ]
    files.sort(key=os.path.getmtime, reverse=True)
    # only keep "real" sessions with some content
    real = []
    for f in files:
        try:
            if os.path.getsize(f) >= 4096:  # >=4KB filter tiny stubs
                real.append(f)
        except OSError:
            pass
    return real[:n]


def analyze_file(path: str):
    stats = {
        "path": path,
        "session_id": os.path.basename(path).replace(".jsonl", ""),
        "size_bytes": os.path.getsize(path),
        "mtime": os.path.getmtime(path),
        "total_records": 0,
        "user_turns": 0,
        "assistant_turns": 0,
        "input_tokens": [],
        "cache_read": [],
        "cache_write": [],
        "output_tokens": [],
        "total_tokens": [],
        "tool_call_by_id": {},   # call_id -> toolName
        "tool_results": [],      # list of dicts with {call_id, tool_name, size, preview, session_id}
        "tool_result_bytes_total": 0,
    }

    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line in fh:
            line = line.rstrip("\n")
            if not line:
                continue
            stats["total_records"] += 1
            try:
                rec = json.loads(line)
            except Exception:
                continue
            if rec.get("type") != "message":
                continue
            msg = rec.get("message", {})
            role = msg.get("role")
            if role == "user":
                stats["user_turns"] += 1
            elif role == "assistant":
                stats["assistant_turns"] += 1
                u = msg.get("usage") or {}
                # schema: input/output/cacheRead/cacheWrite/totalTokens
                if u:
                    stats["input_tokens"].append(int(u.get("input", 0) or 0))
                    stats["cache_read"].append(int(u.get("cacheRead", 0) or 0))
                    stats["cache_write"].append(int(u.get("cacheWrite", 0) or 0))
                    stats["output_tokens"].append(int(u.get("output", 0) or 0))
                    stats["total_tokens"].append(int(u.get("totalTokens", 0) or 0))
            elif role == "toolResult":
                # flat toolResult record: msg has toolName, toolCallId, content[text]
                inner = msg.get("content") or []
                txt_parts = []
                if isinstance(inner, list):
                    for ib in inner:
                        if isinstance(ib, dict) and ib.get("type") == "text":
                            txt_parts.append(ib.get("text", ""))
                        elif isinstance(ib, str):
                            txt_parts.append(ib)
                elif isinstance(inner, str):
                    txt_parts.append(inner)
                full = "".join(txt_parts)
                size = len(full.encode("utf-8"))
                stats["tool_result_bytes_total"] += size
                preview = full[:100].replace("\n", " ").replace("\r", " ")
                stats["tool_results"].append(
                    {
                        "session_id": stats["session_id"],
                        "call_id": msg.get("toolCallId"),
                        "tool_name": msg.get("toolName") or "(unknown)",
                        "size_bytes": size,
                        "preview": preview,
                    }
                )

            # Also scan content for nested toolCall blocks (assistant messages)
            content = msg.get("content") or []
            if not isinstance(content, list):
                continue
            for block in content:
                if not isinstance(block, dict):
                    continue
                btype = block.get("type")
                if btype == "toolCall":
                    cid = block.get("id")
                    nm = block.get("name")
                    if cid:
                        stats["tool_call_by_id"][cid] = nm
                elif btype == "toolResult":
                    # embedded-form fallback (older schema)
                    inner = block.get("content") or []
                    txt_parts = []
                    if isinstance(inner, list):
                        for ib in inner:
                            if isinstance(ib, dict) and ib.get("type") == "text":
                                txt_parts.append(ib.get("text", ""))
                            elif isinstance(ib, str):
                                txt_parts.append(ib)
                    elif isinstance(inner, str):
                        txt_parts.append(inner)
                    full = "".join(txt_parts)
                    size = len(full.encode("utf-8"))
                    stats["tool_result_bytes_total"] += size
                    preview = full[:100].replace("\n", " ").replace("\r", " ")
                    stats["tool_results"].append(
                        {
                            "session_id": stats["session_id"],
                            "call_id": block.get("toolCallId"),
                            "tool_name": block.get("toolName") or "(unknown)",
                            "size_bytes": size,
                            "preview": preview,
                        }
                    )
    return stats


def median(xs):
    if not xs:
        return 0
    return int(statistics.median(xs))


def sum_safe(xs):
    return int(sum(xs)) if xs else 0


def fmt_kb(n):
    return f"{n/1024:.1f}"


def main():
    sessions = pick_sessions(5)
    if not sessions:
        print("ERROR: no sessions found", file=sys.stderr)
        sys.exit(1)

    per = [analyze_file(p) for p in sessions]

    # Table 1: session sample
    t1_rows = []
    session_sum_input = []
    session_peak = []
    overall_input_sum = 0
    overall_cache_read_sum = 0
    all_tr = []
    total_jsonl_bytes = 0
    total_tr_bytes = 0

    for s in per:
        sid = s["session_id"]
        # In openai-codex schema: usage.input = fresh (non-cached) input tokens,
        # usage.cacheRead = tokens read from prompt-cache. Total presented input
        # to the model per turn is (input + cacheRead). Cache-hit-rate =
        # cacheRead / (input + cacheRead).
        fresh_input = sum_safe(s["input_tokens"])
        cache = sum_safe(s["cache_read"])
        presented = fresh_input + cache
        # per-turn total input presented (for peak/median)
        per_turn_presented = [
            (i + c) for i, c in zip(s["input_tokens"], s["cache_read"])
        ]
        peak = max(per_turn_presented) if per_turn_presented else 0
        med = median(per_turn_presented)
        hit = (cache / presented * 100.0) if presented > 0 else 0.0
        session_sum_input.append(presented)
        session_peak.append(peak)
        overall_input_sum += presented
        overall_cache_read_sum += cache
        total_jsonl_bytes += s["size_bytes"]
        total_tr_bytes += s["tool_result_bytes_total"]
        all_tr.extend(s["tool_results"])
        import datetime as _dt
        mtime_str = _dt.datetime.fromtimestamp(
            s["mtime"], tz=_dt.timezone.utc
        ).strftime("%Y-%m-%d %H:%M UTC")
        total_turns = s["user_turns"] + s["assistant_turns"]
        t1_rows.append(
            f"| `{sid[:8]}...` | {mtime_str} | {total_turns} (U{s['user_turns']}/A{s['assistant_turns']}) | "
            f"{presented:,} | {med:,} | {peak:,} | {hit:.1f}% |"
        )

    # Top-10 tool_result blocks
    all_tr.sort(key=lambda d: d["size_bytes"], reverse=True)
    top10 = all_tr[:10]
    t2_rows = []
    for i, r in enumerate(top10, 1):
        preview = r["preview"].replace("|", "\\|")
        t2_rows.append(
            f"| {i} | `{r['session_id'][:8]}...` | `{r['tool_name']}` | "
            f"{fmt_kb(r['size_bytes'])} | `{preview}` |"
        )

    # Aggregates
    med_session_input = median(session_sum_input)
    med_session_peak = median(session_peak)
    overall_hit = (overall_cache_read_sum / overall_input_sum * 100.0) if overall_input_sum > 0 else 0.0
    tr_share = (total_tr_bytes / total_jsonl_bytes * 100.0) if total_jsonl_bytes > 0 else 0.0

    # Tool-dominance in top-10
    tool_counts = defaultdict(int)
    tool_bytes = defaultdict(int)
    for r in all_tr:
        tool_counts[r["tool_name"]] += 1
        tool_bytes[r["tool_name"]] += r["size_bytes"]
    top_tools_by_bytes = sorted(tool_bytes.items(), key=lambda x: x[1], reverse=True)[:5]

    # Build output
    lines = []
    lines.append("---")
    lines.append("title: Context-Baseline 2026-04-22 — CE1 Pre-Flight")
    lines.append("created: 2026-04-22")
    lines.append("purpose: S-CTX-P0 T2 Baseline-Messung vor clear_tool_uses + compaction deployment")
    lines.append("measurement-scope: 5 aktuellste Atlas-Sessions (agents/main/sessions/*.jsonl)")
    lines.append("---")
    lines.append("")
    lines.append("# Context-Baseline 2026-04-22")
    lines.append("")
    lines.append(f"**Source directory:** `{SESSION_DIR}`")
    lines.append(f"**Sessions analyzed:** {len(per)}  ·  **Total JSONL bytes:** {total_jsonl_bytes:,} ({fmt_kb(total_jsonl_bytes)} KB)")
    lines.append("")
    lines.append("## Session-Sample")
    lines.append("")
    lines.append("| Session-ID | Modified (UTC) | Total Turns | Σ presented_input (fresh+cacheRead) | Median/Turn | Peak/Turn | Cache-Hit-Rate |")
    lines.append("|---|---|---|---|---|---|---|")
    lines.extend(t1_rows)
    lines.append("")
    lines.append("## Top-10 Largest tool_result Blocks")
    lines.append("")
    lines.append("| # | Session | Tool | Size (KB) | First 100 chars |")
    lines.append("|---|---|---|---|---|")
    lines.extend(t2_rows)
    lines.append("")
    lines.append("## Aggregates")
    lines.append("")
    lines.append(f"- **Median session presented_input (fresh+cacheRead, sum over turns):** {med_session_input:,}")
    lines.append(f"- **Median peak-per-session (single turn):** {med_session_peak:,}")
    lines.append(f"- **Overall presented_input (all 5 sessions):** {overall_input_sum:,}")
    lines.append(f"- **Overall cacheRead:** {overall_cache_read_sum:,}")
    lines.append(f"- **Overall Cache-Hit-Rate (cacheRead / presented_input):** {overall_hit:.1f}% (target ≥70%)")
    lines.append(f"- **toolResult-Share of JSONL volume:** {tr_share:.1f}% ({total_tr_bytes:,} / {total_jsonl_bytes:,} bytes)")
    lines.append(f"- **Total tool_result blocks counted:** {len(all_tr):,}")
    lines.append("")
    lines.append("### Tool-Dominance (top 5 by cumulative toolResult bytes)")
    lines.append("")
    lines.append("| Tool | Count | Cumulative (KB) |")
    lines.append("|---|---|---|")
    for name, byts in top_tools_by_bytes:
        lines.append(f"| `{name}` | {tool_counts[name]} | {fmt_kb(byts)} |")
    lines.append("")
    lines.append("## Interpretation")
    lines.append("")

    # interpretation logic
    int_lines = []
    if tr_share >= 80:
        int_lines.append(f"- **toolResult-Anteil-Annahme bestätigt:** Messung {tr_share:.1f}% entspricht dem erwarteten ~85%-Wert. Prioritisiere `clear_tool_uses` bei Top-Tools.")
    elif tr_share >= 60:
        int_lines.append(f"- **toolResult-Anteil-Annahme teilweise bestätigt:** Messung {tr_share:.1f}% liegt unter der 85%-Hypothese, ist aber weiterhin dominanter Einzelfaktor.")
    else:
        int_lines.append(f"- **toolResult-Anteil-Annahme widerlegt:** Nur {tr_share:.1f}% der JSONL-Bytes sind toolResult-Content. Andere Blöcke (thinking, system-messages, toolCalls) dominieren.")
    if overall_hit >= 70:
        int_lines.append(f"- **Cache-Hit-Rate {overall_hit:.1f}% ≥ Ziel 70%** — cache_control-Strategie ist effektiv.")
    elif overall_hit >= 40:
        int_lines.append(f"- **Cache-Hit-Rate {overall_hit:.1f}% unter Ziel 70%** — prompt-caching-Breakpoints prüfen; häufige Kontext-Umbrüche deuten auf Context-Rotation / Pseudo-Compaction hin.")
    else:
        int_lines.append(f"- **Cache-Hit-Rate {overall_hit:.1f}% kritisch niedrig** — starker Hinweis auf zu frühe Rotation oder Cache-Invalidierung nach jedem tool_use.")
    if med_session_peak > 150000:
        int_lines.append(f"- **Peak-Turns {med_session_peak:,} tokens (median)** überschreiten den 128K-Warning-Threshold und können Warning- oder Rotation-Events triggern.")
    else:
        int_lines.append(f"- **Peak-Turns {med_session_peak:,} tokens (median)** bleiben unter typischen Warning-Thresholds (128K).")
    if top_tools_by_bytes:
        tname = top_tools_by_bytes[0][0]
        int_lines.append(f"- **Top-Tool nach Volumen:** `{tname}` dominiert die Top-10. Fokus für `clear_tool_uses` / Content-Truncation.")
    lines.extend(int_lines)
    lines.append("")
    lines.append("## Reproducibility")
    lines.append("")
    lines.append("Script: `/home/piet/vault/03-Agents/context-baseline-script-2026-04-22.py`")
    lines.append("")
    lines.append("```sh")
    lines.append("ssh homeserver 'python3 /home/piet/vault/03-Agents/context-baseline-script-2026-04-22.py'")
    lines.append("```")
    lines.append("")
    lines.append("The script picks the 5 most recently modified primary session JSONLs (excludes `.checkpoint.`, `.archived.`, `.lock`, and files < 4 KB), parses each with the same logic as the measurement run, and overwrites this report. Numbers are deterministic for a given snapshot of the sessions directory.")
    lines.append("")

    out = "\n".join(lines)

    os.makedirs(os.path.dirname(OUT_PATH), exist_ok=True)
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        fh.write(out)

    print(f"Wrote report to {OUT_PATH}")
    print(f"Total bytes written: {len(out)}")
    # quick stdout summary
    print("-- SUMMARY --")
    print(f"Sessions: {len(per)}")
    print(f"Total JSONL KB: {fmt_kb(total_jsonl_bytes)}")
    print(f"Overall input_tokens: {overall_input_sum:,}")
    print(f"Overall cache_read: {overall_cache_read_sum:,}")
    print(f"Cache-hit rate: {overall_hit:.1f}%")
    print(f"toolResult share: {tr_share:.1f}%")
    print(f"Top tool: {top_tools_by_bytes[0][0] if top_tools_by_bytes else 'n/a'}")


if __name__ == "__main__":
    main()
