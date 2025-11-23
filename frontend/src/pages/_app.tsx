import Layout from '@/components/Layout';
import { AuthProvider } from '@/contexts/AuthContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import '@/styles/globals.css';
import type { AppProps } from 'next/app';

export default function App({ Component, pageProps }: AppProps) {
    return (
        <ThemeProvider>
            <AuthProvider>
                <Layout>
                    <Component {...pageProps} />
                </Layout>
            </AuthProvider>
        </ThemeProvider>
    );
}
