---
name: write-summary
description: >-
  実装サマリーを .artifacts/features/<feature>/summaries/phase_<phase>.md へ追記する時に使用する。
  フェーズ単位のファイルにタスクごとの変更内容・設計判断・テスト結果を記録し、verifier の入力とする。
  coder サブエージェントが使用する。
user-invocable: false
allowed-tools: [Read, Write, Edit]
---

# 実装サマリー書き込みワークフロー

実装サマリーを `.artifacts/features/<feature>/summaries/phase_<phase>.md` へ追記する手順を定義する。
サマリーはフェーズごとに 1 ファイルへまとめ、そのフェーズに属するタスクの実装内容を時系列で蓄積する。
verifier の受け入れ検証の入力となる。

<workflow>

1. `Read` で `./template.md` を読み込む。
1. タスク ID（`task_<phase>_<task_no>`）から所属フェーズ番号を取り出し、書き込み先を
   `.artifacts/features/<feature>/summaries/phase_<phase>.md` に決定する。
1. 対象のフェーズサマリーが存在しない場合は、テンプレートのヘッダ部分で新規作成する。
1. 既存ファイルがある場合は、末尾にタスク単位のエントリを **追記** する（既存エントリは書き換えない）。
1. プレースホルダーはすべて実際の内容で置き換える。

</workflow>

<principles>

- **フェーズ単位でまとめる**: サマリーはフェーズごとに 1 ファイルとし、同一フェーズのタスクは同じファイルへ追記する。
- **1 タスク 1 エントリ**: タスク ID を見出しに含めて識別可能にする。
- **WHY を残す**: 「何を変更したか」だけでなく「なぜそう判断したか」（設計判断・仕様からの逸脱）を残す。
- **テスト結果を記録する**: コマンド・カバレッジ・ケース数を記録する。
- **スコープ外を明示する**: 残した点があれば、その理由とともに明記する。
- **追記専用とする**: フェーズサマリーは追記のみとし、過去のエントリは改変しない。
- **完了状態は state.db に置く**: `done` / `in_progress` の状態はサマリーではなく `state.db` で管理する
  （`operate-sqlite` スキル経由で更新する）。

</principles>
