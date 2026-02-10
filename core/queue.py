QUEUE_LIST = []

def add_to_queue(tracks):
    QUEUE_LIST.extend(tracks)

def clear_queue():
    QUEUE_LIST.clear()
    print("🧹 Queue cleared")

def display_queue():
    if not QUEUE_LIST:
        print("📭 Queue empty")
        return
    print("\n🎵 Queue:")
    for i, t in enumerate(QUEUE_LIST, 1):
        print(f"{i}) {t['title']}")

def select_from_queue():
    if not QUEUE_LIST:
        return []
    display_queue()
    sel = input("Select items (ENTER=all): ").strip()
    if not sel:
        return list(range(len(QUEUE_LIST)))
    out = set()
    for part in sel.split(","):
        if "-" in part:
            a, b = part.split("-")
            for i in range(int(a), int(b) + 1):
                out.add(i - 1)
        elif part.isdigit():
            out.add(int(part) - 1)
    return sorted(i for i in out if 0 <= i < len(QUEUE_LIST))
