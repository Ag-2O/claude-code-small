---
description: >-
  トラブルシューティング: $ARGUMENTS
  バグ・エラー・予期しない挙動の根本原因を troubleshooter サブエージェントで診断し、troubleshooting/[topic].md へ記録する。
argument-hint: <症状 / エラー>
---

# 指示

トラブルシューティング: $ARGUMENTS

症状・エラー `$ARGUMENTS` で `troubleshooter` サブエージェントを呼び出すこと。
引数が不足していて再現や切り分けの起点が定まらない場合は、実行前にユーザーへ確認すること。

ナレッジベース確認・再現・切り分け・原因特定・修正方針の提案、および診断結果
（`troubleshooting/[topic].md`）の記録は `troubleshooter` 定義の責務に従って実行される（ここでは再指示しない）。
メインは診断・修正を直接行わず、`troubleshooter` へ委譲すること。修正が必要な場合は、診断結果を踏まえて
別途 `/quick:code` または `/flow:code` で対応する。
