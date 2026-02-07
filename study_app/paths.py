"""
paths.py — Centralized path resolution for StudyForge.

When running from source:   All paths relative to project directory.
When running as frozen .exe: User data goes to %APPDATA%/StudyForge,
                              bundled assets come from sys._MEIPASS.
"""

import os
import sys
import shutil


def is_frozen() -> bool:
    """Check if running as a PyInstaller bundle."""
    return getattr(sys, 'frozen', False)


def get_bundle_dir() -> str:
    """Get the directory where bundled assets live (or project root in dev)."""
    if is_frozen():
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_user_data_dir() -> str:
    """
    Get the directory for user-writable data (database, config).
    - Frozen: %APPDATA%/StudyForge  (persists across updates)
    - Dev:    <project_root>        (same as source)
    """
    if is_frozen():
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        data_dir = os.path.join(appdata, "StudyForge")
    else:
        data_dir = os.path.dirname(os.path.abspath(__file__))
    os.makedirs(data_dir, exist_ok=True)
    return data_dir


def get_db_dir() -> str:
    """Get the directory for the SQLite database."""
    db_dir = os.path.join(get_user_data_dir(), "data")
    os.makedirs(db_dir, exist_ok=True)
    return db_dir


def get_db_path() -> str:
    """Get the full path to the SQLite database file."""
    return os.path.join(get_db_dir(), "studyforge.db")


def get_config_path() -> str:
    """Get the path to config.json (user-writable location)."""
    return os.path.join(get_user_data_dir(), "config.json")


def ensure_config_exists():
    """
    On first run of .exe, copy the default config.json to user data dir.
    In dev mode this is a no-op (config is already in the project dir).
    """
    config_path = get_config_path()
    if not os.path.exists(config_path):
        # Try to copy bundled default config
        bundled_config = os.path.join(get_bundle_dir(), "config.json")
        if os.path.exists(bundled_config):
            shutil.copy2(bundled_config, config_path)
        else:
            # Write a fresh default
            import json
            default = {
                "claude_api_key": "YOUR_API_KEY_HERE",
                "claude_model": "claude-sonnet-4-5-20250929",
                "pomodoro_work_minutes": 25,
                "pomodoro_short_break": 5,
                "pomodoro_long_break": 15,
                "pomodoro_sessions_before_long_break": 4,
                "daily_new_cards_limit": 20,
                "theme": "dark",
            }
            with open(config_path, "w") as f:
                json.dump(default, f, indent=2)
    return config_path
