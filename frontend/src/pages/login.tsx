import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/router';
import { FormEvent, useState } from 'react';

export default function LoginPage() {
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const { login } = useAuth();
    const router = useRouter();

    const handleSubmit = async (e: FormEvent) => {
        e.preventDefault();
        setError('');
        setIsLoading(true);

        try {
            await login(username, password);
            // ログイン成功後、元のページまたはホームにリダイレクト
            const returnUrl = (router.query.returnUrl as string) || '/input';
            router.push(returnUrl);
        } catch (err: any) {
            setError(err.message || 'ログインに失敗しました');
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 py-12 px-4 sm:px-6 lg:px-8">
            <div className="max-w-md w-full">
                {/* ロゴとタイトル */}
                <div className="text-center mb-8">
                    <div className="flex justify-center mb-4">
                        <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-4 rounded-2xl shadow-lg">
                            <img src="/logo.png" alt="Logo" className="w-16 h-16" />
                        </div>
                    </div>
                    <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent mb-2">
                        FinSight
                    </h1>
                    <p className="text-gray-600 dark:text-gray-400 text-sm">
                        あなたの投資ポートフォリオを最適化
                    </p>
                </div>

                {/* ログインフォーム */}
                <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8 border border-gray-200 dark:border-gray-700">
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6 text-center">
                        ログイン
                    </h2>

                    <form className="space-y-5" onSubmit={handleSubmit}>
                        {error && (
                            <div className="bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 px-4 py-3 rounded-lg text-sm flex items-center" role="alert">
                                <span className="mr-2">⚠️</span>
                                {error}
                            </div>
                        )}

                        <div>
                            <label htmlFor="username" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                ユーザー名
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <span className="text-gray-400">👤</span>
                                </div>
                                <input
                                    id="username"
                                    name="username"
                                    type="text"
                                    autoComplete="username"
                                    required
                                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 transition-all"
                                    placeholder="ユーザー名を入力"
                                    value={username}
                                    onChange={(e) => setUsername(e.target.value)}
                                    disabled={isLoading}
                                />
                            </div>
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                パスワード
                            </label>
                            <div className="relative">
                                <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                                    <span className="text-gray-400">🔒</span>
                                </div>
                                <input
                                    id="password"
                                    name="password"
                                    type="password"
                                    autoComplete="current-password"
                                    required
                                    className="block w-full pl-10 pr-3 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-400 transition-all"
                                    placeholder="パスワードを入力"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    disabled={isLoading}
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-semibold py-3 px-4 rounded-lg shadow-lg hover:shadow-xl transform hover:-translate-y-0.5 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none"
                            disabled={isLoading}
                        >
                            {isLoading ? (
                                <span className="flex items-center justify-center">
                                    <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                    </svg>
                                    ログイン中...
                                </span>
                            ) : (
                                'ログイン'
                            )}
                        </button>
                    </form>

                    {/* デモアカウント情報 */}
                    <div className="mt-6 p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <p className="text-xs text-blue-800 dark:text-blue-300 font-medium mb-2">
                            💡 デモアカウント
                        </p>
                        <div className="text-xs text-blue-600 dark:text-blue-400 space-y-1">
                            <p>ユーザー名: <code className="bg-white dark:bg-gray-700 px-2 py-0.5 rounded">testuser</code></p>
                            <p>パスワード: <code className="bg-white dark:bg-gray-700 px-2 py-0.5 rounded">testpass123</code></p>
                        </div>
                    </div>
                </div>

                {/* フッター */}
                <div className="mt-6 text-center text-sm text-gray-500 dark:text-gray-400">
                    © 2025 FinSight. All rights reserved.
                </div>
            </div>
        </div>
    );
}
