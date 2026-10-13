import assert from 'node:assert/strict';
import test from 'node:test';
import {loadModule} from './helpers.mjs';

test('JSON requests include credentials and return the decoded payload', async () => {
    // Preserve API data while passing browser credentials to fetch.
    const payload = {demo: {name: 'Demo'}};
    let request;
    const api = await loadModule('fetch.js', {
        fetch: async (...args) => {
            request = args;
            return {ok: true, json: async () => payload};
        },
    }, {'./dom': {inject_html() {}}});
    assert.equal(await api.fetch_data('/api/instruments'), payload);
    assert.equal(request[0], '/api/instruments');
    assert.equal(request[1].credentials, 'include');
});

for (const failure of ['http', 'network', 'decode']) {
    test(`JSON ${failure} failures return false`, async () => {
        // Keep all supported fetch failure modes from escaping to callers.
        const api = await loadModule('fetch.js', {
            fetch: async () => {
                if (failure === 'network') throw new Error('offline');
                return {ok: failure !== 'http', json: async () => { throw new Error('bad JSON'); }};
            },
        }, {'./dom': {inject_html() {}}});
        assert.equal(await api.fetch_data('/api/instruments'), false);
    });
}

for (const method of ['get', 'post']) {
    test(`HTML ${method} requests transmit form values and inject the response`, async () => {
        // Encode GET fields safely and preserve the original POST body.
        const requests = [], injections = [];
        const api = await loadModule('fetch.js', {
            URLSearchParams,
            fetch: async (...args) => {
                requests.push(args);
                return {ok: true, text: async () => '<p>Ready</p>'};
            },
        }, {'./dom': {inject_html: (...args) => injections.push(args)}});
        const data = new URLSearchParams({filter: 'H alpha', brightness: '22'});
        assert.equal(await api.fetch_html('#results', '/ui/results', {method, data}), true);
        const [url, options] = requests[0];
        assert.equal(options.credentials, 'include');
        if (method === 'get') {
            const parsed = new URL(url, 'https://example.test');
            assert.equal(parsed.searchParams.get('filter'), 'H alpha');
            assert.equal(parsed.searchParams.get('brightness'), '22');
        } else {
            assert.equal(url, '/ui/results');
            assert.equal(options.method, 'post');
            assert.equal(options.body, data);
        }
        assert.deepEqual(injections, [['#results', '<p>Ready</p>']]);
        assert.equal(await api.fetch_html('#results', '/ui/form'), true);
        assert.equal(requests[1][0], '/ui/form');
    });
}

for (const failure of ['http', 'network', 'decode', 'injection']) {
    test(`HTML ${failure} failures return false`, async () => {
        // Failed downloads must not replace contents; failed injection is reported.
        let injections = 0;
        const api = await loadModule('fetch.js', {
            fetch: async () => {
                if (failure === 'network') throw new Error('offline');
                return {ok: failure !== 'http', text: async () => {
                    if (failure === 'decode') throw new Error('bad body');
                    return '<p>Ready</p>';
                }};
            },
        }, {'./dom': {inject_html() { injections++; throw new Error('missing target'); }}});
        assert.equal(await api.fetch_html('#results', '/ui/results'), false);
        assert.equal(injections, failure === 'injection' ? 1 : 0);
    });
}
