import os
import requests
from config import CONFIG

os.makedirs(CONFIG["download_dir"], exist_ok=True)

def download_mp3(item):
    filename = item["url"].split("/")[-1]
    path = os.path.join(CONFIG["download_dir"], filename)

    r = requests.get(item["url"], stream=True, timeout=30)
    r.raise_for_status()

    with open(path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)

    return path
