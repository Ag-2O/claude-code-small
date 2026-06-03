---
name: write-verification
description: >-
  受け入れ検証の結果を .artifacts/features/<feature>/verification.md へ書き込む時に使用する。
  受け入れ基準ごとの達成状況・テスト結果・未達ギャップをテンプレートに沿って構造化する。verifier が使用する。
user-invocable: false
allowed-tools: [Read, Write, Edit]
---

# verification.md 書き込みワークフロー

受け入れ検証の結果を `.artifacts/features/<feature>/verification.md` へ書き込む手順を定義する。

<workflow>

1. `Read` で `./template.md` を読み込む。
1. 既存の `.artifacts/features/<feature>/verification.md` があれば読み込み、新しい検証ラウンドとして追記する。
1. テンプレートのセクション構成を維持し、`Write`（新規）または `Edit`（既存）で書き込む。
1. プレースホルダーはすべて実際の内容で置き換え、フロントマターの最終更新日を更新する。

</workflow>

<principles>

- **基準ごとに達成 / 未達を明示する**: 受け入れ基準ごとに判定の根拠（テスト出力・確認手順）を残す。
- **ギャップは具体的に書く**: 未達がある場合は、原因と対象箇所を具体的に記述し、
  ギャップ修正タスクの起点とする。
- **履歴を残す**: 再検証の場合は既存結果を書き換えず、ラウンドを追記して履歴を残す。
- **総合判定を明記する**: Pass / Fail を必ず明示する。
- **テンプレート構造を保つ**: テンプレートで定義されたセクションを追加・削除・並べ替えしない。

</principles>
