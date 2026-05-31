---
description: >-
  実装: $ARGUMENTS
  PLANS.md の Wave 順に未完了タスクを coder サブエージェントで TDD 実装し、完了を STATE.md へ記録する。
argument-hint: <feature> [<task_id>]
---

# 指示

実装: $ARGUMENTS

`$ARGUMENTS` の引数の数で動作を切り替えること。引数が 0 個の場合はユーザーへフィーチャー名を確認すること。

- **引数 1 個（`<feature>`）**: Wave モード。PLANS.md の Wave 順に未完了タスクを `coder` で並列実行する。
- **引数 2 個（`<feature> <task_id>`）**: 単一タスクモード。指定タスクのみ `coder` で実装する。
  (例: `user_auth TASK_1_1` → フィーチャー `user_auth`、タスク ID `TASK_1_1`)

TDD 実装・成果物の記録（SUMMARY 追記・STATE 記録）・報告は `coder` 定義の責務に従って実行される（ここでは再指示しない）。

<workflow>

## 単一タスクモード

1. 引数からフィーチャー名とタスク ID を解釈する。
1. `coder` サブエージェントをタスク ID とフィーチャー名で 1 回起動する。
   prompt は最小限にし、タスク ID・フィーチャー名・対象 `TASK_<phase>_<n>.md` のパスと、
   仕様に書かれていない補足（メインの決定事項など）だけを渡す。
   `TASK_<phase>_<n>.md` や SPECIFICATION.md の内容を prompt 本文へ複製しない（coder が自身で `Read` する）。
1. 実装完了後、`reviewer` によるレビュー（`/flow:review <feature> <task_id>`）を促す。

## Wave モード

1. `.artifacts/features/<feature>/PLANS.md` を `Read` で読み、「Wave（並列実行グループ）」セクションから
   Wave とその構成タスク ID を抽出する。`PLANS.md` が存在しない場合は実行を中止し、
   `/flow:plan <feature>` の先行実行をユーザーへ促す。
1. `.claude/scripts/state/state_tool.py show --feature <feature>` で STATE.md を読み、
   各タスクの状態を取得する。STATE.md が無ければ
   `uv run python .claude/scripts/state/state_tool.py init --feature <feature>` で初期化する。
1. `Glob` で `.artifacts/features/<feature>/phases/**/TASK_*.md` を列挙し、精緻化済みのタスク ID 集合を得る。
1. Wave を番号順に **1 つずつ** 処理する。各 Wave で次を行う。
   1. その Wave に属するタスクから、状態が `done` でないものを「Wave 内未完了タスク」として選ぶ。
   1. **未完了タスクのうち `TASK_<phase>_<n>.md` が未生成のもの**があれば、その Wave 開始前に停止し、
      `/flow:refine <feature>` の実行をユーザーへ促す。
   1. Wave 内未完了タスクすべてに対して、`coder` サブエージェントを**単一メッセージ内で並列起動**する。
      各呼び出しの prompt は最小限にし、対象タスク ID（`TASK_<phase_num>_<task_num>` 形式）・フィーチャー名・
      対象 `TASK_<phase>_<n>.md` のパスと、仕様に書かれていない補足だけを渡す。
      `TASK_<phase>_<n>.md` や SPECIFICATION.md の内容を prompt へ複製しない（coder が自身で `Read` する）。
   1. すべての `coder` 報告を集約する。1 つでも以下のいずれかに該当する場合は **その場で停止** し、
      これまでの結果（成功タスク・失敗タスク・要決定事項）をユーザーへ報告して指示を仰ぐ。
      - `coder` がエラー・実装失敗を報告
      - `coder` が「要決定事項」を含んだ報告を返した
      - STATE.md 上の該当タスク状態が `done` 以外（`blocked` 等）で確定した
      - `coder` の報告が途中で途切れて完了ステップ（SUMMARY 追記・STATE 更新）が未確認の場合は、
        メインで残作業を代行せず、同じタスク ID で `coder` を再起動する
        （`coder` は既存の成果物と STATE.md から状況を復元して再開する）
   1. Wave 内のすべてのタスクが `done` であることを `state_tool.py show` で確認してから次の Wave へ進む。
1. すべての Wave が完了したら、`/flow:review <feature>` の実行をユーザーへ促す。

</workflow>

<principles>

- **Wave をまたがず順序を守る**: 次の Wave は前の Wave のすべてのタスクが `done` になってから着手する。
  依存関係を壊さないため、Wave をスキップしたり混在させない。
- **同一 Wave 内は並列で起動する**: 同一 Wave のタスクは互いに独立しているため、`coder` 呼び出しは
  単一メッセージ内に複数並べて並列に起動する。別メッセージに分けると逐次実行になる。
- **障害時は早期に停止する**: 失敗・要決定事項・blocked が出たら後続 Wave を起動せず、状況を集約して
  ユーザーへ報告する。要決定事項は判断後、該当タスクのみ単一タスクモードで再実装させる。
- **状態は STATE.md を真とする**: 完了判定は `state_tool.py show` の結果に従う。`coder` の口頭報告だけで
  「完了したつもり」にしない。
- **残作業はメインが代行しない**: `coder` の報告が途中で途切れた、または完了ステップが未実施で戻った場合、
  メインで代わりに完結させず、同じタスク ID で `coder` を再起動する。
  メインのコンテキスト消費を抑え、各エージェントの責務境界を保つため。
- **レビューは別フェーズに分ける**: `/flow:code` は実装のみを担当し、`reviewer` の起動は行わない。
  レビューはユーザーが `/flow:review` を別途実行する。

</principles>
