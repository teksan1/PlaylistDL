#!/usr/bin/env python3
import json
from pathlib import Path
from core import pipeline

# Path to the JSON file from threaded YouTube search
JSON_FILE = Path(__file__).parent / "youtube_urls.json"

def load_and_download(json_file=JSON_FILE):
    if not json_file.exists():
        print(f"❌ JSON file not found: {json_file}")
        return

    with open(json_file, "r") as f:
        urls_dict = json.load(f)

    # Convert to PlaylistDL queue format
    queue_list = []
    for track_name, url in urls_dict.items():
        if url:
            queue_list.append({"title": track_name, "url": url, "source": "youtube"})
        else:
            print(f"⚠️ No URL found for {track_name}, skipping.")

    if not queue_list:
        print("⚠️ No valid tracks to download.")
        return

    print(f"🎵 Adding {len(queue_list)} tracks to download queue...")
    stats = pipeline.download_multi(queue_list, max_threads=8)

    print(f"\n✅ Download Summary: {stats['success']}/{len(queue_list)} succeeded, "
          f"{stats['failed']} failed, {stats['skipped']} skipped.")

    if stats['success'] == len(queue_list):
        print("🎯 All tracks downloaded successfully. Cleaning lists for next use...")
        # Clear JSON file
        json_file.unlink()
        print(f"🧹 Cleared {json_file}")
    else:
        print("⚠️ Some tracks failed. JSON file remains for retry.")

if __name__ == "__main__":
    load_and_download()
