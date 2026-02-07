"""app.py — Main application window for StudyForge."""

import customtkinter as ctk
from ui.styles import COLORS, FONTS, PAD
from ui.dashboard import DashboardTab
from ui.pomodoro import PomodoroTab
from ui.flashcards import FlashcardsTab
from ui.notes import NotesTab
from ui.quiz import QuizTab
from ui.settings import SettingsTab
from ui.setup_wizard import SetupWizard
import config_manager as cfg


class StudyForgeApp(ctk.CTk):
    def __init__(self, config: dict, claude_client=None, show_wizard: bool = False):
        super().__init__()
        self.config = config
        self.claude_client = claude_client

        self.title("StudyForge — All-in-One Study Companion")
        self.geometry("1200x780")
        self.minsize(1000, 650)
        self.configure(fg_color=COLORS["bg_primary"])

        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.tabs = {}
        self.nav_buttons = {}
        self.current_tab = None

        if show_wizard:
            self._show_wizard()
        else:
            self._build_main()

    def _show_wizard(self):
        """Show the first-run setup wizard."""
        self.wizard = SetupWizard(self, self._wizard_complete)
        self.wizard.place(relx=0, rely=0, relwidth=1, relheight=1)

    def _wizard_complete(self, api_key: str):
        """Called when wizard finishes. Connects API if key provided, then builds main UI."""
        self.wizard.destroy()

        if api_key:
            try:
                from claude_client import ClaudeStudyClient
                self.claude_client = ClaudeStudyClient(api_key, self.config.get("claude_model", "claude-sonnet-4-5-20250929"))
            except Exception:
                self.claude_client = None

        self.config = cfg.load_config()
        self._build_main()

    def _build_main(self):
        """Build the main application UI with sidebar and content area."""
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ───────────────────────────────────────────────
        sidebar = ctk.CTkFrame(self, width=200, fg_color=COLORS["bg_secondary"], corner_radius=0)
        sidebar.grid(row=0, column=0, sticky="ns")
        sidebar.grid_propagate(False)

        lf = ctk.CTkFrame(sidebar, fg_color="transparent")
        lf.pack(fill="x", padx=12, pady=(18, 20))
        ctk.CTkLabel(lf, text="🎓 StudyForge", font=("Segoe UI", 18, "bold"),
            text_color=COLORS["accent_light"]).pack(anchor="w")
        ctk.CTkLabel(lf, text="Study smarter, not harder",
            font=("Segoe UI", 10), text_color=COLORS["text_muted"]).pack(anchor="w")

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=(0, 10))

        nav = [
            ("📊", "Dashboard"), ("🍅", "Pomodoro"), ("🧠", "Flashcards"),
            ("📝", "Notes"), ("❓", "Quiz"), ("⚙️", "Settings"),
        ]

        for icon, label in nav:
            btn = ctk.CTkButton(sidebar, text=f"  {icon}  {label}", font=FONTS["body"], height=40,
                fg_color="transparent", hover_color=COLORS["bg_card"],
                text_color=COLORS["text_secondary"], anchor="w", corner_radius=8,
                command=lambda l=label: self.select_tab(l))
            btn.pack(fill="x", padx=8, pady=2)
            self.nav_buttons[label] = btn

        # Bottom: API status
        ctk.CTkFrame(sidebar, fg_color="transparent").pack(fill="both", expand=True)
        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=(0, 8))

        status = "🟢 AI Connected" if self.claude_client else "🔴 AI Offline"
        color = COLORS["success"] if self.claude_client else COLORS["danger"]
        self.api_label = ctk.CTkLabel(sidebar, text=status, font=FONTS["small"], text_color=color)
        self.api_label.pack(padx=12, pady=(0, 4), anchor="w")

        hint = "Click Settings to configure" if not self.claude_client else ""
        self.api_hint = ctk.CTkLabel(sidebar, text=hint, font=("Segoe UI", 9),
            text_color=COLORS["text_muted"])
        self.api_hint.pack(padx=12, pady=(0, 14), anchor="w")

        # ── Content Area ──────────────────────────────────────────
        self.content_area = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        self.tabs["Dashboard"] = DashboardTab(self.content_area, self)
        self.tabs["Pomodoro"] = PomodoroTab(self.content_area, self)
        self.tabs["Flashcards"] = FlashcardsTab(self.content_area, self)
        self.tabs["Notes"] = NotesTab(self.content_area, self)
        self.tabs["Quiz"] = QuizTab(self.content_area, self)
        self.tabs["Settings"] = SettingsTab(self.content_area, self)

        self.select_tab("Dashboard")

    def select_tab(self, tab_name: str):
        if self.current_tab and self.current_tab in self.tabs:
            self.tabs[self.current_tab].grid_forget()

        if tab_name in self.tabs:
            self.tabs[tab_name].grid(row=0, column=0, sticky="nsew")
            self.current_tab = tab_name
            if tab_name == "Dashboard":
                self.tabs["Dashboard"].refresh()

        for name, btn in self.nav_buttons.items():
            if name == tab_name:
                btn.configure(fg_color=COLORS["accent"], text_color=COLORS["text_primary"])
            else:
                btn.configure(fg_color="transparent", text_color=COLORS["text_secondary"])

    def update_api_indicator(self, connected: bool):
        """Called by Settings tab when API connection changes."""
        if connected:
            self.api_label.configure(text="🟢 AI Connected", text_color=COLORS["success"])
            self.api_hint.configure(text="")
        else:
            self.api_label.configure(text="🔴 AI Offline", text_color=COLORS["danger"])
            self.api_hint.configure(text="Click Settings to configure")
