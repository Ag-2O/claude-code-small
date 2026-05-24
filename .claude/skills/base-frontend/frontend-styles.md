# フロントエンドスタイルガイド

このファイルは以下の用途に使用する。

- ビューポートフィット必須 CSS ベース
- プリセット選択とムードマッピング
- CSS の注意点と検証ルール

抽象シェイプのみ使用する。ユーザーが明示的に要求しない限り、イラストは避けること。

## ビューポートフィットは必須事項

すべてのスライドは 1 ビューポートに完全に収まること。

### ゴールデンルール

```text
各スライド = ちょうど 1 ビューポートの高さ。
コンテンツが多すぎる = スライドを分割する。
スライド内でスクロールしない。
```

### 密度制限

| スライドの種類       | 最大コンテンツ                                       |
| -------------------- | ---------------------------------------------------- |
| タイトルスライド     | 見出し 1 つ + サブタイトル 1 つ + タグライン（任意） |
| コンテンツスライド   | 見出し 1 つ + 箇条書き 4〜6 つ、または段落 2 つ      |
| フィーチャーグリッド | カード最大 6 枚                                      |
| コードスライド       | 最大 8〜10 行                                        |
| 引用スライド         | 引用 1 つ + 出典                                     |
| 画像スライド         | 画像 1 枚（理想は 60vh 以内）                        |

## 必須ベース CSS

すべてのプレゼンテーションにこのブロックをコピーし、その上にテーマを適用する。

```css
/* ===========================================
   VIEWPORT FITTING: MANDATORY BASE STYLES
   =========================================== */

html, body {
    height: 100%;
    overflow-x: hidden;
}

html {
    scroll-snap-type: y mandatory;
    scroll-behavior: smooth;
}

.slide {
    width: 100vw;
    height: 100vh;
    height: 100dvh;
    overflow: hidden;
    scroll-snap-align: start;
    display: flex;
    flex-direction: column;
    position: relative;
}

.slide-content {
    flex: 1;
    display: flex;
    flex-direction: column;
    justify-content: center;
    max-height: 100%;
    overflow: hidden;
    padding: var(--slide-padding);
}

:root {
    --title-size: clamp(1.5rem, 5vw, 4rem);
    --h2-size: clamp(1.25rem, 3.5vw, 2.5rem);
    --h3-size: clamp(1rem, 2.5vw, 1.75rem);
    --body-size: clamp(0.75rem, 1.5vw, 1.125rem);
    --small-size: clamp(0.65rem, 1vw, 0.875rem);

    --slide-padding: clamp(1rem, 4vw, 4rem);
    --content-gap: clamp(0.5rem, 2vw, 2rem);
    --element-gap: clamp(0.25rem, 1vw, 1rem);
}

.card, .container, .content-box {
    max-width: min(90vw, 1000px);
    max-height: min(80vh, 700px);
}

.feature-list, .bullet-list {
    gap: clamp(0.4rem, 1vh, 1rem);
}

.feature-list li, .bullet-list li {
    font-size: var(--body-size);
    line-height: 1.4;
}

.grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(min(100%, 250px), 1fr));
    gap: clamp(0.5rem, 1.5vw, 1rem);
}

img, .image-container {
    max-width: 100%;
    max-height: min(50vh, 400px);
    object-fit: contain;
}

@media (max-height: 700px) {
    :root {
        --slide-padding: clamp(0.75rem, 3vw, 2rem);
        --content-gap: clamp(0.4rem, 1.5vw, 1rem);
        --title-size: clamp(1.25rem, 4.5vw, 2.5rem);
        --h2-size: clamp(1rem, 3vw, 1.75rem);
    }
}

@media (max-height: 600px) {
    :root {
        --slide-padding: clamp(0.5rem, 2.5vw, 1.5rem);
        --content-gap: clamp(0.3rem, 1vw, 0.75rem);
        --title-size: clamp(1.1rem, 4vw, 2rem);
        --body-size: clamp(0.7rem, 1.2vw, 0.95rem);
    }

    .nav-dots, .keyboard-hint, .decorative {
        display: none;
    }
}

@media (max-height: 500px) {
    :root {
        --slide-padding: clamp(0.4rem, 2vw, 1rem);
        --title-size: clamp(1rem, 3.5vw, 1.5rem);
        --h2-size: clamp(0.9rem, 2.5vw, 1.25rem);
        --body-size: clamp(0.65rem, 1vw, 0.85rem);
    }
}

@media (max-width: 600px) {
    :root {
        --title-size: clamp(1.25rem, 7vw, 2.5rem);
    }

    .grid {
        grid-template-columns: 1fr;
    }
}

@media (prefers-reduced-motion: reduce) {
    *, *::before, *::after {
        animation-duration: 0.01ms !important;
        transition-duration: 0.2s !important;
    }

    html {
        scroll-behavior: auto;
    }
}
```

