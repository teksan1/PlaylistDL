#!/usr/bin/env python3
import os, json, argparse, time, subprocess, re
from pathlib import Path
from core import pipeline, scrape_soundcloud
from config import CONFIG, save_config, load_config

load_config()  # load persistent config

QUEUE_LIST, VERBOSE_MODE, LOG_FILE = [], False, "/tmp/musicdowlder_verbose.log"
DOWNLOAD_IN_PROGRESS, STOP_AFTER_CURRENT = False, False
PROJECT_DIR = Path(__file__).resolve().parents[1]

TOGGLE_KEYS = [
    "enable_youtube","enable_soundcloud","enable_duckduckgo",
    "restriction_checks","copyright_checks","analysis_only",
    "allow_downloads","allow_js","js_runtime_ready",
    "enable_js","max_results","download_dir","max_threads"
]

def log_verbose(msg):
    if VERBOSE_MODE:
        timestamp = time.strftime("[%Y-%m-%d %H:%M:%S]")
        line = f"{timestamp} {msg}"
        print(line)
        with open(LOG_FILE, "a") as f:
            f.write(line+"\n")

def print_toggles():
    print("\n⚙️ TOGGLES")
    for i, key in enumerate(TOGGLE_KEYS, 1):
        value = CONFIG.get(key)
        if key=="download_dir": value=CONFIG.get("download_dir","")
        elif key=="max_threads": value=f"{CONFIG.get('max_threads',4)}/8"
        print(f"{i}) {key}: {value}")
    print("\nEnter number to toggle/modify (ENTER to continue)")

def toggle_option(number):
    if 1<=number<=len(TOGGLE_KEYS):
        key = TOGGLE_KEYS[number-1]
        val = CONFIG.get(key)
        if isinstance(val,bool):
            CONFIG[key]=not val
            print(f"{key} set to {CONFIG[key]}")
        elif isinstance(val,int):
            if key=="max_threads":
                print(f"\nCurrent max threads: {CONFIG.get('max_threads',4)}/8")
                try:
                    new_val=input("Enter new max threads (1-8, ENTER keep current): ").strip()
                    if new_val:
                        new_val=int(new_val)
                        if 1<=new_val<=8:
                            CONFIG[key]=new_val
                            print(f"✅ max_threads set to {CONFIG[key]}")
                        else: print("❌ Must be 1-8")
                except: print("❌ Invalid input")
            else:
                try: CONFIG[key]=int(input(f"Enter new value for {key} (current: {CONFIG[key]}): "))
                except: print("❌ Invalid input")
        elif isinstance(val,str):
            if key=="download_dir":
                print(f"\nCurrent download directory:\n{CONFIG.get('download_dir','')}")
                new_path=input("Enter new download directory (ENTER keep current): ").strip()
                if new_path:
                    os.makedirs(new_path,exist_ok=True)
                    CONFIG[key]=new_path
                    print(f"✅ Download directory set to: {new_path}")
            else:
                CONFIG[key]=input(f"Enter new value for {key} (current: {CONFIG[key]}): ")
        save_config()

def display_queue():
    if not QUEUE_LIST:
        print("📭 Queue is empty")
    else:
        print("🎵 Current Queue:")
        for idx, item in enumerate(QUEUE_LIST,1):
            print(f"{idx}) {item['title']} ({item.get('source','unknown')})")

def parse_selection(selection_str,max_len):
    if not selection_str.strip(): return list(range(max_len))
    selected=set()
    for part in selection_str.split(","):
        part=part.strip()
        if '-' in part:
            try:
                start,end=map(int,part.split('-'))
                start=max(1,start)
                end=min(max_len,end)
                for i in range(start,end+1): selected.add(i-1)
            except: continue
        elif part.isdigit():
            i=int(part)
            if 1<=i<=max_len: selected.add(i-1)
    return sorted(selected)

def select_from_queue():
    if not QUEUE_LIST:
        print("Queue is empty! Nothing to select.")
        return []
    display_queue()
    sel=input("\nSelect numbers to download (comma/range, ENTER=all): ").strip()
    selected_indexes=parse_selection(sel,len(QUEUE_LIST))
    if not selected_indexes:
        print("⚠️ No valid selection. Going back.")
        return []
    choice=input(f"Download {len(selected_indexes)} selected items? (y/N): ").strip().lower()
    if choice!='y':
        print("Selection skipped.")
        return []
    return selected_indexes

