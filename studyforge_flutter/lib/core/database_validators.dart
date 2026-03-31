const validDailyStatFields = {
  'cards_reviewed',
  'cards_added',
  'pomodoro_sessions',
  'study_minutes',
  'quiz_questions_answered',
};

bool isValidDailyStatField(String field) {
  return validDailyStatFields.contains(field);
}
