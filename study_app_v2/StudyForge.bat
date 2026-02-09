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

:: Try local embedded Python as last resort
if not defined PYTHON (
    if exist "%~dp0python_embedded\python.exe" (
        set "PYTHON=%~dp0python_embedded\python.exe"
        echo  [OK] Using embedded Python.
        goto :skip_version
    )
)

:: ── Step 1b: Download embedded Python if none found ──────────────
if not defined PYTHON (
    echo  [!!] Python 3 was not found on this system.
    echo.
    echo  StudyForge can download a portable Python automatically.
    echo  No installation required — it stays inside this folder.
    echo.
    set /p "DOWNLOAD=  Download portable Python now? [Y/n]: "
    if /i "!DOWNLOAD!"=="n" (
        echo.
        echo  You can also install Python 3.10+ from https://www.python.org/downloads/
        echo  IMPORTANT: Check "Add Python to PATH" during installation.
        echo.
        pause
        exit /b 1
    )

    echo.
    echo  [..] Downloading Python 3.11.9 embeddable package...

    set "PY_URL=https://www.python.org/ftp/python/3.11.9/python-3.11.9-embed-amd64.zip"
    set "PY_ZIP=%~dp0python_embedded.zip"
    set "PY_DIR=%~dp0python_embedded"

    :: Use PowerShell to download (available on all modern Windows)
    powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri '%PY_URL%' -OutFile '%PY_ZIP%' }" 2>nul
    if errorlevel 1 (
        echo  [ERROR] Download failed. Check your internet connection.
        echo  You can manually install Python from https://www.python.org/downloads/
        pause
        exit /b 1
    )

    echo  [..] Extracting...
    powershell -Command "Expand-Archive -Path '%PY_ZIP%' -DestinationPath '%PY_DIR%' -Force" 2>nul
    del "%PY_ZIP%" >nul 2>&1

    :: Enable pip in embedded Python by uncommenting import site
    powershell -Command "(Get-Content '%PY_DIR%\python311._pth') -replace '#import site','import site' | Set-Content '%PY_DIR%\python311._pth'"

    :: Download and install pip
    echo  [..] Installing pip...
    powershell -Command "& { [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12; Invoke-WebRequest -Uri 'https://bootstrap.pypa.io/get-pip.py' -OutFile '%PY_DIR%\get-pip.py' }" 2>nul
    "%PY_DIR%\python.exe" "%PY_DIR%\get-pip.py" --no-warn-script-location >nul 2>&1
    del "%PY_DIR%\get-pip.py" >nul 2>&1

    echo  [OK] Portable Python ready.
    set "PYTHON=%PY_DIR%\python.exe"
    goto :skip_version
)

for /f "delims=" %%v in ('%PYTHON% -c "import sys; print(f\"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}\")" 2^>nul') do set "PYVER=%%v"
echo  [OK] Found Python %PYVER%

:skip_version

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
