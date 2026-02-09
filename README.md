#  StudyForge — All-in-One Study Companion

A comprehensive desktop study application combining **Pomodoro Timer**, **Active Recall**, **Spaced Repetition (SM-2)**, **Lecture Notes Management**, and **Claude AI Integration** into a single, polished Windows-native tool.

## Download — No Python Required

Go to the [**Releases**](../../releases) page and download the latest **StudyForge.exe**. Double-click to run — no installation or setup needed.

> Two builds are available: **StudyForge.exe** (full-featured) and **StudyForge_v2.exe** (streamlined with setup wizard). Both are standalone and require no Python.

##  Repository Contents

This repository contains two versions of the StudyForge application:

### `study_app/` — Full-Featured Version
The complete production-ready version with PyInstaller build support:
- Download pre-built `.exe` from [Releases](../../releases) — no Python needed
- Build standalone Windows `.exe` with `build.bat` via PyInstaller
- Comprehensive feature set including interleaved practice
- Detailed documentation
- See [study_app/README.md](study_app/README.md) for complete setup instructions

### `study_app_v2/` — Streamlined Version  
A simplified version with first-run setup wizard:
- Download pre-built `.exe` from [Releases](../../releases) — no Python needed
- `StudyForge.bat` for running from source (auto-downloads Python if needed)
- Build your own `.exe` with `build.bat` via PyInstaller
- In-app configuration via setup wizard and Settings tab
- See [study_app_v2/README.md](study_app_v2/README.md) for quick start guide

## Key Features

- **Pomodoro Timer** — Configurable work/break intervals with session tracking
- **Flashcards + SRS** — Anki-style spaced repetition using SM-2 algorithm
- **Active Recall Quiz** — AI-generated quiz questions from lecture notes
- **Notes Manager** — Import and manage `.txt`, `.md`, `.pdf`, `.docx` files with rich markdown editing, preview, and focus mode
- **Essays** — Essay writing with rubric upload and AI grading
- **Hypotheticals** — AI-generated legal hypothetical scenarios from your notes
- **Class Participation** — AI-generated discussion questions for class prep
- **Claude AI Integration** — Auto-generate flashcards, quizzes, and explanations
- **Dashboard** — Daily stats, streak tracking, review forecasts

## Quick Start

### Option 1: Download Pre-Built App (Recommended)
1. Go to [Releases](../../releases)
2. Download `StudyForge.exe` or `StudyForge_v2.exe`
3. Double-click to run — that's it!

### Option 2: Run from Source (with auto Python setup)
```bash
cd study_app_v2
StudyForge.bat
```
> If Python isn't installed, the launcher will offer to download a portable copy automatically.

### Option 3: Run from Source (manual)
```bash
cd study_app
pip install -r requirements.txt
python main.py
```

## Building the .exe Yourself

Both versions include build scripts that produce standalone `.exe` files via PyInstaller:

```bash
cd study_app    # or study_app_v2
build.bat
```

The GitHub Actions workflow also builds `.exe` files automatically on each tagged release.

## Requirements

- **End users:** Windows 10/11 — no Python needed
- **Developers:** Python 3.10+ (for running from source or building)
- Claude API key (optional, for AI features)
