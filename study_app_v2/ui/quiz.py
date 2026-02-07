"""quiz.py — Active Recall Quiz tab."""

import customtkinter as ctk
import threading
from ui.styles import COLORS, FONTS, PAD
import database as db


class QuizTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.questions = []; self.cur = 0; self.score = 0; self.answered = False
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="❓ Active Recall Quiz", font=FONTS["heading"],
            text_color=COLORS["text_primary"]).pack(padx=PAD["page"], pady=(PAD["page"],5), anchor="w")

        self.setup = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        self.setup.pack(fill="x", padx=PAD["page"], pady=PAD["el"])

        ctk.CTkLabel(self.setup, text="Generate a quiz from your notes using AI",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(padx=PAD["section"], pady=(PAD["section"],8), anchor="w")

        of = ctk.CTkFrame(self.setup, fg_color="transparent")
        of.pack(fill="x", padx=PAD["section"], pady=(0,5))

        self.notes = db.get_all_notes()
        nt = [f"{n['id']}: {n['title'][:50]}" for n in self.notes] if self.notes else ["No notes"]
        self.nv = ctk.StringVar(value=nt[0] if nt else "")
        ctk.CTkLabel(of, text="Note:", font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(side="left")
        ctk.CTkOptionMenu(of, values=nt, variable=self.nv, fg_color=COLORS["bg_input"],
            button_color=COLORS["accent"], font=FONTS["body"], corner_radius=8, width=300).pack(side="left", padx=8)

        ctk.CTkLabel(of, text="Difficulty:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(side="left", padx=(12,0))
        self.dv = ctk.StringVar(value="mixed")
        ctk.CTkOptionMenu(of, values=["easy","medium","hard","mixed"], variable=self.dv,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"], font=FONTS["body"],
            corner_radius=8, width=100).pack(side="left", padx=8)

        ctk.CTkLabel(of, text="Questions:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(side="left", padx=(12,0))
        self.qv = ctk.StringVar(value="5")
        ctk.CTkOptionMenu(of, values=["3","5","8","10"], variable=self.qv,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"], font=FONTS["body"],
            corner_radius=8, width=70).pack(side="left", padx=8)

        bf = ctk.CTkFrame(self.setup, fg_color="transparent")
        bf.pack(pady=(5, PAD["section"]))
        self.gen_btn = ctk.CTkButton(bf, text="⚡ Generate Quiz", width=180, height=40,
            font=FONTS["body_bold"], fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            corner_radius=10, command=self.gen_quiz)
        self.gen_btn.pack()

        self.st = ctk.CTkLabel(self.setup, text="", font=FONTS["small"], text_color=COLORS["text_secondary"])
        self.st.pack(pady=(0,8))

        self.qf = ctk.CTkFrame(self, fg_color="transparent")
        self.qf.pack(fill="both", expand=True, padx=PAD["page"], pady=(0, PAD["page"]))

    def gen_quiz(self):
        if not self.app.claude_client:
            self.st.configure(text="⚠️ AI not connected. Go to Settings.", text_color=COLORS["danger"]); return
        if not self.notes:
            self.st.configure(text="⚠️ No notes.", text_color=COLORS["warning"]); return

        nk = self.nv.get()
        nid = int(nk.split(":")[0]) if ":" in nk else None
        note = db.get_note(nid) if nid else None
        if not note: return

        self.gen_btn.configure(state="disabled", text="⏳ Generating...")
        self.st.configure(text="Generating quiz...", text_color=COLORS["text_secondary"])

        def run():
            try:
                qs = self.app.claude_client.generate_quiz(note["content"], int(self.qv.get()), self.dv.get())
                self.after(0, lambda: self._start(qs))
            except Exception as e:
                self.after(0, lambda: self.st.configure(text=f"❌ {str(e)[:80]}", text_color=COLORS["danger"]))
            finally:
                self.after(0, lambda: self.gen_btn.configure(state="normal", text="⚡ Generate Quiz"))
        threading.Thread(target=run, daemon=True).start()

    def _start(self, qs):
        if not qs: self.st.configure(text="⚠️ Failed.", text_color=COLORS["warning"]); return
        self.questions = qs; self.cur = 0; self.score = 0
        self.st.configure(text=f"✅ {len(qs)} questions ready!", text_color=COLORS["success"])
        self._show_q()

    def _clr(self):
        for w in self.qf.winfo_children(): w.destroy()

    def _show_q(self):
        self._clr(); self.answered = False
        if self.cur >= len(self.questions): self._results(); return
        q = self.questions[self.cur]

        pf = ctk.CTkFrame(self.qf, fg_color="transparent")
        pf.pack(fill="x", pady=(0,8))
        ctk.CTkLabel(pf, text=f"Q{self.cur+1}/{len(self.questions)}  ·  Score: {self.score}/{self.cur}",
            font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(side="left")
        p = ctk.CTkProgressBar(pf, width=200, height=6, fg_color=COLORS["bg_secondary"],
            progress_color=COLORS["accent"])
        p.set(self.cur / len(self.questions)); p.pack(side="right")

        card = ctk.CTkFrame(self.qf, fg_color=COLORS["bg_card"], corner_radius=14)
        card.pack(fill="both", expand=True)
        ctk.CTkLabel(card, text=q["question"], font=FONTS["card_front"],
            text_color=COLORS["text_primary"], wraplength=650, justify="left"
        ).pack(padx=24, pady=(24,16), anchor="w")

        self.opt_btns = []
        correct = q.get("correct", 0)
        for i, opt in enumerate(q.get("options", [])):
            b = ctk.CTkButton(card, text=opt, anchor="w", font=FONTS["body"], height=44,
                fg_color=COLORS["bg_secondary"], hover_color=COLORS["accent"],
                text_color=COLORS["text_primary"], corner_radius=8,
                command=lambda idx=i: self._answer(idx, correct, q))
            b.pack(fill="x", padx=24, pady=3)
            self.opt_btns.append(b)

        self.expl = ctk.CTkLabel(card, text="", font=FONTS["body"],
            text_color=COLORS["text_secondary"], wraplength=600, justify="left")
        self.nxt_btn = ctk.CTkButton(card, text="Next →", width=120, height=38,
            font=FONTS["body_bold"], fg_color=COLORS["accent"], corner_radius=8,
            command=self._next)

    def _answer(self, sel, correct, q):
        if self.answered: return
        self.answered = True
        db.increment_daily_stat("quiz_questions_answered")
        ok = sel == correct
        if ok: self.score += 1
        for i, b in enumerate(self.opt_btns):
            b.configure(state="disabled")
            if i == correct: b.configure(fg_color=COLORS["success"])
            elif i == sel and not ok: b.configure(fg_color=COLORS["danger"])
            else: b.configure(fg_color=COLORS["bg_secondary"])

        txt = "✅ Correct!" if ok else "❌ Incorrect."
        exp = q.get("explanation","")
        if exp: txt += f"\n\n💡 {exp}"
        self.expl.configure(text=txt, text_color=COLORS["success"] if ok else COLORS["danger"])
        self.expl.pack(padx=24, pady=(10,5), anchor="w")
        self.nxt_btn.pack(pady=(5,20))

    def _next(self): self.cur += 1; self._show_q()

    def _results(self):
        self._clr()
        card = ctk.CTkFrame(self.qf, fg_color=COLORS["bg_card"], corner_radius=16)
        card.pack(expand=True, pady=30)
        t = len(self.questions)
        pct = (self.score / t * 100) if t else 0
        em = "🏆" if pct>=90 else "🎉" if pct>=70 else "💪" if pct>=50 else "📚"
        ctk.CTkLabel(card, text=em, font=("Segoe UI", 48)).pack(pady=(30,5))
        ctk.CTkLabel(card, text="Quiz Complete!", font=FONTS["subheading"],
            text_color=COLORS["text_primary"]).pack()
        ctk.CTkLabel(card, text=f"Score: {self.score}/{t}  ({pct:.0f}%)", font=FONTS["stat_number"],
            text_color=COLORS["success"] if pct>=70 else COLORS["warning"]).pack(pady=10)
        msg = ("Excellent!" if pct>=90 else "Great job!" if pct>=70 else
               "Good effort — review and retry." if pct>=50 else "Time for more review.")
        ctk.CTkLabel(card, text=msg, font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(pady=(0,10))
        br = ctk.CTkFrame(card, fg_color="transparent")
        br.pack(pady=(5,25))
        ctk.CTkButton(br, text="🔄 Try Again", width=130, height=38, font=FONTS["body"],
            fg_color=COLORS["accent"], corner_radius=8, command=self.gen_quiz).pack(side="left", padx=6)
        ctk.CTkButton(br, text="🏠 Dashboard", width=130, height=38, font=FONTS["body"],
            fg_color=COLORS["bg_secondary"], corner_radius=8,
            command=lambda: self.app.select_tab("Dashboard")).pack(side="left", padx=6)

    def refresh_notes(self):
        self.notes = db.get_all_notes()
