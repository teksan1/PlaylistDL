#!/usr/bin/env python3
import os
import json
import argparse
import time
from pathlib import Path
from core import pipeline
from core import scrape_soundcloud
from config import CONFIG
import subprocess
import re

# Global state
QUEUE_LIST = []
VERBOSE_MODE = False
LOG_FILE = "/tmp/musicdowlder_verbose.log"
DOWNLOAD_IN_PROGRESS = False
STOP_AFTER_CURRENT = False

PROJECT_DIR = Path(__file__).resolve().parents[1]

TOGGLE_KEYS = [
    "enable_youtube","enable_soundcloud","enable_duckduckgo",
    "restriction_checks","copyright_checks","analysis_only",
    "allow_downloads","allow_js","js_runtime_ready",
    "enable_js","max_results","download_dir"
]

# ------------------ Utilities ------------------
def log_verbose(msg):
    if VERBOSE_MODE:
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
        line = f"{timestamp} {msg}"
        print(line)
        with open(LOG_FILE, "a") as f:
            f.write(line + "\n")

def print_toggles():
    print("\n⚙️ TOGGLES")
    for i, key in enumerate(TOGGLE_KEYS, 1):
        print(f"{i}) {key}: {CONFIG.get(key)}")
    print("\n(ENTER to return)")

def toggle_option(number):
    if 1 <= number <= len(TOGGLE_KEYS):
        key = TOGGLE_KEYS[number-1]
        val = CONFIG.get(key)
        if isinstance(val, bool):
            CONFIG[key] = not val
            print(f"{key} set to {CONFIG[key]}")
        elif isinstance(val, int):
            try:
                CONFIG[key] = int(input(f"Enter new value for {key} (current: {CONFIG[key]}): "))
            except ValueError:
                print("❌ Invalid integer")
        elif isinstance(val, str):
            CONFIG[key] = input(f"Enter new value for {key} (current: {CONFIG[key]}): ")

def display_queue():
    if not QUEUE_LIST:
        print("📭 Queue is empty")
    else:
        print("\n🎵 Current Queue:")
        for idx, item in enumerate(QUEUE_LIST, 1):
            print(f"{idx}) {item['title']} ({item.get('source','unknown')})")

def parse_selection(selection_str, max_len):
    if not selection_str.strip():
        return list(range(max_len))
    selected = set()
    for part in selection_str.split(","):
        part = part.strip()
        if '-' in part:
            try:
                start, end = map(int, part.split('-'))
                start = max(1, start)
                end = min(max_len, end)
                for i in range(start, end+1):
                    selected.add(i-1)
            except ValueError:
                continue
        elif part.isdigit():
            i = int(part)
            if 1 <= i <= max_len:
                selected.add(i-1)
    return sorted(selected)

# ------------------ Core Handlers ------------------
def handle_soundcloud(url):
    log_verbose(f"Detected SoundCloud URL: {url}")
    tracks = scrape_soundcloud.scrape_playlist(url)
    QUEUE_LIST.extend(tracks)
    log_verbose(f"Added {len(tracks)} tracks from SoundCloud to the queue")
    display_queue()
    sc_json = scrape_soundcloud.get_playlist_file_path()
    if os.path.exists(sc_json):
        os.remove(sc_json)
        log_verbose(f"Removed temporary file {sc_json}")

def select_from_queue():
    if not QUEUE_LIST:
        print("Queue is empty! Nothing to select.")
        return []
    display_queue()
    sel = input("\nSelect numbers to download (comma/range, ENTER=all): ").strip()
    selected_indexes = parse_selection(sel, len(QUEUE_LIST))
    if not selected_indexes:
        print("⚠️ No valid selection. Going back.")
        return []
    choice = input(f"Download {len(selected_indexes)} selected items? (y/N): ").strip().lower()
    if choice != 'y':
        print("Selection skipped.")
        return []
    return selected_indexes

def download_selected(selected_indexes):
    global DOWNLOAD_IN_PROGRESS, STOP_AFTER_CURRENT
    if not selected_indexes:
        return
    DOWNLOAD_IN_PROGRESS = True
    items_to_download = [QUEUE_LIST[i] for i in selected_indexes]
    for item in items_to_download:
        if STOP_AFTER_CURRENT:
            break
        pipeline.download_multi([item])
    DOWNLOAD_IN_PROGRESS = False
    STOP_AFTER_CURRENT = False
    for i in sorted(selected_indexes, reverse=True):
        if i < len(QUEUE_LIST):
            del QUEUE_LIST[i]

