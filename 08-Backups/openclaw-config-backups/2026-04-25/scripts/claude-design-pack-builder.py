#!/usr/bin/env python3
"""
claude-design-pack-builder.py

Builds a curated zip of Mission Control's design-critical files + screenshots +
a README brief, ready for upload to Claude Design.

Output: /home/piet/vault/02-Docs/Design-Packs/claude-design-packs/mc-design-pack-<focus>-<timestamp>.zip

Usage:
  python3 claude-design-pack-builder.py <focus> [--screenshots-dir PATH]

focus: taskboard | analytics | monitoring | team | overview | dashboard | all

The pack is built as follows (~2-5 MB total):
  mc-design-pack/
    README.md                 — brief + goals + constraints (generated)
    tailwind.config.ts        — full design tokens
    package.json              — dependency context
    src/app/globals.css       — CSS variables, fluid typo, safe-area
    src/app/layout.tsx        — root layout + theme
    src/components/ui/        — ALL shadcn-style primitives
    src/components/<focus>/   — feature-specific components
    src/app/<focus>/          — the focus page
    src/components/mission-shell.tsx     — global shell
    src/components/bottom-tab-bar.tsx    — mobile nav
    src/components/command-palette.tsx   — FAB
    screenshots/              — up to 10 relevant screenshots

Files explicitly EXCLUDED: node_modules, .next*, data/, e2e/, tests/,
vitest.config, playwright.*, *.bak*, *.log
"""
import argparse
import json
import shutil
import sys
import zipfile
from datetime import datetime, timezone
from pathlib import Path

MC = Path("/home/piet/.openclaw/workspace/mission-control")
VAULT_PACKS = Path("/home/piet/vault/02-Docs/Design-Packs/claude-design-packs")
VAULT_PACKS.mkdir(parents=True, exist_ok=True)

FOCUS_PAGE_MAP = {
    "taskboard":  ["src/app/taskboard", "src/components/taskboard"],
    "analytics":  ["src/app/analytics", "src/components/analytics"],
    "monitoring": ["src/app/monitoring", "src/components/monitoring"],
    "team":       ["src/app/team", "src/components/team"],
    "overview":   ["src/app/overview", "src/components/overview-dashboard.tsx"],
    "dashboard":  ["src/app/dashboard"],
    "ops":        ["src/app/ops", "src/components/ops"],
    "all":        ["src/app", "src/components"],
}

# Always-include design foundation
ALWAYS_FILES = [
    "tailwind.config.ts",
    "package.json",
    "postcss.config.mjs",
    "next.config.ts",
    "src/app/globals.css",
    "src/app/layout.tsx",
    "src/components/ui",  # all shadcn primitives
    "src/components/mission-shell.tsx",
    "src/components/bottom-tab-bar.tsx",
    "src/components/command-palette.tsx",
    "src/components/bulk-action-bar.tsx",
    "src/lib/utils.ts",
]

# Exclude patterns (applied when walking directories)
EXCLUDE_NAMES = {"node_modules", ".next", "data", "e2e", ".git", "coverage", "__pycache__"}
EXCLUDE_SUFFIXES = {".log", ".bak", ".tsbuildinfo", ".map"}
EXCLUDE_GLOBS = ["*.bak-*", "*.bak.*", "tmp_*", "tmp-*"]


def should_exclude(p: Path) -> bool:
    """Return True if path should be excluded from the pack."""
    if p.name in EXCLUDE_NAMES:
        return True
    for part in p.parts:
        if part in EXCLUDE_NAMES:
            return True
    if p.suffix in EXCLUDE_SUFFIXES:
        return True
    for glob in EXCLUDE_GLOBS:
        if p.match(glob):
            return True
    return False


def collect_files(source_rel: str) -> list[tuple[Path, str]]:
    """Return list of (absolute-path, archive-relative-path) tuples."""
    src = MC / source_rel
    if not src.exists():
        print(f"  [skip] {source_rel} (not found)")
        return []
    out = []
    if src.is_file():
        if not should_exclude(src):
            out.append((src, source_rel))
    else:
        for f in src.rglob("*"):
            if f.is_file() and not should_exclude(f):
                rel = f.relative_to(MC)
                out.append((f, str(rel)))
    return out


