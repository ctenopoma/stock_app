/**
 * NISAUsageTable Component
 * Displays detailed NISA usage information in table format
 */

import { YearBreakdown } from "@/services/api";
import styles from "@/styles/pages.module.css";

interface NISAUsageTableProps {
    yearBreakdown: YearBreakdown[];
}

export default function NISAUsageTable({ yearBreakdown }: NISAUsageTableProps) {
    const formatCurrency = (amount: number) => {
        return `¥${Math.round(amount).toLocaleString("ja-JP")}`;
    };

    const formatPercentage = (used: number, limit: number) => {
        const percentage = (used / limit) * 100;
        return `${percentage.toFixed(1)}%`;
    };

    return (
        <div className={styles.tableSection}>
            <h2>NISA枠使用状況（年別詳細）</h2>
            <div style={{ overflowX: "auto" }}>
                <table className={styles.dataTable}>
                    <thead>
                        <tr>
                            <th rowSpan={2}>年</th>
                            <th colSpan={3}>年間使用額</th>
                            <th colSpan={3}>生涯累計</th>
                        </tr>
                        <tr>
                            <th>つみたて投資枠</th>
                            <th>成長投資枠</th>
                            <th>合計</th>
                            <th>つみたて累計</th>
                            <th>成長累計</th>
                            <th>合計累計</th>
                        </tr>
                    </thead>
                    <tbody>
                        {yearBreakdown.map((year) => {
                            const nisa = year.nisa_usage;
                            return (
                                <tr key={year.year}>
                                    <td>
                                        <strong>{year.year}</strong>
                                    </td>
                                    {/* Annual usage */}
                                    <td>
                                        {formatCurrency(nisa.tsumitate.used)}
                                        <br />
                                        <small style={{ color: "#666" }}>
                                            残り: {formatCurrency(nisa.tsumitate.remaining)}
                                        </small>
                                    </td>
                                    <td>
                                        {formatCurrency(nisa.growth.used)}
                                        <br />
                                        <small style={{ color: "#666" }}>
                                            残り: {formatCurrency(nisa.growth.remaining)}
                                        </small>
                                    </td>
                                    <td>
                                        <strong>{formatCurrency(nisa.total.used)}</strong>
                                        <br />
                                        <small style={{ color: "#666" }}>
                                            {formatPercentage(nisa.total.used, nisa.total.limit)}
                                        </small>
                                    </td>
                                    {/* Lifetime usage */}
                                    <td style={{ backgroundColor: "#f0f9ff" }}>
                                        {formatCurrency(nisa.lifetime_tsumitate.used)}
                                    </td>
                                    <td style={{ backgroundColor: "#fef3c7" }}>
                                        {formatCurrency(nisa.lifetime_growth.used)}
                                        <br />
                                        <small style={{ color: "#666" }}>
                                            {formatPercentage(
                                                nisa.lifetime_growth.used,
                                                nisa.lifetime_growth.limit
                                            )}
                                        </small>
                                    </td>
                                    <td style={{ backgroundColor: "#f0fdf4", fontWeight: "bold" }}>
                                        {formatCurrency(nisa.lifetime_total.used)}
                                        <br />
                                        <small style={{ color: "#666" }}>
                                            {formatPercentage(
                                                nisa.lifetime_total.used,
                                                nisa.lifetime_total.limit
                                            )}{" "}
                                            / 1,800万円
                                        </small>
                                    </td>
                                </tr>
                            );
                        })}
                    </tbody>
                </table>
            </div>
            <div style={{ marginTop: "16px", fontSize: "14px", color: "#666" }}>
                <h4>NISA制度の上限（2024年以降）</h4>
                <ul style={{ marginLeft: "20px", lineHeight: "1.6" }}>
                    <li>
                        <strong>年間上限:</strong> つみたて120万円 + 成長240万円 = 合計360万円
                    </li>
                    <li>
                        <strong>生涯上限:</strong> 合計1,800万円（うち成長投資枠は1,200万円まで）
                    </li>
                </ul>
            </div>
        </div>
    );
}
