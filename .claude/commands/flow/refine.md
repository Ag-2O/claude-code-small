---
description: >-
  タスク精緻化: $ARGUMENTS
  plans.md の未精緻化タスクを refiner サブエージェントで一括並列に task_<phase_num>_<task_num>.md へ精緻化する。
argument-hint: <feature>
---

# 指示

タスク精緻化: $ARGUMENTS

`$ARGUMENTS` を「フィーチャー名」として解釈し、対象フィーチャーの未精緻化タスクをすべて
`refiner` サブエージェントへ並列に委譲すること。
引数が不足している場合は、実行前にユーザーへ確認すること。

<workflow>

1. `.artifacts/features/<feature>/plans.md` を `Read` で読み込み、「タスク一覧」テーブルから
   タスク ID（`task_<phase_num>_<task_num>` 形式）とフェーズを抽出する。`plans.md` が存在しない場合は
   実行を中止し、`/flow:plan <feature>` を先に実行するようユーザーへ促すこと。
1. `Glob` で `.artifacts/features/<feature>/phases/**/task_*.md` を列挙し、
   既に精緻化済みのタスク ID を集合として把握する（ファイル名と ID は一致する）。
1. plans.md のタスク ID から精緻化済みを除外し、「未精緻化タスク」のリストを作成する。
   未精緻化タスクが 0 件であればユーザーへその旨を報告して終了する。
1. **未精緻化タスクすべてに対して、`refiner` サブエージェントを単一メッセージ内で並列起動する**。
   各 `refiner` 呼び出しの prompt は最小限にし、対象タスク ID・フィーチャー名と、
   仕様に書かれていない補足だけを渡す。plans.md・specification.md・requirements.md の内容を
   prompt へ複製しない（refiner が自身で `Read` する）。
   依存関係（Wave）に関係なく一括並列で起動してよい（精緻化はコード変更を伴わず、
   依存先タスクが未精緻化でも判断に必要な情報は plans.md と specification.md から取得できるため）。
1. 各 `refiner` からの報告（精緻化結果・要決定事項・前提）を集約し、ユーザーへサマリーを返す。
   要決定事項が含まれていた場合は、メインが判断またはユーザーへ確認のうえ、
   該当タスクのみ `refiner` を再起動して精緻化を更新すること。

</workflow>

<principles>

- **既存 task\_<phase_num>\_<task_num>.md は上書きしない**: 既に精緻化済みのタスクは対象から除外する。
  再精緻化が必要な場合はユーザーから明示指示を受けたうえで、対象タスクのみ個別に refiner を起動すること。
- **要決定事項はメインで判断する**: refiner は仕様にない選択を自分で決めず「要決定事項」として報告する。
  メインがその場で判断するか、ユーザーへ確認のうえ再度該当タスクを精緻化させる。
- **並列起動は単一メッセージで行う**: 複数の `refiner` 呼び出しを別々のメッセージに分けると逐次実行に
  なってしまう。必ず同一メッセージ内に複数の Agent 呼び出しを並べること。

</principles>
