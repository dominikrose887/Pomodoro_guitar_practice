"""
Build script – Pomodoro Guitar Practice → EXE

Lépések:
  1. Generálja az ikont (create_icon.py)
  2. PyInstaller-rel egyetlen .exe fájlba csomagolja az alkalmazást

Használat:
  pip install pyinstaller pillow
  python build.py

Az EXE a dist/ mappában jelenik meg.
"""

import subprocess
import sys
import os

# ── Útvonalak ──────────────────────────────────────────────────────────────
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MAIN_PY = os.path.join(SCRIPT_DIR, "main.py")
ICON_SCRIPT = os.path.join(SCRIPT_DIR, "create_icon.py")
ICON_FILE = os.path.join(SCRIPT_DIR, "app_icon.ico")
APP_NAME = "PomodoroGuitarPractice"


def check_dependencies() -> None:
    """Ellenőrzi, hogy a szükséges csomagok telepítve vannak-e."""
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
        print(f"[HIBA] Hianyzo csomagok: {', '.join(missing)}")
        print(f"   Telepites: pip install {' '.join(missing)}")
        sys.exit(1)


def generate_icon() -> None:
    """Ikon generálása, ha még nem létezik."""
    if os.path.exists(ICON_FILE):
        print(f"[OK] Ikon mar letezik: {ICON_FILE}")
        return

    print("[*] Ikon generalasa...")
    result = subprocess.run(
        [sys.executable, ICON_SCRIPT],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"[HIBA] Ikon generalas sikertelen:\n{result.stderr}")
        sys.exit(1)
    print(result.stdout.strip())


def build_exe() -> None:
    """PyInstaller futtatása."""
    print(f"[*] EXE epitese: {APP_NAME}...")

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--windowed",
        f"--name={APP_NAME}",
        f"--icon={ICON_FILE}",
        "--clean",
        "--noconfirm",
        MAIN_PY,
    ]

    result = subprocess.run(cmd, cwd=SCRIPT_DIR)

    if result.returncode != 0:
        print("[HIBA] Build sikertelen!")
        sys.exit(1)

    exe_path = os.path.join(SCRIPT_DIR, "dist", f"{APP_NAME}.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n[OK] Build sikeres!")
        print(f"   Fajl: {exe_path}")
        print(f"   Meret: {size_mb:.1f} MB")
    else:
        print("[!] Build lefutott, de az EXE nem talalhato a vart helyen.")


def main() -> None:
    print("=" * 60)
    print("  Pomodoro Guitar Practice - EXE Builder")
    print("=" * 60)
    print()

    check_dependencies()
    generate_icon()
    build_exe()

    print()
    print("Kesz! Az alkalmazas futtathato:")
    print(f"   dist\\{APP_NAME}.exe")


if __name__ == "__main__":
    main()
