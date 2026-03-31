import 'package:flutter/material.dart';

import '../../core/app_controller.dart';
import '../../core/models.dart';
import '../../core/notes_tools.dart';

class NotesPage extends StatefulWidget {
  const NotesPage({super.key, required this.controller});

  final AppController controller;

  @override
  State<NotesPage> createState() => _NotesPageState();
}

class _NotesPageState extends State<NotesPage> {
  final titleController = TextEditingController();
  final contentController = TextEditingController();
  final tagsController = TextEditingController();
  final findController = TextEditingController();
  List<Note> notes = [];
  String findStatus = '';

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    titleController.dispose();
    contentController.dispose();
    tagsController.dispose();
    findController.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    final fetched = await widget.controller.database.getNotes();
    if (!mounted) {
      return;
    }
    setState(() {
      notes = fetched;
    });
  }

  Future<void> _saveNote() async {
    final title = titleController.text.trim();
    final content = contentController.text.trim();
    if (title.isEmpty || content.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Title and content are required.')),
      );
      return;
    }

    final now = DateTime.now();
    final note = Note(
      id: null,
      title: title,
      content: content,
      tags: tagsController.text.trim(),
      sourceFile: null,
      createdAt: now,
      updatedAt: now,
    );

    await widget.controller.database.addNote(note);
    titleController.clear();
    contentController.clear();
    tagsController.clear();
    await _load();
  }

  void _findInDraft() {
    final count = countMatches(contentController.text, findController.text);
    setState(() {
      if (findController.text.trim().isEmpty) {
        findStatus = 'Enter text to find.';
      } else {
        findStatus = '$count match${count == 1 ? '' : 'es'} in current draft.';
      }
    });
  }

  Future<void> _exportDraft(String extension) async {
    final title = titleController.text.trim();
    final content = contentController.text;
    if (content.trim().isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Write note content before export.')),
      );
      return;
    }
    try {
      final path = await exportNoteToDocuments(
        title: title.isEmpty ? 'note' : title,
        content: content,
        extension: extension,
      );
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Exported to $path')),
      );
    } catch (e) {
      if (!mounted) {
        return;
      }
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Export failed: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          TextField(
            controller: titleController,
            decoration: const InputDecoration(labelText: 'Note title'),
          ),
          const SizedBox(height: 8),
          TextField(
            controller: tagsController,
            decoration: const InputDecoration(labelText: 'Tags (comma separated)'),
          ),
          const SizedBox(height: 8),
          Expanded(
            child: TextField(
              controller: contentController,
              maxLines: null,
              expands: true,
              decoration: const InputDecoration(
                alignLabelWithHint: true,
                border: OutlineInputBorder(),
                labelText: 'Note content (markdown supported)',
              ),
            ),
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              FilledButton.icon(
                onPressed: _saveNote,
                icon: const Icon(Icons.save),
                label: const Text('Save Note'),
              ),
              const SizedBox(width: 8),
              OutlinedButton.icon(
                onPressed: _load,
                icon: const Icon(Icons.refresh),
                label: const Text('Refresh'),
              ),
              const SizedBox(width: 8),
              OutlinedButton.icon(
                onPressed: () => _exportDraft('txt'),
                icon: const Icon(Icons.download),
                label: const Text('Export .txt'),
              ),
              const SizedBox(width: 8),
              OutlinedButton.icon(
                onPressed: () => _exportDraft('md'),
                icon: const Icon(Icons.download),
                label: const Text('Export .md'),
              )
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              Expanded(
                child: TextField(
                  controller: findController,
                  decoration: const InputDecoration(labelText: 'Find in current draft'),
                ),
              ),
              const SizedBox(width: 8),
              OutlinedButton.icon(
                onPressed: _findInDraft,
                icon: const Icon(Icons.search),
                label: const Text('Find'),
              ),
            ],
          ),
          if (findStatus.isNotEmpty) ...[
            const SizedBox(height: 6),
            Align(alignment: Alignment.centerLeft, child: Text(findStatus)),
          ],
          const SizedBox(height: 16),
          Expanded(
            child: ListView.builder(
              itemCount: notes.length,
              itemBuilder: (context, index) {
                final note = notes[index];
                return ListTile(
                  leading: const Icon(Icons.description),
                  title: Text(note.title),
                  subtitle: Text(
                    note.content,
                    maxLines: 2,
                    overflow: TextOverflow.ellipsis,
                  ),
                  trailing: Text(note.tags),
                );
              },
            ),
          ),
        ],
      ),
    );
  }
}
