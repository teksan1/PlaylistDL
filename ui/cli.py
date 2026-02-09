#!/usr/bin/env python3
import sys
from pathlib import Path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

import os, json, argparse, time, subprocess, re, tempfile
from pathlib import Path
from core import pipeline, scrape_soundcloud
from config import CONFIG, save_config, load_config

load_config()

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
    "enable_js","max_results","download_dir","max_threads"
]

# ------------------ Logging ------------------
def log_verbose(msg):
    if VERBOSE_MODE:
        ts = time.strftime("[%Y-%m-%d %H:%M:%S]")
        line = f"{ts} {msg}"
        print(line)
        with open(LOG_FILE,"a") as f:
            f.write(line+"\n")

# ------------------ Toggles ------------------
def print_toggles():
    print("\n⚙️ TOGGLES")
    for i,k in enumerate(TOGGLE_KEYS,1):
        v = CONFIG.get(k)
        if k=="max_threads":
            v=f"{v}/8"
        print(f"{i}) {k}: {v}")
    print("\nEnter number to modify (ENTER to return)")

def toggle_option(num):
    if not (1<=num<=len(TOGGLE_KEYS)):
        return
    key = TOGGLE_KEYS[num-1]
    val = CONFIG.get(key)
    if isinstance(val,bool):
        CONFIG[key] = not val
    elif key=="max_threads":
        nv=input("Enter threads (1-8): ").strip()
        if nv.isdigit() and 1<=int(nv)<=8:
            CONFIG[key]=int(nv)
    elif isinstance(val,str):
        nv=input(f"Enter new value for {key}: ").strip()
        if nv:
            CONFIG[key]=nv
    save_config()

def options_menu():
    while True:
        print_toggles()
        c=input("> ").strip()
        if not c:
            return
        if c.isdigit():
            toggle_option(int(c))

# ------------------ Queue ------------------
def display_queue():
    if not QUEUE_LIST:
        print("📭 Queue empty")
        return
    print("\n🎵 Queue:")
    for i,t in enumerate(QUEUE_LIST,1):
        print(f"{i}) {t['title']}")

def select_from_queue():
    if not QUEUE_LIST:
        return []
    display_queue()
    sel=input("Select items (ENTER=all): ").strip()
    if not sel:
        return list(range(len(QUEUE_LIST)))
    out=set()
    for part in sel.split(","):
        if "-" in part:
            a,b=part.split("-")
            for i in range(int(a),int(b)+1):
                out.add(i-1)
        elif part.isdigit():
            out.add(int(part)-1)
    return sorted(i for i in out if 0<=i<len(QUEUE_LIST))

def download_selected(indexes):
    global DOWNLOAD_IN_PROGRESS
    if not indexes:
        return
    DOWNLOAD_IN_PROGRESS=True
    items=[QUEUE_LIST[i] for i in indexes]
    pipeline.download_multi(items)
    for i in sorted(indexes,reverse=True):
        del QUEUE_LIST[i]
    DOWNLOAD_IN_PROGRESS=False

# ------------------ SoundCloud ------------------
def handle_soundcloud(url):
    tracks=scrape_soundcloud.scrape_playlist(url)
    QUEUE_LIST.extend(tracks)
    display_queue()

# ------------------ YouTube ------------------
def fetch_youtube(url):
    tracks=[]
    try:
        res=subprocess.run(
            ["yt-dlp","--flat-playlist","-J",url],
            capture_output=True,text=True,check=True
        )
        data=json.loads(res.stdout)
        for e in data.get("entries",[]):
            vid=e.get("id")
            if vid:
                tracks.append({
                    "title":e.get("title",""),
                    "url":f"https://www.youtube.com/watch?v={vid}",
                    "source":"youtube"
                })
    except:
        pass
    return tracks

# ------------------ List → URL → Queue ------------------
def add_list_to_queue():
    print("\nPaste your list (artist - title). Empty line to finish:\n")
    lines=[]
    while True:
        l=input()
        if not l.strip():
            break
        lines.append(l.strip())

    if not lines:
        print("❌ No entries")
        return

    tmp=Path(tempfile.gettempdir())
    txt=tmp/"playlistdl_list.txt"
    txt.write_text("\n".join(lines),encoding="utf-8")

    finder=PROJECT_DIR/"core"/"find_youtube_urls_threaded.py"
    subprocess.run(["python3",str(finder),str(txt)])

    js=txt.with_suffix(".json")
    if not js.exists():
        print("❌ URL resolution failed")
        return

    tracks=json.loads(js.read_text())
    QUEUE_LIST.extend(tracks)
    print(f"✅ Added {len(tracks)} tracks")
    display_queue()

    txt.unlink(missing_ok=True)
    js.unlink(missing_ok=True)


def print_banner():
    print("""
🎧 PlaylistDL – Interactive CLI
────────────────────────────────

This tool helps you find, queue, and download music automatically.

HOW IT WORKS:
• Paste a YouTube or SoundCloud URL → tracks are added to the queue
• Type search text → PlaylistDL finds matching tracks
• Add a written list → PlaylistDL resolves URLs automatically
• Download when ready

COMMANDS:
  -l   Add a written list of tracks
       (format: Artist - Track Title, one per line)

  -d   Download tracks from the queue
       (you can select specific items or press ENTER for all)

  -o   Options & settings
       (sources, threads, download folder, limits)

  -c   Clear the download queue

  -h   Show help

  -e   Exit PlaylistDL

TIP:
• You can paste links or type searches at any time.
• Queue builds first — downloads only start when you run -d.

""")

# ------------------ Help ------------------
def print_help():
    print("""
HELP – PlaylistDL
─────────────────

-l  Add list of tracks
    Paste lines like:
      Artist - Track Name
    Empty line finishes input.
    URLs are resolved automatically and added to the queue.

-d  Download from queue
    You can:
      • Press ENTER to download everything
      • Select items like: 1,3,5 or 2-6

-o  Options / settings
    Toggle sources, threads, limits, and folders.

-c  Clear queue
    Removes all queued tracks (no downloads affected).

-h  Show this help screen

-e  Exit PlaylistDL

You can also:
• Paste YouTube or SoundCloud URLs directly
• Type search text to auto-find tracks
""")

# ------------------ Main ------------------
def main_loop():
    print_banner()

    global VERBOSE_MODE
    p=argparse.ArgumentParser()
    p.add_argument("-v","--verbose",action="store_true")
    a=p.parse_args()
    VERBOSE_MODE=a.verbose

    while True:
        cmd=input("PlaylistDL > ").strip()
        if not cmd:
            continue
        if cmd=="-e":
            break
        if cmd in ("-h","help"):
            print_help(); continue
        if cmd=="-o":
            options_menu(); continue
        if cmd=="-c":
            QUEUE_LIST.clear(); print("🧹 Cleared"); continue
        if cmd=="-l":
            add_list_to_queue(); continue
        if cmd=="-d":
            sel=select_from_queue()
            download_selected(sel); continue
        if "soundcloud.com" in cmd:
            handle_soundcloud(cmd); continue
        if "youtube.com" in cmd:
            QUEUE_LIST.extend(fetch_youtube(cmd))
            display_queue(); continue

        res=pipeline.acquire(cmd)
        if res:
            QUEUE_LIST.extend(res)
            display_queue()

if __name__=="__main__":
    main_loop()
