"""
settings.py — In-app settings panel for StudyForge.
Handles API key entry, connection testing, Pomodoro config, and preferences.
"""

import customtkinter as ctk
import threading
from ui.styles import COLORS, FONTS, PAD
import config_manager as cfg
from claude_client import (
    ClaudeStudyClient,
    detect_provider_from_key,
    get_provider_options,
    PROVIDER_DEFAULT_MODELS,
)


class SettingsTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self._key_visible = False
        self.build_ui()

    def build_ui(self):
        # Scrollable container for all settings
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=PAD["page"], pady=PAD["page"])

        ctk.CTkLabel(scroll, text="⚙️ Settings", font=FONTS["heading"],
                      text_color=COLORS["text_primary"]).pack(anchor="w", pady=(0, 12))

        # ── Claude AI Section ─────────────────────────────────────
        ai_card = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12)
        ai_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(ai_card, text="🤖 AI Integration", font=FONTS["subheading"],
                      text_color=COLORS["text_primary"]).pack(padx=PAD["section"], pady=(PAD["section"], 4), anchor="w")
        ctk.CTkLabel(ai_card, text="Powers flashcard generation, quizzes, summaries, and Q&A.",
                      font=FONTS["small"], text_color=COLORS["text_muted"]).pack(padx=PAD["section"], anchor="w")

        # API Key
        key_frame = ctk.CTkFrame(ai_card, fg_color="transparent")
        key_frame.pack(fill="x", padx=PAD["section"], pady=(10, 4))

        ctk.CTkLabel(key_frame, text="API Key:", font=FONTS["body"],
                      text_color=COLORS["text_secondary"], width=80, anchor="w").pack(side="left")

        self.key_entry = ctk.CTkEntry(
            key_frame, font=FONTS["mono"], fg_color=COLORS["bg_input"],
            text_color=COLORS["text_primary"], border_color=COLORS["border"],
            corner_radius=8, show="•", placeholder_text="sk-ant-..."
        )
        self.key_entry.pack(side="left", fill="x", expand=True, padx=(0, 6))

        config = cfg.load_config()
        # Load existing key
        existing_key = cfg.get_api_key()
        if existing_key:
            self.key_entry.insert(0, existing_key)

        self.toggle_vis_btn = ctk.CTkButton(
            key_frame, text="👁", width=36, height=32, font=FONTS["body"],
            fg_color=COLORS["bg_secondary"], hover_color=COLORS["accent"],
            corner_radius=6, command=self._toggle_key_visibility
        )
        self.toggle_vis_btn.pack(side="left")

        # Key help text
        self.key_help_label = ctk.CTkLabel(
            ai_card, text="Get your key at console.anthropic.com → API Keys → Create Key",
            font=("Segoe UI", 10), text_color=COLORS["text_muted"]
        )
        self.key_help_label.pack(padx=PAD["section"], anchor="w", pady=(0, 6))

        # Provider selector
        provider_frame = ctk.CTkFrame(ai_card, fg_color="transparent")
        provider_frame.pack(fill="x", padx=PAD["section"], pady=(0, 4))

        ctk.CTkLabel(provider_frame, text="Provider:", font=FONTS["body"],
                      text_color=COLORS["text_secondary"], width=80, anchor="w").pack(side="left")

        detected_provider = detect_provider_from_key(existing_key)
        provider_value = config.get("ai_provider") or detected_provider or "anthropic"
        self.provider_var = ctk.StringVar(value=provider_value)
        self._provider_menu = ctk.CTkOptionMenu(
            provider_frame, variable=self.provider_var,
            values=get_provider_options(existing_key),
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            font=FONTS["body"], corner_radius=8, width=300,
            command=self._on_provider_change
        )
        self._provider_menu.pack(side="left", padx=(0, 8))

        self.show_all_var = ctk.BooleanVar(value=False)
        ctk.CTkCheckBox(
            provider_frame, text="Show all", variable=self.show_all_var,
            command=self._refresh_provider_choices, font=FONTS["small"]
        ).pack(side="left")

        # Model selector
        model_frame = ctk.CTkFrame(ai_card, fg_color="transparent")
        model_frame.pack(fill="x", padx=PAD["section"], pady=(0, 4))

        ctk.CTkLabel(model_frame, text="Model:", font=FONTS["body"],
                      text_color=COLORS["text_secondary"], width=80, anchor="w").pack(side="left")

        self.model_var = ctk.StringVar(value=config.get("claude_model", "claude-sonnet-4-5-20250929"))
        self.model_menu = ctk.CTkOptionMenu(
            model_frame, variable=self.model_var,
            values=[self.model_var.get()],
            fg_color=COLORS["bg_input"], button_color=COLORS["accent"],
            font=FONTS["body"], corner_radius=8, width=300
        )
        self.model_menu.pack(side="left", padx=(0, 6))

        # Buttons: Test + Save
        btn_frame = ctk.CTkFrame(ai_card, fg_color="transparent")
        btn_frame.pack(fill="x", padx=PAD["section"], pady=(8, 4))

        self.test_btn = ctk.CTkButton(
            btn_frame, text="🔌 Test Connection", width=160, height=38,
            font=FONTS["body_bold"], fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], corner_radius=8,
            command=self._test_connection
        )
        self.test_btn.pack(side="left", padx=(0, 8))

        self.save_key_btn = ctk.CTkButton(
            btn_frame, text="💾 Save API Settings", width=170, height=38,
            font=FONTS["body_bold"], fg_color=COLORS["success"],
            hover_color="#00d2a0", corner_radius=8,
            command=self._save_api_settings
        )
        self.save_key_btn.pack(side="left")

        # Status indicator
        self.api_status = ctk.CTkLabel(
            ai_card, text="", font=FONTS["body"], text_color=COLORS["text_secondary"]
        )
        self.api_status.pack(padx=PAD["section"], pady=(2, PAD["section"]), anchor="w")

        # Show current status
        if self.app.claude_client:
            self.api_status.configure(text="🟢 Connected and ready", text_color=COLORS["success"])
        elif existing_key:
            self.api_status.configure(text="🟡 Key saved — click Test Connection to verify", text_color=COLORS["warning"])
        else:
            self.api_status.configure(text="🔴 No API key configured — AI features are disabled", text_color=COLORS["danger"])
        self.key_entry.bind("<KeyRelease>", lambda _e: self._refresh_provider_choices())
        self._refresh_provider_choices()

        # ── Pomodoro Settings ─────────────────────────────────────
        pom_card = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12)
        pom_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(pom_card, text="🍅 Pomodoro Timer", font=FONTS["subheading"],
                      text_color=COLORS["text_primary"]).pack(padx=PAD["section"], pady=(PAD["section"], 8), anchor="w")

        pom_grid = ctk.CTkFrame(pom_card, fg_color="transparent")
        pom_grid.pack(fill="x", padx=PAD["section"], pady=(0, PAD["section"]))
        pom_grid.grid_columnconfigure((1, 3), weight=1)

        settings = [
            ("Work Duration:", "pomodoro_work_minutes", 15, 60),
            ("Short Break:", "pomodoro_short_break", 3, 15),
            ("Long Break:", "pomodoro_long_break", 10, 30),
            ("Sessions before long break:", "pomodoro_sessions_before_long_break", 2, 8),
        ]

        self.pom_vars = {}
        for i, (label, key, mn, mx) in enumerate(settings):
            ctk.CTkLabel(pom_grid, text=label, font=FONTS["body"],
                          text_color=COLORS["text_secondary"]).grid(row=i, column=0, sticky="w", pady=4)

            val = config.get(key, mn)
            var = ctk.IntVar(value=val)
            self.pom_vars[key] = var

            val_label = ctk.CTkLabel(pom_grid, text=str(val), font=FONTS["body_bold"],
                                      text_color=COLORS["accent_light"], width=40)
            val_label.grid(row=i, column=2, padx=8)

            slider = ctk.CTkSlider(
                pom_grid, from_=mn, to=mx, number_of_steps=mx - mn,
                fg_color=COLORS["bg_secondary"], progress_color=COLORS["accent"],
                button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"],
                command=lambda v, vr=var, vl=val_label: (vr.set(int(v)), vl.configure(text=str(int(v))))
            )
            slider.set(val)
            slider.grid(row=i, column=1, sticky="ew", padx=(8, 0), pady=4)

        ctk.CTkButton(
            pom_card, text="💾 Save Pomodoro Settings", height=36,
            font=FONTS["body_bold"], fg_color=COLORS["success"],
            corner_radius=8, command=self._save_pomodoro_settings
        ).pack(padx=PAD["section"], pady=(0, PAD["section"]))

        # ── Study Settings ────────────────────────────────────────
        study_card = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12)
        study_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(study_card, text="📚 Study Preferences", font=FONTS["subheading"],
                      text_color=COLORS["text_primary"]).pack(padx=PAD["section"], pady=(PAD["section"], 8), anchor="w")

        limit_frame = ctk.CTkFrame(study_card, fg_color="transparent")
        limit_frame.pack(fill="x", padx=PAD["section"], pady=(0, PAD["section"]))

        ctk.CTkLabel(limit_frame, text="Daily new cards limit:", font=FONTS["body"],
                      text_color=COLORS["text_secondary"]).pack(side="left")

        self.daily_limit_var = ctk.IntVar(value=config.get("daily_new_cards_limit", 20))
        ctk.CTkEntry(
            limit_frame, textvariable=self.daily_limit_var, width=60,
            fg_color=COLORS["bg_input"], text_color=COLORS["text_primary"],
            font=FONTS["body"], corner_radius=6
        ).pack(side="left", padx=8)

        # ── About ─────────────────────────────────────────────────
        about_card = ctk.CTkFrame(scroll, fg_color=COLORS["bg_card"], corner_radius=12)
        about_card.pack(fill="x", pady=(0, 12))

        ctk.CTkLabel(about_card, text="🎓 StudyForge", font=FONTS["subheading"],
                      text_color=COLORS["text_primary"]).pack(padx=PAD["section"], pady=(PAD["section"], 4), anchor="w")
        ctk.CTkLabel(about_card,
            text="Pomodoro · Spaced Repetition (SM-2) · Active Recall · AI-Powered Study\n"
                 "All data stored locally in data/studyforge.db",
            font=FONTS["small"], text_color=COLORS["text_muted"], justify="left"
        ).pack(padx=PAD["section"], pady=(0, PAD["section"]), anchor="w")

    def _toggle_key_visibility(self):
        self._key_visible = not self._key_visible
        self.key_entry.configure(show="" if self._key_visible else "•")
        self.toggle_vis_btn.configure(text="🙈" if self._key_visible else "👁")

    def _refresh_provider_choices(self):
        key = self.key_entry.get().strip()
        if self.show_all_var.get():
            options = ["anthropic", "openai", "gemini", "perplexity"]
        else:
            options = get_provider_options(key)
        self._provider_menu.configure(values=options)
        detected = detect_provider_from_key(key)
        if detected and not self.show_all_var.get():
            self.provider_var.set(detected)
        elif self.provider_var.get() not in options:
            self.provider_var.set(options[0])
        self._on_provider_change(self.provider_var.get())

    def _on_provider_change(self, provider):
        current_model = self.model_var.get()
        if provider == "anthropic":
            models = ["claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001", "claude-opus-4-6"]
            hint = "Get your key at console.anthropic.com → API Keys → Create Key"
        elif provider == "openai":
            models = ["gpt-4o-mini", "gpt-4o", "gpt-4.1-mini"]
            hint = "Get your key at platform.openai.com → API keys"
        elif provider == "gemini":
            models = ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash"]
            hint = "Get your key at aistudio.google.com → Get API key"
        else:
            models = ["sonar", "sonar-pro", "sonar-reasoning-pro"]
            hint = "Get your key at perplexity.ai/settings/api"
        self.model_menu.configure(values=models)
        self.model_var.set(current_model if current_model in models else PROVIDER_DEFAULT_MODELS[provider])
        self.key_help_label.configure(text=hint)

    def _test_connection(self):
        key = self.key_entry.get().strip()
        if not key:
            self.api_status.configure(text="⚠️ Enter an API key first", text_color=COLORS["warning"])
            return

        model = self.model_var.get()
        provider = self.provider_var.get()
        self.test_btn.configure(state="disabled", text="⏳ Testing...")
        self.api_status.configure(text="Testing connection...", text_color=COLORS["text_secondary"])

        def do_test():
            ok, msg = ClaudeStudyClient.test_key(key, model, provider=provider)
            def update():
                self.test_btn.configure(state="normal", text="🔌 Test Connection")
                if ok:
                    self.api_status.configure(text=f"🟢 {msg}  ·  {provider} / {model}", text_color=COLORS["success"])
                else:
                    self.api_status.configure(text=f"🔴 {msg}", text_color=COLORS["danger"])
            self.after(0, update)

        threading.Thread(target=do_test, daemon=True).start()

    def _save_api_settings(self):
        key = self.key_entry.get().strip()
        model = self.model_var.get()
        provider = self.provider_var.get()

        cfg.set_api_key(key)
        cfg.update_setting("claude_model", model)
        cfg.update_setting("ai_provider", provider)

        # Reconnect the client
        if key:
            try:
                client = ClaudeStudyClient(key, model, provider=provider)
                self.app.claude_client = client
                self.app.update_api_indicator(True)
                self.api_status.configure(text="🟢 API settings saved and connected", text_color=COLORS["success"])
            except Exception as e:
                self.app.claude_client = None
                self.app.update_api_indicator(False)
                self.api_status.configure(text=f"⚠️ Saved, but connection failed: {str(e)[:80]}", text_color=COLORS["warning"])
        else:
            self.app.claude_client = None
            self.app.update_api_indicator(False)
            self.api_status.configure(text="🔴 API key cleared — AI features disabled", text_color=COLORS["danger"])

    def _save_pomodoro_settings(self):
        for key, var in self.pom_vars.items():
            cfg.update_setting(key, var.get())
        # Reload config into app
        self.app.config = cfg.load_config()
        self.api_status.configure(text="✅ Pomodoro settings saved (takes effect on next session)", text_color=COLORS["success"])