def build_readme(focus: str, file_count: int, screenshot_count: int) -> str:
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    focus_title = focus.title()
    return f"""# Mission Control — Claude Design Pack (Focus: {focus_title})

Generated: {now}
Files: {file_count} | Screenshots: {screenshot_count}

---

## About Mission Control

**Product:** Internal orchestration dashboard for a multi-agent AI system (OpenClaw).
6 agents (Atlas/Forge/Pixel/Lens/Spark/James) execute coordinated software-engineering
tasks; Mission Control gives the human operator (pieter_pan) realtime visibility,
dispatch control, and incident response.

**Users:** 1 operator (solo). Power-user. Uses on both desktop (27-inch) and mobile (daily commutes).

**Tech stack:** Next.js 15.5 + React + Tailwind + shadcn/ui (Radix primitives) + TypeScript.

---

## Design System (what's in this pack)

### Brand Palette
- **Theme:** Dark-first (html.dark default, no light-theme planned currently)
- **Base:** Zinc gradient backgrounds (zinc-900 → zinc-950)
- **Accent:** Amber-400 for interactive/important elements
- **Status:** Green (ok/active), Amber (warning/stalled), Red (incident/failed), Gray (idle)

### Typography
- **Fluid scale:** `clamp()` based, body 16px minimum (accessibility)
- **Line-height matrix:** tight for headlines, relaxed for body
- **Tabular-nums:** enabled for all numeric data (budgets, latencies, counts)

### Spacing / Layout
- **Safe-area tokens:** iOS/Android safe-area-inset support built in
- **Bottom-Tab-Bar:** 60px+ tap-targets on mobile (WCAG AA)
- **FAB:** bottom-right, offset-aware when bulk-mode is active

### Component Library (ALL in this pack under `src/components/ui/`)
- Radix-based primitives: Button, Card, Tabs, Skeleton, Popover, Command, Dialog, etc.
- Custom composites: TaskCard, TaskDetailModal, PipelineClient, AnalyticsClient
- Nav: MissionShell (root layout), BottomTabBar (mobile), CommandPalette (FAB), BulkActionBar

---

## Focus Area: {focus_title}

This pack is scoped to let you redesign/improve **{focus_title}** specifically while staying
consistent with the rest of MC.

**Key existing files for this focus (in `src/components/{focus}` and `src/app/{focus}`):**
Look at the source files — they represent the current implementation to improve upon.

**Screenshots show current state.** Check `screenshots/` folder.

---

## Redesign Goals (what to achieve)

### Primary
1. **Information hierarchy:** {focus_title} currently shows many states equally — emphasize what operator should ACT on.
2. **Mobile density:** 60%+ of operator use is mobile during commutes. Current desktop layouts cram into mobile.
3. **Dark-first elegance:** visual refinement within existing zinc+amber language. Not neon, not generic-dashboard — "quiet confident ops console".

### Secondary
4. Animation: state-transitions (task done, new alert) — subtle, not distracting
5. Status-storytelling: an idle operator glancing at Mission Control should understand system health in <3 seconds
6. Accessibility: maintain WCAG AA contrast, keyboard-nav on desktop, voice-command hooks on mobile (already scaffolded)

### Explicitly NOT goals
- Don't change color palette (amber+zinc is brand)
- Don't introduce new component library (stay shadcn/ui compatible)
- Don't add light theme (dark-only)
- Don't add new top-level routes (add within existing tabs)

---

## Constraints (technical)

- React 19 / Next.js 15.5 App Router — server+client component split matters
- Tailwind 4.x — CSS-variable-based theming
- shadcn/ui components can be customized via `components.json` config
- Existing routes & API: don't break URL structure (e.g. `/taskboard`, `/analytics`, `/ops`)
- Build must remain < 400 KB first-load JS per route (hard cap)

---

## Deliverable Format

When you're done, please output:
1. **Design rationale** — 1-2 paragraphs explaining the key decisions
2. **Visual prototype** — HTML/CSS or image mockup
3. **Component inventory** — which shadcn primitives did you use, did you introduce new composites?
4. **Handoff bundle** — ideally Claude-Code-compatible so Pixel (frontend-guru agent) can implement
5. **Mobile + Desktop variants** if layout differs

---

## Related Context (for background)

- Sprint-I (done 2026-04-19) implemented mobile-polish v2: fluid typography, tap-targets, loading states, gestures, command-palette.
- Sprint-H (done 2026-04-19) added Analytics dashboard + Alerts engine.
- Sprint-G (done 2026-04-19) added Ops-dashboard route.
- Current Mission-Control version: Next.js 15.5.15, shadcn/ui configured, live at `localhost:3000`.

Happy designing! 🦞
"""


