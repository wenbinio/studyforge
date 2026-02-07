# Quick Start Guide - StudyForge

Get started with StudyForge in 5 minutes!

## Step 1: Build the Application (2 minutes)

```bash
# Navigate to the StudyForge directory
cd StudyForge

# Restore dependencies
dotnet restore

# Build the application
dotnet build

# Run StudyForge
dotnet run
```

## Step 2: First Launch (30 seconds)

When StudyForge opens, you'll see:
- **Dashboard** with empty statistics (normal for first launch)
- **Sidebar** with navigation options
- **Quick Actions** buttons

## Step 3: Create Your First Flashcard (1 minute)

1. Click **"🗂️ Flashcards"** in the sidebar
2. Click **"➕ Create Card"**
3. Fill in:
   - **Category**: "Example"
   - **Question**: "What is the capital of France?"
   - **Answer**: "Paris"
4. Click **"Save"**

Congratulations! You've created your first flashcard.

## Step 4: Try the Review System (1 minute)

1. Still in Flashcards, click **"📚 Start Review"**
2. Read the question: "What is the capital of France?"
3. Try to recall the answer mentally
4. Click **"Show Answer"**
5. Rate your recall (for this example, click **"5 - Easy"**)

The card is now scheduled for review later!

## Step 5: Start a Pomodoro Session (30 seconds)

1. Click **"⏱️ Pomodoro"** in the sidebar
2. Click **"▶ Start"**
3. The timer starts counting down from 25:00
4. Focus on studying for 25 minutes

You're now using the Pomodoro technique!

## Optional: Enable AI Features

If you have a Claude API key:

1. Click **"⚙️ Settings"**
2. Paste your API key in the **"API Key"** field
3. Click **"Save API Key"**

Now you can:
- Create a note (📝 Notes → ➕ Create Note)
- Select it and click **"🤖 Generate Cards"**
- AI will create flashcards from your notes!

## What's Next?

### Learn the Basics
- Read the [User Guide](USER_GUIDE.md) for detailed instructions
- Check the [README](README.md) for feature overview

### Study Effectively
- Create flashcards for your current courses
- Review cards daily
- Use Pomodoro for focused study
- Track your progress on the Dashboard

### Customize
- Change Pomodoro intervals in Pomodoro → Configuration
- Organize cards with categories
- Add notes and tags

## Common First-Time Questions

**Q: Where is my data stored?**
A: `%APPDATA%\StudyForge\studyforge.db` (automatic)

**Q: Do I need the API key to use StudyForge?**
A: No! AI features are optional. All core features work without it.

**Q: How does spaced repetition work?**
A: Cards you rate as "easy" appear less often. Difficult cards appear more frequently. The system optimizes your review schedule.

**Q: Can I import my existing flashcards?**
A: Not yet - create them in StudyForge or use AI generation from notes.

## Quick Tips

💡 **Rate honestly** - The spaced repetition algorithm works best with accurate ratings

💡 **Study daily** - Even 10 minutes helps maintain your streak

💡 **Use categories** - Organize cards by subject or topic

💡 **Take real breaks** - During Pomodoro breaks, actually rest!

💡 **Create clear cards** - One concept per flashcard works best

## Need Help?

- **Full Guide**: [USER_GUIDE.md](USER_GUIDE.md)
- **API Setup**: [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md)
- **Issues**: Open an issue on GitHub

## You're Ready! 🚀

Start studying smarter with StudyForge. Good luck with your learning!

---

**Time to get started**: ~5 minutes  
**Time to master**: Practice makes perfect!
