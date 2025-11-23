/**
 * NISAUsageChart Component
 * Displays NISA frame usage over time with stacked bar chart
 */

import { YearBreakdown } from "@/services/api";
import styles from "@/styles/charts.module.css";
import {
    Bar,
    BarChart,
    CartesianGrid,
    ComposedChart,
    Legend,
    Line,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

interface NISAUsageChartProps {
    yearBreakdown: YearBreakdown[];
}

export default function NISAUsageChart({ yearBreakdown }: NISAUsageChartProps) {
    // Prepare data for NISA usage chart
    const nisaData = yearBreakdown.map((year) => ({
        year: String(year.year),
        yearNum: year.year,
        tsumitate: Math.round(year.nisa_usage.lifetime_tsumitate.used),
        growth: Math.round(year.nisa_usage.lifetime_growth.used),
        totalLimit: 18000000,
        annualTsumitate: Math.round(year.nisa_usage.tsumitate.used),
        annualGrowth: Math.round(year.nisa_usage.growth.used),
        annualLimit: 3600000,
    }));

    // Custom tooltip for better display
    const CustomTooltip = ({ active, payload }: any) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div
                    style={{
                        backgroundColor: "white",
                        padding: "10px",
                        border: "1px solid #ccc",
                        borderRadius: "4px",
                    }}
                >
                    <p style={{ fontWeight: "bold", marginBottom: "8px" }}>
                        {data.year}
                    </p>
                    <p style={{ color: "#06b6d4", margin: "4px 0" }}>
                        つみたて投資枠: ¥{data.tsumitate.toLocaleString("ja-JP")}
                    </p>
                    <p style={{ color: "#f59e0b", margin: "4px 0" }}>
                        成長投資枠: ¥{data.growth.toLocaleString("ja-JP")}
                    </p>
                    <p style={{ fontWeight: "bold", margin: "4px 0" }}>
                        合計: ¥{(data.tsumitate + data.growth).toLocaleString("ja-JP")}
                    </p>
                    <p style={{ color: "#888", fontSize: "12px", marginTop: "8px" }}>
                        残り枠: ¥
                        {(data.totalLimit - data.tsumitate - data.growth).toLocaleString(
                            "ja-JP"
                        )}
                    </p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className={styles.chartContainer}>
            <div className={styles.chartWrapper}>
                <h3>NISA生涯枠の使用状況（累計）</h3>
                <ResponsiveContainer width="100%" height={400}>
                    <ComposedChart data={nisaData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" label={{ value: "年度", position: "insideBottom", offset: -5 }} />
                        <YAxis
                            label={{ value: "金額", angle: -90, position: "insideLeft" }}
                            tickFormatter={(value) =>
                                `￥${(value / 10000).toFixed(0)}万`
                            }
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend />
                        <Bar
                            dataKey="tsumitate"
                            stackId="a"
                            fill="#06b6d4"
                            name="つみたて投資枠（累計）"
                        />
                        <Bar
                            dataKey="growth"
                            stackId="a"
                            fill="#f59e0b"
                            name="成長投資枠（累計）"
                        />
                        <Line
                            type="monotone"
                            dataKey="totalLimit"
                            stroke="#ef4444"
                            strokeWidth={2}
                            strokeDasharray="5 5"
                            dot={false}
                            name="生涯上限（1,800万円）"
                        />
                    </ComposedChart>
                </ResponsiveContainer>
                <div style={{ marginTop: "16px", fontSize: "14px", color: "#666" }}>
                    <p>
                        ※ NISA制度の生涯投資枠は1,800万円（うち成長投資枠は1,200万円まで）
                    </p>
                </div>
            </div>

            <div className={styles.chartWrapper}>
                <h3>年間NISA枠の使用状況</h3>
                <ResponsiveContainer width="100%" height={400}>
                    <BarChart data={nisaData}>
                        <CartesianGrid strokeDasharray="3 3" />
                        <XAxis dataKey="year" label={{ value: "年度", position: "insideBottom", offset: -5 }} />
                        <YAxis
                            label={{ value: "金額", angle: -90, position: "insideLeft" }}
                            tickFormatter={(value) =>
                                `￥${(value / 10000).toFixed(0)}万`
                            }
                        />
                        <Tooltip
                            formatter={(value) =>
                                `¥${typeof value === "number" ? value.toLocaleString("ja-JP") : value}`
                            }
                        />
                        <Legend />
                        <Bar
                            dataKey="annualTsumitate"
                            stackId="b"
                            fill="#06b6d4"
                            name="つみたて投資枠（年間）"
                        />
                        <Bar
                            dataKey="annualGrowth"
                            stackId="b"
                            fill="#f59e0b"
                            name="成長投資枠（年間）"
                        />
                    </BarChart>
                </ResponsiveContainer>
                <div style={{ marginTop: "16px", fontSize: "14px", color: "#666" }}>
                    <p>
                        ※ 年間投資枠: つみたて120万円 + 成長240万円 = 合計360万円
                    </p>
                </div>
            </div>
        </div>
    );
}
