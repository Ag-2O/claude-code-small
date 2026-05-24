# Docker テンプレート (function)

対象:

- 標準的な Web アプリ: app + db + cache
- チーム開発（3〜10 人）
- 開発・本番設定の分離が必要（override）
- マルチステージ Dockerfile で dev/prod イメージを分けたい

## 設計方針

- マルチステージ Dockerfile: deps / dev / build / production
- 標準的な Compose 構成: app + db + redis
- `healthcheck` + `depends_on(condition: service_healthy)` を使う
- 開発用 override と本番用 override を分離する

## Dockerfile テンプレート

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22-alpine AS dev
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
EXPOSE 3000
CMD ["npm", "run", "dev"]

FROM node:22-alpine AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build && npm prune --production

FROM node:22-alpine AS production
WORKDIR /app
RUN addgroup -g 1001 -S appgroup && adduser -S appuser -u 1001
USER appuser
COPY --from=build --chown=appuser:appgroup /app/dist ./dist
COPY --from=build --chown=appuser:appgroup /app/node_modules ./node_modules
COPY --from=build --chown=appuser:appgroup /app/package.json ./
ENV NODE_ENV=production
EXPOSE 3000
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:3000/health || exit 1
CMD ["node", "dist/server.js"]
```

## docker-compose.yml テンプレート

```yaml
services:
  app:
    build:
      context: .
      target: dev
    ports:
      - "3000:3000"
    volumes:
      - .:/app
      - /app/node_modules
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/app_dev
      - REDIS_URL=redis://redis:6379/0
      - NODE_ENV=development
    env_file:
      - .env
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    command: npm run dev

  db:
    image: postgres:16-alpine
    ports:
      - "127.0.0.1:5432:5432"
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: app_dev
    volumes:
      - pgdata:/var/lib/postgresql/data
      - ./scripts/init-db.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redisdata:/data

volumes:
  pgdata:
  redisdata:
```

## docker-compose.override.yml テンプレート（開発環境のみ）

```yaml
# 自動読み込み — 開発環境用の設定を上書きする
services:
  app:
    environment:
      - LOG_LEVEL=debug
      - DEBUG=app:*
    ports:
      - "9229:9229"    # デバッガーポート
```

## docker-compose.prod.yml テンプレート（本番相当）

```yaml
# 明示的に指定する: docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
services:
  app:
    build:
      target: production
    restart: always
    deploy:
      resources:
        limits:
          cpus: "1.0"
          memory: 512M
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
.next
.cache
tests/
```

## 補足

- サービスが frontend / api / worker に分割される場合は `application` に移行する。
- 開発時は `docker compose up`、本番相当は `-f docker-compose.prod.yml` を明示的に指定する。
