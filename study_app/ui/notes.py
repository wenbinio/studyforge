"""
notes.py — Notes Manager tab for StudyForge.
Import .txt, .md, .pdf, .docx files; view, tag, search, and manage notes.
"""

import customtkinter as ctk
import threading
import os
from tkinter import filedialog
from ui.styles import COLORS, FONTS, PADDING
import database as db


def extract_text_from_file(filepath: str) -> str:
    """Extract text content from various file formats."""
    ext = os.path.splitext(filepath)[1].lower()

    if ext in (".txt", ".md"):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()

    elif ext == ".pdf":
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(filepath)
            text = ""
            for page in doc:
                text += page.get_text() + "\n"
            doc.close()
            return text.strip()
        except ImportError:
            return "[Error: PyMuPDF not installed. Run: pip install PyMuPDF]"

    elif ext == ".docx":
        try:
            from docx import Document
            doc = Document(filepath)
            return "\n".join(p.text for p in doc.paragraphs)
        except ImportError:
            return "[Error: python-docx not installed. Run: pip install python-docx]"

    else:
        return f"[Unsupported file format: {ext}]"


class NotesTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.selected_note_id = None
        self._ai_request_id = 0  # Guard against race conditions in async AI calls
        self.build_ui()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PADDING["page"], pady=(PADDING["page"], 5))

        ctk.CTkLabel(
            header, text="📝 Notes Manager",
            font=FONTS["heading"], text_color=COLORS["text_primary"]
        ).pack(side="left")

        btn_row = ctk.CTkFrame(header, fg_color="transparent")
        btn_row.pack(side="right")

        ctk.CTkButton(
            btn_row, text="📂 Import File", width=120, height=34,
            font=FONTS["body"], fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], corner_radius=8,
            command=self.import_file
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row, text="📋 Paste Note", width=120, height=34,
            font=FONTS["body"], fg_color=COLORS["success"],
            hover_color="#00d2a0", corner_radius=8,
            command=self.show_paste_dialog
        ).pack(side="left", padx=4)

        # Search bar
        search_frame = ctk.CTkFrame(self, fg_color="transparent")
        search_frame.pack(fill="x", padx=PADDING["page"], pady=(5, 8))

        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh_list())

        search_entry = ctk.CTkEntry(
            search_frame, textvariable=self.search_var,
            placeholder_text="🔍 Search notes by title, content, or tags...",
            fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], border_color=COLORS["border"],
            corner_radius=8, height=36
        )
        search_entry.pack(fill="x")

        # Split view: list on left, content on right
        split = ctk.CTkFrame(self, fg_color="transparent")
        split.pack(fill="both", expand=True, padx=PADDING["page"], pady=(0, PADDING["page"]))
        split.grid_columnconfigure(0, weight=1, minsize=280)
        split.grid_columnconfigure(1, weight=3)
        split.grid_rowconfigure(0, weight=1)

        # Left: notes list
        self.list_frame = ctk.CTkScrollableFrame(
            split, fg_color=COLORS["bg_card"], corner_radius=12, width=280
        )
        self.list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))

        # Right: note viewer/editor
        self.viewer_frame = ctk.CTkFrame(split, fg_color=COLORS["bg_card"], corner_radius=12)
        self.viewer_frame.grid(row=0, column=1, sticky="nsew")

        self.refresh_list()
        self._show_empty_viewer()

    def _show_empty_viewer(self):
        for w in self.viewer_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.viewer_frame, text="📄",
            font=("Segoe UI", 40), text_color=COLORS["text_muted"]
        ).pack(expand=True)
        ctk.CTkLabel(
            self.viewer_frame, text="Select a note to view, or import a new one.",
            font=FONTS["body"], text_color=COLORS["text_muted"]
        ).pack(pady=(0, 40))

    def refresh_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

        query = self.search_var.get().strip()
        notes = db.search_notes(query) if query else db.get_all_notes()

        if not notes:
            ctk.CTkLabel(
                self.list_frame, text="No notes yet.\nImport or paste a note to start.",
                font=FONTS["body"], text_color=COLORS["text_muted"],
                justify="center"
            ).pack(expand=True, pady=40)
            return

        for note in notes:
            self._create_note_item(note)

    def _create_note_item(self, note):
        is_selected = note["id"] == self.selected_note_id
        bg = COLORS["accent"] if is_selected else COLORS["bg_secondary"]

        item = ctk.CTkFrame(self.list_frame, fg_color=bg, corner_radius=8, cursor="hand2")
        item.pack(fill="x", padx=6, pady=3)

        title = note["title"][:40] + ("..." if len(note["title"]) > 40 else "")
        ctk.CTkLabel(
            item, text=title, font=FONTS["body_bold"],
            text_color=COLORS["text_primary"], anchor="w"
        ).pack(padx=10, pady=(8, 0), anchor="w")

        meta = f"{note.get('tags', '') or 'No tags'}  ·  {note['created_at'][:10]}"
        ctk.CTkLabel(
            item, text=meta, font=FONTS["small"],
            text_color=COLORS["text_muted"], anchor="w"
        ).pack(padx=10, pady=(0, 6), anchor="w")

        # Bind click
        for widget in [item] + item.winfo_children():
            widget.bind("<Button-1>", lambda e, nid=note["id"]: self.view_note(nid))

    def view_note(self, note_id):
        self.selected_note_id = note_id
        self._ai_request_id += 1  # Invalidate any in-flight AI requests
        self.refresh_list()

        note = db.get_note(note_id)
        if not note:
            return

        for w in self.viewer_frame.winfo_children():
            w.destroy()

        # Title bar
        title_bar = ctk.CTkFrame(self.viewer_frame, fg_color="transparent")
        title_bar.pack(fill="x", padx=PADDING["section"], pady=(PADDING["section"], 5))

        self.title_entry = ctk.CTkEntry(
            title_bar, font=FONTS["subheading"],
            fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            border_color=COLORS["border"], corner_radius=8
        )
        self.title_entry.insert(0, note["title"])
        self.title_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))

        ctk.CTkButton(
            title_bar, text="💾 Save", width=70, height=32,
            font=FONTS["small"], fg_color=COLORS["success"],
            corner_radius=6, command=lambda: self._save_note(note_id)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            title_bar, text="🗑️", width=36, height=32,
            font=FONTS["small"], fg_color=COLORS["danger"],
            corner_radius=6, command=lambda: self._delete_note(note_id)
        ).pack(side="left", padx=2)

        # Tags
        tags_frame = ctk.CTkFrame(self.viewer_frame, fg_color="transparent")
        tags_frame.pack(fill="x", padx=PADDING["section"], pady=(0, 5))

        ctk.CTkLabel(tags_frame, text="Tags:", font=FONTS["small"],
                      text_color=COLORS["text_muted"]).pack(side="left")
        self.tags_entry = ctk.CTkEntry(
            tags_frame, font=FONTS["small"], fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], border_color=COLORS["border"],
            corner_radius=6, height=28
        )
        self.tags_entry.insert(0, note.get("tags", ""))
        self.tags_entry.pack(side="left", fill="x", expand=True, padx=6)

        # Action buttons
        action_row = ctk.CTkFrame(self.viewer_frame, fg_color="transparent")
        action_row.pack(fill="x", padx=PADDING["section"], pady=(0, 5))

        ctk.CTkButton(
            action_row, text="🤖 Generate Cards", width=140, height=30,
            font=FONTS["small"], fg_color=COLORS["warning"],
            corner_radius=6, command=lambda: self._generate_from_note(note)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            action_row, text="📋 Summarize", width=110, height=30,
            font=FONTS["small"], fg_color=COLORS["accent"],
            corner_radius=6, command=lambda: self._summarize_note(note)
        ).pack(side="left", padx=2)

        ctk.CTkButton(
            action_row, text="❓ Ask Question", width=120, height=30,
            font=FONTS["small"], fg_color=COLORS["accent_light"],
            corner_radius=6, command=lambda: self._ask_about_note(note)
        ).pack(side="left", padx=2)

        # Content editor
        self.content_editor = ctk.CTkTextbox(
            self.viewer_frame, fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], font=FONTS["body"],
            border_color=COLORS["border"], border_width=1, corner_radius=8,
            wrap="word"
        )
        self.content_editor.insert("1.0", note["content"])
        self.content_editor.pack(fill="both", expand=True, padx=PADDING["section"], pady=(0, PADDING["section"]))

        # AI output area
        self.ai_output_label = ctk.CTkLabel(
            self.viewer_frame, text="",
            font=FONTS["small"], text_color=COLORS["text_secondary"],
            wraplength=600, justify="left"
        )

    def _save_note(self, note_id):
        title = self.title_entry.get().strip()
        content = self.content_editor.get("1.0", "end").strip()
        tags = self.tags_entry.get().strip()
        db.update_note(note_id, title=title, content=content, tags=tags)
        self.refresh_list()

    def _delete_note(self, note_id):
        # Confirmation dialog
        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("380x150")
        dialog.configure(fg_color=COLORS["bg_primary"])
        dialog.attributes("-topmost", True)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="⚠️ Are you sure you want to delete this note?\nThis cannot be undone.",
            font=FONTS["body"], text_color=COLORS["text_primary"], justify="center"
        ).pack(pady=(20, 15))

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack()

        def confirm():
            db.delete_note(note_id)
            self.selected_note_id = None
            self.refresh_list()
            self._show_empty_viewer()
            dialog.destroy()

        ctk.CTkButton(
            btn_row, text="🗑️ Delete", width=100, height=34,
            font=FONTS["body_bold"], fg_color=COLORS["danger"],
            corner_radius=8, command=confirm
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_row, text="Cancel", width=100, height=34,
            font=FONTS["body"], fg_color=COLORS["bg_secondary"],
            corner_radius=8, command=dialog.destroy
        ).pack(side="left", padx=6)

    def _generate_from_note(self, note):
        if not self.app.claude_client:
            return
        # Pass the specific note to flashcards tab for pre-selection
        fc_tab = self.app.tabs.get("Flashcards")
        if fc_tab:
            self.app.select_tab("Flashcards")
            fc_tab.show_ai_generate_dialog(preselect_note_id=note["id"])

    def _get_current_note_content(self):
        """Get the content currently in the editor (which may differ from DB)."""
        try:
            return self.content_editor.get("1.0", "end").strip()
        except Exception:
            return ""

    def _summarize_note(self, note):
        if not self.app.claude_client:
            return

        # Use editor content (may have unsaved edits)
        current_content = self._get_current_note_content() or note["content"]

        self._ai_request_id += 1
        request_id = self._ai_request_id

        self.ai_output_label.configure(text="⏳ Summarizing...")
        self.ai_output_label.pack(fill="x", padx=PADDING["section"], pady=(0, 8))

        def do_summarize():
            try:
                result = self.app.claude_client.summarize_notes(current_content)
                self.after(0, lambda: self._handle_ai_result(request_id, "📋 Summary", result))
            except Exception as e:
                self.after(0, lambda: self._handle_ai_error(request_id, str(e)[:80]))

        threading.Thread(target=do_summarize, daemon=True).start()

    def _ask_about_note(self, note):
        dialog = ctk.CTkInputDialog(
            text="Ask a question about this note:",
            title="Ask Claude"
        )
        question = dialog.get_input()
        if not question or not self.app.claude_client:
            return

        # Use editor content (may have unsaved edits)
        current_content = self._get_current_note_content() or note["content"]

        self._ai_request_id += 1
        request_id = self._ai_request_id

        self.ai_output_label.configure(text="⏳ Thinking...")
        self.ai_output_label.pack(fill="x", padx=PADDING["section"], pady=(0, 8))

        def do_ask():
            try:
                result = self.app.claude_client.answer_question(question, current_content)
                self.after(0, lambda: self._handle_ai_result(request_id, f"❓ {question}", result))
            except Exception as e:
                self.after(0, lambda: self._handle_ai_error(request_id, str(e)[:80]))

        threading.Thread(target=do_ask, daemon=True).start()

    def _handle_ai_result(self, request_id, title, content):
        """Safely handle AI result — only update UI if this is still the active request."""
        if request_id != self._ai_request_id:
            return  # User switched notes; discard stale result
        try:
            self._show_ai_result(title, content)
        except Exception:
            pass  # Widget destroyed; silently ignore

    def _handle_ai_error(self, request_id, error_msg):
        """Safely handle AI error — only update UI if this is still the active request."""
        if request_id != self._ai_request_id:
            return
        try:
            self.ai_output_label.configure(text=f"❌ {error_msg}", text_color=COLORS["danger"])
        except Exception:
            pass

    def _show_ai_result(self, title, content):
        """Show AI result in a popup window."""
        win = ctk.CTkToplevel(self)
        win.title("StudyForge — AI Result")
        win.geometry("700x500")
        win.configure(fg_color=COLORS["bg_primary"])
        win.attributes("-topmost", True)

        ctk.CTkLabel(
            win, text=title, font=FONTS["subheading"],
            text_color=COLORS["accent_light"]
        ).pack(padx=15, pady=(15, 5), anchor="w")

        text_box = ctk.CTkTextbox(
            win, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], wrap="word", corner_radius=8
        )
        text_box.insert("1.0", content)
        text_box.configure(state="disabled")
        text_box.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.ai_output_label.configure(text="✅ Done — result shown in popup.")

    # ── Import ────────────────────────────────────────────────────

    def import_file(self):
        filepaths = filedialog.askopenfilenames(
            title="Import Lecture Notes",
            filetypes=[
                ("All Supported", "*.txt *.md *.pdf *.docx"),
                ("Text files", "*.txt"),
                ("Markdown", "*.md"),
                ("PDF", "*.pdf"),
                ("Word", "*.docx"),
            ]
        )
        for fp in filepaths:
            filename = os.path.basename(fp)
            title = os.path.splitext(filename)[0]
            content = extract_text_from_file(fp)
            db.add_note(title, content, source_file=filename)

        if filepaths:
            self.refresh_list()

    def show_paste_dialog(self):
        win = ctk.CTkToplevel(self)
        win.title("Paste Note")
        win.geometry("600x450")
        win.configure(fg_color=COLORS["bg_primary"])
        win.attributes("-topmost", True)

        ctk.CTkLabel(
            win, text="Title:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        ).pack(padx=15, pady=(15, 2), anchor="w")

        title_entry = ctk.CTkEntry(
            win, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], corner_radius=8
        )
        title_entry.pack(fill="x", padx=15)

        ctk.CTkLabel(
            win, text="Content:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        ).pack(padx=15, pady=(10, 2), anchor="w")

        content_box = ctk.CTkTextbox(
            win, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], wrap="word", corner_radius=8
        )
        content_box.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        def save():
            t = title_entry.get().strip() or "Untitled Note"
            c = content_box.get("1.0", "end").strip()
            if c:
                db.add_note(t, c)
                self.refresh_list()
                win.destroy()

        ctk.CTkButton(
            win, text="💾 Save Note", height=36,
            font=FONTS["body_bold"], fg_color=COLORS["success"],
            corner_radius=8, command=save
        ).pack(padx=15, pady=(0, 15))
