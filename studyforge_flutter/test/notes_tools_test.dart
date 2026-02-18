import 'package:flutter_test/flutter_test.dart';
import 'package:studyforge_flutter/core/notes_tools.dart';

void main() {
  test('countMatches is case-insensitive', () {
    expect(countMatches('Alpha alpha ALPHA', 'alpha'), 3);
  });

  test('safeNoteFilename replaces reserved characters', () {
    expect(safeNoteFilename('Civil/Procedure: Week*1'), 'Civil_Procedure_ Week_1');
  });
}
