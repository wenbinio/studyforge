"""hypotheticals.py — Legal Hypotheticals tab for creating and analyzing legal scenarios."""

import customtkinter as ctk
import threading
from ui.styles import COLORS, FONTS, PAD
import database as db
import config_manager as cfg


class HypotheticalsTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.current_hyp = None
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="⚖️ Legal Hypotheticals", font=FONTS["heading"],
            text_color=COLORS["text_primary"]).pack(padx=PAD["page"], pady=(PAD["page"], 5), anchor="w")

        # ── Model selector ────────────────────────────────────────
        model_f = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        model_f.pack(fill="x", padx=PAD["page"], pady=(0, PAD["el"]))

        mf_inner = ctk.CTkFrame(model_f, fg_color="transparent")
        mf_inner.pack(fill="x", padx=PAD["section"], pady=PAD["el"])

        ctk.CTkLabel(mf_inner, text="Claude Model:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(side="left")
        config = cfg.load_config()
        override = config.get("claude_model_hypotheticals", "")
        self.model_var = ctk.StringVar(value=override if override else "(use default)")
        ctk.CTkOptionMenu(mf_inner, variable=self.model_var,
            values=["(use default)", "claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001", "claude-opus-4-6"],
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            font=FONTS["body"], corner_radius=8, width=300,
            command=self._save_model).pack(side="left", padx=8)

        # ── Generate section ──────────────────────────────────────
        gen_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        gen_card.pack(fill="x", padx=PAD["page"], pady=(0, PAD["el"]))

        ctk.CTkLabel(gen_card, text="Generate a hypothetical from your notes using AI",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(padx=PAD["section"], pady=(PAD["section"], 8), anchor="w")

        of = ctk.CTkFrame(gen_card, fg_color="transparent")
        of.pack(fill="x", padx=PAD["section"], pady=(0, 5))

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
        ctk.CTkEntry(of, textvariable=self.topic_var, placeholder_text="e.g. Contracts, Torts...",
            fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], corner_radius=8, width=200).pack(side="left", padx=8)

        bf = ctk.CTkFrame(gen_card, fg_color="transparent")
        bf.pack(pady=(5, PAD["section"]))
        self.gen_btn = ctk.CTkButton(bf, text="⚡ Generate Hypothetical", width=200, height=40,
            font=FONTS["body_bold"], fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            corner_radius=10, command=self.gen_hypothetical)
        self.gen_btn.pack()

        self.status = ctk.CTkLabel(gen_card, text="", font=FONTS["small"],
            text_color=COLORS["text_secondary"])
        self.status.pack(pady=(0, 8))

        # ── Content area ──────────────────────────────────────────
        self.content_f = ctk.CTkFrame(self, fg_color="transparent")
        self.content_f.pack(fill="both", expand=True, padx=PAD["page"], pady=(0, PAD["page"]))

        self._show_history()

    def _save_model(self, value):
        model = "" if value == "(use default)" else value
        cfg.update_setting("claude_model_hypotheticals", model)

    def _get_model_override(self):
        val = self.model_var.get()
        return None if val == "(use default)" else val

    def gen_hypothetical(self):
        if not self.app.claude_client:
            self.status.configure(text="⚠️ AI not connected. Go to Settings.", text_color=COLORS["danger"])
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
        self.status.configure(text="Generating hypothetical...", text_color=COLORS["text_secondary"])

        def run():
            try:
                result = self.app.claude_client.generate_hypothetical(
                    note["content"], self.topic_var.get(), model_override=self._get_model_override())
                if result and "scenario" in result:
                    title = result.get("title", "Legal Hypothetical")
                    hid = db.add_hypothetical(title, result["scenario"], note_id=nid)
                    if result.get("model_answer"):
                        db.update_hypothetical(hid, feedback=result["model_answer"])
                    self.after(0, lambda: self._on_generated(hid))
                else:
                    self.after(0, lambda: self.status.configure(
                        text="⚠️ Failed to generate.", text_color=COLORS["warning"]))
            except Exception as e:
                self.after(0, lambda: self.status.configure(
                    text=f"❌ {str(e)[:80]}", text_color=COLORS["danger"]))
            finally:
                self.after(0, lambda: self.gen_btn.configure(
                    state="normal", text="⚡ Generate Hypothetical"))
        threading.Thread(target=run, daemon=True).start()

    def _on_generated(self, hid):
        self.status.configure(text="✅ Hypothetical generated!", text_color=COLORS["success"])
        self._show_hypothetical(hid)

    def _clr(self):
        for w in self.content_f.winfo_children():
            w.destroy()

    def _show_history(self):
        self._clr()
        hyps = db.get_all_hypotheticals()
        if not hyps:
            ctk.CTkLabel(self.content_f, text="No hypotheticals yet. Generate one above!",
                font=FONTS["body"], text_color=COLORS["text_muted"]).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self.content_f, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        for h in hyps:
            item = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=10, cursor="hand2")
            item.pack(fill="x", padx=4, pady=3)
            title = h["title"][:60] + ("..." if len(h["title"]) > 60 else "")
            grade_txt = f"  ·  Grade: {h['grade']}" if h.get("grade") else ""
            ctk.CTkLabel(item, text=f"⚖️ {title}{grade_txt}", font=FONTS["body_bold"],
                text_color=COLORS["text_primary"], anchor="w").pack(padx=12, pady=(8, 0), anchor="w")
            meta = f"{h['created_at'][:10]}  ·  {'Answered' if h.get('response') else 'Unanswered'}"
            ctk.CTkLabel(item, text=meta, font=FONTS["small"],
                text_color=COLORS["text_muted"], anchor="w").pack(padx=12, pady=(0, 6), anchor="w")
            for w in [item] + item.winfo_children():
                w.bind("<Button-1>", lambda e, hid=h["id"]: self._show_hypothetical(hid))

    def _show_hypothetical(self, hid):
        self._clr()
        hyp = db.get_hypothetical(hid)
        if not hyp:
            return
        self.current_hyp = hyp

        scroll = ctk.CTkScrollableFrame(self.content_f, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        # Back button
        ctk.CTkButton(scroll, text="← Back to List", width=120, height=30, font=FONTS["small"],
            fg_color=COLORS["bg_secondary"], corner_radius=6,
            command=self._show_history).pack(anchor="w", pady=(0, 8))

        # Scenario card
        sc = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12)
        sc.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(sc, text=f"⚖️ {hyp['title']}", font=FONTS["subheading"],
            text_color=COLORS["accent_light"]).pack(padx=PAD["section"], pady=(PAD["section"], 4), anchor="w")
        scenario_tb = ctk.CTkTextbox(sc, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], wrap="word", corner_radius=8, height=150)
        scenario_tb.insert("1.0", hyp["scenario"])
        scenario_tb.configure(state="disabled")
        scenario_tb.pack(fill="x", padx=PAD["section"], pady=(0, PAD["section"]))

        # Response area
        rc = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12)
        rc.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(rc, text="📝 Your Analysis", font=FONTS["subheading"],
            text_color=COLORS["text_primary"]).pack(padx=PAD["section"], pady=(PAD["section"], 4), anchor="w")

        self.response_tb = ctk.CTkTextbox(rc, fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], font=FONTS["body"], wrap="word",
            corner_radius=8, height=200)
        if hyp.get("response"):
            self.response_tb.insert("1.0", hyp["response"])
        self.response_tb.pack(fill="x", padx=PAD["section"], pady=(0, 8))

        btn_f = ctk.CTkFrame(rc, fg_color="transparent")
        btn_f.pack(padx=PAD["section"], pady=(0, PAD["section"]))
        ctk.CTkButton(btn_f, text="💾 Save Response", width=140, height=36, font=FONTS["body_bold"],
            fg_color=COLORS["success"], corner_radius=8,
            command=lambda: self._save_response(hid)).pack(side="left", padx=4)
        self.grade_btn = ctk.CTkButton(btn_f, text="📊 Grade My Analysis", width=170, height=36,
            font=FONTS["body_bold"], fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"],
            corner_radius=8, command=lambda: self._grade(hid))
        self.grade_btn.pack(side="left", padx=4)
        ctk.CTkButton(btn_f, text="🗑️ Delete", width=80, height=36, font=FONTS["body"],
            fg_color=COLORS["danger"], corner_radius=8,
            command=lambda: self._delete(hid)).pack(side="left", padx=4)

        # Feedback area
        self.feedback_f = ctk.CTkFrame(scroll, fg_color="transparent")
        self.feedback_f.pack(fill="x", pady=(0, 8))
        if hyp.get("grade"):
            self._display_feedback(hyp)

    def _save_response(self, hid):
        response = self.response_tb.get("1.0", "end").strip()
        db.update_hypothetical(hid, response=response)
        self.status.configure(text="✅ Response saved!", text_color=COLORS["success"])

    def _grade(self, hid):
        hyp = db.get_hypothetical(hid)
        if not hyp:
            return
        response = self.response_tb.get("1.0", "end").strip()
        if not response:
            self.status.configure(text="⚠️ Write your analysis first.", text_color=COLORS["warning"])
            return
        if not self.app.claude_client:
            self.status.configure(text="⚠️ AI not connected.", text_color=COLORS["danger"])
            return

        db.update_hypothetical(hid, response=response)
        self.grade_btn.configure(state="disabled", text="⏳ Grading...")

        def run():
            try:
                result = self.app.claude_client.grade_hypothetical(
                    hyp["scenario"], response, hyp.get("feedback", ""),
                    model_override=self._get_model_override())
                if result and "grade" in result:
                    grade_str = result.get("grade", "")
                    feedback_parts = []
                    if result.get("feedback"):
                        feedback_parts.append(result["feedback"])
                    if result.get("strengths"):
                        feedback_parts.append("\n\nStrengths:\n• " + "\n• ".join(result["strengths"]))
                    if result.get("weaknesses"):
                        feedback_parts.append("\n\nAreas for Improvement:\n• " + "\n• ".join(result["weaknesses"]))
                    feedback_text = "".join(feedback_parts)
                    db.update_hypothetical(hid, response=response, grade=grade_str, feedback=feedback_text)
                    self.after(0, lambda: self._show_hypothetical(hid))
                else:
                    self.after(0, lambda: self.status.configure(
                        text="⚠️ Grading failed.", text_color=COLORS["warning"]))
            except Exception as e:
                self.after(0, lambda: self.status.configure(
                    text=f"❌ {str(e)[:80]}", text_color=COLORS["danger"]))
            finally:
                self.after(0, lambda: self.grade_btn.configure(
                    state="normal", text="📊 Grade My Analysis"))
        threading.Thread(target=run, daemon=True).start()

    def _display_feedback(self, hyp):
        for w in self.feedback_f.winfo_children():
            w.destroy()
        fc = ctk.CTkFrame(self.feedback_f, fg_color=COLORS["bg_card"], corner_radius=12)
        fc.pack(fill="x")
        grade = hyp.get("grade", "")
        color = COLORS["success"] if grade.startswith("A") else COLORS["warning"] if grade.startswith("B") else COLORS["danger"]
        ctk.CTkLabel(fc, text=f"📊 Grade: {grade}", font=FONTS["subheading"],
            text_color=color).pack(padx=PAD["section"], pady=(PAD["section"], 4), anchor="w")
        if hyp.get("feedback"):
            fb_tb = ctk.CTkTextbox(fc, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
                font=FONTS["body"], wrap="word", corner_radius=8, height=200)
            fb_tb.insert("1.0", hyp["feedback"])
            fb_tb.configure(state="disabled")
            fb_tb.pack(fill="x", padx=PAD["section"], pady=(0, PAD["section"]))

    def _delete(self, hid):
        db.delete_hypothetical(hid)
        self._show_history()

    def refresh_notes(self):
        self.notes = db.get_all_notes()
