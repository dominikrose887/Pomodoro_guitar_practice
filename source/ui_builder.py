"""
UI builder mixin – creates all widgets for the main window.
"""

from __future__ import annotations

import tkinter as tk

from source.constants import (
    VERSION, DEVELOPER, FONT_FAMILY as _FONT,
    BPM_INCREMENT, MODE_BPM, MODE_SPEED,
)
from source.themes import C


class UIBuilderMixin:
    """Mixin that provides ``_build_ui`` and the ``_card`` helper."""

    # ── Card helper ────────────────────────────────────────────────────────

    @staticmethod
    def _card(parent: tk.Widget, **kw) -> tk.Frame:
        """Card-style frame with a subtle 1-px border."""
        outer = tk.Frame(parent, bg=C["border"], padx=1, pady=1)
        inner = tk.Frame(
            outer,
            bg=kw.get("bg", C["card"]),
            padx=kw.get("padx", 18),
            pady=kw.get("pady", 12),
        )
        inner.pack(fill="both", expand=True)
        outer._inner = inner  # type: ignore[attr-defined]
        return outer

    # ── Build the full UI ──────────────────────────────────────────────────

    def _build_ui(self) -> None:  # noqa: C901 (complexity unavoidable)
        bg = C["bg"]
        card_bg = C["card"]
        sub = C["text_light"]
        muted = C["text_muted"]

        # ── Header ─────────────────────────────────────────────────────────
        self.header = tk.Frame(self.root, bg=bg)
        self.header.pack(fill="x", pady=(18, 2))

        self.status_label = tk.Label(
            self.header, text="🎸  PRACTICE",
            font=(_FONT, 22, "bold"), bg=bg, fg=C["accent"],
        )
        self.status_label.pack()

        # ── Timer card ─────────────────────────────────────────────────────
        self.timer_card = self._card(self.root, pady=16)
        self.timer_card.pack(fill="x", padx=30, pady=(8, 4))
        tc = self.timer_card._inner  # type: ignore[attr-defined]

        self.timer_label = tk.Label(
            tc, text="20:00",
            font=(_FONT, 50, "bold"), bg=card_bg, fg=C["timer_practice"],
        )
        self.timer_label.pack()

        self.progress_canvas = tk.Canvas(
            tc, height=8, bg=C["prog_bg"], highlightthickness=0,
        )
        self.progress_canvas.pack(fill="x", pady=(8, 0))
        self.progress_bar = self.progress_canvas.create_rectangle(
            0, 0, 0, 8, fill=C["prog_practice"], outline="",
        )

        # ── Timer buttons ──────────────────────────────────────────────────
        self.btn_row = tk.Frame(self.root, bg=bg)
        self.btn_row.pack(pady=(8, 2))

        self.start_btn = tk.Button(
            self.btn_row, text="▶  Start",
            font=(_FONT, 11, "bold"), width=16,
            bg=C["btn_ok"], fg=C["btn_ok_text"],
            activebackground=C["btn_ok_act"], activeforeground=C["btn_ok_text"],
            relief="flat", bd=0, cursor="hand2",
            command=self._start_or_resume_timer,
        )
        self.start_btn.grid(row=0, column=0, padx=4, pady=3)

        self.pause_btn = tk.Button(
            self.btn_row, text="⏸  Pause",
            font=(_FONT, 11, "bold"), width=16,
            bg=C["btn_warn"], fg=C["btn_warn_text"],
            activebackground=C["btn_warn_act"], activeforeground=C["btn_warn_text"],
            relief="flat", bd=0, cursor="hand2",
            command=self._pause_timer, state="disabled",
        )
        self.pause_btn.grid(row=0, column=1, padx=4, pady=3)

        self.stop_btn = tk.Button(
            self.btn_row, text="⏹  Reset",
            font=(_FONT, 11, "bold"), width=16,
            bg=C["btn_err"], fg=C["btn_err_text"],
            activebackground=C["btn_err_act"], activeforeground=C["btn_err_text"],
            relief="flat", bd=0, cursor="hand2",
            command=self._stop_timer, state="disabled",
        )
        self.stop_btn.grid(row=0, column=2, padx=4, pady=3)

        # Second button row
        self.btn_row2 = tk.Frame(self.root, bg=bg)
        self.btn_row2.pack(pady=(0, 4))

        self.skip_btn = tk.Button(
            self.btn_row2, text="⏭  Skip",
            font=(_FONT, 9), width=12,
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._skip_phase, state="disabled",
        )
        self.skip_btn.grid(row=0, column=0, padx=3)

        self.stats_btn = tk.Button(
            self.btn_row2, text="📊  Stats",
            font=(_FONT, 9), width=12,
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._show_stats_window,
        )
        self.stats_btn.grid(row=0, column=1, padx=3)

        self.ontop_btn = tk.Button(
            self.btn_row2, text="📌  Pin",
            font=(_FONT, 9), width=12,
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._toggle_always_on_top,
        )
        self.ontop_btn.grid(row=0, column=2, padx=3)

        self.theme_btn = tk.Button(
            self.btn_row2, text="🌙  Dark",
            font=(_FONT, 9), width=12,
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"], relief="flat", bd=0,
            cursor="hand2", command=self._toggle_theme,
        )
        self.theme_btn.grid(row=0, column=3, padx=3)

        # ── Tempo section card ─────────────────────────────────────────────
        self.tempo_card = self._card(self.root, bg=C["card_alt"])
        self.tempo_card.pack(fill="x", padx=30, pady=(6, 4))
        tci = self.tempo_card._inner  # type: ignore[attr-defined]

        self.mode_frame = tk.Frame(tci, bg=C["card_alt"])
        self.mode_frame.pack(pady=(0, 4))

        self.mode_var = tk.StringVar(value=MODE_BPM)

        self.radio_bpm = tk.Radiobutton(
            self.mode_frame, text="♩  BPM Mode", variable=self.mode_var,
            value=MODE_BPM,
            font=(_FONT, 11, "bold"), bg=C["card_alt"], fg=C["accent_dim"],
            selectcolor=C["card_alt"], activebackground=C["card_alt"],
            activeforeground=C["accent_dim"], cursor="hand2",
            command=self._on_mode_change,
        )
        self.radio_bpm.pack(side="left", padx=(0, 20))

        self.radio_speed = tk.Radiobutton(
            self.mode_frame, text="▶  Speed Mode (Reaper)",
            variable=self.mode_var, value=MODE_SPEED,
            font=(_FONT, 11, "bold"), bg=C["card_alt"], fg=C["accent_dim"],
            selectcolor=C["card_alt"], activebackground=C["card_alt"],
            activeforeground=C["accent_dim"], cursor="hand2",
            command=self._on_mode_change,
        )
        self.radio_speed.pack(side="left")

        self.tempo_display = tk.Label(
            tci, text="", font=(_FONT, 28, "bold"),
            bg=C["card_alt"], fg=C["accent_soft"],
        )
        self.tempo_display.pack(pady=(2, 6))

        # Input row
        self.input_frame = tk.Frame(tci, bg=C["card_alt"])
        self.input_frame.pack()

        self.tempo_label = tk.Label(
            self.input_frame, text="BPM:", font=(_FONT, 12),
            bg=C["card_alt"], fg=sub,
        )
        self.tempo_label.grid(row=0, column=0, padx=(0, 6))

        self.tempo_var = tk.StringVar(value=str(self.bpm))
        self.tempo_entry = tk.Entry(
            self.input_frame, textvariable=self.tempo_var,
            font=(_FONT, 13), width=8, justify="center",
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
        self.play_card.pack(fill="x", padx=30, pady=(6, 4))
        pci = self.play_card._inner  # type: ignore[attr-defined]

        self.clean_display = tk.Label(
            pci, text="", font=(_FONT, 13), bg=card_bg, fg=C["accent_soft"],
        )
        self.clean_display.pack(pady=(0, 6))

        self.play_btns = tk.Frame(pci, bg=card_bg)
        self.play_btns.pack()

        self.clean_btn = tk.Button(
            self.play_btns, text="✅  Clean",
            font=(_FONT, 12, "bold"), width=16,
            bg=C["btn_ok"], fg=C["btn_ok_text"],
            activebackground=C["btn_ok_act"], relief="flat", bd=0,
            cursor="hand2", command=self._on_clean_play,
        )
        self.clean_btn.grid(row=0, column=0, padx=5, pady=3)

        self.error_btn = tk.Button(
            self.play_btns, text="❌  Error",
            font=(_FONT, 12, "bold"), width=16,
            bg=C["btn_err"], fg=C["btn_err_text"],
            activebackground=C["btn_err_act"], relief="flat", bd=0,
            cursor="hand2", command=self._on_error_play,
        )
        self.error_btn.grid(row=0, column=1, padx=5, pady=3)

        self.raise_btn = tk.Button(
            pci, text=f"⬆  Raise BPM (+{BPM_INCREMENT})",
            font=(_FONT, 12, "bold"), width=34,
            bg=C["btn_info"], fg=C["btn_info_text"],
            activebackground=C["btn_info_act"], relief="flat", bd=0,
            cursor="hand2", command=self._on_raise_tempo, state="disabled",
        )
        self.raise_btn.pack(pady=(6, 2))

        # ── Footer ─────────────────────────────────────────────────────────
        self.footer = tk.Frame(self.root, bg=bg)
        self.footer.pack(fill="x", pady=(6, 0))

        self.stats_label = tk.Label(
            self.footer,
            text="Session:  clean 0  |  errors 0  |  cycles: 0",
            font=(_FONT, 10), bg=bg, fg=sub,
        )
        self.stats_label.pack()

        self.footer_sep = tk.Frame(self.footer, bg=C["border"], height=1)
        self.footer_sep.pack(fill="x", padx=50, pady=(8, 5))

        tips_text = (
            "💡  Set a comfortable tempo · Play your lick · "
            "Mark Clean or Error\n"
            "After 3 consecutive clean plays you can raise the tempo. "
            "Take breaks — rest helps consolidate skills."
        )
        self.tips_label = tk.Label(
            self.footer, text=tips_text,
            font=(_FONT, 8), bg=bg, fg=muted,
            justify="center", wraplength=620,
        )
        self.tips_label.pack(pady=(0, 4))

        self.hints_label = tk.Label(
            self.footer,
            text=(
                "Space: Start/Pause  ·  S: Reset  ·  N: Skip  ·  "
                "H/1: Clean  ·  E/2: Error  ·  U/3: Raise  ·  "
                "T: Pin  ·  D: Theme  ·  I: Stats"
            ),
            font=(_FONT, 8), bg=bg, fg=muted,
        )
        self.hints_label.pack(pady=(0, 3))

        self.version_label = tk.Label(
            self.footer,
            text=f"Developed by {DEVELOPER}  ·  v{VERSION}",
            font=(_FONT, 8), bg=bg, fg=muted,
        )
        self.version_label.pack(pady=(0, 8))
