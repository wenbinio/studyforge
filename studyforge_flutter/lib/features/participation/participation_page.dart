import 'package:flutter/material.dart';

import '../../core/app_controller.dart';

class ParticipationPage extends StatefulWidget {
  const ParticipationPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<ParticipationPage> createState() => _ParticipationPageState();
}

class _ParticipationPageState extends State<ParticipationPage> {
  final topicController = TextEditingController();
  String category = 'cold-call prep';
  String output = '';
  bool loading = false;

  static const categories = [
    'cold-call prep',
    'counterarguments',
    'policy angle',
    'fact pattern distinctions',
    'exam issue spotting',
  ];

  @override
  void dispose() {
    topicController.dispose();
    super.dispose();
  }

  Future<void> _generateQuestions() async {
    final topic = topicController.text.trim();
    if (topic.isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Enter a topic first.')));
      return;
    }

    setState(() {
      loading = true;
    });

    try {
      final result = await widget.controller.ai.generateText(
        provider: widget.controller.config.aiProvider,
        apiKey: widget.controller.config.apiKey,
        model: widget.controller.config.model,
        prompt:
            'Generate 8 class participation questions for topic "$topic" focused on category "$category". Include concise model answers.',
      );
      if (!mounted) {
        return;
      }
      setState(() {
        output = result;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text('Generation failed: $e')));
    } finally {
      if (mounted) {
        setState(() {
          loading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(
            controller: topicController,
            decoration: const InputDecoration(labelText: 'Topic / Case'),
          ),
          const SizedBox(height: 8),
          DropdownButtonFormField<String>(
            value: category,
            items: categories
                .map((c) => DropdownMenuItem<String>(value: c, child: Text(c)))
                .toList(),
            onChanged: (value) {
              if (value == null) {
                return;
              }
              setState(() {
                category = value;
              });
            },
            decoration: const InputDecoration(labelText: 'Question style'),
          ),
          const SizedBox(height: 8),
          FilledButton.icon(
            onPressed: loading ? null : _generateQuestions,
            icon: const Icon(Icons.auto_awesome),
            label: Text(loading ? 'Generating...' : 'Generate Questions'),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: SingleChildScrollView(
              child: SelectableText(
                output.isEmpty ? 'Generated participation questions appear here.' : output,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
