# StudyForge Documentation Index

Welcome to StudyForge! This index helps you navigate all the documentation for the different implementations of this comprehensive study application.

---

## 🚀 Quick Start

**New to StudyForge?** Start here:

1. Read the [README](README.md) for an overview of this C# WPF implementation
2. Check the [Quick Start Guide](QUICKSTART.md) to get up and running in 5 minutes
3. See [Which Version Should I Use?](#which-version-should-i-use) below

**Want to compare versions?** Jump to [Comparison Documents](#comparison-documents)

---

## 📚 Documentation Structure

### For This Implementation (C# WPF)

| Document | Purpose | Time to Read |
|----------|---------|--------------|
| [README.md](README.md) | Project overview, features, installation | 10 min |
| [QUICKSTART.md](QUICKSTART.md) | Get started in 5 minutes | 5 min |
| [USER_GUIDE.md](USER_GUIDE.md) | Complete usage instructions | 30 min |
| [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md) | Configure AI features | 10 min |
| [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) | Technical implementation details | 15 min |

### Comparison Documents

| Document | Purpose | Time to Read |
|----------|---------|--------------|
| [VERSION_GUIDE.md](VERSION_GUIDE.md) | Quick reference for choosing a version | 5 min |
| [COMPARISON.md](COMPARISON.md) | Comprehensive technical comparison | 20 min |
| [IMPLEMENTATION_COMPARISON.md](IMPLEMENTATION_COMPARISON.md) | Visual summary with charts | 10 min |

### Project Files

| Document | Purpose |
|----------|---------|
| [LICENSE](LICENSE) | MIT License |
| [.gitignore](.gitignore) | Git ignore rules |

---

## 🎯 Which Version Should I Use?

StudyForge has **three implementations**. Here's how to choose:

### 1️⃣ C# WPF (This Repository)

**You're here!** This is the most polished Windows native version.

**Choose this if:**
- ✅ You want the best user experience
- ✅ Performance matters
- ✅ You're on Windows only
- ✅ You want professional deployment

**Get Started:** [QUICKSTART.md](QUICKSTART.md)

### 2️⃣ Python v1 (study_app)

Available on the `copilot/extract-files-within` branch in the `study_app` folder.

**Choose this if:**
- ✅ You need a single executable file
- ✅ Users don't have Python installed
- ✅ You want interleaved practice mode
- ✅ You need PDF/DOCX import

**Get Started:** See branch README

### 3️⃣ Python v2 (study_app_v2)

Available on the `copilot/extract-files-within` branch in the `study_app_v2` folder.

**Choose this if:**
- ✅ You want the easiest development setup
- ✅ You have Python 3.10+ installed
- ✅ You want a setup wizard
- ✅ You need 7-day review forecast

**Get Started:** Just run `StudyForge.bat`

### 🤔 Still Unsure?

Read the [VERSION_GUIDE.md](VERSION_GUIDE.md) for a decision tree and detailed comparison.

---

## 📖 Reading Paths

### Path 1: I Just Want to Use StudyForge (C# Version)

```
1. README.md              (understand what it is)
2. QUICKSTART.md          (get it running)
3. CLAUDE_API_SETUP.md    (enable AI features)
4. USER_GUIDE.md          (learn all features)
```

**Time:** ~1 hour total

### Path 2: I'm Deciding Between Versions

```
1. README.md                        (understand C# version)
2. VERSION_GUIDE.md                 (quick comparison)
3. IMPLEMENTATION_COMPARISON.md     (visual summary)
4. COMPARISON.md                    (deep dive if needed)
```

**Time:** ~30-60 minutes

### Path 3: I'm a Developer Contributing

```
1. README.md                    (project overview)
2. IMPLEMENTATION_SUMMARY.md    (architecture details)
3. COMPARISON.md                (understand all versions)
4. Source code                  (dive into implementation)
```

**Time:** ~2 hours

### Path 4: I'm Migrating from Python Version

```
1. COMPARISON.md               (understand differences)
2. VERSION_GUIDE.md            (migration section)
3. QUICKSTART.md               (get C# version running)
4. Copy your database          (data transfer)
5. CLAUDE_API_SETUP.md         (reconfigure API)
```

**Time:** ~30 minutes

---

## 🔍 Find What You Need

### Installation Help

- **C# WPF**: [README.md § Installation](README.md#installation)
- **Quick start**: [QUICKSTART.md](QUICKSTART.md)
- **Build from source**: [README.md § Building from Source](README.md#building-from-source)

### Using the App

- **Complete guide**: [USER_GUIDE.md](USER_GUIDE.md)
- **Study techniques explained**: [README.md § Study Techniques](README.md#study-techniques-explained)
- **Tips**: [USER_GUIDE.md § Tips for Effective Study](USER_GUIDE.md#tips-for-effective-study)

### AI Integration

- **Setup Claude API**: [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md)
- **Using AI features**: [USER_GUIDE.md § Notes](USER_GUIDE.md#notes)
- **Troubleshooting**: [CLAUDE_API_SETUP.md § Troubleshooting](CLAUDE_API_SETUP.md#troubleshooting)

### Technical Details

- **Architecture**: [IMPLEMENTATION_SUMMARY.md § Architecture](IMPLEMENTATION_SUMMARY.md#file-structure)
- **Database schema**: [IMPLEMENTATION_SUMMARY.md § Data Storage](IMPLEMENTATION_SUMMARY.md#data-storage)
- **Algorithms**: [IMPLEMENTATION_SUMMARY.md § Key Algorithms](IMPLEMENTATION_SUMMARY.md#key-algorithms-implemented)

### Comparing Versions

- **Quick reference**: [VERSION_GUIDE.md](VERSION_GUIDE.md)
- **Visual comparison**: [IMPLEMENTATION_COMPARISON.md](IMPLEMENTATION_COMPARISON.md)
- **Deep dive**: [COMPARISON.md](COMPARISON.md)
- **Which to choose**: [VERSION_GUIDE.md § Decision Tree](VERSION_GUIDE.md#decision-tree)

### Troubleshooting

- **C# WPF issues**: Check GitHub issues
- **API problems**: [CLAUDE_API_SETUP.md § Troubleshooting](CLAUDE_API_SETUP.md#troubleshooting)
- **Common questions**: [USER_GUIDE.md § Common Questions](USER_GUIDE.md#common-questions)

---

## 🎓 Learning Resources

### Understanding Study Techniques

All documents cover the study techniques, but these are best:

- **Pomodoro**: [USER_GUIDE.md § Pomodoro Timer](USER_GUIDE.md#pomodoro-timer)
- **Active Recall**: [USER_GUIDE.md § Flashcards](USER_GUIDE.md#flashcards)
- **Spaced Repetition**: [README.md § Study Techniques](README.md#study-techniques-explained)
- **SM-2 Algorithm**: [IMPLEMENTATION_SUMMARY.md § Algorithms](IMPLEMENTATION_SUMMARY.md#key-algorithms-implemented)

### Technical Learning

- **MVVM Pattern**: [COMPARISON.md § Architecture](COMPARISON.md#architecture-deep-dive)
- **WPF Development**: Study the source code in `Views/` and `ViewModels/`
- **Spaced Repetition Math**: See `Models/Flashcard.cs`

---

## 🗺️ Repository Layout

```
studyforge/                           # Root directory
├── README.md                         # Main overview (start here)
├── QUICKSTART.md                     # 5-minute setup guide
├── USER_GUIDE.md                     # Complete usage instructions
├── CLAUDE_API_SETUP.md               # AI configuration
├── IMPLEMENTATION_SUMMARY.md         # Technical details
├── VERSION_GUIDE.md                  # Quick version comparison
├── COMPARISON.md                     # Detailed comparison
├── IMPLEMENTATION_COMPARISON.md      # Visual comparison
├── LICENSE                           # MIT License
├── .gitignore                        # Git ignore rules
└── StudyForge/                       # C# WPF application
    ├── Models/                       # Data models
    ├── Services/                     # Business logic
    ├── ViewModels/                   # MVVM view models
    ├── Views/                        # XAML UI components
    ├── Dialogs/                      # Modal windows
    └── StudyForge.csproj             # Project file
```

---

## 📞 Getting Help

### For Users

1. Check [USER_GUIDE.md § Common Questions](USER_GUIDE.md#common-questions)
2. Read [CLAUDE_API_SETUP.md § Troubleshooting](CLAUDE_API_SETUP.md#troubleshooting)
3. Search GitHub issues
4. Open a new issue with details

### For Developers

1. Read [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md)
2. Check [COMPARISON.md § Code Quality](COMPARISON.md#code-quality--maintainability)
3. Review source code comments
4. Open an issue for technical questions

### For Version Comparison

1. Start with [VERSION_GUIDE.md](VERSION_GUIDE.md)
2. Use decision tree to narrow options
3. Read relevant sections of [COMPARISON.md](COMPARISON.md)
4. Try multiple versions if still unsure (database is compatible!)

---

## 🔄 Related Resources

### External Links

- **Python Implementations**: `copilot/extract-files-within` branch
- **Anthropic Console**: https://console.anthropic.com/
- **.NET Downloads**: https://dotnet.microsoft.com/download
- **Spaced Repetition Info**: SuperMemo wiki

### Other Branches

- `main`: Initial repository state
- `copilot/extract-files-within`: Python implementations
- `copilot/create-all-in-one-study-app`: This C# WPF version (current)

---

## ⭐ Popular Reading Combinations

**"I want to start studying ASAP"**
→ [QUICKSTART.md](QUICKSTART.md) → [USER_GUIDE.md](USER_GUIDE.md)

**"Which version should I use?"**
→ [VERSION_GUIDE.md](VERSION_GUIDE.md) → [IMPLEMENTATION_COMPARISON.md](IMPLEMENTATION_COMPARISON.md)

**"How does this work technically?"**
→ [IMPLEMENTATION_SUMMARY.md](IMPLEMENTATION_SUMMARY.md) → [COMPARISON.md](COMPARISON.md)

**"I want to enable AI features"**
→ [CLAUDE_API_SETUP.md](CLAUDE_API_SETUP.md) → [USER_GUIDE.md § Notes](USER_GUIDE.md#notes)

**"I'm a Python user, why C#?"**
→ [COMPARISON.md § Python vs C#](COMPARISON.md#architecture-deep-dive) → [VERSION_GUIDE.md](VERSION_GUIDE.md)

---

## 📝 Document Statistics

| Document | Words | Time to Read |
|----------|-------|--------------|
| README.md | ~2,800 | 10 min |
| QUICKSTART.md | ~800 | 5 min |
| USER_GUIDE.md | ~3,500 | 30 min |
| CLAUDE_API_SETUP.md | ~1,200 | 10 min |
| IMPLEMENTATION_SUMMARY.md | ~2,800 | 15 min |
| VERSION_GUIDE.md | ~1,500 | 5 min |
| COMPARISON.md | ~6,000 | 20 min |
| IMPLEMENTATION_COMPARISON.md | ~3,000 | 10 min |
| **Total** | **~21,600** | **~2 hours** |

**Complete Reading:** ~2 hours to read everything
**Essential Reading:** ~30 minutes (README + QUICKSTART + VERSION_GUIDE)

---

## 🎯 Last Updated

This index was last updated: February 7, 2026

All documentation is current with StudyForge v1.0.0.

---

**Happy Studying! 📚✨**

Choose your version, read the relevant docs, and start acing those exams!
