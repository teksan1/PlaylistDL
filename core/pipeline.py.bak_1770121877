import subprocess
import json
import os
import requests
from bs4 import BeautifulSoup
from config import CONFIG
from queue import Queue
import threading

DOWNLOAD_DIR = CONFIG.get("download_dir", "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ---------------------------
# YouTube / SoundCloud search using yt-dlp
# ---------------------------
def yt_dlp_search(query, source="youtube", limit=5):
    if source == "youtube" and not CONFIG["enable_youtube"]:
        return []
    if source == "soundcloud" and not CONFIG["enable_soundcloud"]:
        return []

    cmd = [
        "yt-dlp",
        f"{source}search{limit}:{query}",
        "--dump-json",
        "--skip-download",
        "--no-playlist"
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    results = []
    for line in proc.stdout.splitlines():
        try:
            data = json.loads(line)
            results.append({
                "title": data.get("title"),
                "url": data.get("webpage_url"),
                "source": data.get("extractor"),
                "duration": data.get("duration")
            })
        except json.JSONDecodeError:
            continue
    return results

# ---------------------------
# DuckDuckGo fallback
# ---------------------------
def duckduckgo_search(query, max_results=5):
    if not CONFIG["enable_duckduckgo"]:
        return []
    search_url = f"https://duckduckgo.com/html/?q={query.replace(' ', '+')}+mp3"
    r = requests.get(search_url, headers={"User-Agent": "Mozilla/5.0"})
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(r.text, "html.parser")
    results = []
    for a in soup.select("a[href$='.mp3']")[:max_results]:
        results.append({
            "title": os.path.basename(a['href']),
            "url": a['href'],
            "source": "duckduckgo",
            "duration": None
        })
    return results

# ---------------------------
# Playlist extraction
# ---------------------------
def yt_dlp_playlist(url):
    cmd = [
        "yt-dlp",
        "--dump-json",
        "--flat-playlist",
        url
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    tracks = []
    for line in proc.stdout.splitlines():
        try:
            data = json.loads(line)
            tracks.append({
                "title": data.get("title"),
                "url": data.get("url") if "url" in data else data.get("webpage_url"),
                "source": "playlist"
            })
        except json.JSONDecodeError:
            continue
    return tracks

# ---------------------------
# Acquire tracks from all sources
# ---------------------------
def acquire(query):
    results = []
    results += yt_dlp_search(query, "youtube", CONFIG["max_results"])
    results += yt_dlp_search(query, "soundcloud", CONFIG["max_results"])
    results += duckduckgo_search(query, CONFIG["max_results"])
    if not results:
        return [{"title": "No results found", "url": None, "source": "none"}]
    return results

# ---------------------------
# Multi-threaded download
# ---------------------------
def download_worker(queue_items, results):
    while True:
        try:
            item = queue_items.get_nowait()
        except:
            break
        try:
            if CONFIG['analysis_only'] or not CONFIG['allow_downloads']:
                results['skipped'] += 1
                print(f"Skipped: {item.get('title')}")
            else:
                url = item['url']
                title = item.get('title', 'track')
                cmd = [
                    'yt-dlp',
                    '-x',
                    '--audio-format', 'mp3',
                    '--audio-quality', '0',
                    '-o', os.path.join(DOWNLOAD_DIR, '%(title)s.%(ext)s'),
                    url
                ]
                subprocess.run(cmd)
                results['success'] += 1
                print(f"Downloaded: {title}")
        except Exception as e:
            results['failed'] += 1
            print(f"Failed: {item.get('title')} ({e})")
        finally:
            queue_items.task_done()

def download_multi(queue_list, max_threads=4):
    queue_items = Queue()
    results = {'success': 0, 'failed': 0, 'skipped': 0}
    for item in queue_list:
        queue_items.put(item)
    threads = []
    for _ in range(min(max_threads, queue_items.qsize())):
        t = threading.Thread(target=download_worker, args=(queue_items, results))
        t.start()
        threads.append(t)
    queue_items.join()
    for t in threads:
        t.join()
    print(f"✅ Download complete. Success: {results['success']}, Failed: {results['failed']}, Skipped: {results['skipped']}")
    return results
