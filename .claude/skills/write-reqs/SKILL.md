---
name: write-reqs
description: >-
  明確化された要件を .artifacts/features/<feature>/REQUIREMENTS.md へ書き込む時に使用する。
  define-reqs で固めた要件をテンプレートに沿って構造化する。メインエージェントが直接使用する。
user-invocable: false
allowed-tools: [Read, Write, Edit]
---

# REQUIREMENTS.md 書き込みワークフロー

明確化された要件を `.artifacts/features/<feature>/REQUIREMENTS.md` へ書き込む手順を定義する。

<workflow>

1. `Read` で `./template.md` を読み込む。
1. 既存の `.artifacts/features/<feature>/REQUIREMENTS.md` があれば読み込み、更新箇所を特定する。
1. テンプレートのセクション構成・見出し・順序を維持し、`Write`（新規）または `Edit`（既存）で書き込む。
1. プレースホルダーはすべて実際の内容で置き換え、フロントマターの最終更新日を更新する。

</workflow>

<principles>

- **テンプレート構造を保つ**: テンプレートで定義されたセクションを追加・削除・並べ替えしない。
- **未決事項を明示する**: 仮定で埋めず、「未決事項とリスク」セクションに明示する。

</principles>
