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

対象 Python バージョンは `pyproject.toml` の `requires-python`（現在 `>=3.13`）に従う。
バージョン数値の真実源は `pyproject.toml` とし、本スキルでは個別に固定しない。

## ルールとの関係

コーディング規範（守るべきルール）の正は `.claude/rules/python.md` とする。
`rules/python.md` は `**/*.py` へ自動適用される規範チェックリストであり、
強制自体は `pyproject.toml` の Ruff（`select = ["ALL"]`）が機械的に行う。
本スキルはそれらを再定義せず、規範を満たす具体的な実装パターン（適用例）を提供する。

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
