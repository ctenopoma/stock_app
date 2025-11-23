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
        const userData = await api.auth.login(username, password);
        console.log('[AuthContext] Login successful:', userData);
        console.log('[AuthContext] Cookies after login:', document.cookie);
        setUser(userData);
        localStorage.setItem('user', JSON.stringify(userData));
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
