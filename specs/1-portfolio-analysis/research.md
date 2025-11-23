# Research: Portfolio Analysis & Asset Projection

**Date**: 2025-11-14
**Feature**: Portfolio Analysis & Asset Projection (1-portfolio-analysis)
**Purpose**: Resolve technical questions and establish best practices for implementation

## Research Questions & Findings

### 1. Compound Interest Calculation for Financial Portfolio

**Question**: What is the best approach for accurate compound interest calculation in a financial portfolio application?

**Decision**: Use annual compound interest formula with year-by-year contribution accumulation

**Rationale**:

- Annual compounding is standard in personal finance applications and matches typical Japanese investment products
- Formula: `FV = PV × (1 + r)^n + [contributions applied with compound growth year-by-year]`
- Contributions added at the start of each year are also subject to compound growth
- More accurate than simple interest and simpler than daily compounding

**Formula Details**:

```
Year 0: Balance = Starting Amount
Year 1: Balance = (Starting + Contributions) × (1 + r)
Year 2: Balance = (Prev Balance + Contributions) × (1 + r)
...
Year N: Balance = (Prev Balance + Contributions) × (1 + r)
```

**Alternatives Considered**:

- Monthly compounding: More complex, minimal benefit for retail investors; typically used only for savings accounts
- Daily compounding: Even more complex; not necessary for equity/bond portfolios
- Simple interest: Less accurate; underestimates long-term growth
- **Selected**: Annual compounding with year-by-year accumulated contributions

**Implementation**: Backend service method in `portfolio/services.py` for clean calculation logic, exposed via API endpoint.

---

### 2. Portfolio Visualization Library Selection

**Question**: Which JavaScript charting library is best for pie chart visualization with tooltips and interactivity?

**Decision**: Recharts (preferred) with fallback consideration for Chart.js

**Rationale**:

- **Recharts**: Built for React, TypeScript support, responsive by default, composable components, excellent tooltip customization
- **Chart.js**: Lightweight, well-established, but requires additional wrapper libraries for React integration
- Recharts aligns better with Next.js + React 18 tech stack and constitutional type-safety requirements

**Comparison**:

| Criteria              | Recharts        | Chart.js                 |
| --------------------- | --------------- | ------------------------ |
| React integration     | Native          | Requires react-chartjs-2 |
| TypeScript support    | Full            | Partial                  |
| Responsive            | Yes (automatic) | Requires configuration   |
| Tooltip customization | Excellent       | Good                     |
| Bundle size           | ~50KB gzipped   | ~30KB gzipped            |
| Learning curve        | Moderate        | Low                      |

**Alternatives Considered**:

- Visx (from Airbnb): More granular control but steeper learning curve
- ECharts: Feature-rich but larger bundle
- **Selected**: Recharts for balance of features, TypeScript support, and React ecosystem fit

**Implementation**: `components/PortfolioChart.tsx` and `components/ProjectionChart.tsx` using Recharts `PieChart` component.

---

### 3. Django Authentication for Single-User MVP

**Question**: What is the simplest secure authentication approach for a single-user/session-based MVP?

**Decision**: Django session-based authentication with optional user registration

**Rationale**:

- Session-based auth is built into Django and doesn't require external dependencies
- Simpler than JWT for MVP; user data stored server-side with session ID in cookie
- Good enough for single-user or trusted environment scenarios
- Can migrate to OAuth2/JWT later without core feature changes

**Setup Details**:

- Use Django's built-in `User` model and session middleware
- Login view returns session cookie; frontend sends it in subsequent requests
- Logout invalidates session
- Optional: Skip login for local development, use hardcoded user

**Alternatives Considered**:

- OAuth2: Over-engineered for single-user MVP; adds complexity
- JWT: Stateless but requires refresh token logic; overkill for MVP
- API Key: Too simplistic for multi-user scenarios
- **Selected**: Django sessions with optional registration

**Implementation**: `accounts/views.py` for login/logout/register endpoints, `accounts/models.py` for User extension.

---

### 4. Performance Optimization for Large Portfolio Datasets

**Question**: How to handle performance when users have 1000+ investment holdings?

**Decision**: Implement database indexing, pagination, and calculation caching

**Rationale**:

- Most retail investors have <100 holdings; 1000+ is edge case but possible
- Use database indices on frequently queried fields (user_id, account_type, asset_region)
- Paginate holdings list (50-100 per page) in frontend
- Cache projection calculations (recalculate only when inputs change)

**Optimization Strategies**:

1. **Database**: Index on `(user_id, asset_region)` for fast portfolio aggregation
2. **API**: Return paginated holdings; aggregate endpoint for summary statistics
3. **Frontend**: Lazy-load charts; memoize calculation results
4. **Backend**: Pre-compute total values when saving holdings

**Alternatives Considered**:

- Materialized views: Overkill for MVP; add later if needed
- NoSQL: Django + SQLite/PostgreSQL sufficient for this scale
- **Selected**: Strategic indexing + pagination + caching

**Implementation**:

- Django ORM with `select_related()` and `prefetch_related()`
- Pagination via DRF `PageNumberPagination`
- Frontend React hook memoization

---

### 5. Handling Different Account Types (NISA vs General Account)

**Question**: How to model tax treatment and account type differences in the system?

**Decision**: Track account type as a field; calculate projections separately per account type

**Rationale**:

- NISA and General Accounts have different tax implications, but spec says system doesn't model taxes (gross amounts only)
- Storing account_type allows future tax calculations without data migration
- Visual distinction in pie charts (color coding) helps user understanding
- Spec requires "NISA and general accounts are visually distinguished"

**Data Model**:

- `InvestmentHolding.account_type` (CharField with choices: 'NISA', 'GENERAL')
- Portfolio pie chart uses color/pattern to distinguish holdings by account type
- API provides breakdown by account type in response

**Alternatives Considered**:

- Separate tables for NISA/General: Overengineered; creates redundant code
- No distinction: Loses important context for user
- **Selected**: Single table with account_type field + visual distinction

**Implementation**:

- `portfolio/models.py` defines choices
- `portfolio/serializers.py` includes account_type in response
- `PortfolioChart.tsx` colors slices by account type

---

## Best Practices Summary

| Area              | Best Practice                            | Rationale                                              |
| ----------------- | ---------------------------------------- | ------------------------------------------------------ |
| Compound Interest | Annual with year-by-year contributions   | Accuracy + simplicity balance                          |
| Visualization     | Recharts pie charts with tooltips        | React ecosystem fit + TypeScript support               |
| Authentication    | Django sessions (MVP)                    | Built-in, simple, sufficient for single-user           |
| Performance       | Indexing + pagination + caching          | Scales to 1000+ holdings without optimization burden   |
| Account Types     | Track in data model + visual distinction | Enables future tax features; matches spec requirements |

## Implementation Notes

1. **Type Safety**: All calculations will be in backend (Python + type hints); frontend consumes via API
2. **API Contracts**: OpenAPI schema generated from DRF serializers ensures frontend/backend alignment
3. **Testing**: Unit tests for calculation logic; integration tests for API; component tests for charts
4. **Deployment**: Backend on any Python WSGI host; frontend on Vercel or similar (from constitution)

## Next Steps

- Phase 1: Create `data-model.md` with entity definitions and API contracts
- Phase 1: Generate OpenAPI schemas in `contracts/`
- Phase 1: Create `quickstart.md` with setup and usage instructions
- Phase 2: Break down into tasks by user story (P1 → P2 → P3)
