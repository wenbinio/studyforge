"""
app.py — Main application window for StudyForge.
Manages the sidebar navigation and tab switching.
"""

import customtkinter as ctk
import os
import sys
import subprocess
from ui.styles import COLORS, FONTS, PADDING
from ui.dashboard import DashboardTab
from ui.pomodoro import PomodoroTab
from ui.flashcards import FlashcardsTab
from ui.notes import NotesTab
from ui.notepad import NotepadTab
from ui.quiz import QuizTab
from ui.hypotheticals import HypotheticalsTab
from ui.essays import EssaysTab
from ui.participation import ParticipationTab


class StudyForgeApp(ctk.CTk):
    def __init__(self, config: dict, claude_client=None):
        super().__init__()

        self.config = config
        self.claude_client = claude_client

        # Window setup
        self.title("StudyForge — All-in-One Study Companion")
        self.geometry("1200x780")
        self.minsize(1000, 650)
        self.configure(fg_color=COLORS["bg_primary"])

        # Set appearance
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")

        self.tabs = {}
        self.nav_buttons = {}
        self.current_tab = None
        self.focus_mode = False
        self.sidebar = None

        self.build_ui()
        self.select_tab("Dashboard")

    def build_ui(self):
        # Main layout: sidebar + content
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # ── Sidebar ───────────────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, width=200, fg_color=COLORS["bg_secondary"], corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)
        sidebar = self.sidebar

        # App logo / title
        logo_frame = ctk.CTkFrame(sidebar, fg_color="transparent")
        logo_frame.pack(fill="x", padx=12, pady=(18, 20))

        ctk.CTkLabel(
            logo_frame, text="🎓 StudyForge",
            font=("Segoe UI", 18, "bold"), text_color=COLORS["accent_light"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_frame, text="Study smarter, not harder",
            font=("Segoe UI", 10), text_color=COLORS["text_muted"]
        ).pack(anchor="w")

        # Separator
        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=(0, 10))

        # Navigation items
        nav_items = [
            ("📊", "Dashboard"),
            ("🍅", "Pomodoro"),
            ("🧠", "Flashcards"),
            ("📝", "Notes"),
            ("✏️", "Notepad"),
            ("❓", "Quiz"),
            ("⚖️", "Hypotheticals"),
            ("📜", "Essays"),
            ("🎓", "Participation"),
        ]

        for icon, label in nav_items:
            btn = ctk.CTkButton(
                sidebar, text=f"  {icon}  {label}",
                font=FONTS["body"], height=40,
                fg_color="transparent",
                hover_color=COLORS["bg_card"],
                text_color=COLORS["text_secondary"],
                anchor="w", corner_radius=8,
                command=lambda l=label: self.select_tab(l)
            )
            btn.pack(fill="x", padx=8, pady=2)
            self.nav_buttons[label] = btn

        # Bottom section: API status
        spacer = ctk.CTkFrame(sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=(0, 8))

        api_status = "🟢 AI Connected" if self.claude_client else "🔴 AI Offline"
        api_color = COLORS["success"] if self.claude_client else COLORS["danger"]

        ctk.CTkLabel(
            sidebar, text=api_status,
            font=FONTS["small"], text_color=api_color
        ).pack(padx=12, pady=(0, 4), anchor="w")

        # Show config location so user can find it
        config_path = self.config.get("_config_path", "config.json")
        config_dir = os.path.dirname(config_path)

        ctk.CTkButton(
            sidebar, text="📁 Open Config",
            font=("Segoe UI", 11), text_color=COLORS["text_muted"],
            fg_color="transparent", hover_color=COLORS["bg_secondary"],
            height=26, width=140, anchor="w",
            command=lambda: self._open_folder(config_dir)
        ).pack(padx=8, pady=(0, 14), anchor="w")

        # ── Content Area ──────────────────────────────────────────
        self.content_area = ctk.CTkFrame(self, fg_color=COLORS["bg_primary"], corner_radius=0)
        self.content_area.grid(row=0, column=1, sticky="nsew")
        self.content_area.grid_columnconfigure(0, weight=1)
        self.content_area.grid_rowconfigure(0, weight=1)

        # Create all tabs (hidden by default)
        self.tabs["Dashboard"] = DashboardTab(self.content_area, self)
        self.tabs["Pomodoro"] = PomodoroTab(self.content_area, self)
        self.tabs["Flashcards"] = FlashcardsTab(self.content_area, self)
        self.tabs["Notes"] = NotesTab(self.content_area, self)
        self.tabs["Notepad"] = NotepadTab(self.content_area, self)
        self.tabs["Quiz"] = QuizTab(self.content_area, self)
        self.tabs["Hypotheticals"] = HypotheticalsTab(self.content_area, self)
        self.tabs["Essays"] = EssaysTab(self.content_area, self)
        self.tabs["Participation"] = ParticipationTab(self.content_area, self)

    def _open_folder(self, path):
        """Open a folder in the system file explorer."""
        try:
            if sys.platform == "win32":
                os.startfile(path)
            elif sys.platform == "darwin":
                subprocess.Popen(["open", path])
            else:
                subprocess.Popen(["xdg-open", path])
        except Exception:
            pass

    def select_tab(self, tab_name: str):
        """Switch to the specified tab."""
        # Hide current
        if self.current_tab and self.current_tab in self.tabs:
            self.tabs[self.current_tab].grid_forget()

        # Show new
        if tab_name in self.tabs:
            self.tabs[tab_name].grid(row=0, column=0, sticky="nsew")
            self.current_tab = tab_name

            # Refresh tabs when switching to them
            if tab_name == "Dashboard":
                self.tabs["Dashboard"].refresh()
            elif tab_name == "Quiz":
                self.tabs["Quiz"].refresh_notes()
            elif tab_name == "Notepad":
                self.tabs["Notepad"].refresh()
            elif tab_name == "Flashcards":
                # If in review or interleaved mode, refresh due cards
                fc = self.tabs["Flashcards"]
                if fc.mode == "review":
                    fc.start_review()
                elif fc.mode == "interleaved":
                    fc.start_interleaved_review()

        # Update nav button styles
        for name, btn in self.nav_buttons.items():
            if name == tab_name:
                btn.configure(
                    fg_color=COLORS["accent"],
                    text_color=COLORS["text_primary"]
                )
            else:
                btn.configure(
                    fg_color="transparent",
                    text_color=COLORS["text_secondary"]
                )

    def toggle_focus_mode(self):
        """Toggle sidebar visibility for distraction-free notepad writing."""
        self.focus_mode = not self.focus_mode
        if self.focus_mode:
            self.sidebar.grid_forget()
        else:
            self.sidebar.grid(row=0, column=0, sticky="ns")

        notepad = self.tabs.get("Notepad")
        if notepad:
            notepad.update_focus_btn(self.focus_mode)
