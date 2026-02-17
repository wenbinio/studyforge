import 'dart:convert';

import 'package:http/http.dart' as http;

class AiService {
  Future<String> generateText({
    required String provider,
    required String apiKey,
    required String model,
    required String prompt,
  }) async {
    if (apiKey.trim().isEmpty) {
      throw Exception('API key is required.');
    }

    switch (provider) {
      case 'anthropic':
        return _anthropic(apiKey: apiKey, model: model, prompt: prompt);
      case 'openai':
        return _openai(apiKey: apiKey, model: model, prompt: prompt);
      case 'gemini':
        return _gemini(apiKey: apiKey, model: model, prompt: prompt);
      case 'perplexity':
        return _perplexity(apiKey: apiKey, model: model, prompt: prompt);
      default:
        throw Exception('Unsupported AI provider: $provider');
    }
  }

  Future<String> _anthropic({
    required String apiKey,
    required String model,
    required String prompt,
  }) async {
    final response = await http.post(
      Uri.parse('https://api.anthropic.com/v1/messages'),
      headers: {
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'content-type': 'application/json',
      },
      body: jsonEncode({
        'model': model,
        'max_tokens': 1200,
        'messages': [
          {'role': 'user', 'content': prompt}
        ]
      }),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Anthropic request failed (${response.statusCode}).');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final content = data['content'] as List<dynamic>?;
    if (content == null || content.isEmpty) {
      return '';
    }
    return content.first['text'] as String? ?? '';
  }

  Future<String> _openai({
    required String apiKey,
    required String model,
    required String prompt,
  }) async {
    final response = await http.post(
      Uri.parse('https://api.openai.com/v1/chat/completions'),
      headers: {
        'Authorization': 'Bearer $apiKey',
        'content-type': 'application/json',
      },
      body: jsonEncode({
        'model': model,
        'messages': [
          {'role': 'user', 'content': prompt}
        ]
      }),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('OpenAI request failed (${response.statusCode}).');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final choices = data['choices'] as List<dynamic>?;
    if (choices == null || choices.isEmpty) {
      return '';
    }
    return (choices.first['message']?['content'] as String?) ?? '';
  }

  Future<String> _gemini({
    required String apiKey,
    required String model,
    required String prompt,
  }) async {
    final effectiveModel = model.isEmpty ? 'gemini-1.5-pro' : model;
    final response = await http.post(
      Uri.parse(
          'https://generativelanguage.googleapis.com/v1beta/models/$effectiveModel:generateContent?key=$apiKey'),
      headers: {'content-type': 'application/json'},
      body: jsonEncode({
        'contents': [
          {
            'parts': [
              {'text': prompt}
            ]
          }
        ]
      }),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Gemini request failed (${response.statusCode}).');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final candidates = data['candidates'] as List<dynamic>?;
    if (candidates == null || candidates.isEmpty) {
      return '';
    }
    return (candidates.first['content']?['parts']?.first?['text'] as String?) ??
        '';
  }

  Future<String> _perplexity({
    required String apiKey,
    required String model,
    required String prompt,
  }) async {
    final effectiveModel = model.isEmpty ? 'sonar' : model;
    final response = await http.post(
      Uri.parse('https://api.perplexity.ai/chat/completions'),
      headers: {
        'Authorization': 'Bearer $apiKey',
        'content-type': 'application/json',
      },
      body: jsonEncode({
        'model': effectiveModel,
        'messages': [
          {'role': 'user', 'content': prompt}
        ]
      }),
    );

    if (response.statusCode < 200 || response.statusCode >= 300) {
      throw Exception('Perplexity request failed (${response.statusCode}).');
    }

    final data = jsonDecode(response.body) as Map<String, dynamic>;
    final choices = data['choices'] as List<dynamic>?;
    if (choices == null || choices.isEmpty) {
      return '';
    }
    return (choices.first['message']?['content'] as String?) ?? '';
  }
}
