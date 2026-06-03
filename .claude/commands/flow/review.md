---
description: >-
  コードレビュー: $ARGUMENTS
  state.db で done のタスクを reviewer サブエージェントで一括並列にレビューし、指摘を review-fix タスクへ起票する。
argument-hint: <feature> [<task_id>]
---

# 指示

コードレビュー: $ARGUMENTS

`$ARGUMENTS` の引数の数で動作を切り替えること。引数が 0 個の場合はユーザーへフィーチャー名を確認すること。

- **引数 1 個（`<feature>`）**: 一括レビューモード。state.db で `done` のタスクをすべて `reviewer` で並列にレビューする。
- **引数 2 個（`<feature> <task_id>`）**: 単一タスクモード。指定タスクのみ `reviewer` でレビューする。
  (例: `user_auth task_1_1` → フィーチャー `user_auth`、タスク ID `task_1_1`)

コードの検査と指摘（`review-fix` タスク）の起票は `reviewer` 定義の責務に従って実行される（ここでは再指示しない）。

<workflow>

## 単一タスクモード

1. 引数からフィーチャー名とタスク ID を解釈する。
1. `reviewer` サブエージェントをタスク ID とフィーチャー名で 1 回起動する。
1. 判定（Approve / Warning / Block）と起票された `review-fix` タスクをユーザーへ報告する。

## 一括レビューモード

1. `.claude/skills/operate-sqlite/state_dao.py show --feature <feature>` で state.db を読み、
   状態が `done` のタスク ID（`task_<phase_num>_<task_num>` 形式）を抽出する。state.db が無ければ
   実行を中止し、`/flow:code <feature>` の先行実行をユーザーへ促す。
1. 抽出したタスク ID から `review-fix` タイプのタスクを除外する（無限ループ防止）。
   タスク種別は `Glob` で `.artifacts/features/<feature>/phases/**/task_*.md` を列挙して
   各ファイルのフロントマター `type` から判別する。判別が難しい場合は ID 名やタスク名からの推定でよい。
1. 残ったタスクが 0 件であればユーザーへその旨を報告して終了する。
1. **レビュー対象タスクすべてに対して、`reviewer` サブエージェントを単一メッセージ内で並列起動する**。
   各呼び出しの prompt は最小限にし、対象タスク ID・フィーチャー名と、仕様に書かれていない補足だけを渡す。
   `task_<phase_num>_<task_num>.md`・summaries/phase_<phase>.md・specification.md の内容を prompt へ複製しない（reviewer が自身で `Read` する）。
1. すべての `reviewer` 報告を集約し、ユーザーへサマリーを返す。報告内容には次を含める。
   - タスクごとの判定（Approve / Warning / Block）
   - 起票された `review-fix` タスクの ID 一覧
   - 重大度ごとの指摘件数
1. **Block が 1 件でも出た場合はその場で停止** し、ユーザーへ修正方針の指示を仰ぐ。
   ユーザーは `/flow:code <feature>` で `review-fix` タスクを実装したのち、
   再度 `/flow:review <feature>` を実行する想定。

</workflow>

<principles>

- **完了タスクのみレビューする**: state.db で `done` のタスクだけが対象。`in_progress` や `blocked` は
  実装が確定していないため対象外。
- **review-fix タスクは除外する**: review-fix 自体を再レビューすると指摘の指摘という無限ループを招く。
  対象から外す。
- **レビュー済みの再判定はしない**: 一度レビューしたタスクの履歴は持たない。フィーチャーの状況に応じて
  ユーザーが必要時に実行する想定。再レビューしたい場合もそのまま一括実行してよい。
- **並列起動は単一メッセージで行う**: 複数の `reviewer` 呼び出しを別々のメッセージに分けると逐次実行に
  なってしまう。必ず同一メッセージ内に複数の Agent 呼び出しを並べること。
- **Block 時は早期停止する**: ループ管理（最大 3 回までの反復）はメインで行うが、ユーザー判断を挟むため
  自動ループはせず、状況を集約してユーザーへ報告し指示を待つ。

</principles>
