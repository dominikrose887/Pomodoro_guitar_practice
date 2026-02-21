"""
Timer mixin – start / pause / resume / stop / tick / phase-end / skip.
"""

from __future__ import annotations

from tkinter import messagebox

from source.constants import (
    PRACTICE_MINUTES, BREAK_MINUTES,
    ALERT_30S, ALERT_10S,
)
from source.themes import C
from source import sounds


class TimerMixin:
    """Mixin that provides all Pomodoro timer methods."""

    def _start_or_resume_timer(self) -> None:
        if self.timer_paused:
            self._resume_timer()
            return
        if self.timer_running:
            return

        minutes = PRACTICE_MINUTES if self.is_practice else BREAK_MINUTES
        self.remaining_seconds = minutes * 60
        self.total_phase_seconds = self.remaining_seconds
        self.timer_running = True
        self.timer_paused = False
        self._alerted_30s = False
        self._alerted_10s = False

        self._set_timer_buttons_running()
        self._tick()

    def _pause_timer(self) -> None:
        if not self.timer_running or self.timer_paused:
            return
        self.timer_paused = True
        self.timer_running = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        self.start_btn.configure(state="normal", text="▶  Resume")
        self.pause_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.skip_btn.configure(state="normal")
        self.timer_label.configure(fg=C["timer_paused"])
        self.status_label.configure(text="⏸  PAUSED", fg=C["timer_paused"])

    def _resume_timer(self) -> None:
        if not self.timer_paused:
            return
        self.timer_paused = False
        self.timer_running = True
        if self.is_practice:
            self.status_label.configure(text="🎸  PRACTICE", fg=C["accent"])
            self.timer_label.configure(fg=C["timer_practice"])
        else:
            self.status_label.configure(text="☕  BREAK", fg=C["accent_sec"])
            self.timer_label.configure(fg=C["timer_break"])
        self._set_timer_buttons_running()
        self._tick()

    def _stop_timer(self) -> None:
        self.timer_running = False
        self.timer_paused = False
        if self.timer_id is not None:
            self.root.after_cancel(self.timer_id)
            self.timer_id = None

        minutes = PRACTICE_MINUTES if self.is_practice else BREAK_MINUTES
        self.remaining_seconds = 0
        self.total_phase_seconds = 0
        self.timer_label.configure(text=f"{minutes:02d}:00")

        if self.is_practice:
            self.status_label.configure(text="🎸  PRACTICE", fg=C["accent"])
            self.timer_label.configure(fg=C["timer_practice"])
        else:
            self.status_label.configure(text="☕  BREAK", fg=C["accent_sec"])
            self.timer_label.configure(fg=C["timer_break"])

        self.start_btn.configure(state="normal", text="▶  Start")
        self.pause_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        self.skip_btn.configure(state="disabled")
        self._update_progress_bar()

    def _set_timer_buttons_running(self) -> None:
        self.start_btn.configure(state="disabled", text="▶  Start")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        self.skip_btn.configure(state="normal")

    def _tick(self) -> None:
        if not self.timer_running:
            return

        mins, secs = divmod(self.remaining_seconds, 60)
        self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
        self._update_progress_bar()

        if self.is_practice:
            self.total_practice_seconds += 1
        else:
            self.total_break_seconds += 1

        if self.remaining_seconds == ALERT_30S and not self._alerted_30s:
            self._alerted_30s = True
            sounds.play_warning()
        if self.remaining_seconds == ALERT_10S and not self._alerted_10s:
            self._alerted_10s = True
            sounds.play_imminent()

        if self.remaining_seconds <= 0:
            self._phase_ended()
            return

        self.remaining_seconds -= 1
        self.timer_id = self.root.after(1000, self._tick)

    def _phase_ended(self) -> None:
        self.timer_running = False
        self.timer_paused = False
        self.timer_id = None

        if self.is_practice:
            self.is_practice = False
            self.completed_cycles += 1
            self.status_label.configure(text="☕  BREAK", fg=C["accent_sec"])
            self.timer_label.configure(
                text=f"{BREAK_MINUTES:02d}:00", fg=C["timer_break"],
            )
            sounds.play_phase_end()
            self._update_stats()
            messagebox.showinfo(
                "Break Time!",
                f"🎉 {PRACTICE_MINUTES} minutes of practice completed!\n"
                f"Rest for {BREAK_MINUTES} minutes.\n\n"
                f"Completed cycles: {self.completed_cycles}",
            )
        else:
            self.is_practice = True
            self.status_label.configure(text="🎸  PRACTICE", fg=C["accent"])
            self.timer_label.configure(
                text=f"{PRACTICE_MINUTES:02d}:00", fg=C["timer_practice"],
            )
            sounds.play_phase_end()
            messagebox.showinfo(
                "Practice Time!",
                f"⏰ {BREAK_MINUTES} minute break is over!\n"
                "Time to practice again! 🎸",
            )

        self.start_btn.configure(state="normal", text="▶  Start")
        self.pause_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        self.skip_btn.configure(state="disabled")
        self._update_progress_bar()

    def _skip_phase(self) -> None:
        self._stop_timer()
        self.remaining_seconds = 0
        self._phase_ended()
