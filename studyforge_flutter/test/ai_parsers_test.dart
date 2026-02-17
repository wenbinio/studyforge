import 'package:flutter_test/flutter_test.dart';
import 'package:studyforge_flutter/core/ai_parsers.dart';

void main() {
  group('parseGeneratedFlashcards', () {
    test('parses fenced JSON array', () {
      const raw = '''
```json
[
  {"front":"Q1","back":"A1","tags":"t1"},
  {"front":"Q2","back":"A2"}
]
```
''';
      final cards = parseGeneratedFlashcards(raw);
      expect(cards.length, 2);
      expect(cards.first.front, 'Q1');
      expect(cards.first.back, 'A1');
      expect(cards.first.tags, 't1');
    });

    test('parses object with flashcards key', () {
      const raw = '{"flashcards":[{"front":"Q","back":"A"}]}';
      final cards = parseGeneratedFlashcards(raw);
      expect(cards.length, 1);
      expect(cards.first.front, 'Q');
      expect(cards.first.back, 'A');
    });

    test('filters invalid rows', () {
      const raw = '[{"front":"Q","back":""},{"front":"","back":"A"},{"front":"X","back":"Y"}]';
      final cards = parseGeneratedFlashcards(raw);
      expect(cards.length, 1);
      expect(cards.first.front, 'X');
    });
  });
}
