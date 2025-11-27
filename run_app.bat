@echo off
REM run_app.bat - Runs the app using the venv Python if available
REM Usage: double-click or run from cmd/powershell

:: Resolve script directory
SET SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

:: Prefer venv python if it exists
IF EXIST ".\.venv\Scripts\python.exe" (
    SET PYTHON="%SCRIPT_DIR%\.venv\Scripts\python.exe"
) ELSE (
    SET PYTHON=python
)

:: Run the app as a module (unbuffered)
%PYTHON% -u -m app.main

:: Pause so the window stays open after the script exits
PAUSE
