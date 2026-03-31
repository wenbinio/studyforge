import 'dart:io';

import 'package:path/path.dart' as p;
import 'package:path_provider/path_provider.dart';

int countMatches(String content, String query) {
  final q = query.trim().toLowerCase();
  if (q.isEmpty) {
    return 0;
  }
  return RegExp(RegExp.escape(q)).allMatches(content.toLowerCase()).length;
}

String safeNoteFilename(String title) {
  final trimmed = title.trim();
  final fallback = trimmed.isEmpty ? 'note' : trimmed;
  return fallback.replaceAll(RegExp(r'[\\/:*?"<>|]'), '_');
}

Future<String> exportNoteToDocuments({
  required String title,
  required String content,
  required String extension,
}) async {
  final ext = extension.toLowerCase();
  if (ext != 'txt' && ext != 'md') {
    throw Exception('Unsupported export format.');
  }
  final dir = await getApplicationDocumentsDirectory();
  final filename = '${safeNoteFilename(title)}.$ext';
  final path = p.join(dir.path, filename);
  final file = File(path);
  await file.writeAsString(content);
  return path;
}
