"""
Main application class – composes mixins for UI, theme and timer,
adds key bindings, tempo / play logic and display updates.
"""

from __future__ import annotations

import os
import tkinter as tk
from tkinter import messagebox
import time

from source.constants import (
    FONT_FAMILY as _FONT, ICON_PATH,
    PRACTICE_MINUTES, REQUIRED_CLEAN_PLAYS,
    BPM_INCREMENT, DEFAULT_BPM, MIN_BPM, MAX_BPM,
    SPEED_INCREMENT, DEFAULT_SPEED, MIN_SPEED, MAX_SPEED,
    MODE_BPM, MODE_SPEED,
)
from source.themes import C
from source.stats_window import show_stats_window
from source.ui_builder import UIBuilderMixin
from source.ui_theme import ThemeMixin
from source.timer import TimerMixin


class PomodoroGuitarApp(UIBuilderMixin, ThemeMixin, TimerMixin):
    """Main application – inherits UI-build, theme and timer mixins."""

    # ════════════════════════════════════════════════════════════════════════
    #  INIT
    # ════════════════════════════════════════════════════════════════════════

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Pomodoro Guitar Practice")
        self.root.resizable(False, False)
        self.root.configure(bg=C["bg"])

        # ── Set window icon (title-bar + taskbar) ──────────────────────────
        if os.path.isfile(ICON_PATH):
            try:
                self.root.iconbitmap(ICON_PATH)
            except Exception:
                pass

        # ── State ──────────────────────────────────────────────────────────
        self.mode = MODE_BPM
        self.bpm = DEFAULT_BPM
        self.speed = DEFAULT_SPEED
        self.starting_bpm = DEFAULT_BPM
        self.starting_speed = DEFAULT_SPEED
        self.clean_plays = 0
        self.total_clean = 0
        self.total_errors = 0
        self.completed_cycles = 0
        self.tempo_raises = 0
        self.is_practice = True
        self.timer_running = False
        self.timer_paused = False
        self.remaining_seconds = 0
        self.total_phase_seconds = 0
        self.timer_id = None
        self.always_on_top = False
        self.current_theme = "light"

        # ── Statistics tracking ────────────────────────────────────────────
        self.session_start = time.time()
        self.total_practice_seconds = 0
        self.total_break_seconds = 0
        self.tempo_history: list[tuple[float, int, float]] = []
        self._alerted_30s = False
        self._alerted_10s = False

        self.tempo_history.append((0.0, self.bpm, self.speed))

        # ── Build GUI ──────────────────────────────────────────────────────
        self._build_ui()
        self._update_tempo_display()
        self._update_clean_display()
        self._update_raise_button_state()
        self._bind_keys()

    # ════════════════════════════════════════════════════════════════════════
    #  HELPERS
    # ════════════════════════════════════════════════════════════════════════

    def _elapsed_minutes(self) -> float:
        return (time.time() - self.session_start) / 60.0

    # ════════════════════════════════════════════════════════════════════════
    #  KEY BINDINGS
    # ════════════════════════════════════════════════════════════════════════

    def _bind_keys(self) -> None:
        self.root.bind("<space>", self._key_space)
        for ch, fn in [
            ("s", self._stop_timer), ("n", self._skip_phase),
            ("h", self._on_clean_play), ("e", self._on_error_play),
            ("u", self._on_raise_tempo), ("t", self._toggle_always_on_top),
            ("d", self._toggle_theme), ("i", self._show_stats_window),
        ]:
            self.root.bind(ch, lambda e, f=fn: f())
            self.root.bind(ch.upper(), lambda e, f=fn: f())

        self.root.bind("1", lambda e: self._on_clean_play())
        self.root.bind("2", lambda e: self._on_error_play())
        self.root.bind("3", lambda e: self._on_raise_tempo())

    def _key_space(self, _event=None) -> None:
        if self.root.focus_get() == self.tempo_entry:
            return
        if self.timer_paused:
            self._resume_timer()
        elif self.timer_running:
            self._pause_timer()
        else:
            self._start_or_resume_timer()

    # ════════════════════════════════════════════════════════════════════════
    #  MODE CHANGE
    # ════════════════════════════════════════════════════════════════════════

    def _on_mode_change(self) -> None:
        self.mode = self.mode_var.get()
        self.clean_plays = 0
        if self.mode == MODE_BPM:
            self.tempo_label.configure(text="BPM:")
            self.tempo_var.set(str(self.bpm))
        else:
            self.tempo_label.configure(text="Speed:")
            self.tempo_var.set(f"{self.speed:.2f}")
        self._update_tempo_display()
        self._update_clean_display()
        self._update_raise_button_state()
        self._update_raise_button_text()

    # ════════════════════════════════════════════════════════════════════════
    #  TEMPO & PLAY LOGIC
    # ════════════════════════════════════════════════════════════════════════

    def _on_tempo_entry(self, _event=None) -> None:
        raw = self.tempo_var.get().strip()
        if self.mode == MODE_BPM:
            try:
                val = int(raw)
            except ValueError:
                messagebox.showwarning(
                    "Invalid Input",
                    "Please enter a whole number for BPM!",
                )
                self.tempo_var.set(str(self.bpm))
                return
            if val < MIN_BPM or val > MAX_BPM:
                messagebox.showwarning(
                    "Out of Range",
                    f"BPM must be between {MIN_BPM} and {MAX_BPM}!",
                )
                self.tempo_var.set(str(self.bpm))
                return
            self.bpm = val
        else:
            try:
                val = float(raw)
            except ValueError:
                messagebox.showwarning(
                    "Invalid Input",
                    "Please enter a number (e.g. 0.30)!",
                )
                self.tempo_var.set(f"{self.speed:.2f}")
                return
            if val < MIN_SPEED or val > MAX_SPEED:
                messagebox.showwarning(
                    "Out of Range",
                    f"Speed must be between {MIN_SPEED:.2f}x and {MAX_SPEED:.2f}x!",
                )
                self.tempo_var.set(f"{self.speed:.2f}")
                return
            self.speed = round(val, 2)

        if self.tempo_raises == 0:
            self.starting_bpm = self.bpm
            self.starting_speed = self.speed

        self.tempo_history.append(
            (self._elapsed_minutes(), self.bpm, self.speed),
        )
        self.clean_plays = 0
        self._update_tempo_display()
        self._update_clean_display()
        self._update_raise_button_state()

    def _on_clean_play(self) -> None:
        self.clean_plays += 1
        self.total_clean += 1
        self._update_clean_display()
        self._update_raise_button_state()
        self._update_stats()

    def _on_error_play(self) -> None:
        self.clean_plays = 0
        self.total_errors += 1
        self._update_clean_display()
        self._update_raise_button_state()
        self._update_stats()

    def _on_raise_tempo(self) -> None:
        if self.clean_plays < REQUIRED_CLEAN_PLAYS:
            return
        if self.mode == MODE_BPM:
            self.bpm = min(self.bpm + BPM_INCREMENT, MAX_BPM)
            self.tempo_var.set(str(self.bpm))
        else:
            self.speed = min(round(self.speed + SPEED_INCREMENT, 2), MAX_SPEED)
            self.tempo_var.set(f"{self.speed:.2f}")
        self.clean_plays = 0
        self.tempo_raises += 1
        self.tempo_history.append(
            (self._elapsed_minutes(), self.bpm, self.speed),
        )
        self._update_tempo_display()
        self._update_clean_display()
        self._update_raise_button_state()

    # ════════════════════════════════════════════════════════════════════════
    #  DISPLAY UPDATES
    # ════════════════════════════════════════════════════════════════════════

    def _update_tempo_display(self) -> None:
        if self.mode == MODE_BPM:
            self.tempo_display.configure(text=f"♩  {self.bpm} BPM")
        else:
            self.tempo_display.configure(text=f"▶  {self.speed:.2f}x speed")

    def _update_clean_display(self) -> None:
        remaining = max(0, REQUIRED_CLEAN_PLAYS - self.clean_plays)
        if remaining == 0:
            text = (
                f"Clean: {self.clean_plays}/{REQUIRED_CLEAN_PLAYS}  "
                f"✅  Tempo can be raised!"
            )
            color = C["accent"]
        else:
            dots = "●" * self.clean_plays + "○" * remaining
            text = f"Clean: {dots}  ({self.clean_plays}/{REQUIRED_CLEAN_PLAYS})"
            color = C["accent_dim"]
        self.clean_display.configure(text=text, fg=color)

    def _update_raise_button_state(self) -> None:
        state = "normal" if self.clean_plays >= REQUIRED_CLEAN_PLAYS else "disabled"
        self.raise_btn.configure(state=state)

    def _update_raise_button_text(self) -> None:
        if self.mode == MODE_BPM:
            self.raise_btn.configure(
                text=f"⬆  Raise BPM (+{BPM_INCREMENT})",
            )
        else:
            self.raise_btn.configure(
                text=f"⬆  Raise Speed (+{SPEED_INCREMENT:.2f}x)",
            )

    def _update_stats(self) -> None:
        self.stats_label.configure(
            text=(
                f"Session:  clean {self.total_clean}  |  "
                f"errors {self.total_errors}  |  "
                f"cycles: {self.completed_cycles}"
            ),
        )

    def _update_progress_bar(self) -> None:
        self.progress_canvas.update_idletasks()
        total_w = self.progress_canvas.winfo_width()
        if self.total_phase_seconds > 0:
            elapsed = self.total_phase_seconds - self.remaining_seconds
            ratio = elapsed / self.total_phase_seconds
        else:
            ratio = 0.0
        bar_w = int(total_w * ratio)
        self.progress_canvas.coords(self.progress_bar, 0, 0, bar_w, 8)
        color = C["prog_practice"] if self.is_practice else C["prog_break"]
        self.progress_canvas.itemconfigure(self.progress_bar, fill=color)

    # ════════════════════════════════════════════════════════════════════════
    #  ALWAYS ON TOP
    # ════════════════════════════════════════════════════════════════════════

    def _toggle_always_on_top(self) -> None:
        self.always_on_top = not self.always_on_top
        self.root.attributes("-topmost", self.always_on_top)
        if self.always_on_top:
            self.ontop_btn.configure(bg=C["btn_info"], fg=C["btn_info_text"])
        else:
            self.ontop_btn.configure(bg=C["btn_neut"], fg=C["btn_neut_text"])

    # ════════════════════════════════════════════════════════════════════════
    #  STATS WINDOW (delegates to stats_window module)
    # ════════════════════════════════════════════════════════════════════════

    def _show_stats_window(self) -> None:
        show_stats_window(self)
