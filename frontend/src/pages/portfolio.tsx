/**
 * Portfolio Page
 * Displays current portfolio visualization with pie chart and composition breakdown
 * Allows users to view their asset allocation by region, account type, and asset class
 */

"use client";

import { PortfolioChart } from "@/components/PortfolioChart";
import { withAuth } from "@/hoc/withAuth";
import { api, InvestmentHolding, PortfolioSummary as PortfolioSummaryType } from "@/services/api";
import Link from "next/link";
import React, { useEffect, useState } from "react";

type GroupBy = "region" | "account_type" | "asset_class";

function PortfolioPage(): React.ReactElement {
    const [summary, setSummary] = useState<PortfolioSummaryType | null>(null);
    const [holdings, setHoldings] = useState<InvestmentHolding[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string>("");
    const [groupBy, setGroupBy] = useState<GroupBy>("region");
    const [filterBy, setFilterBy] = useState<"none" | GroupBy>("none");
    const [filterValue, setFilterValue] = useState<string>("ALL");

    const filteredHoldings: InvestmentHolding[] = React.useMemo(() => {
        if (filterBy === "none" || filterValue === "ALL") return holdings;
        return holdings.filter((h) => {
            if (filterBy === "region") return h.asset_region === filterValue;
            if (filterBy === "account_type") return h.account_type === filterValue;
            if (filterBy === "asset_class") return h.asset_class === filterValue;
            return true;
        });
    }, [holdings, filterBy, filterValue]);

    const filterOptions = React.useMemo(() => {
        if (filterBy === "region")
            return Array.from(new Set(holdings.map((h) => h.asset_region)));
        if (filterBy === "account_type")
            return Array.from(new Set(holdings.map((h) => h.account_type)));
        if (filterBy === "asset_class")
            return Array.from(new Set(holdings.map((h) => h.asset_class)));
        return [] as string[];
    }, [holdings, filterBy]);

    useEffect(() => {
        loadPortfolioData();
    }, []);

    const loadPortfolioData = async (): Promise<void> => {
        try {
            setLoading(true);
            setError("");
            const [summary, holdingsList] = await Promise.all([
                api.portfolio.getSummary(),
                api.holdingsAPI.list(1, 1000), // Fetch all holdings (max 1000)
            ]);
            setSummary(summary);
            setHoldings(holdingsList.results || []);
        } catch (err) {
            const error = err as { data?: { detail?: string }; message?: string };
            const errorMsg =
                error?.data?.detail || error?.message || "ポートフォリオ情報の取得に失敗しました";
            setError(String(errorMsg));
            setHoldings([]); // Reset to empty array on error
            setSummary(null);
        } finally {
            setLoading(false);
        }
    };

    const computedSummary: PortfolioSummaryType = React.useMemo(() => {
        if (filterBy === "none" || filterValue === "ALL") return summary as PortfolioSummaryType;

        const total = filteredHoldings.reduce((sum, h) => sum + (Number(h.current_amount_jpy) || 0), 0);
        const groupSum = (key: "asset_region" | "account_type" | "asset_class") => {
            const map: Record<string, number> = {};
            filteredHoldings.forEach((h) => {
                const k = (h as any)[key] as string;
                const val = Number(h.current_amount_jpy) || 0;
                map[k] = (map[k] || 0) + val;
            });
            const out: Record<string, { amount: number; percentage: number }> = {};
            Object.entries(map).forEach(([k, v]) => {
                out[k] = {
                    amount: v,
                    percentage: total > 0 ? (v / total) * 100 : 0,
                };
            });
            return out;
        };

        return {
            total_value_jpy: total,
            composition_by_region: groupSum("asset_region"),
            composition_by_account_type: groupSum("account_type"),
            composition_by_asset_class: groupSum("asset_class"),
            holdings_count: filteredHoldings.length,
        } as PortfolioSummaryType;
    }, [summary, filteredHoldings, filterBy, filterValue]);

    if (loading) {
        return (
            <div className="max-w-6xl mx-auto p-6">
                <div className="flex items-center justify-center h-96">
                    <div className="text-center">
                        <div className="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mb-4"></div>
                        <p className="text-gray-600">ポートフォリオを読み込み中...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (!summary) {
        return (
            <div className="max-w-6xl mx-auto p-6">
                <div className="flex flex-col items-center justify-center h-96">
                    <div className="text-center">
                        <h2 className="text-2xl font-bold text-gray-800 mb-4">
                            ポートフォリオが取得できません
                        </h2>
                        <p className="text-gray-600 mb-6">
                            {error || "ポートフォリオ情報を読み込めませんでした"}
                        </p>
                        <button
                            onClick={loadPortfolioData}
                            className="px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 transition-colors"
                        >
                            再度読み込む
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="max-w-6xl mx-auto p-6">
            {/* Header */}
            <div className="mb-8">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">
                    ポートフォリオ管理
                </h1>
                <p className="text-gray-600">
                    現在の資産配分と投資内訳を確認できます
                </p>
            </div>

            {/* Error Alert */}
            {error && (
                <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg">
                    <p className="text-red-800">{error}</p>
                </div>
            )}

            {/* Navigation Tabs */}
            <div className="mb-6 flex gap-2 border-b border-gray-200" role="tablist" aria-label="ポートフォリオ表示方法">
                <button
                    onClick={() => setGroupBy("region")}
                    role="tab"
                    aria-selected={groupBy === "region"}
                    aria-controls="portfolio-content"
                    className={`px-4 py-3 font-medium border-b-2 transition-colors ${groupBy === "region"
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-600 hover:text-gray-900"
                        }`}
                >
                    投資先
                </button>
                <button
                    onClick={() => setGroupBy("account_type")}
                    role="tab"
                    aria-selected={groupBy === "account_type"}
                    aria-controls="portfolio-content"
                    className={`px-4 py-3 font-medium border-b-2 transition-colors ${groupBy === "account_type"
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-600 hover:text-gray-900"
                        }`}
                >
                    口座別
                </button>
                <button
                    onClick={() => setGroupBy("asset_class")}
                    role="tab"
                    aria-selected={groupBy === "asset_class"}
                    aria-controls="portfolio-content"
                    className={`px-4 py-3 font-medium border-b-2 transition-colors ${groupBy === "asset_class"
                        ? "border-blue-500 text-blue-600"
                        : "border-transparent text-gray-600 hover:text-gray-900"
                        }`}
                >
                    資産別
                </button>
            </div>

            {/* Main Content */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8" id="portfolio-content" role="tabpanel">
                {/* Chart Section */}
                <div className="lg:col-span-2">
                    <PortfolioChart summary={computedSummary} groupBy={groupBy} holdings={filteredHoldings} />
                </div>

                {/* Stats Section */}
                <div className="space-y-4">
                    {/* Total Value Card */}
                    <div className="bg-gradient-to-br from-blue-50 to-blue-100 rounded-lg p-6 border border-blue-200">
                        <p className="text-sm text-blue-700 font-medium mb-1">総資産額</p>
                        <p className="text-3xl font-bold text-blue-900">
                            {new Intl.NumberFormat("ja-JP", {
                                style: "currency",
                                currency: "JPY",
                                maximumFractionDigits: 0,
                            }).format(computedSummary.total_value_jpy)}
                        </p>
                    </div>

                    {/* Holdings Count Card */}
                    <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-lg p-6 border border-green-200">
                        <p className="text-sm text-green-700 font-medium mb-1">保有数</p>
                        <p className="text-3xl font-bold text-green-900">
                            {computedSummary.holdings_count}
                        </p>
                        <p className="text-xs text-green-700 mt-2">件の投資商品</p>
                    </div>

                    {/* Region Count */}
                    <div className="bg-gradient-to-br from-purple-50 to-purple-100 rounded-lg p-6 border border-purple-200">
                        <p className="text-sm text-purple-700 font-medium mb-1">投資先分類</p>
                        <p className="text-3xl font-bold text-purple-900">
                            {Object.keys(computedSummary.composition_by_region).length}
                        </p>
                        <p className="text-xs text-purple-700 mt-2">種類</p>
                    </div>

                    {/* Actions */}
                    <div className="border-t border-gray-200 pt-4 space-y-2">
                        <Link
                            href="/input"
                            className="block w-full px-4 py-2 bg-blue-500 text-white text-center rounded hover:bg-blue-600 transition-colors font-medium"
                            aria-label="新しい資産を追加"
                        >
                            資産を追加
                        </Link>
                        <Link
                            href="/plans"
                            className="block w-full px-4 py-2 bg-purple-500 text-white text-center rounded hover:bg-purple-600 transition-colors font-medium"
                            aria-label="投資計画を管理"
                        >
                            計画を管理
                        </Link>
                        <button
                            onClick={loadPortfolioData}
                            className="w-full px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 transition-colors font-medium"
                            aria-label="ポートフォリオデータを更新"
                        >
                            更新
                        </button>
                    </div>
                </div>
            </div>

            {/* Detailed Tables */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Region Breakdown */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        投資先別の内訳
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-gray-200">
                                    <th className="text-left py-2 px-2 text-gray-600">投資先</th>
                                    <th className="text-right py-2 px-2 text-gray-600">金額</th>
                                    <th className="text-right py-2 px-2 text-gray-600">構成比</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.entries(computedSummary.composition_by_region).map(
                                    ([region, item]) => (
                                        <tr key={region} className="border-b border-gray-100">
                                            <td className="py-3 px-2 text-gray-900">
                                                {formatRegionLabel(region)}
                                            </td>
                                            <td className="py-3 px-2 text-right text-gray-900 font-medium">
                                                {new Intl.NumberFormat("ja-JP", {
                                                    style: "currency",
                                                    currency: "JPY",
                                                    maximumFractionDigits: 0,
                                                }).format(item.amount)}
                                            </td>
                                            <td className="py-3 px-2 text-right text-gray-600">
                                                {item.percentage.toFixed(2)}%
                                            </td>
                                        </tr>
                                    )
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>

                {/* Account Type Breakdown */}
                <div className="bg-white rounded-lg border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">
                        口座タイプ別の内訳
                    </h3>
                    <div className="overflow-x-auto">
                        <table className="w-full text-sm">
                            <thead>
                                <tr className="border-b border-gray-200">
                                    <th className="text-left py-2 px-2 text-gray-600">口座</th>
                                    <th className="text-right py-2 px-2 text-gray-600">金額</th>
                                    <th className="text-right py-2 px-2 text-gray-600">構成比</th>
                                </tr>
                            </thead>
                            <tbody>
                                {Object.entries(computedSummary.composition_by_account_type).map(
                                    ([type, item]) => (
                                        <tr key={type} className="border-b border-gray-100">
                                            <td className="py-3 px-2 text-gray-900">
                                                {formatAccountTypeLabel(type)}
                                            </td>
                                            <td className="py-3 px-2 text-right text-gray-900 font-medium">
                                                {new Intl.NumberFormat("ja-JP", {
                                                    style: "currency",
                                                    currency: "JPY",
                                                    maximumFractionDigits: 0,
                                                }).format(item.amount)}
                                            </td>
                                            <td className="py-3 px-2 text-right text-gray-600">
                                                {item.percentage.toFixed(2)}%
                                            </td>
                                        </tr>
                                    )
                                )}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>

            {/* Holdings List with Filter */}
            <div className="mt-6 bg-white rounded-lg border border-gray-200 p-6">
                <div className="flex flex-col md:flex-row md:items-end md:justify-between gap-4 mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">保有資産一覧</h3>
                    <div className="flex flex-col sm:flex-row gap-3">
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">分類</label>
                            <select
                                className="border rounded px-3 py-2 text-sm"
                                value={filterBy}
                                onChange={(e) => {
                                    const v = e.target.value as "none" | GroupBy;
                                    setFilterBy(v);
                                    setFilterValue("ALL");
                                }}
                            >
                                <option value="none">すべて</option>
                                <option value="region">投資先</option>
                                <option value="account_type">口座</option>
                                <option value="asset_class">資産</option>
                            </select>
                        </div>
                        <div>
                            <label className="block text-sm text-gray-600 mb-1">値</label>
                            <select
                                className="border rounded px-3 py-2 text-sm"
                                value={filterValue}
                                onChange={(e) => setFilterValue(e.target.value)}
                                disabled={filterBy === "none"}
                            >
                                <option value="ALL">すべて</option>
                                {filterOptions.map((opt) => (
                                    <option key={opt} value={opt}>
                                        {filterBy === "region"
                                            ? formatRegionLabel(opt)
                                            : filterBy === "account_type"
                                                ? formatAccountTypeLabel(opt)
                                                : formatAssetClassLabel(opt)}
                                    </option>
                                ))}
                            </select>
                        </div>
                    </div>
                </div>

                <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                        <thead>
                            <tr className="border-b border-gray-200">
                                <th className="text-left py-2 px-2 text-gray-600">名称</th>
                                <th className="text-left py-2 px-2 text-gray-600">コード</th>
                                <th className="text-left py-2 px-2 text-gray-600">口座</th>
                                <th className="text-left py-2 px-2 text-gray-600">資産</th>
                                <th className="text-left py-2 px-2 text-gray-600">投資先</th>
                                <th className="text-right py-2 px-2 text-gray-600">金額</th>
                                <th className="text-right py-2 px-2 text-gray-600">購入日</th>
                            </tr>
                        </thead>
                        <tbody>
                            {filteredHoldings.map((h) => (
                                <tr key={`${h.account_type}-${h.asset_identifier}`} className="border-b border-gray-100">
                                    <td className="py-3 px-2 text-gray-900">{h.asset_name}</td>
                                    <td className="py-3 px-2 text-gray-700">{h.asset_identifier}</td>
                                    <td className="py-3 px-2 text-gray-700">{formatAccountTypeLabel(h.account_type)}</td>
                                    <td className="py-3 px-2 text-gray-700">{formatAssetClassLabel(h.asset_class)}</td>
                                    <td className="py-3 px-2 text-gray-700">{formatRegionLabel(h.asset_region)}</td>
                                    <td className="py-3 px-2 text-right text-gray-900 font-medium">
                                        {new Intl.NumberFormat("ja-JP", { style: "currency", currency: "JPY", maximumFractionDigits: 0 }).format(h.current_amount_jpy)}
                                    </td>
                                    <td className="py-3 px-2 text-right text-gray-600">
                                        {h.purchase_date ? new Date(h.purchase_date).toLocaleDateString("ja-JP") : "-"}
                                    </td>
                                </tr>
                            ))}
                            {filteredHoldings.length === 0 && (
                                <tr>
                                    <td colSpan={7} className="py-6 text-center text-gray-500">該当する保有資産はありません</td>
                                </tr>
                            )}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}

export default withAuth(PortfolioPage);

function formatRegionLabel(region: string): string {
    const labels: Record<string, string> = {
        DOMESTIC_STOCKS: "国内株式",
        INTERNATIONAL_STOCKS: "国際株式",
        DOMESTIC_BONDS: "国内債券",
        INTERNATIONAL_BONDS: "国際債券",
        DOMESTIC_REITS: "国内REIT",
        INTERNATIONAL_REITS: "国際REIT",
        CRYPTOCURRENCY: "暗号資産",
        OTHER: "その他",
    };
    return labels[region] || region;
}

function formatAccountTypeLabel(type: string): string {
    const labels: Record<string, string> = {
        NISA_TSUMITATE: "NISA (つみたて投資枠)",
        NISA_GROWTH: "NISA (成長投資枠)",
        GENERAL: "一般口座",
    };
    return labels[type] || type;
}

function formatAssetClassLabel(cls: string): string {
    const labels: Record<string, string> = {
        INDIVIDUAL_STOCK: "個別株",
        MUTUAL_FUND: "投資信託",
        CRYPTOCURRENCY: "暗号資産",
        REIT: "REIT",
        GOVERNMENT_BOND: "公債",
        OTHER: "その他",
    };
    return labels[cls] || cls;
}
