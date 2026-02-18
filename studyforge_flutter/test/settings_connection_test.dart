import 'package:flutter_test/flutter_test.dart';
import 'package:studyforge_flutter/core/settings_connection.dart';

void main() {
  test('buildConnectionTestPrompt asks for exact OK', () {
    final prompt = buildConnectionTestPrompt();
    expect(prompt, contains('Connection test'));
    expect(prompt, contains('"OK"'));
  });
}
