# Docker テンプレート (application)

対象:

- 複数チームが関わるマルチサービス構成
- frontend / api / worker / db / cache / mail が明確に分離されたサービス
- ネットワーク分離、最小権限、シークレット管理が必要
- 将来的なオーケストレーター（Kubernetes / ECS / Swarm）への移行を前提とした設計

## 設計方針

- 1 プロセス・1 コンテナの原則を維持する
- frontend-net / backend-net によるネットワーク分離
- api と worker に `security_opt`、`read_only`、`cap_drop` を適用する
- Compose は開発・検証用に限定する（本番はオーケストレーターを使う）

## docker-compose.yml テンプレート

```yaml
services:
  frontend:
    build:
      context: ./frontend
      target: dev
    ports:
      - "3000:3000"
    networks:
      - frontend-net
    depends_on:
      - api

  api:
    build:
      context: ./api
      target: dev
    ports:
      - "8080:8080"
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/app_dev
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    networks:
      - frontend-net
      - backend-net
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
      - /app/.cache
    cap_drop:
      - ALL

  worker:
    build:
      context: ./api
      target: dev
    command: npm run worker
    environment:
      - DATABASE_URL=postgres://postgres:postgres@db:5432/app_dev
      - REDIS_URL=redis://redis:6379/0
    env_file:
      - .env
    networks:
      - backend-net
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_started
    security_opt:
      - no-new-privileges:true
    read_only: true
    tmpfs:
      - /tmp
    cap_drop:
      - ALL

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
    networks:
      - backend-net

  redis:
    image: redis:7-alpine
    ports:
      - "127.0.0.1:6379:6379"
    volumes:
      - redisdata:/data
    networks:
      - backend-net

  mailpit:
    image: axllent/mailpit
    ports:
      - "8025:8025"    # Web UI
      - "1025:1025"    # SMTP
    networks:
      - backend-net

networks:
  frontend-net:
  backend-net:

volumes:
  pgdata:
  redisdata:
```

## Dockerfile テンプレート（本番ステージ中心）

```dockerfile
# syntax=docker/dockerfile:1
FROM node:22.12-alpine3.20 AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci

FROM node:22.12-alpine3.20 AS build
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .
RUN npm run build && npm prune --production

FROM node:22.12-alpine3.20 AS production
WORKDIR /app
RUN addgroup -g 1001 -S app && adduser -S app -u 1001
USER app
COPY --from=build --chown=app:app /app/dist ./dist
COPY --from=build --chown=app:app /app/node_modules ./node_modules
COPY --from=build --chown=app:app /app/package.json ./
ENV NODE_ENV=production
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s CMD wget -qO- http://localhost:8080/health || exit 1
CMD ["node", "dist/server.js"]
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
Dockerfile*
docker-compose*.yml
README.md
tests/
```

## 補足

- `.env` のコミットは厳禁。必要な場合は Docker secrets（Swarm モード）を使う。
- 大規模な本番環境で Compose に依存しない。オーケストレーターへの移行を前提に設計する。
- ネットワーク問題は `docker network inspect` とコンテナ内 DNS 解決で切り分ける。
