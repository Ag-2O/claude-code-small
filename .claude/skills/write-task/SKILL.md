---
name: write-task
description: >-
  精緻化されたタスクやレビュー指摘を .artifacts/features/<feature>/phases/<phase>/TASK_<phase>_<n>.md へ書き込む時に使用する。
  アトミックなタスク仕様をテンプレートに沿って構造化する。refiner・reviewer サブエージェントが使用する。
user-invocable: false
allowed-tools: [Read, Write, Edit, Glob]
---

# TASK\_<phase>\_<n>.md 書き込みワークフロー

アトミックなタスク仕様を `.artifacts/features/<feature>/phases/<phase>/TASK_<phase_num>_<task_num>.md` へ
書き込む手順を定義する。refiner（精緻化タスク）と reviewer（レビュー指摘タスク）が使用する。

<workflow>

## 書き込み手順

1. `Read` で `./template.md` を読み込む。
1. 採番が未確定の場合は、`Glob` で `.artifacts/features/<feature>/phases/<phase>/TASK_*.md` を列挙し、
   当該 phase の最大 `<task_num>` + 1 を新タスクの番号として採用する。
1. タスク ID に対応するファイル名（例: `TASK_1_1.md`、`TASK_2_3.md`）で、
   `.artifacts/features/<feature>/phases/<phase>/` 配下に新規作成する。
   ファイル名・フロントマター `id`・本文見出しの ID は完全に一致させる。
1. テンプレートのセクション構成を維持し、フロントマターとタスク本体を埋める。
1. プレースホルダーはすべて実際の内容で置き換える。

## `type` フィールドの使い分け

- **impl**: refiner が生成する通常の実装タスク。
- **review-fix**: reviewer がレビュー指摘から生成する修正タスク。`depends_on` に対象タスクを記載する。

</workflow>

<principles>

- **タスクファイルは読み取り専用として扱う**: `TASK_<phase>_<n>.md` は coder へのプロンプトとして扱い、
  完了後も書き換えない。
- **完了状態は STATE.md に置く**: 完了状態は `TASK_<phase>_<n>.md` ではなく `STATE.md` に記録する
  （状態更新スクリプト経由）。STATE.md 上のタスク ID もファイル名と同じ `TASK_<phase>_<n>` 形式で揃える。
- **意味のある verify を指定する**: `<verify>` には単体テスト・型チェック・AST ベースのリンタなど
  意味のある手段を指定する。`grep -c` のような単純なテキストマッチングは避ける
  （コメントにマッチし、テストを通すための改ざんを招くため）。
- **採番衝突を避ける**: `Glob` で当該 phase の既存タスクファイルを列挙し、最大番号 + 1 を採番する。
  並列起票時に衝突した場合は、後発側がさらに次の番号へ繰り上げる。

</principles>
