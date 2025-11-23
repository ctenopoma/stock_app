/**
 * Projections page - Project future portfolio values
 * Displays projection form and results with year-by-year breakdown
 */

import NISAUsageChart from "@/components/NISAUsageChart";
import NISAUsageTable from "@/components/NISAUsageTable";
import PageHead from "@/components/PageHead";
import ProjectionChart from "@/components/ProjectionChart";
import ProjectionForm from "@/components/ProjectionForm";
import { withAuth } from "@/hoc/withAuth";
import { apiClient, Projection, YearBreakdown } from "@/services/api";
import styles from "@/styles/pages.module.css";
import Link from "next/link";
import { useState } from "react";

function ProjectionsPage() {
    const [projection, setProjection] = useState<Projection | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const handleProjectionSubmit = async (data: {
        projection_years: number;
        annual_return_rate: number;
    }) => {
        setLoading(true);
        setError(null);
        try {
            const result = await apiClient.createProjection(data);
            setProjection(result);
        } catch (err) {
            const error = err as Error;
            setError(error.message || "投影計算に失敗しました");
        } finally {
            setLoading(false);
        }
    };

    const handleDownload = () => {
        if (!projection) return;

        const raw = JSON.parse(projection.year_by_year_breakdown || "[]");
        const baseYear = projection.created_at
            ? new Date(projection.created_at).getFullYear()
            : new Date().getFullYear();
        const display = raw.map((row: { year: number; starting_balance: number; contributions: number; growth_rate: number; ending_balance: number }) => ({
            ...row,
            year: baseYear + (row.year - 1),
            starting_balance:
                typeof row.starting_balance === "number"
                    ? row.starting_balance
                    : Number((row as any).starting_balance) || 0,
            contributions:
                typeof row.contributions === "number"
                    ? row.contributions
                    : Number((row as any).contributions) || 0,
            ending_balance:
                typeof row.ending_balance === "number"
                    ? row.ending_balance
                    : Number((row as any).ending_balance) || 0,
            growth_rate:
                typeof row.growth_rate === "number"
                    ? row.growth_rate
                    : Number((row as any).growth_rate) || 0,
        }));

        const csvContent = [
            ["年", "開始残高", "新規積立", "成長率", "終了残高"],
            ...display.map(
                (row: { year: number; starting_balance: number; contributions: number; growth_rate: number; ending_balance: number }) => [
                    row.year,
                    Math.round(row.starting_balance).toLocaleString("ja-JP"),
                    Math.round(row.contributions).toLocaleString("ja-JP"),
                    `${(row.growth_rate * 100).toFixed(2)}%`,
                    Math.round(row.ending_balance).toLocaleString("ja-JP"),
                ]
            ),
        ]
            .map((row) => row.join(","))
            .join("\n"); const element = document.createElement("a");
        element.setAttribute(
            "href",
            "data:text/csv;charset=utf-8," + encodeURIComponent(csvContent)
        );
        element.setAttribute("download", "projection.csv");
        element.style.display = "none";
        document.body.appendChild(element);
        element.click();
        document.body.removeChild(element);
    };

    return (
        <>
            <PageHead title="投資配分の予測" description="将来のポートフォリオ価値を計算します" />

            <main className={styles.container}>
                <div className={styles.header}>
                    <h1>投資配分の予測</h1>
                    <nav className={styles.breadcrumb}>
                        <Link href="/">ホーム</Link>
                        <span>/</span>
                        <span>予測</span>
                    </nav>
                </div>

                <div className={styles.content}>
                    <section className={styles.formSection}>
                        <h2>予測パラメータ</h2>
                        <ProjectionForm onSubmit={handleProjectionSubmit} loading={loading} />
                    </section>

                    {error && (
                        <div className={styles.error}>
                            <strong>エラー:</strong> {error}
                        </div>
                    )}

                    {projection && (
                        <>
                            <section className={styles.resultSection}>
                                <h2>投影結果</h2>
                                <div className={styles.summaryGrid}>
                                    <div className={styles.summaryCard}>
                                        <h3>開始残高</h3>
                                        <p className={styles.amount}>
                                            ¥
                                            {Math.round(projection.starting_balance_jpy).toLocaleString(
                                                "ja-JP"
                                            )}
                                        </p>
                                    </div>
                                    <div className={styles.summaryCard}>
                                        <h3>総積立額</h3>
                                        <p className={styles.amount}>
                                            ¥
                                            {Math.round(
                                                projection.total_accumulated_contributions_jpy
                                            ).toLocaleString("ja-JP")}
                                        </p>
                                    </div>
                                    <div className={styles.summaryCard}>
                                        <h3>利益</h3>
                                        <p className={styles.amount}>
                                            ¥
                                            {Math.round(projection.total_interest_gains_jpy).toLocaleString(
                                                "ja-JP"
                                            )}
                                        </p>
                                    </div>
                                    <div className={styles.summaryCard}>
                                        <h3>予測最終価値</h3>
                                        <p className={styles.amount + " " + styles.highlight}>
                                            ¥
                                            {Math.round(projection.projected_total_value_jpy).toLocaleString(
                                                "ja-JP"
                                            )}
                                        </p>
                                    </div>
                                </div>
                            </section>

                            <section className={styles.chartSection}>
                                <h2>成長予測チャート</h2>
                                <ProjectionChart projection={projection} />
                            </section>

                            {(() => {
                                const raw: YearBreakdown[] = JSON.parse(
                                    projection.year_by_year_breakdown || "[]"
                                );
                                const baseYear = projection.created_at
                                    ? new Date(projection.created_at).getFullYear()
                                    : new Date().getFullYear();
                                const yearBreakdown: YearBreakdown[] = raw.map((y) => ({
                                    ...y,
                                    year: baseYear + (y.year - 1),
                                    starting_balance:
                                        typeof (y as any).starting_balance === "number"
                                            ? (y as any).starting_balance
                                            : Number((y as any).starting_balance) || 0,
                                    contributions:
                                        typeof (y as any).contributions === "number"
                                            ? (y as any).contributions
                                            : Number((y as any).contributions) || 0,
                                    ending_balance:
                                        typeof (y as any).ending_balance === "number"
                                            ? (y as any).ending_balance
                                            : Number((y as any).ending_balance) || 0,
                                    growth_rate:
                                        typeof (y as any).growth_rate === "number"
                                            ? (y as any).growth_rate
                                            : Number((y as any).growth_rate) || 0,
                                }));
                                const hasNisaData = yearBreakdown.some(
                                    (year) =>
                                        year.nisa_usage &&
                                        (year.nisa_usage.total.used > 0 ||
                                            year.nisa_usage.lifetime_total.used > 0)
                                );

                                return hasNisaData ? (
                                    <>
                                        <section className={styles.chartSection}>
                                            <h2>NISA枠使用予測</h2>
                                            <NISAUsageChart yearBreakdown={yearBreakdown} />
                                        </section>

                                        <NISAUsageTable yearBreakdown={yearBreakdown} />
                                    </>
                                ) : null;
                            })()}

                            <section className={styles.tableSection}>
                                <div className={styles.tableHeader}>
                                    <h2>年別内訳</h2>
                                    <button
                                        onClick={handleDownload}
                                        className={styles.downloadButton}
                                        aria-label="年別内訳データをCSVファイルとしてダウンロード"
                                    >
                                        CSV ダウンロード
                                    </button>
                                </div>
                                <table className={styles.dataTable}>
                                    <thead>
                                        <tr>
                                            <th>年</th>
                                            <th>開始残高</th>
                                            <th>新規積立</th>
                                            <th>成長率</th>
                                            <th>終了残高</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {(() => {
                                            const raw = JSON.parse(projection.year_by_year_breakdown || "[]");
                                            const baseYear = projection.created_at
                                                ? new Date(projection.created_at).getFullYear()
                                                : new Date().getFullYear();
                                            const display = raw.map((row: { year: number; starting_balance: number; contributions: number; growth_rate: number; ending_balance: number }) => ({
                                                ...row,
                                                year: baseYear + (row.year - 1),
                                                starting_balance:
                                                    typeof row.starting_balance === "number"
                                                        ? row.starting_balance
                                                        : Number((row as any).starting_balance) || 0,
                                                contributions:
                                                    typeof row.contributions === "number"
                                                        ? row.contributions
                                                        : Number((row as any).contributions) || 0,
                                                ending_balance:
                                                    typeof row.ending_balance === "number"
                                                        ? row.ending_balance
                                                        : Number((row as any).ending_balance) || 0,
                                                growth_rate:
                                                    typeof row.growth_rate === "number"
                                                        ? row.growth_rate
                                                        : Number((row as any).growth_rate) || 0,
                                            }));
                                            return display.map(
                                                (row: { year: number; starting_balance: number; contributions: number; growth_rate: number; ending_balance: number }) => (
                                                    <tr key={row.year}>
                                                        <td>{row.year}</td>
                                                        <td>
                                                            ¥
                                                            {Math.round(row.starting_balance).toLocaleString(
                                                                "ja-JP"
                                                            )}
                                                        </td>
                                                        <td>
                                                            ¥
                                                            {Math.round(row.contributions).toLocaleString(
                                                                "ja-JP"
                                                            )}
                                                        </td>
                                                        <td>{(row.growth_rate * 100).toFixed(2)}%</td>
                                                        <td>
                                                            ¥
                                                            {Math.round(row.ending_balance).toLocaleString(
                                                                "ja-JP"
                                                            )}
                                                        </td>
                                                    </tr>
                                                )
                                            );
                                        })()}
                                    </tbody>
                                </table>
                            </section>
                        </>
                    )}
                </div>
            </main>
        </>
    );
}

export default withAuth(ProjectionsPage);
