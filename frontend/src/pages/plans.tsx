"use client";

import PlansForm from "@/components/PlansForm";
import { withAuth } from "@/hoc/withAuth";
import { api, NISARemainingResponse, RecurringInvestmentPlan } from "@/services/api";
import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";

const FREQUENCY_LABELS: Record<string, string> = {
    DAILY: "毎日",
    MONTHLY: "毎月",
    BONUS_MONTH: "ボーナス月",
};

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
    NISA_TSUMITATE: "NISA (つみたて投資枠)",
    NISA_GROWTH: "NISA (成長投資枠)",
    GENERAL: "一般",
};

const ASSET_CLASS_LABELS: Record<string, string> = {
    INDIVIDUAL_STOCK: "個別株",
    MUTUAL_FUND: "投資信託",
    CRYPTOCURRENCY: "暗号資産",
    REIT: "不動産投信",
    GOVERNMENT_BOND: "国債",
    OTHER: "その他",
};

const ASSET_REGION_LABELS: Record<string, string> = {
    DOMESTIC_STOCKS: "国内株",
    INTERNATIONAL_STOCKS: "海外株",
    DOMESTIC_BONDS: "国内債券",
    INTERNATIONAL_BONDS: "海外債券",
    DOMESTIC_REITS: "国内不動産投信",
    INTERNATIONAL_REITS: "海外不動産投信",
    CRYPTOCURRENCY: "暗号資産",
    OTHER: "その他",
};

interface PageState {
    plans: RecurringInvestmentPlan[];
    loading: boolean;
    error: string | null;
    showForm: boolean;
    editingId: number | null;
    currentPage: number;
    totalPages: number;
    submitLoading: boolean;
}

