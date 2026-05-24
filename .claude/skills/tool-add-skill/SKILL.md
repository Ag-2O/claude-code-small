---
name: tool-add-skill
description: >-
  新しいスキルを作成する際に使用する。
  スキルの種類（base/flow/tool）を判定し、テンプレートに従って
  SKILL.md と template.md を生成し、システムに登録する。
user-invocable: false
allowed-tools: [Read, Write, Glob, Grep]
---

# スキル追加ワークフロー

このスキルは、プロジェクトに新しいスキルを追加するプロセスを定義する。

## スキルの種類

- `base-` — 言語・ツールのスタイルや構造リファレンス
  （例: `base-python`, `base-docker`）
- `flow-` — 開発ワークフロー定義
  （例: `flow-req`, `flow-spec`, `flow-plan`）
- `tool-` — 調査・生成などの汎用ユーティリティ
  （例: `tool-research`, `tool-add-skill`）

## フェーズ 1: 要件の把握

スキル名とスキルの目的が渡されていない場合は確認する。
また、今までの会話の中で、スキルの必要性や目的が明確になっているかを確認する。

- **スキル名**: `[prefix]-[name]` 形式（例: `base-fastapi`, `flow-deploy`, `tool-lint`）
- **スキルの目的**: どんなタスクで呼び出されるか？
- **入力**: 呼び出し元から受け取る情報（フィーチャー名・ファイルパス・引数など）
- **出力**: 生成または更新するファイルやレポート

## フェーズ 2: 既存スキル参照

`.claude/skills/` の一覧を確認し、同種のスキルを読み込んで構造を把握する。

- `base-*` を作る場合: `base-python/SKILL.md` を参照
- `flow-*` を作る場合: `flow-req/SKILL.md` を参照
- `tool-*` を作る場合: `tool-research/SKILL.md` を参照

同名・類似スキルが既に存在する場合は、新規作成ではなく既存スキルの更新を提案する。

## フェーズ 3: SKILL.md の作成

`./template.md` を読み込み、`.claude/skills/[skill-name]/SKILL.md` を作成する。

### フロントマター

```yaml
---
name: [skill-name]
description: >
  このスキルを使用するタイミングと目的を 2〜3 文で説明する。
  入力・出力が明確な場合はここに記述する。
user-invocable: false
---
```

スキルはすべてエージェント専用。ユーザーが直接呼び出す場合は `.claude/commands/` または `.github/prompts/` 経由とする。

### ボディ構造

スキルの種類に応じて記述スタイルを選択する。

- **base-**\*: 参照ファイルのテーブル + 読み込みタイミング +
  組み合わせルール + 補足（任意）
- **flow-**\*: フェーズ番号付きのワークフロー（フェーズ 1 〜 N）
- **tool-**\*: フェーズ番号付きのワークフロー（フェーズ 1 〜 N）

## フェーズ 4: template.md の作成

スキルが出力ドキュメントを生成する場合は `.claude/skills/[skill-name]/template.md` を作成する。

出力形式が自明な場合（コード生成のみ・既存ファイル編集のみ）は省略可。

テンプレートのプレースホルダーは `[square_brackets]` で統一する。

## ベストプラクティス

- description は「いつ使うか」を明確に書く — 呼び出し判断の根拠になる
- フェーズは独立性を保つ — 各フェーズが前フェーズの出力を入力とする形にする
- 参照先ファイルは相対パスで書く（`./structures/script.md` など）
- スキルはすべて `user-invocable: false` を付ける — ユーザー向け呼び出しは `.claude/commands/` または `.github/prompts/` で定義する
