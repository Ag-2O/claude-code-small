# Docker テンプレート (tool)

対象:

- 単一ツール（アプリ）に付随するサービスが 0〜1 つ
- PoC、検証、小規模社内ツール、個人プロジェクト
- 起動速度最優先

## 設計方針

- 最小構成の単一ステージ Dockerfile（dev ステージのみ）
- シンプルなアプリ中心の Compose 設定
- 依存サービスが増えたら `function` に移行する

## Dockerfile テンプレート

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]
```

## docker-compose.yml テンプレート

```yaml
services:
  app:
    build:
      context: .
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - NODE_ENV=development
    env_file:
      - .env
    command: npm run dev
```

## .dockerignore テンプレート

```gitignore
node_modules
.git
.env
.env.*
dist
coverage
*.log
```

## 補足

- DB やキャッシュが必要になったら `function` に移行する。
- 本番に出す前に、最低限として非 root 実行とヘルスチェックを追加する。
- シークレットは `env_file` + `.env` で管理する（`.gitignore` 追加済みであること）。
