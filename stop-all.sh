#!/usr/bin/env bash
# Stop background processes started by start-all.sh
set -eo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
PID_FILE="$ROOT_DIR/.pids"

if [ ! -f "$PID_FILE" ]; then
  echo "[stop] PID file not found: $PID_FILE"
  exit 1
fi

source "$PID_FILE"

stop_pid() {
  local name="$1" pid="$2"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    echo "[stop] Killing $name (PID $pid)"
    kill "$pid" || true
  else
    echo "[stop] $name not running"
  fi
}

stop_pid "backend" "${BACKEND_PID:-}"
stop_pid "frontend" "${FRONTEND_PID:-}"

rm -f "$PID_FILE"
echo "[stop] Done."
