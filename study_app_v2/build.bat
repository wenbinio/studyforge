@echo off
setlocal
title StudyForge v2 - Build Script
echo.
echo  ============================================
echo    StudyForge v2 - Building standalone .exe
echo  ============================================
echo.

:: Check Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Download from https://www.python.org/downloads/
    echo         Make sure to check "Add to PATH" during installation.
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install requirements. Check your internet connection.
    pause
    exit /b 1
)

echo [2/4] Installing PyInstaller...
python -m pip install pyinstaller
if %errorlevel% neq 0 (
    echo [ERROR] Failed to install PyInstaller.
    pause
    exit /b 1
)

echo [3/4] Building StudyForge.exe (this may take 1-3 minutes)...
echo.
python -m PyInstaller StudyForge.spec --noconfirm
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Build failed. See errors above.
    echo         Common fixes:
    echo         - Close any running StudyForge.exe
    echo         - Run this script as Administrator
    echo         - Try: python -m pip install --upgrade pyinstaller
    pause
    exit /b 1
)

echo.
echo  ============================================
echo    BUILD SUCCESSFUL!
echo  ============================================
echo.
echo  Your .exe is at:
echo    dist\StudyForge.exe
echo.
echo  First run:
echo    1. Double-click StudyForge.exe
echo    2. The setup wizard will guide you through configuration
echo    3. Enter your Claude API key (optional)
echo       (get one at console.anthropic.com)
echo    4. AI features will activate immediately
echo.

:: Open the dist folder
explorer dist

pause
