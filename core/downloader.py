import subprocess
import os
from core.config import DOWNLOAD_DIR, ENABLE_REAL_DOWNLOAD

def download_track(track):
    url = track.get("url")
    title = track.get("title")
    if not url:
        print(f"❌ No URL for {title}")
        return
    print(f"⬇️ Downloading: {title}")
    if ENABLE_REAL_DOWNLOAD:
        os.makedirs(DOWNLOAD_DIR, exist_ok=True)
        subprocess.run([
            "yt-dlp",
            "-o", os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
            url
        ])

def download_multi(tracks):
    for t in tracks:
        download_track(t)
