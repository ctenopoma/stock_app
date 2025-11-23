#!/usr/bin/env bash
# stock_app concurrent backend/frontend starter (background mode)
# 使用方法:
#   1) 初回: ./start-all.sh
#   2) 停止: ./stop-all.sh
# オプション環境変数:
#   USE_DEV_REQUIREMENTS=1 で backend/requirements-dev.txt もインストール
#   BACKEND_PORT (default 8000)
#   FRONTEND_PORT (default 3001)
#   HOST (default 127.0.0.1)

set -eo pipefail

ROOT_DIR="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOG_DIR="$ROOT_DIR/logs"
PID_FILE="$ROOT_DIR/.pids"

HOST="${HOST:-127.0.0.1}"
BACKEND_PORT="${BACKEND_PORT:-8000}"
FRONTEND_PORT="${FRONTEND_PORT:-3001}"
PYTHON_REQUESTED="${PYTHON:-}" # 環境変数 PYTHON でも指定可

print_usage() {
  cat <<EOF
Usage: $(basename "$0") [options]

Options:
  -b, --backend-port PORT    Djangoバックエンドのポート (default: $BACKEND_PORT)
  -f, --frontend-port PORT   Next.jsフロントエンドのポート (default: $FRONTEND_PORT)
  -H, --host HOST            ホスト (default: $HOST)
  -p, --python CMD           利用するPythonコマンド (default: 自動検出 python3.14→python3→python)
  -h, --help                 このヘルプを表示

環境変数でも指定可能: HOST / BACKEND_PORT / FRONTEND_PORT
引数が環境変数より優先されます。
EOF
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      -b|--backend-port)
        BACKEND_PORT="$2"; shift 2;;
      -f|--frontend-port)
        FRONTEND_PORT="$2"; shift 2;;
      -H|--host)
        HOST="$2"; shift 2;;
      -p|--python)
        PYTHON_REQUESTED="$2"; shift 2;;
      -h|--help)
        print_usage; exit 0;;
      --) shift; break;;
      *) echo "[error] Unknown option: $1"; print_usage; exit 1;;
    esac
  done
}

parse_args "$@"

mkdir -p "$LOG_DIR"

echo "[stock_app] Starting services (backend:$BACKEND_PORT frontend:$FRONTEND_PORT host:$HOST)"

activate_venv() {
  # Python コマンド決定: 優先順位 --python 引数 / 環境変数 > python3.14 > python3 > python
  if [ -n "$PYTHON_REQUESTED" ]; then
    PY_CMD="$PYTHON_REQUESTED"
    if ! command -v "$PY_CMD" >/dev/null 2>&1; then
      echo "[backend] 指定Pythonが見つかりません: $PY_CMD" >&2
      exit 1
    fi
  else
    for candidate in python3.12 python3 python; do
      if command -v "$candidate" >/dev/null 2>&1; then
        PY_CMD="$candidate"
        break
      fi
    done
    if [ -z "${PY_CMD:-}" ]; then
      echo "[backend] Python (python3.12/python3/python) が見つかりません" >&2
      exit 1
    fi
  fi
  # venv が利用可能かざっくり確認
  if ! "$PY_CMD" -c "import venv" 2>/dev/null; then
    echo "[backend] エラー: '$PY_CMD' に venv モジュールがありません" >&2
    echo "[backend] 解決方法:" >&2
    echo "  1) システムパッケージの場合: sudo apt install python3.12-venv" >&2
    echo "  2) 手動ビルドの場合: Python をビルド時に --enable-optimizations --with-ensurepip=install オプション付きで再ビルド" >&2
    echo "  3) または利用可能な Python を使用: ./start-all.sh --python python3" >&2
    exit 1
  fi
  if [ -d "$BACKEND_DIR/.venv" ]; then
    # 既存venvのPythonバージョン確認
    if [ -x "$BACKEND_DIR/.venv/bin/python" ]; then
      EXISTING_VER="$($BACKEND_DIR/.venv/bin/python -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
      REQUESTED_VER="$($PY_CMD -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')"
      if [ "$EXISTING_VER" != "$REQUESTED_VER" ]; then
        echo "[backend] Recreating venv (existing $EXISTING_VER != requested $REQUESTED_VER)"
        rm -rf "$BACKEND_DIR/.venv"
      fi
    fi
  fi
  if [ ! -d "$BACKEND_DIR/.venv" ]; then
    echo "[backend] Creating virtualenv using $PY_CMD"
    if ! "$PY_CMD" -m venv "$BACKEND_DIR/.venv" 2>/dev/null; then
      echo "" >&2
      echo "[ERROR] 仮想環境の作成に失敗しました" >&2
      echo "[ERROR] 以下のコマンドで必要なパッケージをインストールしてください:" >&2
      PY_VERSION=$("$PY_CMD" -c 'import sys; print(f"{sys.version_info[0]}.{sys.version_info[1]}")')
      echo "  sudo apt install python${PY_VERSION}-venv" >&2
      echo "" >&2
      exit 1
    fi
  fi
  # shellcheck disable=SC1091
  if ! source "$BACKEND_DIR/.venv/Scripts/activate" 2>/dev/null && ! source "$BACKEND_DIR/.venv/bin/activate" 2>/dev/null; then
    echo "[ERROR] 仮想環境のアクティベートに失敗しました" >&2
    exit 1
  fi
}

