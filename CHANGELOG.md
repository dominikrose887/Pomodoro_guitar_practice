# Changelog

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
