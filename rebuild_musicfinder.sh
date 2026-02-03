#!/bin/bash
set -Eeuo pipefail

BASE=~/musicdowlder/musicfinder
mkdir -p "$BASE/core" "$BASE/ui" "$BASE/downloads" "$BASE/data"
cd "$BASE"

echo "🧹 Cleaning old files…"
rm -rf "$BASE/musicfinder.py" "$BASE/startapp" "$BASE/core" "$BASE/ui"

echo "📦 Rebuilding MusicFinder CLI + Headless API…"

# -----------------------------
# Core: Store (SQLite)
# -----------------------------
cat > core/store.py <<'EOF'
import sqlite3, os
DB="data/music.db"
os.makedirs("data", exist_ok=True)

class Store:
    def __init__(self):
        self.db=sqlite3.connect(DB, check_same_thread=False)
        self.db.execute("CREATE TABLE IF NOT EXISTS queue(id INTEGER PRIMARY KEY, query TEXT)")
        self.db.execute("CREATE TABLE IF NOT EXISTS done(id INTEGER PRIMARY KEY, title TEXT, path TEXT)")
        self.db.commit()
    def add_queue(self,q):
        self.db.execute("INSERT INTO queue(query) VALUES(?)",(q,))
        self.db.commit()
    def get_queue(self):
        return self.db.execute("SELECT id,query FROM queue").fetchall()
    def clear_queue(self):
        self.db.execute("DELETE FROM queue")
        self.db.commit()
    def add_done(self,t,p):
        self.db.execute("INSERT INTO done(title,path) VALUES(?,?)",(t,p))
        self.db.commit()
    def get_done(self):
        return self.db.execute("SELECT title,path FROM done").fetchall()
EOF

# -----------------------------
# Core: Search (placeholder for free sources)
# -----------------------------
cat > core/search.py <<'EOF'
import requests
SOURCES=[
  "https://skysound7.com",
  "https://muzon-club.com",
  "https://web.ligaudio.ru"
]

def search(query):
    results=[]
    for base in SOURCES:
        try:
            r=requests.get(base,timeout=10)
            if r.ok:
                results.append(f"{base} :: search {query}")
        except:
            pass
    if not results:
        results.append("No free sources responded")
    return results[:50]
EOF

# -----------------------------
# Core: Downloader (fake placeholder)
# -----------------------------
cat > core/downloader.py <<'EOF'
import os, subprocess, uuid
DL="downloads"
os.makedirs(DL,exist_ok=True)
def fake_download(label):
    name=f"{label[:40].replace(' ','_')}_{uuid.uuid4().hex[:6]}.mp3"
    path=os.path.join(DL,name)
    subprocess.run(["ffmpeg","-f","lavfi","-i","anullsrc","-t","1",path],
                   stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    return path
EOF

# -----------------------------
# UI: Androsh-style multi-panel
# -----------------------------
cat > ui/app.py <<'EOF'
from blessed import Terminal
from core.store import Store
from core.search import search
from core.downloader import download

term = Terminal()
db = Store()

def draw(results):
    print(term.clear)
    print(term.bold("🎵 MusicFinder CLI + Headless API").center(term.width))
    w = term.width // 3
    print(term.move(2,0) + term.reverse(" SEARCH ".center(w)) +
          term.reverse(" QUEUE ".center(w)) +
          term.reverse(" DOWNLOADED ".center(w)))
    max_rows = 10
    for i in range(max_rows):
        left = results[i] if i < len(results) else ""
        q = db.get_queue()
        middle = q[i][1] if i < len(q) else ""
        d = db.get_done()
        right = d[i][0] if i < len(d) else ""
        print(f"{str(left)[:w].ljust(w)}{str(middle)[:w].ljust(w)}{str(right)[:w].ljust(w)}")

def run():
    results=[]
    with term.fullscreen(), term.cbreak():
        while True:
            draw(results)
            print("\n> ", end="", flush=True)
            val = term.inkey()
            if val.lower()=="c":
                break
            if val.name=="KEY_ENTER":
                for _,q in db.get_queue():
                    path=download(q)
                    db.add_done(q,path)
                db.clear_queue()
                results=[]
                continue
            query = ""
            if val.is_sequence:
                continue
            query += val
            while True:
                ch = term.inkey()
                if ch.name=="KEY_ENTER":
                    break
                elif ch.lower()=="c":
                    return
                else:
                    query += ch
            if query.strip():
                db.add_queue(query.strip())
                results=search(query.strip())
EOF

# -----------------------------
# Runtime: CLI + automatic headless API
# -----------------------------
cat > core/runtime.py <<'EOF'
import threading
from ui.app import run
from core.store import Store
from core.search import search
from core.downloader import download

def start_cli():
    try:
        run()
    except KeyboardInterrupt:
        print("\n👋 Exited cleanly")

def start_api():
    try:
        from fastapi import FastAPI
        import uvicorn
    except ImportError:
        print("⚠️ FastAPI/uvicorn not installed, skipping API")
        return

    app = FastAPI()
    db = Store()

    @app.get("/queue")
    def get_queue():
        return {"queue": db.get_queue()}

    @app.get("/download")
    def download_next():
        items = db.get_queue()
        paths=[]
        for _,q in items:
            path=download(q)
            db.add_done(q,path)
            paths.append(path)
        db.clear_queue()
        return {"downloaded": paths}

    @app.get("/search")
    def api_search(q: str):
        return {"results": search(q)}

    uvicorn.run(app, host="0.0.0.0", port=8000)

def start():
    t = threading.Thread(target=start_api, daemon=True)
    t.start()
    start_cli()
EOF

# -----------------------------
# Main entry
# -----------------------------
cat > musicfinder.py <<'EOF'
from core.runtime import start
if __name__=="__main__":
    start()
EOF

# -----------------------------
# Start script
# -----------------------------
cat > startapp <<'EOF'
#!/data/data/com.termux/files/usr/bin/bash
cd "$(dirname "$0")"
echo "🎵 MusicFinder CLI + Headless API starting…"
python3 musicfinder.py || true
echo "↩ Returned to shell"
EOF
chmod +x startapp

echo "✅ MusicFinder CLI + Headless API rebuilt successfully. Run with ./startapp"

chmod +x rebuild_musicfinder.sh
bash rebuild_musicfinder.sh
