# task\_<phase_num>\_<task_num>.md テンプレート

`.artifacts/features/<feature>/phases/<phase>/task_<phase_num>_<task_num>.md` を以下の構成で作成する。
タスク本体は、情報境界を明確にするため XML タグで構造化する。
ファイル名およびフロントマターの `id` は `task_<phase_num>_<task_num>` 形式に統一する。
タスク番号は phase ごとに 1 から開始する（例: `phase_1` の最初は `task_1_1`、
`phase_2` の最初は `task_2_1`）。

````md
---
id: task_<phase_num>_<task_num>
feature: <feature_name>
phase: <phase>
type: impl
depends_on: []
---

# task_<phase_num>_<task_num>: <タスク名>

## 背景

[このタスクが必要な理由（WHY）と、関連する要件・設計への参照]

## タスク仕様

```xml
<task>
  <name>タスク名</name>
  <files>変更・新規作成するファイルのパス</files>
  <action>
    何をどう実装するか。
    使用するライブラリ・関数、避けるべきアプローチを具体的に記述する。
  </action>
  <verify>
    完了を判定する具体的な手段。
    例: pytest tests/unit/test_foo.py が pass する。
  </verify>
  <done>満たすべき最終状態</done>
</task>
```

## 受け入れ基準

- [ ] 基準 1
- [ ] 基準 2

## 補足

- [coder が知っておくべき制約・前提・注意点]
````

## フィールドの説明

- **id**: ファイル名と一致する `task_<phase_num>_<task_num>` 形式（例: `task_1_1`、`task_2_3`）。
- **type**: `impl`（通常の実装）または `review-fix`（レビュー指摘の修正）。
- **depends_on**: 先行して完了している必要があるタスク ID の配列（例: `[task_1_1, task_1_2]`）。
- **verify**: 単体テスト・型チェック・リンタなど意味のある手段を指定する。`grep -c` は使わない。

## 採番ルール

- タスク番号は phase ごとに `1` から開始する。別 phase であれば同じ番号を使ってよい。
- `review-fix` タスクは対象タスクと同じ phase の続番を割り当てる
  （例: `phase_1` で既存の最大番号が `task_1_5` なら、次の `review-fix` は `task_1_6`）。
- 採番前に `Glob` で `.artifacts/features/<feature>/phases/<phase>/task_*.md` を列挙し、
  当該 phase の最大番号 + 1 を採用する。
