Plan out your process before writing code and wait for approval from the user. Detail your plan and review it for any inaccuracies or common errors.

## Project Overview

StudyForge is a Windows desktop study app built with **Python 3.10+** and **CustomTkinter**. It combines Pomodoro Timer, Flashcards with SM-2 spaced repetition, AI-powered quizzes, and lecture notes management. There are two variants:

- **`study_app/`** — Production version with PyInstaller `.exe` build support and `%APPDATA%\StudyForge` data storage.
- **`study_app_v2/`** — Streamlined version with a `.bat` launcher, first-run setup wizard, and in-app settings.

Both share the same core architecture; v2 adds `config_manager.py`, `ui/settings.py`, and `ui/setup_wizard.py`.

## Tech Stack

- **UI:** CustomTkinter (dark theme via `ui/styles.py`)
- **Database:** SQLite3 (WAL mode, foreign keys, parameterized queries)
- **AI:** Anthropic Claude API (`anthropic` SDK)
- **Document parsing:** PyMuPDF (PDF), python-docx (DOCX), Markdown
- **Build:** PyInstaller (study_app only)
- **Tests:** None yet

## Architecture

```
main.py              → Entry point, config loading
database.py          → SQLite CRUD, context-managed connections
srs_engine.py        → SM-2 algorithm (rating 0-5)
claude_client.py     → AI generation (flashcards, quizzes, summaries)
paths.py             → Path resolution (study_app only)
config_manager.py    → Config persistence (study_app_v2 only)
ui/
  app.py             → Main window, sidebar navigation
  styles.py          → COLORS, FONTS, PADDING constants
  dashboard.py       → Stats, streaks, review forecasts
  flashcards.py      → Card review, creation, AI generation
  pomodoro.py        → Timer with session tracking
  notes.py           → File import (.txt, .md, .pdf, .docx)
  quiz.py            → AI-generated multiple-choice quizzes
  settings.py        → In-app config (study_app_v2 only)
  setup_wizard.py    → First-run wizard (study_app_v2 only)
```

## Coding Conventions

- **Classes:** PascalCase (`StudyForgeApp`, `ClaudeStudyClient`)
- **Functions/methods:** snake_case (`get_all_notes`, `review_card`)
- **Constants:** UPPERCASE dicts/frozensets (`COLORS`, `FONTS`, `VALID_STAT_FIELDS`)
- **Docstrings:** Triple-quote module-level docstrings describing purpose; function docstrings with Args/Returns where non-trivial
- **Imports:** Standard library first, then third-party, then project modules; relative imports within `ui/` package
- **Error handling:** Try-except with rollback for DB operations; graceful fallbacks for AI JSON parsing; no formal logging framework (print statements)
- **SQL safety:** Always use parameterized queries (`?` placeholders); whitelist valid column names via `VALID_STAT_FIELDS`

## Database Schema

Tables: `notes`, `flashcards` (with SM-2 fields: `easiness_factor`, `interval`, `repetitions`, `next_review`), `review_log`, `pomodoro_sessions`, `daily_stats`. Foreign keys cascade deletes from notes to flashcards. All connections go through the `get_connection()` context manager.

## Key Patterns

- **DB access:** Always use `with get_connection() as conn:` — never open raw connections
- **UI tabs:** Each tab is a `CTkFrame` subclass that receives the database and client as constructor args
- **Styles:** Import from `ui.styles` — never hardcode colors, fonts, or padding
- **Config:** In study_app, config lives at `%APPDATA%\StudyForge/config.json`; in study_app_v2, use `config_manager.load_config()` / `save_config()`
- **AI responses:** Always parse with `ClaudeStudyClient._parse_json_response()` which handles markdown-fenced JSON; never assume raw JSON from Claude

## When Making Changes

- Changes to shared logic (database.py, srs_engine.py, claude_client.py) likely need to be applied to **both** `study_app/` and `study_app_v2/`
- UI changes should respect the existing dark theme via `ui/styles.py` constants
- New database tables or columns require migration logic in `init_db()`
- Keep the two app variants consistent unless a feature is intentionally v2-only
