"""
Pomodoro Guitar Practice v1.2.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Guitar practice app with Pomodoro timer, BPM and speed tracking.

20 min practice → 10 min break → repeat
Tempo raise only after 3 consecutive clean plays.
Two modes: BPM (e.g. 80 BPM) or Speed (e.g. 0.3x).
"""

import ctypes
import sys
import tkinter as tk
from source.app import PomodoroGuitarApp

APP_ID = "dominikrose.pomodoro.guitar.practice"


def main() -> None:
    # Set AppUserModelID BEFORE creating any window so Windows
    # associates the correct icon with the taskbar entry.
    # Only needed when running via python.exe (development).
    # For a frozen .exe, Windows auto-derives the ID from the exe path,
    # which already matches the pinned taskbar shortcut.
    if sys.platform == "win32" and not getattr(sys, "frozen", False):
        try:
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except Exception:
            pass

    root = tk.Tk()
    root.geometry("700x750")
    PomodoroGuitarApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
