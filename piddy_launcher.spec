# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for Piddy launcher .exe

Builds a single-file executable that starts the Piddy dashboard
and opens it in the default browser.

Usage:
  cd D:\Piddy
  pyinstaller piddy_launcher.spec --clean
"""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files
import sys
import os

block_cipher = None

# ── Hidden imports (modules loaded dynamically that PyInstaller can't detect) ──
hidden_imports = (
    collect_submodules('fastapi') +
    collect_submodules('uvicorn') +
    collect_submodules('pydantic') +
    collect_submodules('starlette') +
    collect_submodules('anyio') +
    [
        # uvicorn internals
        'uvicorn.logging',
        'uvicorn.loops',
        'uvicorn.loops.auto',
        'uvicorn.protocols',
        'uvicorn.protocols.http',
        'uvicorn.protocols.http.auto',
        'uvicorn.protocols.http.h11_impl',
        'uvicorn.protocols.websockets',
        'uvicorn.protocols.websockets.auto',
        'uvicorn.lifespan',
        'uvicorn.lifespan.on',
        # pydantic
        'pydantic',
        'pydantic_core',
        # sqlite / async
        'sqlite3',
        'aiosqlite',
        'greenlet',
        # Piddy src modules imported at runtime
        'src.dashboard_api',
        'src.log_handler',
        'src.dashboard_data_collector',
        'src.services.rate_limiter',
        'src.approval_workflow',
        'src.approval_gate',
        'src.database',
        # email / dotenv
        'dotenv',
        'email.mime.text',
        'email.mime.multipart',
        # standard lib used by dashboard
        'json',
        'logging',
        'pathlib',
        'asyncio',
        'threading',
        'webbrowser',
        'multiprocessing',
    ]
)

# ── Data files (templates, static assets) ──────────────────────────────────
datas = [
    # Include the entire src/ package
    ('src', 'src'),
    # Include config (settings, not keys)
    ('config/__init__.py', 'config'),
    ('config/settings.py', 'config'),
    # Include piddy/ package
    ('piddy', 'piddy'),
    # Include data directory skeleton
    ('data', 'data'),
    # Include frontend build if it exists
    ('frontend/dist', 'frontend/dist') if os.path.isdir('frontend/dist') else ('frontend/index.html', 'frontend'),
    # Templates
    ('templates', 'templates'),
]

# Filter out entries where source doesn't exist
datas = [(src, dst) for src, dst in datas if os.path.exists(src)]

# Also collect package data
datas += collect_data_files('fastapi')
datas += collect_data_files('pydantic')
datas += collect_data_files('uvicorn')
datas += collect_data_files('starlette')

a = Analysis(
    ['piddy_launcher.py'],
    pathex=['.'],
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
    name='Piddy',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,      # Keep console visible so user sees status + Ctrl+C works
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,          # TODO: add icon path here, e.g. icon='assets/piddy.ico'
)
