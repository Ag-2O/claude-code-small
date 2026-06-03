---
name: write-plan
description: >-
  タスク計画を .artifacts/features/<feature>/plan.md へ書き込む時に使用する。
  plan-tasks で固めたフェーズ・タスク・依存関係・Wave をテンプレートに沿って構造化する。
  メインエージェントが直接使用する。
user-invocable: false
allowed-tools: [Read, Write, Edit]
---

# plan.md 書き込みワークフロー

タスク計画を `.artifacts/features/<feature>/plan.md` へ書き込む手順を定義する。

<workflow>

1. `Read` で `./template.md` を読み込む。
1. 既存の `.artifacts/features/<feature>/plan.md` があれば読み込み、更新箇所を特定する。
1. テンプレートのセクション構成・見出し・順序を維持し、`Write`（新規）または `Edit`（既存）で書き込む。
1. プレースホルダーはすべて実際の内容で置き換え、フロントマターの最終更新日を更新する。

</workflow>

<principles>

- **タスク粒度を記録する**: 各タスクには一意のタスク ID（`task_<phase_num>_<task_num>` 形式、
  例: `task_1_1`、`task_2_3`）、依存関係、想定規模（変更ファイル数・トークン量）を記録する。
- **Wave を明示する**: 依存関係から導いた Wave（並列実行グループ）を明示する。
- **責務を分ける**: plan.md はタスクの全体像と依存グラフを示すものとし、各タスクの詳細仕様は
  refiner が `task_<phase_num>_<task_num>.md` に展開する。
- **テンプレート構造を保つ**: テンプレートで定義されたセクションを追加・削除・並べ替えしない。
- **ファイル名と ID を対応させる**: タスク ID は後段の `task_<phase_num>_<task_num>.md` のファイル名と
  完全に一致させる（例: `task_1_1` → `task_1_1.md`）。
- **採番は phase ごとに 1 から**: タスク番号 `<task_num>` は phase ごとに `1` から開始する。

</principles>
