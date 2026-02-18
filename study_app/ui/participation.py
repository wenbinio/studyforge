"""participation.py — Class Participation tab for tracking legal discussion questions."""

import customtkinter as ctk
import threading
from ui.styles import COLORS, FONTS, PADDING, BUTTON_VARIANTS
import database as db


class ParticipationTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.current_category = "all"
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="🎓 Class Participation", font=FONTS["heading"],
            text_color=COLORS["text_primary"]).pack(padx=PADDING["page"], pady=(PADDING["page"], 5), anchor="w")

        # ── Generate section ──────────────────────────────────────
        gen_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        gen_card.pack(fill="x", padx=PADDING["page"], pady=(0, PADDING["element"]))

        ctk.CTkLabel(gen_card, text="Generate participation questions from your notes using AI",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(padx=PADDING["section"], pady=(PADDING["section"], 8), anchor="w")

        of = ctk.CTkFrame(gen_card, fg_color="transparent")
        of.pack(fill="x", padx=PADDING["section"], pady=(0, 5))

        self.notes = db.get_all_notes()
        nt = [f"{n['id']}: {n['title'][:50]}" for n in self.notes] if self.notes else ["No notes"]
        self.nv = ctk.StringVar(value=nt[0] if nt else "")
        ctk.CTkLabel(of, text="Note:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(side="left")
        ctk.CTkOptionMenu(of, values=nt, variable=self.nv, fg_color=COLORS["bg_input"],
            button_color=COLORS["accent"], font=FONTS["body"], corner_radius=8, width=300
        ).pack(side="left", padx=8)

        ctk.CTkLabel(of, text="Topic:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(side="left", padx=(12, 0))
        self.topic_var = ctk.StringVar()
        ctk.CTkEntry(of, textvariable=self.topic_var, placeholder_text="e.g. Con Law, Civ Pro...",
            fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], corner_radius=8, width=200).pack(side="left", padx=8)

        bf = ctk.CTkFrame(gen_card, fg_color="transparent")
        bf.pack(pady=(5, 4))
        self.gen_btn = ctk.CTkButton(bf, text="⚡ Generate Questions", width=200, height=40,
            font=FONTS["body_bold"], **BUTTON_VARIANTS["primary"],
            corner_radius=10, command=self.gen_questions)
        self.gen_btn.pack(side="left", padx=4)
        ctk.CTkButton(bf, text="✏️ Add Manual Question", width=180, height=40,
            font=FONTS["body_bold"], fg_color=COLORS["success"], hover_color=COLORS["success_hover"],
            corner_radius=10, command=self._add_manual).pack(side="left", padx=4)

        self.status = ctk.CTkLabel(gen_card, text="", font=FONTS["small"],
            text_color=COLORS["text_secondary"])
        self.status.pack(pady=(0, 8))

        # ── Filter bar ────────────────────────────────────────────
        filter_f = ctk.CTkFrame(self, fg_color="transparent")
        filter_f.pack(fill="x", padx=PADDING["page"], pady=(0, PADDING["element"]))

        self.filter_btns = {}
        categories = [
            ("all", "📋 All"),
            ("interesting", "💡 Interesting"),
            ("unanswered", "❓ Unanswered"),
            ("key_questions", "🔑 Key Questions"),
        ]
        for cat_id, cat_label in categories:
            btn = ctk.CTkButton(filter_f, text=cat_label, width=120, height=32,
                font=FONTS["body"], fg_color=BUTTON_VARIANTS["primary"]["fg_color"] if cat_id == "all" else BUTTON_VARIANTS["secondary"]["fg_color"],
                hover_color=BUTTON_VARIANTS["primary"]["hover_color"], corner_radius=8,
                text_color=COLORS["text_primary"],
                command=lambda c=cat_id: self._filter(c))
            btn.pack(side="left", padx=3)
            self.filter_btns[cat_id] = btn

        # ── Content area ──────────────────────────────────────────
        self.content_f = ctk.CTkFrame(self, fg_color="transparent")
        self.content_f.pack(fill="both", expand=True, padx=PADDING["page"], pady=(0, PADDING["page"]))

        self._show_questions()

    def _filter(self, category):
        self.current_category = category
        for cat_id, btn in self.filter_btns.items():
            if cat_id == category:
                btn.configure(fg_color=BUTTON_VARIANTS["primary"]["fg_color"])
            else:
                btn.configure(fg_color=BUTTON_VARIANTS["secondary"]["fg_color"])
        self._show_questions()

    def gen_questions(self):
        if not self.app.claude_client:
            self.status.configure(text="⚠️ AI not connected.", text_color=COLORS["danger"])
            return
        if not self.notes:
            self.status.configure(text="⚠️ No notes available.", text_color=COLORS["warning"])
            return

        nk = self.nv.get()
        nid = int(nk.split(":")[0]) if ":" in nk else None
        note = db.get_note(nid) if nid else None
        if not note:
            return

        self.gen_btn.configure(state="disabled", text="⏳ Generating...")
        self.status.configure(text="Generating questions...", text_color=COLORS["text_secondary"])

        def run():
            try:
                result = self.app.claude_client.generate_participation_questions(
                    note["content"], self.topic_var.get())
                count = 0
                for category in ["interesting", "unanswered", "key_questions"]:
                    for q in result.get(category, []):
                        question_text = q.get("question", "") if isinstance(q, dict) else str(q)
                        why = q.get("why_it_matters", "") if isinstance(q, dict) else ""
                        if question_text:
                            db.add_participation_question(
                                question_text, category=category,
                                note_id=nid, notes=why)
                            count += 1
                self.after(0, lambda: self._on_generated(count))
            except Exception as e:
                self.after(0, lambda: self.status.configure(
                    text=f"❌ {str(e)[:80]}", text_color=COLORS["danger"]))
            finally:
                self.after(0, lambda: self.gen_btn.configure(
                    state="normal", text="⚡ Generate Questions"))
        threading.Thread(target=run, daemon=True).start()

    def _on_generated(self, count):
        self.status.configure(text=f"✅ {count} questions generated!", text_color=COLORS["success"])
        self._show_questions()

    def _add_manual(self):
        w = ctk.CTkToplevel(self)
        w.title("Add Question")
        w.geometry("550x350")
        w.configure(fg_color=COLORS["bg_primary"])
        w.attributes("-topmost", True)

        ctk.CTkLabel(w, text="Question:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=15, pady=(15, 2), anchor="w")
        qe = ctk.CTkTextbox(w, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], wrap="word", corner_radius=8, height=100)
        qe.pack(fill="x", padx=15, pady=(0, 8))

        ctk.CTkLabel(w, text="Category:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=15, anchor="w")
        cat_var = ctk.StringVar(value="interesting")
        ctk.CTkOptionMenu(w, values=["interesting", "unanswered", "key_questions"],
            variable=cat_var, fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            font=FONTS["body"], corner_radius=8, width=200).pack(padx=15, anchor="w", pady=(0, 8))

        ctk.CTkLabel(w, text="Notes (optional):", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=15, anchor="w")
        ne = ctk.CTkEntry(w, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], corner_radius=8)
        ne.pack(fill="x", padx=15, pady=(0, 10))

        def save():
            question = qe.get("1.0", "end").strip()
            if question:
                db.add_participation_question(question, category=cat_var.get(), notes=ne.get().strip())
                self._show_questions()
                w.destroy()

        ctk.CTkButton(w, text="💾 Save", height=36, font=FONTS["body_bold"],
            fg_color=COLORS["success"], corner_radius=8, command=save).pack(padx=15, pady=(0, 15))

    def _clr(self):
        for w in self.content_f.winfo_children():
            w.destroy()

    def _show_questions(self):
        self._clr()
        if self.current_category == "all":
            questions = db.get_all_participation_questions()
        else:
            questions = db.get_participation_questions_by_category(self.current_category)

        if not questions:
            ctk.CTkLabel(self.content_f, text="No questions yet. Generate some from your notes!",
                font=FONTS["body"], text_color=COLORS["text_muted"]).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self.content_f, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        category_icons = {
            "interesting": "💡", "unanswered": "❓", "key_questions": "🔑",
        }
        category_colors = {
            "interesting": COLORS["warning"], "unanswered": COLORS["danger"],
            "key_questions": COLORS["accent_light"],
        }

        for q in questions:
            item = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=10)
            item.pack(fill="x", padx=4, pady=3)

            header = ctk.CTkFrame(item, fg_color="transparent")
            header.pack(fill="x", padx=12, pady=(8, 0))

            cat = q.get("category", "interesting")
            icon = category_icons.get(cat, "📋")
            color = category_colors.get(cat, COLORS["text_secondary"])
            cat_label = cat.replace("_", " ").title()

            ctk.CTkLabel(header, text=f"{icon} {cat_label}", font=FONTS["small"],
                text_color=color).pack(side="left")
            ctk.CTkLabel(header, text=q["created_at"][:10], font=FONTS["small"],
                text_color=COLORS["text_muted"]).pack(side="right")

            ctk.CTkLabel(item, text=q["question"], font=FONTS["body"],
                text_color=COLORS["text_primary"], wraplength=650, justify="left",
                anchor="w").pack(padx=12, pady=(4, 0), anchor="w")

            if q.get("notes"):
                ctk.CTkLabel(item, text=f"📌 {q['notes']}", font=FONTS["small"],
                    text_color=COLORS["text_muted"], wraplength=650, justify="left",
                    anchor="w").pack(padx=12, pady=(2, 0), anchor="w")

            if q.get("answer"):
                ctk.CTkLabel(item, text=f"✅ {q['answer']}", font=FONTS["small"],
                    text_color=COLORS["success"], wraplength=650, justify="left",
                    anchor="w").pack(padx=12, pady=(2, 0), anchor="w")

            btn_f = ctk.CTkFrame(item, fg_color="transparent")
            btn_f.pack(padx=12, pady=(4, 8), anchor="w")

            ctk.CTkButton(btn_f, text="💬 Answer", width=80, height=26, font=FONTS["small"],
                fg_color=BUTTON_VARIANTS["primary"]["fg_color"], corner_radius=6,
                command=lambda qid=q["id"]: self._answer_question(qid)).pack(side="left", padx=2)
            ctk.CTkButton(btn_f, text="🗑️", width=36, height=26, font=FONTS["small"],
                fg_color=BUTTON_VARIANTS["destructive"]["fg_color"], corner_radius=6,
                command=lambda qid=q["id"]: self._delete_question(qid)).pack(side="left", padx=2)

    def _answer_question(self, qid):
        w = ctk.CTkToplevel(self)
        w.title("Answer Question")
        w.geometry("550x300")
        w.configure(fg_color=COLORS["bg_primary"])
        w.attributes("-topmost", True)

        ctk.CTkLabel(w, text="Your Answer:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=15, pady=(15, 2), anchor="w")
        ae = ctk.CTkTextbox(w, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], wrap="word", corner_radius=8, height=150)
        ae.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        def save():
            answer = ae.get("1.0", "end").strip()
            if answer:
                db.update_participation_question(qid, answer=answer)
                self._show_questions()
                w.destroy()

        ctk.CTkButton(w, text="💾 Save Answer", height=36, font=FONTS["body_bold"],
            fg_color=COLORS["success"], corner_radius=8, command=save).pack(padx=15, pady=(0, 15))

    def _delete_question(self, qid):
        db.delete_participation_question(qid)
        self._show_questions()

    def refresh_notes(self):
        self.notes = db.get_all_notes()
