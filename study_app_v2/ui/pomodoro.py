"""pomodoro.py — Pomodoro Timer tab."""

import customtkinter as ctk
from datetime import datetime
import threading
from ui.styles import COLORS, FONTS, PAD, BUTTON_VARIANTS
import database as db


class PomodoroTab(ctk.CTkFrame):
    def __init__(self, parent, app_ref):
        super().__init__(parent, fg_color="transparent")
        self.app = app_ref
        c = app_ref.config
        self.work_dur = c.get("pomodoro_work_minutes", 25) * 60
        self.short_brk = c.get("pomodoro_short_break", 5) * 60
        self.long_brk = c.get("pomodoro_long_break", 15) * 60
        self.sessions_for_long = c.get("pomodoro_sessions_before_long_break", 4)
        self.time_left = self.work_dur
        self.running = False
        self.is_work = True
        self.session_count = 0
        self.started_at = None
        self._tid = None
        self.build_ui()

    def build_ui(self):
        ctk.CTkLabel(self, text="🍅 Pomodoro Timer", font=FONTS["heading"],
            text_color=COLORS["text_primary"]).pack(padx=PAD["page"], pady=(PAD["page"], 5), anchor="w")

        center = ctk.CTkFrame(self, fg_color="transparent")
        center.pack(expand=True, fill="both", padx=PAD["page"])

        tc = ctk.CTkFrame(center, fg_color=COLORS["bg_card"], corner_radius=16)
        tc.pack(pady=20)

        self.sess_label = ctk.CTkLabel(tc, text="WORK SESSION", font=FONTS["timer_label"],
            text_color=COLORS["timer_work"])
        self.sess_label.pack(pady=(24, 0))

        self.time_disp = ctk.CTkLabel(tc, text=self._fmt(self.time_left),
            font=FONTS["timer"], text_color=COLORS["text_primary"])
        self.time_disp.pack(padx=60, pady=(0, 5))

        self.prog = ctk.CTkProgressBar(tc, width=350, height=8,
            fg_color=COLORS["bg_secondary"], progress_color=COLORS["timer_work"], corner_radius=4)
        self.prog.set(1.0)
        self.prog.pack(pady=(0, 5))

        self.dots_frame = ctk.CTkFrame(tc, fg_color="transparent")
        self.dots_frame.pack(pady=(0, 20))
        self._update_dots()

        bf = ctk.CTkFrame(center, fg_color="transparent")
        bf.pack(pady=10)

        self.start_btn = ctk.CTkButton(bf, text="▶  Start", width=130, height=45,
            font=FONTS["body_bold"], corner_radius=10, command=self.toggle,
            **BUTTON_VARIANTS["primary"])
        self.start_btn.pack(side="left", padx=6)

        ctk.CTkButton(bf, text="⏭  Skip", width=130, height=45, font=FONTS["body_bold"],
            fg_color=BUTTON_VARIANTS["secondary"]["fg_color"], hover_color=BUTTON_VARIANTS["secondary"]["hover_color"],
            corner_radius=10, command=self.skip).pack(side="left", padx=6)

        ctk.CTkButton(bf, text="↺  Reset", width=130, height=45, font=FONTS["body_bold"],
            fg_color=BUTTON_VARIANTS["secondary"]["fg_color"], hover_color=BUTTON_VARIANTS["secondary"]["hover_color"],
            corner_radius=10, command=self.reset).pack(side="left", padx=6)

        # Settings row
        sf = ctk.CTkFrame(center, fg_color=COLORS["bg_card"], corner_radius=12)
        sf.pack(fill="x", pady=15)
        ctk.CTkLabel(sf, text="⚙️ Timer Settings", font=FONTS["body_bold"],
            text_color=COLORS["text_primary"]).pack(padx=PAD["section"], pady=(10, 5), anchor="w")

        sg = ctk.CTkFrame(sf, fg_color="transparent")
        sg.pack(fill="x", padx=PAD["section"], pady=(0, 12))
        sg.grid_columnconfigure((0,1,2), weight=1)

        self._mk_slider(sg, 0, "Work (min)", 15, 60, self.work_dur//60, self._on_work)
        self._mk_slider(sg, 1, "Short Break", 3, 15, self.short_brk//60, self._on_short)
        self._mk_slider(sg, 2, "Long Break", 10, 30, self.long_brk//60, self._on_long)

        self.stats_lbl = ctk.CTkLabel(center, text="", font=FONTS["body"],
            text_color=COLORS["text_secondary"])
        self.stats_lbl.pack(pady=5)
        self._update_stats()

    def _mk_slider(self, parent, col, label, mn, mx, init, cb):
        f = ctk.CTkFrame(parent, fg_color="transparent")
        f.grid(row=0, column=col, padx=8, sticky="ew")
        vl = ctk.CTkLabel(f, text=f"{label}: {init}", font=FONTS["small"], text_color=COLORS["text_secondary"])
        vl.pack()
        s = ctk.CTkSlider(f, from_=mn, to=mx, number_of_steps=mx-mn,
            fg_color=COLORS["bg_secondary"], progress_color=COLORS["accent"],
            button_color=COLORS["accent"], button_hover_color=COLORS["accent_hover"],
            command=lambda v, _vl=vl, _lb=label, _cb=cb: (
                _vl.configure(text=f"{_lb}: {int(v)}"), _cb(int(v))))
        s.set(init)
        s.pack(fill="x", padx=4, pady=4)

    def _on_work(self, v):
        self.work_dur = v * 60
        if not self.running and self.is_work:
            self.time_left = self.work_dur
            self.time_disp.configure(text=self._fmt(self.time_left)); self.prog.set(1.0)

    def _on_short(self, v): self.short_brk = v * 60
    def _on_long(self, v): self.long_brk = v * 60

    def _fmt(self, s):
        m, s = divmod(max(0, s), 60); return f"{m:02d}:{s:02d}"

    def _update_dots(self):
        for w in self.dots_frame.winfo_children(): w.destroy()
        for i in range(self.sessions_for_long):
            c = COLORS["accent"] if i < (self.session_count % self.sessions_for_long) else COLORS["bg_secondary"]
            ctk.CTkFrame(self.dots_frame, width=14, height=14, corner_radius=7, fg_color=c).pack(side="left", padx=3)

    def toggle(self):
        if self.running: self.pause()
        else: self.start()

    def start(self):
        self.running = True
        self.start_btn.configure(text="⏸  Pause")
        if not self.started_at: self.started_at = datetime.now().isoformat()
        self._tick()

    def pause(self):
        self.running = False
        self.start_btn.configure(text="▶  Resume")
        if self._tid: self.after_cancel(self._tid)

    def _tick(self):
        if not self.running: return
        if self.time_left > 0:
            self.time_left -= 1
            self.time_disp.configure(text=self._fmt(self.time_left))
            total = self.work_dur if self.is_work else self._brk_dur()
            self.prog.set(self.time_left / total if total else 0)
            self._tid = self.after(1000, self._tick)
        else:
            self._complete()

    def _brk_dur(self):
        return self.long_brk if (self.session_count % self.sessions_for_long == 0 and self.session_count > 0) else self.short_brk

    def _complete(self):
        self.running = False
        self.start_btn.configure(text="▶  Start")
        fin = datetime.now().isoformat()
        try:
            import winsound
            threading.Thread(target=lambda: winsound.MessageBeep(winsound.MB_ICONEXCLAMATION), daemon=True).start()
        except: pass

        if self.is_work:
            db.log_pomodoro("work", self.work_dur // 60, self.started_at, fin)
            self.session_count += 1
            self._update_dots()
            self.is_work = False
            if self.session_count % self.sessions_for_long == 0:
                self.time_left = self.long_brk
                self.sess_label.configure(text="☕ LONG BREAK", text_color=COLORS["timer_break"])
            else:
                self.time_left = self.short_brk
                self.sess_label.configure(text="☕ SHORT BREAK", text_color=COLORS["timer_break"])
            self.prog.configure(progress_color=COLORS["timer_break"])
        else:
            db.log_pomodoro("break", self._brk_dur() // 60, self.started_at, fin)
            self.is_work = True
            self.time_left = self.work_dur
            self.sess_label.configure(text="WORK SESSION", text_color=COLORS["timer_work"])
            self.prog.configure(progress_color=COLORS["timer_work"])

        self.started_at = None
        self.time_disp.configure(text=self._fmt(self.time_left))
        self.prog.set(1.0)
        self._update_stats()

    def skip(self):
        self.pause()
        self.is_work = not self.is_work
        if self.is_work:
            self.time_left = self.work_dur
            self.sess_label.configure(text="WORK SESSION", text_color=COLORS["timer_work"])
            self.prog.configure(progress_color=COLORS["timer_work"])
        else:
            self.time_left = self._brk_dur()
            lbl = "☕ LONG BREAK" if (self.session_count % self.sessions_for_long == 0 and self.session_count > 0) else "☕ SHORT BREAK"
            self.sess_label.configure(text=lbl, text_color=COLORS["timer_break"])
            self.prog.configure(progress_color=COLORS["timer_break"])
        self.started_at = None
        self.time_disp.configure(text=self._fmt(self.time_left))
        self.prog.set(1.0)

    def reset(self):
        self.pause()
        self.is_work = True; self.time_left = self.work_dur; self.session_count = 0; self.started_at = None
        self.time_disp.configure(text=self._fmt(self.time_left))
        self.sess_label.configure(text="WORK SESSION", text_color=COLORS["timer_work"])
        self.prog.configure(progress_color=COLORS["timer_work"]); self.prog.set(1.0)
        self._update_dots()

    def _update_stats(self):
        s = db.get_today_stats()
        self.stats_lbl.configure(text=f"Today: {s['pomodoro_sessions']} sessions  ·  {s['study_minutes']} min focused")
