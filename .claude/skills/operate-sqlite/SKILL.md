---
name: operate-sqlite
description: >-
  ワークフローの状態を共有 SQLite データベース .artifacts/state.db で読み書きする時に使用する。
  フィーチャーの現在フェーズ・タスク状態・進捗・ブロッカーを決定論的な CLI 経由で操作する。
  メインエージェントと coder・reviewer 系のフローが状態の参照・更新に使用する。
user-invocable: false
allowed-tools: [Bash, Read]
---

# state.db 操作ワークフロー

ワークフローの状態は、`.artifacts/state.db`（全フィーチャー共通の単一 SQLite データベース）で管理する。
確率的な LLM に生の状態を直接編集させず、同梱の決定論的 CLI（`state_dao.py`）を唯一の窓口として
読み書きすること。CLI が書き込む固定スキーマのみを扱うため、構造の破壊を防げる。

<principles>

- **状態は必ず CLI 経由で更新する**: タスク状態・現在フェーズ・ブロッカーの更新は `state_dao.py` を経由する。
  SQLite ファイルを手で開いて書き換えたり、`sqlite3` で直接 `UPDATE` / `INSERT` しないこと。
- **進捗は保存しない**: 進捗率は `tasks` から都度算出する。進捗を表す列や成果物は持たない。
- **タスク ID は `task_<phase>_<task_no>` 形式**: 例 `task_1_1`、`task_2_3`。CLI 内部で `phase` 列と
  `task_no` 列へ分解して保存するため、フェーズ単位の抽出が容易（`list-tasks --phase phase_1` など）。
- **`set-task` の前に `init` が要る**: 未初期化のフィーチャーに対する更新はエラー（終了コード 2）になる。
  セッション開始時や作業再開時は、まず `show` で現在地（フェーズ・タスク状態・ブロッカー）を把握すること。
- **`state_dao.py` の実装は参照しない**: `state_dao.py` は CLI として `uv run` 経由で呼び出すだけにとどめ、
  ソースコードを `Read` で読み込まないこと。必要な操作はすべて本スキルに記載のサブコマンドで完結する。
  ソースを読むとコンテキストを無駄に消費するため、インターフェース（サブコマンドと引数）のみを参照する。

</principles>

<workflow>

カレントディレクトリがプロジェクトルートであることを前提とする。`--root` は既定で `.artifacts` を指し、
データベースは `<root>/state.db` に置かれる。実行は `uv run` を経由すること。

```bash
# スクリプトパスを変数に束ねておく
DAO=.claude/skills/operate-sqlite/state_dao.py

# フィーチャーの初期化（DB とスキーマも自動作成。冪等）
uv run python $DAO init --feature <feature> [--phase phase_1]

# タスク状態の更新（status: todo / in_progress / blocked / done）
uv run python $DAO set-task --feature <feature> --task task_1_1 --status done

# 現在フェーズの更新（phase_2 でも 2 でも可）
uv run python $DAO set-phase --feature <feature> --phase phase_2

# ブロッカーの追加 / 全クリア
uv run python $DAO add-blocker --feature <feature> --text "..."
uv run python $DAO clear-blockers --feature <feature>

# 現在地の表示（人間可読なテーブルを出力）
uv run python $DAO show --feature <feature>

# タスク ID の列挙（status / phase で絞り込み可。1 行 1 ID）
uv run python $DAO list-tasks --feature <feature> [--status done] [--phase phase_1]

# スキーマ検証（フィーチャーの存在と状態値の妥当性）
uv run python $DAO validate --feature <feature>
```

</workflow>

## 利用者

- **coder**: タスク完了時に `set-task ... --status done` を実行する。
- **メインエージェント**: フェーズ遷移時の `set-phase`、ブロッカー記録、セッション開始時の `show`、
  Wave 進行時の完了確認（`show` / `list-tasks --status done`）を実行する。
- **レビュー / 検証フロー**: `list-tasks --feature <feature> --status done` で対象タスクを抽出する。
