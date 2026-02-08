import json
from pathlib import Path

# ------------------- Core Defaults -------------------
ENABLE_REAL_DOWNLOAD = True
ENABLE_CHECKS = False
ENABLE_YOUTUBE = True
ENABLE_SOUNDCLOUD = True
ENABLE_METADATA_EDIT = True

# ------------------- Persistent Config -------------------
CONFIG_FILE = Path(__file__).parent / "user_config.json"

CONFIG = {
    "allow_downloads": ENABLE_REAL_DOWNLOAD,
    "restriction_checks": ENABLE_CHECKS,
    "enable_youtube": ENABLE_YOUTUBE,
    "enable_soundcloud": ENABLE_SOUNDCLOUD,
    "edit_metadata": ENABLE_METADATA_EDIT,
    "allow_js": True,
    "js_runtime_ready": True,
    "enable_js": True,
    "max_results": 1000,
    "download_dir": "downloads",
    "max_threads": 4
}

# ------------------- Save / Load Helpers -------------------
def save_config(cfg=None):
    cfg = cfg or CONFIG
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(cfg, f, indent=2)
    except Exception as e:
        print(f"❌ Failed to save config: {e}")

def load_config():
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                CONFIG.update(data)
        except Exception as e:
            print(f"❌ Failed to load config: {e}")
