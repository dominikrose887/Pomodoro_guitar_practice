"""
Statistics popup window.
"""

import tkinter as tk
import time

from source.constants import (
    FONT_FAMILY as _FONT,
    MODE_BPM,
)
from source.themes import C


def show_stats_window(app) -> None:
    """Open a themed statistics popup centred on the main window."""

    win = tk.Toplevel(app.root)
    win.title("Session Statistics")
    win.resizable(False, False)
    win.configure(bg=C["bg"])
    win.transient(app.root)
    win.grab_set()

    # Set taskbar / title-bar icon to match main window
    try:
        from source.constants import ICON_PATH
        import os
        if os.path.isfile(ICON_PATH):
            win.iconbitmap(ICON_PATH)
    except Exception:
        pass

    bg = C["bg"]
    card_bg = C["card"]
    card_alt = C["card_alt"]
    txt = C["text"]
    sub = C["text_light"]
    muted = C["text_muted"]
    border = C["border"]

    # Title
    tk.Label(
        win, text="📊  Session Statistics",
        font=(_FONT, 18, "bold"), bg=bg, fg=C["accent"],
    ).pack(pady=(16, 8))

    # ── Overview card ──────────────────────────────────────────────────────
    ov_outer = tk.Frame(win, bg=border, padx=1, pady=1)
    ov_outer.pack(fill="x", padx=20, pady=4)
    ov = tk.Frame(ov_outer, bg=card_bg, padx=16, pady=10)
    ov.pack(fill="both", expand=True)

    elapsed = time.time() - app.session_start
    eh, erem = divmod(int(elapsed), 3600)
    em, es = divmod(erem, 60)

    ph, prem = divmod(app.total_practice_seconds, 3600)
    pm, ps = divmod(prem, 60)

    bh, brem = divmod(app.total_break_seconds, 3600)
    bm, bs = divmod(brem, 60)

    for lbl, val in [
        ("Session Duration", f"{eh:02d}:{em:02d}:{es:02d}"),
        ("Practice Time",    f"{ph:02d}:{pm:02d}:{ps:02d}"),
        ("Break Time",       f"{bh:02d}:{bm:02d}:{bs:02d}"),
        ("Completed Cycles", str(app.completed_cycles)),
    ]:
        row = tk.Frame(ov, bg=card_bg)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=lbl, font=(_FONT, 11),
                 bg=card_bg, fg=sub, anchor="w").pack(side="left")
        tk.Label(row, text=val, font=(_FONT, 11, "bold"),
                 bg=card_bg, fg=txt, anchor="e").pack(side="right")

    # ── Performance card ───────────────────────────────────────────────────
    pf_outer = tk.Frame(win, bg=border, padx=1, pady=1)
    pf_outer.pack(fill="x", padx=20, pady=4)
    pf = tk.Frame(pf_outer, bg=card_alt, padx=16, pady=10)
    pf.pack(fill="both", expand=True)

    total_plays = app.total_clean + app.total_errors
    rate = (app.total_clean / total_plays * 100) if total_plays > 0 else 0

    if app.mode == MODE_BPM:
        cur_t = f"{app.bpm} BPM"
        start_t = f"{app.starting_bpm} BPM"
        prog = app.bpm - app.starting_bpm
        prog_t = f"+{prog} BPM" if prog >= 0 else f"{prog} BPM"
    else:
        cur_t = f"{app.speed:.2f}x"
        start_t = f"{app.starting_speed:.2f}x"
        prog = app.speed - app.starting_speed
        prog_t = f"+{prog:.2f}x" if prog >= 0 else f"{prog:.2f}x"

    for lbl, val in [
        ("Clean Plays",    str(app.total_clean)),
        ("Errors",         str(app.total_errors)),
        ("Success Rate",   f"{rate:.1f}%"),
        ("Tempo Raises",   str(app.tempo_raises)),
        ("Starting Tempo", start_t),
        ("Current Tempo",  cur_t),
        ("Progress",       prog_t),
    ]:
        row = tk.Frame(pf, bg=card_alt)
        row.pack(fill="x", pady=2)
        tk.Label(row, text=lbl, font=(_FONT, 11),
                 bg=card_alt, fg=sub, anchor="w").pack(side="left")
        tk.Label(row, text=val, font=(_FONT, 11, "bold"),
                 bg=card_alt, fg=txt, anchor="e").pack(side="right")

    # ── Bar chart: Clean vs Errors ─────────────────────────────────────────
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

    max_val = max(app.total_clean, app.total_errors, 1)
    bar_w = 60
    gap = 30

    # Clean bar
    clean_h = max(int((app.total_clean / max_val) * (chart_h - 35)), 2)
    x1 = (chart_w // 2) - bar_w - (gap // 2)
    chart.create_rectangle(
        x1, chart_h - clean_h - 20, x1 + bar_w, chart_h - 20,
        fill=C["btn_ok"], outline="",
    )
    chart.create_text(
        x1 + bar_w // 2, chart_h - clean_h - 26,
        text=str(app.total_clean),
        font=(_FONT, 10, "bold"), fill=txt,
    )
    chart.create_text(
        x1 + bar_w // 2, chart_h - 8,
        text="Clean", font=(_FONT, 9), fill=sub,
    )

    # Error bar
    error_h = max(int((app.total_errors / max_val) * (chart_h - 35)), 2)
    x2 = (chart_w // 2) + (gap // 2)
    chart.create_rectangle(
        x2, chart_h - error_h - 20, x2 + bar_w, chart_h - 20,
        fill=C["btn_err"], outline="",
    )
    chart.create_text(
        x2 + bar_w // 2, chart_h - error_h - 26,
        text=str(app.total_errors),
        font=(_FONT, 10, "bold"), fill=txt,
    )
    chart.create_text(
        x2 + bar_w // 2, chart_h - 8,
        text="Errors", font=(_FONT, 9), fill=sub,
    )

    # ── Tempo progression line chart ───────────────────────────────────────
    if len(app.tempo_history) > 1:
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

        if app.mode == MODE_BPM:
            values = [(t, bpm) for t, bpm, _ in app.tempo_history]
        else:
            values = [(t, spd) for t, _, spd in app.tempo_history]

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

        points = []
        for t, v in values:
            points.extend([tx(t), ty(v)])

        if len(points) >= 4:
            tc.create_line(
                points, fill=C["accent"], width=2, smooth=False,
            )

        for t, v in values:
            cx, cy = tx(t), ty(v)
            r = 4
            tc.create_oval(
                cx - r, cy - r, cx + r, cy + r,
                fill=C["accent_soft"], outline="",
            )

        if app.mode == MODE_BPM:
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
    pw = app.root.winfo_x()
    ph_y = app.root.winfo_y()
    px = app.root.winfo_width()
    ww = win.winfo_width()
    win.geometry(f"+{pw + (px - ww) // 2}+{ph_y + 40}")
    win.focus_set()
