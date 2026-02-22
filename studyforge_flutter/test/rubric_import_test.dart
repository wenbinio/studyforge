import 'dart:io';

import 'package:flutter_test/flutter_test.dart';
import 'package:studyforge_flutter/core/rubric_import.dart';

void main() {
  test('isSupportedRubricPath accepts txt and md only', () {
    expect(isSupportedRubricPath('/tmp/a.txt'), isTrue);
    expect(isSupportedRubricPath('/tmp/a.md'), isTrue);
    expect(isSupportedRubricPath('/tmp/a.pdf'), isFalse);
  });

  test('loadRubricFromPath reads file content', () async {
    final file = File('/tmp/studyforge-rubric-test.md');
    await file.writeAsString('Rubric body');
    final loaded = await loadRubricFromPath(file.path);
    expect(loaded.$1, 'studyforge-rubric-test');
    expect(loaded.$2, 'Rubric body');
  });
}
