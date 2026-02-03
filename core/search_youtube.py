from yt_dlp import YoutubeDL

def search_youtube(query):
    results = []
    try:
        ydl_opts = {"quiet": True, "skip_download": True, "format": "bestaudio/best"}
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(f"ytsearch5:{query}", download=False)
            for entry in info.get("entries", []):
                results.append(f"https://www.youtube.com/watch?v={entry['id']}")
    except Exception:
        pass
    return results
