---
name: write-task
description: >-
  精緻化されたタスクやレビュー指摘を .artifacts/features/<feature>/phases/<phase>/task_<phase_num>_<task_num>.md へ書き込む時に使用する。
  アトミックなタスク仕様をテンプレートに沿って構造化する。refiner・reviewer サブエージェントが使用する。
user-invocable: false
allowed-tools: [Read, Write, Edit, Glob]
---

# task\_<phase_num>\_<task_num>.md 書き込みワークフロー

アトミックなタスク仕様を `.artifacts/features/<feature>/phases/<phase>/task_<phase_num>_<task_num>.md` へ
書き込む手順を定義する。refiner（精緻化タスク）と reviewer（レビュー指摘タスク）が使用する。

## タスク命名規約

タスクファイルの命名と ID 規則は次のとおりとする。

- **ファイル名**: `.artifacts/features/<feature>/phases/<phase>/task_<phase_num>_<task_num>.md`
  （例: `phase_1/task_1_1.md`、`phase_2/task_2_3.md`）
- **タスク ID**: ファイル名の `task_<phase_num>_<task_num>` 部分をそのまま用いる
  （例: `task_1_1`、`task_2_3`）。state.db 上の ID もこの形式で揃える。
- **採番ルール**: タスク番号 `<task_num>` は phase ごとに `1` から開始する。
  別 phase であれば同じ番号を使ってよい（例: `task_1_1` と `task_2_1` は別タスク）。
- **review-fix の採番**: レビューで起票する `review-fix` タスクは、対象タスクと同じ phase の続番を割り当てる
  （例: `phase_1` で既存タスクが `task_1_5` まであれば、次の review-fix は `task_1_6`）。
- **採番の衝突回避**: 同 phase 内で並列に起票する場合は、既存ファイルを `Glob` で列挙してから最大番号 + 1 を採番する。
  万一衝突した場合は、後から起票する側がさらに次の番号へ繰り上げる。

<workflow>

## 書き込み手順

1. `Read` で `./template.md` を読み込む。
1. 採番が未確定の場合は、`Glob` で `.artifacts/features/<feature>/phases/<phase>/task_*.md` を列挙し、
   当該 phase の最大 `<task_num>` + 1 を新タスクの番号として採用する。
1. タスク ID に対応するファイル名（例: `task_1_1.md`、`task_2_3.md`）で、
   `.artifacts/features/<feature>/phases/<phase>/` 配下に新規作成する。
   ファイル名・フロントマター `id`・本文見出しの ID は完全に一致させる。
1. テンプレートのセクション構成を維持し、フロントマターとタスク本体を埋める。
1. プレースホルダーはすべて実際の内容で置き換える。

## `type` フィールドの使い分け

- **impl**: refiner が生成する通常の実装タスク。
- **review-fix**: reviewer がレビュー指摘から生成する修正タスク。`depends_on` に対象タスクを記載する。

</workflow>

<principles>

- **タスクファイルは読み取り専用として扱う**: `task_<phase_num>_<task_num>.md` は coder へのプロンプトとして扱い、
  完了後も書き換えない。
- **完了状態は state.db に置く**: 完了状態は `task_<phase_num>_<task_num>.md` ではなく `state.db` に記録する
  （`operate-sqlite` スキル経由）。state.db 上のタスク ID もファイル名と同じ `task_<phase_num>_<task_num>` 形式で揃える。
- **意味のある verify を指定する**: `<verify>` には単体テスト・型チェック・AST ベースのリンタなど
  意味のある手段を指定する。`grep -c` のような単純なテキストマッチングは避ける
  （コメントにマッチし、テストを通すための改ざんを招くため）。
- **採番衝突を避ける**: `Glob` で当該 phase の既存タスクファイルを列挙し、最大番号 + 1 を採番する。
  並列起票時に衝突した場合は、後発側がさらに次の番号へ繰り上げる。

</principles>
