---
description: >-
  受け入れ検証: $ARGUMENTS
  完成した機能を verifier サブエージェントで検証し、verification.md を作成する。
argument-hint: <feature> [scope]
---

# 指示

受け入れ検証: $ARGUMENTS

検証対象のフィーチャー名 `$ARGUMENTS` で `verifier` サブエージェントを呼び出すこと。
受け入れ基準に対する達成状況の判定と `verification.md` の作成は `verifier` 定義の責務に従って実行される（ここでは再指示しない）。
判定が Fail の場合は、未達項目をギャップ修正タスクとして起票し、修正フローへ戻すこと。
