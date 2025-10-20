@echo off
REM Quick test runner for comprehensive test suite
REM Run from project root or tools directory

:: Change to project root if we're in tools directory
if exist "test_comprehensive.py" (
    cd ..
)

:: Check if we're in the right directory
if not exist "tools\test_comprehensive.py" (
    echo Error: Cannot find test_comprehensive.py
    echo Make sure you're running this from the project root
    pause
    exit /b 1
)

:: Set UTF-8 encoding
chcp 65001 >nul 2>&1

:: Use venv Python if available, otherwise system Python
if exist ".venv\Scripts\python.exe" (
    .venv\Scripts\python.exe tools\test_comprehensive.py
) else (
    python tools\test_comprehensive.py
)

echo.
echo Tests completed. Press any key to exit...
pause >nul