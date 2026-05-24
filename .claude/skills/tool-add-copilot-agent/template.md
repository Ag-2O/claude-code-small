# Copilot エージェント定義テンプレート

```markdown
---
name: [name]
description: >
  [エージェントの役割を 2〜3 文で説明する。]
  [呼び出し時に渡すべき引数があれば明記する。]
tools: [execute, read, edit, search, todo]
model: Claude Haiku 4.5 (copilot)
---

# [name] Agent

## Role

[エージェントが担うタスクを 1〜3 文で説明する。]

## Arguments on Invocation

- **[引数名]**: [説明]（例: `[example]`）

引数不足時は呼び出し元へ確認する。

## Workflow

`[skill-name]` スキルを読み込み、[ワークフロー全体の進め方] に従う。

## Best Practices

- **Stay within scope**: 定義された計画の範囲外で変更や機能追加をしない
- **Follow existing patterns**: 新しい流儀を導入する前に、プロジェクト内の類似実装を確認する
- **Never guess**: 仕様が曖昧ならまず確認し、不明なら呼び出し元へ確認する
- **Avoid unnecessary changes**: 指示なしのリファクタ・コメント追加・スタイル修正はしない
```

## ツール選択の目安

| ツール名 | 用途 |
| -------- | ---- |
| `execute` | コマンド実行・テスト実行 |
| `read` | ファイル読み込み |
| `edit` | ファイル作成・編集 |
| `search` | コード検索・ファイル検索 |
| `web` | Web 検索 |
| `browser` | ブラウザ操作 |
| `todo` | タスク管理 |
| `agent` | サブエージェント呼び出し |
| `'cognitionai/deepwiki/*'` | Deepwiki 調査 |

## モデル選択の目安

| model | 用途例 |
| ----- | ------ |
| `Claude Haiku 4.5 (copilot)` | 実装・調査など高頻度呼び出しタスク |
| `Claude Sonnet 4.6 (copilot)` | レビュー・設計など精度優先タスク |
| `Claude Opus 4.7 (copilot)` | 複雑な推論・意思決定が必要なタスク |
