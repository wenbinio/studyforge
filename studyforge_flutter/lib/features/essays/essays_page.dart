import 'package:flutter/material.dart';

import '../../core/app_controller.dart';
import '../../core/essay_grading.dart';
import '../../core/models.dart';

class EssaysPage extends StatefulWidget {
  const EssaysPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<EssaysPage> createState() => _EssaysPageState();
}

class _EssaysPageState extends State<EssaysPage> {
  final promptController = TextEditingController();
  final draftController = TextEditingController();
  final rubricNameController = TextEditingController();
  final rubricContentController = TextEditingController();
  List<Rubric> rubrics = [];
  int? selectedRubricId;
  String feedback = '';
  bool loading = false;

  @override
  void initState() {
    super.initState();
    _loadRubrics();
  }

  @override
  void dispose() {
    promptController.dispose();
    draftController.dispose();
    rubricNameController.dispose();
    rubricContentController.dispose();
    super.dispose();
  }

  Future<void> _loadRubrics() async {
    final fetched = await widget.controller.database.getRubrics();
    if (!mounted) {
      return;
    }
    setState(() {
      rubrics = fetched;
      selectedRubricId ??= fetched.isEmpty ? null : fetched.first.id;
    });
  }

  Future<void> _saveRubric() async {
    final name = rubricNameController.text.trim();
    final content = rubricContentController.text.trim();
    if (name.isEmpty || content.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Rubric name and content are required.')),
      );
      return;
    }
    await widget.controller.database.addRubric(
      Rubric(
        id: null,
        name: name,
        content: content,
        createdAt: DateTime.now(),
      ),
    );
    rubricNameController.clear();
    rubricContentController.clear();
    await _loadRubrics();
    if (!mounted) {
      return;
    }
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Rubric saved.')),
    );
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
      String rubricText = '';
      if (selectedRubricId != null) {
        final rubric = await widget.controller.database.getRubric(selectedRubricId!);
        rubricText = rubric?.content ?? '';
      }
      final result = await widget.controller.ai.generateText(
        provider: widget.controller.config.aiProvider,
        apiKey: widget.controller.config.apiKey,
        model: widget.controller.config.model,
        prompt: buildEssayGradingPrompt(
          prompt: prompt,
          draft: draft,
          rubricText: rubricText,
        ),
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
          Text('Rubric (optional)', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          DropdownButtonFormField<int?>(
            value: selectedRubricId,
            items: [
              const DropdownMenuItem<int?>(value: null, child: Text('(none)')),
              ...rubrics.where((r) => r.id != null).map(
                    (rubric) => DropdownMenuItem<int?>(
                      value: rubric.id,
                      child: Text(rubric.name, overflow: TextOverflow.ellipsis),
                    ),
                  )
            ],
            onChanged: (value) {
              setState(() {
                selectedRubricId = value;
              });
            },
            decoration: const InputDecoration(labelText: 'Selected rubric'),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: rubricNameController,
            decoration: const InputDecoration(labelText: 'New rubric name'),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: rubricContentController,
            maxLines: 3,
            decoration: const InputDecoration(
              border: OutlineInputBorder(),
              alignLabelWithHint: true,
              labelText: 'New rubric content',
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              FilledButton.icon(
                onPressed: _saveRubric,
                icon: const Icon(Icons.save),
                label: const Text('Save Rubric'),
              ),
              const SizedBox(width: 8),
              OutlinedButton.icon(
                onPressed: _loadRubrics,
                icon: const Icon(Icons.refresh),
                label: const Text('Refresh Rubrics'),
              ),
            ],
          ),
          const SizedBox(height: 8),
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
