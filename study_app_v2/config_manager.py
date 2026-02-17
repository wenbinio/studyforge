"""
config_manager.py — Manages app configuration with file persistence.
Handles API key, Pomodoro settings, and theme preferences.
Users never need to touch config.json directly.
"""

import json
import os
import sys


def _get_config_dir() -> str:
    """
    Get the directory for config.json.
    - Frozen (.exe): %APPDATA%/StudyForge  (persists across updates)
    - Dev:           project directory      (next to source files)
    """
    if getattr(sys, 'frozen', False):
        appdata = os.environ.get("APPDATA", os.path.expanduser("~"))
        config_dir = os.path.join(appdata, "StudyForge")
        os.makedirs(config_dir, exist_ok=True)
        return config_dir
    return os.path.dirname(os.path.abspath(__file__))


CONFIG_PATH = os.path.join(_get_config_dir(), "config.json")

DEFAULTS = {
    "ai_provider": "anthropic",
    "claude_api_key": "",
    "claude_model": "claude-sonnet-4-5-20250929",
    "claude_model_hypotheticals": "",
    "claude_model_essays": "",
    "claude_model_participation": "",
    "pomodoro_work_minutes": 25,
    "pomodoro_short_break": 5,
    "pomodoro_long_break": 15,
    "pomodoro_sessions_before_long_break": 4,
    "daily_new_cards_limit": 20,
    "theme": "dark",
    "first_run": True,
}


def load_config() -> dict:
    config = dict(DEFAULTS)
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, "r") as f:
                user = json.load(f)
            config.update(user)
        except Exception:
            pass
    return config


def save_config(config: dict):
    try:
        with open(CONFIG_PATH, "w") as f:
            json.dump(config, f, indent=4)
    except Exception as e:
        print(f"[StudyForge] Warning: Could not save config: {e}")


def get_api_key() -> str:
    return load_config().get("claude_api_key", "")


def set_api_key(key: str):
    config = load_config()
    config["claude_api_key"] = key.strip()
    save_config(config)


def is_first_run() -> bool:
    return load_config().get("first_run", True)


def mark_setup_complete():
    config = load_config()
    config["first_run"] = False
    save_config(config)


def update_setting(key: str, value):
    config = load_config()
    config[key] = value
    save_config(config)