## ビューポートチェックリスト

- すべての `.slide` に `height: 100vh`、`height: 100dvh`、`overflow: hidden` がある
- すべてのタイポグラフィーに `clamp()` を使用している
- すべての余白に `clamp()` またはビューポート単位を使用している
- 画像に `max-height` 制約がある
- グリッドが `auto-fit` + `minmax()` で適応する
- `700px`、`600px`、`500px` で短高ブレークポイントがある
- 込み入りに感じたらスライドを分割する

## ムードからプリセットへのマッピング

| ムード         | 候補プリセット                                     |
| -------------- | -------------------------------------------------- |
| 感巨・自信     | Bold Signal、Electric Studio、Dark Botanical       |
| 活力・热気     | Creative Voltage、Neon Cyber、Split Pastel         |
| 落ち着き・集中 | Notebook Tabs、Paper & Ink、Swiss Modern           |
| 高揚・感動     | Dark Botanical、Vintage Editorial、Pastel Geometry |

## プリセットカタログ

### 1. Bold Signal

- 雰囲気: 自信、強いインパクト、キーノート準備万全
- 適合: ピッチデッキ、ローンチ、ステートメント
- フォント: Archivo Black + Space Grotesk
- カラー: チャコールベース、ホットオレンジのフォーカルカード、クリーンホワイトの文字
- シグネチャー: オーバーサイズのセクション番号、ダークフィールドに高コントラストカード

### 2. Electric Studio

- 雰囲気: クリーン、ボールド、エージェンシープロフェッショナル
- 適合: クライアントプレゼン、戦略レビュー
- フォント: Manropeのみ
- カラー: 黒、白、鮮梐なコバルトアクセント
- シグネチャー: 2ペイン分割とシャープなエディトリアル配置

### 3. Creative Voltage

- 雰囲気: エネルギッシュ、レトロモダン、肊迫い自信
- 適合: クリエイティブスタジオ、ブランド作業、プロダクトストーリー図
- フォント: Syne + Space Mono
- カラー: エレクトリックブルー、ネオンイエロー、ディープネイビー
- シグネチャー: ハーフトーンテクスチャ、バッジ、パンチのきいたコントラスト

### 4. Dark Botanical

- 雰囲気: 上品、プレミアム、雰囲気豊か
- 適合: ラグジュアリーブランド、丁寧なナラティブ、プレミアム製品デッキ
- フォント: Cormorant + IBM Plex Sans
- カラー: 近黒、ウォームアイボリー、ブラッシュ、ゴールド、テラコッタ
- シグネチャー: ブラーの抽象円、細いルール線、抑制されたモーション

### 5. Notebook Tabs

- 雰囲気: エディトリアル、整理整頓、触覚的
- 適合: レポート、レビュー、構造的ストーリーテリング
- フォント: Bodoni Moda + DM Sans
- カラー: チャコールにクリームペーパーとパステルタブ
- シグネチャー: 紙シート、カラーサイドタブ、バインダーディテール

### 6. Pastel Geometry

- 雰囲気: 親しみやすい、モダン、フレンドリー
- 適合: プロダクト概要、オンボーディング、ライトブランドデッキ
- フォント: Plus Jakarta Sansのみ
- カラー: ペールブルーフィールド、クリームカード、ソフトピンク/ミント/ラベンダーアクセント
- シグネチャー: 縦ピル、丸いカード、ソフトシャドウ

