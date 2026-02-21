# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['D:\\Rose\\Documents\\dev_projects\\Pomodoro_guitar_practice\\main.py'],
    pathex=[],
    binaries=[],
    datas=[('D:\\Rose\\Documents\\dev_projects\\Pomodoro_guitar_practice\\res', 'res'), ('D:\\Rose\\Documents\\dev_projects\\Pomodoro_guitar_practice\\source', 'source')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='PomodoroGuitarPractice',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['D:\\Rose\\Documents\\dev_projects\\Pomodoro_guitar_practice\\app_icon.ico'],
)
