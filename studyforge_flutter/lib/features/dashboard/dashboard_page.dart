import 'package:flutter/material.dart';

import '../../core/app_controller.dart';

class DashboardPage extends StatefulWidget {
  const DashboardPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<DashboardPage> createState() => _DashboardPageState();
}

class _DashboardPageState extends State<DashboardPage> {
  int streak = 0;
  int dueCards = 0;
  int cardsReviewedToday = 0;
  int pomodorosToday = 0;
  int studyMinutesToday = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    final stats = await widget.controller.database.todayStats();
    final fetchedStreak = await widget.controller.database.currentStreak();
    final fetchedDue = await widget.controller.database.dueCardCount();
    if (!mounted) {
      return;
    }
    setState(() {
      streak = fetchedStreak;
      dueCards = fetchedDue;
      cardsReviewedToday = stats?.cardsReviewed ?? 0;
      pomodorosToday = stats?.pomodoroSessions ?? 0;
      studyMinutesToday = stats?.studyMinutes ?? 0;
    });
  }

  @override
  Widget build(BuildContext context) {
    return RefreshIndicator(
      onRefresh: _load,
      child: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Wrap(
            spacing: 12,
            runSpacing: 12,
            children: [
              _statCard('Current Streak', '$streak days', Icons.local_fire_department),
              _statCard('Cards Due', '$dueCards', Icons.pending_actions),
              _statCard('Reviewed Today', '$cardsReviewedToday', Icons.style),
              _statCard('Pomodoros', '$pomodorosToday', Icons.timer),
              _statCard('Study Minutes', '$studyMinutesToday', Icons.schedule),
            ],
          ),
          const SizedBox(height: 20),
          Text(
            'All-in-one study workflow',
            style: Theme.of(context).textTheme.titleMedium,
          ),
          const SizedBox(height: 8),
          const Text(
            'Import notes → generate cards/quizzes with AI → review with SM-2 → track progress with Pomodoro and daily stats.',
          ),
        ],
      ),
    );
  }

  Widget _statCard(String title, String value, IconData icon) {
    return SizedBox(
      width: 180,
      child: Card(
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Icon(icon),
              const SizedBox(height: 8),
              Text(value, style: const TextStyle(fontSize: 20, fontWeight: FontWeight.bold)),
              Text(title),
            ],
          ),
        ),
      ),
    );
  }
}
