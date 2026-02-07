"""
srs_engine.py — SM-2 Spaced Repetition Algorithm for StudyForge.

Implements the SuperMemo 2 algorithm used by Anki.
Rating scale: 0-5
  0 - Complete blackout
  1 - Incorrect; answer remembered upon seeing it
  2 - Incorrect; answer seemed easy to recall
  3 - Correct with serious difficulty
  4 - Correct after hesitation
  5 - Perfect recall
"""

from datetime import date, timedelta
from database import update_flashcard_srs, log_review


def review_card(card: dict, rating: int) -> dict:
    """
    Apply SM-2 algorithm to a flashcard after review.
    
    Args:
        card: dict with keys easiness_factor, interval, repetitions, id
        rating: int 0-5
    
    Returns:
        Updated card dict with new SRS parameters.
    """
    rating = max(0, min(5, rating))

    ef = card["easiness_factor"]
    interval = card["interval"]
    reps = card["repetitions"]

    # Update easiness factor
    ef = ef + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02))
    ef = max(1.3, ef)  # Minimum EF is 1.3

    if rating < 3:
        # Failed — reset and show again today
        reps = 0
        interval = 0
        next_review = date.today().isoformat()
    else:
        # Passed — advance interval
        if reps == 0:
            interval = 1
        elif reps == 1:
            interval = 6
        else:
            interval = round(interval * ef)
        reps += 1
        next_review = (date.today() + timedelta(days=max(interval, 1))).isoformat()

    # Persist to database
    update_flashcard_srs(card["id"], ef, interval, reps, next_review)
    log_review(card["id"], rating)

    return {
        "id": card["id"],
        "easiness_factor": ef,
        "interval": interval,
        "repetitions": reps,
        "next_review": next_review
    }


def get_rating_labels():
    """Return human-readable labels for each rating level."""
    return {
        0: ("Again", "Complete blackout — no recall at all"),
        1: ("Hard", "Wrong, but recognized the answer"),
        2: ("Difficult", "Wrong, but it felt familiar"),
        3: ("Okay", "Correct, but took serious effort"),
        4: ("Good", "Correct after brief hesitation"),
        5: ("Easy", "Instant, perfect recall"),
    }


def forecast_reviews(cards: list, days_ahead: int = 30) -> dict:
    """
    Forecast how many cards are due each day for the next N days.
    Returns dict: {date_str: count}
    """
    forecast = {}
    today = date.today()
    for i in range(days_ahead):
        d = (today + timedelta(days=i)).isoformat()
        forecast[d] = 0

    for card in cards:
        nr = card.get("next_review", "")
        if nr in forecast:
            forecast[nr] += 1
        elif nr and nr < today.isoformat():
            # Overdue cards count as today
            forecast[today.isoformat()] = forecast.get(today.isoformat(), 0) + 1

    return forecast
