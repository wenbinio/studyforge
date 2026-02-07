# -*- mode: python ; coding: utf-8 -*-
"""
StudyForge.spec — PyInstaller build specification.

Usage:
    pyinstaller StudyForge.spec

This produces a single StudyForge.exe in the dist/ folder.
"""

import os
import sys
import importlib

block_cipher = None

# ── Locate customtkinter assets (required for UI to render) ──────
import customtkinter
ctk_path = os.path.dirname(customtkinter.__file__)

# ── Data files to bundle ─────────────────────────────────────────
datas = [
    # customtkinter theme/assets
    (ctk_path, "customtkinter"),
    # Default config file
    ("config.json", "."),
]

# Optionally bundle icon if present
if os.path.exists("assets/icon.ico"):
    datas.append(("assets/icon.ico", "assets"))

# ── Hidden imports ───────────────────────────────────────────────
# anthropic SDK and its HTTP transport have many implicit dependencies
hiddenimports = [
    # Core app modules
    "paths",
    "database",
    "srs_engine",
    "claude_client",
    "ui",
    "ui.app",
    "ui.styles",
    "ui.dashboard",
    "ui.pomodoro",
    "ui.flashcards",
    "ui.notes",
    "ui.quiz",
    "ui.settings",
    "ui.hypotheticals",
    "ui.essays",
    "ui.notepad",
    "ui.notepad",
    "ui.essays",
    "ui.hypotheticals",
    "ui.participation",

    # customtkinter
    "customtkinter",

    # anthropic SDK chain
    "anthropic",
    "anthropic._client",
    "anthropic._base_client",
    "anthropic.resources",
    "httpx",
    "httpx._transports",
    "httpx._transports.default",
    "httpcore",
    "httpcore._async",
    "httpcore._sync",
    "h11",
    "h2",
    "hpack",
    "hyperframe",
    "certifi",
    "anyio",
    "anyio._backends",
    "anyio._backends._asyncio",
    "sniffio",
    "idna",
    "socksio",
    "pydantic",
    "pydantic.deprecated",
    "pydantic_core",
    "annotated_types",
    "distro",
    "jiter",
    "typing_extensions",

    # Document parsers
    "fitz",        # PyMuPDF
    "docx",        # python-docx
    "docx.opc",
    "docx.oxml",

    # PIL for customtkinter
    "PIL",
    "PIL._tkinter_finder",
]

a = Analysis(
    ["main.py"],
    pathex=["."],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        "matplotlib", "numpy", "scipy", "pandas",
        "pytest", "setuptools", "pip",
    ],
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
    name="StudyForge",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,          # No console window — clean GUI launch
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon="assets/icon.ico" if os.path.exists("assets/icon.ico") else None,
)
