"""
main.py — Entry point for StudyForge.
Double-click StudyForge.bat to launch, or run: python main.py
"""

import os
import sys

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_DIR)

from database import init_db
from config_manager import load_config, is_first_run, get_api_key
from claude_client import ClaudeStudyClient
from ui.app import StudyForgeApp


def try_connect_claude(config: dict):
    """Attempt to connect to Claude API. Returns client or None."""
    key = config.get("claude_api_key", "")
    if not key:
        return None

    model = config.get("claude_model", "claude-sonnet-4-5-20250929")
    try:
        client = ClaudeStudyClient(key, model)
        ok, _ = client.test_key(key, model)
        if ok:
            print(f"[StudyForge] Claude connected  ·  Model: {model}")
            return client
        print("[StudyForge] Claude API key invalid — AI features disabled")
        return None
    except Exception as e:
        print(f"[StudyForge] Claude connection failed: {e}")
        return None


def main():
    print("=" * 50)
    print("  🎓 StudyForge — All-in-One Study Companion")
    print("=" * 50)

    init_db()
    config = load_config()

    show_wizard = is_first_run()

    # Only try connecting if not first run (wizard handles its own connection)
    claude_client = None
    if not show_wizard:
        claude_client = try_connect_claude(config)

    print("[StudyForge] Launching...")
    app = StudyForgeApp(config, claude_client, show_wizard=show_wizard)
    app.mainloop()


if __name__ == "__main__":
    main()
