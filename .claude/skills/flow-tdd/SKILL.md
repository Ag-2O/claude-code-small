---
name: flow-tdd
description: >
  TDD（RED → GREEN → REFACTOR）でフィーチャーを実装する際に使用する。
  フィーチャー名を引数として受け取る（例: `feature: user-authentication`）。
  plan_[feature_name].md を読み込み impl_[feature_name].md を生成する。
  flow-plan の後、flow-review の前に実行する。
  base-python などの言語スキルや base-django などのフレームワークスキルと組み合わせる。
user-invocable: false
allowed-tools: [Read, Write, Edit, Glob, Grep, Bash, TodoWrite]
---

# TDD 実装ワークフロー

このスキルは `coder` サブエージェントが従う実装ワークフローと TDD 方法論を定義する。

## セットアップ

フィーチャー名はスキルの引数として渡される。
フィーチャー名が指定されていない場合は、作業前に呼び出し元へ確認する。

> 「実装するフィーチャーの名前は何ですか？」

フィーチャー名が確定したら、以下のアーティファクトの存在を確認する。

- `.artifacts/plans/plan_[feature_name].md` — 存在しない場合は停止し、先に `/plan [feature_name]` を実行するよう呼び出し元へ伝える。
- `.artifacts/specifications/spec_[feature_name].md` — 存在しない場合は停止し、先に `/spec [feature_name]` を実行するよう呼び出し元へ伝える。

両ファイルが揃うまで実装を開始しない。

## ワークフロー

### Phase 1: 計画の読み込み

`Grep` / `Glob` で以下のファイルを読み込み、実装に必要な情報を把握する。

- `.artifacts/plans/plan_[feature_name].md` — 実装ステップ・フェーズ構成・受け入れ基準
- `.artifacts/specifications/spec_[feature_name].md` — データモデル・インターフェース仕様・テスト方針
- `.artifacts/reviews/review_[feature_name].md` — 最新レビューフィードバック（存在する場合）
- コードベース全体 — プロジェクトの命名規則・パターン・スタイル

`.claude/.works/research/*.md` が存在する場合は読み込み、調査結果を実装へ反映する。

### Phase 2: TDD で実装

- `.artifacts/plans/plan_[feature_name].md` で定義されたフェーズ順に従う
- 各ステップ完了後、次へ進む前に動作を検証する
- `.claude/rules/` および関連するスキルファイルの言語 / フレームワーク固有ルールに従う
- 以下の **TDD ステップ** セクションで定義されたサイクルに従う

`.artifacts/plans/plan_[feature_name].md` のスコープ内にとどめる。
定義されたスコープ外の変更や機能追加は行わない。

### Phase 3: 出力

`Read` で `./template.md` のテンプレートを読み込み、
`.artifacts/implementations/impl_[feature_name].md` を作成または更新する。

- ファイル名: `impl_[identifier].md`（例: `impl_user_auth.md`）
- `[identifier]` はフィーチャー名を小文字スネークケースに正規化する
- 同じフィーチャー名の場合は同一ファイルへ追記し、`Round` 番号をインクリメントする
- 新規フィーチャーの場合は新しいファイルを作成する

### Phase 4: 報告

実装した内容・変更ファイル・`.artifacts/implementations/impl_[identifier].md` に詳細を記録したことを呼び出し元へ報告する。
`/review [identifier]` の実行を促す。

## TDD ステップ

### Step 1: RED — 失敗するテストを書く

期待する振る舞いを記述したテストを書き、意図した理由で失敗することを確認する。
RED が確認されるまでプロダクションコードには触れない。

### Step 2: GREEN — 最小限の実装を書く

失敗しているテストをパスさせるために必要な実装だけを行う。再実行して GREEN を確認する。

### Step 3: REFACTOR — コードを改善する

重複を除去し、命名を改善し、最適化する — すべてのテストが GREEN のまま維持されること。

### Step 4: カバレッジ確認

カバレッジレポートを実行し、最低目標（80%）を達成していることを確認する。

## カバレッジ目標

- 最低目標: **80%** カバレッジ
- エッジケースと失敗シナリオを含める

## テスト種別

- **Unit**: 個々の関数を独立してテスト — 常に実施
- **Integration**: API エンドポイント・データベース操作 — 常に実施
- **E2E**: 重要な呼び出し元フロー — クリティカルパスのみ

## カバーすべきエッジケース

1. **Null / 未入力** の入力
1. **空** の配列や文字列
1. **無効な型**: 期待する型や形式外の値
1. **境界値**（最小 / 最大）
1. **エラーパス**（ネットワーク障害・外部サービスエラー）
1. **並行操作**（該当する場合のレースコンディション）

## 避けるべきアンチパターン

- 振る舞いではなく実装の詳細（内部状態）をテストする
- テスト同士が依存している（共有可変状態）
- 意味のある振る舞いを検証しないアサーション
- 外部依存（データベース・API・サービス）を分離しない

## Git チェックポイント（推奨）

- RED 検証後に `test:` コミット
- GREEN 検証後に `fix:` または `feat:` コミット
- クリーンアップ後に `refactor:` コミット

## 組み合わせルール

テストコマンド・構造・スタイルを言語に合わせるために、`base-python` などの関連する言語スキルと組み合わせる。
