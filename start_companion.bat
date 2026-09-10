@echo off
setlocal enabledelayedexpansion
title Dofus Retro Companion Launcher
color 0A
cls

echo.
echo ===================================================
echo        DOFUS RETRO COMPANION - LAUNCHING
echo ===================================================
echo.

REM ============ CONFIG PATHS ============
set "ROOT_DIR=%~dp0"
set "BACKEND_DIR=D:\CODING\dofus1overlay\kimi\electron\backend"
set "ELECTRON_DIR=D:\CODING\dofus1overlay\kimi\electron"
set "DATA_DIR=D:\CODING\dofus1overlay\data"

REM ============ CHECK BACKEND ============
if not exist "%BACKEND_DIR%\app.py" (
    echo [ERROR] Backend not found at:
    echo   %BACKEND_DIR%
    echo Please ensure the backend folder exists.
    pause
    exit /b 1
)

REM ============ CHECK ELECTRON ============
if not exist "%ELECTRON_DIR%\main.js" (
    echo [ERROR] Electron main.js not found at:
    echo   %ELECTRON_DIR%
    echo Please ensure the electron folder exists.
    pause
    exit /b 1
)

REM ============ ENSURE DATA DIRECTORY ============
echo [1/5] Ensuring data directory exists...
if not exist "%DATA_DIR%" mkdir "%DATA_DIR%"

REM ============ CHECK DATABASE ============
if not exist "%DATA_DIR%\dofus.db" (
    echo [WARNING] Database not found.
    echo The app will start with an empty database.
    echo.
)

REM ============ ACTIVATE PYTHON VENV ============
echo [2/5] Checking Python virtual environment...
set "VENV_ACT=%BACKEND_DIR%\venv\Scripts\activate.bat"

if exist "%VENV_ACT%" (
    echo Activating virtual environment...
    set "PYTHON_CMD=call venv\Scripts\activate.bat && python app.py"
) else (
    echo [WARNING] No virtual environment found. Using system Python.
    set "PYTHON_CMD=python app.py"
)

REM ============ START FLASK BACKEND ============
echo [3/5] Starting Flask API Backend (http://127.0.0.1:5000)...
start "Dofus Companion Backend" cmd /k "cd /d %BACKEND_DIR% && %PYTHON_CMD%"

REM ============ WAIT FOR BACKEND ============
echo [4/5] Waiting 5 seconds for backend initialization...
timeout /t 5 /nobreak >nul

REM ============ START ELECTRON ============
echo [5/5] Starting Electron Overlay Interface...
cd /d "%ELECTRON_DIR%"
call npm start

echo.
echo ===================================================
echo     Companion Closed. Cleaning up backend...
echo ===================================================

REM ============ CLEANUP BACKEND PROCESS ============
taskkill /FI "WINDOWTITLE eq Dofus Companion Backend*" /F > nul 2>&1

echo Backend terminated.
echo.
pause
exit /b 0
