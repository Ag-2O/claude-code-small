---
name: write-architecture
description: >-
  コードベースの分析結果を .artifacts/project_architecture.md へ書き込む時に使用する。
  プロジェクト全体マップとして差分更新する。explorer サブエージェントが使用する。
user-invocable: false
allowed-tools: [Read, Write, Edit]
---

# project_architecture.md 書き込みワークフロー

コードベースの分析結果を `.artifacts/project_architecture.md` へ書き込む手順を定義する。
`project_architecture.md` はプロジェクト全体のマップとして単一ファイルで管理し、**差分更新**を原則とする。

<workflow>

1. `Read` で既存の `.artifacts/project_architecture.md` を読み込む。存在しない場合は `./template.md` を基に新規作成する。
1. 今回の調査対象に関係するセクションのみを `Edit` で更新・追記する。無関係なセクションには触れない。
1. フロントマターの `last_updated`（日付）と `commit`（`git rev-parse --short HEAD` の結果）を更新する。
1. 全面再生成は、呼び出し元から明示的に指示された場合のみ行う。

</workflow>

<principles>

- **差分更新を行う**: 既存の記述と矛盾する事実を見つけた場合は、該当箇所を修正し、変更理由を簡潔に残す。
- **既存知識を保全する**: 新しいエリアの分析は該当見出しの下に追記し、該当見出しが無ければ新設する。
  既存セクションの安易な削除は行わない。
- **テンプレートに従う**: `./template.md` のセクション構成・見出し・順序を維持して書き込む。

</principles>