def copy_screenshots(pack_root: Path, focus: str) -> int:
    """Copy matching screenshots from mc/screenshots/ to pack_root/screenshots/."""
    src_dirs = [
        MC / "screenshots",
        Path("/home/piet/vault/_agents/Atlas Main"),  # placeholder
    ]
    dst = pack_root / "screenshots"
    dst.mkdir(exist_ok=True)
    count = 0
    for src_dir in src_dirs:
        if not src_dir.exists():
            continue
        for png in src_dir.glob("*.png"):
            # Match by focus keyword OR include generic overview/audit shots always
            name = png.name.lower()
            if focus in name or "overview" in name or "audit" in name or focus == "all":
                shutil.copy2(png, dst / png.name)
                count += 1
                if count >= 10:
                    return count
    return count


def main():
    ap = argparse.ArgumentParser(description="Build Claude Design pack for Mission Control")
    ap.add_argument("focus", choices=list(FOCUS_PAGE_MAP.keys()))
    ap.add_argument("--out-dir", default=str(VAULT_PACKS))
    args = ap.parse_args()

    focus = args.focus
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d-%H%M")
    pack_name = f"mc-design-pack-{focus}-{ts}"
    staging = Path(f"/tmp/{pack_name}")

    if staging.exists():
        shutil.rmtree(staging)
    staging.mkdir(parents=True)

    # Collect all files
    targets = []
    targets.extend(ALWAYS_FILES)
    targets.extend(FOCUS_PAGE_MAP[focus])

    # Deduplicate preserving order
    seen = set()
    targets_unique = []
    for t in targets:
        if t not in seen:
            seen.add(t)
            targets_unique.append(t)

    print(f"Building pack: {pack_name}")
    print(f"  Focus: {focus}")
    print(f"  Sources: {len(targets_unique)}")

    file_count = 0
    for t in targets_unique:
        files = collect_files(t)
        for src, rel in files:
            dst = staging / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            file_count += 1
        print(f"  [+] {t}: {len(files)} files")

    # Copy screenshots
    screenshot_count = copy_screenshots(staging, focus)
    print(f"  [+] screenshots: {screenshot_count}")

    # README
    readme = staging / "README.md"
    readme.write_text(build_readme(focus, file_count, screenshot_count))

    # Zip
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = out_dir / f"{pack_name}.zip"

    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        for f in staging.rglob("*"):
            if f.is_file():
                arcname = f"{pack_name}/{f.relative_to(staging)}"
                zf.write(f, arcname)

    size_mb = zip_path.stat().st_size / (1024 * 1024)
    print(f"")
    print(f"✓ Pack built: {zip_path}")
    print(f"  Total files: {file_count + screenshot_count + 1}")
    print(f"  Size: {size_mb:.2f} MB")
    print(f"")
    print(f"Download to laptop via:")
    print(f"  scp homeserver:{zip_path} \\")
    print(f"    C:\\Users\\Lenar\\Downloads\\")
    print(f"")
    print(f"Then upload the zip to Claude Design.")

    # Cleanup staging
    shutil.rmtree(staging)


if __name__ == "__main__":
    main()