### 7. Split Pastel

- 雰囲気: プレイフル、モダン、クリエイティブ
- 適合: エージェンシーイントロ、ワークショップ、ポートフォリオ
- フォント: Outfitのみ
- カラー: ピーチ + ラベンダー分割とミントバッジ
- シグネチャー: 分割背景、丸いタグ、ライトグリッドオーバーレイ

### 8. Vintage Editorial

- 雰囲気: ウィット、個性充分、マガジン風
- 適合: パーソナルブランド、感想画等、ストーリーテリング
- フォント: Fraunces + Work Sans
- カラー: クリーム、チャコール、ダスティなウォームアクセント
- シグネチャー: ジオメトリックアクセント、枠線のコールアウト、パンチのきいたセリフ見出し

### 9. Neon Cyber

- 雰囲気: 未来的、テッキー、活動的
- 適合: AI、インフラ、開発ツール、未来系トーク
- フォント: Clash Display + Satoshi
- カラー: ミッドナイトネイビー、シアン、マゼンタ
- シグネチャー: グロー、パーティクル、グリッド、データレーダーエネルギー

### 10. Terminal Green

- 雰囲気: 開発者向け、ハッカークリーン
- 適合: API、CLI ツール、エンジニアリングデモ
- フォント: JetBrains Monoのみ
- カラー: GitHub ダーク + ターミナルグリーン
- シグネチャー: スキャンライン、コマンドラインフレーム、正確な等幅間降リズム

### 11. Swiss Modern

- 雰囲気: ミニマル、精密、データ重視
- 適合: コーポレート、プロダクト戦略、分析
- フォント: Archivo + Nunito
- カラー: 白、黒、シグナルレッド
- シグネチャー: 見えるグリッド、非対称、ジオメトリックな箌績

### 12. Paper & Ink

- 雰囲気: 文学的、思慮深い、ストーリー驱動
- 適合: エッセイ、キーノートナラティブ、マニフェストデッキ
- フォント: Cormorant Garamond + Source Serif 4
- カラー: ウォームクリーム、チャコール、クリムゾンアクセント
- シグネチャー: プルクオート、ドロップキャップ、上品なルール線

## 直接選択プロンプト

ユーザーが希望のスタイルをすでに知っている場合は、プレビュー生成を強制せずプリセット名から直接選択させる。

## アニメーションの雰囲気マッピング

| 雰囲気                            | 動きの方向性                                                   |
| --------------------------------- | -------------------------------------------------------------- |
| ドラマチック / シネマティック     | スローフェード、パララックス、大きなスケールイン               |
| テッキー / 未来的                 | グロー、パーティクル、グリッドモーション、スクランブルテキスト |
| プレイフル / フレンドリー         | スプリンギーイージング、丸い形、浮かび上がる動き               |
| プロフェッショナル / コーポレート | 繋細な 200–300ms トランジション、クリーンなスライド            |
| 落ち着き / ミニマル               | 極めて抑制された動き、ホワイトスペース優先                     |
| エディトリアル / マガジン         | 強い階層構造、テキストと画像の山でスタガーしたインタープレイ   |

## CSS 注意点: 関数の否定

以下は使わない:

```css
right: -clamp(28px, 3.5vw, 44px);
margin-left: -min(10vw, 100px);
```

ブラウザはサイレントに無視する。

常に以下を使用する:

```css
right: calc(-1 * clamp(28px, 3.5vw, 44px));
margin-left: calc(-1 * min(10vw, 100px));
```

## 検証サイズ

最低限以下でテストする:

- デスクトップ: `1920x1080`、`1440x900`、`1280x720`
- タブレット: `1024x768`、`768x1024`
- モバイル: `375x667`、`414x896`
- 横向きフォン: `667x375`、`896x414`

## アンチパターン

以下は使わない:

- パープルオンホワイトのスタートアップテンプレート
- ユーザーが明示的に実用ニュートラルを希望しない限り、Inter / Roboto / Arial をビジュアルの声として使用する
- 箇条書きの壁、小さすぎる文字、スクロールが必要なコードブロック
- 抽象ジオメトリで十分な場面で谷飾りイラストを使用する
