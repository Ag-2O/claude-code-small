---
name: base-python
description: >-
  Python（3+、pyproject の requires-python に従う）コードの実装・リファクタリング・
  デバッグ・テスト・レビュー時に使用する。
  プロジェクト構造、コーディングスタイル、パッケージ管理のリファレンスを提供する。
user-invocable: false
---

# Python 言語コンテキスト

ワークスペースの Python 固有のコンテキストを一元管理するリファレンススキル。
パッケージマネージャー・コーディングスタイル・テスト規約への参照を提供する。

## 参照ファイル

参照ファイルとその読み込みタイミングを次に示す。`standard` と `testing` は常に必要。
PyTorch を使うプロジェクトでのみ `pytorch` を追加する。

| 種別                   | キー       | パス                   | 読み込みタイミング                                    |
| ---------------------- | ---------- | ---------------------- | ----------------------------------------------------- |
| パッケージマネージャー | `uv`       | `./managers/uv.md`     | すべての Python プロジェクト — 常に適用。             |
| スタイル               | `standard` | `./styles/standard.md` | すべての Python ソースファイル — 常に適用。           |
| スタイル               | `testing`  | `./styles/testing.md`  | `tests/` 以下のすべてのテストファイル — 常に適用。    |
| スタイル               | `pytorch`  | `./styles/pytorch.md`  | 機械学習・深層学習で PyTorch を使用するプロジェクト。 |

新規プロジェクトおよびすでに `uv` を使用しているプロジェクトでは `uv` をデフォルトとする。
`uv` がインストールできないレガシー環境のみ `venv` + `requirements.txt` にフォールバックする。

## format と lint の実行

フォーマットと lint は以下の手順で実行する。

```bash
uv run ruff format <対象>        # 整形（lint の前に実行）
uv run ruff check --fix <対象>   # 自動修正できる違反を解消
uv run ruff check <対象>         # 残存違反を確認し、0 件になるまで手で修正
```

対象は**自分が作成・編集したファイルに限定する**（例: `uv run ruff check src/<package>/foo.py tests/test_foo.py`）。
