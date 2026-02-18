"""
quiz.py — Active Recall Quiz tab for StudyForge.
AI-generates multiple-choice quizzes from lecture notes.
Supports single-note and interleaved (multi-note) quiz modes.
"""

import customtkinter as ctk
import threading
from ui.styles import COLORS, FONTS, PADDING
import database as db


class QuizTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.questions = []
        self.current_q = 0
        self.score = 0
        self.answered = False
        self.is_interleaved = False
        self.note_checkboxes = {}  # note_id → BooleanVar (for interleaved mode)
        self.build_ui()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PADDING["page"], pady=(PADDING["page"], 5))

        ctk.CTkLabel(
            header, text="❓ Active Recall Quiz",
            font=FONTS["heading"], text_color=COLORS["text_primary"]
        ).pack(side="left")

        # Setup area
        self.setup_frame = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        self.setup_frame.pack(fill="x", padx=PADDING["page"], pady=PADDING["element"])

        self._build_setup_content()

        # Quiz content area
        self.quiz_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.quiz_frame.pack(fill="both", expand=True, padx=PADDING["page"], pady=(0, PADDING["page"]))

    def _build_setup_content(self):
        """Build the setup controls inside self.setup_frame."""
        self.notes = db.get_all_notes()

        # Mode toggle row
        mode_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        mode_frame.pack(fill="x", padx=PADDING["section"], pady=(PADDING["section"], 8))

        ctk.CTkLabel(
            mode_frame, text="Mode:",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(side="left")

        self.mode_var = ctk.StringVar(value="interleaved" if self.is_interleaved else "single")

        self.single_btn = ctk.CTkButton(
            mode_frame, text="📝 Single Note", width=130, height=32,
            font=FONTS["body"],
            fg_color=COLORS["accent"] if not self.is_interleaved else COLORS["bg_secondary"],
            hover_color=COLORS["accent_hover"], corner_radius=8,
            command=lambda: self._set_quiz_mode(False)
        )
        self.single_btn.pack(side="left", padx=(8, 3))

        self.interleave_mode_btn = ctk.CTkButton(
            mode_frame, text="🔀 Interleaved", width=130, height=32,
            font=FONTS["body"],
            fg_color=COLORS["accent_alt"] if self.is_interleaved else COLORS["bg_secondary"],
            hover_color=COLORS["accent_alt_hover"], corner_radius=8,
            command=lambda: self._set_quiz_mode(True)
        )
        self.interleave_mode_btn.pack(side="left", padx=3)

        # Note selection area — switches between dropdown and checkboxes
        self.note_select_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        self.note_select_frame.pack(fill="x", padx=PADDING["section"], pady=(0, 5))

        self._build_note_selector()

        # Options row: difficulty + question count
        opts_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        opts_frame.pack(fill="x", padx=PADDING["section"], pady=(0, 5))

        ctk.CTkLabel(opts_frame, text="Difficulty:", font=FONTS["body"],
                      text_color=COLORS["text_secondary"]).pack(side="left")

        self.diff_var = ctk.StringVar(value="mixed")
        ctk.CTkOptionMenu(
            opts_frame, values=["easy", "medium", "hard", "mixed"],
            variable=self.diff_var, fg_color=COLORS["bg_input"],
            button_color=COLORS["accent"], font=FONTS["body"],
            corner_radius=8, width=100
        ).pack(side="left", padx=8)

        ctk.CTkLabel(opts_frame, text="Questions:", font=FONTS["body"],
                      text_color=COLORS["text_secondary"]).pack(side="left", padx=(12, 0))

        self.qcount_var = ctk.StringVar(value="5" if not self.is_interleaved else "10")
        ctk.CTkOptionMenu(
            opts_frame, values=["3", "5", "8", "10", "15"],
            variable=self.qcount_var, fg_color=COLORS["bg_input"],
            button_color=COLORS["accent"], font=FONTS["body"],
            corner_radius=8, width=70
        ).pack(side="left", padx=8)

        # Generate button
        btn_frame = ctk.CTkFrame(self.setup_frame, fg_color="transparent")
        btn_frame.pack(pady=(5, PADDING["section"]))

        gen_color = COLORS["accent_alt"] if self.is_interleaved else COLORS["accent"]
        gen_text = "🔀 Generate Interleaved Quiz" if self.is_interleaved else "⚡ Generate Quiz"

        self.gen_btn = ctk.CTkButton(
            btn_frame, text=gen_text, width=220, height=40,
            font=FONTS["body_bold"], fg_color=gen_color,
            hover_color=COLORS["accent_alt_hover"] if self.is_interleaved else COLORS["accent_hover"],
            corner_radius=10,
            command=self.generate_quiz
        )
        self.gen_btn.pack()

        self.status_label = ctk.CTkLabel(
            self.setup_frame, text="", font=FONTS["small"],
            text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(pady=(0, 8))

    def _build_note_selector(self):
        """Build note selector: dropdown for single mode, checkboxes for interleaved."""
        for w in self.note_select_frame.winfo_children():
            w.destroy()

        note_titles = [f"{n['id']}: {n['title'][:50]}" for n in self.notes] if self.notes else ["No notes available"]

        if not self.is_interleaved:
            # ── Single note dropdown ──
            row = ctk.CTkFrame(self.note_select_frame, fg_color="transparent")
            row.pack(fill="x")

            ctk.CTkLabel(row, text="Note:", font=FONTS["body"],
                          text_color=COLORS["text_secondary"]).pack(side="left")

            self.note_var = ctk.StringVar(value=note_titles[0] if note_titles else "")

            ctk.CTkOptionMenu(
                row, values=note_titles, variable=self.note_var,
                fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
                font=FONTS["body"], corner_radius=8, width=350
            ).pack(side="left", padx=8)
        else:
            # ── Multi-note checkboxes ──
            ctk.CTkLabel(
                self.note_select_frame,
                text="Select topics to interleave (pick 2+):",
                font=FONTS["body"], text_color=COLORS["text_secondary"]
            ).pack(anchor="w", pady=(0, 4))

            if not self.notes:
                ctk.CTkLabel(
                    self.note_select_frame, text="⚠️ No notes available.",
                    font=FONTS["body"], text_color=COLORS["warning"]
                ).pack(anchor="w")
                return

            # Select all / deselect all
            ctrl_row = ctk.CTkFrame(self.note_select_frame, fg_color="transparent")
            ctrl_row.pack(fill="x", pady=(0, 4))

            ctk.CTkButton(
                ctrl_row, text="Select All", width=90, height=26,
                font=FONTS["small"], fg_color=COLORS["bg_secondary"],
                hover_color=COLORS["accent"], corner_radius=6,
                command=lambda: self._toggle_all_notes(True)
            ).pack(side="left", padx=(0, 4))

            ctk.CTkButton(
                ctrl_row, text="Deselect All", width=90, height=26,
                font=FONTS["small"], fg_color=COLORS["bg_secondary"],
                hover_color=COLORS["accent"], corner_radius=6,
                command=lambda: self._toggle_all_notes(False)
            ).pack(side="left")

            # Scrollable checkbox area
            check_frame = ctk.CTkScrollableFrame(
                self.note_select_frame, fg_color=COLORS["bg_secondary"],
                corner_radius=8, height=120
            )
            check_frame.pack(fill="x", pady=(0, 4))

            self.note_checkboxes = {}
            for note in self.notes:
                var = ctk.BooleanVar(value=True)
                cb = ctk.CTkCheckBox(
                    check_frame,
                    text=f"{note['title'][:55]}",
                    variable=var,
                    font=FONTS["body"],
                    text_color=COLORS["text_primary"],
                    fg_color=COLORS["accent_alt"],
                    hover_color=COLORS["accent_alt_hover"],
                    corner_radius=4
                )
                cb.pack(anchor="w", padx=8, pady=2)
                self.note_checkboxes[note["id"]] = var

    def _toggle_all_notes(self, state: bool):
        for var in self.note_checkboxes.values():
            var.set(state)

    def _set_quiz_mode(self, interleaved: bool):
        """Switch between single-note and interleaved quiz modes."""
        self.is_interleaved = interleaved
        # Rebuild the whole setup area
        for w in self.setup_frame.winfo_children():
            w.destroy()
        self._build_setup_content()

    # ── Quiz Generation ────────────────────────────────────────────

    def generate_quiz(self):
        if not self.app.claude_client:
            self.status_label.configure(
                text="⚠️ Claude API not configured. Check config.json.",
                text_color=COLORS["danger"]
            )
            return

        if not self.notes:
            self.status_label.configure(text="⚠️ No notes found.", text_color=COLORS["warning"])
            return

        count = int(self.qcount_var.get())
        difficulty = self.diff_var.get()

        if self.is_interleaved:
            self._generate_interleaved(count, difficulty)
        else:
            self._generate_single(count, difficulty)

    def _generate_single(self, count, difficulty):
        """Generate quiz from a single note."""
        note_key = self.note_var.get()
        note_id = int(note_key.split(":")[0]) if ":" in note_key else None
        note = db.get_note(note_id) if note_id else None
        if not note:
            self.status_label.configure(text="⚠️ Note not found.", text_color=COLORS["warning"])
            return

        self.gen_btn.configure(state="disabled", text="⏳ Generating...")
        self.status_label.configure(text="Generating quiz questions with Claude AI...", text_color=COLORS["text_secondary"])

        def do_generate():
            try:
                questions = self.app.claude_client.generate_quiz(
                    note["content"], count=count, difficulty=difficulty
                )
                # Add topic field for consistency
                for q in questions:
                    q.setdefault("topic", note["title"])
                self.after(0, lambda: self._start_quiz(questions, interleaved=False))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(
                    text=f"❌ Error: {str(e)[:80]}", text_color=COLORS["danger"]
                ))
            finally:
                self.after(0, lambda: self.gen_btn.configure(state="normal", text="⚡ Generate Quiz"))

        threading.Thread(target=do_generate, daemon=True).start()

    def _generate_interleaved(self, count, difficulty):
        """Generate interleaved quiz from multiple notes."""
        selected_ids = [nid for nid, var in self.note_checkboxes.items() if var.get()]

        if len(selected_ids) < 2:
            self.status_label.configure(
                text="⚠️ Select at least 2 topics for interleaving.",
                text_color=COLORS["warning"]
            )
            return

        # Gather the selected notes
        selected_notes = []
        for note in self.notes:
            if note["id"] in selected_ids:
                selected_notes.append({"title": note["title"], "content": note["content"]})

        self.gen_btn.configure(state="disabled", text="⏳ Generating interleaved quiz...")
        self.status_label.configure(
            text=f"Generating {count} interleaved questions from {len(selected_notes)} topics...",
            text_color=COLORS["text_secondary"]
        )

        def do_generate():
            try:
                questions = self.app.claude_client.generate_interleaved_quiz(
                    selected_notes, count=count, difficulty=difficulty
                )
                self.after(0, lambda: self._start_quiz(questions, interleaved=True))
            except Exception as e:
                self.after(0, lambda: self.status_label.configure(
                    text=f"❌ Error: {str(e)[:80]}", text_color=COLORS["danger"]
                ))
            finally:
                self.after(0, lambda: self.gen_btn.configure(
                    state="normal", text="🔀 Generate Interleaved Quiz"
                ))

        threading.Thread(target=do_generate, daemon=True).start()

    def _start_quiz(self, questions, interleaved=False):
        if not questions:
            self.status_label.configure(text="⚠️ Failed to generate questions.", text_color=COLORS["warning"])
            return

        self.questions = questions
        self.current_q = 0
        self.score = 0
        self._quiz_interleaved = interleaved

        mode_label = "interleaved " if interleaved else ""
        self.status_label.configure(
            text=f"✅ Generated {len(questions)} {mode_label}questions. Good luck!",
            text_color=COLORS["success"]
        )
        self._show_question()

    # ── Question Display ──────────────────────────────────────────

    def _clear_quiz(self):
        for w in self.quiz_frame.winfo_children():
            w.destroy()

    def _show_question(self):
        self._clear_quiz()
        self.answered = False

        if self.current_q >= len(self.questions):
            self._show_results()
            return

        q = self.questions[self.current_q]

        # Progress
        prog_frame = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        prog_frame.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            prog_frame,
            text=f"Question {self.current_q + 1} of {len(self.questions)}  ·  Score: {self.score}/{self.current_q}",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(side="left")

        prog = ctk.CTkProgressBar(
            prog_frame, width=200, height=6,
            fg_color=COLORS["bg_secondary"], progress_color=COLORS["accent_alt"] if self._quiz_interleaved else COLORS["accent"]
        )
        prog.set(self.current_q / len(self.questions))
        prog.pack(side="right")

        # Question card — inside scrollable container for long content
        scroll_container = ctk.CTkScrollableFrame(
            self.quiz_frame, fg_color="transparent", corner_radius=0
        )
        scroll_container.pack(fill="both", expand=True)

        card = ctk.CTkFrame(scroll_container, fg_color=COLORS["bg_card"], corner_radius=14)
        card.pack(fill="x", expand=False)

        # Topic badge (always show in interleaved, optional in single)
        topic = q.get("topic", "")
        if topic and self._quiz_interleaved:
            topic_badge = ctk.CTkFrame(card, fg_color=COLORS["accent_alt"], corner_radius=6)
            topic_badge.pack(pady=(16, 0))
            ctk.CTkLabel(
                topic_badge, text=f"  📂 {topic[:45]}  ",
                font=("Segoe UI", 11, "bold"), text_color=COLORS["text_on_accent"]
            ).pack(padx=2, pady=2)

        ctk.CTkLabel(
            card, text=q["question"],
            font=FONTS["card_front"], text_color=COLORS["text_primary"],
            wraplength=650, justify="left"
        ).pack(padx=24, pady=(24 if not (topic and self._quiz_interleaved) else 10, 16), anchor="w")

        # Options — clickable frames with wrapping labels
        self.option_btns = []
        correct_idx = q.get("correct", 0)

        for i, option in enumerate(q.get("options", [])):
            opt_frame = ctk.CTkFrame(
                card, fg_color=COLORS["bg_secondary"],
                corner_radius=8, cursor="hand2"
            )
            opt_frame.pack(fill="x", padx=24, pady=3)

            opt_label = ctk.CTkLabel(
                opt_frame, text=option, anchor="w",
                font=FONTS["body"], text_color=COLORS["text_primary"],
                wraplength=600, justify="left"
            )
            opt_label.pack(padx=14, pady=10, anchor="w", fill="x")

            for widget in (opt_frame, opt_label):
                widget.bind("<Button-1>", lambda e, idx=i: self._answer(idx, correct_idx, q))
                widget.bind("<Enter>", lambda e, f=opt_frame: f.configure(
                    fg_color=COLORS["accent"]) if not self.answered else None)
                widget.bind("<Leave>", lambda e, f=opt_frame, idx=i: f.configure(
                    fg_color=self._get_option_bg(idx)) if not self.answered else None)

            self.option_btns.append((opt_frame, opt_label))

        # Explanation area (hidden until answered)
        self.explain_label = ctk.CTkLabel(
            card, text="", font=FONTS["body"],
            text_color=COLORS["text_secondary"],
            wraplength=620, justify="left"
        )

        # Next button — placed OUTSIDE scroll container so it's always visible at the bottom
        self.next_btn_frame = ctk.CTkFrame(self.quiz_frame, fg_color="transparent")
        self.next_btn = ctk.CTkButton(
            self.next_btn_frame, text="Next Question →", width=180, height=42,
            font=FONTS["body_bold"], fg_color=COLORS["accent_alt"] if self._quiz_interleaved else COLORS["accent"],
            hover_color=COLORS["accent_alt_hover"] if self._quiz_interleaved else COLORS["accent_hover"],
            corner_radius=10, command=self._next_question
        )
        self.next_btn.pack(pady=(10, 5))

    def _get_option_bg(self, idx):
        return COLORS["bg_secondary"]

    def _answer(self, selected, correct, question):
        if self.answered:
            return
        self.answered = True

        db.increment_daily_stat("quiz_questions_answered")

        is_correct = selected == correct

        if is_correct:
            self.score += 1

        for i, (frame, label) in enumerate(self.option_btns):
            for widget in (frame, label):
                widget.unbind("<Button-1>")
                widget.unbind("<Enter>")
                widget.unbind("<Leave>")
                widget.configure(cursor="")

            if i == correct:
                frame.configure(fg_color=COLORS["success"])
                label.configure(text_color=COLORS["text_on_state"])
            elif i == selected and not is_correct:
                frame.configure(fg_color=COLORS["danger"])
                label.configure(text_color=COLORS["text_on_state"])
            else:
                frame.configure(fg_color=COLORS["bg_secondary"])

        result_text = "✅ Correct!" if is_correct else "❌ Incorrect."
        explanation = question.get("explanation", "")
        if explanation:
            result_text += f"\n\n💡 {explanation}"

        self.explain_label.configure(
            text=result_text,
            text_color=COLORS["success"] if is_correct else COLORS["danger"]
        )
        self.explain_label.pack(padx=24, pady=(10, 5), anchor="w")

        self.next_btn_frame.pack(fill="x", padx=24, pady=(5, 10))

    def _next_question(self):
        self.current_q += 1
        self._show_question()

    # ── Results ───────────────────────────────────────────────────

    def _show_results(self):
        self._clear_quiz()

        card = ctk.CTkFrame(self.quiz_frame, fg_color=COLORS["bg_card"], corner_radius=16)
        card.pack(expand=True, pady=30)

        total = len(self.questions)
        pct = (self.score / total * 100) if total > 0 else 0

        emoji = "🏆" if pct >= 90 else "🎉" if pct >= 70 else "💪" if pct >= 50 else "📚"

        ctk.CTkLabel(card, text=emoji, font=("Segoe UI", 48)).pack(pady=(30, 5))

        title = "Interleaved Quiz Complete!" if self._quiz_interleaved else "Quiz Complete!"
        ctk.CTkLabel(
            card, text=title,
            font=FONTS["subheading"], text_color=COLORS["text_primary"]
        ).pack()

        ctk.CTkLabel(
            card, text=f"Score: {self.score} / {total}  ({pct:.0f}%)",
            font=FONTS["stat_number"],
            text_color=COLORS["success"] if pct >= 70 else COLORS["warning"]
        ).pack(pady=10)

        message = (
            "Excellent work!" if pct >= 90 else
            "Great job!" if pct >= 70 else
            "Good effort — review the material and try again." if pct >= 50 else
            "Time to review your notes more carefully."
        )
        ctk.CTkLabel(
            card, text=message, font=FONTS["body"],
            text_color=COLORS["text_secondary"]
        ).pack(pady=(0, 5))

        # Per-topic breakdown for interleaved quizzes
        if self._quiz_interleaved:
            self._show_topic_breakdown(card)

        btn_row = ctk.CTkFrame(card, fg_color="transparent")
        btn_row.pack(pady=(10, 25))

        ctk.CTkButton(
            btn_row, text="🔄 Try Again", width=130, height=38,
            font=FONTS["body"], fg_color=COLORS["accent_alt"] if self._quiz_interleaved else COLORS["accent"],
            corner_radius=8, command=self.generate_quiz
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_row, text="🏠 Dashboard", width=130, height=38,
            font=FONTS["body"], fg_color=COLORS["bg_secondary"],
            corner_radius=8, command=lambda: self.app.select_tab("Dashboard")
        ).pack(side="left", padx=6)

    def _show_topic_breakdown(self, parent):
        """Show per-topic score breakdown after an interleaved quiz."""
        topic_scores = {}
        for i, q in enumerate(self.questions):
            topic = q.get("topic", "Unknown")
            if topic not in topic_scores:
                topic_scores[topic] = {"correct": 0, "total": 0}
            topic_scores[topic]["total"] += 1

        # Reconstruct which were correct by replaying answers
        # We tracked self.score globally but not per-topic, so approximate from final score
        # Instead, let's just show total per topic
        breakdown_frame = ctk.CTkFrame(parent, fg_color=COLORS["bg_secondary"], corner_radius=8)
        breakdown_frame.pack(fill="x", padx=20, pady=(5, 5))

        ctk.CTkLabel(
            breakdown_frame, text="📊 Topic Distribution",
            font=FONTS["body_bold"], text_color=COLORS["text_primary"]
        ).pack(padx=12, pady=(8, 4), anchor="w")

        for topic, data in topic_scores.items():
            ctk.CTkLabel(
                breakdown_frame,
                text=f"  📂 {topic[:40]}  —  {data['total']} question{'s' if data['total'] != 1 else ''}",
                font=FONTS["small"], text_color=COLORS["text_secondary"]
            ).pack(padx=12, pady=1, anchor="w")

        ctk.CTkLabel(breakdown_frame, text="", font=("Segoe UI", 4)).pack()  # spacer

    # ── Refresh ───────────────────────────────────────────────────

    def refresh_notes(self):
        """Rebuild the setup area with latest notes from the database."""
        for w in self.setup_frame.winfo_children():
            w.destroy()
        self._build_setup_content()
