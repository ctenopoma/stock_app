/**
 * Integration tests for the API client
 * Tests that the typed client correctly communicates with the backend API
 */

import { api } from "@/services/api";

// Note: These tests assume the backend is running on localhost:8000
// Run with: NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1 npm test

describe("API Client Integration Tests", () => {
    // Setup: Create test user before running tests
    const testUser = {
        username: "testuser",
        password: "testpass123",
    };

    beforeAll(async () => {
        // Login before running tests
        try {
            await api.auth.login(testUser.username, testUser.password);
        } catch (error) {
            console.log(
                "Note: Create test user first via: python manage.py shell"
            );
        }
    });

    afterAll(async () => {
        // Logout after tests
        try {
            await api.auth.logout();
        } catch (error) {
            // Ignore logout errors
        }
    });

    // =========================================================================
    // Authentication Tests
    // =========================================================================

    describe("Authentication", () => {
        it("should login with valid credentials", async () => {
            const user = await api.auth.login(testUser.username, testUser.password);
            expect(user).toHaveProperty("id");
            expect(user).toHaveProperty("username", testUser.username);
        });

        it("should fail to login with invalid credentials", async () => {
            try {
                await api.auth.login("invalid", "credentials");
                fail("Should have thrown an error");
            } catch (error: any) {
                expect(error.status).toBe(401);
            }
        });

        it("should logout successfully", async () => {
            await api.auth.logout();
            // Logout should succeed without errors
        });
    });

    // =========================================================================
    // Holdings Tests
    // =========================================================================

    describe("Holdings API", () => {
        let createdHoldingId: number;

        it("should create a new holding", async () => {
            const holding = await api.holdings.create({
                account_type: "NISA",
                asset_class: "MUTUAL_FUND",
                asset_region: "DOMESTIC_STOCKS",
                asset_identifier: "test-fund-001",
                asset_name: "Test Fund",
                current_amount_jpy: 100000,
            });

            expect(holding).toHaveProperty("id");
            expect(holding.asset_name).toBe("Test Fund");
            expect(holding.current_amount_jpy).toBe(100000);

            createdHoldingId = holding.id!;
        });

        it("should retrieve a holding by ID", async () => {
            const holding = await api.holdings.get(createdHoldingId);
            expect(holding.id).toBe(createdHoldingId);
            expect(holding.asset_name).toBe("Test Fund");
        });

        it("should list holdings with pagination", async () => {
            const response = await api.holdings.list(1, 10);
            expect(response).toHaveProperty("count");
            expect(response).toHaveProperty("results");
            expect(Array.isArray(response.results)).toBe(true);
        });

        it("should update a holding", async () => {
            const updated = await api.holdings.patch(createdHoldingId, {
                current_amount_jpy: 150000,
            });
            expect(updated.current_amount_jpy).toBe(150000);
        });

        it("should delete a holding", async () => {
            await api.holdings.delete(createdHoldingId);
            // Should not throw; verify deletion by attempting to retrieve
            try {
                await api.holdings.get(createdHoldingId);
                fail("Should have thrown 404 error");
            } catch (error: any) {
                expect(error.status).toBe(404);
            }
        });
    });

    // =========================================================================
    // Portfolio Summary Tests
    // =========================================================================

    describe("Portfolio API", () => {
        beforeAll(async () => {
            // Create some test holdings for portfolio summary
            await api.holdings.create({
                account_type: "NISA",
                asset_class: "INDIVIDUAL_STOCK",
                asset_region: "DOMESTIC_STOCKS",
                asset_identifier: "test-stock-001",
                asset_name: "Test Stock",
                current_amount_jpy: 50000,
            });

            await api.holdings.create({
                account_type: "GENERAL",
                asset_class: "MUTUAL_FUND",
                asset_region: "INTERNATIONAL_STOCKS",
                asset_identifier: "test-intl-fund",
                asset_name: "Intl Fund",
                current_amount_jpy: 75000,
            });
        });

        it("should get portfolio summary", async () => {
            const summary = await api.portfolio.getSummary();
            expect(summary).toHaveProperty("total_value_jpy");
            expect(summary).toHaveProperty("composition_by_region");
            expect(summary).toHaveProperty("composition_by_account_type");
            expect(summary).toHaveProperty("holdings_count");

            // Should have at least the holdings we created
            expect(summary.total_value_jpy).toBeGreaterThanOrEqual(125000);
            expect(summary.holdings_count).toBeGreaterThanOrEqual(2);
        });
    });

    // =========================================================================
    // Recurring Plans Tests
    // =========================================================================

    describe("Recurring Plans API", () => {
        let createdPlanId: number;

        it("should create a recurring plan", async () => {
            const plan = await api.recurringPlansAPI.create({
                target_account_type: "NISA",
                target_asset_class: "MUTUAL_FUND",
                target_asset_region: "DOMESTIC_STOCKS",
                frequency: "MONTHLY",
                amount_jpy: 10000,
                start_date: "2025-01-01",
            });

            expect(plan).toHaveProperty("id");
            expect(plan.frequency).toBe("MONTHLY");

            createdPlanId = plan.id!;
        });

        it("should list recurring plans", async () => {
            const response = await api.recurringPlansAPI.list();
            expect(Array.isArray(response.results)).toBe(true);
        });

        it("should delete a recurring plan", async () => {
            await api.recurringPlansAPI.delete(createdPlanId);
        });
    });

    // =========================================================================
    // Projections Tests
    // =========================================================================

    describe("Projections API", () => {
        it("should create a projection", async () => {
            const projection = await api.projectionsAPI.create({
                projection_years: 10,
                annual_return_rate: 5.0,
            });

            expect(projection).toHaveProperty("id");
            expect(projection.projection_years).toBe(10);
            expect(projection.annual_return_rate).toBe(5.0);
            expect(projection).toHaveProperty("projected_total_value_jpy");
        });

        it("should list projections", async () => {
            const response = await api.projectionsAPI.list();
            expect(Array.isArray(response.results)).toBe(true);
        });
    });

    // =========================================================================
    // Error Handling Tests
    // =========================================================================

    describe("Error Handling", () => {
        it("should handle 404 errors", async () => {
            try {
                await api.holdings.get(99999);
                fail("Should have thrown an error");
            } catch (error: any) {
                expect(error.status).toBe(404);
            }
        });

        it("should handle 401 errors for unauthenticated requests", async () => {
            // This test would require a separate client without auth cookies
            // For now, we skip this as the main client maintains session auth
        });
    });
});
