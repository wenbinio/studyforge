"""
setup_wizard.py — First-run welcome screen with optional API key setup.
Shown only once. User can skip and configure later in Settings.
"""

import customtkinter as ctk
import threading
from ui.styles import COLORS, FONTS, PAD
import config_manager as cfg
from claude_client import ClaudeStudyClient


class SetupWizard(ctk.CTkFrame):
    """Full-screen welcome wizard shown on first launch."""

    def __init__(self, parent, on_complete: callable):
        super().__init__(parent, fg_color=COLORS["bg_primary"])
        self.on_complete = on_complete
        self._key_visible = False
        self.build_ui()

    def build_ui(self):
        # Center card
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.place(relx=0.5, rely=0.5, anchor="center")

        # Logo
        ctk.CTkLabel(center, text="🎓", font=("Segoe UI", 56)).pack(pady=(0, 4))
        ctk.CTkLabel(center, text="Welcome to StudyForge",
                      font=("Segoe UI", 28, "bold"), text_color=COLORS["text_primary"]).pack()
        ctk.CTkLabel(center, text="Your all-in-one study companion",
                      font=("Segoe UI", 14), text_color=COLORS["text_muted"]).pack(pady=(2, 20))

        # Features overview
        features_card = ctk.CTkFrame(center, fg_color=COLORS["bg_card"], corner_radius=14)
        features_card.pack(fill="x", padx=20, pady=(0, 16))

        features = [
            ("🍅", "Pomodoro Timer", "Focused study sessions with smart breaks"),
            ("🧠", "Spaced Repetition", "Anki-style SM-2 algorithm for long-term memory"),
            ("❓", "Active Recall Quizzes", "AI-generated MCQs from your notes"),
            ("📝", "Notes Manager", "Import PDF, DOCX, TXT, and Markdown files"),
            ("🤖", "Claude AI Engine", "Auto-generate cards, summaries, and answers"),
        ]

        for icon, title, desc in features:
            row = ctk.CTkFrame(features_card, fg_color="transparent")
            row.pack(fill="x", padx=PAD["section"], pady=4)
            ctk.CTkLabel(row, text=icon, font=("Segoe UI", 16), width=30).pack(side="left")
            ctk.CTkLabel(row, text=f"{title}  —  ", font=FONTS["body_bold"],
                          text_color=COLORS["text_primary"]).pack(side="left")
            ctk.CTkLabel(row, text=desc, font=FONTS["small"],
                          text_color=COLORS["text_muted"]).pack(side="left")

        # API Key setup
        api_card = ctk.CTkFrame(center, fg_color=COLORS["bg_card"], corner_radius=14)
        api_card.pack(fill="x", padx=20, pady=(0, 12))

        ctk.CTkLabel(api_card, text="🔑 Claude API Key (optional — can configure later in Settings)",
                      font=FONTS["body_bold"], text_color=COLORS["text_primary"]
        ).pack(padx=PAD["section"], pady=(PAD["section"], 4), anchor="w")

        ctk.CTkLabel(api_card, text="Get a key at console.anthropic.com → API Keys → Create Key",
                      font=("Segoe UI", 10), text_color=COLORS["text_muted"]
        ).pack(padx=PAD["section"], anchor="w")

        key_row = ctk.CTkFrame(api_card, fg_color="transparent")
        key_row.pack(fill="x", padx=PAD["section"], pady=(6, 4))

        self.key_entry = ctk.CTkEntry(
            key_row, font=FONTS["mono"], fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], border_color=COLORS["border"],
            corner_radius=8, show="•", placeholder_text="sk-ant-...",
            height=38
        )
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        ctk.CTkButton(
            key_row, text="👁", width=36, height=38, font=FONTS["body"],
            fg_color=COLORS["bg_secondary"], hover_color=COLORS["accent"],
            corner_radius=6, command=self._toggle_vis
        ).pack(side="left", padx=(0, 6))

        self.test_btn = ctk.CTkButton(
            key_row, text="Test", width=70, height=38,
            font=FONTS["body"], fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], corner_radius=8,
            command=self._test_key
        )
        self.test_btn.pack(side="left")

        self.key_status = ctk.CTkLabel(
            api_card, text="", font=FONTS["small"], text_color=COLORS["text_muted"]
        )
        self.key_status.pack(padx=PAD["section"], pady=(0, PAD["section"]), anchor="w")

        # Action buttons
        btn_row = ctk.CTkFrame(center, fg_color="transparent")
        btn_row.pack(pady=(4, 0))

        ctk.CTkButton(
            btn_row, text="🚀 Get Started", width=200, height=48,
            font=("Segoe UI", 15, "bold"), fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], corner_radius=12,
            command=self._finish
        ).pack(side="left", padx=8)

        ctk.CTkButton(
            btn_row, text="Skip for now", width=130, height=48,
            font=FONTS["body"], fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_secondary"], corner_radius=12,
            command=self._skip
        ).pack(side="left", padx=8)

    def _toggle_vis(self):
        self._key_visible = not self._key_visible
        self.key_entry.configure(show="" if self._key_visible else "•")

    def _test_key(self):
        key = self.key_entry.get().strip()
        if not key:
            self.key_status.configure(text="Enter a key first", text_color=COLORS["warning"])
            return

        self.test_btn.configure(state="disabled", text="...")
        self.key_status.configure(text="Testing...", text_color=COLORS["text_secondary"])

        def run():
            ok, msg = ClaudeStudyClient.test_key(key)
            def update():
                self.test_btn.configure(state="normal", text="Test")
                if ok:
                    self.key_status.configure(text="✅ " + msg, text_color=COLORS["success"])
                else:
                    self.key_status.configure(text="❌ " + msg, text_color=COLORS["danger"])
            self.after(0, update)

        threading.Thread(target=run, daemon=True).start()

    def _finish(self):
        key = self.key_entry.get().strip()
        if key:
            cfg.set_api_key(key)
        cfg.mark_setup_complete()
        self.on_complete(key)

    def _skip(self):
        cfg.mark_setup_complete()
        self.on_complete("")
