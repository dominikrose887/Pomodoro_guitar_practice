"""
Pomodoro Guitar Practice v1.0.0
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
Gitár gyakorló alkalmazás Pomodoro időzítővel, BPM és sebesség követéssel.

20 perc gyakorlás → 10 perc szünet → ismétlés
Tempó emelés csak 3 hibátlan lejátszás után lehetséges.
Két mód: BPM (pl. 80 BPM) vagy Sebesség (pl. 0.3x Reaper-ben).

Billentyűparancsok:
  Space    – Indítás / Szünet / Folytatás
  S        – Leállítás (reset)
  N        – Átugrás (következő fázis)
  H / 1    – Hibátlan
  E / 2    – Hiba
  U / 3    – Tempó emelés
  T        – Always on top ki/be
  D        – Világos / Sötét téma váltás
"""

import tkinter as tk
from tkinter import messagebox
import winsound
import threading


# ── Konstansok ──────────────────────────────────────────────────────────────
PRACTICE_MINUTES = 20
BREAK_MINUTES = 10
REQUIRED_CLEAN_PLAYS = 3

# BPM mód
BPM_INCREMENT = 5
DEFAULT_BPM = 60
MIN_BPM = 20
MAX_BPM = 300

# Sebesség mód
SPEED_INCREMENT = 0.05
DEFAULT_SPEED = 0.30
MIN_SPEED = 0.05
MAX_SPEED = 2.00

# Mód nevek
MODE_BPM = "bpm"
MODE_SPEED = "speed"


# ── Téma rendszer ───────────────────────────────────────────────────────────
# Világos téma – paletta: #FAF9EE, #A2AF9B, #DCCFC0, #EEEEEE
THEME_LIGHT = {
    # Alapszínek
    "bg":           "#FAF9EE",
    "card":         "#EEEEEE",
    "card_alt":     "#DCCFC0",
    "border":       "#c8bca8",
    "text":         "#3a3a3a",
    "text_light":   "#5a5a5a",
    "text_muted":   "#8a8a8a",
    # Kiemelő színek
    "rose":         "#7a9a6e",
    "gold":         "#c4a040",
    "pine":         "#6a8a60",
    "iris":         "#7a8a6e",
    "love":         "#c07060",
    # Gomb pasztellek
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
    # Időzítő színek
    "timer_practice": "#6a8a60",
    "timer_break":    "#c4a040",
    "timer_paused":   "#c07060",
    # Progress bar
    "prog_bg":      "#DCCFC0",
    "prog_practice":"#A2AF9B",
    "prog_break":   "#e0cc78",
}

# Sötét téma – paletta: #537188, #CBB279, #E1D4BB, #EEEEEE
THEME_DARK = {
    # Alapszínek
    "bg":           "#2e3d4a",
    "card":         "#537188",
    "card_alt":     "#465f72",
    "border":       "#3a5060",
    "text":         "#EEEEEE",
    "text_light":   "#E1D4BB",
    "text_muted":   "#a0b0b8",
    # Kiemelő színek
    "rose":         "#CBB279",
    "gold":         "#CBB279",
    "pine":         "#E1D4BB",
    "iris":         "#d4c490",
    "love":         "#d88080",
    # Gomb pasztellek
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
    # Időzítő színek
    "timer_practice": "#E1D4BB",
    "timer_break":    "#CBB279",
    "timer_paused":   "#d88080",
    # Progress bar
    "prog_bg":      "#3a5060",
    "prog_practice":"#90b8a0",
    "prog_break":   "#CBB279",
}

# Aktív színtéma (mutálható szótár – helyben frissül témaváltáskor)
C = dict(THEME_LIGHT)

# Fontcsalád
_FONT = "Segoe UI"


