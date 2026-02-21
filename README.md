# 🎸 Pomodoro Guitar Practice

A guitar practice app with a built-in Pomodoro timer, BPM and speed tracking, practice statistics, and sound notifications.

## Description

This application helps you practice guitar efficiently using the Pomodoro technique:
**20 minutes of practice**, then **10 minutes of break**, in recurring cycles.

The program tracks your tempo and controls when you can increase it:
you may only raise the tempo after at least **3 consecutive clean plays**.
If you make an error, the counter resets and you start over.

### Two Modes

- **BPM Mode**: classic BPM setting (e.g. 60, 80, 120 BPM)
- **Speed Mode**: Reaper-style speed multiplier (e.g. 0.30x, 0.50x, 1.00x)

### Light / Dark Theme

The app includes two colour themes you can switch between at any time:

- **Light Mode**: warm cream background, sage green accents (`#FAF9EE`, `#A2AF9B`, `#DCCFC0`, `#EEEEEE`)
- **Dark Mode**: deep blue-grey background, gold accents (`#537188`, `#CBB279`, `#E1D4BB`, `#EEEEEE`)

Toggle with the `D` key or the `🌙 Dark` / `☀ Light` button.

## Features

- **Pomodoro timer**: 20 min practice / 10 min break cycles
- **Two modes**: BPM mode and Speed mode (for Reaper)
- **BPM management**: set and track current BPM (20–300)
- **Speed management**: Reaper-style multiplier (0.05x – 2.00x)
- **Clean play counter**: tracks consecutive clean plays (● ○ ○ visual indicator)
- **Automatic tempo gating**: raise only after 3 clean plays in a row
- **Error reset**: counter resets to zero on any error
- **Pause / Resume**: pause and continue the timer at will
- **Progress bar**: visual progress indicator for the current phase
- **Sound alerts**: warning beeps at 30 s and 10 s before phase end, ascending chord on phase transition
- **Statistics window**: session stats, success rate, bar chart (clean vs errors), and tempo progression chart
- **Session statistics**: clean / error / cycle counts displayed in real time
- **Always on top**: pin the window above other apps
- **Light / Dark theme**: two beautiful colour themes
- **Practice guide**: built-in tips for effective practice
- **GUI**: modern, card-based graphical interface (tkinter)

## Keyboard Shortcuts

| Key        | Action                    |
|------------|---------------------------|
| `Space`    | Start / Pause / Resume    |
| `S`        | Stop (reset)              |
| `N`        | Skip (next phase)         |
| `H` / `1`  | Clean play               |
| `E` / `2`  | Error play               |
| `U` / `3`  | Raise tempo              |
| `T`        | Toggle always on top      |
| `D`        | Toggle Light / Dark theme |
| `I`        | Open Statistics window    |

## Requirements

- Python 3.10+ (tested with 3.14)
- Standard libraries only (tkinter – bundled with Python, winsound – Windows only)

## Installation

No extra dependencies are needed — the app uses only Python standard libraries.

```bash
git clone <repo-url>
cd Pomodoro_guitar_practice
```

## Usage

```bash
python main.py
```

### How to Use

1. **Choose a mode**: Select BPM mode or Speed mode (Reaper)
2. **Set your tempo**: Enter the desired starting value (BPM: e.g. 60 | Speed: e.g. 0.30)
3. **Start practising**: Click `▶ Start` — the 20-minute timer begins
4. **Mark clean plays**: Click `✅ Clean` if you played the lick without errors
5. **Mark errors**: Click `❌ Error` if you made a mistake — counter resets to zero
6. **Raise tempo**: After 3 consecutive clean plays the `⬆ Raise` button becomes active
7. **Phase transitions**: The app alerts you with sound at 30 s, 10 s, and when a phase ends
8. **View statistics**: Click `📊 Stats` to see detailed session statistics and charts
9. **Theme toggle**: Press `D` or click the theme button to switch between Light and Dark mode

### Workflow

```
Practice (20 min)
  │
  ├─ Play lick at current BPM / speed
  │   ├─ Clean? → counter +1 (●○○ → ●●○ → ●●●)
  │   └─ Error? → counter = 0 (○○○)
  │
  ├─ Counter ≥ 3 → Tempo can be raised (BPM +5 or Speed +0.05x)
  │
  └─ 20 min elapsed → BREAK notification (sound alert at 30 s and 10 s before)
        │
        Break (10 min)
        │
        └─ 10 min elapsed → PRACTICE notification
              │
              └─ New cycle begins
```

## Building an EXE

The app can be packaged into a single `.exe` using the included build script:

```bash
pip install pyinstaller pillow
python build.py
```

The EXE appears in the `dist/` folder with a custom icon.

## Project Structure

```
Pomodoro_guitar_practice/
├── README.md          # Documentation
├── CHANGELOG.md       # Version history
├── main.py            # Main application (GUI + logic)
├── create_icon.py     # Icon generator script
└── build.py           # EXE builder script (PyInstaller)
```

## License

MIT

---

**By DominikRose** · v1.1.0
