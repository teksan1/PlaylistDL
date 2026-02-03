import os
import requests
from yt_dlp import YoutubeDL
from core.config import DOWNLOAD_DIR, ENABLE_REAL_DOWNLOAD, ENABLE_YOUTUBE, ENABLE_SOUNDCLOUD

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download(url):
    filename = os.path.join(DOWNLOAD_DIR, url.split("/")[-1])
    if not ENABLE_REAL_DOWNLOAD:
        return filename
    try:
        if "youtube.com" in url and ENABLE_YOUTUBE:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": filename,
                "quiet": True,
                "noplaylist": True
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        elif "soundcloud.com" in url and ENABLE_SOUNDCLOUD:
            ydl_opts = {
                "format": "bestaudio/best",
                "outtmpl": filename,
                "quiet": True,
            }
            with YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
        else:
            r = requests.get(url, stream=True, timeout=10)
            with open(filename, "wb") as f:
                for chunk in r.iter_content(1024*10):
                    f.write(chunk)
        return filename
    except Exception as e:
        print(f"⚠️ Failed to download {url}: {e}")
        return None
