/**
 * HoldingsForm Component
 * Form for creating and editing investment holdings
 * Handles input validation and API communication
 */

"use client";

import { api, InvestmentHolding } from "@/services/api";
import { useState } from "react";

interface HoldingsFormProps {
    onSuccess?: (holding: InvestmentHolding) => void;
    onError?: (error: string) => void;
    initialValues?: Partial<InvestmentHolding>;
    isEditing?: boolean;
    holdingId?: number;
}

export function HoldingsForm({
    onSuccess,
    onError,
    initialValues,
    isEditing = false,
    holdingId,
}: HoldingsFormProps) {
    const [formData, setFormData] = useState<
        Omit<InvestmentHolding, "id" | "user" | "created_at" | "updated_at">
    >({
        account_type: initialValues?.account_type || "NISA_TSUMITATE",
        asset_class: initialValues?.asset_class || "MUTUAL_FUND",
        asset_region: initialValues?.asset_region || "DOMESTIC_STOCKS",
        asset_identifier: initialValues?.asset_identifier || "",
        asset_name: initialValues?.asset_name || "",
        current_amount_jpy: initialValues?.current_amount_jpy || 0,
        purchase_date: initialValues?.purchase_date || undefined,
    });

    const [loading, setLoading] = useState(false);
    const [errors, setErrors] = useState<Record<string, string>>({});
    // 金額表示用の状態（カンマ付き文字列）
    const [amountDisplay, setAmountDisplay] = useState(
        initialValues?.current_amount_jpy
            ? Number(initialValues.current_amount_jpy).toLocaleString("ja-JP")
            : ""
    );

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>
    ) => {
        const { name, value, type } = e.target;

        // 金額フィールドの特別処理
        if (name === "current_amount_jpy") {
            const numericValue = value.replace(/,/g, "");
            if (numericValue === "") {
                setFormData((prev) => ({ ...prev, current_amount_jpy: 0 }));
                setAmountDisplay("");
            } else {
                const parsedValue = parseFloat(numericValue);
                if (!Number.isFinite(parsedValue)) {
                    // 入力途中の「-」等はそのまま表示し、数値は更新しない
                    setAmountDisplay(value);
                } else {
                    setFormData((prev) => ({
                        ...prev,
                        current_amount_jpy: parsedValue,
                    }));
                    setAmountDisplay(parsedValue.toLocaleString("ja-JP"));
                }
            }
        } else {
            const finalValue =
                type === "number" ? (value ? parseFloat(value) : 0) : value;

            setFormData((prev) => ({
                ...prev,
                [name]: finalValue,
            }));
        }

        // Clear error for this field when user starts typing
        if (errors[name]) {
            setErrors((prev) => {
                const newErrors = { ...prev };
                delete newErrors[name];
                return newErrors;
            });
        }
    };

    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        if (!formData.asset_identifier.trim()) {
            newErrors.asset_identifier = "資産識別コードは必須です";
        }
        if (!formData.asset_name.trim()) {
            newErrors.asset_name = "資産名は必須です";
        }
        if (formData.current_amount_jpy < 0) {
            newErrors.current_amount_jpy = "金額は0以上である必要があります";
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!validateForm()) {
            return;
        }

        setLoading(true);

        try {
            let result: InvestmentHolding;

            if (isEditing && holdingId) {
                result = await api.holdings.update(holdingId, formData);
            } else {
                result = await api.holdings.create(formData);
            }

            if (onSuccess) {
                onSuccess(result);
            }

            // Reset form on successful creation
            if (!isEditing) {
                setFormData({
                    account_type: "NISA_TSUMITATE",
                    asset_class: "MUTUAL_FUND",
                    asset_region: "DOMESTIC_STOCKS",
                    asset_identifier: "",
                    asset_name: "",
                    current_amount_jpy: 0,
                });
                setAmountDisplay("");
            }
        } catch (error) {
            const err = error as { data?: { detail?: string }; message?: string };
            const errorMessage =
                err.data?.detail || err.message || "資産の保存に失敗しました";
            setErrors({ form: errorMessage });
            if (onError) {
                onError(errorMessage);
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Display */}
            {errors.form && (
                <div className="rounded-md bg-red-50 p-4">
                    <p className="text-sm font-medium text-red-800">{errors.form}</p>
                </div>
            )}

            {/* Account Type */}
            <div>
                <label htmlFor="account_type" className="block text-sm font-medium">
                    口座種別 *
                </label>
                <select
                    id="account_type"
                    name="account_type"
                    value={formData.account_type}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                >
                    <option value="NISA_TSUMITATE">NISA (つみたて投資枠)</option>
                    <option value="NISA_GROWTH">NISA (成長投資枠)</option>
                    <option value="GENERAL">一般口座</option>
                </select>
            </div>

            {/* Asset Class */}
            <div>
                <label htmlFor="asset_class" className="block text-sm font-medium">
                    資産クラス *
                </label>
                <select
                    id="asset_class"
                    name="asset_class"
                    value={formData.asset_class}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                >
                    <option value="INDIVIDUAL_STOCK">個別株式</option>
                    <option value="MUTUAL_FUND">投資信託</option>
                    <option value="CRYPTOCURRENCY">暗号資産</option>
                    <option value="REIT">不動産投信</option>
                    <option value="GOVERNMENT_BOND">国債</option>
                    <option value="OTHER">その他</option>
                </select>
            </div>

            {/* Investment Destination */}
            <div>
                <label htmlFor="asset_region" className="block text-sm font-medium">
                    投資先 *
                </label>
                <select
                    id="asset_region"
                    name="asset_region"
                    value={formData.asset_region}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                >
                    <option value="DOMESTIC_STOCKS">国内株式</option>
                    <option value="INTERNATIONAL_STOCKS">海外株式</option>
                    <option value="DOMESTIC_BONDS">国内債券</option>
                    <option value="INTERNATIONAL_BONDS">海外債券</option>
                    <option value="DOMESTIC_REITS">国内不動産投信</option>
                    <option value="INTERNATIONAL_REITS">海外不動産投信</option>
                    <option value="CRYPTOCURRENCY">暗号資産</option>
                    <option value="OTHER">その他</option>
                </select>
            </div>

            {/* Asset Identifier */}
            <div>
                <label htmlFor="asset_identifier" className="block text-sm font-medium">
                    資産識別コード *
                </label>
                <input
                    type="text"
                    id="asset_identifier"
                    name="asset_identifier"
                    value={formData.asset_identifier}
                    onChange={handleChange}
                    placeholder="例: JP0123456789, AAPL"
                    className={`mt-1 block w-full rounded-md border px-3 py-2 ${errors.asset_identifier ? "border-red-500" : "border-gray-300"
                        }`}
                />
                {errors.asset_identifier && (
                    <p className="mt-1 text-sm text-red-600">{errors.asset_identifier}</p>
                )}
            </div>

            {/* Asset Name */}
            <div>
                <label htmlFor="asset_name" className="block text-sm font-medium">
                    資産名 *
                </label>
                <input
                    type="text"
                    id="asset_name"
                    name="asset_name"
                    value={formData.asset_name}
                    onChange={handleChange}
                    placeholder="例: eMAXIS Slim 全世界株式, Apple Inc."
                    className={`mt-1 block w-full rounded-md border px-3 py-2 ${errors.asset_name ? "border-red-500" : "border-gray-300"
                        }`}
                />
                {errors.asset_name && (
                    <p className="mt-1 text-sm text-red-600">{errors.asset_name}</p>
                )}
            </div>

            {/* Current Amount (JPY) */}
            <div>
                <label
                    htmlFor="current_amount_jpy"
                    className="block text-sm font-medium"
                >
                    現在の金額 (円) *
                </label>
                <input
                    type="text"
                    id="current_amount_jpy"
                    name="current_amount_jpy"
                    value={amountDisplay}
                    onChange={handleChange}
                    placeholder="例: 100,000"
                    className={`mt-1 block w-full rounded-md border px-3 py-2 ${errors.current_amount_jpy ? "border-red-500" : "border-gray-300"
                        }`}
                />
                {errors.current_amount_jpy && (
                    <p className="mt-1 text-sm text-red-600">
                        {errors.current_amount_jpy}
                    </p>
                )}
            </div>

            {/* Purchase Date (Optional) */}
            <div>
                <label htmlFor="purchase_date" className="block text-sm font-medium">
                    購入日 (任意)
                </label>
                <input
                    type="date"
                    id="purchase_date"
                    name="purchase_date"
                    value={formData.purchase_date ? String(formData.purchase_date) : ""}
                    onChange={handleChange}
                    className="mt-1 block w-full rounded-md border border-gray-300 px-3 py-2"
                />
            </div>

            {/* Submit Button */}
            <button
                type="submit"
                disabled={loading}
                className="w-full rounded-md bg-blue-600 px-4 py-2 text-white hover:bg-blue-700 disabled:bg-gray-400"
            >
                {loading
                    ? isEditing
                        ? "更新中..."
                        : "登録中..."
                    : isEditing
                        ? "資産を更新"
                        : "資産を追加"}
            </button>
        </form>
    );
}
