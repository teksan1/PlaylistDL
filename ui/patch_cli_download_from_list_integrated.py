import os
import json
import re
from pathlib import Path
import subprocess

# ------------------ Download from List Integration ------------------
def load_list_and_queue():
    """Prompt user to input a list of tracks in any format, save, find URLs, and queue them."""
    print("\n📄 Paste your track list (one per line, ENTER twice to finish):")
    raw_lines = []
    while True:
        line = input()
        if not line.strip():
            break
        raw_lines.append(line.strip())

    if not raw_lines:
        print("⚠️ No tracks entered.")
        return

    # Clean lines: remove leading numbers, bullets, extra spaces but keep all words
    cleaned_lines = []
    for line in raw_lines:
        # Remove leading numbers, dots, parentheses like "1) " or "12. "
        line = re.sub(r'^\s*\d+[\)\.]?\s*', '', line)
        line = line.strip()
        if line:
            cleaned_lines.append(line)

    # Save cleaned list to track_list.txt
    LIST_FILE = Path(__file__).parent.parent / "core" / "track_list.txt"
    with open(LIST_FILE, "w", encoding="utf-8") as f:
        for line in cleaned_lines:
            f.write(line + "\n")
    print(f"✅ Saved list ({len(cleaned_lines)} tracks) to {LIST_FILE}")

    # Run threaded YouTube URL finder
    FIND_SCRIPT = Path(__file__).parent.parent / "core" / "find_youtube_urls_threaded.py"
    print("🔎 Finding YouTube URLs for the list...")
    subprocess.run(["python3", str(FIND_SCRIPT)])

    # Load generated JSON and add to PlaylistDL queue
    JSON_FILE = Path(__file__).parent.parent / "core" / "youtube_urls.json"
    if not JSON_FILE.exists():
        print("❌ YouTube URLs JSON not found, aborting.")
        return

    with open(JSON_FILE, "r", encoding="utf-8") as f:
        urls_dict = json.load(f)

    # Add to existing queue
    from ui.cli import QUEUE_LIST
    added_count = 0
    for track_name, url in urls_dict.items():
        if url:
            QUEUE_LIST.append({"title": track_name, "url": url, "source": "youtube"})
            added_count += 1
    print(f"🎵 Added {added_count} tracks to queue from list.")

# ------------------ CLI.py Integration ------------------
# 1️⃣ At the top of cli.py add:
# from patch_cli_download_from_list_integrated import load_list_and_queue

# 2️⃣ Inside main_loop() add a new command:
# if cmd == "-l":
#     load_list_and_queue()
#     continue
