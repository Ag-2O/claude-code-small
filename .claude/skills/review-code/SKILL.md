---
name: review-code
description: >-
  coder が実装したコードをレビューする時に使用する。
  セキュリティ・品質・テスト・アーキテクチャの観点で検査し、重大度ガイドに基づき承認可否を判断する。
  reviewer サブエージェントが使用する。
user-invocable: false
allowed-tools: [Read, Glob, Grep, Bash]
---

# コードレビューワークフロー

`reviewer` サブエージェントが従うレビュープロセスと重大度ガイドを定義する。
コードの修正は行わず、検査・判定・指摘の整理のみを担当する。

<workflow>

## フェーズ 1: 変更内容の把握

- `git diff` で変更ファイルと差分を確認する（取得できない場合もある）。
- 対象の `.artifacts/features/<feature>/phases/<phase>/TASK_<phase_num>_<task_num>.md` を読み込み、
  実装が仕様の範囲内かを把握する。
- `.artifacts/features/<feature>/SUMMARY.md` の該当タスクエントリを読み、
  実装内容・設計判断と実際の差分が一致するか検証する。
- `.artifacts/features/<feature>/SPECIFICATION.md` と必要に応じて `.artifacts/ARCHITECTURE.md` を参照し、
  設計からの逸脱を検出する。
- `Grep` / `Glob` で関連する既存コードを確認し、プロジェクト全体への影響を把握する。

## フェーズ 2: 静的解析の実行

プロジェクトで利用可能な静的解析・テストを実行する。
言語固有のコマンドは `.claude/rules/` と該当する言語スキルを参照する。

## フェーズ 3: レビュー

後述の「重大度ガイド」に従い、優先度順に問題を検出する。
実装が `TASK_<phase>_<n>.md` のスコープ・検証ゲート・受け入れ基準の範囲内に収まっているか
必ず確認する。

## フェーズ 4: 完了の扱い

指摘の整理と判定（Approve / Warning / Block）まで、および起票すべき `review-fix` 指摘内容
（対象・重大度・`depends_on`）の整理までが本スキルの責務とする。
修正タスクの起票（ファイル作成）と呼び出し元への報告は本スキルでは行わず、
呼び出し元（`reviewer` エージェント定義）が担う。

</workflow>

## 重大度ガイド

### CRITICAL — セキュリティ

- **Injection**: SQL / コマンド / テンプレートインジェクション。
- **Path traversal**: ユーザー入力をそのままファイルパスに使用。
- **Hardcoded secrets**: API キー・パスワード・トークンの埋め込み。
- **Dangerous functions**: 未検証入力を `eval` / `exec` へ渡す。
- **Unsafe deserialization**: 信頼できないデータの直接デシリアライズ。
- **Weak cryptography**: セキュリティ用途での MD5 / SHA1 使用。
- **Sensitive data exposure**: ログへの機密出力、内部エラー詳細のエンドユーザー返却。

### CRITICAL — エラーハンドリング

- **Swallowed exceptions**: 空の `catch` / `except` で握りつぶし。
- **Ignored errors**: 失敗を検知しても未対処。
- **Unreleased resources**: コンテキストマネージャ / `finally` なしのリソース確保。

### HIGH — コード品質

- **Oversized functions**: 約 50 行超、または引数 5 個超。
- **Deep nesting**: ネスト 4 段超。
- **Duplicated logic**: 同一ロジックの重複。
- **Magic numbers**: 説明のない数値・文字列リテラル。
- **Mutable default arguments**: デフォルト引数に可変オブジェクト。

### HIGH — アーキテクチャ

- **Layer violations**: 依存方向が想定アーキテクチャから逸脱（例: ドメイン層がインフラ層へ依存）。
- **Mixed responsibilities**: 1 つの関数 / クラスが複数責務を持つ。
- **Missing authorization checks**: 重要操作で実行者のロール・所有権確認がない。
- **Missing rate limiting**: 外部公開エンドポイントにリクエスト制限がない。

### HIGH — テスト

- **Missing tests**: 新規ロジックに対応するテストがない。
- **Happy path only**: 正常系のみで異常系・境界値のテストがない。
- **Test interdependence**: テスト間で可変状態を共有。

### MEDIUM — 保守性

