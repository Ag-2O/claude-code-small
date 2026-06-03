---
description: >-
  要件定義: $ARGUMENTS
  ユーザーと対話しながら要件を明確化し、requirements.md を作成する。
argument-hint: <feature>
---

# 指示

要件定義: $ARGUMENTS

フィーチャー名 `$ARGUMENTS` で `define-reqs` スキルを読み込み、ユーザーと対話しながら要件を明確化すること。
要件が固まったら、次を必ず実行すること（省略禁止）。

1. `write-reqs` スキルで `.artifacts/features/$ARGUMENTS/requirements.md` へ書き出す。
1. 書き出した要件の概要をユーザーへ報告し、設計フェーズ（`/flow:spec $ARGUMENTS`）へ進むことを案内する。
