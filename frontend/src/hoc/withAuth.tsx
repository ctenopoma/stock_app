import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/router';
import { ComponentType, useEffect } from 'react';

/**
 * 認証が必要なページを保護するHOC
 */
export function withAuth<P extends object>(Component: ComponentType<P>) {
    return function ProtectedRoute(props: P) {
        const { user, isLoading } = useAuth();
        const router = useRouter();

        useEffect(() => {
            if (!isLoading && !user) {
                // 未認証の場合、ログインページにリダイレクト
                const returnUrl = router.asPath;
                router.push(`/login?returnUrl=${encodeURIComponent(returnUrl)}`);
            }
        }, [user, isLoading, router]);

        // ローディング中またはリダイレクト中は何も表示しない
        if (isLoading || !user) {
            return (
                <div className="min-h-screen flex items-center justify-center">
                    <div className="text-center">
                        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
                        <p className="mt-4 text-gray-600 dark:text-gray-400">読み込み中...</p>
                    </div>
                </div>
            );
        }

        return <Component {...props} />;
    };
}
