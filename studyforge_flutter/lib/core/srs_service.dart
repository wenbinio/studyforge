import 'models.dart';

class SrsService {
  Flashcard applyReview({required Flashcard card, required int rating}) {
    final clampedRating = rating.clamp(0, 5);
    double ef = card.easinessFactor +
        (0.1 - (5 - clampedRating) * (0.08 + (5 - clampedRating) * 0.02));
    if (ef < 1.3) {
      ef = 1.3;
    }

    int reps = card.repetitions;
    int interval = card.interval;

    if (clampedRating < 3) {
      reps = 0;
      interval = 0;
    } else {
      reps += 1;
      if (reps == 1) {
        interval = 1;
      } else if (reps == 2) {
        interval = 6;
      } else {
        interval = (interval * ef).round();
      }
    }

    final now = DateTime.now();
    final nextReview = now.add(Duration(days: interval > 0 ? interval : 1));

    return card.copyWith(
      easinessFactor: ef,
      repetitions: reps,
      interval: interval,
      nextReview: nextReview,
    );
  }
}
