import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';

import 'database_validators.dart';
import 'models.dart';

class DatabaseService {
  Database? _db;

  Future<Database> get database async {
    if (_db != null) {
      return _db!;
    }
    _db = await _open();
    return _db!;
  }

  Future<Database> _open() async {
    final dir = await getApplicationDocumentsDirectory();
    final path = p.join(dir.path, 'studyforge.db');
    return openDatabase(path, version: 1, onCreate: _onCreate);
  }

  Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
CREATE TABLE notes (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  title TEXT NOT NULL,
  content TEXT NOT NULL,
  tags TEXT,
  source_file TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL
);
''');

    await db.execute('''
CREATE TABLE flashcards (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  note_id INTEGER,
  front TEXT NOT NULL,
  back TEXT NOT NULL,
  tags TEXT,
  easiness_factor REAL NOT NULL DEFAULT 2.5,
  interval INTEGER NOT NULL DEFAULT 0,
  repetitions INTEGER NOT NULL DEFAULT 0,
  next_review TEXT NOT NULL,
  created_at TEXT NOT NULL,
  FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE
);
''');

    await db.execute('''
CREATE TABLE review_log (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  card_id INTEGER NOT NULL,
  rating INTEGER NOT NULL,
  reviewed_at TEXT NOT NULL,
  FOREIGN KEY(card_id) REFERENCES flashcards(id) ON DELETE CASCADE
);
''');

    await db.execute('''
CREATE TABLE pomodoro_sessions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  session_type TEXT NOT NULL,
  duration_minutes INTEGER NOT NULL,
  completed INTEGER NOT NULL DEFAULT 1,
  started_at TEXT NOT NULL,
  finished_at TEXT
);
''');

    await db.execute('''
CREATE TABLE daily_stats (
  date TEXT PRIMARY KEY,
  cards_reviewed INTEGER NOT NULL DEFAULT 0,
  cards_added INTEGER NOT NULL DEFAULT 0,
  pomodoro_sessions INTEGER NOT NULL DEFAULT 0,
  study_minutes INTEGER NOT NULL DEFAULT 0,
  quiz_questions_answered INTEGER NOT NULL DEFAULT 0
);
''');

    await db.execute('''
CREATE TABLE hypotheticals (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  note_id INTEGER,
  title TEXT NOT NULL,
  scenario TEXT NOT NULL,
  response TEXT,
  grade TEXT,
  feedback TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE
);
''');

    await db.execute('''
CREATE TABLE rubrics (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  name TEXT NOT NULL,
  content TEXT NOT NULL,
  source_file TEXT,
  created_at TEXT NOT NULL
);
''');

    await db.execute('''
CREATE TABLE essays (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  note_id INTEGER,
  title TEXT NOT NULL,
  prompt TEXT NOT NULL,
  content TEXT NOT NULL,
  rubric_id INTEGER,
  grade TEXT,
  feedback TEXT,
  created_at TEXT NOT NULL,
  updated_at TEXT NOT NULL,
  FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE,
  FOREIGN KEY(rubric_id) REFERENCES rubrics(id) ON DELETE SET NULL
);
''');

    await db.execute('''
CREATE TABLE participation_questions (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  note_id INTEGER,
  question TEXT NOT NULL,
  category TEXT NOT NULL,
  answer TEXT,
  notes TEXT,
  created_at TEXT NOT NULL,
  FOREIGN KEY(note_id) REFERENCES notes(id) ON DELETE CASCADE
);
''');
  }

  Future<int> addNote(Note note) async {
    final db = await database;
    return db.insert('notes', note.toMap()..remove('id'));
  }

  Future<List<Note>> getNotes() async {
    final db = await database;
    final rows = await db.query('notes', orderBy: 'updated_at DESC');
    return rows.map(Note.fromMap).toList();
  }

  Future<int> addFlashcard(Flashcard card) async {
    final db = await database;
    return db.insert('flashcards', card.toMap()..remove('id'));
  }

  Future<List<Flashcard>> getFlashcards({bool dueOnly = false}) async {
    final db = await database;
    final now = DateTime.now().toIso8601String();
    final rows = await db.query(
      'flashcards',
      where: dueOnly ? 'next_review <= ?' : null,
      whereArgs: dueOnly ? [now] : null,
      orderBy: 'next_review ASC',
    );
    return rows.map(Flashcard.fromMap).toList();
  }

  Future<void> updateFlashcard(Flashcard card) async {
    final db = await database;
    await db.update(
      'flashcards',
      card.toMap()..remove('id'),
      where: 'id = ?',
      whereArgs: [card.id],
    );
  }

  Future<void> addReviewLog(ReviewLog log) async {
    final db = await database;
    await db.insert('review_log', log.toMap()..remove('id'));
  }

  Future<void> logPomodoro(PomodoroSession session) async {
    final db = await database;
    await db.insert('pomodoro_sessions', session.toMap()..remove('id'));
  }

  Future<void> incrementDailyStat(String field, int amount) async {
    if (!isValidDailyStatField(field)) {
      throw Exception('Invalid stat field: $field');
    }

    final db = await database;
    final today = _dateOnly(DateTime.now());
    await db.insert('daily_stats', {'date': today},
        conflictAlgorithm: ConflictAlgorithm.ignore);
    await db.rawUpdate(
      'UPDATE daily_stats SET $field = $field + ? WHERE date = ?',
      [amount, today],
    );
  }

  Future<DailyStats?> todayStats() async {
    final db = await database;
    final today = _dateOnly(DateTime.now());
    final rows = await db.query('daily_stats', where: 'date = ?', whereArgs: [today]);
    if (rows.isEmpty) {
      return null;
    }
    return DailyStats.fromMap(rows.first);
  }

  Future<int> currentStreak() async {
    final db = await database;
    final rows = await db.query('daily_stats', orderBy: 'date DESC');
    final byDate = <String, Map<String, Object?>>{};
    for (final row in rows) {
      byDate[row['date'] as String] = row;
    }

    var streak = 0;
    var cursor = DateTime.now();

    while (true) {
      final dateKey = _dateOnly(cursor);
      final row = byDate[dateKey];
      if (row == null) {
        break;
      }
      final reviewed = row['cards_reviewed'] as int? ?? 0;
      if (reviewed <= 0) {
        break;
      }
      streak += 1;
      cursor = cursor.subtract(const Duration(days: 1));
    }

    return streak;
  }

  Future<int> dueCardCount() async {
    final db = await database;
    final now = DateTime.now().toIso8601String();
    final rows = await db.rawQuery(
      'SELECT COUNT(*) AS count FROM flashcards WHERE next_review <= ?',
      [now],
    );
    return rows.first['count'] as int? ?? 0;
  }

  Future<int> addRubric(Rubric rubric) async {
    final db = await database;
    return db.insert('rubrics', rubric.toMap()..remove('id'));
  }

  Future<List<Rubric>> getRubrics() async {
    final db = await database;
    final rows = await db.query('rubrics', orderBy: 'created_at DESC');
    return rows.map(Rubric.fromMap).toList();
  }

  Future<Rubric?> getRubric(int id) async {
    final db = await database;
    final rows = await db.query('rubrics', where: 'id = ?', whereArgs: [id], limit: 1);
    if (rows.isEmpty) {
      return null;
    }
    return Rubric.fromMap(rows.first);
  }

  String _dateOnly(DateTime d) =>
      '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
}
