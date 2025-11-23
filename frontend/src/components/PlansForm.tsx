"use client";

import { RecurringInvestmentPlan } from "@/services/api";
import { useState } from "react";

interface PlansFormProps {
    onSubmit: (plan: Omit<RecurringInvestmentPlan, "id" | "user" | "created_at" | "updated_at">) => Promise<void>;
    initialData?: RecurringInvestmentPlan | null;
    isLoading?: boolean;
    onCancel?: () => void;
}

export default function PlansForm({
    onSubmit,
    initialData,
    isLoading = false,
    onCancel,
}: PlansFormProps) {
    const isEditMode = !!initialData;

    const [formData, setFormData] = useState({
        target_asset_name: (initialData?.target_asset_name || "") as string,
        target_asset_identifier: (initialData?.target_asset_identifier || "") as string,
        target_account_type: (initialData?.target_account_type || "NISA_TSUMITATE") as "NISA_TSUMITATE" | "NISA_GROWTH" | "GENERAL",
        target_asset_class: (initialData?.target_asset_class || "MUTUAL_FUND") as
            | "INDIVIDUAL_STOCK"
            | "MUTUAL_FUND"
            | "CRYPTOCURRENCY"
            | "REIT"
            | "GOVERNMENT_BOND"
            | "OTHER",
        target_asset_region: (initialData?.target_asset_region || "DOMESTIC_STOCKS") as
            | "DOMESTIC_STOCKS"
            | "INTERNATIONAL_STOCKS"
            | "DOMESTIC_BONDS"
            | "INTERNATIONAL_BONDS"
            | "DOMESTIC_REITS"
            | "INTERNATIONAL_REITS"
            | "CRYPTOCURRENCY"
            | "OTHER",
        frequency: (initialData?.frequency || "MONTHLY") as "DAILY" | "MONTHLY" | "BONUS_MONTH",
        amount_jpy: initialData?.amount_jpy || 0,
        start_date: initialData?.start_date || "",
        end_date: initialData?.end_date || "",
        bonus_months: initialData?.bonus_months || "",
        continue_if_limit_exceeded: initialData?.continue_if_limit_exceeded || false,
    });

    // 金額の表示用（カンマ付き文字列）
    const [amountDisplay, setAmountDisplay] = useState(
        initialData?.amount_jpy
            ? Number(initialData.amount_jpy).toLocaleString("ja-JP")
            : ""
    );

    const [errors, setErrors] = useState<Record<string, string>>({});
    const [submitError, setSubmitError] = useState<string | null>(null);

    const handleChange = (
        e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement>
    ) => {
        const { name, value, type } = e.target;
        const checked = (e.target as HTMLInputElement).checked;

        // Clear error for this field when user starts editing
        if (errors[name]) {
            setErrors((prev) => {
                const newErrors = { ...prev };
                delete newErrors[name];
                return newErrors;
            });
        }

        if (name === "amount_jpy") {
            // 入力値からカンマを除去して数値化
            const numeric = value.replace(/,/g, "");
            const parsed = numeric ? parseFloat(numeric) : 0;
            setFormData((prev) => ({
                ...prev,
                amount_jpy: parsed,
            }));
            setAmountDisplay(numeric ? parsed.toLocaleString("ja-JP") : "");
            return;
        }

        setFormData((prev) => ({
            ...prev,
            [name]: type === "checkbox" ? checked : value,
        }));
    };

    const validateForm = (): boolean => {
        const newErrors: Record<string, string> = {};

        // Validate amount_jpy
        if (formData.amount_jpy <= 0) {
            newErrors.amount_jpy = "投資額は0より大きい値を入力してください";
        }

        // Validate start_date
        if (!formData.start_date) {
            newErrors.start_date = "開始日は必須です";
        }

        // Validate end_date if provided
        if (formData.end_date && formData.start_date && formData.end_date < formData.start_date) {
            newErrors.end_date = "終了日は開始日以降である必要があります";
        }

        // Validate bonus_months for BONUS_MONTH frequency
        if (formData.frequency === "BONUS_MONTH") {
            if (!formData.bonus_months) {
                newErrors.bonus_months = "ボーナス月を指定してください";
            } else {
                try {
                    const months = formData.bonus_months.split(",").map((m) => parseInt(m.trim(), 10));
                    for (const month of months) {
                        if (isNaN(month) || month < 1 || month > 12) {
                            newErrors.bonus_months = "ボーナス月は1～12の数値をカンマ区切りで入力してください";
                            break;
                        }
                    }
                } catch {
                    newErrors.bonus_months = "ボーナス月の形式が無効です";
                }
            }
        }

        setErrors(newErrors);
        return Object.keys(newErrors).length === 0;
    };

    const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setSubmitError(null);

        if (!validateForm()) {
            return;
        }

        try {
            await onSubmit(formData);
        } catch (error) {
            setSubmitError(
                error instanceof Error ? error.message : "フォーム送信に失敗しました"
            );
        }
    };

    return (
        <form onSubmit={handleSubmit} className="plans-form">
            <div className="form-section">
                <h3>{isEditMode ? "投資計画を編集" : "新しい投資計画を作成"}</h3>

                {submitError && <div className="form-error">{submitError}</div>}

                {/* Optional Name */}
                <div className="form-group">
                    <label htmlFor="target_asset_name">名称（任意）</label>
                    <input
                        id="target_asset_name"
                        type="text"
                        name="target_asset_name"
                        value={formData.target_asset_name}
                        onChange={handleChange}
                        disabled={isLoading}
                        placeholder="例：eMAXIS Slim 全世界株式"
                    />
                </div>

                {/* Optional Identifier */}
                <div className="form-group">
                    <label htmlFor="target_asset_identifier">コード（任意）</label>
                    <input
                        id="target_asset_identifier"
                        type="text"
                        name="target_asset_identifier"
                        value={formData.target_asset_identifier}
                        onChange={handleChange}
                        disabled={isLoading}
                        placeholder="例：123456、ISIN等"
                    />
                </div>

                {/* Target Account Type */}
                <div className="form-group">
                    <label htmlFor="target_account_type">口座種別 *</label>
                    <select
                        id="target_account_type"
                        name="target_account_type"
                        value={formData.target_account_type}
                        onChange={handleChange}
                        required
                        disabled={isLoading}
                    >
                        <option value="NISA_TSUMITATE">NISA (つみたて投資枠)</option>
                        <option value="NISA_GROWTH">NISA (成長投資枠)</option>
                        <option value="GENERAL">一般</option>
                    </select>
                    {errors.target_account_type && (
                        <span className="error-message">{errors.target_account_type}</span>
                    )}
                </div>

                {/* Target Asset Class */}
                <div className="form-group">
                    <label htmlFor="target_asset_class">資産クラス *</label>
                    <select
                        id="target_asset_class"
                        name="target_asset_class"
                        value={formData.target_asset_class}
                        onChange={handleChange}
                        required
                        disabled={isLoading}
                    >
                        <option value="INDIVIDUAL_STOCK">個別株</option>
                        <option value="MUTUAL_FUND">投資信託</option>
                        <option value="CRYPTOCURRENCY">暗号資産</option>
                        <option value="REIT">不動産投信</option>
                        <option value="GOVERNMENT_BOND">国債</option>
                        <option value="OTHER">その他</option>
                    </select>
                    {errors.target_asset_class && (
                        <span className="error-message">{errors.target_asset_class}</span>
                    )}
                </div>

                {/* Target Investment Destination */}
                <div className="form-group">
                    <label htmlFor="target_asset_region">投資先 *</label>
                    <select
                        id="target_asset_region"
                        name="target_asset_region"
                        value={formData.target_asset_region}
                        onChange={handleChange}
                        required
                        disabled={isLoading}
                    >
                        <option value="DOMESTIC_STOCKS">国内株</option>
                        <option value="INTERNATIONAL_STOCKS">海外株</option>
                        <option value="DOMESTIC_BONDS">国内債券</option>
                        <option value="INTERNATIONAL_BONDS">海外債券</option>
                        <option value="DOMESTIC_REITS">国内不動産投信</option>
                        <option value="INTERNATIONAL_REITS">海外不動産投信</option>
                        <option value="CRYPTOCURRENCY">暗号資産</option>
                        <option value="OTHER">その他</option>
                    </select>
                    {errors.target_asset_region && (
                        <span className="error-message">{errors.target_asset_region}</span>
                    )}
                </div>

                {/* Frequency */}
                <div className="form-group">
                    <label htmlFor="frequency">投資頻度 *</label>
                    <select
                        id="frequency"
                        name="frequency"
                        value={formData.frequency}
                        onChange={handleChange}
                        required
                        disabled={isLoading}
                    >
                        <option value="DAILY">毎日</option>
                        <option value="MONTHLY">毎月</option>
                        <option value="BONUS_MONTH">ボーナス月</option>
                    </select>
                    {errors.frequency && (
                        <span className="error-message">{errors.frequency}</span>
                    )}
                </div>

                {/* Amount */}
                <div className="form-group">
                    <label htmlFor="amount_jpy">投資額（円）*</label>
                    <input
                        id="amount_jpy"
                        type="text"
                        name="amount_jpy"
                        inputMode="decimal"
                        value={amountDisplay}
                        onChange={handleChange}
                        placeholder="例：10,000"
                        required
                        disabled={isLoading}
                    />
                    {errors.amount_jpy && (
                        <span className="error-message">{errors.amount_jpy}</span>
                    )}
                </div>

                {/* Start Date */}
                <div className="form-group">
                    <label htmlFor="start_date">開始日 *</label>
                    <input
                        id="start_date"
                        type="date"
                        name="start_date"
                        value={formData.start_date}
                        onChange={handleChange}
                        required
                        disabled={isLoading}
                    />
                    {errors.start_date && (
                        <span className="error-message">{errors.start_date}</span>
                    )}
                </div>

                {/* End Date */}
                <div className="form-group">
                    <label htmlFor="end_date">終了日</label>
                    <input
                        id="end_date"
                        type="date"
                        name="end_date"
                        value={formData.end_date}
                        onChange={handleChange}
                        disabled={isLoading}
                    />
                    {errors.end_date && (
                        <span className="error-message">{errors.end_date}</span>
                    )}
                </div>

                {/* Bonus Months (only shown for BONUS_MONTH frequency) */}
                {formData.frequency === "BONUS_MONTH" && (
                    <div className="form-group">
                        <label htmlFor="bonus_months">ボーナス月（カンマ区切り：1-12）</label>
                        <textarea
                            id="bonus_months"
                            name="bonus_months"
                            value={formData.bonus_months}
                            onChange={handleChange}
                            placeholder="例：6,12"
                            disabled={isLoading}
                            rows={2}
                        />
                        {errors.bonus_months && (
                            <span className="error-message">{errors.bonus_months}</span>
                        )}
                    </div>
                )}

                {/* Continue if limit exceeded (only for NISA accounts) */}
                {(formData.target_account_type === "NISA_TSUMITATE" ||
                    formData.target_account_type === "NISA_GROWTH") && (
                        <div className="form-group">
                            <label
                                htmlFor="continue_if_limit_exceeded"
                                style={{
                                    display: "flex",
                                    alignItems: "center",
                                    gap: "8px",
                                    cursor: "pointer",
                                }}
                            >
                                <input
                                    id="continue_if_limit_exceeded"
                                    type="checkbox"
                                    name="continue_if_limit_exceeded"
                                    checked={formData.continue_if_limit_exceeded}
                                    onChange={handleChange}
                                    disabled={isLoading}
                                    style={{ cursor: "pointer" }}
                                />
                                <span>NISA枠超過後も投資を継続（一般口座へ自動移行）</span>
                            </label>
                            <small style={{ color: "#666", marginTop: "4px", fontSize: "12px" }}>
                                ※ チェックを入れると、NISAの年間・生涯上限を超えた分は一般口座で投資が続きます。
                                <br />
                                チェックを外すと、上限超過時にエラーとなります。
                            </small>
                        </div>
                    )}

                {/* Form Actions */}
                <div className="form-actions">
                    <button
                        type="submit"
                        disabled={isLoading}
                        className="btn-primary"
                    >
                        {isLoading ? "送信中..." : isEditMode ? "更新" : "作成"}
                    </button>
                    {onCancel && (
                        <button
                            type="button"
                            onClick={onCancel}
                            disabled={isLoading}
                            className="btn-secondary"
                        >
                            キャンセル
                        </button>
                    )}
                </div>
            </div>

            <style>{`
                .plans-form {
                    width: 100%;
                    max-width: 600px;
                }

                .form-section {
                    background: #f9f9f9;
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 24px;
                }

                .form-section h3 {
                    margin: 0 0 20px 0;
                    font-size: 18px;
                    font-weight: 600;
                    color: #333;
                }

                .form-error {
                    background-color: #ffebee;
                    color: #c62828;
                    padding: 12px;
                    border-radius: 4px;
                    margin-bottom: 16px;
                    font-size: 14px;
                }

                .form-group {
                    margin-bottom: 16px;
                    display: flex;
                    flex-direction: column;
                }

                .form-group label {
                    font-weight: 500;
                    margin-bottom: 8px;
                    font-size: 14px;
                    color: #333;
                }

                .form-group input,
                .form-group select,
                .form-group textarea {
                    padding: 10px;
                    border: 1px solid #d0d0d0;
                    border-radius: 4px;
                    font-size: 14px;
                    font-family: inherit;
                }

                .form-group input:focus,
                .form-group select:focus,
                .form-group textarea:focus {
                    outline: none;
                    border-color: #2196f3;
                    box-shadow: 0 0 0 3px rgba(33, 150, 243, 0.1);
                }

                .form-group input:disabled,
                .form-group select:disabled,
                .form-group textarea:disabled {
                    background-color: #f5f5f5;
                    cursor: not-allowed;
                }

                .error-message {
                    color: #c62828;
                    font-size: 12px;
                    margin-top: 4px;
                }

                .form-actions {
                    display: flex;
                    gap: 12px;
                    margin-top: 24px;
                    padding-top: 16px;
                    border-top: 1px solid #e0e0e0;
                }

                .btn-primary,
                .btn-secondary {
                    padding: 10px 20px;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: background-color 0.2s;
                }

                .btn-primary {
                    background-color: #2196f3;
                    color: white;
                }

                .btn-primary:hover:not(:disabled) {
                    background-color: #1976d2;
                }

                .btn-secondary {
                    background-color: #f5f5f5;
                    color: #333;
                    border: 1px solid #d0d0d0;
                }

                .btn-secondary:hover:not(:disabled) {
                    background-color: #eeeeee;
                }

                button:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }
            `}</style>
        </form>
    );
}
