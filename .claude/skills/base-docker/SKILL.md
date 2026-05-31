---
name: base-docker
description: >-
  Dockerfile、docker-compose.yml、.dockerignore の作成・更新時に使用する。
  アーキテクチャ（script/tool/function/application）を判定し、./structures から適切なテンプレートを選択して適用する。
user-invocable: false
---

# Docker コンテナ化コンテキスト

ワークスペースの Docker 固有のコンテキストを一元管理するリファレンススキル。
プロジェクトのアーキテクチャを判定し、対応するコンテナ化テンプレートへの参照を提供する。

## テンプレートの選択

アーキテクチャを判定し、対応するテンプレートを読み込む。デフォルトは `function`。
判断に迷う場合は候補を 2 つ読み比べ、よりシンプルな方を選ぶ。

| アーキテクチャ | パス                          |
| -------------- | ----------------------------- |
| `script`       | `./structures/script.md`      |
| `tool`         | `./structures/tool.md`        |
| `function`     | `./structures/function.md`    |
| `application`  | `./structures/application.md` |

判定基準（このテンプレートを選ぶ条件）は次のとおり。

- `script` — 単発・定期実行スクリプト。外部サービス依存なし。Compose 不要または最大 1 サービス。
- `tool` — 単一ツール + DB／キャッシュ最大 1 つ。PoC・個人プロジェクト・小規模社内ツール。
- `function` — 標準 Web アプリ（app + db + cache）。開発・本番設定の分離が必要なチーム開発（デフォルト）。
- `application` — 複数サービス分割。ネットワーク分離・セキュリティ要件あり・オーケストレーター移行前提。
