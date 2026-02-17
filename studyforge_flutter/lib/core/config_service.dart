import 'dart:convert';

import 'package:shared_preferences/shared_preferences.dart';

import 'models.dart';

class ConfigService {
  static const _configKey = 'studyforge_config';

  Future<AppConfig> loadConfig() async {
    final prefs = await SharedPreferences.getInstance();
    final raw = prefs.getString(_configKey);
    if (raw == null || raw.isEmpty) {
      return const AppConfig();
    }
    final decoded = jsonDecode(raw) as Map<String, Object?>;
    return AppConfig.fromJson(decoded);
  }

  Future<void> saveConfig(AppConfig config) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_configKey, jsonEncode(config.toJson()));
  }

  String detectProviderFromKey(String key) {
    if (key.startsWith('sk-ant-')) {
      return 'anthropic';
    }
    if (key.startsWith('sk-proj-') || key.startsWith('sk-')) {
      return 'openai';
    }
    if (key.startsWith('AIza')) {
      return 'gemini';
    }
    if (key.startsWith('pplx-')) {
      return 'perplexity';
    }
    return 'anthropic';
  }
}
