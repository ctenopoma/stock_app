#!/usr/bin/env bash
# Stop background processes started by start-all.sh
set -eo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
LOG_DIR="$ROOT_DIR/logs"
PID_DIR="$ROOT_DIR/.pids"
PID_FILE="$PID_DIR/services.pid"

if [ ! -f "$PID_FILE" ]; then
  echo "[stop] PID file not found: $PID_FILE"
  exit 1
fi

source "$PID_FILE"

stop_pid() {
  local name="$1" pid="$2"
  if [ -n "$pid" ] && kill -0 "$pid" 2>/dev/null; then
    echo "[stop] Killing $name (PID $pid)"
    # プロセスグループ全体を終了（子プロセスも含む）
    kill -- -"$pid" 2>/dev/null || kill "$pid" 2>/dev/null || true
    sleep 1
    # まだ生きていれば強制終了
    if kill -0 "$pid" 2>/dev/null; then
      echo "[stop] Force killing $name (PID $pid)"
      kill -9 -- -"$pid" 2>/dev/null || kill -9 "$pid" 2>/dev/null || true
    fi
  else
    echo "[stop] $name not running (PID $pid)"
  fi
}

stop_pid "backend" "${BACKEND_PID:-}"
stop_pid "frontend" "${FRONTEND_PID:-}"

# ポート番号でも確認して残っているプロセスを終了
echo "[stop] Checking for remaining processes on ports..."
for port in 8000 3001; do
  pids=$(lsof -ti :$port 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "[stop] Killing remaining processes on port $port: $pids"
    echo "$pids" | xargs -r kill -9 2>/dev/null || true
  fi
done

rm -rf "$PID_DIR"
echo "[stop] Done."
