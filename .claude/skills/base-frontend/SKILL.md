---
name: base-frontend
description: >
  フロントエンドコンポーネント・UI・プレゼンテーションの実装・レビュー時に使用する。
  React/Next.js パターン、状態管理、パフォーマンス最適化、HTML プレゼンテーション作成の
  リファレンスを提供する。
user-invocable: false
---

# フロントエンドコンテキスト

このスキルは、ワークスペースのフロントエンド固有のコンテキストを一元管理する。

## 参照ファイル

| 参照 | パス |
| ---- | ---- |
| `frontend` | `./frontend.md` |
| `frontend-rich` | `./frontend-rich.md` |
| `frontend-styles` | `./frontend-styles.md` |

## 読み込みタイミング

### 通常の UI 開発

以下のいずれかに該当する場合に `frontend` を読み込む。

- コンポーネント設計 — React コンポーネントの実装・リファクタリング
- 状態管理 — useState / useReducer / Zustand / Context の設計
- データフェッチ — SWR、React Query、サーバーコンポーネントの使用
- パフォーマンス — メモ化、仮想化、コード分割の最適化
- フォーム — バリデーション、制御されたコンポーネント、Zod スキーマ
- アクセシビリティ — キーボード操作、フォーカス管理、ARIA 属性

### プレゼンテーション作成

以下のいずれかに該当する場合に `frontend-rich` と `frontend-styles` をセットで読み込む。

- 新規スライド作成 — トークデッキ、ピッチデッキ、社内資料の HTML 化
- PPT 変換 — `.ppt` / `.pptx` の HTML プレゼンテーションへの変換
- 既存デッキ改善 — レイアウト・モーション・タイポグラフィの改善

`frontend-styles` は `frontend-rich` と常にセットで使う。単体では使わない。
プレゼンテーション作成では `frontend` は不要。

## 組み合わせルール

- テスト駆動実装には `tdd` と組み合わせる。
- コードレビュータスクには `review` と組み合わせる。
