// Next.js config with a server-side polyfill for Headers/Request/Response
// Uses `node-fetch@2` (CommonJS) to provide global Headers when missing during build

try {
    // require node-fetch only when available; this keeps build safe if not installed yet
    // node-fetch v2 exports Headers/Request/Response on the fetch() function object
    // This block is safe to run in Node build/runtime.
    // eslint-disable-next-line global-require, @typescript-eslint/no-var-requires
    const nodeFetch = require('node-fetch');
    if (typeof global.Headers === 'undefined' && nodeFetch && nodeFetch.Headers) {
        // node-fetch v2: nodeFetch.Headers exists
        global.Headers = nodeFetch.Headers;
    }
    if (typeof global.Request === 'undefined' && nodeFetch && nodeFetch.Request) {
        global.Request = nodeFetch.Request;
    }
    if (typeof global.Response === 'undefined' && nodeFetch && nodeFetch.Response) {
        global.Response = nodeFetch.Response;
    }
} catch (err) {
    // If node-fetch is not installed yet, ignore - installer step will add it.
    // We purposely swallow errors here because this file is required during build.
}

/** @type {import('next').NextConfig} */
module.exports = {
    reactStrictMode: true,
    trailingSlash: true,
    basePath: '/stock_app',
    assetPrefix: '/stock_app',
    async rewrites() {
        // バックエンドのホスト（環境変数から取得、デフォルトは127.0.0.1）
        const backendHost = process.env.BACKEND_HOST || '127.0.0.1';
        const backendPort = process.env.BACKEND_PORT || '8000';
        const backendUrl = `http://${backendHost}:${backendPort}`;

        console.log(`[Next.js] API proxy configured: ${backendUrl}/api/v1`);

        return {
            beforeFiles: [
                // Match paths with trailing slash
                {
                    source: '/api/v1/:path*/',
                    destination: `${backendUrl}/api/v1/:path*/`,
                },
                // Match paths without trailing slash and add it
                {
                    source: '/api/v1/:path*',
                    destination: `${backendUrl}/api/v1/:path*/`,
                },
            ],
        };
    },
};
