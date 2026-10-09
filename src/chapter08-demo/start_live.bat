@echo off
setlocal
chcp 65001 >nul
set "PYTHONIOENCODING=utf-8"
cd /d "%~dp0..\.." || (
    echo [ERROR] Cannot locate the project directory.
    set /p "COURSEPILOT_CLOSE=Press Enter to close..."
    exit /b 1
)
if not exist ".venv\Scripts\python.exe" (
    echo [ERROR] Run "uv sync --locked" in the project directory first.
    set /p "COURSEPILOT_CLOSE=Press Enter to close..."
    exit /b 1
)
echo [START] CoursePilot live API - configuration: chapter08/.env
".venv\Scripts\python.exe" "%~dp0demo.py" run --mode live
set "COURSEPILOT_EXIT_CODE=%errorlevel%"
echo.
if not "%COURSEPILOT_EXIT_CODE%"=="0" echo [ERROR] Check chapter08/.env and the message above.
set /p "COURSEPILOT_CLOSE=Press Enter to close..."
exit /b %COURSEPILOT_EXIT_CODE%
