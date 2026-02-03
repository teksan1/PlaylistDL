from fastapi import FastAPI, Query
from core.pipeline import acquire, download

app = FastAPI(title="MusicFinder API")

@app.get("/search")
async def search_track(query: str = Query(..., description="Artist - Track")):
    results = acquire(query)
    return {"query": query, "results": results}

@app.get("/download")
async def download_track(url: str = Query(..., description="URL to download")):
    path = download(url)
    return {"url": url, "saved_path": path}
