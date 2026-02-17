import 'package:flutter/material.dart';

import 'core/ai_service.dart';
import 'core/app_controller.dart';
import 'core/config_service.dart';
import 'core/database_service.dart';
import 'core/srs_service.dart';
import 'features/dashboard/dashboard_page.dart';
import 'features/essays/essays_page.dart';
import 'features/flashcards/flashcards_page.dart';
import 'features/hypotheticals/hypotheticals_page.dart';
import 'features/notes/notes_page.dart';
import 'features/participation/participation_page.dart';
import 'features/pomodoro/pomodoro_page.dart';
import 'features/quiz/quiz_page.dart';
import 'features/settings/settings_page.dart';

class StudyForgeApp extends StatefulWidget {
  const StudyForgeApp({super.key});

  @override
  State<StudyForgeApp> createState() => _StudyForgeAppState();
}

class _StudyForgeAppState extends State<StudyForgeApp> {
  late final AppController controller;
  bool loading = true;
  int currentIndex = 0;

  @override
  void initState() {
    super.initState();
    controller = AppController(
      database: DatabaseService(),
      configService: ConfigService(),
      ai: AiService(),
      srs: SrsService(),
    );
    controller.initialize().then((_) {
      if (!mounted) {
        return;
      }
      setState(() {
        loading = false;
      });
    });
  }

  @override
  Widget build(BuildContext context) {
    final themeMode = controller.config.theme == 'dark' ? ThemeMode.dark : ThemeMode.light;

    return MaterialApp(
      title: 'StudyForge Flutter',
      debugShowCheckedModeBanner: false,
      themeMode: themeMode,
      theme: ThemeData.light(useMaterial3: true),
      darkTheme: ThemeData.dark(useMaterial3: true),
      home: loading
          ? const Scaffold(body: Center(child: CircularProgressIndicator()))
          : Scaffold(
              appBar: AppBar(title: const Text('StudyForge')),
              body: IndexedStack(
                index: currentIndex,
                children: [
                  DashboardPage(controller: controller),
                  NotesPage(controller: controller),
                  FlashcardsPage(controller: controller),
                  QuizPage(controller: controller),
                  PomodoroPage(controller: controller),
                  EssaysPage(controller: controller),
                  HypotheticalsPage(controller: controller),
                  ParticipationPage(controller: controller),
                  SettingsPage(
                    controller: controller,
                    onConfigUpdated: () => setState(() {}),
                  ),
                ],
              ),
              bottomNavigationBar: NavigationBar(
                selectedIndex: currentIndex,
                onDestinationSelected: (index) {
                  setState(() {
                    currentIndex = index;
                  });
                },
                destinations: const [
                  NavigationDestination(icon: Icon(Icons.dashboard), label: 'Dashboard'),
                  NavigationDestination(icon: Icon(Icons.note_alt), label: 'Notes'),
                  NavigationDestination(icon: Icon(Icons.style), label: 'Cards'),
                  NavigationDestination(icon: Icon(Icons.quiz), label: 'Quiz'),
                  NavigationDestination(icon: Icon(Icons.timer), label: 'Pomodoro'),
                  NavigationDestination(icon: Icon(Icons.edit_note), label: 'Essays'),
                  NavigationDestination(icon: Icon(Icons.gavel), label: 'Hypos'),
                  NavigationDestination(icon: Icon(Icons.record_voice_over), label: 'Class'),
                  NavigationDestination(icon: Icon(Icons.settings), label: 'Settings'),
                ],
              ),
            ),
    );
  }
}
