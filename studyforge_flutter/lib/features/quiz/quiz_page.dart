import 'package:flutter/material.dart';

import '../../core/app_controller.dart';
import '../../core/models.dart';
import '../../core/quiz_generation.dart';
import '../../core/quiz_results.dart';

class QuizPage extends StatefulWidget {
  const QuizPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<QuizPage> createState() => _QuizPageState();
}

class _QuizPageState extends State<QuizPage> {
  final promptController = TextEditingController();
  List<Note> notes = [];
  bool interleavedMode = false;
  int? selectedNoteId;
  final Set<int> selectedNoteIds = <int>{};
  String output = '';
  bool loading = false;
  Map<String, int> topicBreakdown = const {};

  @override
  void initState() {
    super.initState();
    _loadNotes();
  }

  @override
  void dispose() {
    promptController.dispose();
    super.dispose();
  }

  Future<void> _loadNotes() async {
    final fetched = await widget.controller.database.getNotes();
    if (!mounted) {
      return;
    }
    setState(() {
      notes = fetched;
      selectedNoteId ??= fetched.isEmpty ? null : fetched.first.id;
      if (selectedNoteIds.isEmpty) {
        for (final note in fetched.take(2)) {
          if (note.id != null) {
            selectedNoteIds.add(note.id!);
          }
        }
      }
    });
  }

  Future<void> _generateQuiz() async {
    if (notes.isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Add notes before generating quiz.')));
      return;
    }

    if (interleavedMode && selectedNoteIds.length < 2) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Select at least 2 notes for interleaved quiz.')),
      );
      return;
    }
    if (!interleavedMode && selectedNoteId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Select one note for quiz generation.')),
      );
      return;
    }

    setState(() {
      loading = true;
    });

    try {
      final pickedNotes = pickQuizNotes(
        allNotes: notes,
        interleaved: interleavedMode,
        selectedNoteId: selectedNoteId,
        selectedNoteIds: selectedNoteIds,
        maxNotes: 6,
      );
      if (pickedNotes.isEmpty) {
        throw Exception('No notes selected.');
      }
      final userInstruction = promptController.text.trim();
      final questionCount = interleavedMode ? 10 : 5;
      final prompt = buildQuizPrompt(
        notes: pickedNotes,
        userInstruction: userInstruction,
        interleaved: interleavedMode,
        questionCount: questionCount,
      );

      final result = await widget.controller.ai.generateText(
        provider: widget.controller.config.aiProvider,
        apiKey: widget.controller.config.apiKey,
        model: widget.controller.config.model,
        prompt: prompt,
      );
      await widget.controller.database.incrementDailyStat('quiz_questions_answered', questionCount);
      if (!mounted) {
        return;
      }
      setState(() {
        output = result;
        topicBreakdown = interleavedMode
            ? buildInterleavedTopicBreakdown(
                quizOutput: result,
                selectedNotes: pickedNotes,
              )
            : const {};
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
          SegmentedButton<bool>(
            segments: const [
              ButtonSegment<bool>(value: false, label: Text('Single')),
              ButtonSegment<bool>(value: true, label: Text('Interleaved')),
            ],
            selected: {interleavedMode},
            onSelectionChanged: (selection) {
              setState(() {
                interleavedMode = selection.first;
              });
            },
          ),
          const SizedBox(height: 8),
          if (!interleavedMode)
            DropdownButtonFormField<int>(
              value: selectedNoteId,
              items: notes
                  .where((n) => n.id != null)
                  .map(
                    (note) => DropdownMenuItem<int>(
                      value: note.id,
                      child: Text(note.title, overflow: TextOverflow.ellipsis),
                    ),
                  )
                  .toList(),
              onChanged: (value) {
                setState(() {
                  selectedNoteId = value;
                });
              },
              decoration: const InputDecoration(labelText: 'Source note'),
            )
          else
            SizedBox(
              height: 140,
              child: ListView(
                children: notes.where((n) => n.id != null).take(8).map((note) {
                  final id = note.id!;
                  return CheckboxListTile(
                    dense: true,
                    value: selectedNoteIds.contains(id),
                    title: Text(note.title, maxLines: 1, overflow: TextOverflow.ellipsis),
                    onChanged: (checked) {
                      setState(() {
                        if (checked == true) {
                          selectedNoteIds.add(id);
                        } else {
                          selectedNoteIds.remove(id);
                        }
                      });
                    },
                  );
                }).toList(),
              ),
            ),
          const SizedBox(height: 8),
          TextField(
            controller: promptController,
            maxLines: 2,
            decoration: const InputDecoration(
              labelText: 'Optional quiz focus (e.g., torts, civ pro, anatomy)',
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              OutlinedButton.icon(
                onPressed: _loadNotes,
                icon: const Icon(Icons.refresh),
                label: const Text('Refresh Notes'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          FilledButton.icon(
            onPressed: loading ? null : _generateQuiz,
            icon: const Icon(Icons.auto_awesome),
            label: Text(loading
                ? 'Generating...'
                : interleavedMode
                    ? 'Generate Interleaved Quiz'
                    : 'Generate Quiz'),
          ),
          const SizedBox(height: 12),
          Expanded(
            child: SingleChildScrollView(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  SelectableText(
                    output.isEmpty
                        ? 'Generated quiz output appears here. Configure API key in Settings first.'
                        : output,
                  ),
                  if (interleavedMode && output.isNotEmpty && topicBreakdown.isNotEmpty) ...[
                    const SizedBox(height: 12),
                    const Text(
                      'Interleaved topic breakdown',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    const SizedBox(height: 6),
                    ...topicBreakdown.entries.map((entry) => Text(
                          '• ${entry.key}: ${entry.value} mention${entry.value == 1 ? '' : 's'}',
                        )),
                  ],
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
