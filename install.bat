@echo off
echo ==========================================
echo Setting up TsoeneOps Price List Environment
echo ==========================================

echo [1/3] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Failed to create virtual environment. Please ensure Python is installed and in your PATH.
    pause
    exit /b 1
)

echo [2/3] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo Failed to activate virtual environment.
    pause
    exit /b 1
)

echo [3/3] Installing dependencies from pyproject.toml...
pip install -e .
if errorlevel 1 (
    echo Failed to install dependencies.
    pause
    exit /b 1
)

echo ==========================================
echo Setup Complete!
echo You can now run the server using run.cmd
echo ==========================================
pause
