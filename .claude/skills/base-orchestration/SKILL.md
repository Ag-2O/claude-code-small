---
name: base-orchestration
description: >-
  メインエージェントが機能開発フローを進行・調整・状態管理する際に参照する
  オーケストレーションのリファレンス。
  Thin Orchestrator の原則、フェーズ workflow、サブエージェント一覧を提供する。
  サブエージェントは参照不要。
user-invocable: false
---

# オーケストレーションコンテキスト

メインエージェントが従う、機能開発フローの進行・調整・状態管理のリファレンススキル。
メインは重い推論やコード生成を直接行わず、ユーザーとの対話・調整・状態管理に専念する
Thin Orchestrator として振る舞う。要件・設計・計画の対話はメインが担い、探索・精緻化・実装・
レビュー・検証・調査は専門サブエージェントへ委譲する。すべての状態と成果物は `.artifacts/` 配下に
永続化する。

各フェーズの具体的な手順は対応するスラッシュコマンド（`.claude/commands/flow/`）に定義する。
本スキルは全体像と横断原則を一元的に示す。

<principles>

- **状態起点で進める**: セッション開始時や作業再開時は、まず `operate-sqlite` スキルの `show`
  （`state_dao.py show --feature <feature>`）で現在地（フェーズ・進行中タスク・ブロッカー）を把握すること。
  状態は `.artifacts/state.db`（全フィーチャー共通の SQLite）に集約される。
- **state.db は CLI 経由で操作する**: タスク状態・現在フェーズ・ブロッカーの参照と更新は、
  `operate-sqlite` スキルの `state_dao.py`（`.claude/skills/operate-sqlite/SKILL.md`）を経由すること。
  SQLite ファイルを直接編集しない。`task_<phase_num>_<task_num>.md` も読み取り専用として扱う。
- **要決定事項はエスカレーションする**: サブエージェント（refiner / coder など）は仕様にない選択を自分で決めず、
  「要決定事項」として報告する。メインはそれを判断するか、必要に応じてユーザーへ確認し、決定を踏まえて
  当該サブエージェントを再度起動する（途中状態は保存せず、成果物と state.db から復元して再開する）。
- **サブエージェントの残作業はメインが代行しない**: サブエージェント（特に coder）の報告が途中で打ち切られたり、
  最終ステップ（サマリー追記・state.db 更新など）が未完了のまま戻った場合でも、メインがその作業を直接代行しないこと。
  同じタスク ID で当該サブエージェントを再起動して残作業を完結させる。サブエージェントは既存の成果物・summaries/phase\_<phase>.md・
  state.db から状況を復元して再開できる。これによりメインのコンテキスト消費を抑え、各エージェントの責務境界を保つ。
- **サブエージェントへの prompt は最小限にする**: 成果物（`task_<phase_num>_<task_num>.md`・`specification.md` 等）を
  読めば分かる内容を prompt 本文へ複製しないこと。渡すのは、タスク ID・フィーチャー名・対象成果物のパスと、
  成果物に書かれていない補足（メインが下した決定事項・並列実行時の注意など）だけにとどめる。
  prompt に仕様を二重に書くと、サブエージェントの入力コンテキストと出力トークンを圧迫し、
  報告が途中で打ち切られる原因になる。仕様の参照はサブエージェント自身の `Read` に委ねること。
- **Wave で並列実行する**: `plan.md` の依存関係を参照し、依存のない同一 Wave のタスクは複数の coder を並列で起動する。
  依存先の完了を state.db で確認してから後続 Wave を起動すること。
- **レビュー → 修正ループは 3 回まで**: `/flow:review` が Block を返したら修正タスクを実装し再レビューする。
  反復は最大 3 回までとし、解消しない場合は停止してユーザーへ相談すること。
- **検証で未達なら差し戻す**: `/flow:verify` が Fail を返したら、未達項目をギャップ修正タスクとして起票し
  修正フローへ戻す。

</principles>

<workflow>

機能開発はフェーズ順に進める。各フェーズには対応するスラッシュコマンドがある。

1. `/flow:explore <target>` — explorer がコードベースを分析し `project_architecture.md` を更新（着手前の前提把握）
1. `/flow:reqs <feature>` — メインがユーザーと対話し要件を明確化 → `requirements.md`
1. `/flow:spec <feature>` — メインが設計を詰める → `specification.md`
1. `/flow:plan <feature>` — メインがタスクを分解し依存関係と Wave を定義 → `plan.md`
1. `/flow:refine <feature>` — refiner が未精緻化タスクを精緻化 → `task_<phase_num>_<task_num>.md`
1. `/flow:code <feature> [<task_id>]` — coder が TDD で実装 → `summaries/phase_<phase>.md` 追記・state.db 記録
1. `/flow:review <feature> [<task_id>]` — reviewer が検査し指摘を `review-fix` タスクへ起票
1. `/flow:verify <feature>` — verifier が受け入れ検証 → `verification.md`

`/flow:research <topic>` は任意のフェーズで researcher を呼び、`research/[topic].md` に結果を蓄積する。
`/flow:troubleshoot <topic>` は任意のフェーズで troubleshooter を呼び、バグ・エラーの根本原因を診断して
`troubleshooting/[topic].md` に記録する（診断のみ。修正は別途 `/quick:code` か `/flow:code` で行う）。

</workflow>

## サブエージェント

| エージェント     | 役割             | 主な成果物                           |
| ---------------- | ---------------- | ------------------------------------ |
| `explorer`       | コードベース探索 | `.artifacts/project_architecture.md` |
| `refiner`        | タスク精緻化     | `task_<phase_num>_<task_num>.md`     |
| `coder`          | TDD 実装         | コード・`summaries/phase_<phase>.md` |
| `reviewer`       | コードレビュー   | `review-fix` タスク                  |
| `verifier`       | 受け入れ検証     | `verification.md`                    |
| `researcher`     | 調査             | `research/[topic].md`                |
| `troubleshooter` | バグ・エラー診断 | `troubleshooting/[topic].md`         |

呼び出し時は各コマンドの引数（フィーチャー名・タスク ID・調査トピック等）を必ず渡すこと。
引数が不足している場合は、実行前にユーザーへ確認すること。
