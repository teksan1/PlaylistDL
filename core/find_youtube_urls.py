#!/usr/bin/env python3
import subprocess
import json
from rapidfuzz import fuzz

def youtube_search_deep(track_name, top_n=20):
    """
    Search YouTube for track_name, fetch top_n results, pick the closest match
    based on fuzzy matching of title and track_name.
    """
    try:
        cmd = ["yt-dlp", f"ytsearch{top_n}:{track_name}", "--dump-json"]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        best_score = 0
        best_url = None

        for line in result.stdout.splitlines():
            try:
                data = json.loads(line)
            except json.JSONDecodeError:
                continue

            title = data.get("title", "")
            url = data.get("webpage_url")
            if not url:
                continue

            # Fuzzy match track name vs video title
            score = fuzz.token_sort_ratio(track_name.lower(), title.lower())
            if score > best_score:
                best_score = score
                best_url = url

        return best_url
    except Exception as e:
        print(f"❌ Error searching for '{track_name}': {e}")
        return None

def process_track_list(file_path):
    """
    Read a text file with one track per line, return a list of track -> URL
    """
    results = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            track_name = line.strip()
            if not track_name:
                continue
            url = youtube_search_deep(track_name, top_n=20)
            results.append((track_name, url))
            print(f"{track_name} -> {url}")
    return results

if __name__ == "__main__":
    input_file = "tracks.txt"  # Replace with your file path
    process_track_list(input_file)

