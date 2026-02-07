# StudyForge

<div align="center">

![StudyForge](https://img.shields.io/badge/StudyForge-v1.0.0-blue)
![Platform](https://img.shields.io/badge/platform-Windows-lightgrey)
![.NET](https://img.shields.io/badge/.NET-8.0-purple)
![License](https://img.shields.io/badge/license-MIT-green)

**Your All-in-One Study Companion**

A comprehensive Windows desktop application that combines proven study techniques with AI-powered features to supercharge your learning.

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Documentation](#documentation)

</div>

---

## 🌟 Features

StudyForge integrates the best-known study techniques into a single, powerful application:

### 📚 **Active Recall with Flashcards**
- Create unlimited flashcards for any subject
- Organize cards by categories and tags
- AI-powered flashcard generation from your notes
- Quick search and filtering

### 🧠 **Spaced Repetition (SM-2 Algorithm)**
- Intelligent scheduling based on the SuperMemo 2 algorithm
- Cards automatically appear when they're due for review
- Adaptive difficulty based on your performance
- Track your learning progress over time

### ⏱️ **Pomodoro Timer**
- Built-in Pomodoro technique timer for focused study sessions
- Customizable work and break intervals
- Track completed Pomodoro sessions
- Automatic notifications for breaks and work periods

### 📝 **Note Management**
- Create and organize lecture notes and study materials
- Rich text support for comprehensive note-taking
- Tag and categorize your notes
- Mark materials as completed or in-progress

### 🤖 **Claude AI Integration**
- Generate flashcards automatically from your notes
- Find answers to questions within your study materials
- Summarize lengthy notes
- Intelligent content analysis

### 📊 **Progress Tracking**
- Comprehensive statistics dashboard
- Study streak tracking to keep you motivated
- Visual progress indicators
- Review history and performance analytics

## 🚀 Installation

### Prerequisites
- **Windows 10 or later** (64-bit)
- **.NET 8.0 Runtime** ([Download here](https://dotnet.microsoft.com/download/dotnet/8.0))
- **Claude API Key** (Optional, for AI features - [Get one here](https://console.anthropic.com/))

### Building from Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/wenbinio/studyforge.git
   cd studyforge
   ```

2. **Open the solution**
   ```bash
   cd StudyForge
   ```

3. **Restore dependencies**
   ```bash
   dotnet restore
   ```

4. **Build the application**
   ```bash
   dotnet build --configuration Release
   ```

5. **Run the application**
   ```bash
   dotnet run
   ```

   Or publish as a standalone executable:
   ```bash
   dotnet publish --configuration Release --runtime win-x64 --self-contained true -p:PublishSingleFile=true
   ```

## 📖 Usage

### Getting Started

1. **Launch StudyForge** - Double-click the application icon or run from the command line

2. **Configure Claude AI (Optional)**
   - Navigate to Settings (⚙️)
   - Enter your Claude API key
   - Click "Save API Key"

3. **Create Your First Flashcard**
   - Click on "🗂️ Flashcards" in the sidebar
   - Click "➕ Create Card"
   - Enter your question and answer
   - Click "Save"

### Using the Pomodoro Timer

1. Navigate to "⏱️ Pomodoro"
2. Customize your work/break intervals if desired
3. Click "▶ Start" to begin your study session
4. Work until the timer alerts you for a break
5. After 4 Pomodoros, enjoy a longer break!

### Creating Study Notes

1. Navigate to "📝 Notes"
2. Click "➕ Create Note"
3. Enter your note title, category, and content
4. Click "Save"

### Generating Flashcards with AI

1. Create or select a note in the Notes section
2. Click "🤖 Generate Cards"
3. AI will analyze your notes and create flashcards automatically
4. Review and edit the generated cards as needed

### Review Session (Active Recall)

1. Navigate to "🗂️ Flashcards"
2. Click "📚 Start Review"
3. Read each question carefully
4. Try to recall the answer before clicking "Show Answer"
5. Rate your recall quality:
   - **0 (Forgot)**: Complete blackout, restart learning
   - **3 (Hard)**: Correct but difficult to recall
   - **4 (Good)**: Correct with some hesitation
   - **5 (Easy)**: Perfect recall

## 🎯 Study Techniques Explained

### Active Recall
Instead of passively reading your notes, active recall forces your brain to retrieve information from memory. This strengthens neural pathways and improves long-term retention.

### Spaced Repetition
The SM-2 algorithm schedules reviews at optimal intervals. You review difficult cards more frequently and easy cards less often, maximizing learning efficiency.

### Pomodoro Technique
- Work for 25 minutes (one "Pomodoro")
- Take a 5-minute break
- After 4 Pomodoros, take a 15-minute break
- This prevents burnout and maintains high focus levels

## 🗂️ Project Structure

```
StudyForge/
├── Models/              # Data models (Flashcard, Note, etc.)
├── Services/            # Business logic and data access
│   ├── DatabaseService.cs
│   ├── ClaudeApiService.cs
│   └── PomodoroService.cs
├── Views/               # User interface components
│   ├── DashboardView.xaml
│   ├── FlashcardsView.xaml
│   ├── NotesView.xaml
│   ├── PomodoroView.xaml
│   ├── SettingsView.xaml
│   └── Dialogs/
├── ViewModels/          # View logic and data binding
└── Data/                # Database and storage
```

## 💾 Data Storage

All your data is stored locally on your computer at:
```
%APPDATA%\StudyForge\studyforge.db
```

The database uses SQLite and includes:
- Flashcards and their review history
- Study notes and materials
- Pomodoro session history
- Study statistics and progress
- User preferences and settings

## 🔒 Privacy & Security

- **Local Storage**: All your data stays on your computer
- **API Key Security**: Claude API keys are stored locally in the database
- **No Telemetry**: StudyForge doesn't collect or transmit any usage data
- **Open Source**: Full transparency - review the code yourself!

## 🛠️ Configuration

### Pomodoro Settings
- **Work Duration**: 1-60 minutes (default: 25)
- **Short Break**: 1-30 minutes (default: 5)
- **Long Break**: 1-60 minutes (default: 15)
- **Pomodoros Until Long Break**: 1-10 (default: 4)

### Flashcard Categories
Create custom categories to organize your cards by subject, course, or any system that works for you.

## 🤝 Contributing

Contributions are welcome! Here's how you can help:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

- **SuperMemo** for the SM-2 spaced repetition algorithm
- **Francesco Cirillo** for the Pomodoro Technique
- **Anthropic** for Claude AI API
- All contributors and users of StudyForge

## 📧 Support

Having issues or questions?
- Open an issue on GitHub
- Check the documentation
- Review the FAQ

## 🗺️ Roadmap

Future features planned:
- [ ] Import/export flashcard decks
- [ ] Study together mode (multiplayer)
- [ ] Advanced statistics and charts
- [ ] Mobile companion app
- [ ] Cloud sync (optional)
- [ ] Voice recording for audio flashcards
- [ ] Image support for visual learning
- [ ] Custom themes and appearance

---

<div align="center">

**Built with ❤️ for effective learning**

⭐ Star this repo if you find it helpful!

</div>