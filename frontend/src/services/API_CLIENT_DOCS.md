# Frontend API Client Documentation

## Overview

The API client (`frontend/src/services/api.ts`) is a fully type-safe TypeScript client for the Portfolio Analysis REST API. It provides:

- **Type-safe endpoints**: All responses and request bodies are fully typed
- **Contract-driven**: Types match the OpenAPI spec in `specs/1-portfolio-analysis/contracts/api.openapi.json`
- **Error handling**: Built-in error handling with HTTP status codes
- **Session authentication**: Automatic cookie-based session management
- **Pagination support**: Built-in pagination for list endpoints

## Installation & Configuration

### 1. Environment Setup

Create or update `frontend/.env.local`:

```bash
# Local development (backend on localhost:8000)
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
```

For production, set the appropriate server URL.

### 2. Import the API Client

```typescript
import { api } from "@/services/api";
// Or import specific modules:
import { holdingsAPI, portfolioAPI, api } from "@/services/api";
```

## Usage Examples

### Authentication

```typescript
// Login
const user = await api.auth.login("username", "password");
console.log(user.id, user.username, user.email);

// Logout
await api.auth.logout();
```

### Holdings (Investment Holdings)

```typescript
// Create a holding
const holding = await api.holdings.create({
  account_type: "NISA",
  asset_class: "MUTUAL_FUND",
  asset_region: "DOMESTIC_STOCKS",
  asset_identifier: "JP0123456789",
  asset_name: "Example Fund",
  current_amount_jpy: 100000,
  purchase_date: "2025-01-01", // Optional
});

// List holdings (paginated)
const { count, results, next, previous } = await api.holdings.list(
  1,    // page
  10    // page_size
);

// Get a single holding
const holding = await api.holdings.get(id);

// Update a holding (full replacement)
const updated = await api.holdings.update(id, {
  account_type: "GENERAL",
  asset_class: "MUTUAL_FUND",
  asset_region: "DOMESTIC_STOCKS",
  asset_identifier: "JP0123456789",
  asset_name: "Example Fund",
  current_amount_jpy: 150000,
});

// Partial update (PATCH)
const patched = await api.holdings.patch(id, {
  current_amount_jpy: 200000, // Only update this field
});

// Delete a holding
await api.holdings.delete(id);
```

### Portfolio Summary

```typescript
const summary = await api.portfolio.getSummary();

console.log(summary.total_value_jpy);              // Total portfolio value
console.log(summary.composition_by_region);        // e.g., { "DOMESTIC_STOCKS": 250000, ... }
console.log(summary.composition_by_account_type);  // e.g., { "NISA": 150000, "GENERAL": 100000 }
console.log(summary.composition_by_asset_class);   // e.g., { "MUTUAL_FUND": 200000, ... }
console.log(summary.holdings_count);               // Number of holdings
```

### Recurring Plans

```typescript
// Create a recurring plan
const plan = await api.recurringPlans.create({
  target_account_type: "NISA",
  target_asset_class: "MUTUAL_FUND",
  target_asset_region: "DOMESTIC_STOCKS",
  frequency: "MONTHLY", // "DAILY" | "MONTHLY" | "BONUS_MONTH"
  amount_jpy: 10000,
  start_date: "2025-01-01",
  end_date: "2035-12-31",           // Optional
  bonus_months: "6,12",              // Optional, comma-separated (required if frequency="BONUS_MONTH")
});

// List plans
const { results } = await api.recurringPlans.list(1, 10);

// Get a single plan
const plan = await api.recurringPlans.get(id);

// Update a plan
const updated = await api.recurringPlans.update(id, { ...plan, frequency: "DAILY" });

// Partial update
const patched = await api.recurringPlans.patch(id, { amount_jpy: 15000 });

// Delete a plan
await api.recurringPlans.delete(id);
```

### Projections

```typescript
// Create a projection
const projection = await api.projections.create({
  projection_years: 10,        // 1-50 years
  annual_return_rate: 5.0,     // -100 to 100 percent
});

console.log(projection.projected_total_value_jpy);  // Projected value after N years
console.log(projection.total_interest_gains_jpy);   // Total interest gained
console.log(projection.projected_composition_by_region); // JSON string of regional composition
console.log(projection.year_by_year_breakdown);     // Year-by-year breakdown (JSON string)

// List projections
const { results } = await api.projections.list(1, 10);

// Get a specific projection
const projection = await api.projections.get(id);
```

## Type Definitions

All types are exported from `frontend/src/services/api.ts`:

