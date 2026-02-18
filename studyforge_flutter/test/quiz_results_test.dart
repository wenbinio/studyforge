import 'package:flutter_test/flutter_test.dart';
import 'package:studyforge_flutter/core/models.dart';
import 'package:studyforge_flutter/core/quiz_results.dart';

void main() {
  Note note(String title) => Note(
        id: 1,
        title: title,
        content: 'content',
        createdAt: DateTime.now(),
        updatedAt: DateTime.now(),
      );

  test('buildInterleavedTopicBreakdown counts case-insensitive title mentions', () {
    final breakdown = buildInterleavedTopicBreakdown(
      quizOutput: 'Contracts question. contracts issue. Torts question.',
      selectedNotes: [note('Contracts'), note('Torts')],
    );
    expect(breakdown['Contracts'], 2);
    expect(breakdown['Torts'], 1);
  });
}
