import 'dart:async';

import 'package:flutter/material.dart';

import '../../core/app_controller.dart';
import '../../core/models.dart';

class PomodoroPage extends StatefulWidget {
  const PomodoroPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<PomodoroPage> createState() => _PomodoroPageState();
}

class _PomodoroPageState extends State<PomodoroPage> {
  Timer? timer;
  int remainingSeconds = 0;
  bool running = false;
  String currentType = 'work';

  @override
  void initState() {
    super.initState();
    remainingSeconds = widget.controller.config.pomodoroWorkMinutes * 60;
  }

  @override
  void dispose() {
    timer?.cancel();
    super.dispose();
  }

  void _start() {
    if (running) {
      return;
    }
    setState(() {
      running = true;
    });

    timer = Timer.periodic(const Duration(seconds: 1), (t) async {
      if (remainingSeconds <= 0) {
        t.cancel();
        setState(() {
          running = false;
        });
        await _logCompletedSession();
        return;
      }
      setState(() {
        remainingSeconds -= 1;
      });
    });
  }

  void _pause() {
    timer?.cancel();
    setState(() {
      running = false;
    });
  }

  Future<void> _logCompletedSession() async {
    final duration = currentType == 'work'
        ? widget.controller.config.pomodoroWorkMinutes
        : widget.controller.config.pomodoroShortBreak;
    await widget.controller.database.logPomodoro(
      PomodoroSession(
        sessionType: currentType,
        durationMinutes: duration,
        completed: true,
        startedAt: DateTime.now().subtract(Duration(minutes: duration)),
        finishedAt: DateTime.now(),
      ),
    );
    await widget.controller.database.incrementDailyStat('pomodoro_sessions', 1);
    await widget.controller.database.incrementDailyStat('study_minutes', duration);
    if (!mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('${currentType.toUpperCase()} session completed.')),
    );
  }

  void _switchType(String type) {
    _pause();
    final config = widget.controller.config;
    final mins = switch (type) {
      'work' => config.pomodoroWorkMinutes,
      'short_break' => config.pomodoroShortBreak,
      _ => config.pomodoroLongBreak,
    };
    setState(() {
      currentType = type;
      remainingSeconds = mins * 60;
    });
  }

  @override
  Widget build(BuildContext context) {
    final mm = (remainingSeconds ~/ 60).toString().padLeft(2, '0');
    final ss = (remainingSeconds % 60).toString().padLeft(2, '0');

    return Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(value: 'work', label: Text('Work')),
              ButtonSegment(value: 'short_break', label: Text('Short Break')),
              ButtonSegment(value: 'long_break', label: Text('Long Break')),
            ],
            selected: {currentType},
            onSelectionChanged: (set) => _switchType(set.first),
          ),
          const SizedBox(height: 24),
          Expanded(
            child: Center(
              child: Text(
                '$mm:$ss',
                style: const TextStyle(fontSize: 72, fontWeight: FontWeight.bold),
              ),
            ),
          ),
          Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              FilledButton.icon(
                onPressed: _start,
                icon: const Icon(Icons.play_arrow),
                label: const Text('Start'),
              ),
              const SizedBox(width: 12),
              OutlinedButton.icon(
                onPressed: _pause,
                icon: const Icon(Icons.pause),
                label: const Text('Pause'),
              ),
            ],
          ),
        ],
      ),
    );
  }
}
