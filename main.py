"""
Pomodoro Guitar Practice v1.1.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Guitar practice app with Pomodoro timer, BPM and speed tracking.

20 min practice → 10 min break → repeat
Tempo raise only after 3 consecutive clean plays.
Two modes: BPM (e.g. 80 BPM) or Speed (e.g. 0.3x in Reaper).
"""

import tkinter as tk
from tkinter import messagebox
import winsound
import threading
import time
import os

# Path to the beep sound file (relative to this script)
_BEEP_WAV = os.path.join(os.path.dirname(os.path.abspath(__file__)), "res", "beep.wav")


# ── Constants ───────────────────────────────────────────────────────────────
VERSION = "1.1.0"
DEVELOPER = "DominikRose"

PRACTICE_MINUTES = 20
BREAK_MINUTES = 10
REQUIRED_CLEAN_PLAYS = 3

# BPM mode
BPM_INCREMENT = 5
DEFAULT_BPM = 60
MIN_BPM = 20
MAX_BPM = 300

# Speed mode
SPEED_INCREMENT = 0.05
DEFAULT_SPEED = 0.30
MIN_SPEED = 0.05
MAX_SPEED = 2.00

# Mode names
MODE_BPM = "bpm"
MODE_SPEED = "speed"

# Sound alert thresholds (seconds before phase end)
ALERT_30S = 30
ALERT_10S = 10


# ── Theme System ───────────────────────────────────────────────────────────
# Light theme – palette: #FAF9EE, #A2AF9B, #DCCFC0, #EEEEEE
THEME_LIGHT = {
    # Base colours
    "bg":           "#FAF9EE",
    "card":         "#EEEEEE",
    "card_alt":     "#DCCFC0",
    "border":       "#c8bca8",
    "text":         "#3a3a3a",
    "text_light":   "#5a5a5a",
    "text_muted":   "#8a8a8a",
    # Accent colours
    "rose":         "#7a9a6e",
    "gold":         "#c4a040",
    "pine":         "#6a8a60",
    "iris":         "#7a8a6e",
    "love":         "#c07060",
    # Button pastels
    "btn_ok":       "#A2AF9B",
    "btn_ok_act":   "#8e9d87",
    "btn_ok_text":  "#2d4a2d",
    "btn_err":      "#e0a0a0",
    "btn_err_act":  "#d08888",
    "btn_err_text": "#5a2020",
    "btn_warn":     "#e8d4a0",
    "btn_warn_act": "#d8c490",
    "btn_warn_text":"#5a4a20",
    "btn_info":     "#a0c0d8",
    "btn_info_act": "#88aac8",
    "btn_info_text":"#203850",
    "btn_neut":     "#DCCFC0",
    "btn_neut_act": "#ccbfb0",
    "btn_neut_text":"#4a4a4a",
    # Timer colours
    "timer_practice": "#6a8a60",
    "timer_break":    "#c4a040",
    "timer_paused":   "#c07060",
    # Progress bar
    "prog_bg":      "#DCCFC0",
    "prog_practice":"#A2AF9B",
    "prog_break":   "#e0cc78",
}

# Dark theme – palette: #537188, #CBB279, #E1D4BB, #EEEEEE
THEME_DARK = {
    # Base colours
    "bg":           "#2e3d4a",
    "card":         "#537188",
    "card_alt":     "#465f72",
    "border":       "#3a5060",
    "text":         "#EEEEEE",
    "text_light":   "#E1D4BB",
    "text_muted":   "#a0b0b8",
    # Accent colours
    "rose":         "#CBB279",
    "gold":         "#CBB279",
    "pine":         "#E1D4BB",
    "iris":         "#d4c490",
    "love":         "#d88080",
    # Button pastels
    "btn_ok":       "#6a8a6a",
    "btn_ok_act":   "#5a7a5a",
    "btn_ok_text":  "#d8f0d8",
    "btn_err":      "#8a5050",
    "btn_err_act":  "#7a4040",
    "btn_err_text": "#f0d0d0",
    "btn_warn":     "#CBB279",
    "btn_warn_act": "#b8a068",
    "btn_warn_text":"#2a2010",
    "btn_info":     "#6a8aa0",
    "btn_info_act": "#587888",
    "btn_info_text":"#EEEEEE",
    "btn_neut":     "#465f72",
    "btn_neut_act": "#3a5060",
    "btn_neut_text":"#E1D4BB",
    # Timer colours
    "timer_practice": "#E1D4BB",
    "timer_break":    "#CBB279",
    "timer_paused":   "#d88080",
    # Progress bar
    "prog_bg":      "#3a5060",
    "prog_practice":"#90b8a0",
    "prog_break":   "#CBB279",
}

# Active colour theme (mutable dict – updated in-place on theme change)
C = dict(THEME_LIGHT)

# Font family
_FONT = "Segoe UI"


