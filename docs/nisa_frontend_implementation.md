# NISA枠予測機能 - フロントエンド実装完了

## 実装概要

フロントエンドでNISA枠の将来予測を表示する機能を実装しました。投資計画の作成画面と予測結果画面の両方に新機能が追加されています。

## 実装内容

### 1. 新規コンポーネント作成

#### `NISAUsageChart.tsx`

NISA枠の使用状況をチャートで可視化するコンポーネント。

**機能:**

- 生涯累計使用額の推移（積み上げ棒グラフ）
  - つみたて投資枠（水色）
  - 成長投資枠（オレンジ）
  - 生涯上限1,800万円（赤い破線）
- 年間使用額の内訳（棒グラフ）
  - つみたて120万円/年
  - 成長240万円/年

**表示条件:**

- NISA投資計画が存在し、使用額が0より大きい場合のみ表示

#### `NISAUsageTable.tsx`

NISA枠の詳細情報をテーブル形式で表示するコンポーネント。

**表示内容:**

- 年間使用額
  - つみたて投資枠の使用額と残り枠
  - 成長投資枠の使用額と残り枠
  - 年間合計と使用率
- 生涯累計使用額
  - つみたて投資枠累計
  - 成長投資枠累計（1,200万円制限付き）
  - 全体累計（1,800万円制限）と使用率

### 2. 既存コンポーネント更新

#### `PlansForm.tsx`

投資計画フォームに新しいチェックボックスを追加。

**追加フィールド:**

```tsx
continue_if_limit_exceeded: boolean
```

**表示条件:**

- NISA口座（つみたて投資枠または成長投資枠）選択時のみ表示

**機能:**

- チェックあり: NISA枠超過後も一般口座で投資継続
- チェックなし: NISA枠超過時にエラー表示

**UI:**

```
☑ NISA枠超過後も投資を継続（一般口座へ自動移行）

※ チェックを入れると、NISAの年間・生涯上限を超えた分は一般口座で投資が続きます。
  チェックを外すと、上限超過時にエラーとなります。
```

#### `projections.tsx`

予測結果ページにNISA枠セクションを追加。

**変更内容:**

1. NISAUsageChartコンポーネントをインポート
2. NISAUsageTableコンポーネントをインポート
3. year_by_year_breakdownにNISAデータが含まれる場合のみ表示
4. 既存のチャートセクションの後に配置

**レイアウト:**

```
┌─────────────────────────────────┐
│ 投影結果（サマリー）              │
├─────────────────────────────────┤
│ 成長予測チャート                 │
├─────────────────────────────────┤
│ NISA枠使用予測 ← NEW!            │
│  - 生涯累計チャート              │
│  - 年間使用額チャート            │
├─────────────────────────────────┤
│ NISA枠使用状況（年別詳細）← NEW! │
│  - 詳細テーブル                  │
├─────────────────────────────────┤
│ 年別内訳（既存）                 │
└─────────────────────────────────┘
```

### 3. 型定義の追加

#### `api.ts`

バックエンドのレスポンス構造に対応する型を追加。

**新規型:**

```typescript
export interface NISAUsage {
    tsumitate: { used: number; remaining: number; limit: number };
    growth: { used: number; remaining: number; limit: number };
    total: { used: number; remaining: number; limit: number };
    lifetime_tsumitate: { used: number; remaining: number };
    lifetime_growth: { used: number; remaining: number; limit: number };
    lifetime_total: { used: number; remaining: number; limit: number };
}

export interface YearBreakdown {
    year: number;
    starting_balance: number;
    contributions: number;
    balance_before_growth: number;
    growth_rate: number;
    ending_balance: number;
    interest_earned: number;
    nisa_usage: NISAUsage;
}
```

**更新型:**

```typescript
export interface RecurringInvestmentPlan {
    // ... 既存フィールド
    continue_if_limit_exceeded?: boolean; // ← 追加
}
```

## 使い方

### 1. NISA投資計画の作成

1. 「投資計画」ページへ移動
2. 口座種別で「NISA (つみたて投資枠)」または「NISA (成長投資枠)」を選択
3. 投資額や頻度を入力
4. **「NISA枠超過後も投資を継続」チェックボックス**
   - ☑ チェックあり: 上限超過後も一般口座で投資継続（推奨）
   - ☐ チェックなし: 上限超過時にエラー
5. 計画を保存

### 2. NISA枠予測の確認

