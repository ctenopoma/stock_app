# NISA枠予測機能 - API仕様書

## 概要
将来予測API（`POST /api/v1/projections/`）のレスポンスに、NISA枠の使用状況が含まれるようになりました。
各年のNISA枠使用額（つみたて投資枠・成長投資枠）と残り枠、生涯累計使用額を確認できます。

## APIエンドポイント

### POST /api/v1/projections/

**リクエスト:**
```json
{
  "projection_years": 10,
  "annual_return_rate": 5.0
}
```

**レスポンス:**
```json
{
  "id": 123,
  "user": 1,
  "projection_years": 10,
  "annual_return_rate": "5.00",
  "starting_balance_jpy": "0.00",
  "total_accumulated_contributions_jpy": "18000000.00",
  "total_interest_gains_jpy": "2500000.00",
  "projected_total_value_jpy": "20500000.00",
  "projected_composition_by_region": "{...}",
  "year_by_year_breakdown": "[...]",
  "created_at": "2025-01-15T10:00:00Z",
  "valid_until": "2025-01-15T11:00:00Z"
}
```

## year_by_year_breakdown の詳細構造

`year_by_year_breakdown` フィールドはJSON文字列で、パースすると以下の配列が得られます：

```json
[
  {
    "year": 1,
    "starting_balance": 0,
    "contributions": 1800000,
    "balance_before_growth": 1800000,
    "growth_rate": 0.05,
    "ending_balance": 1890000,
    "interest_earned": 90000,
    "nisa_usage": {
      "tsumitate": {
        "used": 600000,
        "remaining": 600000,
        "limit": 1200000
      },
      "growth": {
        "used": 1200000,
        "remaining": 1200000,
        "limit": 2400000
      },
      "total": {
        "used": 1800000,
        "remaining": 1800000,
        "limit": 3600000
      },
      "lifetime_tsumitate": {
        "used": 600000,
        "remaining": 17400000
      },
      "lifetime_growth": {
        "used": 1200000,
        "remaining": 10800000,
        "limit": 12000000
      },
      "lifetime_total": {
        "used": 1800000,
        "remaining": 16200000,
        "limit": 18000000
      }
    }
  },
  {
    "year": 2,
    "starting_balance": 1890000,
    "contributions": 1800000,
    "balance_before_growth": 3690000,
    "growth_rate": 0.05,
    "ending_balance": 3874500,
    "interest_earned": 184500,
    "nisa_usage": {
      "tsumitate": {
        "used": 600000,
        "remaining": 600000,
        "limit": 1200000
      },
      "growth": {
        "used": 1200000,
        "remaining": 1200000,
        "limit": 2400000
      },
      "total": {
        "used": 1800000,
        "remaining": 1800000,
        "limit": 3600000
      },
      "lifetime_tsumitate": {
        "used": 1200000,
        "remaining": 16800000
      },
      "lifetime_growth": {
        "used": 2400000,
        "remaining": 9600000,
        "limit": 12000000
      },
      "lifetime_total": {
        "used": 3600000,
        "remaining": 14400000,
        "limit": 18000000
      }
    }
  }
]
```

## nisa_usage フィールドの説明

### 年間使用状況

| フィールド            | 説明                                 |
| --------------------- | ------------------------------------ |
| `tsumitate.used`      | その年のつみたて投資枠の使用額（円） |
| `tsumitate.remaining` | その年のつみたて投資枠の残り（円）   |
| `tsumitate.limit`     | つみたて投資枠の年間上限（120万円）  |
| `growth.used`         | その年の成長投資枠の使用額（円）     |
| `growth.remaining`    | その年の成長投資枠の残り（円）       |
| `growth.limit`        | 成長投資枠の年間上限（240万円）      |
| `total.used`          | その年のNISA合計使用額（円）         |
| `total.remaining`     | その年のNISA合計の残り（円）         |
| `total.limit`         | NISA年間合計上限（360万円）          |

### 生涯累計使用状況

| フィールド                     | 説明                              |
| ------------------------------ | --------------------------------- |
| `lifetime_tsumitate.used`      | つみたて投資枠の累計使用額（円）  |
| `lifetime_tsumitate.remaining` | つみたて投資枠の生涯残り枠（円）※ |
| `lifetime_growth.used`         | 成長投資枠の累計使用額（円）      |
| `lifetime_growth.remaining`    | 成長投資枠の生涯残り枠（円）      |
| `lifetime_growth.limit`        | 成長投資枠の生涯上限（1,200万円） |
| `lifetime_total.used`          | NISA全体の累計使用額（円）        |
| `lifetime_total.remaining`     | NISA全体の生涯残り枠（円）        |
| `lifetime_total.limit`         | NISA全体の生涯上限（1,800万円）   |

