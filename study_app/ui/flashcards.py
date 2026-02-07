"""
flashcards.py — Flashcard Review & Management tab for StudyForge.
Supports manual creation, AI generation, and SM-2 spaced repetition review.
"""

import customtkinter as ctk
import threading
import random
from ui.styles import COLORS, FONTS, PADDING
import database as db
from srs_engine import review_card, get_rating_labels


class FlashcardsTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.current_cards = []
        self.card_index = 0
        self.showing_answer = False
        self.mode = "review"  # "review", "interleaved", "browse"
        self.is_interleaved = False

        self.build_ui()

    def build_ui(self):
        # Header with mode toggle
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PADDING["page"], pady=(PADDING["page"], 5))

        ctk.CTkLabel(
            header, text="🧠 Flashcards",
            font=FONTS["heading"], text_color=COLORS["text_primary"]
        ).pack(side="left")

        btn_row = ctk.CTkFrame(header, fg_color="transparent")
        btn_row.pack(side="right")

        self.review_btn = ctk.CTkButton(
            btn_row, text="📖 Review Due", width=120, height=34,
            font=FONTS["body"], fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], corner_radius=8,
            command=self.start_review
        )
        self.review_btn.pack(side="left", padx=4)

        self.interleave_btn = ctk.CTkButton(
            btn_row, text="🔀 Interleaved", width=120, height=34,
            font=FONTS["body"], fg_color="#8b5cf6",
            hover_color="#7c3aed", corner_radius=8,
            command=self.start_interleaved_review
        )
        self.interleave_btn.pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row, text="➕ New Card", width=110, height=34,
            font=FONTS["body"], fg_color=COLORS["success"],
            hover_color="#00d2a0", corner_radius=8,
            command=self.show_create_dialog
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row, text="🤖 AI Generate", width=120, height=34,
            font=FONTS["body"], fg_color=COLORS["warning"],
            hover_color="#f0be50", corner_radius=8,
            command=self.show_ai_generate_dialog
        ).pack(side="left", padx=4)

        ctk.CTkButton(
            btn_row, text="📋 Browse All", width=110, height=34,
            font=FONTS["body"], fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_secondary"], corner_radius=8,
            command=self.show_browse_mode
        ).pack(side="left", padx=4)

        # Status bar
        self.status_label = ctk.CTkLabel(
            self, text="", font=FONTS["body"], text_color=COLORS["text_secondary"]
        )
        self.status_label.pack(padx=PADDING["page"], anchor="w")

        # Main content frame (switches between review and browse)
        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=PADDING["page"], pady=PADDING["element"])

        self.start_review()

    def _clear_content(self):
        for w in self.content.winfo_children():
            w.destroy()

    # ── Review Mode ───────────────────────────────────────────────

    def start_review(self):
        self._clear_content()
        self.mode = "review"
        self.is_interleaved = False
        self.current_cards = db.get_due_cards()
        self.card_index = 0
        self.showing_answer = False

        due_count = len(self.current_cards)
        self.status_label.configure(text=f"📋 {due_count} card{'s' if due_count != 1 else ''} due for review")
        self.review_btn.configure(fg_color=COLORS["accent"])
        self.interleave_btn.configure(fg_color="#8b5cf6")

        if due_count == 0:
            self._show_empty_state()
        else:
            self._show_card()

    def start_interleaved_review(self):
        """Interleaved review: shuffle due cards across all topics."""
        self._clear_content()
        self.mode = "interleaved"
        self.is_interleaved = True
        self.current_cards = db.get_due_cards_with_topics()
        random.shuffle(self.current_cards)
        self.card_index = 0
        self.showing_answer = False

        due_count = len(self.current_cards)
        # Count unique topics
        topics = set(c.get("note_title", "Unlinked") for c in self.current_cards)
        topic_count = len(topics)
        self.status_label.configure(
            text=f"🔀 Interleaved: {due_count} card{'s' if due_count != 1 else ''} across {topic_count} topic{'s' if topic_count != 1 else ''}"
        )
        self.interleave_btn.configure(fg_color=COLORS["accent"])
        self.review_btn.configure(fg_color="#8b5cf6")

        if due_count == 0:
            self._show_empty_state()
        elif topic_count < 2:
            self._show_interleave_warning(due_count)
        else:
            self._show_card()

    def _show_interleave_warning(self, due_count):
        """Show a notice when there's only one topic — interleaving has limited benefit."""
        self._clear_content()
        frame = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=16)
        frame.pack(expand=True, pady=40)

        ctk.CTkLabel(frame, text="🔀", font=("Segoe UI", 40)).pack(pady=(25, 5))
        ctk.CTkLabel(
            frame, text="Only one topic found",
            font=FONTS["subheading"], text_color=COLORS["warning"]
        ).pack()
        ctk.CTkLabel(
            frame,
            text=f"You have {due_count} due card(s), but they're all from the same topic.\n"
                 "Interleaving works best with 2+ topics. You can still review them shuffled.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
            justify="center", wraplength=450
        ).pack(padx=30, pady=(5, 15))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(pady=(0, 25))

        ctk.CTkButton(
            btn_row, text="Review Shuffled Anyway", width=180, height=38,
            font=FONTS["body_bold"], fg_color="#8b5cf6",
            hover_color="#7c3aed", corner_radius=8,
            command=self._show_card
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_row, text="Normal Review", width=140, height=38,
            font=FONTS["body"], fg_color=COLORS["bg_secondary"],
            corner_radius=8, command=self.start_review
        ).pack(side="left", padx=6)

    def _show_empty_state(self):
        self._clear_content()
        frame = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=16)
        frame.pack(expand=True, pady=40)

        ctk.CTkLabel(
            frame, text="✨", font=("Segoe UI", 48)
        ).pack(pady=(30, 5))
        ctk.CTkLabel(
            frame, text="All caught up!",
            font=FONTS["subheading"], text_color=COLORS["success"]
        ).pack()
        ctk.CTkLabel(
            frame, text="No cards are due for review right now.\nAdd new cards or import notes to generate more.",
            font=FONTS["body"], text_color=COLORS["text_secondary"],
            justify="center"
        ).pack(padx=40, pady=(5, 30))

    def _show_card(self):
        self._clear_content()
        if self.card_index >= len(self.current_cards):
            self._show_review_complete()
            return

        card = self.current_cards[self.card_index]
        remaining = len(self.current_cards) - self.card_index

        # Progress
        progress_frame = ctk.CTkFrame(self.content, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(
            progress_frame,
            text=f"Card {self.card_index + 1} of {len(self.current_cards)}  ·  {remaining} remaining",
            font=FONTS["small"], text_color=COLORS["text_muted"]
        ).pack(side="left")

        prog = ctk.CTkProgressBar(
            progress_frame, width=200, height=6,
            fg_color=COLORS["bg_secondary"], progress_color=COLORS["accent"]
        )
        prog.set(self.card_index / len(self.current_cards))
        prog.pack(side="right")

        # Card
        card_frame = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=16)
        card_frame.pack(fill="both", expand=True, pady=5)

        # Topic badge for interleaved mode
        if self.is_interleaved and card.get("note_title"):
            topic_badge = ctk.CTkFrame(card_frame, fg_color="#8b5cf6", corner_radius=6)
            topic_badge.pack(pady=(15, 0))
            ctk.CTkLabel(
                topic_badge, text=f"  📂 {card['note_title'][:45]}  ",
                font=("Segoe UI", 11, "bold"), text_color="#ffffff"
            ).pack(padx=2, pady=2)

        # Front (question)
        ctk.CTkLabel(
            card_frame, text="QUESTION",
            font=FONTS["small"], text_color=COLORS["accent_light"]
        ).pack(pady=(20 if not self.is_interleaved else 8, 5))

        ctk.CTkLabel(
            card_frame, text=card["front"],
            font=FONTS["card_front"], text_color=COLORS["text_primary"],
            wraplength=600, justify="center"
        ).pack(padx=30, pady=(0, 15))

        if self.showing_answer:
            # Divider
            ctk.CTkFrame(
                card_frame, height=1, fg_color=COLORS["border"]
            ).pack(fill="x", padx=30, pady=5)

            ctk.CTkLabel(
                card_frame, text="ANSWER",
                font=FONTS["small"], text_color=COLORS["success"]
            ).pack(pady=(10, 5))

            ctk.CTkLabel(
                card_frame, text=card["back"],
                font=FONTS["card_back"], text_color=COLORS["text_primary"],
                wraplength=600, justify="center"
            ).pack(padx=30, pady=(0, 15))

            # Rating buttons
            ctk.CTkLabel(
                card_frame, text="How well did you recall?",
                font=FONTS["small"], text_color=COLORS["text_muted"]
            ).pack(pady=(10, 5))

            rating_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            rating_frame.pack(pady=(0, 20))

            labels = get_rating_labels()
            rating_colors = [
                COLORS["rating_0"], COLORS["rating_1"], COLORS["rating_2"],
                COLORS["rating_3"], COLORS["rating_4"], COLORS["rating_5"]
            ]

            for rating_val in range(6):
                label_text, tooltip = labels[rating_val]
                btn = ctk.CTkButton(
                    rating_frame, text=f"{rating_val}\n{label_text}",
                    width=75, height=55, font=FONTS["small"],
                    fg_color=rating_colors[rating_val],
                    hover_color=COLORS["accent_hover"],
                    text_color="#1a1a2e",
                    corner_radius=8,
                    command=lambda r=rating_val: self._rate_card(r)
                )
                btn.pack(side="left", padx=3)
        else:
            # Show answer button
            ctk.CTkButton(
                card_frame, text="Show Answer",
                width=200, height=45, font=FONTS["body_bold"],
                fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
                corner_radius=10,
                command=self._reveal_answer
            ).pack(pady=(10, 25))

    def _reveal_answer(self):
        self.showing_answer = True
        self._show_card()

    def _rate_card(self, rating):
        card = self.current_cards[self.card_index]
        review_card(card, rating)

        # If failed, re-add to end of queue
        if rating < 3:
            if self.is_interleaved:
                refreshed = db.get_due_cards_with_topics()
            else:
                refreshed = db.get_due_cards()
            failed = [c for c in refreshed if c["id"] == card["id"]]
            if failed:
                self.current_cards.append(failed[0])

        self.card_index += 1
        self.showing_answer = False
        self._show_card()

    def _show_review_complete(self):
        self._clear_content()
        frame = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=16)
        frame.pack(expand=True, pady=40)

        ctk.CTkLabel(frame, text="🎉", font=("Segoe UI", 48)).pack(pady=(30, 5))

        title = "Interleaved session complete!" if self.is_interleaved else "Review session complete!"
        ctk.CTkLabel(
            frame, text=title,
            font=FONTS["subheading"], text_color=COLORS["success"]
        ).pack()

        stats = db.get_today_stats()
        ctk.CTkLabel(
            frame, text=f"Cards reviewed today: {stats['cards_reviewed']}",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(pady=(5, 20))

        ctk.CTkButton(
            frame, text="Back to Dashboard", width=160, height=38,
            font=FONTS["body"], fg_color=COLORS["accent"],
            command=lambda: self.app.select_tab("Dashboard")
        ).pack(pady=(0, 25))

    # ── Browse Mode ──────────────────────────────────────────────

    def show_browse_mode(self):
        self._clear_content()
        self.mode = "browse"

        all_cards = db.get_all_flashcards()
        self.status_label.configure(text=f"📋 {len(all_cards)} total card{'s' if len(all_cards) != 1 else ''} in collection")

        if not all_cards:
            frame = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=16)
            frame.pack(expand=True, pady=40)
            ctk.CTkLabel(frame, text="No flashcards yet.", font=FONTS["body"],
                          text_color=COLORS["text_muted"]).pack(padx=40, pady=30)
            return

        scroll = ctk.CTkScrollableFrame(
            self.content, fg_color="transparent", corner_radius=8
        )
        scroll.pack(fill="both", expand=True)

        for card in all_cards:
            card_frame = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=8)
            card_frame.pack(fill="x", padx=4, pady=3)

            text_frame = ctk.CTkFrame(card_frame, fg_color="transparent")
            text_frame.pack(side="left", fill="both", expand=True, padx=10, pady=8)

            ctk.CTkLabel(
                text_frame, text=f"Q: {card['front'][:100]}",
                font=FONTS["body_bold"], text_color=COLORS["text_primary"],
                wraplength=500, justify="left", anchor="w"
            ).pack(anchor="w")

            ctk.CTkLabel(
                text_frame, text=f"A: {card['back'][:100]}",
                font=FONTS["small"], text_color=COLORS["text_secondary"],
                wraplength=500, justify="left", anchor="w"
            ).pack(anchor="w")

            meta = f"EF: {card['easiness_factor']:.1f}  ·  Next: {card['next_review']}"
            ctk.CTkLabel(
                text_frame, text=meta,
                font=("Segoe UI", 10), text_color=COLORS["text_muted"], anchor="w"
            ).pack(anchor="w")

            ctk.CTkButton(
                card_frame, text="🗑️", width=36, height=36,
                font=FONTS["small"], fg_color=COLORS["danger"],
                hover_color="#c0392b", corner_radius=6,
                command=lambda cid=card["id"]: self._delete_card_from_browse(cid)
            ).pack(side="right", padx=8, pady=8)

    def _delete_card_from_browse(self, card_id):
        db.delete_flashcard(card_id)
        self.show_browse_mode()  # Refresh the list

    # ── Create Card Dialog ────────────────────────────────────────

    def show_create_dialog(self):
        self._clear_content()
        self.mode = "create"

        frame = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=12)
        frame.pack(fill="both", expand=True, pady=5)

        ctk.CTkLabel(
            frame, text="✏️ Create New Flashcard",
            font=FONTS["subheading"], text_color=COLORS["text_primary"]
        ).pack(padx=PADDING["section"], pady=(PADDING["section"], 10), anchor="w")

        ctk.CTkLabel(frame, text="Front (Question):", font=FONTS["body"],
                      text_color=COLORS["text_secondary"]).pack(padx=PADDING["section"], anchor="w")
        self.front_input = ctk.CTkTextbox(
            frame, height=80, fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], font=FONTS["body"],
            border_color=COLORS["border"], border_width=1, corner_radius=8
        )
        self.front_input.pack(fill="x", padx=PADDING["section"], pady=(2, 8))

        ctk.CTkLabel(frame, text="Back (Answer):", font=FONTS["body"],
                      text_color=COLORS["text_secondary"]).pack(padx=PADDING["section"], anchor="w")
        self.back_input = ctk.CTkTextbox(
            frame, height=80, fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], font=FONTS["body"],
            border_color=COLORS["border"], border_width=1, corner_radius=8
        )
        self.back_input.pack(fill="x", padx=PADDING["section"], pady=(2, 8))

        ctk.CTkLabel(frame, text="Tags (comma-separated):", font=FONTS["body"],
                      text_color=COLORS["text_secondary"]).pack(padx=PADDING["section"], anchor="w")
        self.tags_input = ctk.CTkEntry(
            frame, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], border_color=COLORS["border"], corner_radius=8
        )
        self.tags_input.pack(fill="x", padx=PADDING["section"], pady=(2, 8))

        btn_row = ctk.CTkFrame(frame, fg_color="transparent")
        btn_row.pack(pady=PADDING["section"])

        ctk.CTkButton(
            btn_row, text="💾 Save Card", width=140, height=38,
            font=FONTS["body_bold"], fg_color=COLORS["success"],
            corner_radius=8, command=self._save_card
        ).pack(side="left", padx=6)

        ctk.CTkButton(
            btn_row, text="Cancel", width=100, height=38,
            font=FONTS["body"], fg_color=COLORS["bg_secondary"],
            corner_radius=8, command=self.start_review
        ).pack(side="left", padx=6)

        self.create_status = ctk.CTkLabel(
            frame, text="", font=FONTS["small"], text_color=COLORS["success"]
        )
        self.create_status.pack(pady=(0, 10))

    def _save_card(self):
        front = self.front_input.get("1.0", "end").strip()
        back = self.back_input.get("1.0", "end").strip()
        tags = self.tags_input.get().strip()

        if not front or not back:
            self.create_status.configure(text="⚠️ Both front and back are required.", text_color=COLORS["danger"])
            return

        db.add_flashcard(front, back, tags=tags)
        self.create_status.configure(text="✅ Card saved!", text_color=COLORS["success"])
        self.front_input.delete("1.0", "end")
        self.back_input.delete("1.0", "end")
        self.tags_input.delete(0, "end")

    # ── AI Generate Dialog ────────────────────────────────────────

    def show_ai_generate_dialog(self, preselect_note_id=None):
        self._clear_content()

        frame = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=12)
        frame.pack(fill="both", expand=True, pady=5)

        ctk.CTkLabel(
            frame, text="🤖 AI-Generate Flashcards from Notes",
            font=FONTS["subheading"], text_color=COLORS["text_primary"]
        ).pack(padx=PADDING["section"], pady=(PADDING["section"], 10), anchor="w")

        # Note selector
        ctk.CTkLabel(
            frame, text="Select a note to generate cards from:",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(padx=PADDING["section"], anchor="w")

        notes = db.get_all_notes()
        if not notes:
            ctk.CTkLabel(
                frame, text="⚠️ No notes found. Import notes first in the Notes tab.",
                font=FONTS["body"], text_color=COLORS["warning"]
            ).pack(padx=PADDING["section"], pady=20)
            return

        note_titles = [f"{n['id']}: {n['title'][:60]}" for n in notes]

        # Pre-select the note if requested
        default_title = note_titles[0]
        if preselect_note_id is not None:
            for t in note_titles:
                if t.startswith(f"{preselect_note_id}:"):
                    default_title = t
                    break

        self.note_var = ctk.StringVar(value=default_title)

        ctk.CTkOptionMenu(
            frame, values=note_titles, variable=self.note_var,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            font=FONTS["body"], dropdown_font=FONTS["body"],
            corner_radius=8, width=400
        ).pack(padx=PADDING["section"], pady=(4, 10))

        # Count selector
        count_frame = ctk.CTkFrame(frame, fg_color="transparent")
        count_frame.pack(padx=PADDING["section"], anchor="w")

        ctk.CTkLabel(
            count_frame, text="Number of cards:",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(side="left")

        self.count_var = ctk.StringVar(value="10")
        ctk.CTkOptionMenu(
            count_frame, values=["5", "10", "15", "20"], variable=self.count_var,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            font=FONTS["body"], width=80, corner_radius=8
        ).pack(side="left", padx=8)

        # Generate button
        self.gen_btn = ctk.CTkButton(
            frame, text="⚡ Generate Flashcards", width=200, height=42,
            font=FONTS["body_bold"], fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], corner_radius=10,
            command=self._do_ai_generate
        )
        self.gen_btn.pack(pady=15)

        self.gen_status = ctk.CTkLabel(
            frame, text="", font=FONTS["body"], text_color=COLORS["text_secondary"]
        )
        self.gen_status.pack()

        # Results area
        self.gen_results = ctk.CTkScrollableFrame(
            frame, fg_color=COLORS["bg_secondary"], corner_radius=8, height=200
        )
        self.gen_results.pack(fill="both", expand=True, padx=PADDING["section"], pady=(5, PADDING["section"]))

        self._notes_lookup = {f"{n['id']}: {n['title'][:60]}": n for n in notes}

    def _do_ai_generate(self):
        if not self.app.claude_client:
            self.gen_status.configure(text="⚠️ Claude API not configured. Check config.json.", text_color=COLORS["danger"])
            return

        note_key = self.note_var.get()
        note = self._notes_lookup.get(note_key)
        if not note:
            return

        count = int(self.count_var.get())
        self.gen_btn.configure(state="disabled", text="⏳ Generating...")
        self.gen_status.configure(text="Calling Claude API... please wait.", text_color=COLORS["text_secondary"])

        def generate():
            try:
                cards = self.app.claude_client.generate_flashcards(
                    note["content"], count=count, context=note["title"]
                )
                self.after(0, lambda: self._display_generated_cards(cards, note["id"]))
            except Exception as e:
                self.after(0, lambda: self.gen_status.configure(
                    text=f"❌ Error: {str(e)[:100]}", text_color=COLORS["danger"]
                ))
            finally:
                self.after(0, lambda: self.gen_btn.configure(state="normal", text="⚡ Generate Flashcards"))

        threading.Thread(target=generate, daemon=True).start()

    def _display_generated_cards(self, cards, note_id):
        for w in self.gen_results.winfo_children():
            w.destroy()

        if not cards:
            self.gen_status.configure(text="⚠️ No cards generated. Try different notes.", text_color=COLORS["warning"])
            return

        self.gen_status.configure(
            text=f"✅ Generated {len(cards)} cards. Click 'Save' to add them.",
            text_color=COLORS["success"]
        )

        # Save all button
        ctk.CTkButton(
            self.gen_results, text=f"💾 Save All {len(cards)} Cards", height=36,
            font=FONTS["body_bold"], fg_color=COLORS["success"], corner_radius=8,
            command=lambda: self._save_all_generated(cards, note_id)
        ).pack(fill="x", padx=8, pady=6)

        for i, card in enumerate(cards):
            card_frame = ctk.CTkFrame(self.gen_results, fg_color=COLORS["bg_card"], corner_radius=8)
            card_frame.pack(fill="x", padx=8, pady=3)

            ctk.CTkLabel(
                card_frame, text=f"Q: {card['front']}",
                font=FONTS["body_bold"], text_color=COLORS["text_primary"],
                wraplength=500, justify="left"
            ).pack(padx=10, pady=(8, 2), anchor="w")

            ctk.CTkLabel(
                card_frame, text=f"A: {card['back']}",
                font=FONTS["body"], text_color=COLORS["text_secondary"],
                wraplength=500, justify="left"
            ).pack(padx=10, pady=(0, 8), anchor="w")

    def _save_all_generated(self, cards, note_id):
        count = 0
        for card in cards:
            db.add_flashcard(card["front"], card["back"], note_id=note_id)
            count += 1
        self.gen_status.configure(
            text=f"✅ Saved {count} cards to your collection!",
            text_color=COLORS["success"]
        )
        # Disable save button to prevent duplicate saves
        for w in self.gen_results.winfo_children():
            if isinstance(w, ctk.CTkButton):
                w.configure(state="disabled", text="✅ Saved")
