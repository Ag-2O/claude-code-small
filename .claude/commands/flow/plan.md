---
description: >-
  タスク計画: $ARGUMENTS
  要件・設計をもとにタスクをフェーズへ分解し、依存関係と Wave を含む plans.md を作成する。
argument-hint: <feature>
---

# 指示

タスク計画: $ARGUMENTS

フィーチャー名 `$ARGUMENTS` で `plan-tasks` スキルを読み込み、`.artifacts/features/$ARGUMENTS/specification.md` を
前提にユーザーと対話しながらタスクを整理すること。タスク・依存関係・Wave が固まったら、次を必ず実行すること（省略禁止）。

1. `write-plan` スキルで `.artifacts/features/$ARGUMENTS/plans.md` へ書き出す。
1. 書き出した計画の概要をユーザーへ報告し、各タスクを精緻化するフェーズ（`/flow:refine $ARGUMENTS`）へ進むことを案内する。
