---
name: write-spec
description: >-
  技術設計仕様を .artifacts/features/<feature>/SPECIFICATION.md へ書き込む時に使用する。
  design-spec で固めた設計をテンプレートに沿って構造化する。メインエージェントが直接使用する。
user-invocable: false
allowed-tools: [Read, Write, Edit]
---

# SPECIFICATION.md 書き込みワークフロー

技術設計仕様を `.artifacts/features/<feature>/SPECIFICATION.md` へ書き込む手順を定義する。

<workflow>

## 書き込み手順

1. `Read` で `./template.md` を読み込む。
1. 既存の `.artifacts/features/<feature>/SPECIFICATION.md` があれば読み込み、更新箇所を特定する。
1. テンプレートのセクション構成・見出し・順序を維持し、`Write`（新規）または `Edit`（既存）で書き込む。
1. プレースホルダーはすべて実際の内容で置き換え、フロントマターの最終更新日を更新する。

## Mermaid 図の作成

以下のいずれかに該当する場合は Mermaid 図を作成する。

- 全体アーキテクチャ構造（レイヤー図・コンポーネント図）
- データフロー（シーケンス図・フロー図）
- データモデル（ER 図・クラス図）
- 画面遷移図

</workflow>

<principles>

- **テンプレート構造を保つ**: テンプレートで定義されたセクションを追加・削除・並べ替えしない。
- **未決の前提を記録する**: 設計上の前提（要件で未決だった項目）は明示的に記録する。

</principles>
