import { Head, Html, Main, NextScript } from 'next/document';

export default function Document() {
    return (
        <Html lang="ja" className="light">
            <Head>
                <meta charSet="utf-8" />
                <link rel="icon" href="/favicon.ico" />
            </Head>
            <body className="bg-gray-50 dark:bg-gray-900 text-gray-900 dark:text-gray-100">
                <Main />
                <NextScript />
            </body>
        </Html>
    );
}