※ つみたて投資枠には独立した生涯上限はなく、全体の1,800万円から成長投資枠の使用分を引いた額が上限となります。

## NISA制度の上限（2024年以降）

- **年間上限**
  - つみたて投資枠: 120万円/年
  - 成長投資枠: 240万円/年
  - 合計: 360万円/年

- **生涯上限**
  - NISA全体: 1,800万円
  - うち成長投資枠: 1,200万円まで
  - つみたて投資枠: 残り枠すべて使用可能

## フロントエンド実装例

### React/TypeScriptでの表示例

```typescript
interface NISAUsage {
  tsumitate: { used: number; remaining: number; limit: number };
  growth: { used: number; remaining: number; limit: number };
  total: { used: number; remaining: number; limit: number };
  lifetime_tsumitate: { used: number; remaining: number };
  lifetime_growth: { used: number; remaining: number; limit: number };
  lifetime_total: { used: number; remaining: number; limit: number };
}

interface YearBreakdown {
  year: number;
  starting_balance: number;
  contributions: number;
  ending_balance: number;
  interest_earned: number;
  nisa_usage: NISAUsage;
}

// APIレスポンスをパース
const projection = await fetchProjection();
const yearBreakdown: YearBreakdown[] = JSON.parse(projection.year_by_year_breakdown);

// 年ごとのNISA使用状況を表示
yearBreakdown.forEach(year => {
  const nisa = year.nisa_usage;
  
  console.log(`Year ${year.year}:`);
  console.log(`  つみたて投資枠: ${nisa.tsumitate.used.toLocaleString()}円 / ${nisa.tsumitate.limit.toLocaleString()}円`);
  console.log(`  成長投資枠: ${nisa.growth.used.toLocaleString()}円 / ${nisa.growth.limit.toLocaleString()}円`);
  console.log(`  生涯累計: ${nisa.lifetime_total.used.toLocaleString()}円 / ${nisa.lifetime_total.limit.toLocaleString()}円`);
});
```

### チャート表示例

```typescript
import { Line } from 'react-chartjs-2';

const NISAUsageChart = ({ yearBreakdown }: { yearBreakdown: YearBreakdown[] }) => {
  const chartData = {
    labels: yearBreakdown.map(y => `Year ${y.year}`),
    datasets: [
      {
        label: 'つみたて投資枠（累計）',
        data: yearBreakdown.map(y => y.nisa_usage.lifetime_tsumitate.used),
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.2)',
      },
      {
        label: '成長投資枠（累計）',
        data: yearBreakdown.map(y => y.nisa_usage.lifetime_growth.used),
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.2)',
      },
      {
        label: '生涯上限',
        data: yearBreakdown.map(() => 18000000),
        borderColor: 'rgb(200, 200, 200)',
        borderDash: [5, 5],
        fill: false,
      },
    ],
  };

  return <Line data={chartData} />;
};
```

## 注意事項

1. **continue_if_limit_exceeded フラグ**
   - 投資計画で `continue_if_limit_exceeded=True` が設定されている場合、NISA枠を超える投資は自動的に一般口座に振り分けられます
   - この場合、NISA使用額は上限でキャップされます

2. **計画の終了日**
   - 投資計画に `end_date` が設定されている場合、その日付以降は投資が行われません
   - 生涯累計は継続して表示されます

3. **一般口座**
   - `target_account_type` が `GENERAL` の投資計画は、NISA使用額に含まれません

## テスト

テストスイートで以下のシナリオを検証済み:
- ✅ NISA枠使用状況が年次明細に含まれること
- ✅ 生涯累計が年を跨いで正しく積算されること
- ✅ DAILY/MONTHLY/BONUS_MONTH各頻度で正しく計算されること
- ✅ continue_if_limit_exceeded フラグが正しく機能すること
- ✅ 計画終了日後は新規投資が停止すること
- ✅ 一般口座はNISA枠に影響しないこと

テスト実行:
```bash
pytest tests/integration/test_projection_nisa.py -v
```

すべてのテストがパスしています（7 passed）。
