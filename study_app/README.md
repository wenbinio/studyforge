# 🎓 StudyForge — All-in-One Study Companion for Windows

A comprehensive desktop study application combining **Pomodoro Timer**, **Active Recall**, **Spaced Repetition (SM-2)**, **Lecture Notes Management**, and **Claude AI Integration** into a single, polished Windows-native tool.

---

## ✨ Features

| Module | Description |
|---|---|
| **Pomodoro Timer** | Configurable work/break intervals, session tracking, daily stats |
| **Flashcards + SRS** | Anki-style spaced repetition using the SM-2 algorithm |
| **Interleaved Practice** | Shuffle flashcards and quizzes across topics for deeper learning |
| **Active Recall Quizzer** | AI-generated quiz questions from your lecture notes |
| **Notes Manager** | Import `.txt`, `.md`, `.pdf`, `.docx` lecture notes; tag, search, rich markdown editing, preview, and focus mode |
| **Essays** | Essay writing with rubric upload and AI grading |
| **Hypotheticals** | AI-generated legal hypothetical scenarios from your notes |
| **Class Participation** | AI-generated discussion questions for class preparation |
| **Claude AI Engine** | Auto-generates flashcards, quiz questions, and explanations from notes |
| **Dashboard** | Daily stats, streak tracking, cards due, upcoming reviews |

---

## 🚀 Getting Started

### Option A: Download Pre-Built App (No Python Required)
1. Go to the [Releases](../../releases) page
2. Download **StudyForge.exe**
3. Double-click to run — no installation needed
4. On first run it creates `%APPDATA%\StudyForge\config.json` — click **📁 Open Config** in the sidebar to find it
5. Edit `config.json` to add your Claude API key, then restart

> The `.exe` is fully self-contained. You can move it anywhere on your PC.

### Option B: Run from Source

#### Prerequisites
- **Windows 10/11**
- **Python 3.10+** — Download from [python.org](https://www.python.org/downloads/)
  - ✅ During install, CHECK **"Add Python to PATH"**

#### Steps
```
cd study_app
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Option C: Build the .exe Yourself
Double-click the build script (requires Python):
```
build.bat
```
This installs PyInstaller, bundles everything, and produces a single `dist\StudyForge.exe`.

Or run manually:
```
pip install pyinstaller
pyinstaller StudyForge.spec --noconfirm
```

---

## 🛠️ Configure Your Claude API Key
1. Go to [console.anthropic.com](https://console.anthropic.com/) and create an API key.
2. Open the file `config.json` (or `%APPDATA%\StudyForge\config.json` if using the `.exe`).
3. Paste your key:
```json
{
    "claude_api_key": "sk-ant-xxxxxxxxxxxxxxxxxxxxxxxx",
    "claude_model": "claude-sonnet-4-5-20250929",
    "pomodoro_work_minutes": 25,
    "pomodoro_short_break": 5,
    "pomodoro_long_break": 15,
    "pomodoro_sessions_before_long_break": 4,
    "daily_new_cards_limit": 20,
    "theme": "dark"
}
```

---

## 📂 Project Structure
```
study_app/
├── main.py                 # Entry point (dev + frozen .exe)
├── paths.py                # Centralized path resolution
├── config.json             # Default configuration (bundled into .exe)
├── requirements.txt        # Python dependencies
├── StudyForge.spec         # PyInstaller build specification
├── build.bat               # One-click Windows build script
├── README.md               # This file
├── database.py             # SQLite database manager
├── srs_engine.py           # SM-2 spaced repetition algorithm
├── claude_client.py        # Claude API integration
├── assets/                 # Icons (optional icon.ico for .exe)
├── ui/
│   ├── app.py              # Main application window
│   ├── dashboard.py        # Dashboard / home tab
│   ├── pomodoro.py         # Pomodoro timer tab
│   ├── flashcards.py       # Flashcard review + creation tab
│   ├── notes.py            # Notes manager with rich editing and focus mode
│   ├── quiz.py             # Active recall quiz tab
│   ├── essays.py           # Essay writing with AI grading
│   ├── hypotheticals.py    # Legal hypothetical scenarios
│   ├── participation.py    # Class participation questions
│   └── styles.py           # Shared theme + styling constants
└── data/
    └── studyforge.db       # Auto-created SQLite database
```

---

## 🧠 How the SM-2 Algorithm Works
Each flashcard tracks: `easiness_factor`, `interval`, `repetitions`, and `next_review`.
After each review, you rate yourself 0–5:
- **0–2**: Card resets (you forgot it)
- **3**: Correct but hard — short interval
- **4**: Correct — normal interval
- **5**: Easy — longer interval

The formula adjusts the easiness factor and computes the next review date, ensuring you see difficult cards more often and easy cards less frequently.

---

## 💡 Tips
- **Import notes first**, then use "AI Generate Cards" to auto-create flashcards.
- **Review due cards daily** — consistency beats cramming.
- **Use the Pomodoro timer** during review sessions for focused study blocks.
- The **Quiz** tab generates fresh questions each time from your notes — great for exam prep.
