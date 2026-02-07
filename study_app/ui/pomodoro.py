"""
pomodoro.py — Pomodoro Timer tab for StudyForge.
Full-featured timer with work/break cycles, session tracking, and stats.
"""

import customtkinter as ctk
from datetime import datetime
import threading
import platform
from ui.styles import COLORS, FONTS, PADDING
import database as db

# winsound is Windows-only; graceful fallback on other platforms
try:
    import winsound
except ImportError:
    winsound = None


class PomodoroTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref

        # Timer state
        self.config = app_ref.config
        self.work_duration = self.config.get("pomodoro_work_minutes", 25) * 60
        self.short_break = self.config.get("pomodoro_short_break", 5) * 60
        self.long_break = self.config.get("pomodoro_long_break", 15) * 60
        self.sessions_for_long = self.config.get("pomodoro_sessions_before_long_break", 4)

        self.time_remaining = self.work_duration
        self.is_running = False
        self.is_work = True
        self.session_count = 0
        self.total_work_today = 0
        self.started_at = None
        self._timer_id = None

        self.build_ui()

    def build_ui(self):
        # Header
        ctk.CTkLabel(
            self, text="🍅 Pomodoro Timer",
            font=FONTS["heading"], text_color=COLORS["text_primary"]
        ).pack(padx=PADDING["page"], pady=(PADDING["page"], 5), anchor="w")

        # Center container
        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(expand=True, fill="both", padx=PADDING["page"])

        # Timer display card
        timer_card = ctk.CTkFrame(center, fg_color=COLORS["bg_card"], corner_radius=16)
        timer_card.pack(pady=20)

        # Session type label
        self.session_label = ctk.CTkLabel(
            timer_card, text="WORK SESSION",
            font=FONTS["timer_label"], text_color=COLORS["timer_work"]
        )
        self.session_label.pack(pady=(24, 0))

        # Time display
        self.time_display = ctk.CTkLabel(
            timer_card, text=self._format_time(self.time_remaining),
            font=FONTS["timer"], text_color=COLORS["text_primary"]
        )
        self.time_display.pack(padx=60, pady=(0, 5))

        # Progress bar
        self.progress = ctk.CTkProgressBar(
            timer_card, width=350, height=8,
            fg_color=COLORS["bg_secondary"],
            progress_color=COLORS["timer_work"],
            corner_radius=4
        )
        self.progress.set(1.0)
        self.progress.pack(pady=(0, 5))

        # Session dots
        self.dots_frame = ctk.CTkFrame(timer_card, fg_color="transparent")
        self.dots_frame.pack(pady=(0, 20))
        self._update_dots()

        # Control buttons
        btn_frame = ctk.CTkFrame(center, fg_color="transparent")
        btn_frame.pack(pady=10)

        self.start_btn = ctk.CTkButton(
            btn_frame, text="▶  Start", width=130, height=45,
            font=FONTS["body_bold"], fg_color=COLORS["accent"],
            hover_color=COLORS["accent_hover"], corner_radius=10,
            command=self.toggle_timer
        )
        self.start_btn.pack(side="left", padx=6)

        self.skip_btn = ctk.CTkButton(
            btn_frame, text="⏭  Skip", width=130, height=45,
            font=FONTS["body_bold"], fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_secondary"], corner_radius=10,
            command=self.skip_session
        )
        self.skip_btn.pack(side="left", padx=6)

        self.reset_btn = ctk.CTkButton(
            btn_frame, text="↺  Reset", width=130, height=45,
            font=FONTS["body_bold"], fg_color=COLORS["bg_card"],
            hover_color=COLORS["bg_secondary"], corner_radius=10,
            command=self.reset_timer
        )
        self.reset_btn.pack(side="left", padx=6)

        # Settings row
        settings_frame = ctk.CTkFrame(center, fg_color=COLORS["bg_card"], corner_radius=12)
        settings_frame.pack(fill="x", pady=15)

        ctk.CTkLabel(
            settings_frame, text="⚙️ Timer Settings",
            font=FONTS["body_bold"], text_color=COLORS["text_primary"]
        ).pack(padx=PADDING["section"], pady=(10, 5), anchor="w")

        sliders_frame = ctk.CTkFrame(settings_frame, fg_color="transparent")
        sliders_frame.pack(fill="x", padx=PADDING["section"], pady=(0, 12))
        sliders_frame.grid_columnconfigure((0, 1, 2), weight=1)

        # Work duration slider
        self._create_slider(sliders_frame, 0, "Work (min)", 15, 60,
                            self.work_duration // 60, self._on_work_change)
        # Short break slider
        self._create_slider(sliders_frame, 1, "Short Break", 3, 15,
                            self.short_break // 60, self._on_short_break_change)
        # Long break slider
        self._create_slider(sliders_frame, 2, "Long Break", 10, 30,
                            self.long_break // 60, self._on_long_break_change)

        # Stats row
        self.stats_label = ctk.CTkLabel(
            center, text="",
            font=FONTS["body"], text_color=COLORS["text_secondary"]
        )
        self.stats_label.pack(pady=5)
        self._update_stats_label()

    def _create_slider(self, parent, col, label, min_val, max_val, initial, callback):
        frame = ctk.CTkFrame(parent, fg_color="transparent")
        frame.grid(row=0, column=col, padx=8, sticky="ew")

        val_label = ctk.CTkLabel(
            frame, text=f"{label}: {initial}",
            font=FONTS["small"], text_color=COLORS["text_secondary"]
        )
        val_label.pack()

        slider = ctk.CTkSlider(
            frame, from_=min_val, to=max_val, number_of_steps=max_val - min_val,
            fg_color=COLORS["bg_secondary"], progress_color=COLORS["accent"],
            button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"],
            command=lambda v, lbl=val_label, lb=label, cb=callback: self._slider_update(v, lbl, lb, cb)
        )
        slider.set(initial)
        slider.pack(fill="x", padx=4, pady=4)

    def _slider_update(self, value, label_widget, label_text, callback):
        val = int(value)
        label_widget.configure(text=f"{label_text}: {val}")
        callback(val)

    def _on_work_change(self, val):
        self.work_duration = val * 60
        if not self.is_running and self.is_work:
            self.time_remaining = self.work_duration
            self.time_display.configure(text=self._format_time(self.time_remaining))
            self.progress.set(1.0)

    def _on_short_break_change(self, val):
        self.short_break = val * 60

    def _on_long_break_change(self, val):
        self.long_break = val * 60

    def _format_time(self, seconds):
        m, s = divmod(max(0, seconds), 60)
        return f"{m:02d}:{s:02d}"

    def _update_dots(self):
        for w in self.dots_frame.winfo_children():
            w.destroy()
        for i in range(self.sessions_for_long):
            color = COLORS["accent"] if i < (self.session_count % self.sessions_for_long) else COLORS["bg_secondary"]
            dot = ctk.CTkFrame(self.dots_frame, width=14, height=14, corner_radius=7, fg_color=color)
            dot.pack(side="left", padx=3)

    def toggle_timer(self):
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()

    def start_timer(self):
        self.is_running = True
        self.start_btn.configure(text="⏸  Pause")
        if self.started_at is None:
            self.started_at = datetime.now().isoformat()
        self._last_tick_time = datetime.now()
        self._tick()

    def pause_timer(self):
        self.is_running = False
        self.start_btn.configure(text="▶  Resume")
        if self._timer_id:
            self.after_cancel(self._timer_id)

    def _tick(self):
        if not self.is_running:
            return

        now = datetime.now()
        elapsed = (now - self._last_tick_time).total_seconds()
        self._last_tick_time = now
        self.time_remaining = max(0, self.time_remaining - round(elapsed))

        self.time_display.configure(text=self._format_time(self.time_remaining))

        # Update progress
        total = self.work_duration if self.is_work else self._current_break_duration()
        progress = self.time_remaining / total if total > 0 else 0
        self.progress.set(progress)

        if self.time_remaining > 0:
            self._timer_id = self.after(1000, self._tick)
        else:
            self._session_complete()

    def _current_break_duration(self):
        if self.session_count % self.sessions_for_long == 0 and self.session_count > 0:
            return self.long_break
        return self.short_break

    def _session_complete(self):
        self.is_running = False
        self.start_btn.configure(text="▶  Start")
        finished_at = datetime.now().isoformat()

        # Play sound notification
        try:
            if winsound:
                threading.Thread(target=lambda: winsound.MessageBeep(winsound.MB_ICONEXCLAMATION), daemon=True).start()
            elif platform.system() == "Darwin":
                import subprocess
                threading.Thread(target=lambda: subprocess.run(["afplay", "/System/Library/Sounds/Glass.aiff"], capture_output=True), daemon=True).start()
        except Exception:
            pass

        if self.is_work:
            # Calculate actual elapsed minutes
            try:
                actual_minutes = int((datetime.fromisoformat(finished_at) - datetime.fromisoformat(self.started_at)).total_seconds() / 60)
            except Exception:
                actual_minutes = self.work_duration // 60
            # Log work session
            db.log_pomodoro("work", actual_minutes, self.started_at, finished_at)
            self.session_count += 1
            self.total_work_today += actual_minutes
            self._update_dots()

            # Switch to break
            self.is_work = False
            if self.session_count % self.sessions_for_long == 0:
                self.time_remaining = self.long_break
                self.session_label.configure(text="☕ LONG BREAK", text_color=COLORS["timer_break"])
            else:
                self.time_remaining = self.short_break
                self.session_label.configure(text="☕ SHORT BREAK", text_color=COLORS["timer_break"])
            self.progress.configure(progress_color=COLORS["timer_break"])
        else:
            # Switch to work
            db.log_pomodoro("break", self._current_break_duration() // 60, self.started_at, finished_at)
            self.is_work = True
            self.time_remaining = self.work_duration
            self.session_label.configure(text="WORK SESSION", text_color=COLORS["timer_work"])
            self.progress.configure(progress_color=COLORS["timer_work"])

        self.started_at = None
        self.time_display.configure(text=self._format_time(self.time_remaining))
        self.progress.set(1.0)
        self._update_stats_label()

    def skip_session(self):
        self.pause_timer()
        self.is_work = not self.is_work
        if self.is_work:
            self.time_remaining = self.work_duration
            self.session_label.configure(text="WORK SESSION", text_color=COLORS["timer_work"])
            self.progress.configure(progress_color=COLORS["timer_work"])
        else:
            if self.session_count % self.sessions_for_long == 0 and self.session_count > 0:
                self.time_remaining = self.long_break
                self.session_label.configure(text="☕ LONG BREAK", text_color=COLORS["timer_break"])
            else:
                self.time_remaining = self.short_break
                self.session_label.configure(text="☕ SHORT BREAK", text_color=COLORS["timer_break"])
            self.progress.configure(progress_color=COLORS["timer_break"])

        self.started_at = None
        self.time_display.configure(text=self._format_time(self.time_remaining))
        self.progress.set(1.0)

    def reset_timer(self):
        self.pause_timer()
        self.is_work = True
        self.time_remaining = self.work_duration
        self.session_count = 0
        self.started_at = None
        self.time_display.configure(text=self._format_time(self.time_remaining))
        self.session_label.configure(text="WORK SESSION", text_color=COLORS["timer_work"])
        self.progress.configure(progress_color=COLORS["timer_work"])
        self.progress.set(1.0)
        self._update_dots()

    def _update_stats_label(self):
        stats = db.get_today_stats()
        self.stats_label.configure(
            text=f"Today: {stats['pomodoro_sessions']} sessions completed  ·  "
                 f"{stats['study_minutes']} minutes focused"
        )
