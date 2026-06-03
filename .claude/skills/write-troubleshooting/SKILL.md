---
name: write-troubleshooting
description: >-
  診断結果を .artifacts/troubleshooting/[topic].md へ書き込む時に使用する。
  症状・根本原因・修正方針・再発防止をテンプレートに沿って構造化し、ナレッジベースとして蓄積する。
  troubleshooter が使用する。
user-invocable: false
allowed-tools: [Read, Write, Edit]
---

# troubleshooting/[topic].md 書き込みワークフロー

診断結果を `.artifacts/troubleshooting/[topic].md` へ書き込む手順を定義する。
ナレッジベースとして他エージェントが再利用する前提で構造化する。

<workflow>

1. `Read` で `./template.md` を読み込む。
1. `[topic]` を簡潔な英単語またはスネークケースのフレーズにする（例: `pytest_oom`、`replay_infinite_loop`）。
1. テンプレートのセクション構成を維持し、`Write`（新規）または `Edit`（既存）で書き込む。
1. 同じトピックは既存ファイルを更新し、異なるトピックは新規ファイルを作成する。

</workflow>

<principles>

- **結論を先に書く**: 根本原因と修正方針を先頭に置き、その後に再現・証拠・再発防止を続ける。
- **証拠を明記する**: 参照したファイル・行・ログを明記し、後から検証できるようにする。
- **事実と推測を分ける**: 不明点は「不明」と明記し、推測と事実を混在させない。
- **自己完結を保つ**: ナレッジベースとして他エージェントが再利用する前提で、簡潔かつ自己完結した記述にする。

</principles>
