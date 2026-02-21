"""
Sound helper functions.

All sound playback is non-blocking (runs in a daemon thread).
Uses res/beep.wav via winsound.PlaySound.
"""

import threading
import time
import winsound

from source.constants import BEEP_WAV


def _play_in_thread(fn) -> None:
    threading.Thread(target=fn, daemon=True).start()


def beep_once() -> None:
    """Single beep."""
    def _play():
        try:
            winsound.PlaySound(BEEP_WAV, winsound.SND_FILENAME)
        except Exception:
            pass
    _play_in_thread(_play)


def play_phase_end() -> None:
    """Three beeps – phase transition."""
    def _play():
        try:
            for _ in range(3):
                winsound.PlaySound(BEEP_WAV, winsound.SND_FILENAME)
                time.sleep(0.08)
        except Exception:
            pass
    _play_in_thread(_play)


def play_warning() -> None:
    """Two beeps – 30-second warning."""
    def _play():
        try:
            winsound.PlaySound(BEEP_WAV, winsound.SND_FILENAME)
            time.sleep(0.15)
            winsound.PlaySound(BEEP_WAV, winsound.SND_FILENAME)
        except Exception:
            pass
    _play_in_thread(_play)


def play_imminent() -> None:
    """Three quick beeps – 10-second warning."""
    def _play():
        try:
            for _ in range(3):
                winsound.PlaySound(BEEP_WAV, winsound.SND_FILENAME)
                time.sleep(0.08)
        except Exception:
            pass
    _play_in_thread(_play)
