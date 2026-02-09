#!/usr/bin/env python3
import subprocess
import json
import os
import tempfile

# Path for temporary JSON file
TEMP_JSON = os.path.join(tempfile.gettempdir(), "soundcloud_playlist.json")

def scrape_playlist(url):
    """
    Scrapes a SoundCloud playlist URL using yt-dlp and returns a list of track dicts.
    Each track: {"title": str, "url": str, "source": "soundcloud"}
    """
    print(f"[🎧 Scraping playlist for: {url}]")
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--ignore-errors",
        "--yes-playlist",
        "--no-warnings",
        url
    ]

    tracks = []

    try:
        with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as proc:
            for line in proc.stdout:
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    track = {
                        "title": data.get("title"),
                        "url": data.get("webpage_url"),
                        "source": "soundcloud"
                    }
                    tracks.append(track)
                except json.JSONDecodeError:
                    continue
        # Save temporary JSON for CLI integration
        with open(TEMP_JSON, "w", encoding="utf-8") as f:
            json.dump(tracks, f, ensure_ascii=False, indent=2)

    except subprocess.TimeoutExpired:
        print("⚠️ yt-dlp timed out while fetching playlist.")
    except Exception as e:
        print(f"❌ Error scraping SoundCloud: {e}")

    print(f"[✅ {len(tracks)} tracks found. Saved to {TEMP_JSON}]")
    return tracks


def get_playlist_file_path():
    """Returns the path to the last scraped playlist JSON."""
    return TEMP_JSON
