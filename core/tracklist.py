import re

def extract_tracks_from_text(text):
    tracks = []
    lines = text.splitlines()
    for line in lines:
        clean = line.strip()
        if not clean:
            continue
        clean = re.sub(r"(?:\d{1,2}:\d{2})|▶|https?://\S+|[#\*\-–—•]", "", clean).strip()
        if clean:
            tracks.append({"title": clean})
    return tracks