install_backend_requirements() {
  echo "[backend] Installing requirements"
  pip install --upgrade pip >/dev/null
  pip install -r "$BACKEND_DIR/requirements.txt" >/dev/null
  if [ "${USE_DEV_REQUIREMENTS:-}" = "1" ]; then
    pip install -r "$BACKEND_DIR/requirements-dev.txt" >/dev/null || true
  fi
}

run_backend_migrations() {
  echo "[backend] Applying migrations"
  (cd "$BACKEND_DIR/src" && python manage.py migrate --noinput)
}

start_backend() {
  echo "[backend] Starting Django server"
  cd "$BACKEND_DIR/src"
  nohup python manage.py runserver "$HOST:$BACKEND_PORT" >"$LOG_DIR/backend.log" 2>&1 </dev/null &
  BACKEND_PID=$!
  echo $BACKEND_PID >"$LOG_DIR/backend.pid"
  echo "[backend] PID $BACKEND_PID"
  cd "$ROOT_DIR"
  disown 2>/dev/null || true
}

install_frontend_dependencies() {
  echo "[frontend] Installing node modules if missing"
  if ! command -v npm >/dev/null 2>&1; then
    echo "[frontend] npm が見つかりません。フロントエンド起動をスキップします" >&2
    echo "[frontend] Node.js/npm をインストールするには: https://nodejs.org/" >&2
    SKIP_FRONTEND=1
    return 0
  fi
  if [ ! -d "$FRONTEND_DIR/node_modules" ]; then
    (cd "$FRONTEND_DIR" && npm install >/dev/null)
  fi
}

start_frontend() {
  if [ "${SKIP_FRONTEND:-}" = "1" ]; then
    return 0
  fi
  echo "[frontend] Starting Next.js dev server"
  cd "$FRONTEND_DIR"
  # 環境変数を設定してNext.jsプロキシが正しく動作するようにする
  export BACKEND_HOST="$HOST"
  export BACKEND_PORT="$BACKEND_PORT"
  nohup npm run dev -- -H "$HOST" -p "$FRONTEND_PORT" >"$LOG_DIR/frontend.log" 2>&1 </dev/null &
  FRONTEND_PID=$!
  echo $FRONTEND_PID >"$LOG_DIR/frontend.pid"
  echo "[frontend] PID $FRONTEND_PID"
  cd "$ROOT_DIR"
  disown 2>/dev/null || true
}

write_pid_file() {
  echo "BACKEND_PID=$(cat "$LOG_DIR/backend.pid")" >"$PID_FILE"
  if [ "${SKIP_FRONTEND:-}" != "1" ]; then
    echo "FRONTEND_PID=$(cat "$LOG_DIR/frontend.pid")" >>"$PID_FILE"
  fi
}

activate_venv
install_backend_requirements
run_backend_migrations
start_backend
install_frontend_dependencies
start_frontend
write_pid_file

echo "[stock_app] All services launched. Logs: $LOG_DIR"
echo "  Django   -> http://$HOST:$BACKEND_PORT"
if [ "${SKIP_FRONTEND:-}" != "1" ]; then
  echo "  Next.js  -> http://$HOST:$FRONTEND_PORT"
fi
echo "[stock_app] To stop: ./stop-all.sh"
