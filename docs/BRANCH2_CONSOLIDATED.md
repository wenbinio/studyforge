# Branch 2: Feature Research — Consolidated Unique Content

**Source:** Branch 2 (b2_FEATURE_RESEARCH.md, b2_FEATURE_CHECKLIST.md, b2_RESEARCH_GUIDE.md)  
**Extracted:** User scenarios (before/after), per-category implementation notes with Python libraries, unique feature proposals, full 100+ item checklist with quarterly framework, multi-audience reading paths, and research methodology. Redundant competitor descriptions covered better by Branches 1 and 3 are omitted.

---

## 1. User Scenarios — Before/After Comparisons

### Scenario 1: Medical Student

**Pain Points:**
- Needs to memorize 10,000+ anatomy terms
- Visual learner (diagrams crucial)
- Limited study time (12-hour clinical rotations)

**Before (Current StudyForge):** Basic flashcards with spaced repetition only.

**After (With New Features):**
1. 🆕 **Cloze Deletion:** "The {{c1::brachial plexus}} innervates the upper limb"
2. 🆕 **Image Occlusion:** Anatomy diagrams with hidden labels
3. 🆕 **Audio Cards:** Pronunciation of medical terms
4. 🆕 **Multi-Subject Organization:** Separate decks per anatomy region
5. 🆕 **Mobile App:** Study during commute/lunch breaks

**Why Better Than Anki:** Simpler UI, less intimidating for beginners · AI auto-generates cards from textbook notes (save hours) · AI explains concepts in simple terms (personal tutor)

---

### Scenario 2: Study Group of 5 Law Students

**Pain Points:**
- Creating shared case brief decks (current: email spreadsheets)
- No way to discuss flashcards (current: separate group chat)
- Duplicate effort (everyone creates same cards)