```typescript
// User
export interface User {
  id: number;
  username: string;
  email: string;
}

// Investment holding
export interface InvestmentHolding {
  id?: number;
  user?: number;
  account_type: "NISA" | "GENERAL";
  asset_class: "INDIVIDUAL_STOCK" | "MUTUAL_FUND" | "CRYPTOCURRENCY" | "REIT" | "GOVERNMENT_BOND" | "OTHER";
  asset_region: "DOMESTIC_STOCKS" | "INTERNATIONAL_STOCKS" | "DOMESTIC_BONDS" | "INTERNATIONAL_BONDS" | "DOMESTIC_REITS" | "INTERNATIONAL_REITS" | "CRYPTOCURRENCY" | "OTHER";
  asset_identifier: string;
  asset_name: string;
  current_amount_jpy: number;
  purchase_date?: string | null;
  created_at?: string;
  updated_at?: string;
}

// Recurring plan
export interface RecurringInvestmentPlan {
  id?: number;
  user?: number;
  target_account_type: "NISA" | "GENERAL";
  target_asset_class: string;
  target_asset_region: string;
  frequency: "DAILY" | "MONTHLY" | "BONUS_MONTH";
  amount_jpy: number;
  start_date: string;
  end_date?: string | null;
  bonus_months?: string | null;
  created_at?: string;
  updated_at?: string;
}

// Projection
export interface Projection {
  id?: number;
  user?: number;
  projection_years: number;
  annual_return_rate: number;
  starting_balance_jpy: number;
  total_accumulated_contributions_jpy: number;
  total_interest_gains_jpy: number;
  projected_total_value_jpy: number;
  projected_composition_by_region: string; // JSON string
  year_by_year_breakdown?: string | null;   // JSON string
  created_at?: string;
  valid_until?: string | null;
}

// Portfolio summary
export interface PortfolioSummary {
  total_value_jpy: number;
  composition_by_region: Record<string, number>;
  composition_by_account_type: Record<string, number>;
  composition_by_asset_class: Record<string, number>;
  holdings_count: number;
}
```

## Error Handling

All API methods throw errors on failure. The error object has a `status` property and optional `data` property:

```typescript
try {
  await api.holdings.get(id);
} catch (error: any) {
  if (error.status === 404) {
    console.log("Holding not found");
  } else if (error.status === 401) {
    console.log("Not authenticated - please login");
  } else if (error.status === 400) {
    console.log("Validation error:", error.data);
  } else if (error.status >= 500) {
    console.log("Server error");
  }
}
```

## React Hooks Integration

### Example: useHoldings Hook

```typescript
import { useState, useEffect } from "react";
import { api, InvestmentHolding } from "@/services/api";

export function useHoldings() {
  const [holdings, setHoldings] = useState<InvestmentHolding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetch() {
      try {
        const { results } = await api.holdings.list();
        setHoldings(results);
        setError(null);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetch();
  }, []);

  return { holdings, loading, error };
}

// Usage in component:
// const { holdings, loading, error } = useHoldings();
```

## Testing

Integration tests are available in `frontend/src/services/__tests__/api.integration.test.ts`.

To run tests:

```bash
# Ensure backend is running
cd /c/Users/naoki/Documents/Work/stock_app
source backend/.venv/Scripts/activate
cd backend/src && python manage.py runserver

# In another terminal, run tests
cd /c/Users/naoki/Documents/Work/stock_app/frontend
npm test -- api.integration.test.ts
```

## API Endpoints Reference

| Method | Endpoint                | Description                  |
| ------ | ----------------------- | ---------------------------- |
| POST   | `/auth/login`           | Login with username/password |
| POST   | `/auth/logout`          | Logout (clear session)       |
| GET    | `/holdings`             | List holdings (paginated)    |
| POST   | `/holdings`             | Create a holding             |
| GET    | `/holdings/{id}`        | Get a holding                |
| PUT    | `/holdings/{id}`        | Update a holding (full)      |
| PATCH  | `/holdings/{id}`        | Update a holding (partial)   |
| DELETE | `/holdings/{id}`        | Delete a holding             |
| GET    | `/portfolio/summary`    | Get portfolio summary        |
| GET    | `/recurring-plans`      | List recurring plans         |
| POST   | `/recurring-plans`      | Create a plan                |
| GET    | `/recurring-plans/{id}` | Get a plan                   |
| PUT    | `/recurring-plans/{id}` | Update a plan (full)         |
| PATCH  | `/recurring-plans/{id}` | Update a plan (partial)      |
| DELETE | `/recurring-plans/{id}` | Delete a plan                |
| GET    | `/projections`          | List projections             |
| POST   | `/projections`          | Create a projection          |
| GET    | `/projections/{id}`     | Get a projection             |

For more details, see the OpenAPI spec: `specs/1-portfolio-analysis/contracts/api.openapi.json`
