@echo off
echo ============================================
echo  HealthTrack AI - Setup Script
echo ============================================
echo.

REM Check Python
python --version 2>NUL
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ from https://python.org
    pause
    exit /b 1
)

echo [1/5] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo [ERROR] Failed to create virtual environment.
    pause
    exit /b 1
)

echo [2/5] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/5] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Failed to install dependencies.
    pause
    exit /b 1
)

echo [4/5] Running database migrations...
python manage.py makemigrations accounts health
python manage.py migrate
if errorlevel 1 (
    echo [ERROR] Migration failed.
    pause
    exit /b 1
)

echo [5/5] Creating superuser (optional)...
echo You can create an admin account now (press Ctrl+C to skip).
python manage.py createsuperuser --username admin --email admin@healthtrack.com

echo.
echo ============================================
echo  Setup Complete!
echo ============================================
echo.
echo To start the server, run:  start_server.bat
echo Or manually:  venv\Scripts\activate ^& python manage.py runserver
echo.
echo Visit: http://127.0.0.1:8000
echo Admin: http://127.0.0.1:8000/admin
echo.
pause
