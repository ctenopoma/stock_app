@echo off
echo Starting all servers...
echo.

REM Start Django backend
echo [1/2] Starting Django backend server...
start "Django Backend" cmd /k "cd /d "%~dp0backend" && .venv\Scripts\activate && cd src && python manage.py runserver 127.0.0.1:8000"

REM Wait a bit for backend to start
timeout /t 3 /nobreak > nul

REM Start Next.js frontend
echo [2/2] Starting Next.js frontend server...
start "Next.js Frontend" cmd /k "cd /d "%~dp0frontend" && npm run dev"

echo.
echo All servers started!
echo - Django: http://127.0.0.1:8000
echo - Next.js: http://127.0.0.1:3001
echo.
echo Press any key to exit this window (servers will continue running)...
pause > nul
