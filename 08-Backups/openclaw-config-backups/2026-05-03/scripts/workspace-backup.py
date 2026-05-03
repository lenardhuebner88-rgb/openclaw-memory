#!/usr/bin/env python3
"""
Workspace Backup für OpenClaw/Mission Control
Sichert alle kritischen Daten automatisch.
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

BACKUP_ROOT = Path(os.path.expanduser("~/.openclaw/backups"))
RETENTION_DAYS = 14

CRITICAL_PATHS = [
    ("mission-control-data", "~/.openclaw/state/mission-control/data/"),
    ("learnings.md", "~/.openclaw/workspace/memory/learnings.md"),
    ("kb.md", "~/.openclaw/workspace/agents/kb.md"),
    ("openclaw.json", "~/.openclaw/openclaw.json"),
    ("cron-jobs.json", "~/.openclaw/cron/jobs.json"),
    ("env.local", "~/.openclaw/workspace/mission-control/.env.local"),
    ("agents-config", "~/.openclaw/agents/"),
    ("skills-custom", "~/.openclaw/skills/"),
]

def expand_path(path_str):
    return Path(os.path.expanduser(path_str))

def create_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = BACKUP_ROOT / f"backup_{timestamp}"
    backup_dir.mkdir(parents=True, exist_ok=True)
    
    backed_up = []
    failed = []
    
    for name, path_str in CRITICAL_PATHS:
        path = expand_path(path_str)
        dest = backup_dir / name
        
        if not path.exists():
            failed.append(f"{name} (not found: {path})")
            continue
        
        try:
            if path.is_file():
                shutil.copy2(path, dest)
            elif path.is_dir():
                shutil.copytree(path, dest, dirs_exist_ok=True)
            
            size = sum(f.stat().st_size for f in dest.rglob("*") if f.is_file()) if dest.exists() else 0
            backed_up.append(f"{name} ({size // 1024} KB)")
        except Exception as e:
            failed.append(f"{name} (error: {e})")
    
    # Write manifest
    manifest = {
        "timestamp": timestamp,
        "backup_dir": str(backup_dir),
        "backed_up": backed_up,
        "failed": failed,
        "total_files": len(backed_up),
    }
    
    manifest_file = backup_dir / "manifest.json"
    with open(manifest_file, "w") as f:
        json.dump(manifest, f, indent=2)
    
    # Cleanup old backups
    cleanup_old_backups()
    
    return manifest

def cleanup_old_backups():
    """Delete backups older than RETENTION_DAYS."""
    if not BACKUP_ROOT.exists():
        return
    
    cutoff = datetime.now().timestamp() - (RETENTION_DAYS * 86400)
    removed = 0
    
    for backup_dir in BACKUP_ROOT.iterdir():
        if backup_dir.is_dir() and backup_dir.name.startswith("backup_"):
            if backup_dir.stat().st_mtime < cutoff:
                shutil.rmtree(backup_dir)
                removed += 1
    
    if removed:
        print(f"  🗑 Removed {removed} old backup(s)")

def list_backups():
    """List all available backups."""
    if not BACKUP_ROOT.exists():
        print("Keine Backups vorhanden.")
        return
    
    backups = sorted(BACKUP_ROOT.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
    
    print(f"\n📦 Verfügbare Backups (/{RETENTION_DAYS} Tage):")
    print(f"{'─' * 50}")
    
    for backup_dir in backups[:10]:
        manifest_file = backup_dir / "manifest.json"
        if manifest_file.exists():
            with open(manifest_file) as f:
                manifest = json.load(f)
            print(f"  {manifest['timestamp']} — {manifest['total_files']} Dateien")
        else:
            print(f"  {backup_dir.name} — (kein Manifest)")
    
    if len(backups) > 10:
        print(f"\n  ... und {len(backups) - 10} weitere")

def restore_latest():
    """Restore the latest backup."""
    if not BACKUP_ROOT.exists():
        print("Keine Backups vorhanden.")
        return
    
    backups = sorted(BACKUP_ROOT.iterdir(), key=lambda x: x.stat().st_mtime, reverse=True)
    if not backups:
        print("Keine Backups vorhanden.")
        return
    
    latest = backups[0]
    print(f"⚠️  Restore von: {latest.name}")
    print("  Das überschreibt aktuelle Dateien!")
    print("  Mit --force bestätigen:")
    print(f"  python3 /home/piet/.openclaw/scripts/workspace-backup.py restore --force")

def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "backup"
    
    if cmd == "backup":
        print("📦 Workspace Backup startet...")
        manifest = create_backup()
        print(f"\n✅ Backup erstellt: {manifest['backup_dir'].split('/')[-1]}")
        if manifest['backed_up']:
            print(f"   Gesichert: {', '.join(manifest['backed_up'][:5])}")
            if len(manifest['backed_up']) > 5:
                print(f"   ... und {len(manifest['backed_up']) - 5} weitere")
        if manifest['failed']:
            print(f"   ⚠️ Fehlgeschlagen: {', '.join(manifest['failed'])}")
    
    elif cmd == "list":
        list_backups()
    
    elif cmd == "restore":
        if "--force" in sys.argv:
            restore_latest()
        else:
            restore_latest()
            print("\nAbbruch — keine Änderungen vorgenommen.")
    
    else:
        print(f"Unknown command: {cmd}")
        print("Usage: workspace-backup.py [backup|list|restore]")

if __name__ == "__main__":
    main()
