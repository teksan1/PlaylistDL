import sys

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(0, str(PROJECT_ROOT))
def print_startup_banner():

    print("""

🎧 PlaylistDL – Interactive CLI



Commands:

  -l   Add list of tracks (artist - title) and search automatically

  -d   Download tracks from the queue

  -o   Options / settings toggles

  -c   Clear the queue

  -h   Show this help

  -e   Exit the app



Usage examples:

  pldl            # Start the app

  pldl -l         # Paste a list of tracks to add to the queue

  pldl -d         # Download queued tracks



You can also paste URLs from YouTube, SoundCloud, or other sites,

or search text. The app will detect the platform and find tracks.

""")

import sys

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

if str(PROJECT_ROOT) not in sys.path:

    sys.path.insert(0, str(PROJECT_ROOT))
#!/usr/bin/env python3
from core import queue, downloader, fetchers, list_handler

def print_help():
    print("""
Commands:
  -l   Add list of tracks
  -d   Download from queue
  -o   Options / settings
  -c   Clear queue
  -h   Help
  -e   Exit
Paste URL, search text, or enter command.
""")

def main_loop():
    print_startup_banner()
    while True:
        cmd = input("PlaylistDL > ").strip()
        if not cmd:
            continue
        if cmd in ("-e", "exit"):
            break
        if cmd in ("-h", "help"):
            print_help(); continue
        if cmd == "-c":
            queue.clear_queue(); continue
        if cmd == "-l":
            list_handler.handle_list_file(); queue.display_queue(); continue
        if cmd == "-d":
            sel = queue.select_from_queue()
            downloader.download_multi([queue.QUEUE_LIST[i] for i in sel])
            continue
        tracks = fetchers.handle_input(cmd)
        if tracks:
            queue.add_to_queue(tracks)
            queue.display_queue()
            continue
        print("❌ Could not process input")

if __name__ == "__main__":
    print("🎧 PlaylistDL – Interactive CLI")
    print_help()
    main_loop()
