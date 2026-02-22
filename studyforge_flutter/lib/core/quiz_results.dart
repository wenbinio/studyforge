import 'models.dart';

Map<String, int> buildInterleavedTopicBreakdown({
  required String quizOutput,
  required List<Note> selectedNotes,
}) {
  final text = quizOutput.toLowerCase();
  final counts = <String, int>{};

  for (final note in selectedNotes) {
    final title = note.title.trim();
    if (title.isEmpty) {
      continue;
    }
    final pattern = RegExp(RegExp.escape(title.toLowerCase()));
    final matches = pattern.allMatches(text).length;
    counts[title] = matches;
  }

  final hasAny = counts.values.any((v) => v > 0);
  if (hasAny) {
    return counts;
  }

  for (final title in counts.keys.toList()) {
    counts[title] = 0;
  }
  return counts;
}
