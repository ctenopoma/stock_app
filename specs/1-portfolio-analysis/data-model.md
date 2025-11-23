# Data Model: Portfolio Analysis & Asset Projection

**Date**: 2025-11-14
**Feature**: Portfolio Analysis & Asset Projection (1-portfolio-analysis)
**Purpose**: Define entities, relationships, attributes, and validation rules

## Entity Definitions

### User

Represents an authenticated user of the application.

**Attributes**:
- `id` (int, primary key): Unique user identifier
- `username` (str, unique): Username for login
- `email` (str, unique): Email address
- `password_hash` (str): Hashed password (Django default)
- `created_at` (datetime): Account creation timestamp
- `updated_at` (datetime): Last update timestamp

**Relationships**:
- One user has many `InvestmentHolding` records
- One user has many `RecurringInvestmentPlan` records

**Validation Rules**:
- Username: 3-50 characters, alphanumeric + underscore only
- Email: Valid email format
- Password: Minimum 8 characters (Django default)

**State Transitions**:
- `created` → `active` (login succeeds) → `logged_out` (logout) → `active` (login again)

---

### InvestmentHolding

Represents a single investment position (stock, mutual fund, cryptocurrency, etc.) owned by a user.

**Attributes**:
- `id` (int, primary key): Unique holding identifier
- `user_id` (int, foreign key to User): Owner of the holding
- `account_type` (str): Account classification ('NISA', 'GENERAL')
- `asset_class` (str): Type of investment ('INDIVIDUAL_STOCK', 'MUTUAL_FUND', 'CRYPTOCURRENCY', 'REIT', 'GOVERNMENT_BOND', 'OTHER')
- `asset_region` (str): Geographic region ('DOMESTIC_STOCKS', 'INTERNATIONAL_STOCKS', 'DOMESTIC_BONDS', 'INTERNATIONAL_BONDS', 'DOMESTIC_REITS', 'INTERNATIONAL_REITS', 'CRYPTOCURRENCY', 'OTHER')
- `asset_identifier` (str): Stock symbol, fund code, or crypto ticker (e.g., "1234" for Japanese stock, "VANGUARD_VTI" for ETF)
- `asset_name` (str): Human-readable name of the asset (e.g., "Toyota Motor Corp", "Vanguard Total Stock Market ETF")
- `current_amount_jpy` (decimal): Current investment amount in JPY (can be 0)
- `purchase_date` (date, optional): Date of initial purchase or last significant purchase
- `created_at` (datetime): Record creation timestamp
- `updated_at` (datetime): Last update timestamp

**Relationships**:
- Many holdings belong to one User
- Belongs to one Portfolio (aggregated view, not a separate table)

