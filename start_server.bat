@echo off
echo ============================================
echo  HealthTrack AI - Starting Server
echo ============================================
echo.

REM Activate venv if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
) else (
    echo [WARNING] Virtual environment not found. Running with system Python.
    echo Run setup.bat first for best results.
)

echo Starting Django development server...
echo.
echo Visit: http://127.0.0.1:8000
echo Admin: http://127.0.0.1:8000/admin
echo Press Ctrl+C to stop the server.
echo.

start "" http://127.0.0.1:8000
python manage.py runserver

pause
