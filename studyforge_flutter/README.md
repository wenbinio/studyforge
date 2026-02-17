# StudyForge Flutter (Full Rebuild Track)

This folder contains a Flutter rebuild of StudyForge in a new top-level project.

## Current scope

The Flutter app includes all major product modules as native tabs:

- Dashboard
- Notes
- Flashcards (with SM-2 scheduling)
- Quiz
- Pomodoro
- Essays
- Hypotheticals
- Class Participation
- Settings

Core architecture ported from Python app:

- SQLite local-first schema for notes, flashcards, review logs, pomodoro sessions, daily stats, essays, rubrics, hypotheticals, participation questions
- SM-2 scheduling logic in `lib/core/srs_service.dart`
- AI provider key detection + settings persistence in `lib/core/config_service.dart`
- Multi-provider AI HTTP client in `lib/core/ai_service.dart`

## Setup

1. Install Flutter SDK (stable channel)
2. From this directory:

```bash
cd /home/runner/work/studyforge/studyforge/studyforge_flutter
flutter pub get
```

If you need generated platform folders in a fresh environment:

```bash
flutter create --platforms=android .
```

(When prompted, keep existing `lib/` and `pubspec.yaml` files.)

## Run

```bash
flutter run
```

## Build Android APK

```bash
flutter build apk --release
```

Output APK:

`build/app/outputs/flutter-apk/app-release.apk`

## Test

```bash
flutter test
```