**Validation Rules**:
- `account_type`: Must be one of enum values (NISA, GENERAL)
- `asset_class`: Must be one of enum values
- `asset_region`: Must be one of enum values
- `asset_identifier`: Non-empty string, 1-100 characters
- `asset_name`: Non-empty string, 1-200 characters
- `current_amount_jpy`: >= 0, decimal precision 2 places (JPY doesn't use cents, but decimal column for consistency)
- `purchase_date`: If provided, must be <= today's date

**State Transitions**:
- `created` → `active` (default) → `edited` (when updated) → `deleted` (soft delete or hard delete per business logic)

---

### RecurringInvestmentPlan

Represents a planned future recurring investment (e.g., monthly ¥50,000 to domestic stocks).

**Attributes**:
- `id` (int, primary key): Unique plan identifier
- `user_id` (int, foreign key to User): Owner of the plan
- `target_account_type` (str): Account type for recurring investment (NISA, GENERAL)
- `target_asset_class` (str): Asset class for recurring investment
- `target_asset_region` (str): Asset region for recurring investment
- `frequency` (str): How often to invest ('DAILY', 'MONTHLY', 'BONUS_MONTH')
- `amount_jpy` (decimal): Amount per investment period (JPY)
- `start_date` (date): First investment date
- `end_date` (date, optional): Last investment date (null = ongoing)
- `bonus_months` (json array, optional): For BONUS_MONTH frequency, list of months (e.g., [6, 12] for June and December)
- `created_at` (datetime): Record creation timestamp
- `updated_at` (datetime): Last update timestamp

**Relationships**:
- Many plans belong to one User
- No direct relationship to InvestmentHolding (plans are future; holdings are current)

**Validation Rules**:
- `target_account_type`, `target_asset_class`, `target_asset_region`: Must be valid enum values
- `frequency`: One of DAILY, MONTHLY, BONUS_MONTH
- `amount_jpy`: > 0, decimal precision 2 places
- `start_date`: Must be <= end_date (if end_date provided)
- `end_date`: If provided, must be >= start_date
- `bonus_months`: If frequency is BONUS_MONTH, must contain 1-12 (month numbers)

**State Transitions**:
- `created` → `active` → `paused` (optional, not in spec but useful) → `completed` (end_date reached) → `deleted`

---

### Portfolio (Aggregated View, No Separate Table)

Represents the aggregated view of all holdings for a user, grouped by asset region.

**Computed Attributes** (not stored; calculated from InvestmentHolding records):
- `total_value_jpy` (decimal): Sum of all current_amount_jpy across all holdings
- `holdings_by_region` (dict): Mapping of asset_region → [InvestmentHolding list]
- `composition_by_region` (dict): Mapping of asset_region → (total JPY, percentage)
- `composition_by_account_type` (dict): Mapping of account_type → (total JPY, percentage)

**Example Portfolio Structure**:
```json
{
  "total_value_jpy": 5000000,
  "composition_by_region": {
    "DOMESTIC_STOCKS": { "amount": 2000000, "percentage": 40 },
    "INTERNATIONAL_STOCKS": { "amount": 1500000, "percentage": 30 },
    "DOMESTIC_BONDS": { "amount": 1000000, "percentage": 20 },
    "CRYPTOCURRENCY": { "amount": 500000, "percentage": 10 }
  },
  "composition_by_account_type": {
    "NISA": { "amount": 3000000, "percentage": 60 },
    "GENERAL": { "amount": 2000000, "percentage": 40 }
  },
  "holdings_count": 25
}
```

---

### Projection (Future Portfolio Forecast)

Represents a calculated forecast of portfolio value at a future date, based on current holdings, recurring plans, and user-specified return rate.

**Attributes**:
- `id` (int, primary key): Unique projection identifier
- `user_id` (int, foreign key to User): Owner of the projection
- `projection_years` (int): Number of years into the future (5, 10, 15, 20, or custom)
- `annual_return_rate` (decimal): User-specified annual return rate as percentage (e.g., 4.0 for 4%, can be negative)
- `starting_balance_jpy` (decimal): Current total portfolio value (snapshot at calculation time)
- `total_accumulated_contributions_jpy` (decimal): Sum of all recurring investments over projection period
- `total_interest_gains_jpy` (decimal): Compound interest earned during projection period
- `projected_total_value_jpy` (decimal): Starting balance + contributions + interest gains
- `projected_composition_by_region` (json): Mapping of asset_region → (projected amount, percentage)
- `year_by_year_breakdown` (json, optional): Year 0, Year 1, ... Year N with balance at each point
- `created_at` (datetime): Calculation timestamp
- `valid_until` (datetime, optional): When projection becomes stale and should be recalculated (e.g., 1 hour later)

**Relationships**:
- Many projections belong to one User
- Projections are snapshots; not linked to specific InvestmentHolding or RecurringInvestmentPlan records

**Validation Rules**:
- `projection_years`: 1-50 (reasonable long-term planning horizon)
- `annual_return_rate`: -100 to 100 (allows for market downturns)
- `starting_balance_jpy`: >= 0
- `total_accumulated_contributions_jpy`: >= 0
- `total_interest_gains_jpy`: Can be negative (if annual_return_rate < 0)

**Calculation Formula** (stored logic in backend service):
```
FV = PV × (1 + r)^n + sum of contributions (each also compounded)
```

---

## Database Schema Highlights

**Tables**:
- `auth_user` (Django built-in User model)
- `portfolio_investmentholding`
- `portfolio_recurringinvestmentplan`
- `portfolio_projection`

**Key Indices**:
- `portfolio_investmentholding(user_id, asset_region)` for fast portfolio aggregation
- `portfolio_investmentholding(user_id)` for user's holdings list
- `portfolio_recurringinvestmentplan(user_id)` for user's plans list
- `portfolio_projection(user_id, created_at DESC)` for user's projection history

**Foreign Keys**:
- `InvestmentHolding.user_id` → `auth_user.id` (CASCADE on delete)
- `RecurringInvestmentPlan.user_id` → `auth_user.id` (CASCADE on delete)
- `Projection.user_id` → `auth_user.id` (CASCADE on delete)

---

## Relationships Diagram

```
┌─────────────┐
│    User     │
│  (id, ...)  │
└──────┬──────┘
       │
       ├─── 1:M ──→ InvestmentHolding
       │             (user_id, account_type, asset_region, ...)
       │
       ├─── 1:M ──→ RecurringInvestmentPlan
       │             (user_id, frequency, amount_jpy, ...)
       │
       └─── 1:M ──→ Projection
                     (user_id, projection_years, annual_return_rate, ...)
```

---

## Enumerations

**AccountType**:
- `NISA` - Tax-free savings account (Japan-specific)
- `GENERAL` - General brokerage account

**AssetClass**:
- `INDIVIDUAL_STOCK` - Single stock
- `MUTUAL_FUND` - Mutual fund
- `CRYPTOCURRENCY` - Digital assets (Bitcoin, Ethereum, etc.)
- `REIT` - Real Estate Investment Trust
- `GOVERNMENT_BOND` - Government bond
- `OTHER` - Other asset classes

**AssetRegion**:
- `DOMESTIC_STOCKS` - Japanese equities
- `INTERNATIONAL_STOCKS` - Foreign equities
- `DOMESTIC_BONDS` - Japanese bonds
- `INTERNATIONAL_BONDS` - Foreign bonds
- `DOMESTIC_REITS` - Japanese real estate investment trusts
- `INTERNATIONAL_REITS` - Foreign real estate investment trusts
- `CRYPTOCURRENCY` - Cryptocurrencies and digital assets
- `OTHER` - Other regions/classifications

**InvestmentFrequency**:
- `DAILY` - Every day
- `MONTHLY` - Every month (1st of the month, or user-specified date)
- `BONUS_MONTH` - Specified months only (e.g., June and December for typical Japanese bonus months)

---

## Validation & Business Rules

### InvestmentHolding Validation
1. All enum fields must match predefined choices
2. `current_amount_jpy` >= 0 (zero is valid; represents pending positions)
3. `asset_identifier` must be unique within a user's holdings for the same account type + asset class + region (to prevent duplicate holdings)
4. If `purchase_date` provided, must be in past or today

### RecurringInvestmentPlan Validation
1. All enum fields valid
2. `amount_jpy` > 0 (must be investing *something* each period)
3. `start_date` <= `end_date` (if end_date provided)
4. If `frequency` is BONUS_MONTH, `bonus_months` must be non-empty list of integers 1-12
5. Plans cannot overlap with impossible date ranges (e.g., start_date in future but end_date in past)

### Portfolio Aggregation Rules
1. Sum all `InvestmentHolding.current_amount_jpy` grouped by `asset_region` to get composition
2. Filter holdings by user_id to ensure user sees only their data
3. Calculate percentages: (region_total / portfolio_total) × 100

### Projection Calculation Rules
1. Start with current portfolio total (snapshot of InvestmentHolding totals)
2. For each year from 1 to N:
   - Add recurring contributions for that year (sum MONTHLY×12 + DAILY×365 + BONUS_MONTH contributions)
   - Apply compound growth: (balance + new_contributions) × (1 + annual_return_rate)
3. Track year-by-year breakdown for optional display
4. Calculate interest gains: final_value - starting_balance - total_contributions
5. Maintain asset region composition proportions through projection (assumes all regions grow at same rate)

---

## Notes for Implementation

- **Soft Deletes**: Consider implementing soft deletes for holdings/plans (add `deleted_at` field) to preserve historical data for tax/audit purposes (future enhancement)
- **Audit Trail**: Consider logging changes to sensitive fields (amount_jpy) for compliance
- **Concurrency**: For MVP, assume single-user or no concurrent editing; scale later if needed
- **Currency**: All amounts are in JPY; future version could support other currencies
- **Timezone**: Use UTC for all timestamps; convert to user's timezone on frontend display (future enhancement)
