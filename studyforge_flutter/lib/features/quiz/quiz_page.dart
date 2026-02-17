import 'package:flutter/material.dart';

import '../../core/app_controller.dart';

class QuizPage extends StatefulWidget {
  const QuizPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<QuizPage> createState() => _QuizPageState();
}

class _QuizPageState extends State<QuizPage> {
  final promptController = TextEditingController();
  String output = '';
  bool loading = false;

  @override
  void dispose() {
    promptController.dispose();
    super.dispose();
  }

  Future<void> _generateQuiz() async {
    final notes = await widget.controller.database.getNotes();
    if (notes.isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Add notes before generating quiz.')));
      return;
    }

    setState(() {
      loading = true;
    });

    try {
      final noteBlock = notes.take(6).map((n) => '${n.title}\n${n.content}').join('\n\n');
      final userInstruction = promptController.text.trim();
      final prompt =
          'Generate 5 multiple-choice study questions with 4 options each and provide answer key. '
          'Keep output concise.\n\nNotes:\n$noteBlock\n\nAdditional instruction: $userInstruction';

      final result = await widget.controller.ai.generateText(
        provider: widget.controller.config.aiProvider,
        apiKey: widget.controller.config.apiKey,
        model: widget.controller.config.model,
        prompt: prompt,
      );
      await widget.controller.database.incrementDailyStat('quiz_questions_answered', 5);
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
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Quiz failed: $e')));
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
            controller: promptController,
            maxLines: 2,
            decoration: const InputDecoration(
              labelText: 'Optional quiz focus (e.g., torts, civ pro, anatomy)',
            ),
          ),
          const SizedBox(height: 8),
          FilledButton.icon(
            onPressed: loading ? null : _generateQuiz,
            icon: const Icon(Icons.auto_awesome),
            label: Text(loading ? 'Generating...' : 'Generate Quiz'),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: SingleChildScrollView(
              child: SelectableText(
                output.isEmpty
                    ? 'Generated quiz output appears here. Configure API key in Settings first.'
                    : output,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
