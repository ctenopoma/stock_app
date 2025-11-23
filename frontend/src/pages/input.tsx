/**
 * Holdings Input Page
 * Page for managing investment holdings (create, list, edit, delete)
 */

"use client";

import { HoldingsForm } from "@/components/HoldingsForm";
import { withAuth } from "@/hoc/withAuth";
import { api, InvestmentHolding } from "@/services/api";
import { useEffect, useMemo, useState } from "react";

// 日本語ラベルのマッピング
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
    GOVERNMENT_BOND: "国債",
    OTHER: "その他",
};

const ASSET_REGION_LABELS: Record<string, string> = {
    DOMESTIC_STOCKS: "国内株式",
    INTERNATIONAL_STOCKS: "海外株式",
    DOMESTIC_BONDS: "国内債券",
    INTERNATIONAL_BONDS: "海外債券",
    DOMESTIC_REITS: "国内REIT",
    INTERNATIONAL_REITS: "海外REIT",
    CRYPTOCURRENCY: "暗号資産",
    OTHER: "その他",
};

function InputPage() {
    const [holdings, setHoldings] = useState<InvestmentHolding[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [showForm, setShowForm] = useState(false);
    const [editingId, setEditingId] = useState<number | null>(null);
    const [page, setPage] = useState(1);
    const [totalCount, setTotalCount] = useState(0);
    const pageSize = 10;

    // Filters
    const [filterAccountType, setFilterAccountType] = useState<string>("ALL");
    const [filterAssetClass, setFilterAssetClass] = useState<string>("ALL");
    const [filterRegion, setFilterRegion] = useState<string>("ALL");

    // Load holdings on mount and when page changes
    useEffect(() => {
        loadHoldings();
    }, [page]);

    const loadHoldings = async () => {
        setLoading(true);
        setError(null);

        try {
            const response = await api.holdings.list(page, pageSize);
            // Handle both paginated response and array response
            if (Array.isArray(response)) {
                setHoldings(response);
                setTotalCount(response.length);
            } else {
                setHoldings(response.results || []);
                setTotalCount(response.count || 0);
            }
        } catch (err) {
            const error = err as Error;
            setError(error.message || "資産情報の読み込みに失敗しました");
            setHoldings([]); // Reset to empty array on error
            setTotalCount(0);
        } finally {
            setLoading(false);
        }
    };

    const handleFormSuccess = () => {
        setShowForm(false);
        setEditingId(null);
        loadHoldings();
    };

    const handleDelete = async (id: number) => {
        if (!confirm("この資産を削除してもよろしいですか?")) {
            return;
        }

        try {
            await api.holdings.delete(id);
            loadHoldings();
        } catch (err) {
            const error = err as Error;
            setError(error.message || "資産の削除に失敗しました");
        }
    };

    const handleEdit = (id: number) => {
        setEditingId(id);
        setShowForm(true);
    };

    const handleCancel = () => {
        setShowForm(false);
        setEditingId(null);
    };

    const totalPages = Math.ceil(totalCount / pageSize);

    // Options for filters from current holdings
    const accountTypeOptions = useMemo(() => {
        return Array.from(new Set(holdings.map(h => h.account_type)));
    }, [holdings]);

    const assetClassOptions = useMemo(() => {
        return Array.from(new Set(holdings.map(h => h.asset_class)));
    }, [holdings]);

    const regionOptions = useMemo(() => {
        return Array.from(new Set(holdings.map(h => h.asset_region)));
    }, [holdings]);

    // Apply filters
    const filteredHoldings = useMemo(() => {
        return holdings.filter(h => {
            if (filterAccountType !== "ALL" && h.account_type !== filterAccountType) return false;
            if (filterAssetClass !== "ALL" && h.asset_class !== filterAssetClass) return false;
            if (filterRegion !== "ALL" && h.asset_region !== filterRegion) return false;
            return true;
        });
    }, [holdings, filterAccountType, filterAssetClass, filterRegion]);

    if (loading && (!holdings || holdings.length === 0)) {
        return (
            <div className="flex items-center justify-center py-12">
                <div className="text-center">
                    <div className="spinner mb-4"></div>
                    <p className="text-gray-600 dark:text-gray-400">読み込み中...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6 animate-fadeIn">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div>
                    <h1 className="text-3xl font-bold text-gray-900 dark:text-white">保有資産管理</h1>
                    <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">投資資産の登録と管理</p>
                </div>
                {!showForm && (
                    <button
                        onClick={() => setShowForm(true)}
                        className="btn btn-success"
                    >
                        <span className="mr-2">+</span>
                        資産を追加
                    </button>
                )}
            </div>

            {/* Error Display */}
            {error && (
                <div className="alert alert-error">
                    <p className="text-sm font-medium">{error}</p>
                </div>
            )}

            {/* Form Section */}
            {showForm && (
                <div className="card">
                    <h2 className="mb-6 text-xl font-semibold text-gray-900 dark:text-white">
                        {editingId ? "資産を編集" : "新規資産を追加"}
                    </h2>
                    <HoldingsForm
                        onSuccess={handleFormSuccess}
                        onError={(err) => setError(err)}
                        isEditing={editingId !== null}
                        holdingId={editingId || undefined}
                        initialValues={
                            editingId
                                ? holdings?.find((h) => h.id === editingId)
                                : undefined
                        }
                    />
                    <button
                        onClick={handleCancel}
                        className="mt-4 btn btn-secondary text-sm"
                    >
                        キャンセル
                    </button>
                </div>
            )}

            {/* Holdings List */}
            <div className="card">
                <div className="flex items-center justify-between mb-6">
                    <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                        保有資産一覧
                    </h2>
                    <div className="flex items-center gap-2">
                        <span className="badge badge-secondary">
                            表示: {filteredHoldings.length}件
                        </span>
                        <span className="badge badge-primary">
                            全体: {totalCount}件
                        </span>
                    </div>
                </div>

                {/* Filters */}
                <div className="mb-4 grid grid-cols-1 md:grid-cols-3 gap-3">
                    <div>
                        <label className="block text-sm text-gray-600 dark:text-gray-300 mb-1">口座種別</label>
                        <select
                            className="border rounded px-3 py-2 w-full bg-white dark:bg-gray-800"
                            value={filterAccountType}
                            onChange={(e) => setFilterAccountType(e.target.value)}
                        >
                            <option value="ALL">すべて</option>
                            {accountTypeOptions.map((opt) => (
                                <option key={opt} value={opt}>
                                    {ACCOUNT_TYPE_LABELS[opt] || opt}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm text-gray-600 dark:text-gray-300 mb-1">資産クラス</label>
                        <select
                            className="border rounded px-3 py-2 w-full bg-white dark:bg-gray-800"
                            value={filterAssetClass}
                            onChange={(e) => setFilterAssetClass(e.target.value)}
                        >
                            <option value="ALL">すべて</option>
                            {assetClassOptions.map((opt) => (
                                <option key={opt} value={opt}>
                                    {ASSET_CLASS_LABELS[opt] || opt}
                                </option>
                            ))}
                        </select>
                    </div>
                    <div>
                        <label className="block text-sm text-gray-600 dark:text-gray-300 mb-1">投資先</label>
                        <select
                            className="border rounded px-3 py-2 w-full bg-white dark:bg-gray-800"
                            value={filterRegion}
                            onChange={(e) => setFilterRegion(e.target.value)}
                        >
                            <option value="ALL">すべて</option>
                            {regionOptions.map((opt) => (
                                <option key={opt} value={opt}>
                                    {ASSET_REGION_LABELS[opt] || opt}
                                </option>
                            ))}
                        </select>
                    </div>
                </div>

                {!holdings || holdings.length === 0 ? (
                    <div className="alert alert-info text-center py-12">
                        <p className="text-lg font-medium mb-2">📊 資産がまだ登録されていません</p>
                        <p className="text-sm">
                            最初の投資資産を追加しましょう!
                        </p>
                    </div>
                ) : (
                    <div className="overflow-x-auto rounded-lg border border-gray-200 dark:border-gray-700">
                        <table className="table">
                            <thead>
                                <tr>
                                    <th>
                                        名称
                                    </th>
                                    <th className="border border-gray-200 px-4 py-2 text-left text-sm font-semibold">
                                        識別コード
                                    </th>
                                    <th className="border border-gray-200 px-4 py-2 text-left text-sm font-semibold">
                                        口座種別
                                    </th>
                                    <th className="border border-gray-200 px-4 py-2 text-left text-sm font-semibold">
                                        資産クラス
                                    </th>
                                    <th className="border border-gray-200 px-4 py-2 text-left text-sm font-semibold">
                                        投資先
                                    </th>
                                    <th className="border border-gray-200 px-4 py-2 text-right text-sm font-semibold">
                                        金額 (円)
                                    </th>
                                    <th className="border border-gray-200 px-4 py-2 text-center text-sm font-semibold">
                                        操作
                                    </th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredHoldings?.map((holding) => (
                                    <tr key={holding.id}>
                                        <td className="font-medium">
                                            {holding.asset_name}
                                        </td>
                                        <td className="border border-gray-200 px-4 py-2 text-sm">
                                            {holding.asset_identifier}
                                        </td>
                                        <td className="border border-gray-200 px-4 py-2 text-sm">
                                            {ACCOUNT_TYPE_LABELS[holding.account_type] || holding.account_type}
                                        </td>
                                        <td className="border border-gray-200 px-4 py-2 text-sm">
                                            {ASSET_CLASS_LABELS[holding.asset_class] || holding.asset_class}
                                        </td>
                                        <td className="border border-gray-200 px-4 py-2 text-sm">
                                            {ASSET_REGION_LABELS[holding.asset_region] || holding.asset_region}
                                        </td>
                                        <td className="border border-gray-200 px-4 py-2 text-right font-mono">
                                            ¥{Number(holding.current_amount_jpy || 0).toLocaleString("ja-JP")}
                                        </td>
                                        <td className="text-center">
                                            <div className="flex items-center justify-center gap-2">
                                                <button
                                                    onClick={() => holding.id && handleEdit(holding.id)}
                                                    className="px-3 py-1 text-xs font-medium text-blue-600 dark:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded transition-colors"
                                                >
                                                    編集
                                                </button>
                                                <button
                                                    onClick={() => holding.id && handleDelete(holding.id)}
                                                    className="px-3 py-1 text-xs font-medium text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/30 rounded transition-colors"
                                                >
                                                    削除
                                                </button>
                                            </div>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}

                {/* Pagination */}
                {totalPages > 1 && (
                    <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-200 dark:border-gray-700">
                        <button
                            onClick={() => setPage((p) => Math.max(1, p - 1))}
                            disabled={page === 1}
                            className="btn btn-secondary"
                        >
                            ← 前へ
                        </button>
                        <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                            {page} / {totalPages} ページ
                        </span>
                        <button
                            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
                            disabled={page === totalPages}
                            className="btn btn-secondary"
                        >
                            次へ →
                        </button>
                    </div>
                )}
            </div>
        </div>
    );
}

export default withAuth(InputPage);
