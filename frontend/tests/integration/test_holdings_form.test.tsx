/**
 * Integration tests for HoldingsForm component
 * Tests form submission, validation, and API integration
 */

import { HoldingsForm } from "@/components/HoldingsForm";
import * as api from "@/services/api";
import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";

// Mock the API module
jest.mock("@/services/api");

describe("HoldingsForm", () => {
    beforeEach(() => {
        jest.clearAllMocks();
        // Ensure both legacy and current API namespaces are available on the mocked module
        (api as any).holdings = (api as any).holdings || {};
        (api as any).holdings.create = jest.fn();
        (api as any).holdings.update = jest.fn();
    });

    it("renders form with required fields", () => {
        render(<HoldingsForm />);

        expect(screen.getByLabelText(/口座種別/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/資産クラス/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/投資先/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/資産識別コード/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/資産名/i)).toBeInTheDocument();
        expect(screen.getByLabelText(/現在の金額/i)).toBeInTheDocument();
        expect(screen.getByRole("button", { name: /資産を追加/i })).toBeInTheDocument();
    });

    it("displays default values for select fields", () => {
        render(<HoldingsForm />);

        const accountTypeSelect = screen.getByLabelText(/口座種別/i) as HTMLSelectElement;
        const assetClassSelect = screen.getByLabelText(/資産クラス/i) as HTMLSelectElement;
        const regionSelect = screen.getByLabelText(/投資先/i) as HTMLSelectElement;

        expect(accountTypeSelect.value).toBe("NISA_TSUMITATE");
        expect(assetClassSelect.value).toBe("MUTUAL_FUND");
        expect(regionSelect.value).toBe("DOMESTIC_STOCKS");
    });

    it("validates required fields on submit", async () => {
        const user = userEvent.setup();
        render(<HoldingsForm />);

        const submitButton = screen.getByRole("button", { name: /資産を追加/i });
        await user.click(submitButton);

        // Should show validation errors
        await waitFor(() => {
            expect(screen.getByText(/資産識別コードは必須です/i)).toBeInTheDocument();
            expect(screen.getByText(/資産名は必須です/i)).toBeInTheDocument();
        });

        // API should not be called
        expect(api.holdingsAPI.create).not.toHaveBeenCalled();
    });

    it("validates non-negative amount", async () => {
        const user = userEvent.setup();
        render(<HoldingsForm />);

        const amountInput = screen.getByLabelText(/現在の金額/i);
        await user.clear(amountInput);
        await user.type(amountInput, "-1000");

        const submitButton = screen.getByRole("button", { name: /資産を追加/i });
        await user.click(submitButton);

        await waitFor(() => {
            expect(screen.getByText(/金額は0以上である必要があります/i)).toBeInTheDocument();
        });

        expect(api.holdingsAPI.create).not.toHaveBeenCalled();
    });

    it("submits form with valid data", async () => {
        const user = userEvent.setup();
        const mockOnSuccess = jest.fn();
        const mockHolding = {
            id: 1,
            user: 1,
            account_type: "NISA" as const,
            asset_class: "MUTUAL_FUND" as const,
            asset_region: "DOMESTIC_STOCKS" as const,
            asset_identifier: "JP0123456789",
            asset_name: "Test Fund",
            current_amount_jpy: 100000,
            created_at: "2025-01-01T00:00:00Z",
            updated_at: "2025-01-01T00:00:00Z",
        };

        (api.holdingsAPI.create as jest.Mock).mockResolvedValue(mockHolding);
        (api.holdings.create as unknown as jest.Mock).mockResolvedValue(mockHolding);

        render(<HoldingsForm onSuccess={mockOnSuccess} />);

        // Fill in the form
        const identifierInput = screen.getByLabelText(/資産識別コード/i);
        const nameInput = screen.getByLabelText(/資産名/i);
        const amountInput = screen.getByLabelText(/現在の金額/i);

        await user.clear(identifierInput);
        await user.type(identifierInput, "JP0123456789");

        await user.clear(nameInput);
        await user.type(nameInput, "Test Fund");

        await user.clear(amountInput);
        await user.type(amountInput, "100000");

        // Submit form
        const submitButton = screen.getByRole("button", { name: /資産を追加/i });
        await user.click(submitButton);

        // Check callback was called
        expect(mockOnSuccess).toHaveBeenCalledWith(mockHolding);
    });

    it("displays API error message on submit failure", async () => {
        const user = userEvent.setup();
        const mockOnError = jest.fn();
        const errorMessage = "Duplicate holding for this user";

        (api.holdingsAPI.create as jest.Mock).mockRejectedValue(
            new Error(errorMessage)
        );
        (api.holdings.create as unknown as jest.Mock).mockRejectedValue(new Error(errorMessage));

        render(
            <HoldingsForm onSuccess={jest.fn()} onError={mockOnError} />
        );

        // Fill in required fields
        const identifierInput = screen.getByLabelText(/資産識別コード/i);
        const nameInput = screen.getByLabelText(/資産名/i);
        const amountInput = screen.getByLabelText(/現在の金額/i);

        await user.type(identifierInput, "JP0123456789");
        await user.type(nameInput, "Test Fund");
        await user.type(amountInput, "100000");

        // Submit
        const submitButton = screen.getByRole("button", { name: /資産を追加/i });
        await user.click(submitButton);

        // Wait for error display
        await waitFor(() => {
            expect(mockOnError).toHaveBeenCalledWith(errorMessage);
        });
    });

    it("shows editing mode when provided with initialValues", () => {
        const initialValues = {
            account_type: "GENERAL" as const,
            asset_class: "INDIVIDUAL_STOCK" as const,
            asset_region: "INTERNATIONAL_STOCKS" as const,
            asset_identifier: "AAPL",
            asset_name: "Apple Inc.",
            current_amount_jpy: 50000,
        };

        render(
            <HoldingsForm
                isEditing={true}
                holdingId={1}
                initialValues={initialValues}
            />
        );

        expect(screen.getByRole("button", { name: /資産を更新/i })).toBeInTheDocument();

        const accountTypeSelect = screen.getByLabelText(/口座種別/i) as HTMLSelectElement;
        expect(accountTypeSelect.value).toBe("GENERAL");
    });

    it("calls update API when editing", async () => {
        const user = userEvent.setup();
        const mockOnSuccess = jest.fn();
        const mockHolding = {
            id: 1,
            user: 1,
            account_type: "GENERAL" as const,
            asset_class: "INDIVIDUAL_STOCK" as const,
            asset_region: "INTERNATIONAL_STOCKS" as const,
            asset_identifier: "AAPL",
            asset_name: "Apple Inc.",
            current_amount_jpy: 75000,
            created_at: "2025-01-01T00:00:00Z",
            updated_at: "2025-01-02T00:00:00Z",
        };

        (api.holdingsAPI.update as jest.Mock).mockResolvedValue(mockHolding);
        (api.holdings.update as unknown as jest.Mock).mockResolvedValue(mockHolding);

        const initialValues = {
            account_type: "GENERAL" as const,
            asset_class: "INDIVIDUAL_STOCK" as const,
            asset_region: "INTERNATIONAL_STOCKS" as const,
            asset_identifier: "AAPL",
            asset_name: "Apple Inc.",
            current_amount_jpy: 50000,
        };

        render(
            <HoldingsForm
                isEditing={true}
                holdingId={1}
                initialValues={initialValues}
                onSuccess={mockOnSuccess}
            />
        );

        // Update amount
        const amountInput = screen.getByLabelText(/現在の金額/i);
        await user.clear(amountInput);
        await user.type(amountInput, "75000");

        // Submit
        const submitButton = screen.getByRole("button", { name: /資産を更新/i });
        await user.click(submitButton);

        expect(mockOnSuccess).toHaveBeenCalledWith(mockHolding);
    });

    it("resets form after successful creation", async () => {
        const user = userEvent.setup();
        const mockHolding = {
            id: 1,
            user: 1,
            account_type: "NISA" as const,
            asset_class: "MUTUAL_FUND" as const,
            asset_region: "DOMESTIC_STOCKS" as const,
            asset_identifier: "JP0123456789",
            asset_name: "Test Fund",
            current_amount_jpy: 100000,
            created_at: "2025-01-01T00:00:00Z",
            updated_at: "2025-01-01T00:00:00Z",
        };

        (api.holdingsAPI.create as jest.Mock).mockResolvedValue(mockHolding);
        (api.holdings.create as unknown as jest.Mock).mockResolvedValue(mockHolding);

        render(<HoldingsForm isEditing={false} />);

        const identifierInput = screen.getByLabelText(/資産識別コード/i) as HTMLInputElement;
        const nameInput = screen.getByLabelText(/資産名/i) as HTMLInputElement;
        const amountInput = screen.getByLabelText(/現在の金額/i) as HTMLInputElement;

        await user.type(identifierInput, "JP0123456789");
        await user.type(nameInput, "Test Fund");
        await user.type(amountInput, "100000");

        const submitButton = screen.getByRole("button", { name: /資産を追加/i });
        await user.click(submitButton);

        // Wait for form reset
        await waitFor(() => {
            expect(identifierInput.value).toBe("");
            expect(nameInput.value).toBe("");
            expect(amountInput.value).toBe("");
        });
    });

    it("displays loading state during submission", async () => {
        const user = userEvent.setup();

        // Make the API call hang
        (api.holdingsAPI.create as jest.Mock).mockImplementationOnce(
            () => new Promise(() => {
                // Intentionally never resolves for testing loading state
            })
        );
        (api.holdings.create as unknown as jest.Mock).mockImplementationOnce(
            () => new Promise(() => { })
        );

        render(<HoldingsForm />);

        const identifierInput = screen.getByLabelText(/資産識別コード/i);
        const nameInput = screen.getByLabelText(/資産名/i);

        await user.type(identifierInput, "JP0123456789");
        await user.type(nameInput, "Test Fund");

        const submitButton = screen.getByRole("button", { name: /資産を追加/i });
        await user.click(submitButton);

        // Button should show loading state
        expect(screen.getByRole("button", { name: /登録中/i })).toBeInTheDocument();
    });

    it("displays optional purchase date field", () => {
        render(<HoldingsForm />);

        expect(screen.getByLabelText(/購入日/i)).toBeInTheDocument();
    });

    it("accepts and displays purchase date", async () => {
        const user = userEvent.setup();
        const mockHolding = {
            id: 1,
            user: 1,
            account_type: "NISA" as const,
            asset_class: "MUTUAL_FUND" as const,
            asset_region: "DOMESTIC_STOCKS" as const,
            asset_identifier: "JP0123456789",
            asset_name: "Test Fund",
            current_amount_jpy: 100000,
            purchase_date: "2025-01-15",
            created_at: "2025-01-01T00:00:00Z",
            updated_at: "2025-01-01T00:00:00Z",
        };

        (api.holdingsAPI.create as jest.Mock).mockResolvedValue(mockHolding);
        (api.holdings.create as unknown as jest.Mock).mockResolvedValue(mockHolding);

        render(<HoldingsForm onSuccess={jest.fn()} />);

        const identifierInput = screen.getByLabelText(/資産識別コード/i);
        const nameInput = screen.getByLabelText(/資産名/i);
        const purchaseDateInput = screen.getByLabelText(/購入日/i) as HTMLInputElement;

        await user.type(identifierInput, "JP0123456789");
        await user.type(nameInput, "Test Fund");
        await user.type(purchaseDateInput, "2025-01-15");

        const submitButton = screen.getByRole("button", { name: /資産を追加/i });
        await user.click(submitButton);

        await waitFor(() => {
            expect(api.holdingsAPI.create).toHaveBeenCalledWith(
                expect.objectContaining({
                    purchase_date: "2025-01-15",
                })
            );
        });
    });
});
