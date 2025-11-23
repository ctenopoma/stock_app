# Docker Compose で stock_app を実行

## 必要な環境
- Docker 20.10+
- Docker Compose 2.0+

## 起動方法

### 初回起動（ビルドが必要）
```bash
docker compose up --build
```

### 2回目以降
```bash
docker compose up
```

### バックグラウンドで起動
```bash
docker compose up -d
```

## 停止方法

### サービスを停止
```bash
docker compose down
```

### サービスを停止してボリュームも削除
```bash
docker compose down -v
```

## アクセス URL
- **バックエンド (Django)**: http://localhost:8000
- **フロントエンド (Next.js)**: http://localhost:3001
- **Django Admin**: http://localhost:8000/admin

## 便利なコマンド

### ログを確認
```bash
# 全サービスのログ
docker compose logs -f

# バックエンドのみ
docker compose logs -f backend

# フロントエンドのみ
docker compose logs -f frontend
```

### サービスの再起動
```bash
# 全サービス
docker compose restart

# バックエンドのみ
docker compose restart backend

# フロントエンドのみ
docker compose restart frontend
```

### コンテナ内でコマンド実行
```bash
# バックエンドでシェルを開く
docker compose exec backend bash

# マイグレーション実行
docker compose exec backend python manage.py migrate

# スーパーユーザー作成
docker compose exec backend python manage.py createsuperuser

# フロントエンドでシェルを開く
docker compose exec frontend sh
```

### コンテナの状態確認
```bash
docker compose ps
```

### ビルドキャッシュをクリアして再ビルド
```bash
docker compose build --no-cache
```

## トラブルシューティング

### ポートが既に使用されている
```bash
# 使用中のポートを確認
sudo lsof -i :8000
sudo lsof -i :3001

# プロセスを停止
sudo kill -9 <PID>
```

### ボリュームの削除（データベースをリセット）
```bash
docker compose down -v
docker compose up --build
```

### イメージの完全な再作成
```bash
docker compose down
docker compose rm -f
docker volume prune -f
docker compose up --build
```

## 開発時の注意点

### ホットリロード
- バックエンド: `./backend/src` ディレクトリがマウントされているため、コード変更は自動的に反映されます
- フロントエンド: `./frontend` ディレクトリがマウントされており、Next.jsのホットリロードが動作します

### データベース
- SQLiteデータベースはDockerボリューム `backend_db` に永続化されます
- ボリュームを削除しない限り、コンテナを停止してもデータは保持されます

### 環境変数
- `docker-compose.yml` の `environment` セクションで環境変数を設定できます
- 本番環境では `.env` ファイルを使用して機密情報を管理してください

## ネットワークアクセス

### ローカルネットワークからアクセス
デフォルトでは `localhost` からのみアクセス可能です。ローカルネットワークからアクセスする場合：

1. `docker-compose.yml` のポート設定を変更：
```yaml
ports:
  - "0.0.0.0:8000:8000"  # backend
  - "0.0.0.0:3001:3001"  # frontend
```

2. ホストのIPアドレスでアクセス（例: `http://192.168.50.51:3001`）