**After (With New Features):**
1. 🆕 **Shared Decks:** Collaborate on single deck, everyone syncs
2. 🆕 **Comments:** Discuss confusing cards in-app
3. 🆕 **Leaderboards:** Friendly competition on reviews
4. 🆕 **Group Pomodoro:** Virtual study room (see who's online)
5. 🆕 **Note Bundles:** Share lecture note collections

**Why Better Than Quizlet:** StudyForge has spaced repetition (Quizlet lacks scheduling) · Legal-specific tools (hypotheticals, essays) · No ads, no subscription tiers

---

### Scenario 3: Language Learner

**Pain Points:**
- Needs audio for pronunciation
- Wants both English→Spanish AND Spanish→English cards
- Struggles with verb conjugations (fill-in-blank practice)

**After (With New Features):**
1. 🆕 **Audio Cards:** Record native speaker pronunciation
2. 🆕 **Reverse Cards:** Auto-generate bidirectional cards
3. 🆕 **Cloze Deletion:** "Yo {{c1::hablo}} español" (I speak Spanish)
4. 🆕 **AI Chat:** Practice conversations with AI tutor
5. ✅ **Current:** Spaced repetition for vocabulary retention

**Why Better Than Duolingo:** Custom content (import your textbook vocab) · Spaced repetition (not just level-based progression) · No gamification pressure (optional achievements instead)

---

### Scenario 4: Unmotivated Student

**Pain Points:**
- Finds studying boring
- Loses streaks and gives up
- No external accountability

**After (With New Features):**
1. 🆕 **Gamification:** Earn XP, unlock badges, level up
2. 🆕 **Daily Goals:** "Review 10 cards, earn bonus XP"
3. 🆕 **Achievements:** "Night Owl" badge for late study
4. 🆕 **Leaderboards:** Compete with friends

**Why Better Than Forest:** Forest only tracks time, StudyForge tracks learning · StudyForge = productivity + actual study content

---

### Scenario 5: Graduate Student Writing Thesis

**Pain Points:**
- 200+ sources to manage
- Needs to annotate PDFs
- Wants bidirectional links between concepts

**After (With New Features):**
1. 🆕 **PDF Annotation:** Highlight and comment directly
2. 🆕 **Knowledge Graph:** Link notes, visualize relationships
3. 🆕 **Backlinks:** See what references each note
4. 🆕 **Citation Manager:** Auto-format bibliography

**Why Better Than Notion:** Notion lacks spaced repetition (can't turn notes into quizzes) · Notion lacks AI tutoring (no Claude integration) · StudyForge is local-first (no vendor lock-in)

---

## 2. Per-Category Implementation Notes with Python Libraries

### Category 1: Advanced Flashcard Types

| Feature | Implementation | Library / Approach |
|---------|---------------|-------------------|
| **Cloze Deletion** | Regex parsing of `{{c1::hidden text}}` syntax + custom review UI | Python `re` module |
| **Image Occlusion** | Canvas drawing tool, rectangle coordinates stored in DB | `tkinter.Canvas` or `Pillow` |
| **Audio Cards** | Record/upload pronunciations, playback during review | `pyaudio` or `sounddevice` |
| **Reverse Cards** | Auto-duplicate card with front↔back flipped | DB insert (trivial) |
| **Multi-Cloze** | Multiple `{{c1::}}` `{{c2::}}` deletions per card with independent reveals | Regex + indexed reveals |

**DB Change:** Add `card_type` column to `flashcards` table (`basic`, `cloze`, `image_occlusion`, `audio`, `reverse`)

---

### Category 2: Knowledge Graph & Linked Notes

| Feature | Implementation | Library / Approach |
|---------|---------------|-------------------|
| **Bidirectional Links** | Parse `[[Note Title]]` wiki-syntax in notes | Python `re` module |
| **Graph Visualization** | Visual map of note connections | `networkx` + `matplotlib` |
| **Backlinks Panel** | Query `links` table for incoming references | SQLite JOIN query |
| **Orphan Detection** | Identify notes with zero links | SQL `LEFT JOIN ... IS NULL` |

**DB Change:** Add `links` table: `source_note_id`, `target_note_id`, `link_text`

---

### Category 3: Gamification & Motivation

| Feature | Implementation | Library / Approach |
|---------|---------------|-------------------|
| **XP System** | +10 XP per card reviewed, +50 per quiz, +25 per Pomodoro | DB counter + triggers |
| **Levels & Ranks** | Novice → Scholar → Expert → Master tier progression | Threshold lookup table |
| **Achievements** | 50+ badges with condition-checking engine | Event-driven checks |
| **Daily Goals** | "Review 20 cards today" with progress bars | `CTkProgressBar` widget |
| **Leaderboards** | Weekly XP rankings (requires cloud) | Firebase/Supabase API |

**DB Change:** Add `user_progress` table (level, xp, achievements_unlocked) + `goals` table (goal_type, target, current, deadline)

**Sample Achievements:**
- "Century Club" — review 100 cards in one day
- "Streak Master" — maintain 30-day streak
- "Night Owl" — study past midnight
- "Early Bird" — study before 7am
- "Quiz Ace" — score 100% on a quiz

---

### Category 4: Multi-Subject Organization

| Feature | Implementation | Library / Approach |
|---------|---------------|-------------------|
| **Subject Folders** | Course-level grouping | New `subjects` table |
| **Color-Coded Tags** | Visual categorization with customizable colors | CSS/CTk styling |
| **Hierarchical Decks** | Nested structure: Course → Unit → Topic | Parent-child FK |
| **Subject-Specific Settings** | Per-subject Pomodoro durations, review targets | `settings_json` column |

**DB Change:** Add `subjects` table (name, color, icon, settings_json) + `subject_id` FK to notes, flashcards, quizzes

---

### Category 5: Enhanced AI Tutor

| Feature | Implementation | Library / Approach |
|---------|---------------|-------------------|
| **AI Chat Interface** | Conversational Q&A with history | New tab + Claude streaming API |
| **Socratic Questioning** | AI asks follow-up questions, not direct answers | Prompt engineering |
| **Voice Interaction** | Speak questions, hear answers | `speech_recognition` + `pyttsx3` or `gTTS` |
| **Context-Aware** | AI grounds responses in user's actual notes | RAG over user's note DB |

**DB Change:** Add `conversations` table for chat history persistence

---

### Category 6: PDF Annotation & Highlighting

| Feature | Implementation | Library / Approach |
|---------|---------------|-------------------|
| **Highlight & Annotate** | Mark up imported PDFs in-app | `PyMuPDF` (fitz) advanced features |
| **Auto-Flashcard from Highlights** | Convert highlights to cards with AI | Highlight text → Claude → card |
| **Linked Highlights** | Jump from flashcard to source PDF location | `source_location` FK field |
| **Drawing Tools** | Arrows, shapes, freehand on PDFs | `tkinter.Canvas` overlay |

**DB Change:** Store highlights with page number + coordinates, link to flashcards via `source_location`

---

### Category 7: Calendar & Study Planning

| Feature | Implementation | Library / Approach |
|---------|---------------|-------------------|
| **Study Schedule Calendar** | Plan sessions in advance | `tkcalendar` library |
| **Exam Countdown** | Days-remaining display | Simple date math |
| **Review Distribution** | Balance daily card workload | Algorithm to spread due cards |
| **Google Calendar Sync** | Two-way sync | Google Calendar API (optional) |

**DB Change:** Add `study_plan` table (event_type, subject, scheduled_time, duration, completed)

---

### Category 8: Advanced Analytics

| Feature | Implementation | Library / Approach |
|---------|---------------|-------------------|
| **Heatmaps** | Study patterns by hour/day/week | `matplotlib` or `plotly` |
| **Forgetting Curve** | Retention over time per card/deck | Query `review_log` table |
| **Predictive Analytics** | "3 more hours to master topic" | Claude analysis of stats |
| **Export Reports** | PDF/CSV study reports | `reportlab` or HTML→PDF |

---

### Category 9: Templates & Study Frameworks

| Feature | Implementation | Library / Approach |
|---------|---------------|-------------------|
| **Note Templates** | Case Brief, Cornell Notes, IRAC pre-structured | JSON files |
| **Flashcard Templates** | Definition, Example, Comparison formats | JSON schema |
| **Quiz Templates** | Weekly Review (10 Q), Mock Exam (50 Q, timed) | JSON config |
| **Custom Template Creator** | Build and save own templates | Settings UI |

**DB Change:** Add `templates` table (name, type, content_json). Ship with 10–15 built-in templates.

---

### Implementation Effort Summary

| Effort Level | Features | Notes |
|-------------|----------|-------|
| **Low** (days) | Reverse cards, color-coded tags, daily goals, templates, export/import bundles | DB + UI widget changes only |
| **Medium** (weeks) | Cloze deletion, knowledge graph (`networkx`), gamification engine, PDF annotation, analytics charts (`matplotlib`/`plotly`) | New parsing/rendering logic |
| **High** (months) | Image occlusion (canvas tool), audio cards (`pyaudio`), collaboration (cloud backend), mobile apps (React Native/Flutter), AI chat (streaming API) | Significant new infrastructure |

---

## 3. Unique Feature Proposals (Not in Other Branches)

### Health & Wellness Integration
- **Eye Strain Reminders** — 20-20-20 rule notifications (every 20 min, look 20 ft away for 20 sec)
- **Posture Alerts** — Stretch reminders every 45–60 minutes
- **Hydration Tracker** — Water intake logging
- **Sleep Schedule** — Bedtime reminders based on study patterns ("You studied 3 hours tonight. Time for sleep!")
- **Break Suggestions** — AI detects fatigue patterns, suggests rest
- **Screen Time Limits** — Optional daily caps with warnings

### Advanced Legal Features (Domain-Specific)
- **Case Law Database** — Integrated legal research (Supreme Court cases)
- **Citation Manager** — Auto-format Bluebook citations
- **Bibliography Generator** — Compile citations from notes
- **Mock Trial Prep** — Simulate courtroom scenarios (direct/cross-examination practice)
- **Jurisdiction Toggles** — US vs UK vs Canadian law support with localized hypotheticals
- **Case Comparison Tables** — Side-by-side analysis of 5+ cases

### Integrations & Ecosystem
- **Discord Bot** — Study group integration ("StudyBot, quiz me on torts")
- **Canvas/Blackboard Integration** — Import assignments and syllabi
- **Grammarly API** — Real-time writing assistance in essays
- **Zotero/Mendeley** — Reference management for research papers
- **Zapier/IFTTT** — Automation workflows (e.g., auto-import emails)

### Spaced Repetition Enhancements
- **FSRS Algorithm** — Modern alternative to SM-2 (more accurate predictions, used by Anki's FSRS-4.5)
- **Custom Algorithms** — User-selectable per deck
- **Cram Mode** — Ignore scheduling for rapid pre-exam review
- **Learn Ahead** — Preview cards not yet due
- **Filtered Decks** — Dynamic subsets by tag, difficulty, age
- **Suspend/Bury Cards** — Temporarily hide cards from review
- **Manual Interval Adjustment** — Override AI scheduling when needed

---

## 4. Full Feature Checklist (100+ Items, GitHub-Style)

### 🚀 HIGH PRIORITY (Immediate Impact)

#### Advanced Flashcard Types
- [ ] **Cloze Deletion Cards** — Fill-in-blank format with `{{c1::hidden}}` syntax
- [ ] **Image Occlusion** — Hide parts of images for visual recall (anatomy, geography, diagrams)
- [ ] **Audio Cards** — Record/upload pronunciations, play back during review
- [ ] **Reverse Cards** — Auto-generate front↔back variants (bidirectional learning)
- [ ] **Multi-Cloze Support** — Multiple deletions per card with independent reveals

#### Knowledge Graph & Linking
- [ ] **Bidirectional Links** — `[[Note Title]]` wiki-style linking between notes
- [ ] **Backlinks Panel** — "What links here?" section showing incoming references
- [ ] **Graph Visualization** — Visual map of note connections and relationships
- [ ] **Tag Graph** — Visualize tag relationships and clusters
- [ ] **Orphan Detection** — Identify isolated notes without connections

#### Gamification & Motivation
- [ ] **Experience Points (XP)** — Earn points for reviews, notes, sessions
- [ ] **Levels & Ranks** — Progress through tiers (Novice → Scholar → Expert → Master)
- [ ] **Achievements System** — 50+ badges to unlock (streaks, milestones, challenges)
- [ ] **Daily Goals** — Set and track review/study targets with progress bars
- [ ] **Leaderboards** — Compete with friends on XP, cards reviewed, study time (opt-in)
- [ ] **Streak Enhancements** — Bonus XP for consecutive days, visual flame icons
- [ ] **Unlockable Rewards** — Themes, emojis, card types locked behind levels

#### Multi-Subject Organization
- [ ] **Subject/Course Folders** — Organize content by class or topic area
- [ ] **Color-Coded Tags** — Visual categorization with customizable colors
- [ ] **Hierarchical Decks** — Nested deck structure (Course → Unit → Topic)
- [ ] **Subject-Specific Settings** — Per-subject Pomodoro durations, review targets
- [ ] **Subject Dashboard** — Stats and progress tracking per course
- [ ] **Bulk Tag Operations** — Add/remove tags across multiple items at once

---

### ⭐ MEDIUM PRIORITY (Enhance Existing)

#### Enhanced AI Tutor
- [ ] **AI Chat Interface** — Conversational Q&A with conversation history
- [ ] **Socratic Questioning** — AI asks follow-up questions instead of giving answers
- [ ] **Personalized Study Plans** — AI analyzes weak areas, suggests focus topics
- [ ] **Voice Interaction** — Speak questions, hear answers (hands-free studying)
- [ ] **Context-Aware Assistance** — AI grounds responses in user's actual notes
- [ ] **Study Recommendations** — "You're struggling with X, focus on Y next"

#### PDF Annotation & Highlighting
- [ ] **Highlight & Annotate** — Mark up imported PDFs directly in-app
- [ ] **Auto-Flashcard from Highlights** — Convert highlights to cards with AI
- [ ] **Linked Highlights** — Jump from flashcard to source PDF location
- [ ] **Export Annotations** — Save highlights as notes or Markdown
- [ ] **Drawing Tools** — Arrows, shapes, freehand drawing on PDFs
- [ ] **Sticky Notes** — Add comment boxes to specific PDF locations

#### Calendar & Study Planning
- [ ] **Study Schedule Calendar** — Plan sessions in advance with calendar view
- [ ] **Exam Countdown** — Track deadlines with days-remaining display
- [ ] **Review Distribution** — Balance daily workload, reschedule to spread load
- [ ] **Time Blocking** — Allocate specific hours to subjects
- [ ] **Google Calendar Sync** — Two-way sync with external calendars
- [ ] **Pomodoro Integration** — Start timer directly from calendar events

#### Advanced Analytics & Insights
- [ ] **Heatmaps** — Visualize study patterns by hour/day/week
- [ ] **Forgetting Curve Analysis** — Track retention over time per card/deck
- [ ] **Performance Metrics** — Detailed stats per subject (retention rate, time/card)
- [ ] **Predictive Analytics** — AI-powered insights ("3 more hours to master topic")
- [ ] **Export Reports** — Generate PDF/CSV study reports
- [ ] **Weekly Summary Emails** — Automated progress reports

#### Templates & Study Frameworks
- [ ] **Note Templates** — Pre-structured formats (Case Brief, Cornell Notes, IRAC)
- [ ] **Flashcard Templates** — Custom card formats (Definition, Example, Comparison)
- [ ] **Quiz Templates** — Reusable quiz types (Weekly Review, Mock Exam)
- [ ] **Study Method Guides** — Built-in tutorials for effective studying
- [ ] **Custom Template Creator** — Build and save your own templates
- [ ] **Template Marketplace** — Share templates with community (future)

---

### 💡 NICE-TO-HAVE (Future Expansion)

#### Collaboration & Sharing
- [ ] **Shared Flashcard Decks** — Collaborate with classmates on decks
- [ ] **Note Sharing** — Export/import note bundles (JSON format)
- [ ] **Group Study Sessions** — Real-time co-study with virtual rooms
- [ ] **Comments & Annotations** — Discuss flashcards and notes in-app
- [ ] **Activity Feed** — See what study group members are working on
- [ ] **Cloud Backend** — Firebase/Supabase for real-time sync (required for above)

#### Multi-Format Content
- [ ] **Video Notes** — Embed YouTube, Vimeo, local videos with timestamps
- [ ] **AI Video Transcription** — Auto-generate notes from video lectures
- [ ] **Diagrams & Drawings** — Built-in whiteboard/canvas for concept maps
- [ ] **Tables & Spreadsheets** — Enhanced table editing (comparison charts)
- [ ] **Code Blocks** — Syntax highlighting for CS students (Python, Java, etc.)
- [ ] **LaTeX/MathJax Support** — Render mathematical equations

#### Spaced Repetition Enhancements
- [ ] **FSRS Algorithm** — Modern alternative to SM-2 (more accurate predictions)
- [ ] **Custom Algorithms** — User-selectable per deck
- [ ] **Cram Mode** — Ignore scheduling for rapid pre-exam review
- [ ] **Learn Ahead** — Preview cards not yet due
- [ ] **Filtered Decks** — Dynamic subsets by tag, difficulty, age
- [ ] **Suspend/Bury Cards** — Temporarily hide cards
- [ ] **Manual Interval Adjustment** — Override AI scheduling when needed

#### Import/Export Ecosystem
- [ ] **Anki Import** — Convert Anki decks (.apkg) with scheduling preserved
- [ ] **Notion Import** — Convert Notion databases to notes
- [ ] **CSV Import/Export** — Bulk flashcard management via spreadsheets
- [ ] **Browser Extension** — Web clipper for saving articles as notes
- [ ] **Markdown Export** — Export entire knowledge base as Markdown files
- [ ] **API Access** — Programmatic access for power users

#### Accessibility & Inclusivity
- [ ] **Light Theme** — High contrast alternative to dark theme
- [ ] **High Contrast Mode** — Accessibility for visual impairments
- [ ] **Screen Reader Support** — JAWS, NVDA compatibility
- [ ] **Dyslexia-Friendly Font** — OpenDyslexic option
- [ ] **Text-to-Speech** — Read flashcards and notes aloud
- [ ] **Full Keyboard Navigation** — No mouse required
- [ ] **Font Size Controls** — User-adjustable text size
- [ ] **Language Support** — i18n for Spanish, French, German, Chinese

#### Advanced Legal Features (Law Student Specific)
- [ ] **Case Law Database** — Integrated legal research (Supreme Court cases)
- [ ] **Citation Manager** — Auto-format Bluebook citations
- [ ] **Bibliography Generator** — Compile citations from notes
- [ ] **Mock Trial Prep** — Simulate courtroom scenarios
- [ ] **Jurisdiction Toggles** — US vs UK vs Canadian law support
- [ ] **Case Comparison Tables** — Side-by-side analysis of 5+ cases

#### Health & Wellness
- [ ] **Eye Strain Reminders** — 20-20-20 rule notifications
- [ ] **Posture Alerts** — Stretch reminders every 45-60 minutes
- [ ] **Hydration Tracker** — Water intake logging
- [ ] **Sleep Schedule** — Bedtime reminders based on study patterns
- [ ] **Break Suggestions** — AI detects fatigue, suggests rest
- [ ] **Screen Time Limits** — Optional daily caps with warnings

#### Integrations & Ecosystem
- [ ] **Google Drive Sync** — Cloud backup of notes and flashcards
- [ ] **Dropbox Integration** — Alternative cloud storage option
- [ ] **Zapier/IFTTT** — Automation workflows (e.g., auto-import emails)
- [ ] **Discord Bot** — Study group integration ("quiz me on torts")
- [ ] **Canvas/Blackboard** — Import assignments and syllabi
- [ ] **Grammarly API** — Real-time writing assistance in essays
- [ ] **Zotero/Mendeley** — Reference management for research papers

#### Mobile & Cross-Platform
- [ ] **Cloud Sync Infrastructure** — Central backend for multi-device support
- [ ] **iOS App** — Native iPhone/iPad app (React Native or Flutter)
- [ ] **Android App** — Native Android app (React Native or Flutter)
- [ ] **Web App** — Browser-based version for Chromebooks/Linux
- [ ] **Offline Mode** — Full functionality without internet on mobile
- [ ] **Cross-Device Continuity** — Pick up where you left off on any device

---

## 5. Quarterly Prioritization Framework

### Immediate (Q1 2026)
1. Multi-subject organization (LOW effort, HIGH impact)
2. Reverse cards (LOW effort, MEDIUM impact)
3. Cloze deletion cards (MEDIUM effort, HIGH impact)
4. Daily goals (LOW effort, HIGH impact)

### Short-Term (Q2 2026)
5. Gamification — XP, achievements (MEDIUM effort, VERY HIGH impact)
6. Bidirectional links (MEDIUM effort, HIGH impact)
7. Enhanced analytics (MEDIUM effort, MEDIUM impact)
8. Templates (LOW effort, MEDIUM impact)

### Mid-Term (Q3–Q4 2026)
9. PDF annotation (HIGH effort, HIGH impact)
10. AI chat tutor (MEDIUM effort, HIGH impact)
11. Audio cards (MEDIUM effort, MEDIUM impact)
12. Calendar planning (MEDIUM effort, MEDIUM impact)

### Long-Term (2027+)
13. Image occlusion (HIGH effort, HIGH impact)
14. Collaboration features (HIGH effort, HIGH impact — requires cloud)
15. Mobile apps (VERY HIGH effort, VERY HIGH impact)
16. Import/export ecosystem (MEDIUM-HIGH effort, MEDIUM impact)

### Phased Strategic Roadmap

| Phase | Timeframe | Goal | Key Deliverables | Expected Impact |
|-------|-----------|------|-------------------|-----------------|
| **Phase 1** | Months 1–3 | Expand user base beyond legal | Advanced card types, multi-subject org, templates | +300% addressable market |
| **Phase 2** | Months 4–6 | Increase retention & DAU | Gamification, enhanced analytics, AI chat tutor | +50% retention, +80% session length |
| **Phase 3** | Months 7–9 | Enable social/group study | Shared decks, note bundles, comments | +40% word-of-mouth growth |
| **Phase 4** | Months 10–12 | Go cross-platform | Cloud sync, iOS/Android apps, web app | +500% total addressable market |

---

## 6. Multi-Audience Reading Paths

### If You Have 5 Minutes
→ Read Section 5 (Quarterly Framework) for priorities and effort/impact ratings

### If You Have 15 Minutes
→ Read Section 1 (User Scenarios) to understand who benefits and how, then Section 5

### If You Have 1 Hour
→ Read the full document: Scenarios → Implementation Notes → Checklist → Roadmap

### By Role

| Role | Start Here | Then Read | Action Items |
|------|-----------|-----------|-------------|
| **Product Manager** | Section 1 (Scenarios) | Section 5 (Roadmap) | Prioritize based on user impact |
| **Developer** | Section 2 (Implementation) | Section 4 (Checklist) | Pick features, reference libraries |
| **Stakeholder** | Section 5 (Framework) | Section 1 (Scenarios) | Approve quarterly plan |
| **Designer** | Section 1 (Scenarios) | Section 3 (Unique Features) | Prototype new UIs |

---

## 7. Research Methodology

### Data Sources
1. Complete codebase analysis (study_app + study_app_v2)
2. Database schema review (10 tables, 50+ fields)
3. UI/UX evaluation (9 tabs, 100+ features)
4. Competitive intelligence (8 major competitors)
5. Market research (student populations, use-cases)
6. Feature gap analysis (vs. category leaders)

### Competitors Analyzed
Anki (20+ years, flashcard king) · Notion (real-time collaboration) · RemNote (knowledge graphs) · Quizlet (700M+ study sets) · Obsidian (plugin ecosystem) · Forest (gamified focus) · Grammarly (AI writing) · Khan Academy (interactive learning)

### Quick Stats
- **Total Features Identified:** 100+
- **High Priority:** 31 features (4 categories)
- **Medium Priority:** 39 features (5 categories)
- **Nice-to-Have:** 38 features (8 categories)
- **Estimated to 10× Market:** Phases 1–3 (Advanced cards + Gamification + Organization)
- **Estimated to 100× Market:** Phase 4+ (Mobile apps + Cloud sync)

### Checklist Usage Guide
This checklist is a **living document** for tracking feature development:
1. Mark items as complete: `- [x] Feature name`
2. Add implementation notes or PR numbers
3. Update priority as user feedback comes in
4. Archive completed phases to separate document
