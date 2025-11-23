import { api, User } from '@/services/api';
import { createContext, ReactNode, useContext, useEffect, useState } from 'react';

interface AuthContextType {
    user: User | null;
    isLoading: boolean;
    login: (username: string, password: string) => Promise<void>;
    logout: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    useEffect(() => {
        // 初回ロード時にローカルストレージから暫定復元
        const storedUser = localStorage.getItem('user');
        if (storedUser) {
            try {
                setUser(JSON.parse(storedUser));
            } catch (e) {
                localStorage.removeItem('user');
            }
        }
        // サーバーセッションを確認して正とする
        (async () => {
            try {
                const me = await api.auth.me();
                setUser(me);
                localStorage.setItem('user', JSON.stringify(me));
            } catch (_) {
                // 未ログインの場合は無視
            } finally {
                setIsLoading(false);
            }
        })();
    }, []);

    const login = async (username: string, password: string) => {
        try {
            const userData = await api.auth.login(username, password);
            console.log('[AuthContext] Login successful:', userData);
            console.log('[AuthContext] Cookies after login:', document.cookie);
            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));
        } catch (error: any) {
            // エラーメッセージを日本語に変換
            if (error.message?.includes('Unable to log in with provided credentials')) {
                throw new Error('ユーザー名またはパスワードが間違っています');
            } else if (error.message?.includes('User account is disabled')) {
                throw new Error('このアカウントは無効化されています');
            } else if (error.status === 401 || error.status === 403) {
                throw new Error('認証に失敗しました');
            }
            throw error;
        }
    };

    const logout = async () => {
        try {
            await api.auth.logout();
        } catch (error) {
            console.error('Logout error:', error);
        } finally {
            setUser(null);
            localStorage.removeItem('user');
        }
    };

    return (
        <AuthContext.Provider value={{ user, isLoading, login, logout }}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
