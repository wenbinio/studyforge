@echo off
setlocal enabledelayedexpansion
title StudyForge — Launcher
color 0A

echo.
echo  ========================================
echo    StudyForge - All-in-One Study Tool
echo  ========================================
echo.

:: ── Step 1: Find Python ──────────────────────────────────────────
set "PYTHON="

:: Try common commands
where python >nul 2>&1 && (
    for /f "delims=" %%i in ('python -c "import sys; print(sys.version_info.major)" 2^>nul') do (
        if "%%i"=="3" set "PYTHON=python"
    )
)

if not defined PYTHON (
    where python3 >nul 2>&1 && (
        for /f "delims=" %%i in ('python3 -c "import sys; print(sys.version_info.major)" 2^>nul') do (
            if "%%i"=="3" set "PYTHON=python3"
        )
    )
)

if not defined PYTHON (
    where py >nul 2>&1 && (
        for /f "delims=" %%i in ('py -3 -c "import sys; print(sys.version_info.major)" 2^>nul') do (
            if "%%i"=="3" set "PYTHON=py -3"
        )
    )
)

if not defined PYTHON (
    echo  [ERROR] Python 3 was not found on this system.
    echo.
    echo  Please install Python 3.10+ from https://www.python.org/downloads/
    echo  IMPORTANT: Check "Add Python to PATH" during installation.
    echo.
    echo  After installing, close this window and double-click StudyForge.bat again.
    echo.
    pause
    exit /b 1
)

for /f "delims=" %%v in ('%PYTHON% -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\")" 2^>nul') do set "PYVER=%%v"
echo  [OK] Found Python %PYVER%

:: ── Step 2: Create virtual environment if needed ─────────────────
cd /d "%~dp0"

if not exist "venv\Scripts\activate.bat" (
    echo  [..] Creating virtual environment (first run only^)...
    %PYTHON% -m venv venv
    if errorlevel 1 (
        echo  [ERROR] Failed to create virtual environment.
        echo  Try running: %PYTHON% -m pip install --user virtualenv
        pause
        exit /b 1
    )
    echo  [OK] Virtual environment created.
) else (
    echo  [OK] Virtual environment found.
)

:: ── Step 3: Activate and install dependencies ────────────────────
call venv\Scripts\activate.bat

:: Check if deps are installed by trying to import customtkinter
venv\Scripts\python.exe -c "import customtkinter" >nul 2>&1
if errorlevel 1 (
    echo  [..] Installing dependencies (first run only^)...
    echo.
    venv\Scripts\python.exe -m pip install --upgrade pip >nul 2>&1
    venv\Scripts\python.exe -m pip install customtkinter>=5.2.0 anthropic>=0.39.0 python-docx>=1.1.0 PyMuPDF>=1.24.0 Pillow>=10.0.0 markdown>=3.5.0
    if errorlevel 1 (
        echo.
        echo  [ERROR] Failed to install some dependencies.
        echo  Check your internet connection and try again.
        pause
        exit /b 1
    )
    echo.
    echo  [OK] All dependencies installed.
) else (
    echo  [OK] Dependencies already installed.
)

:: ── Step 4: Launch the app ───────────────────────────────────────
echo.
echo  [**] Launching StudyForge...
echo  ========================================
echo.
venv\Scripts\python.exe main.py
if errorlevel 1 (
    echo.
    echo  [ERROR] App crashed. Check the output above for details.
    pause
)
