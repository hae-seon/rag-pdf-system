@echo off
echo ====================================
echo RAG PDF System - Setup Script
echo ====================================
echo.

echo [1/4] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/4] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/4] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo .env file created. Please edit it with your OpenAI API key.
) else (
    echo .env file already exists.
)

echo.
echo ====================================
echo Setup completed successfully!
echo ====================================
echo.
echo Next steps:
echo 1. Edit .env file and add your OpenAI API key
echo 2. Run 'run.bat' to start the application
echo.
pause
