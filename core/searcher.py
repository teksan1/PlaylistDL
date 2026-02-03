import requests, re
from urllib.parse import quote

# ---------------- Free MP3 site search ----------------
FREE_SITES = [
    "https://freemusicarchive.org",
    "https://archive.org/details/audio"
]

def search_free_sites(query):
    results = []
    for site in FREE_SITES:
        try:
            url = f"{site}/search?q={quote(query)}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                # Very simple regex to find mp3 links
                matches = re.findall(r'https?://[^ ]+\.mp3', r.text)
                results.extend(matches)
        except:
            continue
    return results

# ---------------- DuckDuckGo search fallback ----------------
def duckduckgo_search(query):
    results = []
    try:
        search_url = f"https://html.duckduckgo.com/html/?q={quote(query)}+mp3"
        r = requests.get(search_url, timeout=10)
        matches = re.findall(r'https?://[^ ]+\.mp3', r.text)
        results.extend(matches)
    except:
        pass
    return results

# ---------------- YouTube search placeholder ----------------
def search_youtube(query):
    # Just return a search URL, downloading handled elsewhere
    query_encoded = quote(query)
    return [f"https://www.youtube.com/results?search_query={query_encoded}"]

# ---------------- SoundCloud search placeholder ----------------
def search_soundcloud(query):
    query_encoded = quote(query)
    return [f"https://soundcloud.com/search?q={query_encoded}"]
