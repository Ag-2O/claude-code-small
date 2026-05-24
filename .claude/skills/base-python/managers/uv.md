# uv 使用ルール

このプロジェクトではパッケージマネージャーとして `uv` を使用する。

## 基本コマンド

```bash
# スクリプトを実行する
uv run python main.py

# モジュールを実行する
uv run python -m <module>

# 依存関係を追加する
uv add <package>
```

## 仮想環境

- 仮想環境は `.venv/` 以下に自動生成される。`uv run` を使うため手動でのアクティベートは不要。
- パッケージ管理はすべて `uv` を使う。`pip`、`poetry`、`virtualenv`、`conda` は使わない。
- **仮想環境を手動でアクティベートしない。**

## パッケージ管理

依存関係は `pyproject.toml` で管理される。`uv add` を実行すると自動的に記録される。

```bash
# 開発依存関係を追加する
uv add --dev <package>

# パッケージを削除する
uv remove <package>

# pyproject.toml に合わせて依存関係を同期する
uv sync
```

## 開発ツール

コード品質の維持とテストカバレッジの計測のために以下のツールをインストールする。

- `ruff`: フォーマット、リント、セキュリティ解析
- `pytest`: テストフレームワーク
- `pytest-cov`: テストカバレッジ計測

インストール:

```bash
uv add --dev ruff pytest pytest-cov
```

## 開発ツールの設定

各ツールの設定を `pyproject.toml` に追加する。

```toml
[tool.pytest.ini_options]
pythonpath = [
  "src",              # ソースコードのルートディレクトリ
]

[tool.ruff]
line-length = 88      # 最大行長（プロジェクトのスタイルに合わせて調整する）

[tool.ruff.lint]
select = [
  "E",                # PEP 8 スタイルエラー
  "F",                # flake8 互換エラー
  "S",                # bandit 互換セキュリティエラー
  "I",                # isort 互換インポート順序エラー
]

[tool.ruff.format]
indent-style = "space"  # スペースでインデントする
quote-style = "double"  # 文字列にはダブルクォートを使う
```
