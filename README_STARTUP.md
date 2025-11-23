# stock_app 起動ガイド

## 概要
このプロジェクトは Django バックエンドと Next.js フロントエンドで構成されています。

## 必要な環境
- Python 3.12 以上 (または python3)
- Node.js / npm (フロントエンド用、オプション)

## Python 仮想環境
- **場所**: `backend/.venv`
- **自動管理**: `start-all.sh` が自動的に作成・アクティベート
- **バージョン管理**: Python バージョンが変わると自動再作成

## 起動方法

### 基本起動
```bash
./start-all.sh
```

### カスタムポート指定
```bash
./start-all.sh -b 8010 -f 3010
```

### Python バージョン指定
```bash
./start-all.sh --python python3.12
```

### すべてのオプション
```bash
./start-all.sh --help
```

## 停止方法
```bash
./stop-all.sh
```

## ログ確認
```bash
# バックエンドログ
tail -f logs/backend.log

# フロントエンドログ
tail -f logs/frontend.log
```

## トラブルシューティング

### Python venv モジュールがない
```bash
sudo apt install python3.12-venv
```

### npm が見つからない
フロントエンドは自動的にスキップされます。インストールする場合:
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

### 既存プロセスの強制終了
```bash
pkill -f "manage.py runserver"
pkill -f "npm run dev"
```

## ファイル構成
- `start-all.sh` - バックエンド/フロントエンド同時起動スクリプト
- `stop-all.sh` - 停止スクリプト
- `backend/.venv/` - Python 仮想環境 (自動生成)
- `logs/` - 実行ログ (自動生成)
- `.pids` - プロセス ID ファイル (自動生成)

## アクセス URL
- **バックエンド (Django)**: http://127.0.0.1:8000
- **フロントエンド (Next.js)**: http://127.0.0.1:3001