# ------------------ YouTube Playlist Fetch ------------------
def fetch_youtube_playlist(playlist_url):
    playlist_url = re.sub(r"&si=.*$", "", playlist_url)
    tracks = []
    try:
        result = subprocess.run(
            ["yt-dlp", "--flat-playlist", "-J", "--js-runtimes", "node", "--remote-components", "ejs:github", playlist_url],
            capture_output=True, text=True, check=True
        )
        data = json.loads(result.stdout)
        for e in data.get("entries", []):
            vid_id = e.get("id")
            if not vid_id:
                continue
            url = f"https://www.youtube.com/watch?v={vid_id}"
            title = e.get("title") or url
            tracks.append({"title": title, "url": url, "source": "youtube"})
    except subprocess.CalledProcessError as e:
        out = e.stdout + e.stderr
        for line in out.splitlines():
            if "Private video" in line or "Video unavailable" in line:
                continue
        if not tracks:
            print(f"❌ Failed to fetch playlist (some videos skipped)")
    except Exception as e:
        print(f"❌ Failed to fetch playlist: {e}")
    return tracks

# ------------------ Options Menu ------------------
def options_menu():
    while True:
        print_toggles()
        print("\nd) Change download directory")
        choice = input("\nSelect option (ENTER to return): ").strip().lower()
        if choice == "":
            return
        if choice == "d":
            new_path = input("Enter new download directory: ").strip()
            if new_path:
                os.makedirs(new_path, exist_ok=True)
                CONFIG["download_dir"] = new_path
                print(f"✅ Download directory set to: {new_path}")
            continue
        if choice.isdigit():
            toggle_option(int(choice))
            continue
        print("❌ Invalid option")

def print_help():
    print("""
📖 MusicDowlder Help
Commands:
  -o   Open options / toggles menu
  -d   Download from current queue
  -c   Clear queue
  -e   Exit application
  -h   Show this help screen
""")

# ------------------ Main Loop ------------------
def main_loop():
    global VERBOSE_MODE, STOP_AFTER_CURRENT
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    args = parser.parse_args()
    VERBOSE_MODE = args.verbose
    if VERBOSE_MODE:
        open(LOG_FILE,"w").close()
        log_verbose("🎵 MusicDowlder App Started (verbose mode)")

    while True:
        try:
            cmd = input(
                "Enter URL or command:\n"
                "-d download\n"
                "-c clear\n"
                "-e exit\n"
                "-o options\n"
                "-b backup\n> "
            ).strip()
        except KeyboardInterrupt:
            if input("Exit? (y/N): ").strip().lower() == "y":
                print("👋 Exiting...")
                break
            print()
            continue

        if not cmd:
            continue
        if cmd == "-o":
            options_menu()
            continue
        if cmd == "-c":
            if DOWNLOAD_IN_PROGRESS:
                STOP_AFTER_CURRENT = True
            QUEUE_LIST.clear()
            print("🧹 Queue cleared.")
            continue
        if cmd == "-e":
            if input("Exit? (y/N): ").strip().lower() == "y":
                print("👋 Exiting...")
                break
            continue
        if cmd == "-d":
            selected = select_from_queue()
            download_selected(selected)
            continue
        if cmd == "-b":
            # Call backup script
            download_dir = CONFIG.get("download_dir","")
            exclude_dirs = [download_dir] if download_dir else []
            env = os.environ.copy()
            env["EXCLUDE_DIRS"] = ":".join(exclude_dirs)
            subprocess.run(["python3", str(Path(PROJECT_DIR)/"backups"/"backup_manager.py")], env=env)
            continue
        if "soundcloud.com" in cmd:
            handle_soundcloud(cmd)
            continue
        if "youtube.com/playlist" in cmd:
            tracks = fetch_youtube_playlist(cmd)
            if tracks:
                QUEUE_LIST.extend(tracks)
                print(f"✅ Added {len(tracks)} tracks from YouTube playlist")
                display_queue()
            else:
                print("❌ No results found.")
            continue
        results = pipeline.acquire(cmd)
        if results and results[0].get("url"):
            QUEUE_LIST.extend(results)
            display_queue()
        else:
            print("❌ No results found.")

if __name__ == "__main__":
    main_loop()
