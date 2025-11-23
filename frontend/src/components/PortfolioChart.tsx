/**
 * PortfolioChart Component
 * Displays portfolio composition as a pie chart with tooltips and legends
 * Groups holdings by investment destination (投資先)
 */

"use client";

import React, { useMemo } from "react";
import {
    Cell,
    Legend,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
} from "recharts";

interface CompositionItem {
    amount: number;
    percentage: number;
}

interface PortfolioSummary {
    total_value_jpy: number;
    composition_by_region: Record<string, CompositionItem>;
    composition_by_account_type: Record<string, CompositionItem>;
    composition_by_asset_class: Record<string, CompositionItem>;
    holdings_count: number;
}

interface InvestmentHolding {
    id?: number;
    asset_region?: string;
    account_type?: string;
    asset_class?: string;
    current_amount_jpy?: number;
    asset_name?: string;
}

interface PortfolioChartProps {
    summary: PortfolioSummary;
    holdings?: InvestmentHolding[];
    groupBy?: "region" | "account_type" | "asset_class";
}

const COLORS = [
    "#8b5cf6", // Purple
    "#ec4899", // Pink
    "#f59e0b", // Amber
    "#10b981", // Emerald
    "#3b82f6", // Blue
    "#06b6d4", // Cyan
    "#84cc16", // Lime
    "#f97316", // Orange
    "#6366f1", // Indigo
    "#14b8a6", // Teal
];

const REGION_LABELS: Record<string, string> = {
    DOMESTIC_STOCKS: "国内株式",
    INTERNATIONAL_STOCKS: "国際株式",
    DOMESTIC_BONDS: "国内債券",
    INTERNATIONAL_BONDS: "国際債券",
    DOMESTIC_REITS: "国内REIT",
    INTERNATIONAL_REITS: "国際REIT",
    CRYPTOCURRENCY: "暗号資産",
    OTHER: "その他",
};

const ACCOUNT_TYPE_LABELS: Record<string, string> = {
    NISA_TSUMITATE: "NISA (つみたて投資枠)",
    NISA_GROWTH: "NISA (成長投資枠)",
    GENERAL: "一般口座",
};

const ASSET_CLASS_LABELS: Record<string, string> = {
    INDIVIDUAL_STOCK: "個別株",
    MUTUAL_FUND: "投資信託",
    CRYPTOCURRENCY: "暗号資産",
    REIT: "REIT",
    GOVERNMENT_BOND: "公債",
    OTHER: "その他",
};

interface ChartDataPoint {
    name: string;
    value: number;
    percentage: number;
    amount: number;
    holdingsCount?: number;
}

const formatJPY = (amount: number): string => {
    return new Intl.NumberFormat("ja-JP", {
        style: "currency",
        currency: "JPY",
        maximumFractionDigits: 0,
    }).format(amount);
};

const CustomTooltip = ({ active, payload }: { active?: boolean; payload?: Array<{ name: string; value: number; payload: { name: string; value: number; amount?: number; percentage?: number; holdingsCount?: number } }> }): React.ReactElement | null => {
    if (!active || !payload || !payload.length) {
        return null;
    }

    const data = payload[0].payload;

    return (
        <div className="bg-white p-3 border border-gray-300 rounded shadow-lg">
            <p className="font-semibold text-gray-800">{data.name}</p>
            <p className="text-sm text-gray-600">
                {formatJPY(data.amount || data.value)}
            </p>
            {data.percentage !== undefined && (
                <p className="text-sm text-gray-600">
                    {data.percentage.toFixed(2)}%
                </p>
            )}
            {data.holdingsCount !== undefined && (
                <p className="text-sm text-gray-600 border-t border-gray-200 mt-2 pt-2">
                    保有数: {data.holdingsCount}件
                </p>
            )}
        </div>
    );
};

