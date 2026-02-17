import 'package:flutter_test/flutter_test.dart';
import 'package:studyforge_flutter/core/models.dart';
import 'package:studyforge_flutter/core/srs_service.dart';

void main() {
  group('SrsService', () {
    final srs = SrsService();

    test('resets repetitions for failing review', () {
      final card = Flashcard(
        id: 1,
        noteId: 1,
        front: 'Q',
        back: 'A',
        easinessFactor: 2.5,
        interval: 6,
        repetitions: 3,
        nextReview: DateTime.now(),
        createdAt: DateTime.now(),
      );

      final updated = srs.applyReview(card: card, rating: 2);
      expect(updated.repetitions, 0);
      expect(updated.interval, 0);
      expect(updated.easinessFactor, greaterThanOrEqualTo(1.3));
    });

    test('uses 1 then 6 day intervals for first correct reviews', () {
      final start = Flashcard(
        id: 1,
        noteId: 1,
        front: 'Q',
        back: 'A',
        easinessFactor: 2.5,
        interval: 0,
        repetitions: 0,
        nextReview: DateTime.now(),
        createdAt: DateTime.now(),
      );

      final first = srs.applyReview(card: start, rating: 4);
      final second = srs.applyReview(card: first, rating: 4);

      expect(first.interval, 1);
      expect(second.interval, 6);
      expect(second.repetitions, 2);
    });
  });
}