1. 「投資配分の予測」ページへ移動
2. 予測年数と年間利回りを入力
3. 「計算」をクリック
4. 結果画面に以下が表示されます:
   - **NISA枠使用予測チャート**
     - 生涯累計の推移（積み上げ棒グラフ）
     - 年間使用額の内訳
   - **NISA枠使用状況テーブル**
     - 年ごとの詳細な使用額と残り枠
     - 生涯累計と使用率

## UI/UXの特徴

### チャート表示

- **色分け**: つみたて投資枠（水色）、成長投資枠（オレンジ）で視覚的に区別
- **上限表示**: 生涯上限1,800万円を赤い破線で表示
- **ツールチップ**: ホバー時に詳細情報を表示（使用額、残り枠）
- **レスポンシブ**: 画面サイズに応じて自動調整

### テーブル表示

- **背景色**: 生涯累計列に色付け（つみたて：青、成長：黄、合計：緑）
- **使用率表示**: パーセンテージで進捗を可視化
- **注釈**: NISA制度の上限情報を表示

### 条件付き表示

- NISA投資計画が存在しない場合は非表示
- NISA使用額が0の場合も非表示（無駄な表示を避ける）

## テクニカルノート

### データフロー

```
1. バックエンド: POST /api/v1/projections/
   ↓
2. レスポンス: year_by_year_breakdown (JSON文字列)
   ↓
3. フロントエンド: JSON.parse()
   ↓
4. YearBreakdown[] 型で処理
   ↓
5. NISAUsageChart / NISAUsageTable コンポーネントで表示
```

### パフォーマンス

- チャートライブラリ: Recharts（既存の依存関係を活用）
- 条件付きレンダリング: NISA データがある場合のみコンポーネントをマウント
- メモ化不要: 投影結果は変更頻度が低いため

### ブラウザ対応

- モダンブラウザ（Chrome、Firefox、Safari、Edge）
- Next.js 14のデフォルトサポート範囲に準拠

## 今後の拡張可能性

### Phase 2 候補機能

1. **NISA枠の最適化提案**
   - 現在の投資計画で効率的にNISA枠を使えているか分析
   - つみたて/成長のバランス提案

2. **アラート機能**
   - NISA枠がもうすぐ満杯になる場合に通知
   - 年間上限超過のリスク警告

3. **シナリオ比較**
   - 複数の投資計画パターンでNISA枠使用を比較
   - 最適な投資配分をシミュレーション

4. **CSVエクスポート**
   - NISA枠使用状況をCSVでダウンロード
   - Excelで詳細分析が可能に

## トラブルシューティング

### Q: NISA枠チャートが表示されない

**A:** 以下を確認してください:

- NISA口座（つみたて/成長）の投資計画が登録されているか
- 投資計画の開始日が予測期間内に含まれているか
- ブラウザのコンソールにエラーが出ていないか

### Q: 生涯上限が1,800万円を超えている

**A:** これは正常な動作です。`continue_if_limit_exceeded=True` の場合、NISA枠を超えた分は一般口座に計上されますが、チャートでは計画上の投資額を表示しています。

### Q: 年間上限が360万円を超えている

**A:** 同様に、`continue_if_limit_exceeded=True` の投資計画では、計画上の年間投資額が表示されます。実際のNISA枠使用額は上限でキャップされています。

## 関連ファイル

### フロントエンド

- `frontend/src/components/NISAUsageChart.tsx` - チャートコンポーネント
- `frontend/src/components/NISAUsageTable.tsx` - テーブルコンポーネント
- `frontend/src/components/PlansForm.tsx` - 投資計画フォーム（更新）
- `frontend/src/pages/projections.tsx` - 予測結果ページ（更新）
- `frontend/src/services/api.ts` - API型定義（更新）

### バックエンド

- `backend/src/portfolio/models.py` - NISA定数定義
- `backend/src/portfolio/services.py` - NISA枠計算ロジック
- `backend/src/portfolio/serializers.py` - バリデーション

### テスト

- `backend/tests/integration/test_projection_nisa.py` - NISA枠予測のテスト
- `backend/tests/contract/test_nisa_limit_validation.py` - 上限バリデーションのテスト

## 確認事項

✅ NISA枠チャート表示
✅ NISA枠テーブル表示
✅ 投資計画フォームにチェックボックス追加
✅ 型定義の追加・更新
✅ 条件付き表示（NISAデータがある場合のみ）
✅ レスポンシブデザイン
✅ ツールチップ・ヘルプテキスト
✅ バックエンドとの型整合性

## デモ

開発サーバー起動中: <http://127.0.0.1:3001>

1. ログイン: testuser / testpass123
2. 「投資計画」でNISA計画を作成
3. 「投資配分の予測」で10年予測を実行
4. NISA枠の使用状況を確認