export function PortfolioChart({
    summary,
    holdings = [],
    groupBy = "region",
}: PortfolioChartProps) {
    const chartData = useMemo(() => {
        let sourceData: Record<string, CompositionItem> = {};
        let labels: Record<string, string> = {};
        let groupKey: keyof InvestmentHolding = "asset_region";

        switch (groupBy) {
            case "account_type":
                sourceData = summary.composition_by_account_type;
                labels = ACCOUNT_TYPE_LABELS;
                groupKey = "account_type";
                break;
            case "asset_class":
                sourceData = summary.composition_by_asset_class;
                labels = ASSET_CLASS_LABELS;
                groupKey = "asset_class";
                break;
            case "region":
            default:
                sourceData = summary.composition_by_region;
                labels = REGION_LABELS;
                groupKey = "asset_region";
        }

        // Calculate holdings count per group
        const holdingsCounts: Record<string, number> = {};
        holdings.forEach((holding) => {
            const key = String(holding[groupKey] || "OTHER");
            holdingsCounts[key] = (holdingsCounts[key] || 0) + 1;
        });

        return Object.entries(sourceData).map(([key, item]) => ({
            name: labels[key] || key,
            value: item.amount,
            percentage: item.percentage,
            amount: item.amount,
            holdingsCount: holdingsCounts[key] || 0,
        }));
    }, [summary, groupBy, holdings]);

    if (summary.total_value_jpy === 0) {
        return (
            <div className="flex items-center justify-center w-full h-96 bg-gray-50 rounded-lg border border-gray-200">
                <div className="text-center">
                    <p className="text-gray-500 text-lg mb-2">ポートフォリオデータなし</p>
                    <p className="text-gray-400 text-sm">保有資産を追加してください</p>
                </div>
            </div>
        );
    }

    return (
        <div className="w-full bg-white rounded-lg border border-gray-200 p-6">
            <div className="mb-6">
                <h3 className="text-xl font-semibold text-gray-800 mb-2">
                    ポートフォリオ構成
                </h3>
                <div className="flex items-baseline gap-2">
                    <span className="text-sm text-gray-600">総資産額:</span>
                    <span className="text-2xl font-bold text-gray-900">
                        {formatJPY(summary.total_value_jpy)}
                    </span>
                    <span className="text-sm text-gray-500 ml-4">
                        保有数: {summary.holdings_count}件
                    </span>
                </div>
            </div>

            <div className="w-full h-96">
                <ResponsiveContainer width="100%" height="100%">
                    <PieChart>
                        <Pie
                            data={chartData}
                            cx="50%"
                            cy="50%"
                            labelLine={false}
                            label={({ name, percentage }: { name: string; percentage: number }) =>
                                `${name} ${percentage.toFixed(1)}%`
                            }
                            outerRadius={120}
                            fill="#8884d8"
                            dataKey="value"
                        >
                            {chartData.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={COLORS[index % COLORS.length]}
                                />
                            ))}
                        </Pie>
                        <Tooltip content={<CustomTooltip />} />
                        <Legend
                            verticalAlign="bottom"
                            height={36}
                            formatter={(value, entry) => {
                                const data = entry.payload as unknown as ChartDataPoint;
                                return `${data.name}: ${formatJPY(data.amount)}`;
                            }}
                        />
                    </PieChart>
                </ResponsiveContainer>
            </div>

            <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-800 mb-3 text-sm">
                        投資先構成
                    </h4>
                    <div className="space-y-2 text-sm">
                        {Object.entries(summary.composition_by_region).map(([region, item]) => (
                            <div key={region} className="flex justify-between items-center">
                                <span className="text-gray-700">
                                    {REGION_LABELS[region] || region}
                                </span>
                                <div className="text-right">
                                    <div className="font-medium text-gray-900">
                                        {formatJPY(item.amount)}
                                    </div>
                                    <div className="text-gray-500">
                                        {item.percentage.toFixed(2)}%
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-semibold text-gray-800 mb-3 text-sm">
                        口座種別構成
                    </h4>
                    <div className="space-y-2 text-sm">
                        {Object.entries(summary.composition_by_account_type).map(([type, item]) => (
                            <div key={type} className="flex justify-between items-center">
                                <span className="text-gray-700">
                                    {ACCOUNT_TYPE_LABELS[type] || type}
                                </span>
                                <div className="text-right">
                                    <div className="font-medium text-gray-900">
                                        {formatJPY(item.amount)}
                                    </div>
                                    <div className="text-gray-500">
                                        {item.percentage.toFixed(2)}%
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
