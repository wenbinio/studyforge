"""notes.py — Notes Manager tab."""

import customtkinter as ctk
import threading, os
from tkinter import filedialog
from ui.styles import COLORS, FONTS, PAD
import database as db


def extract_text(filepath: str) -> str:
    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".txt", ".md"):
        with open(filepath, "r", encoding="utf-8", errors="replace") as f: return f.read()
    elif ext == ".pdf":
        try:
            import fitz
            doc = fitz.open(filepath)
            t = "\n".join(p.get_text() for p in doc); doc.close(); return t.strip()
        except ImportError: return "[PyMuPDF not installed]"
    elif ext == ".docx":
        try:
            from docx import Document
            return "\n".join(p.text for p in Document(filepath).paragraphs)
        except ImportError: return "[python-docx not installed]"
    return f"[Unsupported: {ext}]"


class NotesTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.sel_id = None
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PAD["page"], pady=(PAD["page"], 5))
        ctk.CTkLabel(header, text="📝 Notes Manager", font=FONTS["heading"],
            text_color=COLORS["text_primary"]).pack(side="left")

        br = ctk.CTkFrame(header, fg_color="transparent")
        br.pack(side="right")
        ctk.CTkButton(br, text="📂 Import File", width=120, height=34, font=FONTS["body"],
            fg_color=COLORS["accent"], hover_color=COLORS["accent_hover"], corner_radius=8,
            command=self.import_file).pack(side="left", padx=4)
        ctk.CTkButton(br, text="📋 Paste Note", width=120, height=34, font=FONTS["body"],
            fg_color=COLORS["success"], hover_color="#00d2a0", corner_radius=8,
            command=self.paste_dlg).pack(side="left", padx=4)

        sf = ctk.CTkFrame(self, fg_color="transparent")
        sf.pack(fill="x", padx=PAD["page"], pady=(5,8))
        self.search_var = ctk.StringVar()
        self.search_var.trace_add("write", lambda *_: self.refresh())
        ctk.CTkEntry(sf, textvariable=self.search_var, placeholder_text="🔍 Search notes...",
            fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"], font=FONTS["body"],
            border_color=COLORS["border"], corner_radius=8, height=36).pack(fill="x")

        split = ctk.CTkFrame(self, fg_color="transparent")
        split.pack(fill="both", expand=True, padx=PAD["page"], pady=(0, PAD["page"]))
        split.grid_columnconfigure(0, weight=1, minsize=280)
        split.grid_columnconfigure(1, weight=3)
        split.grid_rowconfigure(0, weight=1)

        self.list_f = ctk.CTkScrollableFrame(split, fg_color=COLORS["bg_card"], corner_radius=12, width=280)
        self.list_f.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        self.viewer = ctk.CTkFrame(split, fg_color=COLORS["bg_card"], corner_radius=12)
        self.viewer.grid(row=0, column=1, sticky="nsew")

        self.refresh()
        self._empty_viewer()

    def _empty_viewer(self):
        for w in self.viewer.winfo_children(): w.destroy()
        ctk.CTkLabel(self.viewer, text="📄", font=("Segoe UI", 40),
            text_color=COLORS["text_muted"]).pack(expand=True)
        ctk.CTkLabel(self.viewer, text="Select a note or import one.",
            font=FONTS["body"], text_color=COLORS["text_muted"]).pack(pady=(0,40))

    def refresh(self):
        for w in self.list_f.winfo_children(): w.destroy()
        q = self.search_var.get().strip()
        notes = db.search_notes(q) if q else db.get_all_notes()
        if not notes:
            ctk.CTkLabel(self.list_f, text="No notes yet.", font=FONTS["body"],
                text_color=COLORS["text_muted"]).pack(pady=40)
            return
        for n in notes:
            sel = n["id"] == self.sel_id
            bg = COLORS["accent"] if sel else COLORS["bg_secondary"]
            item = ctk.CTkFrame(self.list_f, fg_color=bg, corner_radius=8, cursor="hand2")
            item.pack(fill="x", padx=6, pady=3)
            t = n["title"][:40] + ("..." if len(n["title"]) > 40 else "")
            ctk.CTkLabel(item, text=t, font=FONTS["body_bold"],
                text_color=COLORS["text_primary"], anchor="w").pack(padx=10, pady=(8,0), anchor="w")
            meta = f"{n.get('tags','') or 'No tags'}  ·  {n['created_at'][:10]}"
            ctk.CTkLabel(item, text=meta, font=FONTS["small"],
                text_color=COLORS["text_muted"], anchor="w").pack(padx=10, pady=(0,6), anchor="w")
            for w in [item] + item.winfo_children():
                w.bind("<Button-1>", lambda e, nid=n["id"]: self.view_note(nid))

    def view_note(self, nid):
        self.sel_id = nid; self.refresh()
        note = db.get_note(nid)
        if not note: return
        for w in self.viewer.winfo_children(): w.destroy()

        tb = ctk.CTkFrame(self.viewer, fg_color="transparent")
        tb.pack(fill="x", padx=PAD["section"], pady=(PAD["section"],5))
        self.title_e = ctk.CTkEntry(tb, font=FONTS["subheading"], fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], border_color=COLORS["border"], corner_radius=8)
        self.title_e.insert(0, note["title"])
        self.title_e.pack(side="left", fill="x", expand=True, padx=(0,8))
        ctk.CTkButton(tb, text="💾", width=36, height=32, font=FONTS["small"],
            fg_color=COLORS["success"], corner_radius=6,
            command=lambda: self._save(nid)).pack(side="left", padx=2)
        ctk.CTkButton(tb, text="🗑️", width=36, height=32, font=FONTS["small"],
            fg_color=COLORS["danger"], corner_radius=6,
            command=lambda: self._del(nid)).pack(side="left", padx=2)

        tgf = ctk.CTkFrame(self.viewer, fg_color="transparent")
        tgf.pack(fill="x", padx=PAD["section"], pady=(0,5))
        ctk.CTkLabel(tgf, text="Tags:", font=FONTS["small"],
            text_color=COLORS["text_muted"]).pack(side="left")
        self.tags_e = ctk.CTkEntry(tgf, font=FONTS["small"], fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], border_color=COLORS["border"], corner_radius=6, height=28)
        self.tags_e.insert(0, note.get("tags",""))
        self.tags_e.pack(side="left", fill="x", expand=True, padx=6)

        ar = ctk.CTkFrame(self.viewer, fg_color="transparent")
        ar.pack(fill="x", padx=PAD["section"], pady=(0,5))
        ctk.CTkButton(ar, text="🤖 Generate Cards", width=140, height=30, font=FONTS["small"],
            fg_color=COLORS["warning"], corner_radius=6,
            command=lambda: self._gen_cards(note)).pack(side="left", padx=2)
        ctk.CTkButton(ar, text="📋 Summarize", width=110, height=30, font=FONTS["small"],
            fg_color=COLORS["accent"], corner_radius=6,
            command=lambda: self._summarize(note)).pack(side="left", padx=2)
        ctk.CTkButton(ar, text="❓ Ask Question", width=120, height=30, font=FONTS["small"],
            fg_color=COLORS["accent_light"], corner_radius=6,
            command=lambda: self._ask(note)).pack(side="left", padx=2)

        self.editor = ctk.CTkTextbox(self.viewer, fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], font=FONTS["body"],
            border_color=COLORS["border"], border_width=1, corner_radius=8, wrap="word")
        self.editor.insert("1.0", note["content"])
        self.editor.pack(fill="both", expand=True, padx=PAD["section"], pady=(0, PAD["section"]))

    def _save(self, nid):
        db.update_note(nid, title=self.title_e.get().strip(),
            content=self.editor.get("1.0","end").strip(), tags=self.tags_e.get().strip())
        self.refresh()

    def _del(self, nid):
        db.delete_note(nid); self.sel_id = None; self.refresh(); self._empty_viewer()

    def _gen_cards(self, note):
        self.app.select_tab("Flashcards")
        fc = self.app.tabs.get("Flashcards")
        if fc: fc.show_ai_gen()

    def _summarize(self, note):
        if not self.app.claude_client: return
        def run():
            try:
                r = self.app.claude_client.summarize_notes(note["content"])
                self.after(0, lambda: self._popup("📋 Summary", r))
            except Exception as e:
                self.after(0, lambda: self._popup("Error", str(e)))
        threading.Thread(target=run, daemon=True).start()

    def _ask(self, note):
        d = ctk.CTkInputDialog(text="Ask a question about this note:", title="Ask Claude")
        q = d.get_input()
        if not q or not self.app.claude_client: return
        def run():
            try:
                r = self.app.claude_client.answer_question(q, note["content"])
                self.after(0, lambda: self._popup(f"❓ {q}", r))
            except Exception as e:
                self.after(0, lambda: self._popup("Error", str(e)))
        threading.Thread(target=run, daemon=True).start()

    def _popup(self, title, content):
        w = ctk.CTkToplevel(self); w.title("StudyForge"); w.geometry("700x500")
        w.configure(fg_color=COLORS["bg_primary"]); w.attributes("-topmost", True)
        ctk.CTkLabel(w, text=title, font=FONTS["subheading"],
            text_color=COLORS["accent_light"]).pack(padx=15, pady=(15,5), anchor="w")
        tb = ctk.CTkTextbox(w, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], wrap="word", corner_radius=8)
        tb.insert("1.0", content); tb.configure(state="disabled")
        tb.pack(fill="both", expand=True, padx=15, pady=(0,15))

    def import_file(self):
        fps = filedialog.askopenfilenames(title="Import Notes",
            filetypes=[("All Supported","*.txt *.md *.pdf *.docx"),("Text","*.txt"),
                       ("Markdown","*.md"),("PDF","*.pdf"),("Word","*.docx")])
        for fp in fps:
            fn = os.path.basename(fp)
            db.add_note(os.path.splitext(fn)[0], extract_text(fp), source_file=fn)
        if fps: self.refresh()

    def paste_dlg(self):
        w = ctk.CTkToplevel(self); w.title("Paste Note"); w.geometry("600x450")
        w.configure(fg_color=COLORS["bg_primary"]); w.attributes("-topmost", True)
        ctk.CTkLabel(w, text="Title:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=15, pady=(15,2), anchor="w")
        te = ctk.CTkEntry(w, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], corner_radius=8)
        te.pack(fill="x", padx=15)
        ctk.CTkLabel(w, text="Content:", font=FONTS["body"],
            text_color=COLORS["text_secondary"]).pack(padx=15, pady=(10,2), anchor="w")
        cb = ctk.CTkTextbox(w, fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], wrap="word", corner_radius=8)
        cb.pack(fill="both", expand=True, padx=15, pady=(0,10))
        def save():
            t = te.get().strip() or "Untitled"
            c = cb.get("1.0","end").strip()
            if c: db.add_note(t, c); self.refresh(); w.destroy()
        ctk.CTkButton(w, text="💾 Save", height=36, font=FONTS["body_bold"],
            fg_color=COLORS["success"], corner_radius=8, command=save).pack(padx=15, pady=(0,15))
