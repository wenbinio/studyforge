"""essays.py — Legal Essays tab with rubric upload and AI grading."""

import customtkinter as ctk
import json
import os
import threading
from tkinter import filedialog
from ui.styles import COLORS, FONTS, PADDING, BUTTON_VARIANTS
import database as db

DEFAULT_HEIGHT_RATIO = 0.35
ESSAY_HEIGHT_RATIO = 0.4
FEEDBACK_HEIGHT_RATIO = 0.3


def _update_config_setting(config_path, key, value):
    """Update a single setting in the config file."""
    config = {}
    if os.path.exists(config_path):
        try:
            with open(config_path, "r") as f:
                config = json.load(f)
        except Exception:
            pass
    config[key] = value
    try:
        with open(config_path, "w") as f:
            json.dump(config, f, indent=2)
    except Exception:
        pass


def extract_rubric_text(filepath: str) -> str:
    """Extract text from a rubric file (.txt, .md, .pdf, .docx)."""
    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".txt", ".md"):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    elif ext == ".pdf":
        try:
            import fitz
            doc = fitz.open(filepath)
            t = "\n".join(p.get_text() for p in doc)
            doc.close()
            return t.strip()
        except ImportError:
            return "[PyMuPDF not installed]"
    elif ext == ".docx":
        try:
            from docx import Document
            return "\n".join(p.text for p in Document(filepath).paragraphs)
        except ImportError:
            return "[python-docx not installed]"
    return f"[Unsupported: {ext}]"


class EssaysTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.current_essay = None
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="📜 Legal Essays", font=FONTS["heading"],
            text_color=COLORS["text_primary"]).pack(padx=PADDING["page"], pady=(PADDING["page"], 5), anchor="w")

        # ── Model selector ────────────────────────────────────────
        model_f = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        model_f.pack(fill="x", padx=PADDING["page"], pady=(0, PADDING["element"]))

        mf_inner = ctk.CTkFrame(model_f, fg_color="transparent")
        mf_inner.pack(fill="x", padx=PADDING["section"], pady=PADDING["element"])

        ctk.CTkLabel(mf_inner, text="Claude Model:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(side="left")
        override = self.app.config.get("claude_model_essays", "")
        self.model_var = ctk.StringVar(value=override if override else "(use default)")
        ctk.CTkOptionMenu(mf_inner, variable=self.model_var,
            values=["(use default)", "claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001", "claude-opus-4-6"],
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            font=FONTS["body"], corner_radius=8, width=300,
            command=self._save_model).pack(side="left", padx=8)

        # ── Create / Rubric section ───────────────────────────────
        create_card = ctk.CTkFrame(self, fg_color=COLORS["bg_card"], corner_radius=12)
        create_card.pack(fill="x", padx=PADDING["page"], pady=(0, PADDING["element"]))

        cf_top = ctk.CTkFrame(create_card, fg_color="transparent")
        cf_top.pack(fill="x", padx=PADDING["section"], pady=(PADDING["section"], 8))

        ctk.CTkLabel(cf_top, text="Title:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(side="left")
        self.title_var = ctk.StringVar()
        ctk.CTkEntry(cf_top, textvariable=self.title_var, placeholder_text="Essay title...",
            fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], corner_radius=8, width=300).pack(side="left", padx=8)

        rf = ctk.CTkFrame(create_card, fg_color="transparent")
        rf.pack(fill="x", padx=PADDING["section"], pady=(0, 5))

        ctk.CTkLabel(rf, text="Rubric:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(side="left")
        self.rubrics = db.get_all_rubrics()
        rt = ["(none)"] + [f"{r['id']}: {r['name'][:40]}" for r in self.rubrics]
        self.rubric_var = ctk.StringVar(value="(none)")
        ctk.CTkOptionMenu(rf, values=rt, variable=self.rubric_var,
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            font=FONTS["body"], corner_radius=8, width=250).pack(side="left", padx=8)
        ctk.CTkButton(rf, text="📂 Upload Rubric", width=130, height=30, font=FONTS["small"],
            fg_color=COLORS["warning"], corner_radius=6,
            command=self._upload_rubric).pack(side="left", padx=4)
        ctk.CTkButton(rf, text="📋 Paste Rubric", width=120, height=30, font=FONTS["small"],
            fg_color=COLORS["accent_light"], corner_radius=6,
            command=self._paste_rubric).pack(side="left", padx=4)

        ctk.CTkLabel(create_card, text="Essay Prompt:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=PADDING["section"], anchor="w")
        self.prompt_tb = ctk.CTkTextbox(create_card, fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], font=FONTS["body"], wrap="word",
            corner_radius=8, height=80)
        self.prompt_tb.pack(fill="x", padx=PADDING["section"], pady=(0, 8))

        btn_f = ctk.CTkFrame(create_card, fg_color="transparent")
        btn_f.pack(pady=(0, PADDING["section"]))
        ctk.CTkButton(btn_f, text="📝 Create Essay", width=150, height=36,
            font=FONTS["body_bold"], fg_color=BUTTON_VARIANTS["primary"]["fg_color"], hover_color=BUTTON_VARIANTS["primary"]["hover_color"],
            corner_radius=8, command=self._create_essay).pack(side="left", padx=4)

        self.status = ctk.CTkLabel(create_card, text="", font=FONTS["small"],
            text_color=COLORS["text_secondary"])
        self.status.pack(pady=(0, 8))

        # ── Content area ──────────────────────────────────────────
        self.content_f = ctk.CTkFrame(self, fg_color="transparent")
        self.content_f.pack(fill="both", expand=True, padx=PADDING["page"], pady=(0, PADDING["page"]))

        self._show_history()

    def _get_window_height(self):
        """Return the window height, falling back to screen height before render."""
        window = self.winfo_toplevel()
        height = window.winfo_height()
        if height <= 1:
            height = window.winfo_screenheight()
        return height

    def _responsive_height(self, base_height, ratio=DEFAULT_HEIGHT_RATIO):
        """Return a responsive height that stays above the base height."""
        return max(base_height, int(self._get_window_height() * ratio))

    def _save_model(self, value):
        model = "" if value == "(use default)" else value
        config_path = self.app.config.get("_config_path", "config.json")
        _update_config_setting(config_path, "claude_model_essays", model)
        self.app.config["claude_model_essays"] = model

    def _get_model_override(self):
        val = self.model_var.get()
        return None if val == "(use default)" else val

    def _upload_rubric(self):
        fp = filedialog.askopenfilename(title="Upload Rubric",
            filetypes=[("All Supported", "*.txt *.md *.pdf *.docx"),
                       ("Text", "*.txt"), ("Markdown", "*.md"),
                       ("PDF", "*.pdf"), ("Word", "*.docx")])
        if not fp:
            return
        fn = os.path.basename(fp)
        content = extract_rubric_text(fp)
        name = os.path.splitext(fn)[0]
        db.add_rubric(name, content, source_file=fn)
        self._refresh_rubrics()
        self.status.configure(text=f"✅ Rubric '{name}' uploaded!", text_color=COLORS["success"])

    def _paste_rubric(self):
        w = ctk.CTkToplevel(self)
        w.title("Paste Rubric")
        w.geometry("600x450")
        w.configure(fg_color=COLORS["bg_primary"])
        w.attributes("-topmost", True)

        ctk.CTkLabel(w, text="Rubric Name:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=15, pady=(15, 2), anchor="w")
        ne = ctk.CTkEntry(w, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], corner_radius=8)
        ne.pack(fill="x", padx=15)

        ctk.CTkLabel(w, text="Rubric Content:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=15, pady=(10, 2), anchor="w")
        cb = ctk.CTkTextbox(w, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], wrap="word", corner_radius=8)
        cb.pack(fill="both", expand=True, padx=15, pady=(0, 10))

        def save():
            name = ne.get().strip() or "Untitled Rubric"
            content = cb.get("1.0", "end").strip()
            if content:
                db.add_rubric(name, content)
                self._refresh_rubrics()
                self.status.configure(text=f"✅ Rubric '{name}' saved!", text_color=COLORS["success"])
                w.destroy()

        ctk.CTkButton(w, text="💾 Save Rubric", height=36, font=FONTS["body_bold"],
            fg_color=COLORS["success"], corner_radius=8, command=save).pack(padx=15, pady=(0, 15))

    def _refresh_rubrics(self):
        self.rubrics = db.get_all_rubrics()
        for w in self.winfo_children():
            w.destroy()
        self.build_ui()

    def _create_essay(self):
        title = self.title_var.get().strip() or "Untitled Essay"
        prompt = self.prompt_tb.get("1.0", "end").strip()
        if not prompt:
            self.status.configure(text="⚠️ Enter an essay prompt.", text_color=COLORS["warning"])
            return

        rubric_id = None
        rv = self.rubric_var.get()
        if rv != "(none)" and ":" in rv:
            rubric_id = int(rv.split(":")[0])

        eid = db.add_essay(title, prompt, rubric_id=rubric_id)
        self._show_essay(eid)

    def _clr(self):
        for w in self.content_f.winfo_children():
            w.destroy()

    def _show_history(self):
        self._clr()
        essays = db.get_all_essays()
        if not essays:
            ctk.CTkLabel(self.content_f, text="No essays yet. Create one above!",
                font=FONTS["body"], text_color=COLORS["text_muted"]).pack(pady=40)
            return

        scroll = ctk.CTkScrollableFrame(self.content_f, fg_color="transparent")
        scroll.pack(fill="both", expand=True)
        for e in essays:
            item = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=10, cursor="hand2")
            item.pack(fill="x", padx=4, pady=3)
            title = e["title"][:60] + ("..." if len(e["title"]) > 60 else "")
            grade_txt = f"  ·  Grade: {e['grade']}" if e.get("grade") else ""
            ctk.CTkLabel(item, text=f"📜 {title}{grade_txt}", font=FONTS["body_bold"],
                text_color=COLORS["text_primary"], anchor="w").pack(padx=12, pady=(8, 0), anchor="w")
            has_content = "Written" if e.get("content") else "Not started"
            meta = f"{e['created_at'][:10]}  ·  {has_content}"
            ctk.CTkLabel(item, text=meta, font=FONTS["small"],
                text_color=COLORS["text_muted"], anchor="w").pack(padx=12, pady=(0, 6), anchor="w")
            for w in [item] + item.winfo_children():
                w.bind("<Button-1>", lambda ev, eid=e["id"]: self._show_essay(eid))

    def _show_essay(self, eid):
        self._clr()
        essay = db.get_essay(eid)
        if not essay:
            return
        self.current_essay = essay

        scroll = ctk.CTkScrollableFrame(self.content_f, fg_color="transparent")
        scroll.pack(fill="both", expand=True)

        ctk.CTkButton(scroll, text="← Back to List", width=120, height=30, font=FONTS["small"],
            fg_color=BUTTON_VARIANTS["secondary"]["fg_color"], corner_radius=6,
            command=self._show_history).pack(anchor="w", pady=(0, 8))

        pc = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12)
        pc.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(pc, text=f"📜 {essay['title']}", font=FONTS["subheading"],
            text_color=COLORS["accent_light"]).pack(padx=PADDING["section"], pady=(PADDING["section"], 4), anchor="w")
        ctk.CTkLabel(pc, text="Prompt:", font=FONTS["body_bold"],
            text_color=COLORS["text_secondary"]).pack(padx=PADDING["section"], anchor="w")
        prompt_tb = ctk.CTkTextbox(pc, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], wrap="word", corner_radius=8, height=80)
        prompt_tb.insert("1.0", essay["prompt"])
        prompt_tb.configure(state="disabled")
        prompt_tb.pack(fill="x", padx=PADDING["section"], pady=(0, PADDING["section"]))

        if essay.get("rubric_id"):
            rubric = db.get_rubric(essay["rubric_id"])
            if rubric:
                rub_c = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12)
                rub_c.pack(fill="x", pady=(0, 8))
                ctk.CTkLabel(rub_c, text=f"📋 Rubric: {rubric['name']}", font=FONTS["body_bold"],
                    text_color=COLORS["warning"]).pack(padx=PADDING["section"], pady=(PADDING["section"], 4), anchor="w")
                rub_tb = ctk.CTkTextbox(rub_c, fg_color=COLORS["bg_input"],
                    text_color=COLORS["text_primary"], font=FONTS["small"], wrap="word",
                    corner_radius=8, height=100)
                rub_tb.insert("1.0", rubric["content"][:2000])
                rub_tb.configure(state="disabled")
                rub_tb.pack(fill="x", padx=PADDING["section"], pady=(0, PADDING["section"]))

        ec = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12)
        ec.pack(fill="x", pady=(0, 8))
        ctk.CTkLabel(ec, text="📝 Your Essay", font=FONTS["subheading"],
            text_color=COLORS["text_primary"]).pack(padx=PADDING["section"], pady=(PADDING["section"], 4), anchor="w")

        essay_h = self._responsive_height(250, ratio=ESSAY_HEIGHT_RATIO)
        self.essay_tb = ctk.CTkTextbox(ec, fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], font=FONTS["body"], wrap="word",
            corner_radius=8, height=essay_h)
        if essay.get("content"):
            self.essay_tb.insert("1.0", essay["content"])
        self.essay_tb.pack(fill="x", padx=PADDING["section"], pady=(0, 8))

        btn_f = ctk.CTkFrame(ec, fg_color="transparent")
        btn_f.pack(padx=PADDING["section"], pady=(0, PADDING["section"]))
        ctk.CTkButton(btn_f, text="💾 Save Essay", width=130, height=36, font=FONTS["body_bold"],
            fg_color=COLORS["success"], corner_radius=8,
            command=lambda: self._save_essay(eid)).pack(side="left", padx=4)
        self.grade_btn = ctk.CTkButton(btn_f, text="📊 Grade Essay", width=140, height=36,
            font=FONTS["body_bold"], fg_color=BUTTON_VARIANTS["primary"]["fg_color"], hover_color=BUTTON_VARIANTS["primary"]["hover_color"],
            corner_radius=8, command=lambda: self._grade(eid))
        self.grade_btn.pack(side="left", padx=4)
        ctk.CTkButton(btn_f, text="🗑️ Delete", width=80, height=36, font=FONTS["body"],
            fg_color=BUTTON_VARIANTS["destructive"]["fg_color"], corner_radius=8,
            command=lambda: self._delete(eid)).pack(side="left", padx=4)

        self.feedback_f = ctk.CTkFrame(scroll, fg_color="transparent")
        self.feedback_f.pack(fill="x", pady=(0, 8))
        if essay.get("grade"):
            self._display_feedback(essay)

    def _save_essay(self, eid):
        content = self.essay_tb.get("1.0", "end").strip()
        db.update_essay(eid, content=content)
        self.status.configure(text="✅ Essay saved!", text_color=COLORS["success"])

    def _grade(self, eid):
        essay = db.get_essay(eid)
        if not essay:
            return
        content = self.essay_tb.get("1.0", "end").strip()
        if not content:
            self.status.configure(text="⚠️ Write your essay first.", text_color=COLORS["warning"])
            return
        if not self.app.claude_client:
            self.status.configure(text="⚠️ AI not connected.", text_color=COLORS["danger"])
            return

        db.update_essay(eid, content=content)
        self.grade_btn.configure(state="disabled", text="⏳ Grading...")

        rubric_text = ""
        if essay.get("rubric_id"):
            rubric = db.get_rubric(essay["rubric_id"])
            if rubric:
                rubric_text = rubric["content"]

        def run():
            try:
                result = self.app.claude_client.grade_essay(
                    essay["prompt"], content, rubric_text,
                    model_override=self._get_model_override())
                if result and "grade" in result:
                    grade_str = result.get("grade", "")
                    feedback_parts = []
                    if result.get("feedback"):
                        feedback_parts.append(result["feedback"])
                    if result.get("rubric_scores"):
                        feedback_parts.append("\n\nRubric Scores:")
                        for criterion, score in result["rubric_scores"].items():
                            feedback_parts.append(f"\n  • {criterion}: {score}")
                    if result.get("strengths"):
                        feedback_parts.append("\n\nStrengths:\n• " + "\n• ".join(result["strengths"]))
                    if result.get("weaknesses"):
                        feedback_parts.append("\n\nAreas for Improvement:\n• " + "\n• ".join(result["weaknesses"]))
                    if result.get("suggestions"):
                        feedback_parts.append("\n\nSuggestions:\n• " + "\n• ".join(result["suggestions"]))
                    feedback_text = "".join(feedback_parts)
                    db.update_essay(eid, content=content, grade=grade_str, feedback=feedback_text)
                    self.after(0, lambda: self._show_essay(eid))
                else:
                    self.after(0, lambda: self.status.configure(
                        text="⚠️ Grading failed.", text_color=COLORS["warning"]))
            except Exception as e:
                self.after(0, lambda: self.status.configure(
                    text=f"❌ {str(e)[:80]}", text_color=COLORS["danger"]))
            finally:
                self.after(0, lambda: self.grade_btn.configure(
                    state="normal", text="📊 Grade Essay"))
        threading.Thread(target=run, daemon=True).start()

    def _display_feedback(self, essay):
        for w in self.feedback_f.winfo_children():
            w.destroy()
        fc = ctk.CTkFrame(self.feedback_f, fg_color=COLORS["bg_card"], corner_radius=12)
        fc.pack(fill="x")
        grade = essay.get("grade", "")
        color = COLORS["success"] if grade.startswith("A") else COLORS["warning"] if grade.startswith("B") else COLORS["danger"]
        ctk.CTkLabel(fc, text=f"📊 Grade: {grade}", font=FONTS["subheading"],
            text_color=color).pack(padx=PADDING["section"], pady=(PADDING["section"], 4), anchor="w")
        if essay.get("feedback"):
            fb_h = self._responsive_height(250, ratio=FEEDBACK_HEIGHT_RATIO)
            fb_tb = ctk.CTkTextbox(fc, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
                font=FONTS["body"], wrap="word", corner_radius=8, height=fb_h)
            fb_tb.insert("1.0", essay["feedback"])
            fb_tb.configure(state="disabled")
            fb_tb.pack(fill="x", padx=PADDING["section"], pady=(0, PADDING["section"]))

    def _delete(self, eid):
        db.delete_essay(eid)
        self._show_history()

    def refresh_rubrics(self):
        self.rubrics = db.get_all_rubrics()
