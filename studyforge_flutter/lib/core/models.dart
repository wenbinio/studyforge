class AppConfig {
  const AppConfig({
    this.aiProvider = 'anthropic',
    this.apiKey = '',
    this.model = 'claude-sonnet-4-5-20250929',
    this.pomodoroWorkMinutes = 25,
    this.pomodoroShortBreak = 5,
    this.pomodoroLongBreak = 15,
    this.pomodoroSessionsBeforeLongBreak = 4,
    this.dailyNewCardsLimit = 20,
    this.theme = 'dark',
  });

  final String aiProvider;
  final String apiKey;
  final String model;
  final int pomodoroWorkMinutes;
  final int pomodoroShortBreak;
  final int pomodoroLongBreak;
  final int pomodoroSessionsBeforeLongBreak;
  final int dailyNewCardsLimit;
  final String theme;

  AppConfig copyWith({
    String? aiProvider,
    String? apiKey,
    String? model,
    int? pomodoroWorkMinutes,
    int? pomodoroShortBreak,
    int? pomodoroLongBreak,
    int? pomodoroSessionsBeforeLongBreak,
    int? dailyNewCardsLimit,
    String? theme,
  }) {
    return AppConfig(
      aiProvider: aiProvider ?? this.aiProvider,
      apiKey: apiKey ?? this.apiKey,
      model: model ?? this.model,
      pomodoroWorkMinutes: pomodoroWorkMinutes ?? this.pomodoroWorkMinutes,
      pomodoroShortBreak: pomodoroShortBreak ?? this.pomodoroShortBreak,
      pomodoroLongBreak: pomodoroLongBreak ?? this.pomodoroLongBreak,
      pomodoroSessionsBeforeLongBreak:
          pomodoroSessionsBeforeLongBreak ?? this.pomodoroSessionsBeforeLongBreak,
      dailyNewCardsLimit: dailyNewCardsLimit ?? this.dailyNewCardsLimit,
      theme: theme ?? this.theme,
    );
  }

  Map<String, Object> toJson() {
    return {
      'ai_provider': aiProvider,
      'api_key': apiKey,
      'model': model,
      'pomodoro_work_minutes': pomodoroWorkMinutes,
      'pomodoro_short_break': pomodoroShortBreak,
      'pomodoro_long_break': pomodoroLongBreak,
      'pomodoro_sessions_before_long_break': pomodoroSessionsBeforeLongBreak,
      'daily_new_cards_limit': dailyNewCardsLimit,
      'theme': theme,
    };
  }

  factory AppConfig.fromJson(Map<String, Object?> json) {
    return AppConfig(
      aiProvider: json['ai_provider'] as String? ?? 'anthropic',
      apiKey: json['api_key'] as String? ?? '',
      model: json['model'] as String? ?? 'claude-sonnet-4-5-20250929',
      pomodoroWorkMinutes: json['pomodoro_work_minutes'] as int? ?? 25,
      pomodoroShortBreak: json['pomodoro_short_break'] as int? ?? 5,
      pomodoroLongBreak: json['pomodoro_long_break'] as int? ?? 15,
      pomodoroSessionsBeforeLongBreak:
          json['pomodoro_sessions_before_long_break'] as int? ?? 4,
      dailyNewCardsLimit: json['daily_new_cards_limit'] as int? ?? 20,
      theme: json['theme'] as String? ?? 'dark',
    );
  }
}

class Note {
  const Note({
    required this.id,
    required this.title,
    required this.content,
    this.tags = '',
    this.sourceFile,
    required this.createdAt,
    required this.updatedAt,
  });

  final int? id;
  final String title;
  final String content;
  final String tags;
  final String? sourceFile;
  final DateTime createdAt;
  final DateTime updatedAt;

