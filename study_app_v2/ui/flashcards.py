"""flashcards.py — Flashcard Review & Management tab."""

import customtkinter as ctk
import threading
from ui.styles import COLORS, FONTS, PAD
import database as db
from srs_engine import review_card, get_rating_labels


class FlashcardsTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.current_cards = []
        self.card_index = 0
        self.showing_answer = False
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PAD["page"], pady=(PAD["page"], 5))
        ctk.CTkLabel(header, text="🧠 Flashcards", font=FONTS["heading"],
            text_color=COLORS["text_primary"]).pack(side="left")

        br = ctk.CTkFrame(header, fg_color="transparent")
        br.pack(side="right")
        self.review_btn = ctk.CTkButton(br, text="📖 Review Due", width=120, height=34,
            font=FONTS["body"], fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            corner_radius=8, command=self.start_review)
        self.review_btn.pack(side="left", padx=4)
        ctk.CTkButton(br, text="➕ New Card", width=110, height=34, font=FONTS["body"],
            fg_color=COLORS["success"], hover_color="#00d2a0", corner_radius=8,
            command=self.show_create).pack(side="left", padx=4)
        ctk.CTkButton(br, text="🤖 AI Generate", width=120, height=34, font=FONTS["body"],
            fg_color=COLORS["warning"], hover_color="#f0be50", corner_radius=8,
            command=self.show_ai_gen).pack(side="left", padx=4)

        self.status = ctk.CTkLabel(self, text="", font=FONTS["body"], text_color=COLORS["text_secondary"])
        self.status.pack(padx=PAD["page"], anchor="w")

        self.content = ctk.CTkFrame(self, fg_color="transparent")
        self.content.pack(fill="both", expand=True, padx=PAD["page"], pady=PAD["el"])
        self.start_review()

    def _clear(self):
        for w in self.content.winfo_children(): w.destroy()

    def start_review(self):
        self._clear()
        self.current_cards = db.get_due_cards()
        self.card_index = 0; self.showing_answer = False
        n = len(self.current_cards)
        self.status.configure(text=f"📋 {n} card{'s' if n!=1 else ''} due")
        if n == 0: self._empty()
        else: self._show_card()

    def _empty(self):
        self._clear()
        f = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=16)
        f.pack(expand=True, pady=40)
        ctk.CTkLabel(f, text="✨", font=("Segoe UI", 48)).pack(pady=(30,5))
        ctk.CTkLabel(f, text="All caught up!", font=FONTS["subheading"],
            text_color=COLORS["success"]).pack()
        ctk.CTkLabel(f, text="No cards due. Add notes and generate cards to get started.",
            font=FONTS["body"], text_color=COLORS["text_secondary"], justify="center"
        ).pack(padx=40, pady=(5,30))

    def _show_card(self):
        self._clear()
        if self.card_index >= len(self.current_cards):
            self._done(); return

        card = self.current_cards[self.card_index]
        rem = len(self.current_cards) - self.card_index

        pf = ctk.CTkFrame(self.content, fg_color="transparent")
        pf.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(pf, text=f"Card {self.card_index+1}/{len(self.current_cards)}  ·  {rem} left",
            font=FONTS["small"], text_color=COLORS["text_muted"]).pack(side="left")
        p = ctk.CTkProgressBar(pf, width=200, height=6, fg_color=COLORS["bg_secondary"],
            progress_color=COLORS["accent"])
        p.set(self.card_index / len(self.current_cards)); p.pack(side="right")

        cf = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=16)
        cf.pack(fill="both", expand=True, pady=5)

        ctk.CTkLabel(cf, text="QUESTION", font=FONTS["small"],
            text_color=COLORS["accent_light"]).pack(pady=(20,5))
        ctk.CTkLabel(cf, text=card["front"], font=FONTS["card_front"],
            text_color=COLORS["text_primary"], wraplength=600, justify="center").pack(padx=30, pady=(0,15))

        if self.showing_answer:
            ctk.CTkFrame(cf, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=30, pady=5)
            ctk.CTkLabel(cf, text="ANSWER", font=FONTS["small"],
                text_color=COLORS["success"]).pack(pady=(10,5))
            ctk.CTkLabel(cf, text=card["back"], font=FONTS["card_back"],
                text_color=COLORS["text_primary"], wraplength=600, justify="center").pack(padx=30, pady=(0,15))

            ctk.CTkLabel(cf, text="How well did you recall?", font=FONTS["small"],
                text_color=COLORS["text_muted"]).pack(pady=(10,5))

            rf = ctk.CTkFrame(cf, fg_color="transparent")
            rf.pack(pady=(0,20))
            labels = get_rating_labels()
            colors = [COLORS[f"rating_{i}"] for i in range(6)]
            for r in range(6):
                ctk.CTkButton(rf, text=f"{r}\n{labels[r][0]}", width=75, height=55,
                    font=FONTS["small"], fg_color=colors[r], hover_color=COLORS["accent_hover"],
                    text_color="#1a1a2e", corner_radius=8,
                    command=lambda rv=r: self._rate(rv)).pack(side="left", padx=3)
        else:
            ctk.CTkButton(cf, text="Show Answer", width=200, height=45,
                font=FONTS["body_bold"], fg_color=COLORS["accent"],
                hover_color=COLORS["accent_hover"], corner_radius=10,
                command=self._reveal).pack(pady=(10,25))

    def _reveal(self):
        self.showing_answer = True; self._show_card()

    def _rate(self, rating):
        card = self.current_cards[self.card_index]
        review_card(card, rating)
        if rating < 3:
            refreshed = db.get_due_cards()
            failed = [c for c in refreshed if c["id"] == card["id"]]
            if failed: self.current_cards.append(failed[0])
        self.card_index += 1; self.showing_answer = False; self._show_card()

    def _done(self):
        self._clear()
        f = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=16)
        f.pack(expand=True, pady=40)
        ctk.CTkLabel(f, text="🎉", font=("Segoe UI", 48)).pack(pady=(30,5))
        ctk.CTkLabel(f, text="Session complete!", font=FONTS["subheading"],
            text_color=COLORS["success"]).pack()
        s = db.get_today_stats()
        ctk.CTkLabel(f, text=f"Reviewed today: {s['cards_reviewed']}", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(pady=(5,20))
        ctk.CTkButton(f, text="Back to Dashboard", width=160, height=38,
            font=FONTS["body"], fg_color=COLORS["accent"],
            command=lambda: self.app.select_tab("Dashboard")).pack(pady=(0,25))

    # ── Create Card ───────────────────────────────────────────────

    def show_create(self):
        self._clear()
        f = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=12)
        f.pack(fill="both", expand=True, pady=5)
        ctk.CTkLabel(f, text="✏️ Create Flashcard", font=FONTS["subheading"],
            text_color=COLORS["text_primary"]).pack(padx=PAD["section"], pady=(PAD["section"],10), anchor="w")

        ctk.CTkLabel(f, text="Front (Question):", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=PAD["section"], anchor="w")
        self.front_in = ctk.CTkTextbox(f, height=80, fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], font=FONTS["body"],
            border_color=COLORS["border"], border_width=1, corner_radius=8)
        self.front_in.pack(fill="x", padx=PAD["section"], pady=(2,8))

        ctk.CTkLabel(f, text="Back (Answer):", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=PAD["section"], anchor="w")
        self.back_in = ctk.CTkTextbox(f, height=80, fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], font=FONTS["body"],
            border_color=COLORS["border"], border_width=1, corner_radius=8)
        self.back_in.pack(fill="x", padx=PAD["section"], pady=(2,8))

        ctk.CTkLabel(f, text="Tags (comma-separated):", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=PAD["section"], anchor="w")
        self.tags_in = ctk.CTkEntry(f, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], border_color=COLORS["border"], corner_radius=8)
        self.tags_in.pack(fill="x", padx=PAD["section"], pady=(2,8))

        br = ctk.CTkFrame(f, fg_color="transparent")
        br.pack(pady=PAD["section"])
        ctk.CTkButton(br, text="💾 Save Card", width=140, height=38, font=FONTS["body_bold"],
            fg_color=COLORS["success"], corner_radius=8, command=self._save_card).pack(side="left", padx=6)
        ctk.CTkButton(br, text="Cancel", width=100, height=38, font=FONTS["body"],
            fg_color=COLORS["bg_secondary"], corner_radius=8, command=self.start_review).pack(side="left", padx=6)

        self.create_st = ctk.CTkLabel(f, text="", font=FONTS["small"], text_color=COLORS["success"])
        self.create_st.pack(pady=(0,10))

    def _save_card(self):
        fr = self.front_in.get("1.0","end").strip()
        bk = self.back_in.get("1.0","end").strip()
        tg = self.tags_in.get().strip()
        if not fr or not bk:
            self.create_st.configure(text="⚠️ Both sides required.", text_color=COLORS["danger"]); return
        db.add_flashcard(fr, bk, tags=tg)
        self.create_st.configure(text="✅ Saved!", text_color=COLORS["success"])
        self.front_in.delete("1.0","end"); self.back_in.delete("1.0","end"); self.tags_in.delete(0,"end")

    # ── AI Generate ───────────────────────────────────────────────

    def show_ai_gen(self):
        self._clear()
        f = ctk.CTkFrame(self.content, fg_color=COLORS["bg_card"], corner_radius=12)
        f.pack(fill="both", expand=True, pady=5)
        ctk.CTkLabel(f, text="🤖 AI-Generate Flashcards", font=FONTS["subheading"],
            text_color=COLORS["text_primary"]).pack(padx=PAD["section"], pady=(PAD["section"],10), anchor="w")

        notes = db.get_all_notes()
        if not notes:
            ctk.CTkLabel(f, text="⚠️ No notes. Import notes first in the Notes tab.",
                font=FONTS["body"], text_color=COLORS["warning"]).pack(padx=PAD["section"], pady=20)
            return

        nt = [f"{n['id']}: {n['title'][:60]}" for n in notes]
        self.note_var = ctk.StringVar(value=nt[0])

        ctk.CTkLabel(f, text="Select note:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=PAD["section"], anchor="w")
        ctk.CTkOptionMenu(f, values=nt, variable=self.note_var, fg_color=COLORS["bg_input"],
            button_color=COLORS["accent"], font=FONTS["body"], corner_radius=8, width=400
        ).pack(padx=PAD["section"], pady=(4,10))

        cf = ctk.CTkFrame(f, fg_color="transparent")
        cf.pack(padx=PAD["section"], anchor="w")
        ctk.CTkLabel(cf, text="Cards:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(side="left")
        self.cnt_var = ctk.StringVar(value="10")
        ctk.CTkOptionMenu(cf, values=["5","10","15","20"], variable=self.cnt_var,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            font=FONTS["body"], width=80, corner_radius=8).pack(side="left", padx=8)

        self.gen_btn = ctk.CTkButton(f, text="⚡ Generate", width=200, height=42,
            font=FONTS["body_bold"], fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], corner_radius=10, command=self._do_gen)
        self.gen_btn.pack(pady=15)

        self.gen_st = ctk.CTkLabel(f, text="", font=FONTS["body"], text_color=COLORS["text_secondary"])
        self.gen_st.pack()

        self.gen_res = ctk.CTkScrollableFrame(f, fg_color=COLORS["bg_secondary"], corner_radius=8, height=200)
        self.gen_res.pack(fill="both", expand=True, padx=PAD["section"], pady=(5, PAD["section"]))

        self._notes_map = {f"{n['id']}: {n['title'][:60]}": n for n in notes}

    def _do_gen(self):
        if not self.app.claude_client:
            self.gen_st.configure(text="⚠️ AI not connected. Go to Settings to add your API key.",
                text_color=COLORS["danger"]); return

        note = self._notes_map.get(self.note_var.get())
        if not note: return
        count = int(self.cnt_var.get())
        self.gen_btn.configure(state="disabled", text="⏳ Generating...")
        self.gen_st.configure(text="Calling Claude API...", text_color=COLORS["text_secondary"])

        def run():
            try:
                cards = self.app.claude_client.generate_flashcards(note["content"], count, note["title"])
                self.after(0, lambda: self._show_gen(cards, note["id"]))
            except Exception as e:
                self.after(0, lambda: self.gen_st.configure(text=f"❌ {str(e)[:100]}", text_color=COLORS["danger"]))
            finally:
                self.after(0, lambda: self.gen_btn.configure(state="normal", text="⚡ Generate"))

        threading.Thread(target=run, daemon=True).start()

    def _show_gen(self, cards, note_id):
        for w in self.gen_res.winfo_children(): w.destroy()
        if not cards:
            self.gen_st.configure(text="⚠️ No cards generated.", text_color=COLORS["warning"]); return

        self.gen_st.configure(text=f"✅ {len(cards)} cards ready.", text_color=COLORS["success"])
        ctk.CTkButton(self.gen_res, text=f"💾 Save All {len(cards)} Cards", height=36,
            font=FONTS["body_bold"], fg_color=COLORS["success"], corner_radius=8,
            command=lambda: self._save_all(cards, note_id)).pack(fill="x", padx=8, pady=6)

        for c in cards:
            cf = ctk.CTkFrame(self.gen_res, fg_color=COLORS["bg_card"], corner_radius=8)
            cf.pack(fill="x", padx=8, pady=3)
            ctk.CTkLabel(cf, text=f"Q: {c['front']}", font=FONTS["body_bold"],
                text_color=COLORS["text_primary"], wraplength=500, justify="left"
            ).pack(padx=10, pady=(8,2), anchor="w")
            ctk.CTkLabel(cf, text=f"A: {c['back']}", font=FONTS["body"],
                text_color=COLORS["text_secondary"], wraplength=500, justify="left"
            ).pack(padx=10, pady=(0,8), anchor="w")

    def _save_all(self, cards, note_id):
        for c in cards: db.add_flashcard(c["front"], c["back"], note_id=note_id)
        self.gen_st.configure(text=f"✅ Saved {len(cards)} cards!", text_color=COLORS["success"])
