---
name: refine-task
description: >-
  計画されたタスクを、coder が実行できる具体的でアトミックなタスク仕様へ精緻化する時に使用する。
  対象ファイル・実装内容・検証方法・完了条件を明確化し、依存関係を引き継ぐ。refiner サブエージェントが使用する。
user-invocable: false
allowed-tools: [Read, Write, Edit, Glob, Grep]
---

# タスク精緻化ワークフロー

`refiner` サブエージェントが従う精緻化プロセスを定義する。
計画段階の粗いタスクを、coder がそのまま実行できる自己完結したタスク仕様へ変換する。

<workflow>

## 準備

精緻化対象のタスク ID とフィーチャー名を確認する。未指定の場合は呼び出し元へ確認する。

## フェーズ 1: 入力の収集

- `.artifacts/features/<feature>/plan.md` を読み込み、対象タスクの概要・対象ファイル・依存・想定規模を把握する。
- `.artifacts/features/<feature>/specification.md` と `requirements.md` から関連する仕様・受け入れ基準を抽出する。
- `.artifacts/project_architecture.md` があれば、関係するレイヤー・既存パターンを確認する。
- 対象ファイル周辺の既存コードを `Read` / `Grep` で確認し、命名規約・パターンを把握する。

## フェーズ 2: タスクの精緻化

タスク仕様に以下を具体化する。

- **対象ファイル**: 変更・新規作成するファイルの正確なパス。
- **実装内容（action）**: 何をどう実装するか。使用するライブラリ・関数・避けるべきアプローチを具体的に。
- **検証方法（verify）**: 完了を判定する具体的な手段（テストコマンド・型チェック・リンタなど）。
- **完了条件（done）**: 満たすべき最終状態。
- **依存関係**: plan.md から引き継いだ先行タスク ID。

### verify の設計

完了判定（verify）には、確実で意味のある手段を選ぶ。具体例は後述の `<examples>` を参照する。

- **推奨**: 単体テスト・統合テスト、型チェック、AST ベースのリンタ。
- **避ける**: `grep -c <token> <file>` のような単純なテキストマッチング。
  コメントや TODO 内の文字列にもマッチし、テストを通すためにドキュメントを削除するなどの本末転倒を招く。
  どうしても grep を使う場合は、コメント行を除外する正規表現を用いる。

## フェーズ 3: 完了の扱い

タスク仕様の内容（対象ファイル・action・verify・done・依存関係）が固まった時点で本スキルの責務は完了とする。
タスクファイルへの書き出しと呼び出し元への報告は本スキルでは行わず、呼び出し元（`refiner` エージェント定義）が担う。
精緻化中に生じた疑問点・要決定事項は、報告に引き継げるよう整理しておく。

</workflow>

完了判定（verify）の具体例を以下に示す。`<verify>` の良い書き方・悪い書き方の判断基準として用いる。

<examples>

<example>

**シナリオ**: `User` クラスに `is_premium()` メソッドを追加するタスク。

**Bad（避ける書き方）**:

```xml
<verify>
grep -c "def is_premium" src/models/user.py が 1 以上を返す。
</verify>
```

**Good（推奨する書き方）**:

```xml
<verify>
uv run pytest tests/unit/test_user.py::test_is_premium_returns_true_for_premium_plan が pass する。
uv run pytest tests/unit/test_user.py::test_is_premium_returns_false_for_free_plan が pass する。
uv run ruff check src/models tests が 0 件で終了する。
</verify>
```

**理由**: Bad はテキストマッチで「関数が存在するか」しか確認できず、振る舞いを保証しない。
さらに、コメントや docstring 内に `def is_premium` の文字列があれば誤って通る。
Good は振る舞いを単体テストで検証し、静的解析で型・スタイル違反も同時に防ぐ。

</example>

<example>

**シナリオ**: 設定ファイルに `timeout: 30` というキーを追加するタスク。

**Bad（避ける書き方）**:

```xml
<verify>
grep -c "timeout: 30" config/app.yaml が 1 以上を返す。
</verify>
```

**Good（推奨する書き方）**:

```xml
<verify>
uv run python -c "import yaml; assert yaml.safe_load(open('config/app.yaml'))['timeout'] == 30"
が exit 0 で終了する。
</verify>
```

**理由**: Bad はコメント行内の `timeout: 30` にも誤マッチする。Good は YAML として構文解析し、
キー `timeout` が値 `30` を持つことを意味的に検証する。

</example>

</examples>

<thinking>

精緻化中、各要素について以下の順でステップごとに思考を展開すること。
最終出力には含めず、内部推論として用いる。

1. **対象ファイルの特定**: plan.md と既存コードから、変更・新規作成するファイルパスを確定する。
1. **action の具体化**: 何をどう実装するか、使用するライブラリ・関数、避けるべきアプローチを言語化する。
1. **verify の設計**: 完了判定が確実かつ意味のある手段になっているかを確認する
   （単体テスト・型チェック・AST ベースのリンタを優先し、`grep -c` は避ける）。
1. **done の明確化**: 満たすべき最終状態が、coder が他文脈を参照せず判定できるかを確認する。
1. **要決定事項の検出**: 仕様・設計に明記されていない選択肢があれば「要決定事項」として列挙する。

</thinking>

<principles>

- **アトミックに保つ**: 1 タスク 1 目的。コンテキスト・コスト（変更ファイル数・トークン量）が大きすぎる場合は、
  呼び出し元へタスク分割を提案する。
- **自己完結を保つ**: coder が他の文脈を参照せずに完結できるよう、必要な情報をタスク内へ集約する。
- **検証可能にする**: 完了判定の手段を必ず定義する。曖昧な「動くこと」で終わらせない。
- **要決定事項はエスカレーションする**: 仕様・設計に明記されていない選択は自分で決めず、選択肢を
  「要決定事項」として列挙して呼び出し元（メインエージェント）へ委ねる。タスク仕様には論点を残し、
  暫定の前提を置いた場合は前提であると明示する。方針が決まれば呼び出し元から改めて精緻化タスクが渡され、
  既存の `task_<phase_num>_<task_num>.md` と `state.db` から状況を復元して再開する（途中状態の保存は不要）。

</principles>
