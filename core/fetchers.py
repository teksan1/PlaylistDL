import subprocess, json
from core.config import MAX_RESULTS, ENABLE_YOUTUBE, ENABLE_SOUNDCLOUD
from core import tracklist

def fetch_youtube(query_or_url):
    print(f"🔍 Searching YouTube: {query_or_url}")
    tracks = []
    if not ENABLE_YOUTUBE:
        return tracks
    try:
        res = subprocess.run(
            [ "yt-dlp", f"ytsearch{MAX_RESULTS}:{query_or_url}", "-J"],
            capture_output=True, text=True, check=True
        )
        data = json.loads(res.stdout)
        for e in data.get("entries", []):
            vid = e.get("id")
            if vid:
                tracks.append({
                    "title": e.get("title", ""),
                    "url": f"https://www.youtube.com/watch?v={vid}",
                    "source": "youtube"
                })
    except Exception as e:
        print(f"❌ Error searching YouTube: {e}")
    return tracks

def scrape_soundcloud(url):
    print(f"🔍 Scraping SoundCloud: {url}")
    tracks = []
    if not ENABLE_SOUNDCLOUD:
        return tracks
    try:
        res = subprocess.run(
            ["scdl", "--playlist", url, "--dump-json"],
            capture_output=True, text=True
        )
        for line in res.stdout.splitlines():
            data = json.loads(line)
            desc = data.get("description", "")
            extracted = tracklist.extract_tracks_from_text(desc)
            tracks.extend(extracted)
    except Exception as e:
        print(f"❌ Error scraping SoundCloud: {e}")
    return tracks

def handle_input(input_str):
    input_str = input_str.strip()
    if "soundcloud.com" in input_str:
        return scrape_soundcloud(input_str)
    if "youtube.com" in input_str or ENABLE_YOUTUBE:
        return fetch_youtube(input_str)
    return []
