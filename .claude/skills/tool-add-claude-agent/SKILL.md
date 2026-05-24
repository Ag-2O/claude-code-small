---
name: tool-add-claude-agent
description: >
  新しいエージェントを作成する際に使用する。
  エージェントの役割・ツール・モデルを確認し、テンプレートに従って
  .claude/agents/[name].md を生成し、システムに登録する。
user-invocable: false
allowed-tools: [Read, Write, Glob, Grep]
---

# エージェント追加ワークフロー

このスキルは、プロジェクトに新しいエージェントを追加するプロセスを定義する。

## フェーズ 1: 要件の把握

エージェント名と目的が渡されていない場合は確認する。

- **エージェント名**: 小文字のケバブケース（例: `linter`, `deploy-checker`）
- **役割**: エージェントが担うタスク（実装・調査・レビューなど）
- **ツール**: 使用するツール一覧（`Read`, `Write`, `Bash` など）
- **モデル**: `haiku`（軽量タスク）/ `sonnet`（標準）/ `opus`（複雑タスク）
- **ワークフロー**: 呼び出し時にどのスキルを読み込むか

## フェーズ 2: 既存エージェント参照

`.claude/agents/` の一覧を確認し、同種のエージェントを読み込んで構造を把握する。

- 実装系: `coder.md` を参照
- 調査系: `researcher.md` を参照
- レビュー系: `reviewer.md` を参照

同名・類似エージェントが既に存在する場合は、新規作成ではなく既存エージェントの更新を提案する。

## フェーズ 3: エージェント定義ファイルの作成

`./template.md` を読み込み、`.claude/agents/[name].md` を作成する。

### フロントマター必須フィールド

```yaml
---
name: [name]
description: >
  エージェントの役割を 2〜3 文で説明する。
  呼び出し時に渡すべき引数があれば明記する。
tools: [Read, Write, Edit, Glob, Grep, Bash, ...]
model: haiku | sonnet | opus
color: blue | lightblue | purple | green | orange | red
---
```

### ボディ構造

- **Role**: エージェントの責務を 1〜3 文で説明する
- **Arguments on Invocation**: 呼び出し時の引数と例
- **Workflow**: 読み込むスキルと実行順序
- **Best Practices**: 越境・推測・スコープ外変更を防ぐルール

## ベストプラクティス

- description は「いつ呼び出すか」を明確に書く — 呼び出し判断の根拠になる
- tools は最小権限にする — 不要なツールは渡さない
- モデルは役割に合わせる — 調査・実装は `haiku`、レビューは `sonnet` 以上
- Workflow ではスキル名を具体的に書く（例: `flow-tdd` スキルを読み込む）
- Best Practices には「しないこと」を必ず含める
