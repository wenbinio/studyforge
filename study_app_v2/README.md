# 🎓 StudyForge — All-in-One Study Companion

Pomodoro Timer · Spaced Repetition (SM-2) · Active Recall · AI-Powered Study

---

## 🚀 Getting Started

### Option A: Download Pre-Built App (No Python Required)
1. Go to the [Releases](../../releases) page
2. Download **StudyForge_v2.exe**
3. Double-click to run — the setup wizard will guide you

> The `.exe` is fully self-contained. No Python or other software needed.

### Option B: One-Click Launcher
**Double-click `StudyForge.bat`** — that's it.

On first run it will:
1. Detect your Python installation
2. **If Python isn't found**, offer to download a portable copy automatically (no install required)
3. Create a virtual environment
4. Install all dependencies
5. Launch the app with a welcome wizard

The welcome wizard lets you paste your Claude API key (optional — you can skip and add it later in **Settings**).

### Option C: Build the .exe Yourself
Double-click the build script (requires Python):
```
build.bat
```
This installs PyInstaller, bundles everything, and produces a single `dist\StudyForge.exe`.

---

## 📖 Features

| Module | Description |
|---|---|
| **Dashboard** | Daily stats, streak, cards due, 7-day review forecast |
| **Pomodoro Timer** | Configurable work/break cycles, session dots, stats |
| **Flashcards** | SM-2 spaced repetition review, manual creation, AI bulk generation |
| **Notes Manager** | Import `.txt` `.md` `.pdf` `.docx`; tag, search, edit with rich markdown formatting, preview, and focus mode |
| **Active Recall Quiz** | AI-generated MCQs with difficulty, explanations, scoring |
| **Essays** | Essay writing with rubric upload and AI grading |
| **Hypotheticals** | AI-generated legal hypothetical scenarios from your notes |
| **Class Participation** | AI-generated discussion questions for class preparation |
| **Settings** | In-app API key entry, connection testing, all preferences |

---

## 🤖 Claude AI Features

Requires an API key from [console.anthropic.com](https://console.anthropic.com):

- **Generate Flashcards** — creates Q&A cards from any note
- **Generate Quizzes** — MCQ questions with explanations
- **Summarize Notes** — structured summaries with exam topics
- **Ask Questions** — answers grounded in your specific notes
- **Explain Concepts** — tutor-style explanations with analogies

Set up your key in **Settings → Claude AI Integration** inside the app.

---

## 📂 Project Structure
```
StudyForge/
├── StudyForge.bat          ← Double-click to launch (auto-downloads Python if needed)
├── build.bat               ← Build standalone .exe (requires Python)
├── StudyForge.spec         ← PyInstaller build specification
├── main.py                 ← Python entry point
├── config_manager.py       ← Auto-managed config (never edit manually)
├── database.py             ← SQLite database
├── srs_engine.py           ← SM-2 algorithm
├── claude_client.py        ← Claude API integration
├── requirements.txt        ← Python dependencies
├── ui/
│   ├── app.py              ← Main window + sidebar
│   ├── setup_wizard.py     ← First-run welcome screen
│   ├── dashboard.py        ← Dashboard tab
│   ├── pomodoro.py         ← Pomodoro timer tab
│   ├── flashcards.py       ← Flashcard review + creation
│   ├── notes.py            ← Notes manager with rich editing and focus mode
│   ├── quiz.py             ← Active recall quiz tab
│   ├── essays.py           ← Essay writing with AI grading
│   ├── hypotheticals.py    ← Legal hypothetical scenarios
│   ├── participation.py    ← Class participation questions
│   ├── settings.py         ← In-app settings + API key
│   └── styles.py           ← Theme constants
└── data/
    └── studyforge.db       ← Auto-created database
```

---

## 💡 Tips
- **Import notes first**, then AI-generate flashcards from them
- **Review due cards daily** — consistency beats cramming
- The app works fully offline for Pomodoro + manual flashcards
- AI features only require the API key (configured in-app)
