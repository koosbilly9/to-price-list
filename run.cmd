@echo off
echo Starting TsoeneOps Price List Server...

REM Check if venv exists
if not exist venv\Scripts\activate.bat (
    echo Virtual environment not found. Please run install.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate.bat
python src\run_server.py
pause
