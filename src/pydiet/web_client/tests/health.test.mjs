import assert from 'node:assert/strict';
import test from 'node:test';
import {loadModule} from './helpers.mjs';

for (const status of ['ok', 'unhealthy', 'http', 'network', 'decode', 'timeout']) {
    test(`health monitor reports ${status} and cleans up its timeout`, async () => {
        // Drive the public monitor using fake timers, without network access or real delays.
        const classes = new Map(), timeouts = new Map(), cleared = [], requests = [];
        const element = {classList: {toggle: (name, value) => classes.set(name, value)}};
        let interval, milliseconds, timerID = 0;
        const api = await loadModule('health.js', {
            AbortController,
            document: {getElementById: () => element},
            setTimeout: (callback, delay) => {
                assert.equal(delay, 2000);
                timeouts.set(++timerID, callback);
                return timerID;
            },
            clearTimeout: id => cleared.push(id),
            setInterval: (callback, delay) => { interval = callback; milliseconds = delay; },
            fetch: async (url, options) => {
                requests.push([url, options]);
                if (status === 'timeout') {
                    return new Promise((resolve, reject) => options.signal.addEventListener('abort', () => reject(new Error('aborted'))));
                }
                if (status === 'network') throw new Error('offline');
                return {ok: status !== 'http', status: 503, json: async () => {
                    if (status === 'decode') throw new Error('bad JSON');
                    return {ok: status === 'ok'};
                }};
            },
        }, {'./url': {etc_url: '/prefix/api'}});
        api.setup_health();
        assert.equal(requests.length, 1);
        assert.equal(milliseconds, 10000);
        if (status === 'timeout') timeouts.get(1)();
        await new Promise(resolve => setImmediate(resolve));
        assert.equal(classes.get('ok'), status === 'ok');
        assert.equal(classes.get('fail'), status !== 'ok');
        const titles = {ok: 'Server OK', unhealthy: 'Server failed', http: 'Status failed: HTTP 503'};
        assert.equal(element.title, titles[status] ?? 'Server down or unreachable');
        assert.deepEqual(cleared, [1]);
        assert.equal(requests[0][0], '/prefix/api/health');
        assert.equal(requests[0][1].cache, 'no-store');
        assert.equal(requests[0][1].headers.accept, 'application/json');
        const pending = interval();
        if (status === 'timeout') timeouts.get(2)();
        await pending;
        assert.equal(requests.length, 2);
        assert.deepEqual(cleared, [1, 2]);
    });
}
