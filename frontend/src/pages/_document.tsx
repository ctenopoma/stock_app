import { Head, Html, Main, NextScript } from 'next/document';

export default function Document() {
    return (
        <Html lang="ja" className="light">
            <Head>
                <meta charSet="utf-8" />
                <link rel="icon" href="/stock_app/favicon.ico" />

                {/* PWA設定 */}
                <link rel="manifest" href="/stock_app/manifest.json" />

                {/* iOS用アイコン */}
                <link rel="apple-touch-icon" href="/stock_app/apple-touch-icon.png" />

                {/* iOS用メタタグ */}
                <meta name="apple-mobile-web-app-capable" content="yes" />
                <meta name="apple-mobile-web-app-status-bar-style" content="default" />
                <meta name="apple-mobile-web-app-title" content="Stock App" />

                {/* テーマカラー */}
                <meta name="theme-color" content="#1f2937" />

                {/* その他のPWA設定 */}
                <meta name="mobile-web-app-capable" content="yes" />
            </Head>
            <body className="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
                <Main />
                <NextScript />
            </body>
        </Html>
    );
}
