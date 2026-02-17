import 'package:flutter/material.dart';

import '../../core/app_controller.dart';
import '../../core/ai_parsers.dart';
import '../../core/models.dart';

class FlashcardsPage extends StatefulWidget {
  const FlashcardsPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<FlashcardsPage> createState() => _FlashcardsPageState();
}

class _FlashcardsPageState extends State<FlashcardsPage> {
  final frontController = TextEditingController();
  final backController = TextEditingController();
  final tagsController = TextEditingController();

  List<Flashcard> dueCards = [];
  List<Note> notes = [];
  int currentIndex = 0;
  bool showBack = false;
  bool generatingAiCards = false;
  int? selectedNoteId;

  @override
  void initState() {
    super.initState();
    _loadDueCards();
    _loadNotes();
  }

  @override
  void dispose() {
    frontController.dispose();
    backController.dispose();
    tagsController.dispose();
    super.dispose();
  }

  Future<void> _loadDueCards() async {
    final cards = await widget.controller.database.getFlashcards(dueOnly: true);
    if (!mounted) {
      return;
    }
    setState(() {
      dueCards = cards;
      currentIndex = 0;
      showBack = false;
    });
  }

  Future<void> _loadNotes() async {
    final fetched = await widget.controller.database.getNotes();
    if (!mounted) {
      return;
    }
    setState(() {
      notes = fetched;
      selectedNoteId ??= fetched.isEmpty ? null : fetched.first.id;
    });
  }

  Future<void> _addCard() async {
    final front = frontController.text.trim();
    final back = backController.text.trim();
    if (front.isEmpty || back.isEmpty) {
      ScaffoldMessenger.of(context)
          .showSnackBar(const SnackBar(content: Text('Front and back are required.')));
      return;
    }

    await widget.controller.database.addFlashcard(
      Flashcard(
        id: null,
        noteId: null,
        front: front,
        back: back,
        tags: tagsController.text.trim(),
        nextReview: DateTime.now(),
        createdAt: DateTime.now(),
      ),
    );
    await widget.controller.database.incrementDailyStat('cards_added', 1);

    frontController.clear();
    backController.clear();
    tagsController.clear();

    await _loadDueCards();
  }

  Future<void> _rateCard(int rating) async {
    if (dueCards.isEmpty || currentIndex >= dueCards.length) {
      return;
    }
    final card = dueCards[currentIndex];
    final reviewed = widget.controller.srs.applyReview(card: card, rating: rating);
    await widget.controller.database.updateFlashcard(reviewed);
    await widget.controller.database.addReviewLog(
      ReviewLog(
        cardId: card.id!,
        rating: rating,
        reviewedAt: DateTime.now(),
      ),
    );
    await widget.controller.database.incrementDailyStat('cards_reviewed', 1);

    await _loadDueCards();
  }

  Future<void> _generateCardsFromNote() async {
    final noteId = selectedNoteId;
    if (noteId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Create a note before AI generation.')),
      );
      return;
    }
    Note? note;
    for (final n in notes) {
      if (n.id == noteId) {
        note = n;
        break;
      }
    }
    if (note == null) {
      return;
    }

    setState(() {
      generatingAiCards = true;
    });
    try {
      final raw = await widget.controller.ai.generateText(
        provider: widget.controller.config.aiProvider,
        apiKey: widget.controller.config.apiKey,
        model: widget.controller.config.model,
        prompt:
            'Generate 10 flashcards from the notes below. Return ONLY valid JSON as either an array or object with key "flashcards". '
            'Each item must include "front", "back", and optional "tags".\n\n'
            'Title: ${note.title}\n'
            'Tags: ${note.tags}\n'
            'Content:\n${note.content}',
      );
      final generated = parseGeneratedFlashcards(raw).take(10).toList();
      if (generated.isEmpty) {
        throw Exception('AI returned no usable cards.');
      }
      for (final card in generated) {
        await widget.controller.database.addFlashcard(
          Flashcard(
            id: null,
            noteId: noteId,
            front: card.front,
            back: card.back,
            tags: card.tags,
            nextReview: DateTime.now(),
            createdAt: DateTime.now(),
          ),
        );
      }
      await widget.controller.database.incrementDailyStat('cards_added', generated.length);
      await _loadDueCards();
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Added ${generated.length} AI flashcards.')),
      );
    } catch (e) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('AI generation failed: $e')),
      );
    } finally {
      if (mounted) {
        setState(() {
          generatingAiCards = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final currentCard = dueCards.isEmpty ? null : dueCards[currentIndex];

    return ListView(
      padding: const EdgeInsets.all(16),
      children: [
        Text('Due cards: ${dueCards.length}', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        Card(
          child: SizedBox(
            height: 180,
            child: currentCard == null
                ? const Center(child: Text('No cards due right now.'))
                : InkWell(
                    onTap: () {
                      setState(() {
                        showBack = !showBack;
                      });
                    },
                    child: Center(
                      child: Padding(
                        padding: const EdgeInsets.all(16),
                        child: Text(
                          showBack ? currentCard.back : currentCard.front,
                          style: const TextStyle(fontSize: 20),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ),
                  ),
          ),
        ),
        if (currentCard != null) ...[
          const SizedBox(height: 8),
          Wrap(
            spacing: 8,
            children: List.generate(
              6,
              (rating) => FilledButton(
                onPressed: () => _rateCard(rating),
                child: Text('$rating'),
              ),
            ),
          ),
        ],
        const Divider(height: 32),
        Text('Add flashcard', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
        TextField(
          controller: frontController,
          decoration: const InputDecoration(labelText: 'Front'),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: backController,
          decoration: const InputDecoration(labelText: 'Back'),
        ),
        const SizedBox(height: 8),
        TextField(
          controller: tagsController,
          decoration: const InputDecoration(labelText: 'Tags'),
        ),
        const SizedBox(height: 8),
         Row(
          children: [
            FilledButton.icon(
              onPressed: _addCard,
              icon: const Icon(Icons.add),
              label: const Text('Add Card'),
            ),
            const SizedBox(width: 8),
            OutlinedButton.icon(
              onPressed: _loadDueCards,
              icon: const Icon(Icons.refresh),
              label: const Text('Refresh Due'),
            )
          ],
        ),
        const Divider(height: 32),
        Text('AI generate from note', style: Theme.of(context).textTheme.titleMedium),
        const SizedBox(height: 8),
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
        ),
        const SizedBox(height: 8),
        FilledButton.icon(
          onPressed: generatingAiCards ? null : _generateCardsFromNote,
          icon: const Icon(Icons.auto_awesome),
          label: Text(generatingAiCards ? 'Generating...' : 'Generate 10 Cards'),
        ),
      ],
    );
  }
}
