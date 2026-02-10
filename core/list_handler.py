import tempfile, json, os
from core import fetchers, tracklist, queue

def handle_list_file(file_path=None):
    if not file_path:
        print("\nPaste your list (artist - title). Empty line to finish:\n")
        lines = []
        while True:
            l = input()
            if not l.strip():
                break
            lines.append(l.strip())
        if not lines:
            print("❌ No entries")
            return []
        tmp = tempfile.gettempdir()
        file_path = os.path.join(tmp, "playlistdl_list.txt")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    tracks = []
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                print(f"🔎 Searching: {line}")
                found = fetchers.handle_input(line)
                if not found:
                    extracted = tracklist.extract_tracks_from_text(line)
                    found.extend(extracted)
                tracks.extend(found)
    queue.add_to_queue(tracks)
    print(f"✅ Added {len(tracks)} tracks")
    return tracks
