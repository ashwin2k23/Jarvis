# -*- mode: python ; coding: utf-8 -*-

import os
import sys

block_cipher = None

# Include assets and data files
added_files = [
    ('assets', 'assets'),
]

# Hidden imports that PyInstaller might miss dynamically
hidden_imports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'PySide6.QtSvg',
    'speech_recognition',
    'pyttsx3',
    'edge_tts',
    'psutil',
    'requests',
    'PIL',
    'cv2',
    'pdfplumber',
    'openai',
    'google.genai',
    'pynput',
    'playwright',
]

a = Analysis(
    ['run.py'],
    pathex=['.'],
    binaries=[],
    datas=added_files,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Building standard folder distribution (dist/JarvisAI/)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='JarvisAI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  # Set to True to show console window for debugging logs
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='JarvisAI',
)
