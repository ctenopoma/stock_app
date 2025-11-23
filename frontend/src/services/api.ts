/**
 * Typed API client for Portfolio Analysis API
 * Contract-driven development: Types match OpenAPI schema in specs/1-portfolio-analysis/contracts/api.openapi.json
 */

// ============================================================================
// Type Definitions (matching OpenAPI schema)
// ============================================================================

export interface User {
    id: number;
    username: string;
    email: string;
}

export interface InvestmentHolding {
    id?: number;
    user?: number;
    account_type: "NISA_TSUMITATE" | "NISA_GROWTH" | "GENERAL";
    asset_class:
    | "INDIVIDUAL_STOCK"
    | "MUTUAL_FUND"
    | "CRYPTOCURRENCY"
    | "REIT"
    | "GOVERNMENT_BOND"
    | "OTHER";
    asset_region:
    | "DOMESTIC_STOCKS"
    | "INTERNATIONAL_STOCKS"
    | "DOMESTIC_BONDS"
    | "INTERNATIONAL_BONDS"
    | "DOMESTIC_REITS"
    | "INTERNATIONAL_REITS"
    | "CRYPTOCURRENCY"
    | "OTHER";
    asset_identifier: string;
    asset_name: string;
    current_amount_jpy: number;
    purchase_date?: string | null;
    created_at?: string;
    updated_at?: string;
}

export interface HoldingsListResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: InvestmentHolding[];
}

export interface RecurringInvestmentPlan {
    id?: number;
    user?: number;
    target_account_type: "NISA_TSUMITATE" | "NISA_GROWTH" | "GENERAL";
    target_asset_class:
    | "INDIVIDUAL_STOCK"
    | "MUTUAL_FUND"
    | "CRYPTOCURRENCY"
    | "REIT"
    | "GOVERNMENT_BOND"
    | "OTHER";
    target_asset_region:
    | "DOMESTIC_STOCKS"
    | "INTERNATIONAL_STOCKS"
    | "DOMESTIC_BONDS"
    | "INTERNATIONAL_BONDS"
    | "DOMESTIC_REITS"
    | "INTERNATIONAL_REITS"
    | "CRYPTOCURRENCY"
    | "OTHER";
    target_asset_identifier?: string;
    target_asset_name?: string;
    frequency: "DAILY" | "MONTHLY" | "BONUS_MONTH";
    amount_jpy: number;
    start_date: string;
    end_date?: string | null;
    bonus_months?: string | null;
    continue_if_limit_exceeded?: boolean;
    created_at?: string;
    updated_at?: string;
}

export interface RecurringPlansListResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: RecurringInvestmentPlan[];
}

export interface NISAUsage {
    tsumitate: {
        used: number;
        remaining: number;
        limit: number;
    };
    growth: {
        used: number;
        remaining: number;
        limit: number;
    };
    total: {
        used: number;
        remaining: number;
        limit: number;
    };
    lifetime_tsumitate: {
        used: number;
        remaining: number;
    };
    lifetime_growth: {
        used: number;
        remaining: number;
        limit: number;
    };
    lifetime_total: {
        used: number;
        remaining: number;
        limit: number;
    };
}

export interface NISARemainingResponse {
    year: number;
    annual: {
        tsumitate: { amount: number; remaining: number };
        growth: { amount: number; remaining: number };
        total: { amount: number; remaining: number };
    };
    lifetime: {
        tsumitate: { amount: number; remaining: number };
        growth: { amount: number; remaining: number; limit?: number };
        total: { amount: number; remaining: number; limit?: number };
    };
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
    projected_composition_by_asset_class?: string; // JSON string (optional for backward compatibility)
    year_by_year_breakdown?: string | null; // JSON string
    created_at?: string;
    valid_until?: string | null;
}

export interface ProjectionsListResponse {
    count: number;
    next: string | null;
    previous: string | null;
    results: Projection[];
}

