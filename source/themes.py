"""
Colour theme definitions.

Light – warm off-white with soft sage/olive tones.
Dark  – deep slate with muted gold/teal accents.

The mutable dict ``C`` always reflects the *active* theme and is
updated in-place so every module that imports it stays in sync.
"""

# ── Light theme ─────────────────────────────────────────────────────────────
#    Warm paper white, soft sage green, gentle rose, dusty gold.
THEME_LIGHT: dict[str, str] = {
    # Base
    "bg":             "#f6f5f0",
    "card":           "#ffffff",
    "card_alt":       "#edeae3",
    "border":         "#d6d1c7",
    "text":           "#2c2c2c",
    "text_light":     "#555555",
    "text_muted":     "#9a9a9a",
    # Accent
    "accent":         "#6b9e78",   # sage green
    "accent_sec":     "#c8a951",   # dusty gold
    "accent_soft":    "#8aad7e",   # lighter sage
    "accent_dim":     "#7d9e76",   # muted sage
    "love":           "#c27264",   # muted rose
    # Buttons
    "btn_ok":         "#b6d4a8",
    "btn_ok_act":     "#9fc494",
    "btn_ok_text":    "#2a4a26",
    "btn_err":        "#e8b4b0",
    "btn_err_act":    "#dca09a",
    "btn_err_text":   "#5a2424",
    "btn_warn":       "#edd9a4",
    "btn_warn_act":   "#e0cc90",
    "btn_warn_text":  "#524418",
    "btn_info":       "#a4c8dd",
    "btn_info_act":   "#8fbace",
    "btn_info_text":  "#1e3a50",
    "btn_neut":       "#e4dfd7",
    "btn_neut_act":   "#d4cfc5",
    "btn_neut_text":  "#4a4a4a",
    # Timer
    "timer_practice": "#5a8f64",
    "timer_break":    "#c8a951",
    "timer_paused":   "#c27264",
    # Progress bar
    "prog_bg":        "#e0ddd5",
    "prog_practice":  "#8cba7c",
    "prog_break":     "#e0cc78",
}

# ── Dark theme ──────────────────────────────────────────────────────────────
#    Deep blue-slate, warm gold highlights, soft teal accents.
THEME_DARK: dict[str, str] = {
    # Base
    "bg":             "#1e272e",
    "card":           "#2d3a44",
    "card_alt":       "#283340",
    "border":         "#374856",
    "text":           "#e8e4dc",
    "text_light":     "#c8c0b0",
    "text_muted":     "#7e8e96",
    # Accent
    "accent":         "#d4b563",   # warm gold
    "accent_sec":     "#d4b563",
    "accent_soft":    "#c8c0b0",   # warm stone
    "accent_dim":     "#b8a878",   # muted gold
    "love":           "#d07870",   # muted rose
    # Buttons
    "btn_ok":         "#4a7a52",
    "btn_ok_act":     "#3e6a46",
    "btn_ok_text":    "#d0ecd0",
    "btn_err":        "#7a4444",
    "btn_err_act":    "#6a3838",
    "btn_err_text":   "#f0d0d0",
    "btn_warn":       "#a08840",
    "btn_warn_act":   "#8e7838",
    "btn_warn_text":  "#f8f0d8",
    "btn_info":       "#486e84",
    "btn_info_act":   "#3e6074",
    "btn_info_text":  "#d8ecf4",
    "btn_neut":       "#364855",
    "btn_neut_act":   "#2e3e4a",
    "btn_neut_text":  "#c8c0b0",
    # Timer
    "timer_practice": "#c8c0b0",
    "timer_break":    "#d4b563",
    "timer_paused":   "#d07870",
    # Progress bar
    "prog_bg":        "#283340",
    "prog_practice":  "#6aaa74",
    "prog_break":     "#d4b563",
}

# ── Active colour map (mutable – updated in-place on theme change) ──────────
C: dict[str, str] = dict(THEME_LIGHT)
