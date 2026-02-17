String buildEssayGradingPrompt({
  required String prompt,
  required String draft,
  String rubricText = '',
}) {
  final trimmedRubric = rubricText.trim();
  final rubricSection = trimmedRubric.isEmpty ? '' : '\n\nRubric:\n$trimmedRubric';
  return 'Grade this essay and return: score, strengths, weaknesses, and revision plan.\n\n'
      'Prompt:\n$prompt\n\nEssay:\n$draft$rubricSection';
}
