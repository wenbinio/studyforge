import 'dart:math';

import 'models.dart';

int interleavedTopicCount(List<Flashcard> cards) {
  return cards.map((c) => c.noteId).toSet().length;
}

List<Flashcard> buildReviewQueue(
  List<Flashcard> cards, {
  required bool interleaved,
  Random? random,
}) {
  final queue = List<Flashcard>.from(cards);
  if (interleaved) {
    queue.shuffle(random ?? Random());
  }
  return queue;
}
