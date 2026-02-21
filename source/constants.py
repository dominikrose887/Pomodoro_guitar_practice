"""
Application-wide constants.
"""

import os

VERSION = "1.2.1"
DEVELOPER = "DominikRose"

# ── Paths ───────────────────────────────────────────────────────────────────
_PKG_DIR = os.path.dirname(os.path.abspath(__file__))
_ROOT_DIR = os.path.dirname(_PKG_DIR)

BEEP_WAV = os.path.join(_ROOT_DIR, "res", "beep.wav")
ICON_PATH = os.path.join(_ROOT_DIR, "res", "app_icon.ico")
ICON_PNG_PATH = os.path.join(_ROOT_DIR, "res", "app_icon.png")

# ── Timer ───────────────────────────────────────────────────────────────────
PRACTICE_MINUTES = 20
BREAK_MINUTES = 10
REQUIRED_CLEAN_PLAYS = 3

# ── BPM mode ────────────────────────────────────────────────────────────────
BPM_INCREMENT = 5
DEFAULT_BPM = 60
MIN_BPM = 20
MAX_BPM = 300

# ── Speed mode ──────────────────────────────────────────────────────────────
SPEED_INCREMENT = 0.05
DEFAULT_SPEED = 0.30
MIN_SPEED = 0.05
MAX_SPEED = 2.00

# ── Mode names ──────────────────────────────────────────────────────────────
MODE_BPM = "bpm"
MODE_SPEED = "speed"

# ── Sound alert thresholds (seconds before phase end) ───────────────────────
ALERT_30S = 30
ALERT_10S = 10

# ── Font ────────────────────────────────────────────────────────────────────
FONT_FAMILY = "Segoe UI"
