#!/usr/bin/env python3
import json
import os
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from queue import Queue
import subprocess
import re
from rapidfuzz import fuzz

# ----------------- Config -----------------
MAX_THREADS = 8
SAVE_JSON = True
OUTPUT_FILE = Path(__file__).parent / "youtube_urls.json"

# Example track list
TRACKS = [
    "Rhythm Is Rhythm – Icon (Transmat)",
    "Esser’ay – Forces ‘Reese Mix’ (KMS)",
    "E-Dancer – Pump The Move (KMS)",
    "Outlander -The Vamp ‘Kevin Saunderson Remix’ (R&S)",
    "E-Dancer – World of Deep (KMS)",
    "Slam – Positive Education (Soma)",
    "Lemon 8 – Model 8 ‘Lemon 8 Remix’ (Basic Energy)",
    "Robert Armani – Circus Bells ‘Remixed By Hardfloor’ (Djax -Up-Beats)",
    "FEOS vs M/S/O – Into The Groove (Ongaku)",
    "Ian Pooley – Chord Memory (Force Inc.)",
    "DJ Gilb-R – Pressure ‘Laurentlaboratoiral'ancienne Mix’ (Versatile)",
    "Dot Allison – We’re Only Science ‘Slam Remix’ (Mantra)",
    "Adam Beyer – Remainings III ‘DK Remix 1’ (Drumcode)",
    "Green Velvet – Land Of The Lost ‘Ian Pooley’s Infected Mix’ (Music Man)",
    "Black Water – Black Water (430 Wes)"
]

# ----------------- Functions -----------------
def search_youtube(track_name):
    try:
        result = subprocess.run(
            ["yt-dlp", f"ytsearch20:{track_name}", "--dump-json", "--skip-download", "--no-playlist"],
            capture_output=True,
            text=True,
            check=True
        )
        best_match = None
        highest_ratio = -1
        for line in result.stdout.splitlines():
            data = json.loads(line)
            title = data.get("title", "")
            url = data.get("webpage_url", "")
            ratio = fuzz.ratio(track_name.lower(), title.lower())
            if ratio > highest_ratio:
                highest_ratio = ratio
                best_match = url
        return best_match
    except Exception as e:
        print(f"❌ Failed to find {track_name}: {e}")
        return None

def worker(queue, output):
    while True:
        try:
            track = queue.get_nowait()
        except:
            break
        url = search_youtube(track)
        output[track] = url
        print(f"✅ {track}: {url}")
        queue.task_done()

# ----------------- Main -----------------
def main():
    q = Queue()
    for track in TRACKS:
        q.put(track)

    results = {}
    threads = []
    for _ in range(min(MAX_THREADS, len(TRACKS))):
        t = ThreadPoolExecutor(max_workers=1).submit(worker, q, results)
        threads.append(t)

    q.join()

    if SAVE_JSON:
        with open(OUTPUT_FILE, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Saved JSON to {OUTPUT_FILE}")

if __name__ == "__main__":
    main()
