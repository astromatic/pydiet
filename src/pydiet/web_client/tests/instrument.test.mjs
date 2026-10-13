import assert from 'node:assert/strict';
import test from 'node:test';
import {loadModule, storage} from './helpers.mjs';

async function setup(payload) {
    const localStorage = storage(), requests = [], updates = [], loading = [];
    const api = await loadModule('instrument.js', {localStorage}, {
        '@ionic/core': {loadingController: {create: async () => ({
            present: () => loading.push('present'), dismiss: () => loading.push('dismiss'),
        })}},
        './url': {etc_url: '/prefix/api'},
        './etc': {update_etcform: value => updates.push(value)},
        './fetch': {fetch_data: async url => { requests.push(url); return payload; }},
    });
    return {api, localStorage, requests, updates, loading};
}

for (const payload of [{demo: {id: 'demo'}}, false]) {
    test(`instrument requests cache ${payload === false ? 'failure' : 'success'}`, async () => {
        // Sequential calls reuse the loaded result instead of fetching again.
        const {api, requests, loading} = await setup(payload);
        assert.equal(await api.get_instruments(), payload);
        assert.equal(await api.get_instruments(), payload);
        assert.deepEqual(requests, ['/prefix/api/instruments']);
        assert.deepEqual(loading, ['present', 'dismiss']);
    });
}

test('filter selections persist independently for each instrument', async () => {
    // Falsy updates retrieve the existing selection without overwriting it.
    const {api} = await setup({});
    assert.equal(api.get_filterID('megacam'), null);
    assert.equal(api.update_filter('megacam', 'g'), 'g');
    assert.equal(api.update_filter('wircam', 'J'), 'J');
    assert.equal(api.update_filter('megacam'), 'g');
    assert.equal(api.update_filter('megacam', ''), 'g');
    assert.equal(api.get_filterID('wircam'), 'J');
});

test('selecting an instrument rebuilds its form and persists its ID', async () => {
    // Exercise selection in strict module scope without a browser global named instrument.
    const demo = {id: 'demo'};
    const {api, updates} = await setup({demo});
    assert.equal(api.get_instrumentID(), null);
    await api.get_instruments();
    assert.equal(api.update_instrument('demo'), undefined);
    // The public function starts asynchronous work but does not return its promise.
    await new Promise(resolve => setImmediate(resolve));
    assert.deepEqual(updates, [demo]);
    assert.equal(api.get_instrumentID(), 'demo');
});
