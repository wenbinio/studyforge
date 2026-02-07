"""
srs_engine.py — SM-2 Spaced Repetition Algorithm.
"""

from datetime import date, timedelta
from database import update_flashcard_srs, log_review


def review_card(card: dict, rating: int) -> dict:
    rating = max(0, min(5, rating))
    ef = card["easiness_factor"]
    interval = card["interval"]
    reps = card["repetitions"]

    ef = ef + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02))
    ef = max(1.3, ef)

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

    update_flashcard_srs(card["id"], ef, interval, reps, next_review)
    log_review(card["id"], rating)
    return {"id": card["id"], "easiness_factor": ef, "interval": interval,
            "repetitions": reps, "next_review": next_review}


def get_rating_labels():
    return {
        0: ("Again", "Complete blackout"), 1: ("Hard", "Wrong, but recognized"),
        2: ("Difficult", "Wrong, felt familiar"), 3: ("Okay", "Correct with effort"),
        4: ("Good", "Correct, brief hesitation"), 5: ("Easy", "Instant recall"),
    }


def forecast_reviews(cards: list, days_ahead: int = 30) -> dict:
    forecast = {}
    today = date.today()
    for i in range(days_ahead):
        forecast[(today + timedelta(days=i)).isoformat()] = 0
    for card in cards:
        nr = card.get("next_review", "")
        if nr in forecast: forecast[nr] += 1
        elif nr and nr < today.isoformat():
            forecast[today.isoformat()] = forecast.get(today.isoformat(), 0) + 1
    return forecast
