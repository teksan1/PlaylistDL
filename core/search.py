import requests
from config import CONFIG

HEADERS = {"User-Agent": "Mozilla/5.0"}

def duckduckgo_mp3_search(query):
    if not CONFIG["enable_duckduckgo"]:
        return []

    results = []
    r = requests.get(
        "https://duckduckgo.com/html/",
        params={"q": f"{query} filetype:mp3"},
        headers=HEADERS,
        timeout=15
    )

    for line in r.text.splitlines():
        if ".mp3" in line and "http" in line:
            url = "http" + line.split("http")[1].split('"')[0]
            if url.endswith(".mp3"):
                results.append({
                    "source": "duckduckgo",
                    "type": "mp3",
                    "url": url
                })

    return results
