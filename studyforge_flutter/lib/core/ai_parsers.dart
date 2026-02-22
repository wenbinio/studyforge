import 'dart:convert';

class GeneratedFlashcard {
  const GeneratedFlashcard({
    required this.front,
    required this.back,
    this.tags = '',
  });

  final String front;
  final String back;
  final String tags;
}

List<GeneratedFlashcard> parseGeneratedFlashcards(String raw) {
  final parsed = _decodeJson(_stripCodeFences(raw));
  final list = _toList(parsed);
  if (list == null) {
    return const [];
  }

  final cards = <GeneratedFlashcard>[];
  for (final item in list) {
    if (item is! Map<String, dynamic>) {
      continue;
    }
    final front = (item['front'] as String? ?? '').trim();
    final back = (item['back'] as String? ?? '').trim();
    if (front.isEmpty || back.isEmpty) {
      continue;
    }
    cards.add(
      GeneratedFlashcard(
        front: front,
        back: back,
        tags: (item['tags'] as String? ?? '').trim(),
      ),
    );
  }
  return cards;
}

Object? _decodeJson(String input) {
  try {
    return jsonDecode(input);
  } catch (_) {
    return null;
  }
}

String _stripCodeFences(String input) {
  final trimmed = input.trim();
  final fenced = RegExp(r'^```(?:json)?\s*([\s\S]*?)\s*```$', caseSensitive: false);
  final match = fenced.firstMatch(trimmed);
  if (match != null) {
    return (match.group(1) ?? '').trim();
  }
  return trimmed;
}

List<dynamic>? _toList(Object? parsed) {
  if (parsed is List<dynamic>) {
    return parsed;
  }
  if (parsed is Map<String, dynamic>) {
    final nested = parsed['flashcards'];
    if (nested is List<dynamic>) {
      return nested;
    }
  }
  return null;
}
