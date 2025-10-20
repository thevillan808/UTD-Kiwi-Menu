@echo off
REM run_tests.bat - Runs the comprehensive test suite
REM Usage: double-click or run from cmd/powershell

:: Set console title
title UTD Kiwi CLI - Test Suite

:: Resolve script directory and change to it
SET SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

echo.
echo ============================================
echo UTD Kiwi CLI - Comprehensive Test Suite
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

:: Run the comprehensive test suite
echo [INFO] Running comprehensive test suite...
echo.
%PYTHON% tools\test_comprehensive.py

:: Check exit code
if %errorlevel% equ 0 (
    echo.
    echo [SUCCESS] All tests completed successfully!
) else (
    echo.
    echo [ERROR] Some tests may have failed. Check output above.
)

:end
echo.
echo Press any key to exit...
pause >nul