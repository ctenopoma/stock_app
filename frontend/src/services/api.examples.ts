/**
 * Example usage of the Portfolio Analysis API Client
 * This demonstrates how to use the typed API client in React components
 */

import { api } from "@/services/api";

// ============================================================================
// Example 1: Login
// ============================================================================

async function exampleLogin() {
    try {
        const user = await api.auth.login("testuser", "testpass");
        console.log("Logged in as:", user.username);
    } catch (error: any) {
        console.error("Login failed:", error.message);
    }
}

// ============================================================================
// Example 2: Create a holding
// ============================================================================

async function exampleCreateHolding() {
    try {
        const newHolding = await api.holdings.create({
            account_type: "NISA",
            asset_class: "MUTUAL_FUND",
            asset_region: "DOMESTIC_STOCKS",
            asset_identifier: "JP0123456789",
            asset_name: "Example Fund",
            current_amount_jpy: 100000,
            purchase_date: "2025-01-01",
        });
        console.log("Created holding:", newHolding.id);
    } catch (error: any) {
        console.error("Failed to create holding:", error.message);
    }
}

// ============================================================================
// Example 3: List holdings with pagination
// ============================================================================

async function exampleListHoldings() {
    try {
        const response = await api.holdings.list(1, 10);
        console.log(`Total holdings: ${response.count}`);
        response.results.forEach((holding) => {
            console.log(
                `- ${holding.asset_name} (${holding.current_amount_jpy} JPY)`
            );
        });
    } catch (error: any) {
        console.error("Failed to list holdings:", error.message);
    }
}

// ============================================================================
// Example 4: Update a holding
// ============================================================================

async function exampleUpdateHolding(holdingId: number) {
    try {
        const updated = await api.holdings.patch(holdingId, {
            current_amount_jpy: 150000,
        });
        console.log("Updated holding:", updated);
    } catch (error: any) {
        console.error("Failed to update holding:", error.message);
    }
}

// ============================================================================
// Example 5: Get portfolio summary
// ============================================================================

async function exampleGetPortfolioSummary() {
    try {
        const summary = await api.portfolio.getSummary();
        console.log("Total portfolio value:", summary.total_value_jpy, "JPY");
        console.log("Holdings count:", summary.holdings_count);
        console.log(
            "Composition by region:",
            summary.composition_by_region
        );
    } catch (error: any) {
        console.error("Failed to get portfolio summary:", error.message);
    }
}

// ============================================================================
// Example 6: Create a projection
// ============================================================================

async function exampleCreateProjection() {
    try {
        const projection = await api.projections.create({
            projection_years: 10,
            annual_return_rate: 5.0,
        });
        console.log(
            "Projected value after 10 years:",
            projection.projected_total_value_jpy,
            "JPY"
        );
    } catch (error: any) {
        console.error("Failed to create projection:", error.message);
    }
}

// ============================================================================
// Error Handling Pattern
// ============================================================================

async function exampleErrorHandling() {
    try {
        await api.holdings.get(99999); // Non-existent holding
    } catch (error: any) {
        if (error.status === 404) {
            console.log("Holding not found");
        } else if (error.status === 401) {
            console.log("Not authenticated");
        } else if (error.status === 500) {
            console.log("Server error");
        } else {
            console.log("Unexpected error:", error.message);
        }
    }
}

// ============================================================================
// React Component Pattern
// ============================================================================

// Example React component using the API client
/*
import { useState, useEffect } from "react";
import { api, InvestmentHolding } from "@/services/api";

export function HoldingsList() {
  const [holdings, setHoldings] = useState<InvestmentHolding[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    async function fetchHoldings() {
      try {
        const response = await api.holdings.list();
        setHoldings(response.results);
      } catch (err: any) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }

    fetchHoldings();
  }, []);

  if (loading) return <div>Loading...</div>;
  if (error) return <div>Error: {error}</div>;

  return (
    <ul>
      {holdings.map((holding) => (
        <li key={holding.id}>
          {holding.asset_name} - {holding.current_amount_jpy} JPY
        </li>
      ))}
    </ul>
  );
}
*/

export {
    exampleCreateHolding, exampleCreateProjection,
    exampleErrorHandling, exampleGetPortfolioSummary, exampleListHoldings, exampleLogin, exampleUpdateHolding
};