class PomodoroGuitarApp:
    """Fő alkalmazás osztály."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("🎸 Pomodoro Guitar Practice")
        self.root.resizable(False, False)
        self.root.configure(bg=C["bg"])

        # ── Állapot ────────────────────────────────────────────────────────
        self.mode = MODE_BPM
        self.bpm = DEFAULT_BPM
        self.speed = DEFAULT_SPEED
        self.clean_plays = 0
        self.total_clean = 0
        self.total_errors = 0
        self.completed_cycles = 0
        self.is_practice = True
        self.timer_running = False
        self.timer_paused = False
        self.remaining_seconds = 0
        self.total_phase_seconds = 0
        self.timer_id = None
        self.always_on_top = False
        self.current_theme = "light"

        # ── GUI ────────────────────────────────────────────────────────────
        self._build_ui()
        self._update_tempo_display()
        self._update_clean_display()
        self._update_raise_button_state()
        self._bind_keys()

    # ════════════════════════════════════════════════════════════════════════
    #  SEGÉDEK – kártya-frame készítő
    # ════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _card(parent, **kw) -> tk.Frame:
        """Kártya-stílusú frame: finom szegéllyel, lekerekített érzés."""
        outer = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        inner = tk.Frame(outer, bg=kw.get("bg", C["card"]),
                         padx=kw.get("padx", 16), pady=kw.get("pady", 10))
        inner.pack(fill="both", expand=True)
        outer._inner = inner
        return outer

    # ════════════════════════════════════════════════════════════════════════
    #  GUI FELÉPÍTÉS
    # ════════════════════════════════════════════════════════════════════════

    def _build_ui(self) -> None:
        bg = C["bg"]
        card_bg = C["card"]
        sub = C["text_light"]
        muted = C["text_muted"]

        # ── Fejléc ─────────────────────────────────────────────────────────
        self.header = tk.Frame(self.root, bg=bg)
        self.header.pack(fill="x", pady=(20, 4))

        self.status_label = tk.Label(
            self.header, text="🎸 GYAKORLÁS",
            font=(_FONT, 24, "bold"), bg=bg, fg=C["rose"],
        )
        self.status_label.pack()

        # ── Időzítő kártya ────────────────────────────────────────────────
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

        # ── Időzítő gombok ────────────────────────────────────────────────
        self.btn_row = tk.Frame(self.root, bg=bg)
        self.btn_row.pack(pady=(8, 2))

        self.start_btn = tk.Button(
            self.btn_row, text="▶  Indítás  [Space]",
            font=(_FONT, 12, "bold"), width=17,
            bg=C["btn_ok"], fg=C["btn_ok_text"],
            activebackground=C["btn_ok_act"], activeforeground=C["btn_ok_text"],
            relief="flat", bd=0, cursor="hand2",
            command=self._start_or_resume_timer,
        )
        self.start_btn.grid(row=0, column=0, padx=5, pady=4)

        self.pause_btn = tk.Button(
            self.btn_row, text="⏸  Szünet  [Space]",
            font=(_FONT, 12, "bold"), width=17,
            bg=C["btn_warn"], fg=C["btn_warn_text"],
            activebackground=C["btn_warn_act"], activeforeground=C["btn_warn_text"],
            relief="flat", bd=0, cursor="hand2",
            command=self._pause_timer, state="disabled",
        )
        self.pause_btn.grid(row=0, column=1, padx=5, pady=4)

        self.stop_btn = tk.Button(
            self.btn_row, text="⏹  Reset  [S]",
            font=(_FONT, 12, "bold"), width=17,
            bg=C["btn_err"], fg=C["btn_err_text"],
            activebackground=C["btn_err_act"], activeforeground=C["btn_err_text"],
            relief="flat", bd=0, cursor="hand2",
            command=self._stop_timer, state="disabled",
        )
        self.stop_btn.grid(row=0, column=2, padx=5, pady=4)

        # Második gombsor
        self.btn_row2 = tk.Frame(self.root, bg=bg)
        self.btn_row2.pack(pady=(0, 6))

        self.skip_btn = tk.Button(
            self.btn_row2, text="⏭  Átugrás  [N]",
            font=(_FONT, 10), width=17,
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._skip_phase, state="disabled",
        )
        self.skip_btn.grid(row=0, column=0, padx=5)

        self.ontop_btn = tk.Button(
            self.btn_row2, text="📌  Mindig felül  [T]",
            font=(_FONT, 10), width=17,
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._toggle_always_on_top,
        )
        self.ontop_btn.grid(row=0, column=1, padx=5)

        self.theme_btn = tk.Button(
            self.btn_row2, text="🌙  Sötét  [D]",
            font=(_FONT, 10), width=17,
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._toggle_theme,
        )
        self.theme_btn.grid(row=0, column=2, padx=5)

        # ── Tempó szekció kártya ───────────────────────────────────────────
        self.tempo_card = self._card(self.root, bg=C["card_alt"])
        self.tempo_card.pack(fill="x", padx=28, pady=(8, 4))
        tci = self.tempo_card._inner

        # Mód választó
        self.mode_frame = tk.Frame(tci, bg=C["card_alt"])
        self.mode_frame.pack(pady=(0, 6))

        self.mode_var = tk.StringVar(value=MODE_BPM)

        self.radio_bpm = tk.Radiobutton(
            self.mode_frame, text="♩ BPM mód", variable=self.mode_var,
            value=MODE_BPM,
            font=(_FONT, 11, "bold"), bg=C["card_alt"], fg=C["iris"],
            selectcolor=C["card_alt"], activebackground=C["card_alt"],
            activeforeground=C["iris"], cursor="hand2",
            command=self._on_mode_change,
        )
        self.radio_bpm.pack(side="left", padx=(0, 24))

        self.radio_speed = tk.Radiobutton(
            self.mode_frame, text="▶ Sebesség mód (Reaper)",
            variable=self.mode_var, value=MODE_SPEED,
            font=(_FONT, 11, "bold"), bg=C["card_alt"], fg=C["iris"],
            selectcolor=C["card_alt"], activebackground=C["card_alt"],
            activeforeground=C["iris"], cursor="hand2",
            command=self._on_mode_change,
        )
        self.radio_speed.pack(side="left")

        # Tempó megjelenítő
        self.tempo_display = tk.Label(
            tci, text="", font=(_FONT, 30, "bold"),
            bg=C["card_alt"], fg=C["pine"],
        )
        self.tempo_display.pack(pady=(2, 6))

        # Beviteli sor
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
            self.input_frame, text="Beállít", font=(_FONT, 10),
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._on_tempo_entry,
        )
        self.tempo_set_btn.grid(row=0, column=2)

        # ── Játék szekció kártya ───────────────────────────────────────────
        self.play_card = self._card(self.root)
        self.play_card.pack(fill="x", padx=28, pady=(8, 4))
        pci = self.play_card._inner

        # Hibátlan számláló
        self.clean_display = tk.Label(
            pci, text="", font=(_FONT, 14), bg=card_bg, fg=C["pine"],
        )
        self.clean_display.pack(pady=(0, 8))

        # Hibátlan / Hiba gombok
        self.play_btns = tk.Frame(pci, bg=card_bg)
        self.play_btns.pack()

        self.clean_btn = tk.Button(
            self.play_btns, text="✅  Hibátlan  [H]",
            font=(_FONT, 13, "bold"), width=17,
            bg=C["btn_ok"], fg=C["btn_ok_text"],
            activebackground=C["btn_ok_act"], relief="flat", bd=0,
            cursor="hand2", command=self._on_clean_play,
        )
        self.clean_btn.grid(row=0, column=0, padx=6, pady=4)

        self.error_btn = tk.Button(
            self.play_btns, text="❌  Hiba  [E]",
            font=(_FONT, 13, "bold"), width=17,
            bg=C["btn_err"], fg=C["btn_err_text"],
            activebackground=C["btn_err_act"], relief="flat", bd=0,
            cursor="hand2", command=self._on_error_play,
        )
        self.error_btn.grid(row=0, column=1, padx=6, pady=4)

        # Tempó emelés gomb
        self.raise_btn = tk.Button(
            pci, text=f"⬆  BPM emelés (+{BPM_INCREMENT})  [U]",
            font=(_FONT, 13, "bold"), width=36,
            bg=C["btn_info"], fg=C["btn_info_text"],
            activebackground=C["btn_info_act"], relief="flat", bd=0,
            cursor="hand2", command=self._on_raise_tempo, state="disabled",
        )
        self.raise_btn.pack(pady=(8, 2))

        # ── Statisztika + súgó ─────────────────────────────────────────────
        self.footer = tk.Frame(self.root, bg=bg)
        self.footer.pack(fill="x", pady=(8, 4))

        self.stats_label = tk.Label(
            self.footer,
            text="Session: hibátlan 0  |  hiba 0  |  ciklusok: 0",
            font=(_FONT, 11), bg=bg, fg=sub,
        )
        self.stats_label.pack()

        self.hints_label = tk.Label(
            self.footer,
            text="Space: Indít/Szünet  ·  S: Reset  ·  N: Átugrás  ·  "
                 "H: Hibátlan  ·  E: Hiba  ·  U: Emelés  ·  T: Felül  ·  D: Téma",
            font=(_FONT, 8), bg=bg, fg=muted,
        )
        self.hints_label.pack(pady=(4, 10))

    # ════════════════════════════════════════════════════════════════════════
    #  TÉMA VÁLTÁS
    # ════════════════════════════════════════════════════════════════════════

    def _toggle_theme(self) -> None:
        """Világos ↔ Sötét téma váltás."""
        if self.current_theme == "light":
            self.current_theme = "dark"
            C.update(THEME_DARK)
            self.theme_btn.configure(text="☀  Világos  [D]")
        else:
            self.current_theme = "light"
            C.update(THEME_LIGHT)
            self.theme_btn.configure(text="🌙  Sötét  [D]")
        self._apply_theme()

    def _apply_theme(self) -> None:
        """Rekonfigurálja az összes widget színét az aktuális témára."""
        bg = C["bg"]
        card_bg = C["card"]
        card_alt = C["card_alt"]
        border = C["border"]
        txt = C["text"]
        sub = C["text_light"]
        muted = C["text_muted"]

        # Gyökér ablak
        self.root.configure(bg=bg)

        # ── Fejléc ─────────────────────────────────────────────────────────
        self.header.configure(bg=bg)
        if self.timer_paused:
            self.status_label.configure(bg=bg, fg=C["timer_paused"])
        elif self.is_practice:
            self.status_label.configure(bg=bg, fg=C["rose"])
        else:
            self.status_label.configure(bg=bg, fg=C["gold"])

        # ── Időzítő kártya ────────────────────────────────────────────────
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

        # ── Időzítő gombok ────────────────────────────────────────────────
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

        # ── Tempó kártya ──────────────────────────────────────────────────
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

        # ── Játék kártya ──────────────────────────────────────────────────
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

        # ── Lábléc ────────────────────────────────────────────────────────
        self.footer.configure(bg=bg)
        self.stats_label.configure(bg=bg, fg=sub)
        self.hints_label.configure(bg=bg, fg=muted)

        # Frissítjük az állapotfüggő kijelzőket
        self._update_clean_display()

    # ════════════════════════════════════════════════════════════════════════
    #  BILLENTYŰPARANCSOK
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
    #  IDŐZÍTŐ LOGIKA
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

        self.start_btn.configure(state="normal", text="▶  Folytatás  [Space]")
        self.pause_btn.configure(state="disabled")
        self.stop_btn.configure(state="normal")
        self.skip_btn.configure(state="normal")

        self.timer_label.configure(fg=C["timer_paused"])
        self.status_label.configure(text="⏸ SZÜNETELTETVE", fg=C["timer_paused"])

    def _resume_timer(self) -> None:
        if not self.timer_paused:
            return

        self.timer_paused = False
        self.timer_running = True

        if self.is_practice:
            self.status_label.configure(text="🎸 GYAKORLÁS", fg=C["rose"])
            self.timer_label.configure(fg=C["timer_practice"])
        else:
            self.status_label.configure(text="☕ SZÜNET", fg=C["gold"])
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
            self.status_label.configure(text="🎸 GYAKORLÁS", fg=C["rose"])
            self.timer_label.configure(fg=C["timer_practice"])
        else:
            self.status_label.configure(text="☕ SZÜNET", fg=C["gold"])
            self.timer_label.configure(fg=C["timer_break"])

        self.start_btn.configure(state="normal", text="▶  Indítás  [Space]")
        self.pause_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        self.skip_btn.configure(state="disabled")
        self._update_progress_bar()

    def _set_timer_buttons_running(self) -> None:
        self.start_btn.configure(state="disabled", text="▶  Indítás  [Space]")
        self.pause_btn.configure(state="normal")
        self.stop_btn.configure(state="normal")
        self.skip_btn.configure(state="normal")

    def _tick(self) -> None:
        if not self.timer_running:
            return

        mins, secs = divmod(self.remaining_seconds, 60)
        self.timer_label.configure(text=f"{mins:02d}:{secs:02d}")
        self._update_progress_bar()

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
            self.status_label.configure(text="☕ SZÜNET", fg=C["gold"])
            self.timer_label.configure(
                text=f"{BREAK_MINUTES:02d}:00", fg=C["timer_break"],
            )
            self._play_sound()
            self._update_stats()
            messagebox.showinfo(
                "Szünet!",
                f"🎉 Lejárt a {PRACTICE_MINUTES} perc gyakorlás!\n"
                f"Pihenj {BREAK_MINUTES} percet.\n\n"
                f"Befejezett ciklusok: {self.completed_cycles}",
            )
        else:
            self.is_practice = True
            self.status_label.configure(text="🎸 GYAKORLÁS", fg=C["rose"])
            self.timer_label.configure(
                text=f"{PRACTICE_MINUTES:02d}:00", fg=C["timer_practice"],
            )
            self._play_sound()
            messagebox.showinfo(
                "Gyakorlás!",
                f"⏰ Lejárt a {BREAK_MINUTES} perc szünet!\n"
                "Ideje újra gyakorolni! 🎸",
            )

        self.start_btn.configure(state="normal", text="▶  Indítás  [Space]")
        self.pause_btn.configure(state="disabled")
        self.stop_btn.configure(state="disabled")
        self.skip_btn.configure(state="disabled")
        self._update_progress_bar()

    def _skip_phase(self) -> None:
        self._stop_timer()
        self.remaining_seconds = 0
        self._phase_ended()

    # ════════════════════════════════════════════════════════════════════════
    #  MÓD VÁLTÁS
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
    #  TEMPÓ ÉS JÁTÉK LOGIKA
    # ════════════════════════════════════════════════════════════════════════

    def _on_tempo_entry(self, _event=None) -> None:
        raw = self.tempo_var.get().strip()

        if self.mode == MODE_BPM:
            try:
                val = int(raw)
            except ValueError:
                messagebox.showwarning("Hiba", "Kérlek egész számot adj meg a BPM-hez!")
                self.tempo_var.set(str(self.bpm))
                return

            if val < MIN_BPM or val > MAX_BPM:
                messagebox.showwarning(
                    "Hiba", f"BPM {MIN_BPM} és {MAX_BPM} között legyen!"
                )
                self.tempo_var.set(str(self.bpm))
                return
            self.bpm = val
        else:
            try:
                val = float(raw)
            except ValueError:
                messagebox.showwarning("Hiba", "Kérlek számot adj meg (pl. 0.30)!")
                self.tempo_var.set(f"{self.speed:.2f}")
                return

            if val < MIN_SPEED or val > MAX_SPEED:
                messagebox.showwarning(
                    "Hiba",
                    f"Sebesség {MIN_SPEED:.2f}x és {MAX_SPEED:.2f}x között legyen!",
                )
                self.tempo_var.set(f"{self.speed:.2f}")
                return
            self.speed = round(val, 2)

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
        self._update_tempo_display()
        self._update_clean_display()
        self._update_raise_button_state()

    # ════════════════════════════════════════════════════════════════════════
    #  KIJELZŐ FRISSÍTÉSEK
    # ════════════════════════════════════════════════════════════════════════

    def _update_tempo_display(self) -> None:
        if self.mode == MODE_BPM:
            self.tempo_display.configure(text=f"♩ {self.bpm} BPM")
        else:
            self.tempo_display.configure(text=f"▶ {self.speed:.2f}x sebesség")

    def _update_clean_display(self) -> None:
        label = "Tempó" if self.mode == MODE_BPM else "Sebesség"
        remaining = max(0, REQUIRED_CLEAN_PLAYS - self.clean_plays)
        if remaining == 0:
            text = f"Hibátlan: {self.clean_plays} / {REQUIRED_CLEAN_PLAYS}  ✅  {label} emelhető!"
            color = C["pine"]
        else:
            dots = "●" * self.clean_plays + "○" * remaining
            text = f"Hibátlan: {dots}  ({self.clean_plays}/{REQUIRED_CLEAN_PLAYS})"
            color = C["iris"]
        self.clean_display.configure(text=text, fg=color)

    def _update_raise_button_state(self) -> None:
        if self.clean_plays >= REQUIRED_CLEAN_PLAYS:
            self.raise_btn.configure(state="normal")
        else:
            self.raise_btn.configure(state="disabled")

    def _update_raise_button_text(self) -> None:
        if self.mode == MODE_BPM:
            self.raise_btn.configure(text=f"⬆  BPM emelés (+{BPM_INCREMENT})  [U]")
        else:
            self.raise_btn.configure(
                text=f"⬆  Sebesség emelés (+{SPEED_INCREMENT:.2f}x)  [U]"
            )

    def _update_stats(self) -> None:
        self.stats_label.configure(
            text=(
                f"Session: hibátlan {self.total_clean}  |  "
                f"hiba {self.total_errors}  |  "
                f"ciklusok: {self.completed_cycles}"
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
    #  HANG
    # ════════════════════════════════════════════════════════════════════════

    @staticmethod
    def _play_sound() -> None:
        def _beep():
            try:
                for freq in (523, 659, 784):
                    winsound.Beep(freq, 200)
            except Exception:
                pass
        threading.Thread(target=_beep, daemon=True).start()


# ── Indítás ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    root.geometry("680x780")
    app = PomodoroGuitarApp(root)
    root.mainloop()
