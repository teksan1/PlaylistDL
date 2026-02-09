#!/usr/bin/env python3
import os
import shutil
import tarfile
import time
from pathlib import Path
import sys

BASE_DIR = Path.home() / "musicdowlder"
BACKUP_DIR = BASE_DIR / "backups"
BASELINE_DIR = BACKUP_DIR / "baseline"
RUNNING_BACKUP_SUFFIX = ".running.bak"
LITE_BASELINE_SUFFIX = ".tar.gz"

ESSENTIAL_FOLDERS = ["ui", "core", "server", "config", "setup"]
ESSENTIAL_FILES = ["requirements.txt", "package.json", "pnpm-lock.yaml", "Makefile"]

BACKUP_DIR.mkdir(exist_ok=True)
BASELINE_DIR.mkdir(exist_ok=True)

def get_timestamp():
    return time.strftime("%Y%m%d_%H%M%S")

def is_excluded(path):
    # Exclude downloads folder content
    return path.is_file() and "downloads" in str(path)

def collect_paths(selected_paths=None, full=False):
    paths = []
    if full:
        for item in BASE_DIR.iterdir():
            if item.exists():
                paths.append(item)
    elif selected_paths:
        for p in selected_paths:
            full_path = BASE_DIR / p
            if full_path.exists():
                paths.append(full_path)
    else:
        for folder in ESSENTIAL_FOLDERS:
            full = BASE_DIR / folder
            if full.exists():
                paths.append(full)
        for f in ESSENTIAL_FILES:
            full = BASE_DIR / f
            if full.exists():
                paths.append(full)
    return paths

def print_progress_bar(iteration, total, prefix='', suffix='', length=40):
    percent = f"{100 * (iteration / float(total)):.1f}"
    filled_length = int(length * iteration // total)
    bar = '█' * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end='\r')
    if iteration == total:
        print()

def create_running_backup(paths):
    print("🔹 Creating running backup...")
    total_items = len(paths)
    for i, path in enumerate(paths, 1):
        dst = BASE_DIR / (path.name + RUNNING_BACKUP_SUFFIX)
        if dst.exists():
            if dst.is_file():
                dst.unlink()
            else:
                shutil.rmtree(dst)
        if path.exists():
            if path.is_file():
                shutil.copy2(path, dst)
            else:
                shutil.copytree(path, dst, ignore=shutil.ignore_patterns("*"))
        print_progress_bar(i, total_items, prefix='Running Backup', suffix='Complete')
    print("✅ Running backup complete.\n")

def create_lite_baseline(paths):
    timestamp = get_timestamp()
    filename = f"baseline_{timestamp}{LITE_BASELINE_SUFFIX}"
    fullpath = BASELINE_DIR / filename
    print(f"🔹 Creating lite baseline backup: {filename}")
    total_items = len(paths)
    start_time = time.time()
    with tarfile.open(fullpath, "w:gz") as tar:
        for i, path in enumerate(paths, 1):
            if path.exists() and not is_excluded(path):
                arcname = path.relative_to(BASE_DIR)
                tar.add(path, arcname=arcname)
            elapsed = time.time() - start_time
            rate = i / elapsed if elapsed > 0 else 1
            remaining = total_items - i
            eta = remaining / rate if rate > 0 else 0
            mins, secs = divmod(int(eta), 60)
            print_progress_bar(i, total_items, prefix='Baseline Backup', suffix=f'ETA {mins}m {secs}s')
    print(f"✅ Lite baseline backup complete: {fullpath}\n")

def rollback_backup():
    print("⚠️ Rollback selected. Available backups:")
    backups = [f for f in BASELINE_DIR.iterdir() if f.suffix == ".gz"]
    if not backups:
        print("❌ No backups available to rollback.")
        return
    for i, b in enumerate(backups, 1):
        print(f"{i}) {b.name}")
    choice = input("Select backup to restore (number): ").strip()
    if not choice.isdigit() or int(choice) < 1 or int(choice) > len(backups):
        print("❌ Invalid selection.")
        return
    backup_file = backups[int(choice)-1]
    print(f"🔹 Restoring from {backup_file}")
    with tarfile.open(backup_file, "r:gz") as tar:
        tar.extractall(BASE_DIR)
    print("✅ Rollback complete.\n")

def main():
    print("=== MusicDowlder Backup Utility ===")
    print("Options:\n1) Backup\n2) Full Backup\n3) Rollback\n4) Exit")
    action = input("Select action: ").strip()
    if action == "1":
        paths = input("Enter comma-separated folders/files to backup or ENTER for default essential: ").strip()
        paths = [p.strip() for p in paths.split(",")] if paths else None
        selected_paths = collect_paths(paths)
        baseline = input("Is this a baseline backup? (y/N): ").strip().lower()
        create_running_backup(selected_paths)
        if baseline == "y":
            create_lite_baseline(selected_paths)
    elif action == "2":
        print("🔹 Creating full backup of MusicDowlder directory...")
        selected_paths = collect_paths(full=True)
        create_running_backup(selected_paths)
        baseline = input("Is this a baseline full backup? (y/N): ").strip().lower()
        if baseline == "y":
            create_lite_baseline(selected_paths)
        print("✅ Full backup complete.\n")
    elif action == "3":
        rollback_backup()
    elif action == "4":
        print("👋 Exiting backup utility.")
    else:
        print("❌ Invalid selection.")

if __name__ == "__main__":
    main()
