@echo off
REM Helper batch to run Django makemigrations and migrate on Windows (cmd)
SETROOT=%~dp0
SET VENV=%~dp0\.venv

IF NOT EXIST "%VENV%\Scripts\activate.bat" (
  echo Creating virtualenv at %VENV%
  python -m venv "%VENV%"
)

call "%VENV%\Scripts\activate.bat"
echo Installing dev requirements (may take a few minutes)
pip install --upgrade pip
pip install -r "%~dp0\requirements-dev.txt"

cd /d "%~dp0src"
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo Migrations complete
