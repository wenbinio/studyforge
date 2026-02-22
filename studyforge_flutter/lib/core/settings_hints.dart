String providerHint(String provider) {
  switch (provider) {
    case 'anthropic':
      return 'Anthropic key starts with sk-ant-.';
    case 'openai':
      return 'OpenAI key usually starts with sk- or sk-proj-.';
    case 'gemini':
      return 'Gemini key usually starts with AIza.';
    case 'perplexity':
      return 'Perplexity key starts with pplx-.';
    default:
      return 'Check your provider key prefix and model.';
  }
}

String recommendedModel(String provider) {
  switch (provider) {
    case 'anthropic':
      return 'claude-sonnet-4-5-20250929';
    case 'openai':
      return 'gpt-4o-mini';
    case 'gemini':
      return 'gemini-1.5-flash';
    case 'perplexity':
      return 'sonar';
    default:
      return '';
  }
}
