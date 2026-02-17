import 'package:flutter/material.dart';

import '../../core/app_controller.dart';
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
  int currentIndex = 0;
  bool showBack = false;

  @override
  void initState() {
    super.initState();
    _loadDueCards();
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
        )
      ],
    );
  }
}
