"""
setup_wizard.py — First-run welcome screen with optional API key setup.
Shown only once. User can skip and configure later in Settings.
"""

import customtkinter as ctk
import threading
from ui.styles import COLORS, FONTS, PAD
import config_manager as cfg
from claude_client import (
    ClaudeStudyClient,
    detect_provider_from_key,
    get_provider_options,
    get_provider_models,
    PROVIDER_DEFAULT_MODELS,
)


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

        ctk.CTkLabel(api_card, text="🔑 AI API Key (optional — can configure later in Settings)",
                      font=FONTS["body_bold"], text_color=COLORS["text_primary"]
        ).pack(padx=PAD["section"], pady=(PAD["section"], 4), anchor="w")

        self.key_help_label = ctk.CTkLabel(
            api_card, text="Get a key at console.anthropic.com → API Keys → Create Key",
            font=("Segoe UI", 10), text_color=COLORS["text_muted"]
        )
        self.key_help_label.pack(padx=PAD["section"], anchor="w")

        provider_row = ctk.CTkFrame(api_card, fg_color="transparent")
        provider_row.pack(fill="x", padx=PAD["section"], pady=(6, 2))

        ctk.CTkLabel(provider_row, text="Provider:", font=FONTS["body"],
                     text_color=COLORS["text_secondary"], width=80, anchor="w").pack(side="left")
        self.provider_var = ctk.StringVar(value="anthropic")
        self.provider_menu = ctk.CTkOptionMenu(
            provider_row, variable=self.provider_var, values=["anthropic", "openai", "gemini", "perplexity", "other"],
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            font=FONTS["body"], corner_radius=8, width=220,
            command=self._on_provider_change
        )
        self.provider_menu.pack(side="left", padx=(0, 8))
        self.show_all_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            provider_row, text="Show all", variable=self.show_all_var,
            command=self._refresh_provider_choices, font=FONTS["small"]
        ).pack(side="left")

        key_row = ctk.CTkFrame(api_card, fg_color="transparent")
        key_row.pack(fill="x", padx=PAD["section"], pady=(6, 4))

        self.key_entry = ctk.CTkEntry(
            key_row, font=FONTS["mono"], fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], border_color=COLORS["border"],
            corner_radius=8, show="•", placeholder_text="sk-ant-...",
            height=38
        )
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))
        self.key_entry.bind("<KeyRelease>", lambda _e: self._refresh_provider_choices())

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
        self._refresh_provider_choices()

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

        provider = self.provider_var.get()
        model = PROVIDER_DEFAULT_MODELS.get(provider, "claude-sonnet-4-5-20250929")
        live_models = get_provider_models(key, provider)
        if live_models:
            model = live_models[0]

        def run():
            ok, msg = ClaudeStudyClient.test_key(key, model=model, provider=provider)
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
        cfg.update_setting("ai_provider", self.provider_var.get())
        model = PROVIDER_DEFAULT_MODELS.get(self.provider_var.get(), "claude-sonnet-4-5-20250929")
        live_models = get_provider_models(key, self.provider_var.get()) if key else []
        if live_models:
            model = live_models[0]
        cfg.update_setting("claude_model", model)
        cfg.mark_setup_complete()
        self.on_complete(key)

    def _skip(self):
        cfg.mark_setup_complete()
        self.on_complete("")

    def _refresh_provider_choices(self):
        key = self.key_entry.get().strip()
        if self.show_all_var.get():
            options = ["anthropic", "openai", "gemini", "perplexity", "other"]
        else:
            options = get_provider_options(key)
        self.provider_menu.configure(values=options)
        detected = detect_provider_from_key(key)
        if detected and not self.show_all_var.get():
            self.provider_var.set(detected)
        elif self.provider_var.get() not in options:
            self.provider_var.set(options[0])
        self._on_provider_change(self.provider_var.get())

    def _on_provider_change(self, provider):
        hints = {
            "anthropic": "Get a key at console.anthropic.com → API Keys → Create Key",
            "openai": "Get a key at platform.openai.com → API keys",
            "gemini": "Get a key at aistudio.google.com → Get API key",
            "perplexity": "Get a key at perplexity.ai/settings/api",
            "other": "Catch-all provider — models are discovered live from your key",
        }
        self.key_help_label.configure(text=hints.get(provider, hints["anthropic"]))
