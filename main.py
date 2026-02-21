"""
Pomodoro Guitar Practice v1.2.1
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Guitar practice app with Pomodoro timer, BPM and speed tracking.

20 min practice → 10 min break → repeat
Tempo raise only after 3 consecutive clean plays.
Two modes: BPM (e.g. 80 BPM) or Speed (e.g. 0.3x).
"""

import tkinter as tk
from source.app import PomodoroGuitarApp


def main() -> None:
    root = tk.Tk()
    root.geometry("700x750")
    PomodoroGuitarApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
