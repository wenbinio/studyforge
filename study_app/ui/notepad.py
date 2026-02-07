"""
notepad.py — Comprehensive Notepad tab for StudyForge.
Rich text editor with markdown formatting, preview, and focus mode.
"""

import customtkinter as ctk
import re
from tkinter import font as tkfont
from ui.styles import COLORS, FONTS, PADDING
import database as db


class NotepadTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.preview_visible = False
        self.current_note_id = None
        self._build_ui()

    def _build_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # ── Header row ────────────────────────────────────────────
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(PADDING["page"], 5))

        ctk.CTkLabel(
            header, text="✏️ Notepad",
            font=FONTS["heading"], text_color=COLORS["text_primary"]
        ).pack(side="left")

        btn_row = ctk.CTkFrame(header, fg_color="transparent")
        btn_row.pack(side="right")

        # Focus mode button
        self.focus_btn = ctk.CTkButton(
            btn_row, text="🖥️ Focus Mode", width=120, height=34,
            font=FONTS["body"], fg_color=COLORS["bg_card"],
            hover_color=COLORS["accent_hover"], corner_radius=8,
            command=self._toggle_focus_mode
        )
        self.focus_btn.pack(side="left", padx=4)

        # Preview toggle
        self.preview_btn = ctk.CTkButton(
            btn_row, text="👁️ Preview", width=100, height=34,
            font=FONTS["body"], fg_color=COLORS["bg_card"],
            hover_color=COLORS["accent_hover"], corner_radius=8,
            command=self._toggle_preview
        )
        self.preview_btn.pack(side="left", padx=4)

        # Navigator toggle
        self.nav_visible = False
        self.nav_btn = ctk.CTkButton(
            btn_row, text="Navigator", width=100, height=34,
            font=FONTS["body"], fg_color=COLORS["bg_card"],
            hover_color=COLORS["accent_hover"], corner_radius=8,
            command=self._toggle_navigator
        )
        self.nav_btn.pack(side="left", padx=4)

        # Save note
        ctk.CTkButton(
            btn_row, text="💾 Save", width=80, height=34,
            font=FONTS["body"], fg_color=COLORS["success"],
            hover_color="#00d2a0", corner_radius=8,
            command=self._save_note
        ).pack(side="left", padx=4)

        # New note
        ctk.CTkButton(
            btn_row, text="📄 New", width=80, height=34,
            font=FONTS["body"], fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], corner_radius=8,
            command=self._new_note
        ).pack(side="left", padx=4)

        # ── Formatting toolbar ────────────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color=COLORS["bg_secondary"], corner_radius=8, height=40)
        toolbar.grid(row=1, column=0, sticky="ew", pady=(0, 0))

        fmt_buttons = [
            ("H1", lambda: self._insert_prefix("# ")),
            ("H2", lambda: self._insert_prefix("## ")),
            ("H3", lambda: self._insert_prefix("### ")),
            ("H4", lambda: self._insert_prefix("#### ")),
            ("|", None),
            ("B", lambda: self._wrap_selection("**")),
            ("I", lambda: self._wrap_selection("*")),
            ("~~", lambda: self._wrap_selection("~~")),
            ("|", None),
            ("• List", lambda: self._insert_prefix("- ")),
            ("1. List", lambda: self._insert_prefix("1. ")),
            ("☑ Task", lambda: self._insert_prefix("- [ ] ")),
            ("|", None),
            ("`Code`", lambda: self._wrap_selection("`")),
            ("```", self._insert_code_block),
            ("> Quote", lambda: self._insert_prefix("> ")),
            ("---", lambda: self._insert_line("\n---\n")),
        ]

        for text, cmd in fmt_buttons:
            if cmd is None:
                # Separator
                ctk.CTkFrame(toolbar, width=1, height=20, fg_color=COLORS["border"]).pack(
                    side="left", padx=4, pady=8
                )
            else:
                is_heading = text in ("H1", "H2", "H3", "H4")
                if is_heading or text == "B":
                    btn_font = ("Segoe UI", 12, "bold")
                elif text == "I":
                    btn_font = ("Segoe UI", 12, "italic")
                else:
                    btn_font = FONTS["small"]
                ctk.CTkButton(
                    toolbar, text=text, width=max(36, len(text) * 10 + 10), height=28,
                    font=btn_font, fg_color="transparent",
                    hover_color=COLORS["bg_card"],
                    text_color=COLORS["text_secondary"], corner_radius=6,
                    command=cmd
                ).pack(side="left", padx=1, pady=4)

        # ── Title entry ───────────────────────────────────────────
        title_frame = ctk.CTkFrame(self, fg_color="transparent")
        title_frame.grid(row=2, column=0, sticky="ew", pady=(0, 5))

        self.title_entry = ctk.CTkEntry(
            title_frame, placeholder_text="Note title...",
            fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["subheading"], border_color=COLORS["border"],
            corner_radius=8, height=38
        )
        self.title_entry.pack(fill="x")

        # ── Note selector row ────────────────────────────────────
        selector_frame = ctk.CTkFrame(self, fg_color="transparent")
        selector_frame.grid(row=3, column=0, sticky="ew", pady=(0, 5))

        ctk.CTkLabel(
            selector_frame, text="📂 Open:", font=FONTS["small"],
            text_color=COLORS["text_muted"]
        ).pack(side="left")

        self.note_selector = ctk.CTkOptionMenu(
            selector_frame, values=["— New Note —"],
            font=FONTS["small"], fg_color=COLORS["bg_input"],
            button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"],
            dropdown_fg_color=COLORS["bg_card"], dropdown_hover_color=COLORS["accent"],
            text_color=COLORS["text_primary"], corner_radius=6, height=28,
            command=self._on_note_selected
        )
        self.note_selector.pack(side="left", padx=8)

        ctk.CTkButton(
            selector_frame, text="🗑️ Delete", width=70, height=28,
            font=FONTS["small"], fg_color=COLORS["danger"],
            corner_radius=6, command=self._delete_current_note
        ).pack(side="left", padx=4)

        self.status_label = ctk.CTkLabel(
            selector_frame, text="", font=FONTS["small"],
            text_color=COLORS["text_muted"]
        )
        self.status_label.pack(side="right")

        # ── Main editor + preview area ────────────────────────────
        # Adjust grid row weights
        self.grid_rowconfigure(2, weight=0)
        self.grid_rowconfigure(3, weight=0)
        self.grid_rowconfigure(4, weight=1)

        self.editor_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.editor_frame.grid(row=4, column=0, sticky="nsew")
        self.editor_frame.grid_columnconfigure(0, weight=0)  # navigator (fixed width)
        self.editor_frame.grid_columnconfigure(1, weight=1)  # editor
        self.editor_frame.grid_columnconfigure(2, weight=0)  # preview (shown dynamically)
        self.editor_frame.grid_rowconfigure(0, weight=1)

        # Navigator panel (hidden by default)
        self.nav_panel = ctk.CTkScrollableFrame(
            self.editor_frame, fg_color=COLORS["bg_card"],
            width=180, corner_radius=8,
            border_color=COLORS["border"], border_width=1
        )

        # Editor
        self.editor = ctk.CTkTextbox(
            self.editor_frame, fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], font=("Consolas", 13),
            border_color=COLORS["border"], border_width=1, corner_radius=8,
            wrap="word", undo=True
        )
        self.editor.grid(row=0, column=0, sticky="nsew")

        # Preview panel (hidden by default)
        self.preview_panel = ctk.CTkTextbox(
            self.editor_frame, fg_color=COLORS["bg_card"],
            text_color=COLORS["text_primary"], font=FONTS["body"],
            border_color=COLORS["accent"], border_width=1, corner_radius=8,
            wrap="word"
        )

        self._update_editor_layout()

        # ── Keyboard shortcuts ────────────────────────────────────
        self.editor.bind("<Control-b>", lambda e: (self._wrap_selection("**"), "break"))
        self.editor.bind("<Control-i>", lambda e: (self._wrap_selection("*"), "break"))
        self.editor.bind("<Control-k>", lambda e: (self._wrap_selection("`"), "break"))
        self.editor.bind("<Control-s>", lambda e: (self._save_note(), "break"))
        self.editor.bind("<Control-B>", lambda e: (self._wrap_selection("**"), "break"))
        self.editor.bind("<Control-I>", lambda e: (self._wrap_selection("*"), "break"))
        self.editor.bind("<Control-K>", lambda e: (self._wrap_selection("`"), "break"))
        self.editor.bind("<Control-S>", lambda e: (self._save_note(), "break"))

        # Load saved notes into selector
        self._refresh_note_selector()

    # ── Formatting helpers ────────────────────────────────────────

    def _insert_prefix(self, prefix):
        """Insert a prefix at the beginning of the current line."""
        try:
            cursor = self.editor.index("insert")
            line = cursor.split(".")[0]
            line_start = f"{line}.0"
            line_text = self.editor.get(line_start, f"{line}.end")
            if line_text.startswith(prefix):
                return
            self.editor.insert(line_start, prefix)
            self.editor.focus_set()
        except Exception:
            pass

    def _wrap_selection(self, wrapper):
        """Wrap the selected text with a marker (e.g., ** for bold)."""
        try:
            sel_start = self.editor.index("sel.first")
            sel_end = self.editor.index("sel.last")
            selected = self.editor.get(sel_start, sel_end)
            self.editor.delete(sel_start, sel_end)
            self.editor.insert(sel_start, f"{wrapper}{selected}{wrapper}")
            self.editor.focus_set()
        except Exception:
            cursor = self.editor.index("insert")
            self.editor.insert(cursor, f"{wrapper}{wrapper}")
            new_pos = self.editor.index(f"{cursor} + {len(wrapper)} chars")
            self.editor.mark_set("insert", new_pos)
            self.editor.focus_set()

    def _insert_code_block(self):
        """Insert a fenced code block."""
        try:
            sel_start = self.editor.index("sel.first")
            sel_end = self.editor.index("sel.last")
            selected = self.editor.get(sel_start, sel_end)
            self.editor.delete(sel_start, sel_end)
            self.editor.insert(sel_start, f"```\n{selected}\n```")
        except Exception:
            cursor = self.editor.index("insert")
            self.editor.insert(cursor, "```\n\n```")
            new_pos = self.editor.index(f"{cursor} + 4 chars")
            self.editor.mark_set("insert", new_pos)
        self.editor.focus_set()

    def _insert_line(self, text):
        """Insert text at the current cursor position."""
        cursor = self.editor.index("insert")
        self.editor.insert(cursor, text)
        self.editor.focus_set()

    # ── Preview ───────────────────────────────────────────────────
    def _update_editor_layout(self):
        editor_col = 1 if self.nav_visible else 0
        preview_col = editor_col + 1

        if self.nav_visible:
            self.nav_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 5))
        else:
            self.nav_panel.grid_forget()

        self.editor.grid(row=0, column=editor_col, sticky="nsew")

        if self.preview_visible:
            self.preview_panel.grid(row=0, column=preview_col, sticky="nsew", padx=(5, 0))
        else:
            self.preview_panel.grid_forget()

        for col in range(3):
            self.editor_frame.grid_columnconfigure(col, weight=0)
        self.editor_frame.grid_columnconfigure(editor_col, weight=1)
        if self.preview_visible:
            self.editor_frame.grid_columnconfigure(preview_col, weight=1)

    def _toggle_preview(self):
        """Toggle markdown preview panel side-by-side with editor."""
        if self.preview_visible:
            self.preview_btn.configure(fg_color=COLORS["bg_card"])
            self.preview_visible = False
        else:
            self._render_preview()
            self.preview_btn.configure(fg_color=COLORS["accent"])
            self.preview_visible = True
        self._update_editor_layout()

    # ── Markdown Navigator ────────────────────────────────────────

    def _toggle_navigator(self):
        """Toggle the heading navigator panel."""
        if self.nav_visible:
            self.nav_btn.configure(fg_color=COLORS["bg_card"])
            self.nav_visible = False
        else:
            self._refresh_navigator()
            self.nav_btn.configure(fg_color=COLORS["accent"])
            self.nav_visible = True
        self._update_editor_layout()

    def _refresh_navigator(self):
        """Scan the editor content for headings and populate the navigator."""
        for w in self.nav_panel.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.nav_panel, text="Headings",
            font=FONTS["body_bold"], text_color=COLORS["text_primary"]
        ).pack(anchor="w", padx=6, pady=(4, 6))

        content = self.editor.get("1.0", "end")
        lines = content.split("\n")
        found = False
        for i, line in enumerate(lines):
            stripped = line.strip()
            level = 0
            title = ""
            if stripped.startswith("#### "):
                level, title = 4, stripped[5:]
            elif stripped.startswith("### "):
                level, title = 3, stripped[4:]
            elif stripped.startswith("## "):
                level, title = 2, stripped[3:]
            elif stripped.startswith("# "):
                level, title = 1, stripped[2:]

            if level and title:
                found = True
                indent = (level - 1) * 10
                line_num = i + 1
                btn = ctk.CTkButton(
                    self.nav_panel, text=title[:30],
                    font=FONTS["small"] if level > 2 else FONTS["body_bold"],
                    fg_color="transparent", hover_color=COLORS["bg_secondary"],
                    text_color=COLORS["text_secondary"], anchor="w",
                    height=24, corner_radius=4,
                    command=lambda ln=line_num: self._navigate_to_line(ln)
                )
                btn.pack(fill="x", padx=(6 + indent, 4), pady=1)

        if not found:
            ctk.CTkLabel(
                self.nav_panel, text="No headings found",
                font=FONTS["small"], text_color=COLORS["text_muted"]
            ).pack(padx=6, pady=8)

    def _navigate_to_line(self, line_num):
        """Scroll the editor to a specific line."""
        pos = f"{line_num}.0"
        self.editor.mark_set("insert", pos)
        self.editor.see(pos)
        self.editor.focus_set()

    def _render_preview(self):
        """Render markdown content as styled text in the preview panel."""
        content = self.editor.get("1.0", "end").strip()
        self.preview_panel.configure(state="normal")
        self.preview_panel.delete("1.0", "end")

        if not content:
            self.preview_panel.insert("1.0", "Start typing to see preview...")
            self.preview_panel.configure(state="disabled")
            return

        rendered = self._markdown_to_display(content)
        self.preview_panel.insert("1.0", rendered)
        self.preview_panel.configure(state="disabled")

    def _markdown_to_display(self, text):
        """Convert markdown to display text with visual formatting cues."""
        lines = text.split("\n")
        output = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith("#### "):
                output.append(f"    {stripped[5:]}")
            elif stripped.startswith("### "):
                output.append(f"   {stripped[4:].upper()}")
            elif stripped.startswith("## "):
                output.append(f"  ━━ {stripped[3:].upper()} ━━")
            elif stripped.startswith("# "):
                output.append(f"═══ {stripped[2:].upper()} ═══")
            elif stripped.startswith("---") or stripped.startswith("***"):
                output.append("─" * 40)
            elif stripped.startswith("- [ ] "):
                output.append(f"  ☐ {stripped[6:]}")
            elif stripped.startswith("- [x] ") or stripped.startswith("- [X] "):
                output.append(f"  ☑ {stripped[6:]}")
            elif stripped.startswith("- "):
                output.append(f"  • {stripped[2:]}")
            elif stripped.startswith("> "):
                output.append(f"  │ {stripped[2:]}")
            elif stripped.startswith("```"):
                output.append("  ┌────────────────────")
            else:
                display = stripped
                display = re.sub(r'\*\*(.+?)\*\*', r'[\1]', display)
                display = re.sub(r'\*(.+?)\*', r'\1', display)
                display = re.sub(r'~~(.+?)~~', r'\1', display)
                display = re.sub(r'`(.+?)`', r'⟨\1⟩', display)
                output.append(display)
        return "\n".join(output)

    # ── Focus Mode ────────────────────────────────────────────────

    def _toggle_focus_mode(self):
        """Toggle sidebar visibility for distraction-free writing."""
        self.app.toggle_focus_mode()

    def update_focus_btn(self, is_focused):
        """Update focus button appearance based on state."""
        if is_focused:
            self.focus_btn.configure(
                text="↩️ Exit Focus", fg_color=COLORS["accent"]
            )
        else:
            self.focus_btn.configure(
                text="🖥️ Focus Mode", fg_color=COLORS["bg_card"]
            )

    # ── Note management ───────────────────────────────────────────

    def _refresh_note_selector(self):
        """Refresh the dropdown list of saved notes."""
        notes = db.get_all_notes()
        self._notes_map = {}
        values = ["— New Note —"]
        for n in notes:
            label = n["title"][:50] + ("..." if len(n["title"]) > 50 else "")
            values.append(label)
            self._notes_map[label] = n["id"]
        self.note_selector.configure(values=values)

    def _on_note_selected(self, choice):
        """Load a selected note into the editor."""
        if choice == "— New Note —":
            self._new_note()
            return

        note_id = self._notes_map.get(choice)
        if not note_id:
            return

        note = db.get_note(note_id)
        if not note:
            return

        self.current_note_id = note_id
        self.title_entry.delete(0, "end")
        self.title_entry.insert(0, note["title"])
        self.editor.delete("1.0", "end")
        self.editor.insert("1.0", note["content"])
        self.status_label.configure(text=f"Loaded: {note['title'][:30]}", text_color=COLORS["text_muted"])

        if self.preview_visible:
            self._render_preview()

    def _new_note(self):
        """Clear editor for a new note."""
        self.current_note_id = None
        self.title_entry.delete(0, "end")
        self.editor.delete("1.0", "end")
        self.status_label.configure(text="New note", text_color=COLORS["text_muted"])
        self.note_selector.set("— New Note —")

        if self.preview_visible:
            self._render_preview()

    def _save_note(self):
        """Save the current note to the database."""
        title = self.title_entry.get().strip() or "Untitled Note"
        content = self.editor.get("1.0", "end").strip()

        if not content:
            self.status_label.configure(text="⚠️ Nothing to save", text_color=COLORS["warning"])
            return

        if self.current_note_id:
            db.update_note(self.current_note_id, title=title, content=content)
            self.status_label.configure(text=f"✅ Saved: {title[:30]}", text_color=COLORS["success"])
        else:
            new_id = db.add_note(title, content)
            self.current_note_id = new_id
            self.status_label.configure(text=f"✅ Created: {title[:30]}", text_color=COLORS["success"])

        self._refresh_note_selector()

    def _delete_current_note(self):
        """Delete the currently loaded note."""
        if not self.current_note_id:
            return

        dialog = ctk.CTkToplevel(self)
        dialog.title("Confirm Delete")
        dialog.geometry("380x150")
        dialog.configure(fg_color=COLORS["bg_primary"])
        dialog.attributes("-topmost", True)
        dialog.grab_set()

        ctk.CTkLabel(
            dialog, text="⚠️ Delete this note?\nThis cannot be undone.",
            font=FONTS["body"], text_color=COLORS["text_primary"], justify="center"
        ).pack(pady=(20, 15))

        btn_row = ctk.CTkFrame(dialog, fg_color="transparent")
        btn_row.pack()

        def confirm():
            db.delete_note(self.current_note_id)
            self._new_note()
            self._refresh_note_selector()
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

    def refresh(self):
        """Called when tab is switched to — refresh note list."""
        self._refresh_note_selector()
        if self.preview_visible:
            self._render_preview()
        if self.nav_visible:
            self._refresh_navigator()
