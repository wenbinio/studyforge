# User Guide - StudyForge

## Table of Contents
1. [Getting Started](#getting-started)
2. [Dashboard](#dashboard)
3. [Flashcards](#flashcards)
4. [Notes](#notes)
5. [Pomodoro Timer](#pomodoro-timer)
6. [Settings](#settings)
7. [Tips for Effective Study](#tips-for-effective-study)

---

## Getting Started

### First Launch

When you first launch StudyForge, you'll see the Dashboard with empty statistics. This is normal! As you use the app, your progress will be tracked automatically.

### Navigation

The sidebar on the left provides quick access to all features:
- 📊 **Dashboard**: Overview of your study progress
- 🗂️ **Flashcards**: Create and review flashcards
- 📝 **Notes**: Manage your study notes
- ⏱️ **Pomodoro**: Focus timer for study sessions
- ⚙️ **Settings**: Configure the app and AI features

---

## Dashboard

The Dashboard is your study command center.

### Statistics Cards

**Cards Due Today**
- Shows how many flashcards need review today
- Click to navigate to the review session

**Total Reviewed**
- Lifetime count of flashcards you've reviewed
- Tracks your overall progress

**Pomodoros**
- Number of completed Pomodoro sessions
- Measures your focused study time

**Current Streak**
- Days in a row you've studied
- Helps maintain consistency

### Quick Actions

Fast shortcuts to common tasks:
- **Start Review Session**: Begin reviewing due flashcards
- **Create Flashcard**: Add a new card
- **Add Note**: Create a new study note
- **Start Pomodoro**: Begin a focused study session

### Study Progress

Detailed view of your learning metrics:
- Total study time
- Flashcard collection size
- Note count
- Best study streak

### Cards Due for Review

List of flashcards scheduled for today:
- See questions at a glance
- Organized by category
- Click to start reviewing

---

## Flashcards

### Creating Flashcards

1. Click "➕ Create Card"
2. Fill in the fields:
   - **Category**: Subject or topic (e.g., "Biology", "Spanish")
   - **Question**: What you want to remember
   - **Answer**: The correct response
   - **Notes** (Optional): Additional context or mnemonics
3. Click "Save"

**Tips for Good Flashcards:**
- Keep questions focused on one concept
- Make answers concise and clear
- Use your own words
- Include context in the question
- Add memory aids in the notes field

### Viewing Flashcards

The Flashcard list shows all your cards with:
- Question and answer preview
- Category tag
- Next review date
- Edit and delete buttons

**Filter Options:**
- By category
- By status (All, Due Today, Upcoming)

### Editing Flashcards

1. Click the ✏️ button on any card
2. Make your changes
3. Click "Save"

### Deleting Flashcards

1. Click the 🗑️ button on any card
2. Confirm deletion
3. The card is permanently removed

### Review Sessions

This is where the magic happens!

**Starting a Review:**
1. Click "📚 Start Review"
2. Cards due today will appear one at a time

**During Review:**
1. Read the question carefully
2. Try to recall the answer mentally
3. Click "Show Answer" when ready
4. Rate your recall honestly:

**Rating Scale:**
- **0 - Forgot**: Couldn't remember at all
  - Card resets and will appear frequently
- **3 - Hard**: Remembered with difficulty
  - Card interval increases slightly
- **4 - Good**: Remembered with minor hesitation
  - Card interval increases moderately
- **5 - Easy**: Perfect recall
  - Card interval increases significantly

**Why Rating Matters:**
The SM-2 spaced repetition algorithm uses your ratings to:
- Schedule reviews at optimal times
- Focus on cards you struggle with
- Gradually increase intervals for easy cards
- Maximize long-term retention

---

## Notes

### Creating Notes

1. Click "➕ Create Note"
2. Enter:
   - **Title**: Descriptive name for your note
   - **Category**: Subject area
   - **Content**: Your study material
3. Click "Save"

**Note-Taking Tips:**
- Use clear headings and structure
- Include definitions, examples, and explanations
- Write in your own words
- Add diagrams descriptions
- Keep related information together

### Managing Notes

**Editing:**
1. Click ✏️ on any note
2. Modify the content
3. Save changes

**Deleting:**
1. Click 🗑️ on any note
2. Confirm deletion

### AI-Powered Flashcard Generation

Turn your notes into flashcards automatically!

1. Select a note from the list
2. Click "🤖 Generate Cards"
3. Wait for Claude AI to analyze your content
4. Review the generated flashcards
5. Edit if needed

**Best Results:**
- Use detailed, well-structured notes
- Include definitions and examples
- Break complex topics into smaller notes
- Provide clear explanations

---

## Pomodoro Timer

The Pomodoro Technique helps you maintain focus and avoid burnout.

### How It Works

**Default Settings:**
- 25 minutes of focused work
- 5-minute short break
- 15-minute long break (after 4 Pomodoros)

### Using the Timer

1. Navigate to "⏱️ Pomodoro"
2. Click "▶ Start" to begin
3. Work without interruption until the timer sounds
4. Take your break when prompted
5. Repeat!

**Controls:**
- **Start**: Begin or resume the timer
- **Pause**: Temporarily stop the timer
- **Reset**: Cancel current session and start fresh

### Customizing Settings

1. Scroll to "Configuration"
2. Adjust durations:
   - Work Duration (1-60 minutes)
   - Short Break (1-30 minutes)
   - Long Break (1-60 minutes)
3. Click "Apply Settings"

**Custom Configurations:**
- **Deep Work**: 50min work / 10min break
- **Quick Study**: 15min work / 3min break
- **Traditional**: 25min work / 5min break

### During Breaks

**Short Breaks (5 min):**
- Stretch
- Get water
- Look away from screen
- Take deep breaths

**Long Breaks (15 min):**
- Take a walk
- Have a snack
- Do light exercise
- Completely disconnect from study

---

## Settings

### Claude AI Configuration

Enable AI features by adding your API key:

1. Get an API key from [console.anthropic.com](https://console.anthropic.com)
2. Paste it in the "API Key" field
3. Click "Save API Key"

See [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md) for detailed instructions.

### Study Preferences

Customize your experience:
- Notification settings
- Default categories
- Auto-advance options

### Data Management

**Database Location:**
- View where your data is stored
- Located at: `%APPDATA%\StudyForge\studyforge.db`

**Reset Statistics:**
- Clear all progress tracking
- Keeps flashcards and notes intact
- Use when starting fresh

---

## Tips for Effective Study

### 1. Use the System Regularly

**Daily Habit:**
- Review due cards every day
- Even 10 minutes makes a difference
- Consistency beats intensity

**Maintain Your Streak:**
- StudyForge tracks daily study
- Build momentum with consecutive days
- Don't break the chain!

### 2. Quality Over Quantity

**Better Flashcards:**
- One concept per card
- Clear, specific questions
- Concise answers
- Add context

**Active Recall:**
- Actually try to remember
- Don't just click "Show Answer" immediately
- Honest self-assessment is crucial

### 3. Optimize Your Environment

**During Pomodoros:**
- Eliminate distractions
- Phone in another room
- Close unnecessary tabs
- Tell others you're focusing

**Take Breaks Seriously:**
- Actually stop working
- Move your body
- Rest your eyes
- Clear your mind

### 4. Trust the Process

**Spaced Repetition:**
- Let the algorithm work
- Don't over-study easy cards
- Accept forgetting is normal
- Long-term retention takes time

**Be Patient:**
- Results compound over weeks/months
- Early progress seems slow
- Keep reviewing consistently
- Your brain is building connections

### 5. Combine Techniques

**Pomodoro + Flashcards:**
- Use Pomodoros for initial learning
- Review flashcards during short breaks
- Deep study during work periods

**Notes + AI:**
- Take detailed notes during lectures
- Generate flashcards with AI
- Review cards the same day
- Reinforce learning

### 6. Track Your Progress

**Use the Dashboard:**
- Check your stats regularly
- Celebrate milestones
- Identify patterns
- Adjust strategy

**Reflect:**
- What's working?
- What's challenging?
- How can you improve?

---

## Common Questions

**Q: How many cards should I review per day?**
A: Start with 10-20 new cards daily. Adjust based on time available and retention.

**Q: What if I miss a day?**
A: No problem! Cards will accumulate, but the algorithm adjusts. Just resume when you can.

**Q: Should I use AI-generated cards or manual cards?**
A: Both! AI saves time, but manual creation aids learning. Mix them.

**Q: How long until I see results?**
A: Initial retention improves in days. Long-term memory builds over weeks.

**Q: Can I study multiple subjects?**
A: Absolutely! Use categories to organize different topics.

**Q: What's the optimal Pomodoro length?**
A: 25 minutes works for most. Adjust based on your attention span and task difficulty.

---

## Keyboard Shortcuts

(Coming in future update)

---

## Getting Help

- Check this user guide
- Review the README.md
- Open an issue on GitHub
- Check the FAQ

---

**Happy studying! 📚**
