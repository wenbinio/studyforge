import 'package:flutter/material.dart';

import '../../core/app_controller.dart';

class EssaysPage extends StatefulWidget {
  const EssaysPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<EssaysPage> createState() => _EssaysPageState();
}

class _EssaysPageState extends State<EssaysPage> {
  final promptController = TextEditingController();
  final draftController = TextEditingController();
  String feedback = '';
  bool loading = false;

  @override
  void dispose() {
    promptController.dispose();
    draftController.dispose();
    super.dispose();
  }

  Future<void> _gradeEssay() async {
    final prompt = promptController.text.trim();
    final draft = draftController.text.trim();
    if (prompt.isEmpty || draft.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Prompt and essay draft are required.')),
      );
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
            'Grade this essay and return: score, strengths, weaknesses, and revision plan.\n\nPrompt:\n$prompt\n\nEssay:\n$draft',
      );
      if (!mounted) {
        return;
      }
      setState(() {
        feedback = result;
      });
    } catch (e) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('Grading failed: $e')));
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
            maxLines: 3,
            decoration: const InputDecoration(labelText: 'Essay Prompt'),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: TextField(
              controller: draftController,
              maxLines: null,
              expands: true,
              decoration: const InputDecoration(
                labelText: 'Essay Draft',
                border: OutlineInputBorder(),
                alignLabelWithHint: true,
              ),
            ),
          ),
          const SizedBox(height: 8),
          FilledButton.icon(
            onPressed: loading ? null : _gradeEssay,
            icon: const Icon(Icons.auto_awesome),
            label: Text(loading ? 'Grading...' : 'Grade with AI'),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: SingleChildScrollView(
              child: SelectableText(feedback.isEmpty ? 'AI feedback appears here.' : feedback),
            ),
          )
        ],
      ),
    );
  }
}
