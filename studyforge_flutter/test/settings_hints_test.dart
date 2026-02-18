import 'package:flutter_test/flutter_test.dart';
import 'package:studyforge_flutter/core/settings_hints.dart';

void main() {
  test('providerHint returns provider-specific guidance', () {
    expect(providerHint('anthropic'), contains('sk-ant-'));
    expect(providerHint('gemini'), contains('AIza'));
  });

  test('recommendedModel returns defaults', () {
    expect(recommendedModel('openai'), isNotEmpty);
    expect(recommendedModel('unknown-provider'), '');
  });
}
