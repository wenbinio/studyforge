"""
database.py — SQLite database manager for StudyForge.
"""

import sqlite3
import os
from datetime import datetime, date

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
DB_PATH = os.path.join(DB_DIR, "studyforge.db")


def get_connection():
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn


def init_db():
    conn = get_connection()
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
    conn.commit()
    conn.close()


# ── Notes ─────────────────────────────────────────────────────────

def add_note(title, content, tags="", source_file=""):
    conn = get_connection()
    now = datetime.now().isoformat()
    c = conn.execute(
        "INSERT INTO notes (title, content, tags, source_file, created_at, updated_at) VALUES (?,?,?,?,?,?)",
        (title, content, tags, source_file, now, now))
    nid = c.lastrowid
    conn.commit(); conn.close()
    return nid

def get_all_notes():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM notes ORDER BY updated_at DESC").fetchall()
    conn.close(); return [dict(r) for r in rows]

def get_note(note_id):
    conn = get_connection()
    row = conn.execute("SELECT * FROM notes WHERE id=?", (note_id,)).fetchone()
    conn.close(); return dict(row) if row else None

def update_note(note_id, title=None, content=None, tags=None):
    conn = get_connection()
    note = get_note(note_id)
    if not note: conn.close(); return
    conn.execute("UPDATE notes SET title=?, content=?, tags=?, updated_at=? WHERE id=?",
        (title or note["title"], content if content is not None else note["content"],
         tags if tags is not None else note["tags"], datetime.now().isoformat(), note_id))
    conn.commit(); conn.close()

def delete_note(note_id):
    conn = get_connection()
    conn.execute("DELETE FROM notes WHERE id=?", (note_id,))
    conn.commit(); conn.close()

def search_notes(query):
    conn = get_connection()
    rows = conn.execute(
        "SELECT * FROM notes WHERE title LIKE ? OR content LIKE ? OR tags LIKE ? ORDER BY updated_at DESC",
        (f"%{query}%", f"%{query}%", f"%{query}%")).fetchall()
    conn.close(); return [dict(r) for r in rows]


# ── Flashcards ────────────────────────────────────────────────────

def add_flashcard(front, back, note_id=None, tags=""):
    conn = get_connection()
    now = datetime.now().isoformat()
    today = date.today().isoformat()
    c = conn.execute(
        "INSERT INTO flashcards (note_id,front,back,tags,next_review,created_at) VALUES (?,?,?,?,?,?)",
        (note_id, front, back, tags, today, now))
    cid = c.lastrowid
    conn.commit(); conn.close()
    increment_daily_stat("cards_added")
    return cid

def get_due_cards(limit=None):
    conn = get_connection()
    today = date.today().isoformat()
    q = "SELECT * FROM flashcards WHERE next_review<=? ORDER BY next_review ASC"
    if limit: q += f" LIMIT {limit}"
    rows = conn.execute(q, (today,)).fetchall()
    conn.close(); return [dict(r) for r in rows]

def get_all_flashcards():
    conn = get_connection()
    rows = conn.execute("SELECT * FROM flashcards ORDER BY created_at DESC").fetchall()
    conn.close(); return [dict(r) for r in rows]

def get_flashcards_for_note(note_id):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM flashcards WHERE note_id=? ORDER BY created_at DESC", (note_id,)).fetchall()
    conn.close(); return [dict(r) for r in rows]

def update_flashcard_srs(card_id, easiness_factor, interval, repetitions, next_review):
    conn = get_connection()
    conn.execute("UPDATE flashcards SET easiness_factor=?,interval=?,repetitions=?,next_review=? WHERE id=?",
        (easiness_factor, interval, repetitions, next_review, card_id))
    conn.commit(); conn.close()

def log_review(card_id, rating):
    conn = get_connection()
    conn.execute("INSERT INTO review_log (card_id,rating,reviewed_at) VALUES (?,?,?)",
        (card_id, rating, datetime.now().isoformat()))
    conn.commit(); conn.close()
    increment_daily_stat("cards_reviewed")

def delete_flashcard(card_id):
    conn = get_connection()
    conn.execute("DELETE FROM flashcards WHERE id=?", (card_id,))
    conn.commit(); conn.close()


# ── Pomodoro ──────────────────────────────────────────────────────

def log_pomodoro(session_type, duration_minutes, started_at, finished_at, completed=True):
    conn = get_connection()
    conn.execute(
        "INSERT INTO pomodoro_sessions (session_type,duration_minutes,completed,started_at,finished_at) VALUES (?,?,?,?,?)",
        (session_type, duration_minutes, int(completed), started_at, finished_at))
    conn.commit(); conn.close()
    if session_type == "work" and completed:
        increment_daily_stat("pomodoro_sessions")
        increment_daily_stat("study_minutes", duration_minutes)


# ── Daily Stats ───────────────────────────────────────────────────

def get_today_stats():
    conn = get_connection()
    today = date.today().isoformat()
    row = conn.execute("SELECT * FROM daily_stats WHERE date=?", (today,)).fetchone()
    conn.close()
    if row: return dict(row)
    return {"date": today, "cards_reviewed": 0, "cards_added": 0,
            "pomodoro_sessions": 0, "study_minutes": 0, "quiz_questions_answered": 0}

def increment_daily_stat(field, amount=1):
    conn = get_connection()
    today = date.today().isoformat()
    conn.execute(f"""INSERT INTO daily_stats (date, {field}) VALUES (?, ?)
        ON CONFLICT(date) DO UPDATE SET {field} = {field} + ?""", (today, amount, amount))
    conn.commit(); conn.close()

def get_stats_range(days=7):
    conn = get_connection()
    rows = conn.execute("SELECT * FROM daily_stats ORDER BY date DESC LIMIT ?", (days,)).fetchall()
    conn.close(); return [dict(r) for r in rows]

def get_streak():
    conn = get_connection()
    rows = conn.execute("SELECT date FROM daily_stats WHERE cards_reviewed>0 ORDER BY date DESC").fetchall()
    conn.close()
    if not rows: return 0
    streak = 0; expected = date.today()
    for row in rows:
        d = date.fromisoformat(row["date"])
        if d == expected: streak += 1; expected = date.fromordinal(expected.toordinal()-1)
        elif d < expected: break
    return streak

def get_total_cards():
    conn = get_connection()
    row = conn.execute("SELECT COUNT(*) as cnt FROM flashcards").fetchone()
    conn.close(); return row["cnt"]
