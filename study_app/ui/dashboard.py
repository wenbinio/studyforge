"""
dashboard.py — Dashboard / Home tab for StudyForge.
Shows daily stats, streak, due cards, and review forecast.
"""

import customtkinter as ctk
from datetime import date
from ui.styles import COLORS, FONTS, PADDING
import database as db


class DashboardTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.build_ui()

    def build_ui(self):
        # Header
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PADDING["page"], pady=(PADDING["page"], 5))

        ctk.CTkLabel(
            header, text="📊 Dashboard",
            font=FONTS["heading"], text_color=COLORS["text_primary"]
        ).pack(side="left")

        today_str = date.today().strftime("%A, %B %d, %Y")
        ctk.CTkLabel(
            header, text=today_str,
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        ).pack(side="right")

        # Stats cards row
        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=PADDING["page"], pady=PADDING["section"])

        # Main content area
        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=PADDING["page"], pady=(0, PADDING["page"]))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        # Left: Quick Actions
        self.actions_frame = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        self.actions_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8), pady=0)

        # Right: Review forecast
        self.forecast_frame = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        self.forecast_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0), pady=0)
        content.grid_rowconfigure(0, weight=1)

        self.refresh()

    def refresh(self):
        """Refresh all dashboard data."""
        stats = db.get_today_stats()
        streak = db.get_streak()
        due = len(db.get_due_cards())
        total = db.get_total_cards()

        # Clear and rebuild stat cards
        for w in self.stats_frame.winfo_children():
            w.destroy()

        self.stats_frame.grid_columnconfigure((0, 1, 2, 3, 4), weight=1)

        stat_items = [
            ("🔥", str(streak), "Day Streak", COLORS["danger"]),
            ("📚", str(due), "Cards Due", COLORS["warning"]),
            ("✅", str(stats["cards_reviewed"]), "Reviewed Today", COLORS["success"]),
            ("🍅", str(stats["pomodoro_sessions"]), "Pomodoros Today", COLORS["accent"]),
            ("⏱️", f"{stats['study_minutes']}m", "Study Time", COLORS["accent_light"]),
        ]

        for i, (icon, value, label, color) in enumerate(stat_items):
            card = ctk.CTkFrame(self.stats_frame, fg_color=COLORS["bg_card"], corner_radius=12)
            card.grid(row=0, column=i, sticky="nsew", padx=4, pady=0)

            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 20)).pack(pady=(12, 2))
            ctk.CTkLabel(
                card, text=value,
                font=FONTS["stat_number"], text_color=color
            ).pack(pady=0)
            ctk.CTkLabel(
                card, text=label,
                font=FONTS["stat_label"], text_color=COLORS["text_muted"]
            ).pack(pady=(0, 12))

        # Quick Actions
        for w in self.actions_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.actions_frame, text="⚡ Quick Actions",
            font=FONTS["subheading"], text_color=COLORS["text_primary"]
        ).pack(padx=PADDING["section"], pady=(PADDING["section"], 10), anchor="w")

        actions = [
            ("🧠  Review Due Cards", lambda: self.app.select_tab("Flashcards"), COLORS["accent"], due > 0),
            ("🍅  Start Pomodoro", lambda: self.app.select_tab("Pomodoro"), COLORS["timer_work"], True),
            ("📝  Add New Note", lambda: self.app.select_tab("Notes"), COLORS["success"], True),
            ("❓  Take a Quiz", lambda: self.app.select_tab("Quiz"), COLORS["warning"], True),
        ]

        for text, cmd, color, enabled in actions:
            btn = ctk.CTkButton(
                self.actions_frame, text=text, command=cmd,
                fg_color=color if enabled else COLORS["bg_secondary"],
                hover_color=COLORS["accent_hover"],
                font=FONTS["body_bold"], height=42, anchor="w",
                corner_radius=8
            )
            btn.pack(fill="x", padx=PADDING["section"], pady=3)

        # Status summary
        summary_text = f"\n📦 Total flashcards in collection: {total}"
        if due > 0:
            summary_text += f"\n⚠️ You have {due} card{'s' if due != 1 else ''} due for review!"
        else:
            summary_text += "\n✨ All caught up! No cards due right now."

        ctk.CTkLabel(
            self.actions_frame, text=summary_text,
            font=FONTS["small"], text_color=COLORS["text_secondary"],
            justify="left", wraplength=300
        ).pack(padx=PADDING["section"], pady=PADDING["section"], anchor="w")

        # Forecast
        for w in self.forecast_frame.winfo_children():
            w.destroy()

        ctk.CTkLabel(
            self.forecast_frame, text="📅 Upcoming Reviews (7 days)",
            font=FONTS["subheading"], text_color=COLORS["text_primary"]
        ).pack(padx=PADDING["section"], pady=(PADDING["section"], 10), anchor="w")

        from srs_engine import forecast_reviews
        all_cards = db.get_all_flashcards()
        forecast = forecast_reviews(all_cards, days_ahead=7)

        from datetime import timedelta
        today = date.today()
        for i in range(7):
            d = today + timedelta(days=i)
            d_str = d.isoformat()
            count = forecast.get(d_str, 0)
            day_label = "Today" if i == 0 else ("Tomorrow" if i == 1 else d.strftime("%a %b %d"))

            row = ctk.CTkFrame(self.forecast_frame, fg_color="transparent")
            row.pack(fill="x", padx=PADDING["section"], pady=2)

            ctk.CTkLabel(
                row, text=day_label,
                font=FONTS["body"], text_color=COLORS["text_secondary"], width=120, anchor="w"
            ).pack(side="left")

            # Bar
            bar_frame = ctk.CTkFrame(row, fg_color=COLORS["bg_secondary"], height=18, corner_radius=4)
            bar_frame.pack(side="left", fill="x", expand=True, padx=8)
            bar_frame.pack_propagate(False)

            max_count = max(forecast.values()) if forecast.values() and max(forecast.values()) > 0 else 1
            bar_width = max(0.02, count / max_count)
            color = COLORS["accent"] if count > 0 else COLORS["bg_secondary"]
            bar_fill = ctk.CTkFrame(bar_frame, fg_color=color, corner_radius=4)
            bar_fill.place(relx=0, rely=0, relwidth=bar_width, relheight=1)

            ctk.CTkLabel(
                row, text=str(count),
                font=FONTS["body_bold"],
                text_color=COLORS["warning"] if count > 10 else COLORS["text_primary"],
                width=40, anchor="e"
            ).pack(side="right")

        # Weekly stats
        week_stats = db.get_stats_range(7)
        total_reviewed = sum(s.get("cards_reviewed", 0) for s in week_stats)
        total_study = sum(s.get("study_minutes", 0) for s in week_stats)

        summary = f"\n📈 This week: {total_reviewed} cards reviewed, {total_study} min studied"
        ctk.CTkLabel(
            self.forecast_frame, text=summary,
            font=FONTS["small"], text_color=COLORS["text_secondary"],
            wraplength=300, justify="left"
        ).pack(padx=PADDING["section"], pady=(10, PADDING["section"]), anchor="w")
