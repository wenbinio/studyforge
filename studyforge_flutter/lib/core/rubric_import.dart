import 'dart:io';

import 'package:path/path.dart' as p;

bool isSupportedRubricPath(String path) {
  final ext = p.extension(path).toLowerCase();
  return ext == '.txt' || ext == '.md';
}

Future<(String name, String content)> loadRubricFromPath(String rawPath) async {
  final path = rawPath.trim();
  if (path.isEmpty) {
    throw Exception('Path is required.');
  }
  if (!isSupportedRubricPath(path)) {
    throw Exception('Only .txt and .md rubric files are supported.');
  }
  final file = File(path);
  if (!await file.exists()) {
    throw Exception('Rubric file not found.');
  }
  final content = (await file.readAsString()).trim();
  if (content.isEmpty) {
    throw Exception('Rubric file is empty.');
  }
  final base = p.basenameWithoutExtension(path).trim();
  return (base.isEmpty ? 'Imported Rubric' : base, content);
}