  Map<String, Object?> toMap() {
    return {
      'id': id,
      'title': title,
      'content': content,
      'tags': tags,
      'source_file': sourceFile,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }

  factory Note.fromMap(Map<String, Object?> map) {
    return Note(
      id: map['id'] as int?,
      title: map['title'] as String,
      content: map['content'] as String,
      tags: map['tags'] as String? ?? '',
      sourceFile: map['source_file'] as String?,
      createdAt: DateTime.parse(map['created_at'] as String),
      updatedAt: DateTime.parse(map['updated_at'] as String),
    );
  }
}

class Flashcard {
  const Flashcard({
    required this.id,
    required this.noteId,
    required this.front,
    required this.back,
    this.tags = '',
    this.easinessFactor = 2.5,
    this.interval = 0,
    this.repetitions = 0,
    required this.nextReview,
    required this.createdAt,
  });

  final int? id;
  final int? noteId;
  final String front;
  final String back;
  final String tags;
  final double easinessFactor;
  final int interval;
  final int repetitions;
  final DateTime nextReview;
  final DateTime createdAt;

  bool get isDue => !nextReview.isAfter(DateTime.now());

  Flashcard copyWith({
    int? id,
    int? noteId,
    String? front,
    String? back,
    String? tags,
    double? easinessFactor,
    int? interval,
    int? repetitions,
    DateTime? nextReview,
    DateTime? createdAt,
  }) {
    return Flashcard(
      id: id ?? this.id,
      noteId: noteId ?? this.noteId,
      front: front ?? this.front,
      back: back ?? this.back,
      tags: tags ?? this.tags,
      easinessFactor: easinessFactor ?? this.easinessFactor,
      interval: interval ?? this.interval,
      repetitions: repetitions ?? this.repetitions,
      nextReview: nextReview ?? this.nextReview,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  Map<String, Object?> toMap() {
    return {
      'id': id,
      'note_id': noteId,
      'front': front,
      'back': back,
      'tags': tags,
      'easiness_factor': easinessFactor,
      'interval': interval,
      'repetitions': repetitions,
      'next_review': nextReview.toIso8601String(),
      'created_at': createdAt.toIso8601String(),
    };
  }

  factory Flashcard.fromMap(Map<String, Object?> map) {
    return Flashcard(
      id: map['id'] as int?,
      noteId: map['note_id'] as int?,
      front: map['front'] as String,
      back: map['back'] as String,
      tags: map['tags'] as String? ?? '',
      easinessFactor: (map['easiness_factor'] as num?)?.toDouble() ?? 2.5,
      interval: map['interval'] as int? ?? 0,
      repetitions: map['repetitions'] as int? ?? 0,
      nextReview: DateTime.parse(map['next_review'] as String),
      createdAt: DateTime.parse(map['created_at'] as String),
    );
  }
}

class ReviewLog {
  const ReviewLog({
    this.id,
    required this.cardId,
    required this.rating,
    required this.reviewedAt,
  });

  final int? id;
  final int cardId;
  final int rating;
  final DateTime reviewedAt;

  Map<String, Object?> toMap() {
    return {
      'id': id,
      'card_id': cardId,
      'rating': rating,
      'reviewed_at': reviewedAt.toIso8601String(),
    };
  }
}

class PomodoroSession {
  const PomodoroSession({
    this.id,
    required this.sessionType,
    required this.durationMinutes,
    required this.completed,
    required this.startedAt,
    this.finishedAt,
  });

  final int? id;
  final String sessionType;
  final int durationMinutes;
  final bool completed;
  final DateTime startedAt;
  final DateTime? finishedAt;

  Map<String, Object?> toMap() {
    return {
      'id': id,
      'session_type': sessionType,
      'duration_minutes': durationMinutes,
      'completed': completed ? 1 : 0,
      'started_at': startedAt.toIso8601String(),
      'finished_at': finishedAt?.toIso8601String(),
    };
  }
}

class DailyStats {
  const DailyStats({
    required this.date,
    this.cardsReviewed = 0,
    this.cardsAdded = 0,
    this.pomodoroSessions = 0,
    this.studyMinutes = 0,
    this.quizQuestionsAnswered = 0,
  });

  final DateTime date;
  final int cardsReviewed;
  final int cardsAdded;
  final int pomodoroSessions;
  final int studyMinutes;
  final int quizQuestionsAnswered;

  Map<String, Object?> toMap() {
    return {
      'date': _dateOnly(date),
      'cards_reviewed': cardsReviewed,
      'cards_added': cardsAdded,
      'pomodoro_sessions': pomodoroSessions,
      'study_minutes': studyMinutes,
      'quiz_questions_answered': quizQuestionsAnswered,
    };
  }

  factory DailyStats.fromMap(Map<String, Object?> map) {
    return DailyStats(
      date: DateTime.parse(map['date'] as String),
      cardsReviewed: map['cards_reviewed'] as int? ?? 0,
      cardsAdded: map['cards_added'] as int? ?? 0,
      pomodoroSessions: map['pomodoro_sessions'] as int? ?? 0,
      studyMinutes: map['study_minutes'] as int? ?? 0,
      quizQuestionsAnswered: map['quiz_questions_answered'] as int? ?? 0,
    );
  }

  static String _dateOnly(DateTime d) =>
      '${d.year.toString().padLeft(4, '0')}-${d.month.toString().padLeft(2, '0')}-${d.day.toString().padLeft(2, '0')}';
}

class Rubric {
  const Rubric({
    this.id,
    required this.name,
    required this.content,
    this.sourceFile,
    required this.createdAt,
  });

  final int? id;
  final String name;
  final String content;
  final String? sourceFile;
  final DateTime createdAt;

  Map<String, Object?> toMap() {
    return {
      'id': id,
      'name': name,
      'content': content,
      'source_file': sourceFile,
      'created_at': createdAt.toIso8601String(),
    };
  }

  factory Rubric.fromMap(Map<String, Object?> map) {
    return Rubric(
      id: map['id'] as int?,
      name: map['name'] as String,
      content: map['content'] as String,
      sourceFile: map['source_file'] as String?,
      createdAt: DateTime.parse(map['created_at'] as String),
    );
  }
}

class Essay {
  const Essay({
    this.id,
    this.noteId,
    required this.title,
    required this.prompt,
    required this.content,
    this.rubricId,
    this.grade,
    this.feedback,
    required this.createdAt,
    required this.updatedAt,
  });

  final int? id;
  final int? noteId;
  final String title;
  final String prompt;
  final String content;
  final int? rubricId;
  final String? grade;
  final String? feedback;
  final DateTime createdAt;
  final DateTime updatedAt;

  Map<String, Object?> toMap() {
    return {
      'id': id,
      'note_id': noteId,
      'title': title,
      'prompt': prompt,
      'content': content,
      'rubric_id': rubricId,
      'grade': grade,
      'feedback': feedback,
      'created_at': createdAt.toIso8601String(),
      'updated_at': updatedAt.toIso8601String(),
    };
  }
}

class Hypothetical {
  const Hypothetical({
    this.id,
    this.noteId,
    required this.title,
    required this.scenario,
    this.response,
    this.grade,
    this.feedback,
    required this.createdAt,
  });

  final int? id;
  final int? noteId;
  final String title;
  final String scenario;
  final String? response;
  final String? grade;
  final String? feedback;
  final DateTime createdAt;

  Map<String, Object?> toMap() {
    return {
      'id': id,
      'note_id': noteId,
      'title': title,
      'scenario': scenario,
      'response': response,
      'grade': grade,
      'feedback': feedback,
      'created_at': createdAt.toIso8601String(),
    };
  }
}

class ParticipationQuestion {
  const ParticipationQuestion({
    this.id,
    this.noteId,
    required this.question,
    required this.category,
    this.answer,
    this.notes,
    required this.createdAt,
  });

  final int? id;
  final int? noteId;
  final String question;
  final String category;
  final String? answer;
  final String? notes;
  final DateTime createdAt;

  Map<String, Object?> toMap() {
    return {
      'id': id,
      'note_id': noteId,
      'question': question,
      'category': category,
      'answer': answer,
      'notes': notes,
      'created_at': createdAt.toIso8601String(),
    };
  }
}
