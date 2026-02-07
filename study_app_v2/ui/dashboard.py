"""dashboard.py — Home tab with stats overview."""

import customtkinter as ctk
from datetime import date, timedelta
from ui.styles import COLORS, FONTS, PAD
import database as db


class DashboardTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        self.build_ui()

    def build_ui(self):
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.pack(fill="x", padx=PAD["page"], pady=(PAD["page"], 5))
        ctk.CTkLabel(header, text="📊 Dashboard", font=FONTS["heading"],
                      text_color=COLORS["text_primary"]).pack(side="left")
        ctk.CTkLabel(header, text=date.today().strftime("%A, %B %d, %Y"),
                      font=FONTS["body"], text_color=COLORS["text_secondary"]).pack(side="right")

        self.stats_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.stats_frame.pack(fill="x", padx=PAD["page"], pady=PAD["section"])

        content = ctk.CTkFrame(self, fg_color="transparent")
        content.pack(fill="both", expand=True, padx=PAD["page"], pady=(0, PAD["page"]))
        content.grid_columnconfigure(0, weight=1)
        content.grid_columnconfigure(1, weight=1)

        self.actions_frame = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        self.actions_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        self.forecast_frame = ctk.CTkFrame(content, fg_color=COLORS["bg_card"], corner_radius=12)
        self.forecast_frame.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        content.grid_rowconfigure(0, weight=1)

        self.refresh()

    def refresh(self):
        stats = db.get_today_stats()
        streak = db.get_streak()
        due = len(db.get_due_cards())
        total = db.get_total_cards()

        for w in self.stats_frame.winfo_children(): w.destroy()
        self.stats_frame.grid_columnconfigure((0,1,2,3,4), weight=1)

        items = [
            ("🔥", str(streak), "Day Streak", COLORS["danger"]),
            ("📚", str(due), "Cards Due", COLORS["warning"]),
            ("✅", str(stats["cards_reviewed"]), "Reviewed Today", COLORS["success"]),
            ("🍅", str(stats["pomodoro_sessions"]), "Pomodoros", COLORS["accent"]),
            ("⏱️", f"{stats['study_minutes']}m", "Study Time", COLORS["accent_light"]),
        ]

        for i, (icon, val, label, color) in enumerate(items):
            card = ctk.CTkFrame(self.stats_frame, fg_color=COLORS["bg_card"], corner_radius=12)
            card.grid(row=0, column=i, sticky="nsew", padx=4)
            ctk.CTkLabel(card, text=icon, font=("Segoe UI", 20)).pack(pady=(12, 2))
            ctk.CTkLabel(card, text=val, font=FONTS["stat_number"], text_color=color).pack()
            ctk.CTkLabel(card, text=label, font=FONTS["stat_label"], text_color=COLORS["text_muted"]).pack(pady=(0, 12))

        # Quick Actions
        for w in self.actions_frame.winfo_children(): w.destroy()
        ctk.CTkLabel(self.actions_frame, text="⚡ Quick Actions", font=FONTS["subheading"],
                      text_color=COLORS["text_primary"]).pack(padx=PAD["section"], pady=(PAD["section"], 10), anchor="w")

        actions = [
            ("🧠  Review Due Cards", lambda: self.app.select_tab("Flashcards"), COLORS["accent"]),
            ("🍅  Start Pomodoro", lambda: self.app.select_tab("Pomodoro"), COLORS["timer_work"]),
            ("📝  Add New Note", lambda: self.app.select_tab("Notes"), COLORS["success"]),
            ("❓  Take a Quiz", lambda: self.app.select_tab("Quiz"), COLORS["warning"]),
            ("⚙️  Settings", lambda: self.app.select_tab("Settings"), COLORS["bg_secondary"]),
        ]
        for text, cmd, color in actions:
            ctk.CTkButton(self.actions_frame, text=text, command=cmd, fg_color=color,
                hover_color=COLORS["accent_hover"], font=FONTS["body_bold"], height=42,
                anchor="w", corner_radius=8).pack(fill="x", padx=PAD["section"], pady=3)

        info = f"\n📦 Total cards: {total}"
        info += f"\n⚠️ {due} card{'s' if due!=1 else ''} due!" if due else "\n✨ All caught up!"
        ctk.CTkLabel(self.actions_frame, text=info, font=FONTS["small"],
            text_color=COLORS["text_secondary"], justify="left", wraplength=300
        ).pack(padx=PAD["section"], pady=PAD["section"], anchor="w")

        # Forecast
        for w in self.forecast_frame.winfo_children(): w.destroy()
        ctk.CTkLabel(self.forecast_frame, text="📅 Upcoming Reviews (7 days)", font=FONTS["subheading"],
            text_color=COLORS["text_primary"]).pack(padx=PAD["section"], pady=(PAD["section"], 10), anchor="w")

        from srs_engine import forecast_reviews
        all_cards = db.get_all_flashcards()
        forecast = forecast_reviews(all_cards, 7)
        today = date.today()
        max_c = max(forecast.values()) if forecast.values() and max(forecast.values()) > 0 else 1

        for i in range(7):
            d = today + timedelta(days=i)
            count = forecast.get(d.isoformat(), 0)
            day_label = "Today" if i == 0 else ("Tomorrow" if i == 1 else d.strftime("%a %b %d"))

            row = ctk.CTkFrame(self.forecast_frame, fg_color="transparent")
            row.pack(fill="x", padx=PAD["section"], pady=2)
            ctk.CTkLabel(row, text=day_label, font=FONTS["body"],
                text_color=COLORS["text_secondary"], width=120, anchor="w").pack(side="left")

            bar_frame = ctk.CTkFrame(row, fg_color=COLORS["bg_secondary"], height=18, corner_radius=4)
            bar_frame.pack(side="left", fill="x", expand=True, padx=8)
            bar_frame.pack_propagate(False)
            bw = max(0.02, count / max_c) if count else 0.02
            color = COLORS["accent"] if count else COLORS["bg_secondary"]
            ctk.CTkFrame(bar_frame, fg_color=color, corner_radius=4).place(relx=0, rely=0, relwidth=bw, relheight=1)

            ctk.CTkLabel(row, text=str(count), font=FONTS["body_bold"],
                text_color=COLORS["warning"] if count > 10 else COLORS["text_primary"],
                width=40, anchor="e").pack(side="right")

        week = db.get_stats_range(7)
        tr = sum(s.get("cards_reviewed", 0) for s in week)
        ts = sum(s.get("study_minutes", 0) for s in week)
        ctk.CTkLabel(self.forecast_frame, text=f"\n📈 This week: {tr} reviewed, {ts} min studied",
            font=FONTS["small"], text_color=COLORS["text_secondary"], wraplength=300, justify="left"
        ).pack(padx=PAD["section"], pady=(10, PAD["section"]), anchor="w")
