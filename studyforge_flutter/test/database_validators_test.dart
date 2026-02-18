import 'package:flutter_test/flutter_test.dart';
import 'package:studyforge_flutter/core/database_validators.dart';

void main() {
  test('isValidDailyStatField allows only whitelisted fields', () {
    expect(isValidDailyStatField('cards_added'), isTrue);
    expect(isValidDailyStatField('cards_reviewed'), isTrue);
    expect(isValidDailyStatField('invalid_field'), isFalse);
  });
}
