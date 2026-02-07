#  StudyForge — All-in-One Study Companion

A comprehensive desktop study application combining **Pomodoro Timer**, **Active Recall**, **Spaced Repetition (SM-2)**, **Lecture Notes Management**, and **Claude AI Integration** into a single, polished Windows-native tool.

##  Repository Contents

This repository contains two versions of the StudyForge application:

### `study_app/` — Full-Featured Version
The complete production-ready version with PyInstaller build support:
- Build standalone Windows .exe files
- Comprehensive feature set
- Detailed documentation
- See [study_app/README.md](study_app/README.md) for complete setup instructions

### `study_app_v2/` — Streamlined Version  
A simplified version with one-click launcher:
- `StudyForge.bat` for instant setup
- Setup wizard on first run
- In-app configuration
- See [study_app_v2/README.md](study_app_v2/README.md) for quick start guide

## Key Features

- **Pomodoro Timer** — Configurable work/break intervals with session tracking
- **Flashcards + SRS** — Anki-style spaced repetition using SM-2 algorithm
- **Active Recall Quiz** — AI-generated quiz questions from lecture notes
- **Notes Manager** — Import and manage `.txt`, `.md`, `.pdf`, `.docx` files
- **Notepad** — Rich text editor with markdown formatting and focus mode
- **Essays** — Essay writing with rubric upload and AI grading
- **Hypotheticals** — AI-generated legal hypothetical scenarios from your notes
- **Class Participation** — AI-generated discussion questions for class prep
- **Claude AI Integration** — Auto-generate flashcards, quizzes, and explanations
- **Dashboard** — Daily stats, streak tracking, review forecasts

## Quick Start

Choose your preferred version:

**Option 1: Streamlined Setup (Recommended for beginners)**
```bash
cd study_app_v2
StudyForge.bat
```

**Option 2: Full Setup (Recommended for building .exe)**
```bash
cd study_app
python main.py
```
## Requirements

- Windows 10/11
- Python 3.10+
- Claude API key (optional, for AI features)

For detailed setup instructions, refer to the README in each application folder.
