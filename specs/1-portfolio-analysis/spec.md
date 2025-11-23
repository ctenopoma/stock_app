# Feature Specification: Portfolio Analysis & Asset Projection

**Feature Branch**: `1-portfolio-analysis`
**Created**: 2025-11-14
**Status**: Draft
**Input**: User description: "投資している株式、投資信託、仮想通貨の情報を入力し、ポートフォリオ、将来の資産額を分析・表示するアプリケーション..."

## User Scenarios & Testing

### User Story 1 - Input Current Investment Holdings (Priority: P1)

User logs into the application and inputs their current investment holdings across various account types (NISA, general accounts) and asset classes. This establishes the baseline for portfolio analysis.

**Why this priority**: This is the foundational user journey—without current holdings data, no portfolio analysis is possible. It directly enables portfolio visualization (P2) and future projections (P3).

**Independent Test**: User can input and save a diversified portfolio with 5+ investment holdings spanning different account types and asset classes, and verify that the data persists when retrieving the portfolio view.

**Acceptance Scenarios**:

1. **Given** a user with no investment holdings, **When** they navigate to the input screen, **Then** they see a form to add holdings with the following fields:
   - Account type (NISA / General Account)
   - Asset class (Individual Stock / Mutual Fund / Cryptocurrency / REIT / Government Bond / etc.)
   - Asset region (Domestic Stocks / International Stocks / Domestic Bonds / International Bonds / Domestic REITs / International REITs / Cryptocurrency / Other)
   - Current investment amount (JPY)
   - Asset name/symbol
   - Purchase date (optional)

2. **Given** a user has entered investment details, **When** they click "Save," **Then** the system validates that all required fields are populated and displays a confirmation message

3. **Given** a user has saved holdings, **When** they navigate back to the portfolio view, **Then** they see their previously entered holdings listed with edit and delete options

4. **Given** a user with existing holdings, **When** they click "Edit" on a holding, **Then** they can modify the amount, account type, or asset class and save the changes

---

### User Story 2 - Visualize Current Portfolio (Priority: P2)

User views their current portfolio composition as a pie chart, breaking down holdings by asset region or asset class as a visual overview of their current asset allocation.

**Why this priority**: Portfolio visualization provides immediate value and insight into current allocation. It reinforces data entry (P1) and is prerequisite for future projection comparisons (P3).

**Independent Test**: After inputting 3+ holdings of different asset regions, user can view a pie chart showing the percentage allocation of each asset region, with labels and percentages clearly visible.

**Acceptance Scenarios**:

1. **Given** a user with multiple holdings, **When** they navigate to the "Portfolio" tab, **Then** a pie chart displays showing:
   - Each asset region as a distinct slice
   - Percentage allocation for each region
   - Total portfolio value in JPY
   - Legend with asset region names and values

2. **Given** a pie chart on screen, **When** they hover over a slice, **Then** a tooltip displays:
   - Asset region name
   - Total amount invested in that region
   - Percentage of overall portfolio
   - Number of holdings in that region

3. **Given** a portfolio with holdings across different account types, **When** they view the chart, **Then** holdings from NISA and general accounts are visually distinguished (e.g., different colors or patterns)

---

### User Story 3 - Input Recurring Investment Plans (Priority: P2)

User specifies recurring investment plans (daily, monthly, bonus month contributions) to model future portfolio growth and accumulation.

**Why this priority**: Recurring investment input directly enables P3 (future projections). While not immediately valuable alone, it is essential for realistic long-term analysis and should be addressed in the same phase as current portfolio visualization.

**Independent Test**: User can specify 2+ recurring investment plans (e.g., monthly ¥50,000 to domestic stocks + bonus month ¥200,000 to international stocks), save them, and retrieve the plans in edit/view mode.

**Acceptance Scenarios**:

1. **Given** a user on the "Investment Plans" tab, **When** they click "Add Recurring Investment," **Then** they see a form with:
   - Target asset (account type + asset class + asset region)
   - Frequency (Daily / Monthly / Bonus Month)
   - Amount (JPY)
   - Start date
   - End date (optional; default to ongoing)

2. **Given** a user has selected "Bonus Month," **When** they save, **Then** the system prompts for:
   - Which months are bonus months (e.g., June, December)
   - Amount for bonus contributions

3. **Given** a user has created recurring investment plans, **When** they navigate back to the Investment Plans view, **Then** they see all plans listed with:
   - Target asset
   - Frequency
   - Monthly/annual equivalent amount
   - Edit and delete options

---

### User Story 4 - Project Future Portfolio & Asset Growth (Priority: P3)

User specifies an annual return rate and time horizon (5 years, 10 years, etc.), and the system calculates and displays the projected portfolio composition and total asset value considering compound interest.

**Why this priority**: This is the analysis and insights layer—valuable but depends on P1 and P2 data. It directly addresses the core business need: helping users understand future wealth accumulation.

**Independent Test**: User inputs 2 recurring investment plans, selects a 5-year projection horizon with 4% annual return, and the system displays:
  - Projected portfolio pie chart showing asset allocation after accumulated contributions
  - Total projected asset value with compound interest applied
  - Year-by-year breakdown (optional) showing growth trajectory

**Acceptance Scenarios**:

1. **Given** a user with current holdings and recurring investment plans, **When** they navigate to "Future Projections" tab, **Then** they see:
   - A form to input: projection years (5, 10, 15, 20, custom), annual return rate (as %)
   - A submit button labeled "Calculate Projection"

2. **Given** a user has submitted projection parameters, **When** the system calculates, **Then** it displays:
   - Projected total asset value after the selected time horizon
   - Pie chart showing projected portfolio composition (by asset region)
   - Breakdown of: starting balance + accumulated contributions + compound interest gains
   - Comparison table showing current vs. projected portfolio side-by-side

