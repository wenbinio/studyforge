# StudyForge Flutter Parity Review vs Desktop `.exe`

Date: 2026-02-17

## Verdict

`studyforge_flutter` **does not yet fulfill all functionality** of the original desktop app (`study_app` / `.exe`).

It currently covers the major module surface (Dashboard, Notes, Flashcards, Quiz, Pomodoro, Essays, Hypotheticals, Participation, Settings), but several desktop capabilities are missing or simplified.

## Parity Matrix

| Area | Desktop (`study_app`) | Flutter (`studyforge_flutter`) | Status |
|---|---|---|---|
| App module coverage | `ui/app.py` includes Dashboard, Pomodoro, Flashcards, Notes, Quiz, Hypotheticals, Essays, Participation, Settings | `lib/app.dart` has matching tabs in bottom nav | ✅ High-level parity |
| Notes import formats | `ui/notes.py` `extract_text_from_file()` handles `.txt`, `.md`, `.pdf`, `.docx` | `features/notes/notes_page.dart` supports manual note entry only | ❌ Missing |
| Notes export | `ui/notes.py` `_export_note()` and `_export_docx()` | No export action in `features/notes/notes_page.dart` | ❌ Missing |
| Notes find/replace | `ui/notes.py` `_show_find_replace()` | No find/replace UI in notes page | ❌ Missing |
| Notes navigator / preview / focus-mode editor tooling | `ui/notes.py` includes navigator + preview/focus-mode functions | Notes page is basic editor/list only | ❌ Missing |
| Flashcards review (SM-2) | Review with SM-2 in `ui/flashcards.py` | SM-2 review in `features/flashcards/flashcards_page.dart` + `core/srs_service.dart` | ✅ Parity |
| Flashcards interleaved review | `ui/flashcards.py` `start_interleaved_review()` | No interleaved review mode in Flutter page | ❌ Missing |
| Flashcards AI generation from notes | `ui/flashcards.py` `show_ai_generate_dialog()` | No AI card-generation flow in Flutter flashcards page | ❌ Missing |
| Quiz single + interleaved | `ui/quiz.py` supports single and interleaved multi-note quiz generation | `features/quiz/quiz_page.dart` generates one quiz from top notes batch only | ⚠️ Partial |
| Essay rubric workflow | `ui/essays.py` includes rubric upload/management (`extract_rubric_text`, rubric selection) | `features/essays/essays_page.dart` has prompt+draft grading only | ❌ Missing |
| Settings connection test UX | Desktop settings has `_test_connection()` action and live status | Flutter settings saves config but no explicit connection test button | ⚠️ Partial |

## What is already strong in Flutter

- Local SQLite + SM-2 core foundation is present (`lib/core/database_service.dart`, `lib/core/srs_service.dart`).
- AI-powered flows for quiz/essays/hypotheticals/participation are implemented.
- Core study loop (notes -> cards -> review -> stats -> pomodoro) exists.

## Validation Notes

I attempted to run the existing Flutter checks in this environment:

```bash
cd /home/runner/work/studyforge/studyforge/studyforge_flutter
flutter --version
flutter pub get
flutter analyze
flutter test
```

But `flutter` is not installed in the sandbox (`bash: flutter: command not found`), so parity assessment here is based on static code inspection.

## Priority Gaps to Reach Desktop Parity

1. **Notes power features**: import (`pdf/docx`), export, find/replace, preview/navigator/focus-mode.
2. **Flashcards advanced modes**: AI generate from note + interleaved review.
3. **Essay rubric support**: rubric upload/selection and rubric-aware grading prompt.
4. **Quiz interleaved mode**: multi-note user selection and topic-aware result handling.
5. **Settings test-connection UX**: explicit key/model/provider test action.