def download_selected(selected_indexes):
    global DOWNLOAD_IN_PROGRESS, STOP_AFTER_CURRENT
    if not selected_indexes: return
    DOWNLOAD_IN_PROGRESS=True
    items_to_download=[QUEUE_LIST[i] for i in selected_indexes]
    pipeline.download_multi(items_to_download)
    DOWNLOAD_IN_PROGRESS=False
    STOP_AFTER_CURRENT=False
    for i in sorted(selected_indexes,reverse=True):
        if i<len(QUEUE_LIST): del QUEUE_LIST[i]

# ------------------ SoundCloud ------------------
def handle_soundcloud(url):
    log_verbose(f"Detected SoundCloud URL: {url}")
    tracks=scrape_soundcloud.scrape_playlist(url)
    QUEUE_LIST.extend(tracks)
    display_queue()
    sc_json=scrape_soundcloud.get_playlist_file_path()
    if os.path.exists(sc_json): os.remove(sc_json)

# ------------------ YouTube (playlist or single) ------------------
def fetch_youtube(url):
    tracks=[]
    # Playlist
    if "playlist" in url:
        url=re.sub(r"&si=.*$","",url)
        try:
            result=subprocess.run(["yt-dlp","--flat-playlist","-J",url],capture_output=True,text=True,check=True)
            data=json.loads(result.stdout)
            for e in data.get("entries",[]):
                vid_id=e.get("id")
                if not vid_id: continue
                video_url=f"https://www.youtube.com/watch?v={vid_id}"
                title=e.get("title") or video_url
                tracks.append({"title":title,"url":video_url,"source":"youtube"})
        except Exception as e:
            print(f"❌ Failed to fetch playlist: {e}")
    else:
        # Single video
        try:
            result=subprocess.run(["yt-dlp","-J",url],capture_output=True,text=True,check=True)
            data=json.loads(result.stdout)
            title=data.get("title") or url
            tracks.append({"title":title,"url":url,"source":"youtube"})
        except Exception as e:
            print(f"❌ Failed to fetch video: {e}")
    return tracks

# ------------------ Options / Help ------------------
def options_menu():
    while True:
        print_toggles()
        choice=input("\nSelect option (ENTER return): ").strip()
        if choice=="": return
        if choice.isdigit(): toggle_option(int(choice)); continue
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
    parser=argparse.ArgumentParser()
    parser.add_argument("-v","--verbose",action="store_true",help="Verbose logging")
    args=parser.parse_args()
    VERBOSE_MODE=args.verbose
    if VERBOSE_MODE:
        open(LOG_FILE,"w").close()
        log_verbose("🎵 MusicDowlder Started (verbose mode)")
    while True:
        try:
            cmd=input("Enter URL or command:\n-d download\n-c clear\n-e exit\n-o options\n-b backup\n> ").strip()
        except KeyboardInterrupt:
            if input("Exit? (y/N): ").strip().lower()=="y": break
            print(); continue
        if not cmd: continue
        if cmd=="-o": options_menu(); continue
        if cmd=="-c":
            if DOWNLOAD_IN_PROGRESS: STOP_AFTER_CURRENT=True
            QUEUE_LIST.clear()
            print("🧹 Queue cleared."); continue
        if cmd=="-e":
            if input("Exit? (y/N): ").strip().lower()=="y": break
            continue
        if cmd=="-d":
            selected=select_from_queue()
            download_selected(selected)
            continue
        if cmd=="-b":
            download_dir=CONFIG.get("download_dir","")
            exclude_dirs=[download_dir] if download_dir else []
            env=os.environ.copy()
            env["EXCLUDE_DIRS"]=":".join(exclude_dirs)
            subprocess.run(["python3",str(Path(PROJECT_DIR)/"backups"/"backup_manager.py")],env=env)
            continue
        if "soundcloud.com" in cmd:
            handle_soundcloud(cmd); continue
        if "youtube.com" in cmd:
            tracks=fetch_youtube(cmd)
            if tracks:
                QUEUE_LIST.extend(tracks)
                print(f"✅ Added {len(tracks)} tracks from YouTube")
                display_queue()
            else: print("❌ No results found."); continue
        results=pipeline.acquire(cmd)
        if results and results[0].get("url"):
            QUEUE_LIST.extend(results)
            display_queue()
        else: print("❌ No results found.")

if __name__=="__main__":
    main_loop()