3. **Given** a projected portfolio pie chart, **When** user hovers over a slice, **Then** a tooltip shows:
   - Asset region name
   - Projected amount (including contributions and returns)
   - Percentage of projected portfolio
   - Growth rate (gain amount) for that region

4. **Given** a user viewing a projection, **When** they change the annual return rate or time horizon, **Then** the system recalculates and updates all charts and values in real-time (without requiring a page reload)

---

### Edge Cases

- What happens when a user inputs a current investment amount of 0? System MUST accept and display as valid holding (useful for tracking accounts with pending distributions).
- What happens when recurring investment end date is before start date? System MUST reject with a clear error message.
- What happens when annual return rate is negative (market downturn scenario)? System MUST accept and calculate projected decline accordingly.
- What happens when user has no recurring investments? System MUST still allow projection, treating only current holdings as the baseline.
- What happens when projected portfolio composition is extreme (>99% in one asset region)? System MUST display warning that portfolio is highly concentrated and may suggest diversification.

## Requirements

### Functional Requirements

- **FR-001**: System MUST store user investment holdings with: account type, asset class, asset region, current amount, and asset identifier.
- **FR-002**: System MUST support the following account types: NISA, General Account.
- **FR-003**: System MUST support the following asset classes: Individual Stock, Mutual Fund, Cryptocurrency, REIT, Government Bond, Other.
- **FR-004**: System MUST support the following asset regions: Domestic Stocks, International Stocks, Domestic Bonds, International Bonds, Domestic REITs, International REITs, Cryptocurrency, Other.
- **FR-005**: System MUST validate that all required investment holding fields are populated before saving.
- **FR-006**: System MUST allow users to edit and delete existing investment holdings.
- **FR-007**: System MUST display current portfolio as a pie chart, grouped by asset region, showing percentages and JPY amounts.
- **FR-008**: System MUST calculate and display total current portfolio value in JPY.
- **FR-009**: System MUST allow users to specify recurring investments with: target asset, frequency (Daily / Monthly / Bonus Month), amount, and date range.
- **FR-010**: System MUST support bonus month selection (multiple months per year, user-configurable).
- **FR-011**: System MUST calculate annual accumulated investment amount based on recurring plans (sum of monthly amounts × 12 + bonus contributions).
- **FR-012**: System MUST accept a user-specified annual return rate (as percentage, can be positive or negative).
- **FR-013**: System MUST calculate future portfolio value using compound interest formula: FV = PV × (1 + r)^n + contributions, where contributions are also compounded year-by-year.
- **FR-014**: System MUST display projected portfolio as a pie chart (by asset region) for the selected time horizon.
- **FR-015**: System MUST show a comparison view of current vs. projected portfolio side-by-side.
- **FR-016**: System MUST display breakdown of projected value: starting balance + accumulated contributions + compound interest gains.
- **FR-017**: System MUST allow real-time recalculation when user adjusts return rate or projection years without page reload.
- **FR-018**: System MUST provide interactive tooltips on pie charts (hover to see detailed values).
- **FR-019**: System MUST persist all user data (holdings, recurring investments) across sessions.
- **FR-020**: System MUST handle edge case of zero investment amounts and negative return rates.

### Key Entities

- **Investment Holding**: Represents a single investment position. Attributes: account_type, asset_class, asset_region, current_amount_jpy, asset_identifier, purchase_date.
- **Recurring Investment Plan**: Represents a planned future investment. Attributes: target_account_type, target_asset_class, target_asset_region, frequency, amount_jpy, start_date, end_date, bonus_months.
- **Portfolio**: Aggregated view of holdings. Attributes: total_value_jpy, holdings_list, composition_by_region.
- **Projection**: Future portfolio forecast. Attributes: projection_years, annual_return_rate, projected_total_value_jpy, projected_composition, breakdown (starting_balance, accumulated_contributions, interest_gains).

## Success Criteria

### Measurable Outcomes

- **SC-001**: Users can input and save investment holdings with 5+ different asset regions in under 5 minutes, with 100% data accuracy (no data loss on save/retrieve).
- **SC-002**: Portfolio pie chart renders within 2 seconds and is visually accurate (verified by spot-checking percentages against manual calculation).
- **SC-003**: Users can create and modify 3+ recurring investment plans without encountering errors or data validation failures.
- **SC-004**: Projection calculation (for 5-10 year horizons with 2-3 recurring plans) completes in under 1 second with accurate compound interest math (verified against manual calculation).
- **SC-005**: 90% of users can independently complete the primary flow (input holdings → view portfolio → create projection) on first attempt, indicating intuitive UX.
- **SC-006**: Pie chart tooltips display and disappear smoothly without delays, enhancing user understanding of portfolio composition.
- **SC-007**: System correctly handles edge cases (zero amounts, negative returns, missing end dates) with appropriate error messages or default behaviors.
- **SC-008**: Year-over-year projections for same holdings/plans/rate are bit-identical, ensuring calculation consistency and reproducibility.

## Assumptions

- Users are Japanese-based investors (currency is JPY; tax treatment like NISA is relevant).
- Annual return rate is a simple, uniform percentage applied to all assets (no asset-specific returns modeled).
- Recurring investments are distributed evenly throughout the month (daily) or applied on the 1st of each month (monthly) unless specified otherwise.
- Bonus month investments occur once per month, on a user-selected date.
- Compound interest is calculated annually (annual compounding, not monthly or daily).
- System does not model taxes, fees, or trading costs—values shown are gross amounts.
- User authentication and authorization are out of scope; assume single-user local or session-authenticated experience.
