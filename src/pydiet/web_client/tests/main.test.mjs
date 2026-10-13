import assert from 'node:assert/strict';
import test from 'node:test';
import {loadModule} from './helpers.mjs';

test('startup activates monitoring and themes before instrument loading completes', async () => {
    // Delayed API data must reach the instrument selector without delaying other setup.
    const calls = [], instruments = {demo: {name: 'Demo'}};
    let resolve;
    const pending = new Promise(done => { resolve = done; });
    await loadModule('main.js', {}, {
        './health': {setup_health: () => calls.push('health')},
        './instrument': {get_instruments: () => pending},
        './settings': {
            setup_theme_settings: () => calls.push('theme'),
            setup_instrument_settings: value => calls.push(value),
        },
    });
    assert.deepEqual(calls, ['health', 'theme']);
    resolve(instruments);
    await new Promise(done => setImmediate(done));
    assert.deepEqual(calls, ['health', 'theme', instruments]);
});
