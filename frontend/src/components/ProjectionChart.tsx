/**
 * ProjectionChart Component
 * Displays year-by-year projection growth with Recharts
 */

import { Projection } from "@/services/api";
import styles from "@/styles/charts.module.css";
import {
    Bar,
    BarChart,
    CartesianGrid,
    Cell,
    Legend,
    Line,
    LineChart,
    Pie,
    PieChart,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

interface ProjectionChartProps {
    projection: Projection;
}

export default function ProjectionChart({
    projection,
}: ProjectionChartProps) {
    const yearlyData = JSON.parse(projection.year_by_year_breakdown || "[]");
    const compositionData = JSON.parse(
        projection.projected_composition_by_region || "{}"
    );
    const classCompositionData = projection.projected_composition_by_asset_class
        ? JSON.parse(projection.projected_composition_by_asset_class || "{}")
        : {};
    const baseYear = projection.created_at
        ? new Date(projection.created_at).getFullYear()
        : new Date().getFullYear();
    // Prepare data for line chart (growth over time)
    const lineData = yearlyData.map((item: { year: number; ending_balance: number }) => ({
        year: String(baseYear + (item.year - 1)),
        balance: Math.round(item.ending_balance),
    }));
    // Prepare data for bar chart with calendar year labels
    const barData = yearlyData.map((item: any) => ({
        yearLabel: String(baseYear + (item.year - 1)),
        contributions:
            typeof item.contributions === "number"
                ? item.contributions
                : Number(item.contributions) || 0,
        growth_amount:
            typeof item.growth_amount === "number"
                ? item.growth_amount
                : Number(item.growth_amount) || 0,
    }));

    // Prepare data for pie chart (composition)
    const pieData = Object.entries(compositionData as Record<string, { amount: number }>).map(([region, data]) => ({
        name: formatRegionName(region),
        value: Math.round(data.amount),
    }));
    const pieDataByClass = Object.entries(classCompositionData as Record<string, { amount: number }>).map(([cls, data]) => ({
        name: formatClassName(cls),
        value: Math.round((data as any).amount || 0),
    }));

    const colors = [
        "#8b5cf6",
        "#06b6d4",
        "#10b981",
        "#f59e0b",
        "#ef4444",
        "#ec4899",
    ];

    // Dynamic unit scaling (円/万円/億円) based on max value across charts
    const maxLine = lineData.reduce((m, d) => Math.max(m, d.balance || 0), 0);
    const maxStack = barData.reduce((m, d) => Math.max(m, (d.contributions || 0) + (d.growth_amount || 0)), 0);
    const maxValue = Math.max(maxLine, maxStack);
    let divisor = 1;
    let unitLabel = "円";
    if (maxValue >= 100000000) {
        divisor = 100000000; // 1億円
        unitLabel = "億円";
    } else if (maxValue >= 10000) {
        divisor = 10000; // 1万円
        unitLabel = "万円";
    }
    const axisLabel = `金額（${unitLabel}）`;
    const formatTick = (value: number) => (value / divisor).toLocaleString("ja-JP");
    const formatTooltip = (value: number) => `${(value / divisor).toLocaleString("ja-JP")}${unitLabel}`;

    return (
        <div className={styles.chartContainer}>
            <div className={styles.chartWrapper}>
                <h3>ポートフォリオ成長予測</h3>
                <ResponsiveContainer width="100%" height={400}>
                    <LineChart data={lineData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" label={{ value: "年度", position: "insideBottom", offset: -5 }} />
                        <YAxis
                            label={{ value: axisLabel, angle: -90, position: "insideLeft" }}
                            tickFormatter={(value: number) => formatTick(value)}
                        />
                        <Tooltip formatter={(value: any) => formatTooltip(Number(value) || 0)} />
                        <Legend />
                        <Line
                            type="monotone"
                            dataKey="balance"
                            stroke="#8b5cf6"
                            strokeWidth={2}
                            dot={{ fill: "#8b5cf6", r: 5 }}
                            activeDot={{ r: 7 }}
                            name="ポートフォリオ価値"
                        />
                    </LineChart>
                </ResponsiveContainer>
            </div>

            {yearlyData.length > 1 && (
                <div className={styles.chartWrapper}>
                    <h3>年別成長額</h3>
                    <ResponsiveContainer width="100%" height={400}>
                        <BarChart data={barData}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="yearLabel" label={{ value: "年度", position: "insideBottom", offset: -5 }} />
                            <YAxis
                                label={{ value: axisLabel, angle: -90, position: "insideLeft" }}
                                tickFormatter={(value: number) => formatTick(value)}
                            />
                            <Tooltip formatter={(value: any) => formatTooltip(Number(value) || 0)} />
                            <Legend />
                            <Bar
                                dataKey="contributions"
                                stackId="a"
                                fill="#06b6d4"
                                name="新規積立"
                            />
                            <Bar
                                dataKey="growth_amount"
                                stackId="a"
                                fill="#10b981"
                                name="成長"
                            />
                        </BarChart>
                    </ResponsiveContainer>
                </div>
            )}

            {pieData.length > 0 && (
                <div className={styles.chartWrapper}>
                    <h3>資産配分（最終予測）</h3>
                    <ResponsiveContainer width="100%" height={400}>
                        <PieChart>
                            <Pie
                                data={pieData}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, value, percent }) =>
                                    `${name}: ¥${value.toLocaleString("ja-JP")} (${(percent * 100).toFixed(1)}%)`
                                }
                                outerRadius={120}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {pieData.map((_, index) => (
                                    <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                formatter={(value) =>
                                    `¥${typeof value === "number" ? value.toLocaleString("ja-JP") : value}`
                                }
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            )}

            {pieDataByClass.length > 0 && (
                <div className={styles.chartWrapper}>
                    <h3>資産配分（資産クラス・最終予測）</h3>
                    <ResponsiveContainer width="100%" height={400}>
                        <PieChart>
                            <Pie
                                data={pieDataByClass}
                                cx="50%"
                                cy="50%"
                                labelLine={false}
                                label={({ name, value, percent }) =>
                                    `${name}: ¥${value.toLocaleString("ja-JP")} (${(percent * 100).toFixed(1)}%)`
                                }
                                outerRadius={120}
                                fill="#8884d8"
                                dataKey="value"
                            >
                                {pieDataByClass.map((_, index) => (
                                    <Cell key={`cell-class-${index}`} fill={colors[index % colors.length]} />
                                ))}
                            </Pie>
                            <Tooltip
                                formatter={(value) =>
                                    `¥${typeof value === "number" ? value.toLocaleString("ja-JP") : value}`
                                }
                            />
                        </PieChart>
                    </ResponsiveContainer>
                </div>
            )}
        </div>
    );
}

function formatRegionName(region: string): string {
    const names: Record<string, string> = {
        DOMESTIC_STOCKS: "国内株式",
        INTERNATIONAL_STOCKS: "国際株式",
        DOMESTIC_BONDS: "国内債券",
        INTERNATIONAL_BONDS: "国際債券",
        DOMESTIC_REITS: "国内不動産投信",
        INTERNATIONAL_REITS: "海外不動産投信",
        REAL_ESTATE: "不動産",
        CRYPTOCURRENCY: "暗号資産",
        CASH: "現金",
        OTHER: "その他",
    };
    return names[region] || region;
}

function formatClassName(cls: string): string {
    const names: Record<string, string> = {
        INDIVIDUAL_STOCK: "個別株",
        MUTUAL_FUND: "投資信託",
        CRYPTOCURRENCY: "暗号資産",
        REIT: "REIT",
        GOVERNMENT_BOND: "国債",
        OTHER: "その他",
    };
    return names[cls] || cls;
}