- **Unclear naming**: 名前から意図を読み取れない。
- **Stale comments**: 現在のコードと矛盾するコメント。
- **Dead code**: 未使用の変数・関数・import。
- **Insufficient logging**: 重要な処理経路でログ不足。

<examples>

代表的なパターンを以下に示す。実コードと照らし合わせる際の判断基準として用いる。

<example>

**カテゴリ**: CRITICAL — セキュリティ（SQL Injection）

**Bad**:

```python
def get_user(user_id: str) -> dict:
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    return db.execute(query).fetchone()
```

**Good**:

```python
def get_user(user_id: str) -> dict:
    query = "SELECT * FROM users WHERE id = %s"
    return db.execute(query, (user_id,)).fetchone()
```

**判定理由**: ユーザー入力を文字列補間で SQL に埋め込んでいる。CRITICAL として Block する。
パラメータバインディングへの置き換えを `review-fix` で起票する。

</example>

<example>

**カテゴリ**: CRITICAL — エラーハンドリング（Swallowed exceptions）

**Bad**:

```python
def fetch_config() -> dict:
    try:
        return json.loads(Path("config.json").read_text())
    except Exception:
        return {}
```

**Good**:

```python
def fetch_config() -> dict:
    try:
        return json.loads(Path("config.json").read_text())
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        logger.warning("config load failed: %s", exc)
        return {}
```

**判定理由**: 例外を握りつぶしており、設定ロードの失敗が検知できない。CRITICAL として Block する。
具体的な例外型での捕捉とログ出力を求める。

</example>

<example>

**カテゴリ**: HIGH — コード品質（Magic numbers）

**Bad**:

```python
def calculate_fee(amount: int) -> int:
    if amount > 10000:
        return amount * 3 // 100
    return amount * 5 // 100
```

**Good**:

```python
_HIGH_AMOUNT_THRESHOLD = 10000
_HIGH_AMOUNT_FEE_RATE = 3
_STANDARD_FEE_RATE = 5
_PERCENT = 100


def calculate_fee(amount: int) -> int:
    rate = _HIGH_AMOUNT_FEE_RATE if amount > _HIGH_AMOUNT_THRESHOLD else _STANDARD_FEE_RATE
    return amount * rate // _PERCENT
```

**判定理由**: 閾値・料率・分母の意味がコードから読み取れない。HIGH として指摘し、定数抽出を求める。

</example>

<example>

**カテゴリ**: HIGH — テスト（Missing tests）

**Bad**: 新規追加された `discount_for(user)` 関数に対応するテストがない。

**Good**: `tests/unit/test_discount.py` に、通常会員・プレミアム会員・期限切れ会員の 3 ケースを含む
テストが追加されており、いずれも `uv run pytest` で pass する。

**判定理由**: 新規ロジックに対応するテストが欠落している。HIGH として Block する。
テスト追加タスクを `review-fix` で起票する。

</example>

<example>

**カテゴリ**: MEDIUM — 保守性（Stale comments）

**Bad**:

```python
def normalize(value: str) -> str:
    # 全角スペースを半角に変換する
    return value.lower().strip()
```

**Good**:

```python
def normalize(value: str) -> str:
    return value.lower().strip()
```

**判定理由**: コメントの記述と実装が一致していない。MEDIUM として Warning とし、
コメントの削除または正しい記述への修正を求める（実装の変更は不要）。

</example>

</examples>

## 判定基準

すべての判定に共通の条件: ブランチカバレッジ 80% 以上（未満は Block）。

| 判定        | 条件                                                |
| ----------- | --------------------------------------------------- |
| **Approve** | CRITICAL / HIGH / MEDIUM の指摘がない               |
| **Warning** | CRITICAL / HIGH はないが MEDIUM がある              |
| **Block**   | CRITICAL または HIGH がある、もしくはカバレッジ不足 |

<principles>

- **確信度の高い指摘に絞る**: 目安 80% 以上。スタイル指摘より挙動上の欠陥を優先する。
- **同根の指摘はまとめる**: 同じ根本原因の重複指摘は 1 件に統合する。
- **言語スキルと組み合わせる**: 言語固有のチェックを適用するため、`base-python` などの
  関連する言語スキルと併用する。

</principles>
