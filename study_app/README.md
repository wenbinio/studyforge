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
| **Notes Manager** | Import `.txt`, `.md`, `.pdf`, `.docx` lecture notes; tag and search |
| **Claude AI Engine** | Auto-generates flashcards, quiz questions, and explanations from notes |
| **Dashboard** | Daily stats, streak tracking, cards due, upcoming reviews |

---

## 🛠️ Setup Instructions (Step by Step)

### Prerequisites
- **Windows 10/11**
- **Python 3.10+** — Download from [python.org](https://www.python.org/downloads/)
  - ✅ During install, CHECK **"Add Python to PATH"**

### Step 1: Download the Project
Place the entire `study_app` folder anywhere on your PC (e.g., `C:\Users\YourName\study_app`).

### Step 2: Open Terminal
Press `Win + R`, type `cmd`, press Enter. Then navigate to the project:
```
cd C:\Users\YourName\study_app
```

### Step 3: Create a Virtual Environment (recommended)
```
python -m venv venv
venv\Scripts\activate
```

### Step 4: Install Dependencies
```
pip install -r requirements.txt
```

### Step 5: Configure Your Claude API Key
1. Go to [console.anthropic.com](https://console.anthropic.com/) and create an API key.
2. Open the file `config.json` in the project root.
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

### Step 6: Run the App
```
python main.py
```

### (Option A) Step 7: Build a Standalone .exe
The easiest way — just double-click the build script:
```
build.bat
```
This installs PyInstaller, bundles everything, and produces a single `dist\StudyForge.exe`.

Or run it manually:
```
pip install pyinstaller
pyinstaller StudyForge.spec --noconfirm
```

#### After building:
1. **Double-click** `dist\StudyForge.exe` — it launches with no console window.
2. On first run it creates `%APPDATA%\StudyForge\config.json` — click **📁 Open Config** in the sidebar to find it.
3. Edit `config.json` to add your Claude API key, then restart.
4. Your database and study data persist at `%APPDATA%\StudyForge\data\`.
5. You can move `StudyForge.exe` anywhere — it's fully self-contained.

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
│   ├── notes.py            # Notes manager tab
│   ├── quiz.py             # Active recall quiz tab
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
