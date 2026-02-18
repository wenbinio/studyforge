"""
app.py — Main application window for StudyForge.
Manages the sidebar navigation and tab switching.
"""

import customtkinter as ctk
import os
import sys
import subprocess
from ui.styles import COLORS, FONTS, PADDING, BUTTON_VARIANTS
from ui.dashboard import DashboardTab
from ui.pomodoro import PomodoroTab
from ui.flashcards import FlashcardsTab
from ui.notes import NotesTab
from ui.quiz import QuizTab
from ui.hypotheticals import HypotheticalsTab
from ui.essays import EssaysTab
from ui.participation import ParticipationTab
from ui.settings import SettingsTab


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
        self.nav_order = []
        self.current_tab = None
        self.focus_mode = False
        self.sidebar = None

        self.build_ui()
        self.select_tab("Dashboard")
        self._bind_keyboard_shortcuts()

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
            ("❓", "Quiz"),
            ("⚖️", "Hypotheticals"),
            ("📜", "Essays"),
            ("🎓", "Participation"),
            ("⚙️", "Settings"),
        ]

        for icon, label in nav_items:
            self.nav_order.append(label)
            btn_frame = ctk.CTkFrame(sidebar, fg_color="transparent", corner_radius=8)
            btn_frame.pack(fill="x", padx=8, pady=2)

            icon_label = ctk.CTkLabel(btn_frame, text=icon, width=30, font=FONTS["body"],
                text_color=COLORS["text_secondary"])
            icon_label.pack(side="left", padx=(8, 0))

            btn = ctk.CTkButton(btn_frame, text=label, font=FONTS["body"], height=40,
                fg_color=BUTTON_VARIANTS["ghost"]["fg_color"], hover=False,
                text_color=COLORS["text_secondary"], anchor="w", corner_radius=8,
                border_width=1, border_color=COLORS["bg_secondary"],
                command=lambda l=label: self.select_tab(l))
            btn.pack(side="left", fill="x", expand=True)

            self.nav_buttons[label] = {"frame": btn_frame, "icon": icon_label, "btn": btn}

            # Full-row hover: bind Enter/Leave on frame and children
            for widget in (btn_frame, icon_label, btn):
                widget.bind("<Enter>", lambda e, l=label: self._on_nav_enter(l))
                widget.bind("<Leave>", lambda e, l=label: self._on_nav_leave(l))
            btn.bind("<FocusIn>", lambda _e, l=label: self._on_nav_focus_in(l))
            btn.bind("<FocusOut>", lambda _e, l=label: self._on_nav_focus_out(l))

        # Bottom section: API status
        spacer = ctk.CTkFrame(sidebar, fg_color="transparent")
        spacer.pack(fill="both", expand=True)

        ctk.CTkFrame(sidebar, height=1, fg_color=COLORS["border"]).pack(fill="x", padx=12, pady=(0, 8))

        api_status = "🟢 AI Connected" if self.claude_client else "🔴 AI Offline"
        api_color = COLORS["success"] if self.claude_client else COLORS["danger"]

        self.api_label = ctk.CTkLabel(
            sidebar, text=api_status,
            font=FONTS["small"], text_color=api_color
        )
        self.api_label.pack(padx=12, pady=(0, 4), anchor="w")

        hint = "" if self.claude_client else "Click Settings to configure"
        self.api_hint = ctk.CTkLabel(
            sidebar, text=hint, font=("Segoe UI", 9),
            text_color=COLORS["text_muted"]
        )
        self.api_hint.pack(padx=12, pady=(0, 14), anchor="w")

        self.shortcuts_hint = ctk.CTkLabel(
            sidebar, text="⌨ Alt+1..9 • Ctrl+Tab",
            font=("Segoe UI", 9), text_color=COLORS["text_muted"]
        )
        self.shortcuts_hint.pack(padx=12, pady=(0, 10), anchor="w")

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
        self.tabs["Quiz"] = QuizTab(self.content_area, self)
        self.tabs["Hypotheticals"] = HypotheticalsTab(self.content_area, self)
        self.tabs["Essays"] = EssaysTab(self.content_area, self)
        self.tabs["Participation"] = ParticipationTab(self.content_area, self)
        self.tabs["Settings"] = SettingsTab(self.content_area, self)

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

    def _on_nav_enter(self, label):
        """Highlight full nav row on hover."""
        if label != self.current_tab:
            widgets = self.nav_buttons[label]
            widgets["frame"].configure(fg_color=COLORS["bg_hover"])
            widgets["icon"].configure(text_color=COLORS["text_primary"])
            widgets["btn"].configure(fg_color=COLORS["bg_hover"])

    def _on_nav_leave(self, label):
        """Un-highlight nav row when mouse leaves the row area."""
        if label != self.current_tab:
            frame = self.nav_buttons[label]["frame"]
            # Avoid event bubbling: only un-highlight if pointer left the row
            x, y = frame.winfo_pointerxy()
            fx, fy = frame.winfo_rootx(), frame.winfo_rooty()
            if fx <= x < fx + frame.winfo_width() and fy <= y < fy + frame.winfo_height():
                return
            widgets = self.nav_buttons[label]
            widgets["frame"].configure(fg_color="transparent")
            widgets["icon"].configure(text_color=COLORS["text_secondary"])
            widgets["btn"].configure(fg_color="transparent")

    def _on_nav_focus_in(self, label):
        """Show a visible focus ring for keyboard navigation."""
        widgets = self.nav_buttons[label]
        widgets["btn"].configure(border_color=COLORS["accent_light"])

    def _on_nav_focus_out(self, label):
        """Clear focus ring when nav button loses focus."""
        widgets = self.nav_buttons[label]
        widgets["btn"].configure(border_color=COLORS["bg_secondary"])

    def _bind_keyboard_shortcuts(self):
        """Bind keyboard shortcuts for faster tab navigation."""
        for index, label in enumerate(self.nav_order, start=1):
            self.bind(f"<Alt-Key-{index}>", lambda _e, l=label: self.select_tab(l))
        self.bind("<Control-Tab>", lambda _e: self._cycle_tab(1))
        self.bind("<Control-Shift-Tab>", lambda _e: self._cycle_tab(-1))

    def _cycle_tab(self, direction: int):
        """Move to next/previous sidebar tab."""
        if self.current_tab not in self.nav_order:
            return
        current_index = self.nav_order.index(self.current_tab)
        next_index = (current_index + direction) % len(self.nav_order)
        self.select_tab(self.nav_order[next_index])

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
            elif tab_name == "Flashcards":
                # If in review or interleaved mode, refresh due cards
                fc = self.tabs["Flashcards"]
                if fc.mode == "review":
                    fc.start_review()
                elif fc.mode == "interleaved":
                    fc.start_interleaved_review()

        # Update nav button styles
        for name, widgets in self.nav_buttons.items():
            if name == tab_name:
                widgets["frame"].configure(fg_color=COLORS["accent"])
                widgets["icon"].configure(text_color=COLORS["text_primary"])
                widgets["btn"].configure(fg_color=COLORS["accent"], text_color=COLORS["text_primary"])
            else:
                widgets["frame"].configure(fg_color="transparent")
                widgets["icon"].configure(text_color=COLORS["text_secondary"])
                widgets["btn"].configure(fg_color="transparent", text_color=COLORS["text_secondary"])

    def update_api_indicator(self, connected: bool):
        """Called by Settings tab when API connection changes."""
        if connected:
            self.api_label.configure(text="🟢 AI Connected", text_color=COLORS["success"])
            self.api_hint.configure(text="")
        else:
            self.api_label.configure(text="🔴 AI Offline", text_color=COLORS["danger"])
            self.api_hint.configure(text="Click Settings to configure")

    def toggle_focus_mode(self):
        """Toggle sidebar visibility for distraction-free writing."""
        self.focus_mode = not self.focus_mode
        if self.focus_mode:
            self.sidebar.grid_forget()
        else:
            self.sidebar.grid(row=0, column=0, sticky="ns")

        notes = self.tabs.get("Notes")
        if notes:
            notes.update_focus_btn(self.focus_mode)
