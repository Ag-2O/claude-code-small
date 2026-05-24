# impl_[identifier].md テンプレート

```md
# 実装サマリー: [identifier]

## 概要

[2〜3 文のサマリー]

---

- **出力ファイル**: `.artifacts/implementations/impl_[identifier].md`
- **入力ドキュメント**:
  - `.artifacts/plans/plan_[feature_name].md`
  - `.artifacts/specifications/spec_[feature_name].md`
  - `.artifacts/reviews/review_*.md`（該当する場合）
```

同一の `[identifier]` で再実装または修正が発生した場合は、同じファイルへ以下を末尾追記する。

```md
## Round R: [ステップ実装 / レビュー修正]

### 変更ファイル

- `src/foo/bar.py` — 新規作成: XXX のユースケースを実装
- `src/foo/baz.py` — 変更: YYY のインターフェースを追加
- `tests/unit/test_bar.py` — 新規作成: bar.py の単体テスト

### 実装詳細

- **実装した内容**:
  - 構築したものの説明
- **設計判断**:
  - このアプローチを選んだ理由（`.artifacts/specifications/spec_[feature_name].md` からの逸脱や追加があれば記載）
- **対処したエッジケース**:
  - 対応した例外や境界条件

### テスト結果

- **コマンド**: `[テストコマンド]`
- **カバレッジ**: xx%
- **ハッピーパス**: [N] ケース / すべてパス
- **エラーケース**: [N] ケース / すべてパス

### 既知の問題 / スコープ外

- [対処しなかった内容とその理由]

```
