/**
 * ProjectionForm Component
 * Accepts projection_years and annual_return_rate inputs
 */

import styles from "@/styles/forms.module.css";
import { FormEvent, useState } from "react";

interface ProjectionFormProps {
    onSubmit: (data: {
        projection_years: number;
        annual_return_rate: number;
    }) => void;
    loading?: boolean;
}

export default function ProjectionForm({
    onSubmit,
    loading = false,
}: ProjectionFormProps) {
    const [projectionYears, setProjectionYears] = useState<number>(10);
    const [annualReturnRate, setAnnualReturnRate] = useState<number>(4);
    const [errors, setErrors] = useState<Record<string, string>>({});

    const handleSubmit = (e: FormEvent<HTMLFormElement>) => {
        e.preventDefault();
        setErrors({});

        // Validation
        const newErrors: Record<string, string> = {};

        if (!projectionYears || projectionYears < 1 || projectionYears > 50) {
            newErrors.projectionYears =
                "投影年数は1～50年の間で指定してください";
        }

        if (
            annualReturnRate === null ||
            annualReturnRate < -100 ||
            annualReturnRate > 100
        ) {
            newErrors.annualReturnRate =
                "年間利回りは-100～100の範囲で指定してください";
        }

        if (Object.keys(newErrors).length > 0) {
            setErrors(newErrors);
            return;
        }

        onSubmit({
            projection_years: projectionYears,
            annual_return_rate: annualReturnRate,
        });
    };

    return (
        <form onSubmit={handleSubmit} className={styles.form}>
            <div className={styles.formGroup}>
                <label htmlFor="projectionYears">投影年数 *</label>
                <input
                    id="projectionYears"
                    type="number"
                    min="1"
                    max="50"
                    value={projectionYears}
                    onChange={(e) => setProjectionYears(Number(e.target.value))}
                    disabled={loading}
                    className={errors.projectionYears ? styles.error : ""}
                />
                {errors.projectionYears && (
                    <span className={styles.errorText}>{errors.projectionYears}</span>
                )}
                <small>将来のポートフォリオを計算する期間（年数）</small>
            </div>

            <div className={styles.formGroup}>
                <label htmlFor="annualReturnRate">年間利回り (%) *</label>
                <input
                    id="annualReturnRate"
                    type="number"
                    step="0.1"
                    min="-100"
                    max="100"
                    value={annualReturnRate}
                    onChange={(e) => setAnnualReturnRate(Number(e.target.value))}
                    disabled={loading}
                    className={errors.annualReturnRate ? styles.error : ""}
                />
                {errors.annualReturnRate && (
                    <span className={styles.errorText}>{errors.annualReturnRate}</span>
                )}
                <small>
                    期待される年間平均利回り（例：4.0 = 4%）
                </small>
            </div>

            <button
                type="submit"
                disabled={loading}
                className={styles.submitButton}
            >
                {loading ? "計算中..." : "投影を計算"}
            </button>
        </form>
    );
}
