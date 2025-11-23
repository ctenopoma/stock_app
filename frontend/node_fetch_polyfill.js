// Lightweight polyfill to provide Headers/Request/Response and fetch on Node builds
// Uses node-fetch v2 (CommonJS) if available.
try {
    // eslint-disable-next-line global-require, @typescript-eslint/no-var-requires
    const nodeFetch = require('node-fetch');
    if (nodeFetch) {
        if (typeof global.Headers === 'undefined' && nodeFetch.Headers) {
            global.Headers = nodeFetch.Headers;
        }
        if (typeof global.Request === 'undefined' && nodeFetch.Request) {
            global.Request = nodeFetch.Request;
        }
        if (typeof global.Response === 'undefined' && nodeFetch.Response) {
            global.Response = nodeFetch.Response;
        }
        if (typeof global.fetch === 'undefined') {
            global.fetch = nodeFetch;
        }
    }
} catch (err) {
    // ignore if node-fetch is not installed yet
}

// Polyfill Web Streams (ReadableStream, WritableStream, TransformStream) for older Node
try {
    // eslint-disable-next-line global-require, @typescript-eslint/no-var-requires
    const ponyfill = require('web-streams-polyfill/ponyfill');
    if (ponyfill) {
        if (typeof global.ReadableStream === 'undefined' && ponyfill.ReadableStream) {
            global.ReadableStream = ponyfill.ReadableStream;
        }
        if (typeof global.WritableStream === 'undefined' && ponyfill.WritableStream) {
            global.WritableStream = ponyfill.WritableStream;
        }
        if (typeof global.TransformStream === 'undefined' && ponyfill.TransformStream) {
            global.TransformStream = ponyfill.TransformStream;
        }
    }
} catch (err) {
    // ignore if not installed
}
