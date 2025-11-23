/**
 * Layout Component - 共通レイアウトとナビゲーション
 */
import { useAuth } from '@/contexts/AuthContext';
import { useTheme } from '@/contexts/ThemeContext';
import Link from 'next/link';
import { useRouter } from 'next/router';
import { ReactNode } from 'react';

interface LayoutProps {
    children: ReactNode;
}

export default function Layout({ children }: LayoutProps) {
    const router = useRouter();
    const { user, logout } = useAuth();

    // ThemeContextが利用可能かチェック
    let theme: 'light' | 'dark' = 'light';
    let toggleTheme: (() => void) | undefined;

    try {
        const themeContext = useTheme();
        theme = themeContext.theme;
        toggleTheme = themeContext.toggleTheme;
    } catch (e) {
        // サーバーサイドレンダリング時はデフォルト値を使用
    }

    const navigation = [
        { name: '保有資産', href: '/input', icon: '📊' },
        { name: 'ポートフォリオ', href: '/portfolio', icon: '💼' },
        { name: '積立計画', href: '/plans', icon: '📅' },
        { name: '将来予測', href: '/projections', icon: '📈' },
    ];

    const isActive = (href: string) => router.pathname === href;

    const handleLogout = async () => {
        try {
            await logout();
            router.push('/login');
        } catch (error) {
            console.error('Logout failed:', error);
        }
    };

    // ログインページではレイアウトをスキップ
    if (router.pathname === '/login') {
        return <>{children}</>;
    }

    return (
        <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-200">
            {/* Header */}
            <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex justify-between items-center h-16">
                        {/* Logo */}
                        <Link href="/" className="flex items-center space-x-2">
                            <img src="/logo.png" alt="Logo" className="w-8 h-8" />
                            <span className="text-xl font-bold bg-gradient-to-r from-blue-600 to-purple-600 bg-clip-text text-transparent">
                                FinSight
                            </span>
                        </Link>

                        {/* Desktop Navigation */}
                        <nav className="hidden md:flex items-center space-x-1">
                            {navigation.map((item) => (
                                <Link
                                    key={item.name}
                                    href={item.href}
                                    className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${isActive(item.href)
                                        ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                                        : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                                        }`}
                                >
                                    <span className="mr-2">{item.icon}</span>
                                    {item.name}
                                </Link>
                            ))}
                        </nav>

                        {/* Theme Toggle */}
                        {toggleTheme && (
                            <div className="flex items-center space-x-2">
                                {user && (
                                    <div className="hidden sm:flex items-center space-x-3">
                                        <span className="text-sm text-gray-700 dark:text-gray-300">
                                            👤 {user.username}
                                        </span>
                                        <button
                                            onClick={handleLogout}
                                            className="px-3 py-1.5 text-sm rounded-lg bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 hover:bg-red-200 dark:hover:bg-red-800 transition-colors"
                                        >
                                            ログアウト
                                        </button>
                                    </div>
                                )}
                                <button
                                    onClick={toggleTheme}
                                    className="p-2 rounded-lg bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                                    aria-label="テーマ切り替え"
                                >
                                    {theme === 'light' ? '🌙' : '☀️'}
                                </button>
                            </div>
                        )}
                    </div>

                    {/* Mobile Navigation */}
                    <nav className="md:hidden flex overflow-x-auto pb-2 space-x-2 -mx-2 px-2">
                        {navigation.map((item) => (
                            <Link
                                key={item.name}
                                href={item.href}
                                className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${isActive(item.href)
                                    ? 'bg-blue-100 dark:bg-blue-900 text-blue-700 dark:text-blue-300'
                                    : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700'
                                    }`}
                            >
                                <span className="mr-1">{item.icon}</span>
                                {item.name}
                            </Link>
                        ))}
                    </nav>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {children}
            </main>

            {/* Footer */}
            <footer className="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 mt-auto">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
                    <div className="text-center text-sm text-gray-600 dark:text-gray-400">
                        © 2025 FinSight. All rights reserved.
                    </div>
                </div>
            </footer>
        </div>
    );
}
