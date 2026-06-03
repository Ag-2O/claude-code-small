# 実装サマリーテンプレート

新規作成時は、以下のヘッダで `.artifacts/features/<feature>/summaries/phase_<phase>.md` を作成する。

```md
---
feature: <feature_name>
phase: phase_<phase_num>
last_updated: YYYY-MM-DD
---

# 実装サマリー: <feature_name> / phase_<phase_num>

このファイルはフェーズ <phase_num> に属するタスク単位の実装内容を時系列で蓄積する。各エントリは追記専用とする。
```

既存ファイルには、タスクごとに以下のエントリを末尾へ追記する。

```md
## task_<phase_num>_<task_num>: <タスク名>

### 変更ファイル

- `src/foo/bar.py` — 新規作成: XXX を実装
- `tests/unit/test_bar.py` — 新規作成: bar.py の単体テスト

### 実装内容

- 構築したものの説明。

### 設計判断

- このアプローチを選んだ理由。仕様からの逸脱や追加があれば記載する。

### 対処したエッジケース

- 対応した例外や境界条件。

### テスト結果

- **コマンド**: `[テストコマンド]`
- **カバレッジ**: xx%
- **ハッピーパス**: [N] ケース / すべてパス
- **エラーケース**: [N] ケース / すべてパス

### スコープ外 / 残課題

- [対処しなかった内容とその理由]
```
