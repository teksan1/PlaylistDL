#!/usr/bin/env python3
import sys, re, json, subprocess, requests, tempfile
from bs4 import BeautifulSoup
from urllib.parse import urlparse
from pathlib import Path

HEADERS = {"User-Agent": "PlaylistDL Universal Extractor"}

def clean(line):
    line = re.sub(r"\[[^\]]+\]", "", line)
    line = re.sub(r"\([^)]*\)", "", line)
    line = re.sub(r"\d{1,2}:\d{2}", "", line)
    line = re.sub(r"https?://\S+", "", line)
    line = re.sub(r"[▶►•◆●]", "", line)
    line = re.sub(r"\s+", " ", line).strip(" -–•\t")
    return line

def looks_like_track(line):
    if not line or len(line)<3 or len(line)>100:
        return False
    return True

def extract_yt_sc(url):
    try:
        res=subprocess.run(["yt-dlp","-J",url], capture_output=True, text=True, check=True)
        data=json.loads(res.stdout)
        desc=data.get("description","")
        artist=data.get("uploader","Unknown Artist")
        lines=[clean(l) for l in desc.splitlines() if looks_like_track(clean(l))]
        return artist, lines
    except:
        return "Unknown Artist", []

def extract_setlist(url):
    html=requests.get(url, headers=HEADERS).text
    soup=BeautifulSoup(html,"html.parser")
    artist_meta=soup.select_one("meta[property='og:title']")
    artist=artist_meta["content"].split(" Setlist")[0] if artist_meta else "Unknown Artist"
    tracks=[clean(li.get_text()) for li in soup.select("li.setlistParts-song")]
    return artist, tracks

def extract_generic(url):
    html=requests.get(url, headers=HEADERS).text
    soup=BeautifulSoup(html,"html.parser")
    title=soup.title.string if soup.title else "Unknown Artist"
    artist=title.split("-")[0].strip()
    tracks=[]
    for tag in soup.find_all(["li","p"]):
        text=clean(tag.get_text())
        if text:
            tracks.append(text)
    return artist, list(dict.fromkeys(tracks))

def extract(input_str):
    if input_str.startswith("http://") or input_str.startswith("https://"):
        domain=urlparse(input_str).netloc.lower()
        if "youtube.com" in domain or "youtu.be" in domain or "soundcloud.com" in domain:
            return extract_yt_sc(input_str)
        if "setlist.fm" in domain:
            return extract_setlist(input_str)
        return extract_generic(input_str)
    else:
        lines=[clean(l) for l in input_str.splitlines() if looks_like_track(clean(l))]
        return "Unknown Artist", lines

def normalize(artist, tracks):
    out=[]
    for t in tracks:
        if " - " in t or " – " in t:
            out.append(t)
        else:
            out.append(f"{artist} – {t}")
    return out

def main():
    if len(sys.argv)==1:
        print("Paste tracklist or enter URL (empty line to finish):")
        lines=[]
        while True:
            try: l=input()
            except EOFError: break
            if not l.strip(): break
            lines.append(l)
        input_str="\n".join(lines)
    else:
        input_str=sys.argv[1]
    artist, tracks=extract(input_str)
    if not tracks:
        print("❌ No tracks detected")
        return
    tracks=normalize(artist, tracks)
    json_path=Path(tempfile.gettempdir())/"playlistdl_last.json"
    json_path.write_text(json.dumps(tracks, ensure_ascii=False), encoding="utf-8")
    for t in tracks: print(t)

if __name__=="__main__":
    main()
