import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/router';
import { useEffect } from 'react';

export default function Home() {
    const router = useRouter();
    const { user, isLoading } = useAuth();

    useEffect(() => {
        if (!isLoading) {
            if (user) {
                // ログイン済みの場合は入力画面へ
                router.replace('/input');
            } else {
                // 未ログインの場合はログイン画面へ
                router.replace('/login');
            }
        }
    }, [router, user, isLoading]);

    return null;
}
