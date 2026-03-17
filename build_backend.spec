# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec file for building Piddy backend as standalone executable

Usage:
  pyinstaller build_backend.spec

Output:
  dist/piddy-backend.exe (Windows)
  dist/piddy-backend (Linux/Mac)
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import sys
import os

block_cipher = None

# Collect all submodules for common packages
hidden_imports = collect_submodules('fastapi') + \
                 collect_submodules('uvicorn') + \
                 collect_submodules('pydantic') + \
                 collect_submodules('sqlalchemy') + \
                 collect_submodules('starlette') + \
                 [
                     'fastapi',
                     'uvicorn',
                     'uvicorn.logging',
                     'uvicorn.loops',
                     'uvicorn.loops.auto',
                     'uvicorn.protocols',
                     'uvicorn.protocols.http',
                     'uvicorn.protocols.http.auto',
                     'uvicorn.protocols.websocket',
                     'uvicorn.protocols.websocket.auto',
                     'uvicorn.server',
                     'uvicorn.config',
                     'uvicorn.middleware',
                     'uvicorn.middleware.proxy_headers',
                     'uvicorn.middleware.wsgi',
                     'pydantic',
                     'pydantic.utils',
                     'pydantic.validators',
                     'pydantic.json',
                     'pydantic_core',
                     'sqlalchemy.ext.declarative',
                     'sqlalchemy.orm',
                     'sqlalchemy.pool',
                     'sqlite3',
                     'aiosqlite',
                     'greenlet',
                     'dotenv',
                 ]

# Collect data files
datas = []
datas += collect_data_files('fastapi')
datas += collect_data_files('pydantic')
datas += collect_data_files('uvicorn')

a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='piddy-backend',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,  # Show console window for debugging
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
)
