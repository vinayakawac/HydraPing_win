# -*- mode: python ; coding: utf-8 -*-


import sys
from pathlib import Path

# Get Python DLL path from system Python installation
python_dll = Path(r'C:\Users\vinay\AppData\Local\Programs\Python\Python313\python313.dll')

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[(str(python_dll), '.')],
    datas=[('icon.png', '.'), ('icon.ico', '.'), ('core', 'core'), ('theme_manager.py', '.'), ('settings_dialog.py', '.'), ('overlay_window.py', '.'), ('db_schema.py', '.')],
    hiddenimports=['PySide6.QtCore', 'PySide6.QtWidgets', 'PySide6.QtGui', 'sqlite3', 'hashlib', 'ctypes', 'winsound'],
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
    name='HydraPing',
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
    icon=['icon.ico'],
)
