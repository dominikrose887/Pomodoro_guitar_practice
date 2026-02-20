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
        print(f"❌ Hiányzó csomagok: {', '.join(missing)}")
        print(f"   Telepítés: pip install {' '.join(missing)}")
        sys.exit(1)


def generate_icon() -> None:
    """Ikon generálása, ha még nem létezik."""
    if os.path.exists(ICON_FILE):
        print(f"✅ Ikon már létezik: {ICON_FILE}")
        return

    print("🎨 Ikon generálása...")
    result = subprocess.run(
        [sys.executable, ICON_SCRIPT],
        cwd=SCRIPT_DIR,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        print(f"❌ Ikon generálás sikertelen:\n{result.stderr}")
        sys.exit(1)
    print(result.stdout.strip())


def build_exe() -> None:
    """PyInstaller futtatása."""
    print(f"🔨 EXE építése: {APP_NAME}...")

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
        print("❌ Build sikertelen!")
        sys.exit(1)

    exe_path = os.path.join(SCRIPT_DIR, "dist", f"{APP_NAME}.exe")
    if os.path.exists(exe_path):
        size_mb = os.path.getsize(exe_path) / (1024 * 1024)
        print(f"\n✅ Build sikeres!")
        print(f"   📁 {exe_path}")
        print(f"   📦 Méret: {size_mb:.1f} MB")
    else:
        print("⚠️  Build lefutott, de az EXE nem található a várt helyen.")


def main() -> None:
    print("=" * 60)
    print("  🎸 Pomodoro Guitar Practice – EXE Builder")
    print("=" * 60)
    print()

    check_dependencies()
    generate_icon()
    build_exe()

    print()
    print("🎉 Kész! Az alkalmazás futtatható:")
    print(f"   dist\\{APP_NAME}.exe")


if __name__ == "__main__":
    main()
