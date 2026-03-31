import 'dart:math';

import 'package:flutter_test/flutter_test.dart';
import 'package:studyforge_flutter/core/flashcard_review.dart';
import 'package:studyforge_flutter/core/models.dart';

void main() {
  Flashcard card(int id, int? noteId) => Flashcard(
        id: id,
        noteId: noteId,
        front: 'Q$id',
        back: 'A$id',
        nextReview: DateTime.now(),
        createdAt: DateTime.now(),
      );

  group('flashcard_review helpers', () {
    test('interleavedTopicCount counts unique note ids including null topic bucket', () {
      final cards = [card(1, 10), card(2, 10), card(3, 11), card(4, null)];
      expect(interleavedTopicCount(cards), 3);
    });

    test('buildReviewQueue keeps order for normal mode', () {
      final cards = [card(1, 1), card(2, 2), card(3, 3)];
      final queue = buildReviewQueue(cards, interleaved: false);
      expect(queue.map((c) => c.id).toList(), [1, 2, 3]);
    });

    test('buildReviewQueue returns shuffled set in interleaved mode', () {
      final cards = [card(1, 1), card(2, 2), card(3, 3), card(4, 4)];
      final queue = buildReviewQueue(cards, interleaved: true, random: Random(7));
      expect(queue.map((c) => c.id).toSet(), {1, 2, 3, 4});
      expect(queue.length, 4);
    });
  });
}
