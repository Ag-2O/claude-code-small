---
name: write-summary
description: >-
  実装サマリーを .artifacts/features/<feature>/SUMMARY.md へ追記する時に使用する。
  タスクごとに変更内容・設計判断・テスト結果を記録し、verifier の入力とする。coder サブエージェントが使用する。
user-invocable: false
allowed-tools: [Read, Write, Edit]
---

# SUMMARY.md 書き込みワークフロー

実装サマリーを `.artifacts/features/<feature>/SUMMARY.md` へ追記する手順を定義する。
SUMMARY.md はタスクごとの実装内容を時系列で蓄積し、verifier の受け入れ検証の入力となる。

<workflow>

1. `Read` で `./template.md` を読み込む。
1. `.artifacts/features/<feature>/SUMMARY.md` が存在しない場合は、テンプレートのヘッダ部分で新規作成する。
1. 既存ファイルがある場合は、末尾にタスク単位のエントリを **追記** する（既存エントリは書き換えない）。
1. プレースホルダーはすべて実際の内容で置き換える。

</workflow>

<principles>

- **1 タスク 1 エントリ**: タスク ID を見出しに含めて識別可能にする。
- **WHY を残す**: 「何を変更したか」だけでなく「なぜそう判断したか」（設計判断・仕様からの逸脱）を残す。
- **テスト結果を記録する**: コマンド・カバレッジ・ケース数を記録する。
- **スコープ外を明示する**: 残した点があれば、その理由とともに明記する。
- **追記専用とする**: SUMMARY.md は追記のみとし、過去のエントリは改変しない。
- **完了状態は STATE.md に置く**: `done` / `in_progress` の状態は SUMMARY.md ではなく STATE.md で管理する。

</principles>
