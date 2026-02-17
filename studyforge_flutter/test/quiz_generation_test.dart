import 'package:flutter_test/flutter_test.dart';
import 'package:studyforge_flutter/core/models.dart';
import 'package:studyforge_flutter/core/quiz_generation.dart';

void main() {
  Note note(int id, String title) => Note(
        id: id,
        title: title,
        content: 'content-$id',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

  group('quiz_generation helpers', () {
    test('pickQuizNotes returns single selected note in single mode', () {
      final all = [note(1, 'A'), note(2, 'B')];
      final picked = pickQuizNotes(
        allNotes: all,
        interleaved: false,
        selectedNoteId: 2,
        selectedNoteIds: <int>{},
      );
      expect(picked.map((n) => n.id).toList(), [2]);
    });

    test('pickQuizNotes returns selected notes in interleaved mode', () {
      final all = [note(1, 'A'), note(2, 'B'), note(3, 'C')];
      final picked = pickQuizNotes(
        allNotes: all,
        interleaved: true,
        selectedNoteId: 1,
        selectedNoteIds: {1, 3},
      );
      expect(picked.map((n) => n.id).toList(), [1, 3]);
    });

    test('buildQuizPrompt includes mode and note content', () {
      final prompt = buildQuizPrompt(
        notes: [note(1, 'Contracts')],
        userInstruction: 'Focus on remedies',
        interleaved: false,
        questionCount: 5,
      );
      expect(prompt, contains('Mode: single-topic'));
      expect(prompt, contains('Contracts'));
      expect(prompt, contains('Focus on remedies'));
    });
  });
}