class PomodoroGuitarApp:
    """Main application class."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("🎸 Pomodoro Guitar Practice")
        self.root.resizable(False, False)
        self.root.configure(bg=C["bg"])

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
        self.tempo_history = []  # [(elapsed_minutes, bpm, speed)]
        self._alerted_30s = False
        self._alerted_10s = False

        # Record initial tempo
        self.tempo_history.append((0.0, self.bpm, self.speed))

        # ── GUI ────────────────────────────────────────────────────────────
        self._build_ui()
        self._update_tempo_display()
        self._update_clean_display()
        self._update_raise_button_state()
        self._bind_keys()

    # ════════════════════════════════════════════════════════════════════════
    #  HELPERS
    # ════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _card(parent, **kw) -> tk.Frame:
        """Card-style frame with subtle border."""
        outer = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        inner = tk.Frame(outer, bg=kw.get("bg", C["card"]),
                         padx=kw.get("padx", 16), pady=kw.get("pady", 10))
        inner.pack(fill="both", expand=True)
        outer._inner = inner
        return outer

    def _elapsed_minutes(self) -> float:
        """Minutes elapsed since session start."""
        return (time.time() - self.session_start) / 60.0

    # ════════════════════════════════════════════════════════════════════════
    #  BUILD UI
    # ════════════════════════════════════════════════════════════════════════

    def _build_ui(self) -> None:
        bg = C["bg"]
        card_bg = C["card"]
        sub = C["text_light"]
        muted = C["text_muted"]

        # ── Header ─────────────────────────────────────────────────────────
        self.header = tk.Frame(self.root, bg=bg)
        self.header.pack(fill="x", pady=(20, 4))

        self.status_label = tk.Label(
            self.header, text="🎸 PRACTICE",
            font=(_FONT, 24, "bold"), bg=bg, fg=C["rose"],
        )
        self.status_label.pack()

        # ── Timer card ─────────────────────────────────────────────────────
        self.timer_card = self._card(self.root, pady=14)
        self.timer_card.pack(fill="x", padx=28, pady=(8, 4))
        tc = self.timer_card._inner

        self.timer_label = tk.Label(
            tc, text="20:00",
            font=(_FONT, 52, "bold"), bg=card_bg, fg=C["timer_practice"],
        )
        self.timer_label.pack()

        # Progress bar
        self.progress_canvas = tk.Canvas(
            tc, height=6, bg=C["prog_bg"], highlightthickness=0,
        )
        self.progress_canvas.pack(fill="x", pady=(6, 0))
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 6, fill=C["prog_practice"], outline="",
        )

        # ── Timer buttons ──────────────────────────────────────────────────
        self.btn_row = tk.Frame(self.root, bg=bg)
        self.btn_row.pack(pady=(8, 2))

        self.start_btn = tk.Button(
            self.btn_row, text="▶  Start",
            font=(_FONT, 12, "bold"), width=17,
            bg=C["btn_ok"], fg=C["btn_ok_text"],
            activebackground=C["btn_ok_act"], activeforeground=C["btn_ok_text"],
            relief="flat", bd=0, cursor="hand2",
            command=self._start_or_resume_timer,
        )
        self.start_btn.grid(row=0, column=0, padx=5, pady=4)

        self.pause_btn = tk.Button(
            self.btn_row, text="⏸  Pause",
            font=(_FONT, 12, "bold"), width=17,
            bg=C["btn_warn"], fg=C["btn_warn_text"],
            activebackground=C["btn_warn_act"], activeforeground=C["btn_warn_text"],
            relief="flat", bd=0, cursor="hand2",
            command=self._pause_timer, state="disabled",
        )
        self.pause_btn.grid(row=0, column=1, padx=5, pady=4)

        self.stop_btn = tk.Button(
            self.btn_row, text="⏹  Reset",
            font=(_FONT, 12, "bold"), width=17,
            bg=C["btn_err"], fg=C["btn_err_text"],
            activebackground=C["btn_err_act"], activeforeground=C["btn_err_text"],
            relief="flat", bd=0, cursor="hand2",
            command=self._stop_timer, state="disabled",
        )
        self.stop_btn.grid(row=0, column=2, padx=5, pady=4)

        # Second button row
        self.btn_row2 = tk.Frame(self.root, bg=bg)
        self.btn_row2.pack(pady=(0, 6))

        self.skip_btn = tk.Button(
            self.btn_row2, text="⏭  Skip",
            font=(_FONT, 10), width=13,
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._skip_phase, state="disabled",
        )
        self.skip_btn.grid(row=0, column=0, padx=4)

        self.stats_btn = tk.Button(
            self.btn_row2, text="📊  Stats",
            font=(_FONT, 10), width=13,
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._show_stats_window,
        )
        self.stats_btn.grid(row=0, column=1, padx=4)

        self.ontop_btn = tk.Button(
            self.btn_row2, text="📌  Pin",
            font=(_FONT, 10), width=13,
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._toggle_always_on_top,
        )
        self.ontop_btn.grid(row=0, column=2, padx=4)

        self.theme_btn = tk.Button(
            self.btn_row2, text="🌙  Dark",
            font=(_FONT, 10), width=13,
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._toggle_theme,
        )
        self.theme_btn.grid(row=0, column=3, padx=4)

        # ── Tempo section card ─────────────────────────────────────────────
        self.tempo_card = self._card(self.root, bg=C["card_alt"])
        self.tempo_card.pack(fill="x", padx=28, pady=(8, 4))
        tci = self.tempo_card._inner

        # Mode selector
        self.mode_frame = tk.Frame(tci, bg=C["card_alt"])
        self.mode_frame.pack(pady=(0, 6))

        self.mode_var = tk.StringVar(value=MODE_BPM)

        self.radio_bpm = tk.Radiobutton(
            self.mode_frame, text="♩ BPM Mode", variable=self.mode_var,
            value=MODE_BPM,
            font=(_FONT, 11, "bold"), bg=C["card_alt"], fg=C["iris"],
            selectcolor=C["card_alt"], activebackground=C["card_alt"],
            activeforeground=C["iris"], cursor="hand2",
            command=self._on_mode_change,
        )
        self.radio_bpm.pack(side="left", padx=(0, 24))

        self.radio_speed = tk.Radiobutton(
            self.mode_frame, text="▶ Speed Mode (Reaper)",
            variable=self.mode_var, value=MODE_SPEED,
            font=(_FONT, 11, "bold"), bg=C["card_alt"], fg=C["iris"],
            selectcolor=C["card_alt"], activebackground=C["card_alt"],
            activeforeground=C["iris"], cursor="hand2",
            command=self._on_mode_change,
        )
        self.radio_speed.pack(side="left")

        # Tempo display
        self.tempo_display = tk.Label(
            tci, text="", font=(_FONT, 30, "bold"),
            bg=C["card_alt"], fg=C["pine"],
        )
        self.tempo_display.pack(pady=(2, 6))

        # Input row
        self.input_frame = tk.Frame(tci, bg=C["card_alt"])
        self.input_frame.pack()

        self.tempo_label = tk.Label(
            self.input_frame, text="BPM:", font=(_FONT, 13),
            bg=C["card_alt"], fg=sub,
        )
        self.tempo_label.grid(row=0, column=0, padx=(0, 6))

        self.tempo_var = tk.StringVar(value=str(self.bpm))
        self.tempo_entry = tk.Entry(
            self.input_frame, textvariable=self.tempo_var,
            font=(_FONT, 14), width=8, justify="center",
            bg=C["card"], fg=C["text"], insertbackground=C["text"],
            relief="flat", bd=4,
        )
        self.tempo_entry.grid(row=0, column=1, padx=(0, 6))
        self.tempo_entry.bind("<Return>", self._on_tempo_entry)

        self.tempo_set_btn = tk.Button(
            self.input_frame, text="Set", font=(_FONT, 10),
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._on_tempo_entry,
        )
        self.tempo_set_btn.grid(row=0, column=2)

        # ── Play section card ──────────────────────────────────────────────
        self.play_card = self._card(self.root)
        self.play_card.pack(fill="x", padx=28, pady=(8, 4))
        pci = self.play_card._inner

        # Clean plays counter
        self.clean_display = tk.Label(
            pci, text="", font=(_FONT, 14), bg=card_bg, fg=C["pine"],
        )
        self.clean_display.pack(pady=(0, 8))

        # Clean / Error buttons
        self.play_btns = tk.Frame(pci, bg=card_bg)
        self.play_btns.pack()

        self.clean_btn = tk.Button(
            self.play_btns, text="✅  Clean",
            font=(_FONT, 13, "bold"), width=17,
            bg=C["btn_ok"], fg=C["btn_ok_text"],
            activebackground=C["btn_ok_act"], relief="flat", bd=0,
            cursor="hand2", command=self._on_clean_play,
        )
        self.clean_btn.grid(row=0, column=0, padx=6, pady=4)

        self.error_btn = tk.Button(
            self.play_btns, text="❌  Error",
            font=(_FONT, 13, "bold"), width=17,
            bg=C["btn_err"], fg=C["btn_err_text"],
            activebackground=C["btn_err_act"], relief="flat", bd=0,
            cursor="hand2", command=self._on_error_play,
        )
        self.error_btn.grid(row=0, column=1, padx=6, pady=4)

        # Tempo raise button
        self.raise_btn = tk.Button(
            pci, text=f"⬆  Raise BPM (+{BPM_INCREMENT})",
            font=(_FONT, 13, "bold"), width=36,
            bg=C["btn_info"], fg=C["btn_info_text"],
            activebackground=C["btn_info_act"], relief="flat", bd=0,
            cursor="hand2", command=self._on_raise_tempo, state="disabled",
        )
        self.raise_btn.pack(pady=(8, 2))

        # ── Footer ─────────────────────────────────────────────────────────
        self.footer = tk.Frame(self.root, bg=bg)
        self.footer.pack(fill="x", pady=(8, 0))

        # Session stats line
        self.stats_label = tk.Label(
            self.footer,
            text="Session:  clean 0  |  errors 0  |  cycles: 0",
            font=(_FONT, 11), bg=bg, fg=sub,
        )
        self.stats_label.pack()

        # Separator
        self.footer_sep = tk.Frame(self.footer, bg=C["border"], height=1)
        self.footer_sep.pack(fill="x", padx=40, pady=(10, 6))

        # Practice tips
        tips_text = (
            "💡 How to practice effectively:\n"
            "Set a comfortable tempo → Play your lick → "
            "Mark Clean (if perfect) or Error (if not)\n"
            "After 3 consecutive clean plays you can raise the tempo. "
            "Take breaks when the timer tells you — rest helps your "
            "brain consolidate skills."
        )
        self.tips_label = tk.Label(
            self.footer, text=tips_text,
            font=(_FONT, 8), bg=bg, fg=muted,
            justify="center", wraplength=620,
        )
        self.tips_label.pack(pady=(0, 6))

        # Keyboard shortcuts
        shortcuts_text = (
            "Keyboard:  Space: Start / Pause  ·  S: Reset  ·  "
            "N: Skip  ·  H / 1: Clean  ·  E / 2: Error  ·  "
            "U / 3: Raise  ·  T: Pin  ·  D: Theme  ·  I: Stats"
        )
        self.hints_label = tk.Label(
            self.footer, text=shortcuts_text,
            font=(_FONT, 8), bg=bg, fg=muted,
        )
        self.hints_label.pack(pady=(0, 4))

        # Developer info & version
        self.version_label = tk.Label(
            self.footer,
            text=f"Developed by {DEVELOPER}  ·  v{VERSION}",
            font=(_FONT, 8), bg=bg, fg=muted,
        )
        self.version_label.pack(pady=(0, 10))

    # ════════════════════════════════════════════════════════════════════════
    #  THEME TOGGLE
    # ════════════════════════════════════════════════════════════════════════

    def _toggle_theme(self) -> None:
        """Light ↔ Dark theme toggle."""
        if self.current_theme == "light":
            self.current_theme = "dark"
            C.update(THEME_DARK)
            self.theme_btn.configure(text="☀  Light")
        else:
            self.current_theme = "light"
            C.update(THEME_LIGHT)
            self.theme_btn.configure(text="🌙  Dark")
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Reconfigure all widget colours to the active theme."""
        bg = C["bg"]
        card_bg = C["card"]
        card_alt = C["card_alt"]
        border = C["border"]
        txt = C["text"]
        sub = C["text_light"]
        muted = C["text_muted"]

        # Root window
        self.root.configure(bg=bg)

        # ── Header ─────────────────────────────────────────────────────────
        self.header.configure(bg=bg)
        if self.timer_paused:
            self.status_label.configure(bg=bg, fg=C["timer_paused"])
        elif self.is_practice:
            self.status_label.configure(bg=bg, fg=C["rose"])
        else:
            self.status_label.configure(bg=bg, fg=C["gold"])

        # ── Timer card ─────────────────────────────────────────────────────
        self.timer_card.configure(bg=border)
        self.timer_card._inner.configure(bg=card_bg)

        if self.timer_paused:
            timer_fg = C["timer_paused"]
        elif self.is_practice:
            timer_fg = C["timer_practice"]
        else:
            timer_fg = C["timer_break"]
        self.timer_label.configure(bg=card_bg, fg=timer_fg)

        self.progress_canvas.configure(bg=C["prog_bg"])
        prog_c = C["prog_practice"] if self.is_practice else C["prog_break"]
        self.progress_canvas.itemconfigure(self.progress_bar, fill=prog_c)

        # ── Timer buttons ──────────────────────────────────────────────────
        self.btn_row.configure(bg=bg)
        self.start_btn.configure(
            bg=C["btn_ok"], fg=C["btn_ok_text"],
            activebackground=C["btn_ok_act"], activeforeground=C["btn_ok_text"],
        )
        self.pause_btn.configure(
            bg=C["btn_warn"], fg=C["btn_warn_text"],
            activebackground=C["btn_warn_act"], activeforeground=C["btn_warn_text"],
        )
        self.stop_btn.configure(
            bg=C["btn_err"], fg=C["btn_err_text"],
            activebackground=C["btn_err_act"], activeforeground=C["btn_err_text"],
        )

        self.btn_row2.configure(bg=bg)
        self.skip_btn.configure(
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"],
        )
        self.stats_btn.configure(
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"],
        )
        if self.always_on_top:
            self.ontop_btn.configure(
                bg=C["btn_info"], fg=C["btn_info_text"],
                activebackground=C["btn_info_act"],
            )
        else:
            self.ontop_btn.configure(
                bg=C["btn_neut"], fg=C["btn_neut_text"],
                activebackground=C["btn_neut_act"],
            )
        self.theme_btn.configure(
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"],
        )

        # ── Tempo card ─────────────────────────────────────────────────────
        self.tempo_card.configure(bg=border)
        self.tempo_card._inner.configure(bg=card_alt)
        self.mode_frame.configure(bg=card_alt)
        self.radio_bpm.configure(
            bg=card_alt, fg=C["iris"],
            selectcolor=card_alt, activebackground=card_alt,
            activeforeground=C["iris"],
        )
        self.radio_speed.configure(
            bg=card_alt, fg=C["iris"],
            selectcolor=card_alt, activebackground=card_alt,
            activeforeground=C["iris"],
        )
        self.tempo_display.configure(bg=card_alt, fg=C["pine"])
        self.input_frame.configure(bg=card_alt)
        self.tempo_label.configure(bg=card_alt, fg=sub)
        self.tempo_entry.configure(bg=card_bg, fg=txt, insertbackground=txt)
        self.tempo_set_btn.configure(
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"],
        )

        # ── Play card ─────────────────────────────────────────────────────
        self.play_card.configure(bg=border)
        self.play_card._inner.configure(bg=card_bg)
        self.play_btns.configure(bg=card_bg)
        self.clean_btn.configure(
            bg=C["btn_ok"], fg=C["btn_ok_text"],
            activebackground=C["btn_ok_act"],
        )
        self.error_btn.configure(
            bg=C["btn_err"], fg=C["btn_err_text"],
            activebackground=C["btn_err_act"],
        )
        self.raise_btn.configure(
            bg=C["btn_info"], fg=C["btn_info_text"],
            activebackground=C["btn_info_act"],
        )

        # ── Footer ─────────────────────────────────────────────────────────
        self.footer.configure(bg=bg)
        self.stats_label.configure(bg=bg, fg=sub)
        self.footer_sep.configure(bg=border)
        self.tips_label.configure(bg=bg, fg=muted)
        self.hints_label.configure(bg=bg, fg=muted)
        self.version_label.configure(bg=bg, fg=muted)

        # Refresh state-dependent displays
        self._update_clean_display()

    # ════════════════════════════════════════════════════════════════════════
    #  KEY BINDINGS
    # ════════════════════════════════════════════════════════════════════════

    def _bind_keys(self) -> None:
        self.root.bind("<space>", self._key_space)
        self.root.bind("s", lambda e: self._stop_timer())
        self.root.bind("S", lambda e: self._stop_timer())
        self.root.bind("n", lambda e: self._skip_phase())
        self.root.bind("N", lambda e: self._skip_phase())
        self.root.bind("h", lambda e: self._on_clean_play())
        self.root.bind("H", lambda e: self._on_clean_play())
        self.root.bind("1", lambda e: self._on_clean_play())
        self.root.bind("e", lambda e: self._on_error_play())
        self.root.bind("E", lambda e: self._on_error_play())
        self.root.bind("2", lambda e: self._on_error_play())
        self.root.bind("u", lambda e: self._on_raise_tempo())
        self.root.bind("U", lambda e: self._on_raise_tempo())
        self.root.bind("3", lambda e: self._on_raise_tempo())
        self.root.bind("t", lambda e: self._toggle_always_on_top())
        self.root.bind("T", lambda e: self._toggle_always_on_top())
        self.root.bind("d", lambda e: self._toggle_theme())
        self.root.bind("D", lambda e: self._toggle_theme())
        self.root.bind("i", lambda e: self._show_stats_window())
        self.root.bind("I", lambda e: self._show_stats_window())

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
    #  TIMER LOGIC
    # ════════════════════════════════════════════════════════════════════════

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
        self.status_label.configure(text="⏸ PAUSED", fg=C["timer_paused"])

    def _resume_timer(self) -> None:
        if not self.timer_paused:
            return

        self.timer_paused = False
        self.timer_running = True

        if self.is_practice:
            self.status_label.configure(text="🎸 PRACTICE", fg=C["rose"])
            self.timer_label.configure(fg=C["timer_practice"])
        else:
            self.status_label.configure(text="☕ BREAK", fg=C["gold"])
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
            self.status_label.configure(text="🎸 PRACTICE", fg=C["rose"])
            self.timer_label.configure(fg=C["timer_practice"])
        else:
            self.status_label.configure(text="☕ BREAK", fg=C["gold"])
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

        # Track elapsed time
        if self.is_practice:
            self.total_practice_seconds += 1
        else:
            self.total_break_seconds += 1

        # Sound alerts
        if self.remaining_seconds == ALERT_30S and not self._alerted_30s:
            self._alerted_30s = True
            self._play_warning_sound()
        if self.remaining_seconds == ALERT_10S and not self._alerted_10s:
            self._alerted_10s = True
            self._play_imminent_sound()

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
            self.status_label.configure(text="☕ BREAK", fg=C["gold"])
            self.timer_label.configure(
                text=f"{BREAK_MINUTES:02d}:00", fg=C["timer_break"],
            )
            self._play_phase_end_sound()
            self._update_stats()
            messagebox.showinfo(
                "Break Time!",
                f"🎉 {PRACTICE_MINUTES} minutes of practice completed!\n"
                f"Rest for {BREAK_MINUTES} minutes.\n\n"
                f"Completed cycles: {self.completed_cycles}",
            )
        else:
            self.is_practice = True
            self.status_label.configure(text="🎸 PRACTICE", fg=C["rose"])
            self.timer_label.configure(
                text=f"{PRACTICE_MINUTES:02d}:00", fg=C["timer_practice"],
            )
            self._play_phase_end_sound()
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
                    f"Speed must be between {MIN_SPEED:.2f}x "
                    f"and {MAX_SPEED:.2f}x!",
                )
                self.tempo_var.set(f"{self.speed:.2f}")
                return
            self.speed = round(val, 2)

        # Update starting tempo if no raises yet
        if self.tempo_raises == 0:
            self.starting_bpm = self.bpm
            self.starting_speed = self.speed

        # Record manual tempo change
        self.tempo_history.append(
            (self._elapsed_minutes(), self.bpm, self.speed)
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

        # Record tempo raise in history
        self.tempo_history.append(
            (self._elapsed_minutes(), self.bpm, self.speed)
        )

        self._update_tempo_display()
        self._update_clean_display()
        self._update_raise_button_state()

    # ════════════════════════════════════════════════════════════════════════
    #  DISPLAY UPDATES
    # ════════════════════════════════════════════════════════════════════════

    def _update_tempo_display(self) -> None:
        if self.mode == MODE_BPM:
            self.tempo_display.configure(text=f"♩ {self.bpm} BPM")
        else:
            self.tempo_display.configure(text=f"▶ {self.speed:.2f}x speed")

    def _update_clean_display(self) -> None:
        remaining = max(0, REQUIRED_CLEAN_PLAYS - self.clean_plays)
        if remaining == 0:
            text = (
                f"Clean: {self.clean_plays} / {REQUIRED_CLEAN_PLAYS}  "
                f"✅  Tempo can be raised!"
            )
            color = C["pine"]
        else:
            dots = "●" * self.clean_plays + "○" * remaining
            text = f"Clean: {dots}  ({self.clean_plays}/{REQUIRED_CLEAN_PLAYS})"
            color = C["iris"]
        self.clean_display.configure(text=text, fg=color)

    def _update_raise_button_state(self) -> None:
        if self.clean_plays >= REQUIRED_CLEAN_PLAYS:
            self.raise_btn.configure(state="normal")
        else:
            self.raise_btn.configure(state="disabled")

    def _update_raise_button_text(self) -> None:
        if self.mode == MODE_BPM:
            self.raise_btn.configure(
                text=f"⬆  Raise BPM (+{BPM_INCREMENT})"
            )
        else:
            self.raise_btn.configure(
                text=f"⬆  Raise Speed (+{SPEED_INCREMENT:.2f}x)"
            )

    def _update_stats(self) -> None:
        self.stats_label.configure(
            text=(
                f"Session:  clean {self.total_clean}  |  "
                f"errors {self.total_errors}  |  "
                f"cycles: {self.completed_cycles}"
            )
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
        self.progress_canvas.coords(self.progress_bar, 0, 0, bar_w, 6)

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
    #  SOUND SYSTEM
    # ════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _beep_once() -> None:
        """Play beep.wav once (non-blocking, in a thread)."""
        def _play():
            try:
                winsound.PlaySound(_BEEP_WAV, winsound.SND_FILENAME)
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()

    @staticmethod
    def _play_phase_end_sound() -> None:
        """Three beeps for phase transitions."""
        def _play():
            try:
                for _ in range(3):
                    winsound.PlaySound(_BEEP_WAV, winsound.SND_FILENAME)
                    time.sleep(0.08)
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()

    @staticmethod
    def _play_warning_sound() -> None:
        """Two beeps – 30-second warning."""
        def _play():
            try:
                winsound.PlaySound(_BEEP_WAV, winsound.SND_FILENAME)
                time.sleep(0.15)
                winsound.PlaySound(_BEEP_WAV, winsound.SND_FILENAME)
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()

    @staticmethod
    def _play_imminent_sound() -> None:
        """Three quick beeps – 10-second warning."""
        def _play():
            try:
                for _ in range(3):
                    winsound.PlaySound(_BEEP_WAV, winsound.SND_FILENAME)
                    time.sleep(0.08)
            except Exception:
                pass
        threading.Thread(target=_play, daemon=True).start()

    # ════════════════════════════════════════════════════════════════════════
    #  STATISTICS WINDOW
    # ════════════════════════════════════════════════════════════════════════

    def _show_stats_window(self) -> None:
        """Open a themed statistics popup."""
        win = tk.Toplevel(self.root)
        win.title("📊 Session Statistics")
        win.resizable(False, False)
        win.configure(bg=C["bg"])
        win.transient(self.root)
        win.grab_set()

        bg = C["bg"]
        card_bg = C["card"]
        card_alt = C["card_alt"]
        txt = C["text"]
        sub = C["text_light"]
        muted = C["text_muted"]
        border = C["border"]

        # Title
        tk.Label(
            win, text="📊 Session Statistics",
            font=(_FONT, 18, "bold"), bg=bg, fg=C["rose"],
        ).pack(pady=(16, 8))

        # ── Overview card ──────────────────────────────────────────────────
        ov_outer = tk.Frame(win, bg=border, padx=1, pady=1)
        ov_outer.pack(fill="x", padx=20, pady=4)
        ov = tk.Frame(ov_outer, bg=card_bg, padx=16, pady=10)
        ov.pack(fill="both", expand=True)

        elapsed = time.time() - self.session_start
        eh, erem = divmod(int(elapsed), 3600)
        em, es = divmod(erem, 60)

        ph, prem = divmod(self.total_practice_seconds, 3600)
        pm, ps = divmod(prem, 60)

        bh, brem = divmod(self.total_break_seconds, 3600)
        bm, bs = divmod(brem, 60)

        overview = [
            ("Session Duration", f"{eh:02d}:{em:02d}:{es:02d}"),
            ("Practice Time", f"{ph:02d}:{pm:02d}:{ps:02d}"),
            ("Break Time", f"{bh:02d}:{bm:02d}:{bs:02d}"),
            ("Completed Cycles", str(self.completed_cycles)),
        ]

        for lbl, val in overview:
            row = tk.Frame(ov, bg=card_bg)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=lbl, font=(_FONT, 11),
                     bg=card_bg, fg=sub, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=(_FONT, 11, "bold"),
                     bg=card_bg, fg=txt, anchor="e").pack(side="right")

        # ── Performance card ───────────────────────────────────────────────
        pf_outer = tk.Frame(win, bg=border, padx=1, pady=1)
        pf_outer.pack(fill="x", padx=20, pady=4)
        pf = tk.Frame(pf_outer, bg=card_alt, padx=16, pady=10)
        pf.pack(fill="both", expand=True)

        total_plays = self.total_clean + self.total_errors
        rate = (self.total_clean / total_plays * 100) if total_plays > 0 else 0

        if self.mode == MODE_BPM:
            cur_t = f"{self.bpm} BPM"
            start_t = f"{self.starting_bpm} BPM"
            prog = self.bpm - self.starting_bpm
            prog_t = f"+{prog} BPM" if prog >= 0 else f"{prog} BPM"
        else:
            cur_t = f"{self.speed:.2f}x"
            start_t = f"{self.starting_speed:.2f}x"
            prog = self.speed - self.starting_speed
            prog_t = f"+{prog:.2f}x" if prog >= 0 else f"{prog:.2f}x"

        perf = [
            ("Clean Plays", str(self.total_clean)),
            ("Errors", str(self.total_errors)),
            ("Success Rate", f"{rate:.1f}%"),
            ("Tempo Raises", str(self.tempo_raises)),
            ("Starting Tempo", start_t),
            ("Current Tempo", cur_t),
            ("Progress", prog_t),
        ]

        for lbl, val in perf:
            row = tk.Frame(pf, bg=card_alt)
            row.pack(fill="x", pady=2)
            tk.Label(row, text=lbl, font=(_FONT, 11),
                     bg=card_alt, fg=sub, anchor="w").pack(side="left")
            tk.Label(row, text=val, font=(_FONT, 11, "bold"),
                     bg=card_alt, fg=txt, anchor="e").pack(side="right")

        # ── Bar chart: Clean vs Errors ─────────────────────────────────────
        bc_outer = tk.Frame(win, bg=border, padx=1, pady=1)
        bc_outer.pack(fill="x", padx=20, pady=4)
        bc = tk.Frame(bc_outer, bg=card_bg, padx=16, pady=10)
        bc.pack(fill="both", expand=True)

        tk.Label(bc, text="Clean vs Errors", font=(_FONT, 12, "bold"),
                 bg=card_bg, fg=txt).pack(pady=(0, 4))

        chart_h = 120
        chart_w = 240
        chart = tk.Canvas(bc, width=chart_w, height=chart_h,
                          bg=card_bg, highlightthickness=0)
        chart.pack()

        max_val = max(self.total_clean, self.total_errors, 1)
        bar_w = 60
        gap = 30

        # Clean bar
        clean_h = max(int((self.total_clean / max_val) * (chart_h - 35)), 2)
        x1 = (chart_w // 2) - bar_w - (gap // 2)
        chart.create_rectangle(
            x1, chart_h - clean_h - 20, x1 + bar_w, chart_h - 20,
            fill=C["btn_ok"], outline="",
        )
        chart.create_text(
            x1 + bar_w // 2, chart_h - clean_h - 26,
            text=str(self.total_clean),
            font=(_FONT, 10, "bold"), fill=txt,
        )
        chart.create_text(
            x1 + bar_w // 2, chart_h - 8,
            text="Clean", font=(_FONT, 9), fill=sub,
        )

        # Error bar
        error_h = max(int((self.total_errors / max_val) * (chart_h - 35)), 2)
        x2 = (chart_w // 2) + (gap // 2)
        chart.create_rectangle(
            x2, chart_h - error_h - 20, x2 + bar_w, chart_h - 20,
            fill=C["btn_err"], outline="",
        )
        chart.create_text(
            x2 + bar_w // 2, chart_h - error_h - 26,
            text=str(self.total_errors),
            font=(_FONT, 10, "bold"), fill=txt,
        )
        chart.create_text(
            x2 + bar_w // 2, chart_h - 8,
            text="Errors", font=(_FONT, 9), fill=sub,
        )

        # ── Tempo progression line chart ───────────────────────────────────
        if len(self.tempo_history) > 1:
            tp_outer = tk.Frame(win, bg=border, padx=1, pady=1)
            tp_outer.pack(fill="x", padx=20, pady=4)
            tp = tk.Frame(tp_outer, bg=card_alt, padx=16, pady=10)
            tp.pack(fill="both", expand=True)

            tk.Label(tp, text="Tempo Progression",
                     font=(_FONT, 12, "bold"),
                     bg=card_alt, fg=txt).pack(pady=(0, 4))

            tc_w = 420
            tc_h = 100
            tc = tk.Canvas(tp, width=tc_w, height=tc_h,
                           bg=card_alt, highlightthickness=0)
            tc.pack()

            # Extract values for the active mode
            if self.mode == MODE_BPM:
                values = [(t, bpm) for t, bpm, _ in self.tempo_history]
            else:
                values = [(t, spd) for t, _, spd in self.tempo_history]

            min_t = values[0][0]
            max_t = max(values[-1][0], min_t + 0.1)
            vals_only = [v for _, v in values]
            min_v = min(vals_only)
            max_v = max(vals_only)
            if min_v == max_v:
                min_v -= 1
                max_v += 1

            pad = 20

            def tx(t):
                return pad + (t - min_t) / (max_t - min_t) * (tc_w - 2 * pad)

            def ty(v):
                return (tc_h - pad) - (v - min_v) / (max_v - min_v) * (tc_h - 2 * pad)

            # Draw connecting line
            points = []
            for t, v in values:
                points.extend([tx(t), ty(v)])

            if len(points) >= 4:
                tc.create_line(
                    points, fill=C["rose"], width=2, smooth=False,
                )

            # Draw data points
            for t, v in values:
                cx, cy = tx(t), ty(v)
                r = 4
                tc.create_oval(
                    cx - r, cy - r, cx + r, cy + r,
                    fill=C["pine"], outline="",
                )

            # Y-axis labels
            if self.mode == MODE_BPM:
                hi_lbl = f"{max_v:.0f}"
                lo_lbl = f"{min_v:.0f}"
            else:
                hi_lbl = f"{max_v:.2f}x"
                lo_lbl = f"{min_v:.2f}x"

            tc.create_text(
                pad - 4, pad, text=hi_lbl,
                font=(_FONT, 7), fill=muted, anchor="e",
            )
            tc.create_text(
                pad - 4, tc_h - pad, text=lo_lbl,
                font=(_FONT, 7), fill=muted, anchor="e",
            )

        # Close button
        tk.Button(
            win, text="Close", font=(_FONT, 11, "bold"),
            width=12, bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=win.destroy,
        ).pack(pady=(8, 16))

        # Centre on parent
        win.update_idletasks()
        pw = self.root.winfo_x()
        ph_y = self.root.winfo_y()
        px = self.root.winfo_width()
        ww = win.winfo_width()
        wh = win.winfo_height()
        win.geometry(f"+{pw + (px - ww) // 2}+{ph_y + 40}")
        win.focus_set()


# ── Launch ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("700x900")
    app = PomodoroGuitarApp(root)
    root.mainloop()
