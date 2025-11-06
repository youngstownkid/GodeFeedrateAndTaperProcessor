@echo off
echo ========================================
echo GCode A-Axis Feedrate Processor
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo Python is not installed or not in PATH.
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation!
    echo.
    pause
    exit /b 1
)

echo Python found! Starting application...
echo.

REM Run the GCode processor
python gcode_processor.py

if %errorlevel% neq 0 (
    echo.
    echo An error occurred while running the application.
    pause
)