export interface PortfolioSummary {
    total_value_jpy: number;
    // Each composition entry contains amount and percentage
    composition_by_region: Record<string, { amount: number; percentage: number }>;
    composition_by_account_type: Record<string, { amount: number; percentage: number }>;
    composition_by_asset_class: Record<string, { amount: number; percentage: number }>;
    holdings_count: number;
}

export interface ApiErrorResponse {
    detail?: string;
    [key: string]: unknown;
}

// ============================================================================
// API Configuration
// ============================================================================

const API_BASE_URL =
    process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface RequestOptions extends RequestInit {
    headers?: Record<string, string>;
}

// ============================================================================
// HTTP Helper Functions
// ============================================================================

function getCSRFCookie(name = "csrftoken"): string | null {
    if (typeof document === "undefined") return null;
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop()!.split(";").shift() || null;
    return null;
}

/**
 * Wrapper for fetch with error handling and JSON parsing
 */
async function apiRequest<T = unknown>(
    endpoint: string,
    options: RequestOptions = {}
): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`;

    const headers: Record<string, string> = {
        "Content-Type": "application/json",
        ...options.headers,
    };

    // Attach CSRF token for unsafe methods
    const method = (options.method || "GET").toUpperCase();
    if (!["GET", "HEAD", "OPTIONS"].includes(method)) {
        const csrf = getCSRFCookie();
        console.log(`[API] ${method} ${endpoint} - CSRF token:`, csrf ? 'present' : 'missing');
        if (csrf && !("X-CSRFToken" in headers)) {
            headers["X-CSRFToken"] = csrf;
        }
    }

    console.log(`[API] ${method} ${url} - credentials: include, cookies:`, document.cookie);

    const response = await fetch(url, {
        ...options,
        headers,
        credentials: "include", // Include cookies for session auth
    });

    console.log(`[API] ${method} ${endpoint} - response status:`, response.status);

    if (!response.ok) {
        // Handle 401/403 as authentication errors
        if (response.status === 401 || response.status === 403) {
            const error = new Error('認証が必要です。ログインしてください。');
            (error as any).status = response.status;
            throw error;
        }

        const errorData: ApiErrorResponse = await response.json().catch(() => ({}));
        // Compose a helpful message from field errors when detail is missing
        let message = (errorData && (errorData as any).detail) as string | undefined;
        if (!message && errorData && typeof errorData === 'object') {
            const parts: string[] = [];
            for (const [k, v] of Object.entries(errorData)) {
                if (k === 'detail') continue;
                if (Array.isArray(v)) {
                    parts.push(`${k}: ${v.join(', ')}`);
                } else if (v != null) {
                    parts.push(`${k}: ${String(v)}`);
                }
            }
            if (parts.length) {
                message = parts.join(' | ');
            }
        }
        const error = new Error(
            message || `HTTP ${response.status}: ${response.statusText}`
        );
        (error as any).status = response.status;
        (error as any).data = errorData;
        throw error;
    }

    // Gracefully handle empty responses (e.g., 204 No Content on DELETE)
    if (response.status === 204) {
        return undefined as unknown as T;
    }

    // Try to parse JSON if content-type indicates JSON; otherwise return undefined
    const contentType = response.headers.get("content-type") || "";
    if (!contentType.includes("application/json")) {
        // Attempt to read text to consume the body; ignore if empty
        await response.text().catch(() => "");
        return undefined as unknown as T;
    }

    // Parse JSON with fallback for empty body
    try {
        const data: T = await response.json();
        return data;
    } catch {
        return undefined as unknown as T;
    }
}

// ============================================================================
// Authentication Endpoints
// ============================================================================

export const authAPI = {
    /**
     * POST /auth/login
     * Login with username and password
     */
    async login(username: string, password: string): Promise<User> {
        return apiRequest<User>("auth/login/", {
            method: "POST",
            body: JSON.stringify({ username, password }),
        });
    },

    /**
     * GET /auth/me
     * Get current authenticated user
     */
    async me(): Promise<User> {
        return apiRequest<User>("auth/me/");
    },

    /**
     * POST /auth/logout
     * Logout current user (clears session)
     */
    async logout(): Promise<void> {
        return apiRequest<void>("auth/logout/", {
            method: "POST",
        });
    },
};

// ============================================================================
// Holdings Endpoints
// ============================================================================

export const holdingsAPI = {
    /**
     * GET /holdings
     * List all investment holdings for current user with pagination
     */
    async list(page = 1, pageSize = 50): Promise<HoldingsListResponse> {
        return apiRequest<HoldingsListResponse>(
            `holdings/?page=${page}&page_size=${pageSize}`
        );
    },

    /**
     * GET /holdings/{id}
     * Retrieve a specific holding by ID
     */
    async get(id: number): Promise<InvestmentHolding> {
        return apiRequest<InvestmentHolding>(`holdings/${id}/`);
    },

    /**
     * POST /holdings
     * Create a new investment holding
     */
    async create(holding: Omit<InvestmentHolding, "id" | "user" | "created_at" | "updated_at">): Promise<InvestmentHolding> {
        // Remove undefined fields to avoid sending them to the backend
        const cleanedHolding = Object.fromEntries(
            Object.entries(holding).filter(([_, value]) => value !== undefined)
        );
        return apiRequest<InvestmentHolding>("holdings/", {
            method: "POST",
            body: JSON.stringify(cleanedHolding),
        });
    },

    /**
     * PUT /holdings/{id}
     * Update an existing holding (full replacement)
     */
    async update(
        id: number,
        holding: Omit<InvestmentHolding, "id" | "user" | "created_at" | "updated_at">
    ): Promise<InvestmentHolding> {
        // Remove undefined fields to avoid sending them to the backend
        const cleanedHolding = Object.fromEntries(
            Object.entries(holding).filter(([_, value]) => value !== undefined)
        );
        return apiRequest<InvestmentHolding>(`holdings/${id}/`, {
            method: "PUT",
            body: JSON.stringify(cleanedHolding),
        });
    },

    /**
     * PATCH /holdings/{id}
     * Partial update to an existing holding
     */
    async patch(
        id: number,
        updates: Partial<Omit<InvestmentHolding, "id" | "user" | "created_at" | "updated_at">>
    ): Promise<InvestmentHolding> {
        return apiRequest<InvestmentHolding>(`holdings/${id}/`, {
            method: "PATCH",
            body: JSON.stringify(updates),
        });
    },

    /**
     * DELETE /holdings/{id}
     * Delete a holding
     */
    async delete(id: number): Promise<void> {
        return apiRequest<void>(`holdings/${id}/`, {
            method: "DELETE",
        });
    },

    /**
     * GET /holdings/nisa-usage
     * Get current year's annual NISA remaining and lifetime remaining
     */
    async getNisaUsage(): Promise<NISARemainingResponse> {
        return apiRequest<NISARemainingResponse>("holdings/nisa-usage/");
    },
};

// ============================================================================
// Portfolio Summary Endpoints
// ============================================================================

export const portfolioAPI = {
    /**
     * GET /portfolio/summary
     * Get portfolio summary: total value, composition by region/account type/asset class
     */
    async getSummary(): Promise<PortfolioSummary> {
        return apiRequest<PortfolioSummary>("portfolio/summary/");
    },
};

// ============================================================================
// Recurring Plans Endpoints
// ============================================================================

export const recurringPlansAPI = {
    /**
     * GET /recurring-plans
     * List all recurring investment plans for current user
     */
    async list(page = 1, pageSize = 50): Promise<RecurringPlansListResponse> {
        return apiRequest<RecurringPlansListResponse>(
            `recurring-plans/?page=${page}&page_size=${pageSize}`
        );
    },

    /**
     * GET /recurring-plans/{id}
     * Retrieve a specific plan by ID
     */
    async get(id: number): Promise<RecurringInvestmentPlan> {
        return apiRequest<RecurringInvestmentPlan>(`recurring-plans/${id}/`);
    },

    /**
     * POST /recurring-plans
     * Create a new recurring investment plan
     */
    async create(plan: Omit<RecurringInvestmentPlan, "id" | "user" | "created_at" | "updated_at">): Promise<RecurringInvestmentPlan> {
        // Clean payload: drop undefined and normalize empty strings to null for optional fields
        const cleanedEntries = Object.entries(plan)
            .filter(([_, v]) => v !== undefined)
            .map(([k, v]) => {
                if ((k === 'end_date' || k === 'bonus_months') && v === "") return [k, null];
                return [k, v];
            });
        const cleanedPlan = Object.fromEntries(cleanedEntries);
        return apiRequest<RecurringInvestmentPlan>("recurring-plans/", {
            method: "POST",
            body: JSON.stringify(cleanedPlan),
        });
    },

    /**
     * PUT /recurring-plans/{id}
     * Update an existing plan (full replacement)
     */
    async update(
        id: number,
        plan: Omit<RecurringInvestmentPlan, "id" | "user" | "created_at" | "updated_at">
    ): Promise<RecurringInvestmentPlan> {
        const cleanedEntries = Object.entries(plan)
            .filter(([_, v]) => v !== undefined)
            .map(([k, v]) => {
                if ((k === 'end_date' || k === 'bonus_months') && v === "") return [k, null];
                return [k, v];
            });
        const cleanedPlan = Object.fromEntries(cleanedEntries);
        return apiRequest<RecurringInvestmentPlan>(`recurring-plans/${id}/`, {
            method: "PUT",
            body: JSON.stringify(cleanedPlan),
        });
    },

    /**
     * PATCH /recurring-plans/{id}
     * Partial update to an existing plan
     */
    async patch(
        id: number,
        updates: Partial<Omit<RecurringInvestmentPlan, "id" | "user" | "created_at" | "updated_at">>
    ): Promise<RecurringInvestmentPlan> {
        return apiRequest<RecurringInvestmentPlan>(`recurring-plans/${id}/`, {
            method: "PATCH",
            body: JSON.stringify(updates),
        });
    },

    /**
     * DELETE /recurring-plans/{id}
     * Delete a recurring plan
     */
    async delete(id: number): Promise<void> {
        return apiRequest<void>(`recurring-plans/${id}/`, {
            method: "DELETE",
        });
    },
};

// ============================================================================
// Projections Endpoints
// ============================================================================

export const projectionsAPI = {
    /**
     * GET /projections
     * List all projections for current user
     */
    async list(page = 1, pageSize = 50): Promise<ProjectionsListResponse> {
        return apiRequest<ProjectionsListResponse>(
            `projections/?page=${page}&page_size=${pageSize}`
        );
    },

    /**
     * GET /projections/{id}
     * Retrieve a specific projection by ID
     */
    async get(id: number): Promise<Projection> {
        return apiRequest<Projection>(`projections/${id}/`);
    },

    /**
     * POST /projections
     * Calculate and create a new projection
     * Accepts: projection_years, annual_return_rate (both required)
     * Returns: Full projection with calculated values
     */
    async create(projectionData: {
        projection_years: number;
        annual_return_rate: number;
    }): Promise<Projection> {
        return apiRequest<Projection>("projections/", {
            method: "POST",
            body: JSON.stringify(projectionData),
        });
    },
};

// ============================================================================
// Export all API modules
// ============================================================================

export const api = {
    auth: authAPI,
    holdings: holdingsAPI,
    portfolio: portfolioAPI,
    recurringPlans: recurringPlansAPI,
    projections: projectionsAPI,
    // Backwards-compatible aliases
    holdingsAPI: holdingsAPI,
    recurringPlansAPI: recurringPlansAPI,
    projectionsAPI: projectionsAPI,
};

export default api;

/**
 * Convenience method to create a projection
 * Used in components that import { apiClient } from this module
 */
export async function createProjection(data: {
    projection_years: number;
    annual_return_rate: number;
}): Promise<Projection> {
    return projectionsAPI.create(data);
}

/**
 * Convenience export combining all API functions
 */
export const apiClient = {
    ...api,
    createProjection,
};
