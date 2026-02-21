# Changelog

## [1.2.1] - 2026-02-21

### Changed
- Window size reduced from 700×900 to 700×750 (removed excess empty space)
- Speed Mode label simplified: removed "(Reaper)" suffix
- Icon files (`app_icon.ico`, `app_icon.png`) moved into `res/` folder

### Fixed
- **Taskbar icon**: added `SetCurrentProcessExplicitAppUserModelID` and `iconphoto` so the custom icon reliably appears on both the title bar and the Windows taskbar

---

## [1.2.0] - 2025-06-20

### Added
- **Modular source layout**: codebase refactored from a single 1 300-line `main.py` into a `source/` package (`constants`, `themes`, `sounds`, `stats_window`, `app`)
- **Redesigned colour palettes**: warm paper-white light theme (sage green, dusty gold, muted rose) and deep-slate dark theme (warm gold, teal accents)
- **Clean build step**: `build.py` now removes `build/`, `dist/`, `__pycache__`, and `.spec` files before every build
- Build script bundles `res/` and `source/` via `--add-data` for correct EXE packaging

### Changed
- `main.py` is now a thin entry point (imports `source.app`)
- Build script fully translated to English
- All theme key names modernised (`accent`, `accent_sec`, `accent_soft`, `accent_dim` replace old names)
- Button and card colours updated for better contrast in both themes
- `build.py` automatically detects and bundles `res/` and `source/` directories

### Fixed
- **Window icon not showing** on taskbar and title bar – now calls `root.iconbitmap()` and `Toplevel.iconbitmap()` with `app_icon.ico`

---

## [1.1.0] - 2026-02-21

### Added
- **Sound alerts**: warning beeps at 30s and 10s before phase end (both practice and break phases)
- **Statistics window** (`📊 Stats` button or `I` key): detailed session stats with bar chart (clean vs errors) and tempo progression line chart
- **Practice guide**: short tips section in the footer explaining how to practice effectively
- **Keyboard shortcuts reference**: dedicated section at the bottom listing all shortcuts in grey text
- **Developer info & version number** displayed at the bottom of the UI
- New keyboard shortcut: `I` to open the Statistics window
- Tempo history tracking for progression chart
- Session time tracking (practice time, break time, session duration)
- Tempo raise counter

### Changed
- **All UI text translated to English** (was Hungarian)
- Keyboard shortcut hints **removed from button labels** — listed separately at bottom instead
- Button labels simplified: `Start`, `Pause`, `Reset`, `Skip`, `Pin`, `Dark`/`Light`, `Clean`, `Error`, `Raise BPM`/`Raise Speed`
- Second button row now includes 4 buttons: Skip, Stats, Pin, Theme
- Window size adjusted to `700×900` to accommodate new footer content
- Error/warning message dialogs now in English

### Fixed
- N/A

## [1.0.0] - Initial Release

- Pomodoro timer (20 min practice / 10 min break cycles)
- BPM and Speed (Reaper) modes
- Clean play tracking with 3-consecutive-clean requirement for tempo raise
- Light and Dark theme support
- Always on top functionality
- Keyboard shortcuts
- Phase-end sound notification
- Card-based modern GUI (tkinter)
