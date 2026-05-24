# エージェント定義テンプレート

```markdown
---
name: [name]
description: >
  [エージェントの役割を 2〜3 文で説明する。]
  [呼び出し時に渡すべき引数があれば明記する。]
tools: [Read, Write, Edit, Glob, Grep, Bash]
model: haiku
color: blue
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

## カラー選択の目安

| color       | 用途例                   |
| ----------- | ------------------------ |
| `blue`      | 実装・ビルド系           |
| `lightblue` | 調査・情報収集系         |
| `purple`    | レビュー・検証系         |
| `green`     | デプロイ・運用系         |
| `orange`    | 警告・注意が必要な操作系 |
| `red`       | 破壊的操作・緊急対応系   |

## モデル選択の目安

| model    | 用途例                             |
| -------- | ---------------------------------- |
| `haiku`  | 実装・調査など高頻度呼び出しタスク |
| `sonnet` | レビュー・設計など精度優先タスク   |
| `opus`   | 複雑な推論・意思決定が必要なタスク |
