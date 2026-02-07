"""
database.py — SQLite database manager for StudyForge.
All connections use context managers to prevent leaks.
"""

import sqlite3
import os
from datetime import datetime, date
from contextlib import contextmanager

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "studyforge.db")

# Whitelist of valid stat fields to prevent SQL injection
VALID_STAT_FIELDS = frozenset({
    "cards_reviewed", "cards_added", "pomodoro_sessions",
    "study_minutes", "quiz_questions_answered"
})


@contextmanager
def get_connection():
    """Context manager for safe database connections."""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db():
    with get_connection() as conn:
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL, content TEXT NOT NULL,
                tags TEXT DEFAULT '', source_file TEXT DEFAULT '',
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS flashcards (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER, front TEXT NOT NULL, back TEXT NOT NULL,
                tags TEXT DEFAULT '', easiness_factor REAL DEFAULT 2.5,
                interval INTEGER DEFAULT 0, repetitions INTEGER DEFAULT 0,
                next_review TEXT NOT NULL, created_at TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE SET NULL
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS review_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                card_id INTEGER NOT NULL, rating INTEGER NOT NULL,
                reviewed_at TEXT NOT NULL,
                FOREIGN KEY (card_id) REFERENCES flashcards(id) ON DELETE CASCADE
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_type TEXT NOT NULL, duration_minutes INTEGER NOT NULL,
                completed INTEGER DEFAULT 1, started_at TEXT NOT NULL, finished_at TEXT NOT NULL
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY, cards_reviewed INTEGER DEFAULT 0,
                cards_added INTEGER DEFAULT 0, pomodoro_sessions INTEGER DEFAULT 0,
                study_minutes INTEGER DEFAULT 0, quiz_questions_answered INTEGER DEFAULT 0
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS hypotheticals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER, title TEXT NOT NULL, scenario TEXT NOT NULL,
                response TEXT DEFAULT '', grade TEXT DEFAULT '',
                feedback TEXT DEFAULT '', created_at TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE SET NULL
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS essays (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER, title TEXT NOT NULL, prompt TEXT NOT NULL,
                content TEXT DEFAULT '', rubric_id INTEGER,
                grade TEXT DEFAULT '', feedback TEXT DEFAULT '',
                created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE SET NULL,
                FOREIGN KEY (rubric_id) REFERENCES rubrics(id) ON DELETE SET NULL
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS rubrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL, content TEXT NOT NULL,
                source_file TEXT DEFAULT '', created_at TEXT NOT NULL
            )""")
        c.execute("""
            CREATE TABLE IF NOT EXISTS participation_questions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                note_id INTEGER, question TEXT NOT NULL,
                category TEXT NOT NULL DEFAULT 'interesting',
                answer TEXT DEFAULT '', notes TEXT DEFAULT '',
                created_at TEXT NOT NULL,
                FOREIGN KEY (note_id) REFERENCES notes(id) ON DELETE SET NULL
            )""")


# ── Notes ─────────────────────────────────────────────────────────

def add_note(title, content, tags="", source_file=""):
    now = datetime.now().isoformat()
    with get_connection() as conn:
        c = conn.execute(
            "INSERT INTO notes (title, content, tags, source_file, created_at, updated_at) VALUES (?,?,?,?,?,?)",
            (title, content, tags, source_file, now, now))
        return c.lastrowid

def get_all_notes():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM notes ORDER BY updated_at DESC").fetchall()
        return [dict(r) for r in rows]

def get_note(note_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
        return dict(row) if row else None

def update_note(note_id, title=None, content=None, tags=None):
    note = get_note(note_id)
    if not note: return
    with get_connection() as conn:
        conn.execute("UPDATE notes SET title=?, content=?, tags=?, updated_at=? WHERE id=?",
            (title if title is not None else note["title"],
             content if content is not None else note["content"],
             tags if tags is not None else note["tags"],
             datetime.now().isoformat(), note_id))

def delete_note(note_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM notes WHERE id=?", (note_id,))

def search_notes(query):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? ORDER BY updated_at DESC",
            (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
        return [dict(r) for r in rows]


# ── Flashcards ────────────────────────────────────────────────────

def add_flashcard(front, back, note_id=None, tags=""):
    now = datetime.now().isoformat()
    today = date.today().isoformat()
    with get_connection() as conn:
        c = conn.execute(
            "INSERT INTO flashcards (note_id,front,back,tags,next_review,created_at) VALUES (?,?,?,?,?,?)",
            (note_id, front, back, tags, today, now))
        cid = c.lastrowid
    increment_daily_stat("cards_added")
    return cid

def get_due_cards(limit=None):
    today = date.today().isoformat()
    with get_connection() as conn:
        if limit:
            rows = conn.execute(
                "SELECT * FROM flashcards WHERE next_review<=? ORDER BY next_review ASC LIMIT ?",
                (today, int(limit))).fetchall()
        else:
            rows = conn.execute(
                "SELECT * FROM flashcards WHERE next_review<=? ORDER BY next_review ASC",
                (today,)).fetchall()
        return [dict(r) for r in rows]

def get_all_flashcards():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM flashcards ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

def get_flashcards_for_note(note_id):
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM flashcards WHERE note_id=? ORDER BY created_at DESC", (note_id,)).fetchall()
        return [dict(r) for r in rows]

def update_flashcard_srs(card_id, easiness_factor, interval, repetitions, next_review):
    with get_connection() as conn:
        conn.execute("UPDATE flashcards SET easiness_factor=?,interval=?,repetitions=?,next_review=? WHERE id=?",
            (easiness_factor, interval, repetitions, next_review, card_id))

def log_review(card_id, rating):
    with get_connection() as conn:
        conn.execute("INSERT INTO review_log (card_id,rating,reviewed_at) VALUES (?,?,?)",
            (card_id, rating, datetime.now().isoformat()))
    increment_daily_stat("cards_reviewed")

def delete_flashcard(card_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM flashcards WHERE id=?", (card_id,))


# ── Pomodoro ──────────────────────────────────────────────────────

def log_pomodoro(session_type, duration_minutes, started_at, finished_at, completed=True):
    with get_connection() as conn:
        conn.execute(
            "INSERT INTO pomodoro_sessions (session_type,duration_minutes,completed,started_at,finished_at) VALUES (?,?,?,?,?)",
            (session_type, duration_minutes, int(completed), started_at, finished_at))
    if session_type == "work" and completed:
        increment_daily_stat("pomodoro_sessions")
        increment_daily_stat("study_minutes", duration_minutes)


# ── Daily Stats ───────────────────────────────────────────────────

def get_today_stats():
    today = date.today().isoformat()
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM daily_stats WHERE date=?", (today,)).fetchone()
        if row: return dict(row)
    return {"date": today, "cards_reviewed": 0, "cards_added": 0,
            "pomodoro_sessions": 0, "study_minutes": 0, "quiz_questions_answered": 0}

def increment_daily_stat(field, amount=1):
    # Validate field against whitelist to prevent SQL injection
    if field not in VALID_STAT_FIELDS:
        raise ValueError(f"Invalid stat field: {field}. Must be one of: {', '.join(sorted(VALID_STAT_FIELDS))}")
    with get_connection() as conn:
        today = date.today().isoformat()
        conn.execute(f"""INSERT INTO daily_stats (date, {field}) VALUES (?, ?)
            ON CONFLICT(date) DO UPDATE SET {field} = {field} + ?""", (today, amount, amount))

def get_stats_range(days=7):
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM daily_stats ORDER BY date DESC LIMIT ?", (days,)).fetchall()
        return [dict(r) for r in rows]

def get_streak():
    with get_connection() as conn:
        rows = conn.execute("SELECT date FROM daily_stats WHERE cards_reviewed>0 ORDER BY date DESC").fetchall()
    if not rows: return 0
    streak = 0; expected = date.today()
    for row in rows:
        d = date.fromisoformat(row["date"])
        if d == expected: streak += 1; expected = date.fromordinal(expected.toordinal()-1)
        elif d < expected: break
    return streak

def get_total_cards():
    with get_connection() as conn:
        row = conn.execute("SELECT COUNT(*) as cnt FROM flashcards").fetchone()
        return row["cnt"]


# ── Hypotheticals ─────────────────────────────────────────────────

def add_hypothetical(title, scenario, note_id=None):
    now = datetime.now().isoformat()
    with get_connection() as conn:
        c = conn.execute(
            "INSERT INTO hypotheticals (note_id,title,scenario,created_at) VALUES (?,?,?,?)",
            (note_id, title, scenario, now))
        return c.lastrowid

def get_all_hypotheticals():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM hypotheticals ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

def get_hypothetical(hyp_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM hypotheticals WHERE id=?", (hyp_id,)).fetchone()
        return dict(row) if row else None

def update_hypothetical(hyp_id, response=None, grade=None, feedback=None):
    hyp = get_hypothetical(hyp_id)
    if not hyp: return
    with get_connection() as conn:
        conn.execute("UPDATE hypotheticals SET response=?, grade=?, feedback=? WHERE id=?",
            (response if response is not None else hyp["response"],
             grade if grade is not None else hyp["grade"],
             feedback if feedback is not None else hyp["feedback"], hyp_id))

def delete_hypothetical(hyp_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM hypotheticals WHERE id=?", (hyp_id,))


# ── Essays ────────────────────────────────────────────────────────

def add_essay(title, prompt, note_id=None, rubric_id=None):
    now = datetime.now().isoformat()
    with get_connection() as conn:
        c = conn.execute(
            "INSERT INTO essays (note_id,title,prompt,rubric_id,created_at,updated_at) VALUES (?,?,?,?,?,?)",
            (note_id, title, prompt, rubric_id, now, now))
        return c.lastrowid

def get_all_essays():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM essays ORDER BY updated_at DESC").fetchall()
        return [dict(r) for r in rows]

def get_essay(essay_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM essays WHERE id=?", (essay_id,)).fetchone()
        return dict(row) if row else None

def update_essay(essay_id, content=None, grade=None, feedback=None):
    essay = get_essay(essay_id)
    if not essay: return
    with get_connection() as conn:
        conn.execute("UPDATE essays SET content=?, grade=?, feedback=?, updated_at=? WHERE id=?",
            (content if content is not None else essay["content"],
             grade if grade is not None else essay["grade"],
             feedback if feedback is not None else essay["feedback"],
             datetime.now().isoformat(), essay_id))

def delete_essay(essay_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM essays WHERE id=?", (essay_id,))


# ── Rubrics ───────────────────────────────────────────────────────

def add_rubric(name, content, source_file=""):
    now = datetime.now().isoformat()
    with get_connection() as conn:
        c = conn.execute(
            "INSERT INTO rubrics (name,content,source_file,created_at) VALUES (?,?,?,?)",
            (name, content, source_file, now))
        return c.lastrowid

def get_all_rubrics():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM rubrics ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

def get_rubric(rubric_id):
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM rubrics WHERE id=?", (rubric_id,)).fetchone()
        return dict(row) if row else None

def delete_rubric(rubric_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM rubrics WHERE id=?", (rubric_id,))


# ── Participation Questions ───────────────────────────────────────

def add_participation_question(question, category="interesting", note_id=None, answer="", notes=""):
    now = datetime.now().isoformat()
    with get_connection() as conn:
        c = conn.execute(
            "INSERT INTO participation_questions (note_id,question,category,answer,notes,created_at) VALUES (?,?,?,?,?,?)",
            (note_id, question, category, answer, notes, now))
        return c.lastrowid

def get_all_participation_questions():
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM participation_questions ORDER BY created_at DESC").fetchall()
        return [dict(r) for r in rows]

def get_participation_questions_by_category(category):
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM participation_questions WHERE category=? ORDER BY created_at DESC",
            (category,)).fetchall()
        return [dict(r) for r in rows]

def update_participation_question(q_id, answer=None, notes=None):
    with get_connection() as conn:
        q = conn.execute("SELECT * FROM participation_questions WHERE id=?", (q_id,)).fetchone()
        if not q: return
        q = dict(q)
        conn.execute("UPDATE participation_questions SET answer=?, notes=? WHERE id=?",
            (answer if answer is not None else q["answer"],
             notes if notes is not None else q["notes"], q_id))

def delete_participation_question(q_id):
    with get_connection() as conn:
        conn.execute("DELETE FROM participation_questions WHERE id=?", (q_id,))
