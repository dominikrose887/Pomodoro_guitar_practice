"""
Theme-switching mixin – toggle light/dark and re-apply colours.
"""

from __future__ import annotations

from source.themes import C, THEME_LIGHT, THEME_DARK


class ThemeMixin:
    """Mixin that provides ``_toggle_theme`` and ``_apply_theme``."""

    def _toggle_theme(self) -> None:
        if self.current_theme == "light":
            self.current_theme = "dark"
            C.update(THEME_DARK)
            self.theme_btn.configure(text="☀  Light")
        else:
            self.current_theme = "light"
            C.update(THEME_LIGHT)
            self.theme_btn.configure(text="🌙  Dark")
        self._apply_theme()

    def _apply_theme(self) -> None:  # noqa: C901
        bg = C["bg"]
        card_bg = C["card"]
        card_alt = C["card_alt"]
        border = C["border"]
        txt = C["text"]
        sub = C["text_light"]
        muted = C["text_muted"]

        self.root.configure(bg=bg)

        # Header
        self.header.configure(bg=bg)
        if self.timer_paused:
            self.status_label.configure(bg=bg, fg=C["timer_paused"])
        elif self.is_practice:
            self.status_label.configure(bg=bg, fg=C["accent"])
        else:
            self.status_label.configure(bg=bg, fg=C["accent_sec"])

        # Timer card
        self.timer_card.configure(bg=border)
        self.timer_card._inner.configure(bg=card_bg)
        if self.timer_paused:
            tfg = C["timer_paused"]
        elif self.is_practice:
            tfg = C["timer_practice"]
        else:
            tfg = C["timer_break"]
        self.timer_label.configure(bg=card_bg, fg=tfg)
        self.progress_canvas.configure(bg=C["prog_bg"])
        pc = C["prog_practice"] if self.is_practice else C["prog_break"]
        self.progress_canvas.itemconfigure(self.progress_bar, fill=pc)

        # Timer buttons
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

        # Tempo card
        self.tempo_card.configure(bg=border)
        self.tempo_card._inner.configure(bg=card_alt)
        self.mode_frame.configure(bg=card_alt)
        self.radio_bpm.configure(
            bg=card_alt, fg=C["accent_dim"],
            selectcolor=card_alt, activebackground=card_alt,
            activeforeground=C["accent_dim"],
        )
        self.radio_speed.configure(
            bg=card_alt, fg=C["accent_dim"],
            selectcolor=card_alt, activebackground=card_alt,
            activeforeground=C["accent_dim"],
        )
        self.tempo_display.configure(bg=card_alt, fg=C["accent_soft"])
        self.input_frame.configure(bg=card_alt)
        self.tempo_label.configure(bg=card_alt, fg=sub)
        self.tempo_entry.configure(bg=card_bg, fg=txt, insertbackground=txt)
        self.tempo_set_btn.configure(
            bg=C["btn_neut"], fg=C["btn_neut_text"],
            activebackground=C["btn_neut_act"],
        )

        # Play card
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

        # Footer
        self.footer.configure(bg=bg)
        self.stats_label.configure(bg=bg, fg=sub)
        self.footer_sep.configure(bg=border)
        self.tips_label.configure(bg=bg, fg=muted)
        self.hints_label.configure(bg=bg, fg=muted)
        self.version_label.configure(bg=bg, fg=muted)

        self._update_clean_display()
