@echo off
REM run_assignment2_tests.bat - Runs pytest with coverage for Assignment 2

:: Set console title
title Kiwi Portfolio - Assignment 2 Tests

:: Resolve script directory and change to it
SET SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo ============================================
echo Kiwi Portfolio - Assignment 2 Test Suite
echo ============================================
echo.

:: Check if Python is available
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python and try again.
    echo.
    goto :end
)

:: Check if virtual environment exists and use it if available
if exist ".\.venv\Scripts\python.exe" (
    echo [INFO] Using virtual environment Python
    SET PYTHON="%SCRIPT_DIR%\.venv\Scripts\python.exe"
) else (
    echo [INFO] Using system Python
    SET PYTHON=python
)

:: Set encoding to handle any potential Unicode issues
chcp 65001 >nul 2>&1

:: Run pytest with coverage
echo [INFO] Running test suite with coverage...
echo.
%PYTHON% -m pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

:: Check exit code
if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] All tests passed!
    echo.
    echo [INFO] Coverage report saved to htmlcov\index.html
) else (
    echo.
    echo [ERROR] Some tests failed. Check output above.
)

:end
echo.
echo Press any key to exit...
pause >nul
