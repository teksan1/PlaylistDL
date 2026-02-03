import requests
from bs4 import BeautifulSoup

def search_soundcloud(query):
    """Scrape SoundCloud search results"""
    results = []
    try:
        r = requests.get(f"https://soundcloud.com/search?q={query}", timeout=5)
        soup = BeautifulSoup(r.text, "html.parser")
        for link in soup.find_all("a"):
            href = link.get("href")
            if href and href.startswith("/"):
                results.append("https://soundcloud.com" + href)
    except Exception:
        pass
    return results
