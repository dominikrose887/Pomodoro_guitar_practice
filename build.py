"""
Build script – Pomodoro Guitar Practice → EXE

Steps:
  1. Clean previous build artefacts (build/, dist/, __pycache__, *.spec)
  2. Optionally regenerate the icon (create_icon.py)
  3. Bundle into a single .exe with PyInstaller (includes res/ and source/)

Usage:
  pip install pyinstaller pillow
  python build.py

The EXE appears in dist/.
"""

import glob
import os
import shutil
import subprocess
import sys

# ── Paths ──────────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PY = os.path.join(SCRIPT_DIR, "main.py")
ICON_SCRIPT = os.path.join(SCRIPT_DIR, "create_icon.py")
ICON_FILE = os.path.join(SCRIPT_DIR, "app_icon.ico")
RES_DIR = os.path.join(SCRIPT_DIR, "res")
SOURCE_DIR = os.path.join(SCRIPT_DIR, "source")
APP_NAME = "PomodoroGuitarPractice"

# Directories and patterns to remove before building
CLEAN_DIRS = ["build", "dist"]
CLEAN_PATTERNS = ["*.spec"]
PYCACHE = "__pycache__"


def _rmtree(path: str) -> None:
    """Remove a directory tree if it exists."""
    if os.path.isdir(path):
        shutil.rmtree(path, ignore_errors=True)
        print(f"   removed {os.path.relpath(path, SCRIPT_DIR)}/")


def clean() -> None:
    """Delete all artefacts from previous builds."""
    print("[*] Cleaning previous build artefacts...")

    # Top-level build / dist
    for name in CLEAN_DIRS:
        _rmtree(os.path.join(SCRIPT_DIR, name))

    # .spec files
    for pattern in CLEAN_PATTERNS:
        for f in glob.glob(os.path.join(SCRIPT_DIR, pattern)):
            os.remove(f)
            print(f"   removed {os.path.relpath(f, SCRIPT_DIR)}")

    # __pycache__ everywhere under the project
    for root, dirs, _ in os.walk(SCRIPT_DIR):
        for d in dirs:
            if d == PYCACHE:
                _rmtree(os.path.join(root, d))

    print("[OK] Clean complete.\n")


def check_dependencies() -> None:
    """Verify required packages are installed."""
    missing = []
    try:
        import PIL  # noqa: F401
    except ImportError:
        missing.append("pillow")
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        missing.append("pyinstaller")

    if missing:
        print(f"[ERROR] Missing packages: {', '.join(missing)}")
        print(f"   Install with:  pip install {' '.join(missing)}")
        sys.exit(1)


def generate_icon() -> None:
    """Generate icon if it doesn't already exist."""
    if os.path.exists(ICON_FILE):
        print(f"[OK] Icon already exists: {ICON_FILE}")
        return

    if not os.path.isfile(ICON_SCRIPT):
        print("[!] create_icon.py not found – skipping icon generation.")
        return

    print("[*] Generating icon...")
    result = subprocess.run(
        [sys.executable, ICON_SCRIPT],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[ERROR] Icon generation failed:\n{result.stderr}")
        sys.exit(1)
    print(result.stdout.strip())


def build_exe() -> None:
    """Run PyInstaller to create the EXE."""
    print(f"[*] Building EXE: {APP_NAME}...")

    # Determine --add-data separator (';' on Windows, ':' elsewhere)
    sep = ";" if sys.platform.startswith("win") else ":"

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        f"--icon={ICON_FILE}",
        "--clean",
        "--noconfirm",
    ]

    # Bundle res/ (beep.wav etc.)
    if os.path.isdir(RES_DIR):
        cmd.append(f"--add-data={RES_DIR}{sep}res")

    # Bundle source/ package
    if os.path.isdir(SOURCE_DIR):
        cmd.append(f"--add-data={SOURCE_DIR}{sep}source")

    cmd.append(MAIN_PY)

    result = subprocess.run(cmd, cwd=SCRIPT_DIR)

    if result.returncode != 0:
        print("[ERROR] Build failed!")
        sys.exit(1)

    exe_path = os.path.join(SCRIPT_DIR, "dist", f"{APP_NAME}.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n[OK] Build succeeded!")
        print(f"   File: {exe_path}")
        print(f"   Size: {size_mb:.1f} MB")
    else:
        print("[!] Build finished but EXE not found at expected path.")


def main() -> None:
    print("=" * 60)
    print("  Pomodoro Guitar Practice – EXE Builder")
    print("=" * 60)
    print()

    clean()
    check_dependencies()
    generate_icon()
    build_exe()

    print()
    print("Done!  Run the application:")
    print(f"   dist\\{APP_NAME}.exe")


if __name__ == "__main__":
    main()
