import 'package:flutter/material.dart';

import '../../core/app_controller.dart';
import '../../core/models.dart';
import '../../core/settings_connection.dart';

class SettingsPage extends StatefulWidget {
  const SettingsPage({
    super.key,
    required this.controller,
    required this.onConfigUpdated,
  });

  final AppController controller;
  final VoidCallback onConfigUpdated;

  @override
  State<SettingsPage> createState() => _SettingsPageState();
}

class _SettingsPageState extends State<SettingsPage> {
  late final TextEditingController apiKeyController;
  late final TextEditingController modelController;
  late final TextEditingController workController;
  late final TextEditingController shortController;
  late final TextEditingController longController;
  late final TextEditingController sessionsBeforeLongController;
  late final TextEditingController newCardsLimitController;

  late String provider;
  late String theme;
  bool testingConnection = false;
  String connectionStatus = '';

  @override
  void initState() {
    super.initState();
    final config = widget.controller.config;
    provider = config.aiProvider;
    theme = config.theme;
    apiKeyController = TextEditingController(text: config.apiKey);
    modelController = TextEditingController(text: config.model);
    workController = TextEditingController(text: '${config.pomodoroWorkMinutes}');
    shortController = TextEditingController(text: '${config.pomodoroShortBreak}');
    longController = TextEditingController(text: '${config.pomodoroLongBreak}');
    sessionsBeforeLongController =
        TextEditingController(text: '${config.pomodoroSessionsBeforeLongBreak}');
    newCardsLimitController = TextEditingController(text: '${config.dailyNewCardsLimit}');
  }

  @override
  void dispose() {
    apiKeyController.dispose();
    modelController.dispose();
    workController.dispose();
    shortController.dispose();
    longController.dispose();
    sessionsBeforeLongController.dispose();
    newCardsLimitController.dispose();
    super.dispose();
  }

  Future<void> _save() async {
    final detected = widget.controller.configService.detectProviderFromKey(
      apiKeyController.text.trim(),
    );

    final parsedWork = int.tryParse(workController.text.trim());
    final parsedShort = int.tryParse(shortController.text.trim());
    final parsedLong = int.tryParse(longController.text.trim());
    final parsedSessions = int.tryParse(sessionsBeforeLongController.text.trim());
    final parsedNewCards = int.tryParse(newCardsLimitController.text.trim());

    if (parsedWork == null ||
        parsedShort == null ||
        parsedLong == null ||
        parsedSessions == null ||
        parsedNewCards == null) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Numeric settings are invalid.')));
      return;
    }

    final updated = AppConfig(
      aiProvider: detected,
      apiKey: apiKeyController.text.trim(),
      model: modelController.text.trim(),
      pomodoroWorkMinutes: parsedWork,
      pomodoroShortBreak: parsedShort,
      pomodoroLongBreak: parsedLong,
      pomodoroSessionsBeforeLongBreak: parsedSessions,
      dailyNewCardsLimit: parsedNewCards,
      theme: theme,
    );

    await widget.controller.saveConfig(updated);
    if (!mounted) {
      return;
    }
    setState(() {
      provider = detected;
    });
    widget.onConfigUpdated();
    ScaffoldMessenger.of(context)
        .showSnackBar(const SnackBar(content: Text('Settings saved.')));
  }

  Future<void> _testConnection() async {
    final key = apiKeyController.text.trim();
    if (key.isEmpty) {
      setState(() {
        connectionStatus = '⚠️ Enter an API key first.';
      });
      return;
    }
    final detected = widget.controller.configService.detectProviderFromKey(key);
    final model = modelController.text.trim();

    setState(() {
      testingConnection = true;
      connectionStatus = 'Testing connection...';
    });
    try {
      final result = await widget.controller.ai.generateText(
        provider: detected,
        apiKey: key,
        model: model,
        prompt: buildConnectionTestPrompt(),
      );
      if (!mounted) {
        return;
      }
      setState(() {
        provider = detected;
        connectionStatus = '🟢 Connected: $detected / ${model.isEmpty ? "(default model)" : model}';
      });
      if (result.trim().isEmpty) {
        setState(() {
          connectionStatus = '🟢 Connected (empty response from model).';
        });
      }
    } catch (e) {
      if (!mounted) {
        return;
      }
      setState(() {
        connectionStatus = '🔴 Connection failed: $e';
      });
    } finally {
      if (mounted) {
        setState(() {
          testingConnection = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        const Text('AI Settings', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        TextField(
          controller: apiKeyController,
          decoration: const InputDecoration(labelText: 'API Key'),
          obscureText: true,
          onChanged: (value) {
            setState(() {
              provider = widget.controller.configService.detectProviderFromKey(value.trim());
            });
          },
        ),
        const SizedBox(height: 8),
        Text('Detected provider: $provider'),
        const SizedBox(height: 8),
        TextField(
          controller: modelController,
          decoration: const InputDecoration(labelText: 'Model'),
        ),
        const SizedBox(height: 8),
        FilledButton.icon(
          onPressed: testingConnection ? null : _testConnection,
          icon: const Icon(Icons.wifi_tethering),
          label: Text(testingConnection ? 'Testing...' : 'Test Connection'),
        ),
        if (connectionStatus.isNotEmpty) ...[
          const SizedBox(height: 8),
          Text(connectionStatus),
        ],
        const Divider(height: 28),
        const Text('Pomodoro', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        TextField(
          controller: workController,
          decoration: const InputDecoration(labelText: 'Work minutes'),
          keyboardType: TextInputType.number,
        ),
        const SizedBox(height: 8),
        TextField(
          controller: shortController,
          decoration: const InputDecoration(labelText: 'Short break minutes'),
          keyboardType: TextInputType.number,
        ),
        const SizedBox(height: 8),
        TextField(
          controller: longController,
          decoration: const InputDecoration(labelText: 'Long break minutes'),
          keyboardType: TextInputType.number,
        ),
        const SizedBox(height: 8),
        TextField(
          controller: sessionsBeforeLongController,
          decoration: const InputDecoration(labelText: 'Sessions before long break'),
          keyboardType: TextInputType.number,
        ),
        const Divider(height: 28),
        const Text('Study', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        const SizedBox(height: 8),
        TextField(
          controller: newCardsLimitController,
          decoration: const InputDecoration(labelText: 'Daily new card limit'),
          keyboardType: TextInputType.number,
        ),
        const SizedBox(height: 8),
        DropdownButtonFormField<String>(
          value: theme,
          items: const [
            DropdownMenuItem(value: 'dark', child: Text('Dark')),
            DropdownMenuItem(value: 'light', child: Text('Light')),
          ],
          onChanged: (value) {
            if (value == null) {
              return;
            }
            setState(() {
              theme = value;
            });
          },
          decoration: const InputDecoration(labelText: 'Theme'),
        ),
        const SizedBox(height: 12),
        FilledButton.icon(
          onPressed: _save,
          icon: const Icon(Icons.save),
          label: const Text('Save Settings'),
        ),
      ],
    );
  }
}
