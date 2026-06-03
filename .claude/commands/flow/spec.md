---
description: >-
  設計仕様: $ARGUMENTS
  要件をもとにユーザーと対話しながら設計を詰め、specification.md を作成する。
argument-hint: <feature>
---

# 指示

設計仕様: $ARGUMENTS

フィーチャー名 `$ARGUMENTS` で `design-spec` スキルを読み込み、`.artifacts/features/$ARGUMENTS/requirements.md` を
前提にユーザーと対話しながら設計を詰めること。設計が固まったら、次を必ず実行すること（省略禁止）。

1. `write-spec` スキルで `.artifacts/features/$ARGUMENTS/specification.md` へ書き出す。
1. 書き出した設計の概要をユーザーへ報告し、タスク計画フェーズ（`/flow:plan $ARGUMENTS`）へ進むことを案内する。
