#  StudyForge — All-in-One Study Companion

A comprehensive desktop study application combining **Pomodoro Timer**, **Active Recall**, **Spaced Repetition (SM-2)**, **Lecture Notes Management**, and **Claude AI Integration** into a single, polished Windows-native tool.

## Download — No Python Required

Go to the [**Releases**](../../releases) page and download the latest **StudyForge.exe**. Double-click to run — no installation or setup needed.

> Two builds are available: **StudyForge.exe** (full-featured) and **StudyForge_v2.exe** (streamlined with setup wizard). Both are standalone and require no Python.
>
> A **Latest Build** pre-release is automatically published from the `main` branch whenever changes are pushed. Tagged releases (e.g. `v1.0.0`) are created for stable milestones.

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

## Potential New Use-Cases (Competitive Gap List)

Based on common workflows in Anki, RemNote, Quizlet, Forest, Notion, and Obsidian learning setups, these are high-impact use-cases StudyForge can own next:

1. **Exam countdown planning**  
   Auto-build a daily review queue from exam date + syllabus weight, not just card due dates.

2. **Course-mode study plans**  
   Semester templates (law, med, language, STEM) that preconfigure Pomodoro, card limits, and weekly targets.

3. **Missed-question recovery loop**  
   Convert wrong quiz answers into tagged flashcards automatically and schedule immediate reinforcement.

4. **Source-linked flashcards**  
   Each card keeps a citation jump-back to the exact note section/PDF page for fast context recovery.

5. **AI oral exam / viva mode**  
   Voice-style rapid questioning with follow-up depth checks and confidence scoring for verbal prep.

6. **Case briefing workflows (law-specific)**  
   Generate issue/rule/application/conclusion briefs from notes and turn each section into recall drills.

7. **Memory decay risk alerts**  
   Predict likely-forgotten topics before they become due and prompt pre-emptive review.

8. **Study accountability mode**  
   Weekly commitment tracking (hours, streak quality, target completion) with “at-risk” warnings.

9. **Adaptive interleaving by weakness**  
   Mix topics dynamically based on recent error patterns instead of static random shuffling.

10. **One-click exam simulation**  
   Time-boxed mixed quiz + short-answer + essay practice set from selected notes/tags.
