# STATE.md 管理スクリプト

`state_tool.py` は、各フィーチャーの `.artifacts/features/<feature>/STATE.md`（現在地アンカー）への
構造的な書き込みを一手に担う決定論的 CLI である。確率的な LLM にフロントマターを直接編集させず、
このスクリプト経由で状態を更新することで、ファイル構造の破壊を防ぐ。

## 設計方針

- スクリプトが書き込む固定フォーマットのみをパースするため、外部ライブラリ（PyYAML 等）に依存しない。
- 状態を変更するたびに進捗率を再計算し、本文の進捗テーブルを自動再生成する。
- フロントマターの `tasks` ・`blockers` は手動編集せず、必ずこの CLI を経由すること。

## コマンド

カレントディレクトリがプロジェクトルートであることを前提とする。`--root` は既定で `.artifacts` を指す。
実行は `uv run` を経由すること。

```bash
# パスを変数に束ねておく
TOOL=.claude/scripts/state/state_tool.py

# 新規作成
uv run python $TOOL init --feature <feature>

# タスク状態の更新（status: todo / in_progress / blocked / done）
# タスク ID は `TASK_<phase_num>_<task_num>` 形式（例: TASK_1_1、TASK_2_3）。
uv run python $TOOL set-task --feature <feature> --task TASK_1_1 --status done

# 現在フェーズの更新
uv run python $TOOL set-phase --feature <feature> --phase phase_2

# ブロッカーの追加 / クリア
uv run python $TOOL add-blocker --feature <feature> --text "..."
uv run python $TOOL clear-blockers --feature <feature>

# 表示 / スキーマ検証
uv run python $TOOL show --feature <feature>
uv run python $TOOL validate --feature <feature>
```

## 利用者

- **coder**: タスク完了時に `set-task ... --status done` を実行する。
- **メインエージェント**: フェーズ遷移時の `set-phase`、ブロッカー記録、セッション開始時の `show` を実行する。
