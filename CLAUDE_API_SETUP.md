# Claude API Setup Guide

This guide will help you set up the Claude API integration in StudyForge to enable AI-powered features.

## What You'll Need

- A Claude API account from Anthropic
- An API key
- Internet connection

## Step 1: Create an Anthropic Account

1. Visit [https://console.anthropic.com/](https://console.anthropic.com/)
2. Sign up for an account or log in if you already have one
3. Complete the registration process

## Step 2: Get Your API Key

1. Once logged in, navigate to the API Keys section
2. Click "Create Key" or "New API Key"
3. Give your key a descriptive name (e.g., "StudyForge App")
4. Copy the generated API key (it will look like: `sk-ant-...`)
5. **Important**: Save this key securely - you won't be able to see it again!

## Step 3: Configure StudyForge

1. Launch StudyForge
2. Click on the "⚙️ Settings" icon in the sidebar
3. Find the "Claude AI Configuration" section
4. Paste your API key into the "API Key" field
5. Click "Save API Key"

You should see a confirmation message: "API key saved successfully! AI features are now enabled."

## Step 4: Verify the Integration

Test the AI features by:

1. Creating a study note with some content
2. Navigating to the Notes section
3. Selecting your note
4. Clicking "🤖 Generate Cards"
5. Wait a few moments for the AI to process your notes

If successful, you'll see newly generated flashcards!

## AI-Powered Features

Once configured, you can use:

### 1. Automatic Flashcard Generation
- Select any note
- Click "Generate Cards"
- AI analyzes your content and creates relevant question/answer pairs

### 2. Answer Discovery
- Ask questions about your study materials
- AI searches your notes and provides answers

### 3. Note Summarization
- Get concise summaries of lengthy notes
- Extract key concepts automatically

## API Usage & Costs

- Claude API uses a pay-per-use model
- Costs are based on tokens processed
- StudyForge uses the Claude 3.5 Sonnet model
- Typical flashcard generation: ~$0.01-0.05 per request
- Check [Anthropic's pricing page](https://www.anthropic.com/pricing) for current rates

## Troubleshooting

### "API key not set" Error
- Make sure you saved the API key in Settings
- Verify the key is correct (should start with `sk-ant-`)

### "Failed to communicate with Claude API" Error
- Check your internet connection
- Verify your API key is valid and active
- Ensure you have API credits available

### Generated Flashcards Are Poor Quality
- Provide more detailed notes
- Include clear definitions and examples
- Try generating cards from specific sections rather than entire documents

## Privacy & Security

- Your API key is stored locally in the StudyForge database
- API keys are never transmitted to anyone except Anthropic
- All communication with Claude API is encrypted (HTTPS)
- Your study materials are only sent to Claude during AI operations

## Managing Your API Key

### Updating Your Key
1. Go to Settings
2. Enter a new API key
3. Click "Save API Key"

### Removing Your Key
1. Go to Settings
2. Clear the API key field
3. Click "Save API Key"

Note: Removing your API key will disable all AI features.

## Best Practices

1. **Don't share your API key** - Treat it like a password
2. **Monitor your usage** - Check your Anthropic dashboard regularly
3. **Set up billing alerts** - Configure spending limits in your Anthropic account
4. **Rotate keys periodically** - Generate new keys every few months for security

## Getting Help

If you encounter issues:
1. Check the Anthropic API status page
2. Review your API usage and limits in the Anthropic console
3. Consult the StudyForge documentation
4. Open an issue on the GitHub repository

## Alternative: Using Without AI

StudyForge works perfectly without the AI features! You can:
- Create flashcards manually
- Write your own notes
- Use all spaced repetition features
- Track your study progress

The AI integration is optional and designed to enhance, not replace, your study workflow.
