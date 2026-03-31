import 'package:flutter_test/flutter_test.dart';
import 'package:studyforge_flutter/core/essay_grading.dart';

void main() {
  group('buildEssayGradingPrompt', () {
    test('includes rubric section when rubric text exists', () {
      final prompt = buildEssayGradingPrompt(
        prompt: 'Analyze negligence.',
        draft: 'My analysis...',
        rubricText: 'IRAC, case support, conclusion',
      );
      expect(prompt, contains('Rubric:'));
      expect(prompt, contains('IRAC'));
    });

    test('omits rubric section when rubric text is empty', () {
      final prompt = buildEssayGradingPrompt(
        prompt: 'Analyze negligence.',
        draft: 'My analysis...',
      );
      expect(prompt, isNot(contains('Rubric:')));
    });
  });
}
