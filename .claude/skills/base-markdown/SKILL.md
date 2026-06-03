---
name: base-markdown
description: >-
  Markdown ファイル（*.md / *.mdx）の作成・更新・レビュー時に使用する。
  フォーマットと lint のツール操作（mdformat・pymarkdown）への参照を提供する。
user-invocable: false
---

# Markdown 言語コンテキスト

ワークスペースの Markdown 固有のコンテキストを一元管理するリファレンススキル。
フォーマッター・リンターの具体的なツール操作への参照を提供する。

## format と lint の実行

フォーマットと lint は以下の手順で実行する。

```bash
uv run mdformat <対象>          # 整形（lint の前に実行）
uv run pymarkdown fix <対象>    # 自動修正できる違反を解消
uv run pymarkdown scan <対象>   # 残存違反を確認し、0 件になるまで手で修正
```

対象は**自分が作成・編集したファイルに限定する**（例: `uv run pymarkdown scan docs/foo.md`）。
