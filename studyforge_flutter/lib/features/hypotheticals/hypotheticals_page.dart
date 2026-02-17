import 'package:flutter/material.dart';

import '../../core/app_controller.dart';

class HypotheticalsPage extends StatefulWidget {
  const HypotheticalsPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<HypotheticalsPage> createState() => _HypotheticalsPageState();
}

class _HypotheticalsPageState extends State<HypotheticalsPage> {
  final topicController = TextEditingController();
  final answerController = TextEditingController();

  String scenario = '';
  String grading = '';
  bool generating = false;
  bool gradingLoading = false;

  @override
  void dispose() {
    topicController.dispose();
    answerController.dispose();
    super.dispose();
  }

  Future<void> _generateScenario() async {
    final topic = topicController.text.trim();
    if (topic.isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Enter a topic first.')));
      return;
    }

    setState(() {
      generating = true;
    });

    try {
      final result = await widget.controller.ai.generateText(
        provider: widget.controller.config.aiProvider,
        apiKey: widget.controller.config.apiKey,
        model: widget.controller.config.model,
        prompt:
            'Generate a realistic legal hypothetical scenario about: $topic. Include key facts and 3 analytical questions.',
      );
      if (!mounted) {
        return;
      }
      setState(() {
        scenario = result;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Scenario generation failed: $e')));
    } finally {
      if (mounted) {
        setState(() {
          generating = false;
        });
      }
    }
  }

  Future<void> _gradeAnswer() async {
    final response = answerController.text.trim();
    if (scenario.isEmpty || response.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Generate scenario and provide response first.')),
      );
      return;
    }

    setState(() {
      gradingLoading = true;
    });

    try {
      final result = await widget.controller.ai.generateText(
        provider: widget.controller.config.aiProvider,
        apiKey: widget.controller.config.apiKey,
        model: widget.controller.config.model,
        prompt:
            'Grade this hypothetical response. Return score, legal reasoning analysis, and concise improvement suggestions.\n\nScenario:\n$scenario\n\nResponse:\n$response',
      );
      if (!mounted) {
        return;
      }
      setState(() {
        grading = result;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Grading failed: $e')));
    } finally {
      if (mounted) {
        setState(() {
          gradingLoading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        TextField(
          controller: topicController,
          decoration: const InputDecoration(labelText: 'Hypothetical topic'),
        ),
        const SizedBox(height: 8),
        FilledButton.icon(
          onPressed: generating ? null : _generateScenario,
          icon: const Icon(Icons.auto_awesome),
          label: Text(generating ? 'Generating...' : 'Generate Hypothetical'),
        ),
        const SizedBox(height: 12),
        SelectableText(scenario.isEmpty ? 'Scenario output appears here.' : scenario),
        const Divider(height: 28),
        TextField(
          controller: answerController,
          maxLines: 6,
          decoration: const InputDecoration(
            border: OutlineInputBorder(),
            labelText: 'Your response',
            alignLabelWithHint: true,
          ),
        ),
        const SizedBox(height: 8),
        FilledButton.icon(
          onPressed: gradingLoading ? null : _gradeAnswer,
          icon: const Icon(Icons.gavel),
          label: Text(gradingLoading ? 'Grading...' : 'Grade Response'),
        ),
        const SizedBox(height: 12),
        SelectableText(grading.isEmpty ? 'Feedback appears here.' : grading),
      ],
    );
  }
}
