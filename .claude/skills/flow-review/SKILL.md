---
name: flow-review
description: >
  コード変更・プルリクエスト・staged/unstaged diff を対象に、
  欠陥・デグレ・セキュリティリスク・テスト漏れをレビューする際に使用する。
  flow-tdd の後に実行する。
  base-python などの言語スキルや base-django などのフレームワークスキルと組み合わせる。
user-invocable: false
allowed-tools: [Read, Glob, Grep, Bash]
---

# コードレビューワークフロー

このスキルは `reviewer` サブエージェントが従うレビューワークフローを定義する。

## ワークフロー

### Phase 1: 変更内容の把握

- `git diff` を実行して変更ファイルと差分を確認する（取得できない場合もある）
- `.artifacts/specifications/spec_[feature_name].md` と `.artifacts/plans/plan_[feature_name].md` が存在する場合は読み込み、意図した実装からの逸脱を検出する
- identifier（ステップ名またはイシューのサマリーを小文字スネークケースにしたもの）を決定し、対応する `.artifacts/implementations/impl_[identifier].md` を読み込む
- `impl_[identifier].md`（実装詳細・テスト結果・ラウンド履歴）が実際のコード差分と一致しているか検証する
- `Grep` / `Glob` で関連する既存コードを確認し、プロジェクト全体への影響を把握する

### Phase 2: 静的解析の実行

プロジェクトで利用可能なすべてのツールを実行する。

```bash
git diff --name-only HEAD~1
```

言語固有の静的解析コマンドは `.claude/rules/` および該当する言語スキルを参照する。

### Phase 3: レビュー

`reviewer` エージェントの重大度ガイドに従い、優先度順に問題を検出する。
CRITICAL の問題が見つかった場合は即座に報告し、継続するか確認する。

実装が `impl_[identifier].md` で定義されたスコープ・除外事項・テスト方針の範囲内に収まっているか必ず確認する。

### Phase 4: 出力

`./template.md` のテンプレートに従い、`.artifacts/reviews/review_[identifier].md` を作成または更新する。

- ファイル名: `review_[identifier].md`（例: `review_user_auth.md`）
- identifierの候補が渡された場合はそれを `[identifier]` として使用する
- `impl_[identifier].md` と同じ命名規則（小文字スネークケース）を使用する
- 同じidentifierの場合は同一ファイルへ追記し、`Round` をインクリメントして履歴を保持する
- ラウンド番号は対応する `.artifacts/implementations/impl_[identifier].md` と一致させる

### Phase 5: 報告

判定結果をサマリーとして呼び出し元へ報告する（承認は不要）。

## 組み合わせルール

言語固有のチェックを適用するために、`base-python` などの関連する言語スキルと組み合わせる。
