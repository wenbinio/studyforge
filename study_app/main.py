"""
main.py — Entry point for StudyForge.

Works both as:
  python main.py       (development)
  StudyForge.exe       (frozen PyInstaller build)
"""

import json
import os
import sys

# ── Path setup ────────────────────────────────────────────────────
# Must happen before any local imports so modules resolve correctly.
if getattr(sys, 'frozen', False):
    # Running as PyInstaller bundle — add the temp extract dir to path
    sys.path.insert(0, sys._MEIPASS)
else:
    PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, PROJECT_DIR)

from paths import get_config_path, ensure_config_exists, get_user_data_dir, DEFAULT_CONFIG
from database import init_db
from claude_client import ClaudeStudyClient
from ui.app import StudyForgeApp


def load_config() -> dict:
    """Load configuration from user data directory."""
    default_config = dict(DEFAULT_CONFIG)

    config_path = ensure_config_exists()

    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                user_config = json.load(f)
            default_config.update(user_config)
        except Exception as e:
            print(f"Warning: Could not load config.json: {e}")

    # Store the config path so the app can tell users where it is
    default_config["_config_path"] = config_path
    default_config["_data_dir"] = get_user_data_dir()

    return default_config


def init_claude_client(config: dict):
    """Initialize the Claude API client if a valid key is present."""
    api_key = config.get("claude_api_key", "")
    if not api_key or api_key == "YOUR_API_KEY_HERE":
        print("[StudyForge] No Claude API key configured. AI features disabled.")
        return None

    model = config.get("claude_model", "claude-sonnet-4-5-20250929")
    try:
        client = ClaudeStudyClient(api_key, model)
        ok, msg = client.test_connection()
        if ok:
            print(f"[StudyForge] Claude API connected. Model: {model}")
            return client
        else:
            print(f"[StudyForge] Claude API connection failed: {msg}")
            return None
    except Exception as e:
        print(f"[StudyForge] Error initializing Claude client: {e}")
        return None


def main():
    print("=" * 50)
    print("  StudyForge — All-in-One Study Companion")
    print("=" * 50)

    # Initialize database
    print("[StudyForge] Initializing database...")
    init_db()

    # Load config
    print("[StudyForge] Loading configuration...")
    config = load_config()
    print(f"[StudyForge] Data directory: {config['_data_dir']}")
    print(f"[StudyForge] Config file:    {config['_config_path']}")

    # Initialize Claude client
    print("[StudyForge] Connecting to Claude API...")
    claude_client = init_claude_client(config)

    # Launch the app
    print("[StudyForge] Launching application...")
    app = StudyForgeApp(config, claude_client)
    app.mainloop()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        # If the app crashes before the window opens, show a native error dialog
        try:
            import tkinter as tk
            from tkinter import messagebox
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror(
                "StudyForge — Startup Error",
                f"Failed to start StudyForge:\n\n{e}\n\n"
                f"If this persists, try deleting the data folder and restarting."
            )
            root.destroy()
        except Exception:
            pass
        raise
