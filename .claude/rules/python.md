---
description: >-
  プロジェクトの Python コーディングスタイル: フォーマット、型ヒント、ドキュメント、
  命名規則、モダンな Python の書き方、およびインポートの整理方法。
paths: ['**/*.py', '**/*.pyi']
---

# Python コーディングガイドライン

## 1. 強制方法とこのルールの位置づけ

- フォーマットと lint の強制は `pyproject.toml` の Ruff（`select = ["ALL"]`）が機械的に行う。
  末尾カンマ・`Any` 禁止・型ヒントの付与・docstring・mutable デフォルト引数・bare except・
  import 順・`import *` 禁止・`is`/`==` の使い分けなどは Ruff が検出するため、本ルールでは再掲しない。
- プロジェクト固有の例外（無効化するルール）は `pyproject.toml` の `[tool.ruff.lint]` の
  `ignore` と `per-file-ignores` に集約する。判断はそちらを正とする。
- 本ルールは Ruff で機械的に測れない判断基準（命名の意図・設計方針・ドキュメントの粒度など）を補足する。
- 対象 Python バージョンは `pyproject.toml` の `requires-python`（現在 `>=3.13`）に従う。

## 2. 型ヒント

- 型は具体的に付ける。`Optional` / `Union` ではなく `X | None` のユニオン構文を使う。
- `Generator` や `Callable` などの抽象型は `collections.abc` からインポートする。
- 型エイリアスは `type` 文（3.12+）で定義する（例: `type UserId = str`）。
- シグネチャを保持するデコレータは `ParamSpec` で型付けする（`TypeVar(bound=Callable)` +
  `# type: ignore` は使わない）。

## 3. ドキュメント

- 公開 API（モジュール・クラス・公開関数）には docstring を必ず書く。
  メソッドや、内容が自明な短いプライベートヘルパーは 1 行要約でよい（省略も可）。
- docstring にはサマリー、引数、戻り値、送出するエラーを含める。
- **Google Style** または **NumPy Style** を使う。
- ドキュメントは **English** で書く。
- **Sphinx** 生成ドキュメントへそのまま使える粒度を目安とする。
- Claude Code のビルトイン指示（「コメントはデフォルトで書かない」）よりこのルールを優先する。

## 4. 命名規則

- 変数と関数は `snake_case` を使う（関数名は動詞で始める）。
- 定数は `UPPER_CASE`、クラスは `PascalCase` を使う。
- プライベートメンバー、および外部公開しないモジュールレベルの変数・定数・関数は `_` で始める
  （例: `_cache`、`_DEFAULT_TIMEOUT`、`_load_config()`）。
- モジュール外から利用する公開 API には `_` を付けない。公開範囲は `__all__` と import 方針で明示する。

## 5. モダンな Python スタイル

- 文字列整形は `%` フォーマットや `.format()` ではなく f-string を使う。
- パス操作は `os.path` ではなく `pathlib` を使う（Windows と Linux の両対応を考慮する）。
- 主にデータ保持を目的とするクラスには `@dataclass` を使う。
- 設定は専用の settings/config モジュールへ集約し、ビジネスロジック内で `os.environ` や
  `os.getenv` を直接読まない。
- ファイルが大きくなったら責務ごとにモジュールやクラスへ分割することを優先する。
  やむを得ず 1 ファイルに複数責務を同居させる場合のみ、`# region <name>` と `# endregion` で区切ってよい。

## 6. テスト

- テストフレームワークは `pytest` を主とし、モックには `unittest.mock`（`patch`・`MagicMock`）と
  `monkeypatch`、`pytest.fixture` を使う。
- パッチ専用の独自クラスや関数は作らない。
- ログ出力の検証には `caplog` を使う。
- カバレッジは statement（行）単位で測定する。
- テストコードにも Ruff のフォーマット・lint を適用する。

## 7. Hook エラー・警告対応（必須）

- Python ファイルを作成または編集した後は、PostToolUse で返る lint/format メッセージを必ず確認する。
- 対象ファイルが自分の編集範囲に含まれる場合、完了報告前に警告とエラーを修正する。
- 修正後は再確認し、問題 0 件を明示するか、残件理由を明示する。
- ユーザーが明示的に「修正不要」と言った場合だけ未修正で残し、その理由を報告に含める。
- 同じ問題が 3 回の修正で解消できない場合、停止して原因と次の対応をユーザーに確認する。
