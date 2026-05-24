# Docker テンプレート (script)

対象:

- 単発または定期実行スクリプト: CI/CD ジョブ、バッチ処理、データ移行
- 外部サービス依存なし（DB/キャッシュなし）
- Compose 不要、または最大 1 サービス

## 設計方針

- 単一ステージの Dockerfile で十分
- コンテナは 1 回実行して終了する（`CMD` が 1 回実行されて終わる）
- 設定は環境変数で注入する。スクリプト固有のシークレットは `.env` で管理する

## Dockerfile テンプレート

```dockerfile
# syntax=docker/dockerfile:1
FROM python:3.13-slim
WORKDIR /app
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV PYTHONUNBUFFERED=1
CMD ["python", "main.py"]
```

## docker-compose.yml テンプレート（外部サービスが 1 つ必要な場合のみ）

```yaml
services:
  script:
    build:
      context: .
    env_file:
      - .env
    # Compose なしでも実行できる設計を維持する
    # 依存関係が増えたら tool に移行する
```

## .dockerignore テンプレート

```gitignore
.git
.env
.env.*
__pycache__
*.pyc
*.log
tests/
```

## 補足

- 外部サービス依存が 1 つ増えたら `tool` に移行する。
- CI/CD での使用を想定し、軽量イメージと高速な再ビルドを優先する。
- タスク完了後にコンテナが終了するよう設計する（`restart: no`）。