function PlansPage() {
    const [state, setState] = useState<PageState>({
        plans: [],
        loading: true,
        error: null,
        showForm: false,
        editingId: null,
        currentPage: 1,
        totalPages: 1,
        submitLoading: false,
    });

    // NISA残枠（年間・生涯）
    const [nisa, setNisa] = useState<NISARemainingResponse | null>(null);

    // Load plans data
    const loadPlans = useCallback(async (page = 1) => {
        try {
            setState((prev) => ({ ...prev, loading: true, error: null }));
            const response = await api.recurringPlans.list(page, 10);
            const totalPages = Math.ceil(response.count / 10);

            setState((prev) => ({
                ...prev,
                plans: response.results,
                currentPage: page,
                totalPages,
                loading: false,
            }));
        } catch (error) {
            setState((prev) => ({
                ...prev,
                plans: [],
                error:
                    error instanceof Error
                        ? error.message
                        : "投資計画の読み込みに失敗しました",
                loading: false,
            }));
        }
    }, []);

    // Initial load
    useEffect(() => {
        loadPlans(1);
    }, [loadPlans]);

    // Load NISA remaining (annual & lifetime)
    useEffect(() => {
        (async () => {
            try {
                const usage = await api.holdings.getNisaUsage();
                setNisa(usage);
            } catch (e) {
                // 非致命的: 取得失敗時はNISAカードを非表示
                setNisa(null);
            }
        })();
    }, []);

    const handleAddClick = () => {
        setState((prev) => ({ ...prev, showForm: true, editingId: null }));
    };

    const handleEditClick = (id: number) => {
        setState((prev) => ({ ...prev, editingId: id, showForm: true }));
    };

    const handleCancel = () => {
        setState((prev) => ({ ...prev, showForm: false, editingId: null }));
    };

    const handleDeleteClick = async (id: number) => {
        if (
            !confirm(
                "この投資計画を削除してもよろしいですか？"
            )
        ) {
            return;
        }

        try {
            setState((prev) => ({ ...prev, submitLoading: true }));
            await api.recurringPlans.delete(id);
            await loadPlans(state.currentPage);
            setState((prev) => ({ ...prev, submitLoading: false }));
        } catch (error) {
            setState((prev) => ({
                ...prev,
                error:
                    error instanceof Error
                        ? error.message
                        : "投資計画の削除に失敗しました",
                submitLoading: false,
            }));
        }
    };

    const handleFormSubmit = async (
        plan: Omit<RecurringInvestmentPlan, "id" | "user" | "created_at" | "updated_at">
    ) => {
        try {
            setState((prev) => ({ ...prev, submitLoading: true }));

            if (state.editingId) {
                // Update existing plan
                await api.recurringPlans.update(state.editingId, plan);
            } else {
                // Create new plan
                await api.recurringPlans.create(plan);
            }

            // Reset form and reload data
            setState((prev) => ({
                ...prev,
                showForm: false,
                editingId: null,
                submitLoading: false,
            }));

            await loadPlans(state.currentPage);
        } catch (error) {
            setState((prev) => ({
                ...prev,
                submitLoading: false,
            }));
            throw error;
        }
    };

    const editingPlan = state.editingId
        ? state.plans.find((p) => p.id === state.editingId)
        : null;

    const formatDate = (dateString?: string | null) => {
        if (!dateString) return "-";
        const date = new Date(dateString);
        return date.toLocaleDateString("ja-JP");
    };

    const formatAmount = (amount: number) => {
        return new Intl.NumberFormat("ja-JP", {
            style: "currency",
            currency: "JPY",
            minimumFractionDigits: 0,
            maximumFractionDigits: 2,
        }).format(amount);
    };

    // Calculate investment totals
    const totals = useMemo(() => {
        const result = {
            daily: 0,
            monthly: 0,
            annual: 0,
        };

        state.plans.forEach((plan) => {
            const amount = typeof plan.amount_jpy === 'number'
                ? plan.amount_jpy
                : parseFloat(String(plan.amount_jpy)) || 0;

            // 暗号資産は365日、それ以外は営業日のみ（約245日/年、約20日/月）
            const isCrypto = plan.target_asset_region === "CRYPTOCURRENCY" ||
                plan.target_asset_class === "CRYPTOCURRENCY";
            const tradingDaysPerYear = isCrypto ? 365 : 245;  // 営業日は約245日/年
            const tradingDaysPerMonth = isCrypto ? 30 : 20;   // 営業日は約20日/月

            switch (plan.frequency) {
                case "DAILY":
                    result.daily += amount;
                    result.monthly += amount * tradingDaysPerMonth;
                    result.annual += amount * tradingDaysPerYear;
                    break;
                case "MONTHLY":
                    result.daily += amount / tradingDaysPerMonth;
                    result.monthly += amount;
                    result.annual += amount * 12;
                    break;
                case "BONUS_MONTH":
                    const bonusCount = plan.bonus_months
                        ? plan.bonus_months.split(",").map(m => m.trim()).filter(Boolean).length
                        : 0;
                    result.annual += amount * bonusCount;
                    result.monthly += (amount * bonusCount) / 12; // Average per month
                    result.daily += (amount * bonusCount) / tradingDaysPerYear; // Average per trading day
                    break;
            }
        });

        return result;
    }, [state.plans]);

    const nisaAnnualEligible = useMemo(() => {
        if (!nisa) return null;

        const annualPlan = {
            tsumitate: 0,
            growth: 0,
        } as { tsumitate: number; growth: number };

        state.plans.forEach((plan) => {
            if (
                plan.target_account_type !== "NISA_TSUMITATE" &&
                plan.target_account_type !== "NISA_GROWTH"
            )
                return;

            const amount = typeof plan.amount_jpy === 'number'
                ? plan.amount_jpy
                : parseFloat(String(plan.amount_jpy)) || 0;

            const isCrypto = plan.target_asset_region === "CRYPTOCURRENCY" ||
                plan.target_asset_class === "CRYPTOCURRENCY";
            const tradingDaysPerYear = isCrypto ? 365 : 245;

            let annualAmount = 0;
            switch (plan.frequency) {
                case "DAILY":
                    annualAmount = amount * tradingDaysPerYear;
                    break;
                case "MONTHLY":
                    annualAmount = amount * 12;
                    break;
                case "BONUS_MONTH": {
                    const bonusCount = plan.bonus_months
                        ? plan.bonus_months.split(",").map(m => m.trim()).filter(Boolean).length
                        : 0;
                    annualAmount = amount * bonusCount;
                    break;
                }
            }

            if (plan.target_account_type === "NISA_TSUMITATE") annualPlan.tsumitate += annualAmount;
            if (plan.target_account_type === "NISA_GROWTH") annualPlan.growth += annualAmount;
        });

        const lifetimeRem = {
            growth: nisa.lifetime.growth?.remaining ?? Number.POSITIVE_INFINITY,
            total: nisa.lifetime.total?.remaining ?? Number.POSITIVE_INFINITY,
        };

        // 年間上限は「今年既投資を勘案しない」固定上限を採用
        const ANNUAL_CAP = {
            tsumitate: 1200000,
            growth: 2400000,
            total: 3600000,
        } as const;

        // 今年の既投資分を考慮しない「有効上限」
        const effectiveCaps = {
            tsumitate: Math.min(ANNUAL_CAP.tsumitate, lifetimeRem.total),
            growth: Math.min(ANNUAL_CAP.growth, lifetimeRem.growth, lifetimeRem.total),
            total: Math.min(ANNUAL_CAP.total, lifetimeRem.total),
        } as const;

        // 合計上限（total）を先に見て、つみたて→成長の順に配分
        let totalCapLeft = effectiveCaps.total;
        const tsumitateEligible = Math.min(
            annualPlan.tsumitate,
            effectiveCaps.tsumitate,
            totalCapLeft
        );
        totalCapLeft -= tsumitateEligible;

        const growthEligible = Math.min(
            annualPlan.growth,
            effectiveCaps.growth,
            totalCapLeft
        );

        const totalEligible = tsumitateEligible + growthEligible;

        return {
            tsumitate: { planned: annualPlan.tsumitate, eligible: tsumitateEligible },
            growth: { planned: annualPlan.growth, eligible: growthEligible },
            total: { planned: annualPlan.tsumitate + annualPlan.growth, eligible: totalEligible },
            caps: {
                annual: { ...nisa.annual },
                lifetime: { ...nisa.lifetime },
            },
            effectiveCaps,
        } as const;
    }, [state.plans, nisa]);

    return (
        <div className="plans-page">
            <header className="page-header">
                <div className="header-content">
                    <h1>投資計画管理</h1>
                    <p>定期的な投資計画を管理します</p>
                </div>
                <Link href="/portfolio" className="link-to-portfolio">
                    ← ポートフォリオに戻る
                </Link>
            </header>

            <div className="page-content">
                {/* Error Message */}
                {state.error && <div className="error-banner">{state.error}</div>}

                {/* Form Section */}
                {state.showForm && (
                    <div className="form-container">
                        <PlansForm
                            onSubmit={handleFormSubmit}
                            initialData={editingPlan || null}
                            isLoading={state.submitLoading}
                            onCancel={handleCancel}
                        />
                    </div>
                )}

                {/* Investment Summary */}
                {!state.showForm && state.plans.length > 0 && (
                    <div className="summary-container">
                        <h2>投資額合計</h2>
                        <div className="summary-grid">
                            <div className="summary-card">
                                <div className="summary-label">日間投資額</div>
                                <div className="summary-amount">
                                    {formatAmount(totals.daily)}
                                </div>
                                <div className="summary-note">※ 1日あたりの平均額</div>
                            </div>
                            <div className="summary-card">
                                <div className="summary-label">月間投資額</div>
                                <div className="summary-amount highlight">
                                    {formatAmount(totals.monthly)}
                                </div>
                                <div className="summary-note">※ 1ヶ月あたりの平均額</div>
                            </div>
                            <div className="summary-card">
                                <div className="summary-label">年間投資額</div>
                                <div className="summary-amount highlight-primary">
                                    {formatAmount(totals.annual)}
                                </div>
                                <div className="summary-note">※ 1年間の合計額</div>
                            </div>
                        </div>

                        {nisaAnnualEligible && (
                            <>
                                <h2 style={{ marginTop: 24 }}>NISA対象（年間）</h2>
                                <div className="summary-grid">
                                    <div className="summary-card">
                                        <div className="summary-label">NISA対象 合計</div>
                                        <div className="summary-amount highlight-primary">
                                            {`${formatAmount(nisaAnnualEligible.total.eligible)} / ${formatAmount(nisaAnnualEligible.effectiveCaps.total)}`}
                                        </div>
                                        <div className="summary-note">
                                            計画: {formatAmount(nisaAnnualEligible.total.planned)}
                                        </div>
                                    </div>
                                    <div className="summary-card">
                                        <div className="summary-label">つみたて投資枠 対象</div>
                                        <div className="summary-amount">
                                            {`${formatAmount(nisaAnnualEligible.tsumitate.eligible)} / ${formatAmount(nisaAnnualEligible.effectiveCaps.tsumitate)}`}
                                        </div>
                                        <div className="summary-note">
                                            計画: {formatAmount(nisaAnnualEligible.tsumitate.planned)}
                                        </div>
                                    </div>
                                    <div className="summary-card">
                                        <div className="summary-label">成長投資枠 対象</div>
                                        <div className="summary-amount">
                                            {`${formatAmount(nisaAnnualEligible.growth.eligible)} / ${formatAmount(nisaAnnualEligible.effectiveCaps.growth)}`}
                                        </div>
                                        <div className="summary-note">
                                            計画: {formatAmount(nisaAnnualEligible.growth.planned)}
                                        </div>
                                    </div>
                                </div>
                            </>
                        )}
                    </div>
                )}

                {/* List Section */}
                <div className="list-container">
                    <div className="list-header">
                        <h2>投資計画リスト</h2>
                        {!state.showForm && (
                            <button onClick={handleAddClick} className="btn-add">
                                + 新規追加
                            </button>
                        )}
                    </div>

                    {state.loading ? (
                        <div className="loading-message">読み込み中...</div>
                    ) : !state.plans || state.plans.length === 0 ? (
                        <div className="empty-state">
                            <p>投資計画がまだ登録されていません</p>
                            {!state.showForm && (
                                <button onClick={handleAddClick} className="btn-add-primary">
                                    投資計画を作成
                                </button>
                            )}
                        </div>
                    ) : (
                        <>
                            <div className="plans-grid">
                                {state.plans?.map((plan) => (
                                    <div key={plan.id} className="plan-card">
                                        <div className="plan-header">
                                            <div className="plan-info">
                                                <h3>{ACCOUNT_TYPE_LABELS[plan.target_account_type] || plan.target_account_type}</h3>
                                                {plan.target_asset_name && (
                                                    <p className="plan-name">{plan.target_asset_name}</p>
                                                )}
                                                {plan.target_asset_identifier && (
                                                    <p className="plan-code">コード：{plan.target_asset_identifier}</p>
                                                )}
                                                <p className="plan-frequency">
                                                    {FREQUENCY_LABELS[plan.frequency] || plan.frequency}
                                                </p>
                                            </div>
                                            <div className="plan-amount">
                                                {formatAmount(plan.amount_jpy)}
                                            </div>
                                        </div>

                                        <div className="plan-details">
                                            <div className="detail-row">
                                                <span className="label">資産クラス：</span>
                                                <span className="value">
                                                    {ASSET_CLASS_LABELS[plan.target_asset_class] ||
                                                        plan.target_asset_class}
                                                </span>
                                            </div>
                                            {(!plan.target_asset_name && !plan.target_asset_identifier) ? null : (
                                                <div className="detail-row">
                                                    <span className="label">名称/コード：</span>
                                                    <span className="value">
                                                        {plan.target_asset_name || '-'} / {plan.target_asset_identifier || '-'}
                                                    </span>
                                                </div>
                                            )}
                                            <div className="detail-row">
                                                <span className="label">投資先：</span>
                                                <span className="value">
                                                    {ASSET_REGION_LABELS[plan.target_asset_region] ||
                                                        plan.target_asset_region}
                                                </span>
                                            </div>
                                            <div className="detail-row">
                                                <span className="label">開始日：</span>
                                                <span className="value">
                                                    {formatDate(plan.start_date)}
                                                </span>
                                            </div>
                                            <div className="detail-row">
                                                <span className="label">終了日：</span>
                                                <span className="value">
                                                    {formatDate(plan.end_date)}
                                                </span>
                                            </div>
                                            {plan.frequency === "BONUS_MONTH" && plan.bonus_months && (
                                                <div className="detail-row">
                                                    <span className="label">ボーナス月：</span>
                                                    <span className="value">
                                                        {plan.bonus_months}
                                                    </span>
                                                </div>
                                            )}
                                        </div>

                                        <div className="plan-actions">
                                            <button
                                                onClick={() => handleEditClick(plan.id || 0)}
                                                className="btn-action btn-edit"
                                                disabled={state.submitLoading}
                                            >
                                                編集
                                            </button>
                                            <button
                                                onClick={() =>
                                                    handleDeleteClick(plan.id || 0)
                                                }
                                                className="btn-action btn-delete"
                                                disabled={state.submitLoading}
                                            >
                                                削除
                                            </button>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            {/* Pagination */}
                            {state.totalPages > 1 && (
                                <div className="pagination">
                                    <button
                                        onClick={() =>
                                            loadPlans(state.currentPage - 1)
                                        }
                                        disabled={state.currentPage === 1}
                                        className="btn-page"
                                    >
                                        前へ
                                    </button>
                                    <span className="page-indicator">
                                        {state.currentPage} / {state.totalPages}
                                    </span>
                                    <button
                                        onClick={() =>
                                            loadPlans(state.currentPage + 1)
                                        }
                                        disabled={state.currentPage === state.totalPages}
                                        className="btn-page"
                                    >
                                        次へ
                                    </button>
                                </div>
                            )}
                        </>
                    )}
                </div>
            </div>

            <style>{`
                .plans-page {
                    min-height: 100vh;
                    background-color: #fafafa;
                }

                .page-header {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white;
                    padding: 40px 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    gap: 20px;
                }

                .header-content h1 {
                    margin: 0 0 8px 0;
                    font-size: 32px;
                    font-weight: 700;
                }

                .header-content p {
                    margin: 0;
                    opacity: 0.9;
                    font-size: 16px;
                }

                .link-to-portfolio {
                    color: white;
                    text-decoration: none;
                    padding: 8px 16px;
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 4px;
                    transition: background 0.2s;
                    white-space: nowrap;
                }

                .link-to-portfolio:hover {
                    background: rgba(255, 255, 255, 0.3);
                }

                .page-content {
                    max-width: 1200px;
                    margin: 0 auto;
                    padding: 30px 20px;
                }

                .error-banner {
                    background-color: #ffebee;
                    color: #c62828;
                    padding: 16px;
                    border-radius: 8px;
                    margin-bottom: 20px;
                    border-left: 4px solid #c62828;
                }

                .form-container {
                    background: white;
                    border-radius: 8px;
                    padding: 30px;
                    margin-bottom: 30px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }

                .summary-container {
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    border-radius: 8px;
                    padding: 30px;
                    margin-bottom: 30px;
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
                    color: white;
                }

                .summary-container h2 {
                    margin: 0 0 20px 0;
                    font-size: 20px;
                    font-weight: 600;
                    opacity: 0.95;
                }

                .summary-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                    gap: 20px;
                }

                .summary-card {
                    background: rgba(255, 255, 255, 0.15);
                    backdrop-filter: blur(10px);
                    border-radius: 8px;
                    padding: 24px;
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    transition: transform 0.2s, background 0.2s;
                }

                .summary-card:hover {
                    transform: translateY(-4px);
                    background: rgba(255, 255, 255, 0.2);
                }

                .summary-label {
                    font-size: 14px;
                    opacity: 0.9;
                    margin-bottom: 8px;
                    font-weight: 500;
                }

                .summary-amount {
                    font-size: 28px;
                    font-weight: 700;
                    margin-bottom: 8px;
                    letter-spacing: -0.5px;
                }

                .summary-amount.highlight {
                    font-size: 32px;
                    text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
                }

                .summary-amount.highlight-primary {
                    font-size: 36px;
                    text-shadow: 0 2px 12px rgba(0, 0, 0, 0.3);
                }

                .summary-note {
                    font-size: 12px;
                    opacity: 0.8;
                    font-style: italic;
                }

                .list-container {
                    background: white;
                    border-radius: 8px;
                    padding: 30px;
                    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
                }

                .list-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 24px;
                    padding-bottom: 16px;
                    border-bottom: 2px solid #f0f0f0;
                }

                .list-header h2 {
                    margin: 0;
                    font-size: 20px;
                    font-weight: 600;
                    color: #333;
                }

                .btn-add {
                    background-color: #2196f3;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: background-color 0.2s;
                }

                .btn-add:hover {
                    background-color: #1976d2;
                }

                .loading-message {
                    text-align: center;
                    padding: 40px;
                    color: #999;
                    font-size: 16px;
                }

                .empty-state {
                    text-align: center;
                    padding: 60px 20px;
                }

                .empty-state p {
                    margin: 0 0 20px 0;
                    color: #999;
                    font-size: 16px;
                }

                .btn-add-primary {
                    background-color: #2196f3;
                    color: white;
                    border: none;
                    padding: 12px 24px;
                    border-radius: 4px;
                    font-size: 14px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: background-color 0.2s;
                }

                .btn-add-primary:hover {
                    background-color: #1976d2;
                }

                .plans-grid {
                    display: grid;
                    grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                    gap: 20px;
                    margin-bottom: 30px;
                }

                .plan-card {
                    border: 1px solid #e0e0e0;
                    border-radius: 8px;
                    padding: 20px;
                    background: white;
                    transition: box-shadow 0.2s, transform 0.2s;
                }

                .plan-card:hover {
                    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
                    transform: translateY(-2px);
                }

                .plan-header {
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                    margin-bottom: 16px;
                    padding-bottom: 16px;
                    border-bottom: 1px solid #f0f0f0;
                }

                .plan-info h3 {
                    margin: 0;
                    font-size: 16px;
                    font-weight: 600;
                    color: #333;
                }

                .plan-frequency {
                    margin: 4px 0 0 0;
                    font-size: 12px;
                    color: #666;
                }

                .plan-amount {
                    font-size: 18px;
                    font-weight: 600;
                    color: #2196f3;
                    text-align: right;
                }

                .plan-details {
                    margin-bottom: 16px;
                }

                .detail-row {
                    display: flex;
                    justify-content: space-between;
                    padding: 8px 0;
                    font-size: 14px;
                    border-bottom: 1px solid #f9f9f9;
                }

                .detail-row:last-child {
                    border-bottom: none;
                }

                .detail-row .label {
                    color: #666;
                    font-weight: 500;
                }

                .detail-row .value {
                    color: #333;
                    text-align: right;
                }

                .plan-actions {
                    display: flex;
                    gap: 8px;
                    padding-top: 16px;
                    border-top: 1px solid #f0f0f0;
                }

                .btn-action {
                    flex: 1;
                    padding: 8px;
                    border: none;
                    border-radius: 4px;
                    font-size: 12px;
                    font-weight: 500;
                    cursor: pointer;
                    transition: background-color 0.2s;
                }

                .btn-edit {
                    background-color: #4caf50;
                    color: white;
                }

                .btn-edit:hover:not(:disabled) {
                    background-color: #45a049;
                }

                .btn-delete {
                    background-color: #f44336;
                    color: white;
                }

                .btn-delete:hover:not(:disabled) {
                    background-color: #da190b;
                }

                .btn-action:disabled {
                    opacity: 0.6;
                    cursor: not-allowed;
                }

                .pagination {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    gap: 16px;
                    padding-top: 20px;
                    border-top: 1px solid #f0f0f0;
                }

                .btn-page {
                    padding: 8px 16px;
                    border: 1px solid #d0d0d0;
                    background: white;
                    border-radius: 4px;
                    cursor: pointer;
                    font-size: 14px;
                    font-weight: 500;
                    transition: background-color 0.2s;
                }

                .btn-page:hover:not(:disabled) {
                    background-color: #f5f5f5;
                }

                .btn-page:disabled {
                    opacity: 0.5;
                    cursor: not-allowed;
                }

                .page-indicator {
                    font-size: 14px;
                    color: #666;
                }

                @media (max-width: 768px) {
                    .page-header {
                        flex-direction: column;
                    }

                    .summary-grid {
                        grid-template-columns: 1fr;
                    }

                    .summary-amount {
                        font-size: 24px;
                    }

                    .summary-amount.highlight {
                        font-size: 28px;
                    }

                    .summary-amount.highlight-primary {
                        font-size: 32px;
                    }

                    .plans-grid {
                        grid-template-columns: 1fr;
                    }
                }
            `}</style>
        </div>
    );
}

export default withAuth(PlansPage);
