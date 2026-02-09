#!/usr/bin/env python3
import json
import os
from pathlib import Path

CONFIG_FILE = Path(__file__).resolve().parent / "config.json"

# Default configuration
CONFIG = {
    "enable_youtube": True,
    "enable_soundcloud": True,
    "enable_duckduckgo": True,
    "restriction_checks": True,
    "copyright_checks": True,
    "analysis_only": False,
    "allow_downloads": True,
    "allow_js": False,
    "js_runtime_ready": False,
    "enable_js": False,
    "max_results": 10,
    "download_dir": str(Path.home() / "Music"),
    "max_threads": 4,
}

def load_config():
    global CONFIG
    if CONFIG_FILE.exists():
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict):
                    CONFIG.update(data)
        except Exception:
            pass

def save_config():
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(CONFIG, f, indent=2)
    except Exception:
        pass
