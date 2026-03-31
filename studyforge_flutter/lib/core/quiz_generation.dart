import 'models.dart';

List<Note> pickQuizNotes({
  required List<Note> allNotes,
  required bool interleaved,
  required int? selectedNoteId,
  required Set<int> selectedNoteIds,
  int maxNotes = 6,
}) {
  if (interleaved) {
    return allNotes
        .where((n) => n.id != null && selectedNoteIds.contains(n.id))
        .take(maxNotes)
        .toList();
  }
  if (selectedNoteId == null) {
    return const [];
  }
  return allNotes.where((n) => n.id == selectedNoteId).take(1).toList();
}

String buildQuizPrompt({
  required List<Note> notes,
  required String userInstruction,
  required bool interleaved,
  required int questionCount,
}) {
  final noteBlock = notes.map((n) => '${n.title}\n${n.content}').join('\n\n');
  final mode = interleaved ? 'interleaved' : 'single-topic';
  return 'Generate $questionCount multiple-choice study questions with 4 options each and provide answer key. '
      'Keep output concise. Mode: $mode.\n\n'
      'Notes:\n$noteBlock\n\n'
      'Additional instruction: $userInstruction';
}
