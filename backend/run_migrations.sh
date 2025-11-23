#!/usr/bin/env bash
# Helper script to create and apply Django migrations for development
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
SRC_DIR="$ROOT_DIR/src"

echo "Running migrations in $SRC_DIR"

if [ -d "$ROOT_DIR/.venv" ]; then
  echo "Activating existing virtualenv .venv"
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/Scripts/activate" || source "$ROOT_DIR/.venv/bin/activate"
else
  echo "Creating virtualenv at $ROOT_DIR/.venv"
  python -m venv "$ROOT_DIR/.venv"
  # shellcheck disable=SC1091
  source "$ROOT_DIR/.venv/Scripts/activate" || source "$ROOT_DIR/.venv/bin/activate"
fi

echo "Installing dev requirements (may take a few minutes)"
pip install --upgrade pip
pip install -r "$ROOT_DIR/requirements-dev.txt"

cd "$SRC_DIR"
python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Migrations complete"
