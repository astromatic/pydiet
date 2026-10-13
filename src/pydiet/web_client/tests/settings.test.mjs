import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import {createContext, SourceTextModule, SyntheticModule} from 'node:vm';
import {loadModule} from './helpers.mjs';

const source = await readFile(new URL('../js/settings.js', import.meta.url), 'utf8');

async function setup(instruments, storedId, present = true) {
    const updates = [];
    const listeners = {};
    const segment = {
        children: [],
        appendChild(child) { this.children.push(child); },
        addEventListener(name, callback) { listeners[name] = callback; },
    };
    const context = createContext({
        document: {
            querySelector: () => present ? segment : null,
            createElement: () => ({appendChild() {}}),
        },
    });
    const module = new SourceTextModule(source, {
        context, identifier: new URL('../js/settings.js', import.meta.url).href,
    });
    await module.link(specifier => {
        const exports = specifier === './instrument' ? {
            get_instrumentID: () => storedId,
            update_instrument: id => updates.push(id),
        } : {
            get_theme() {}, update_theme() {}, themes: [], theme_icons: [],
        };
        return new SyntheticModule(Object.keys(exports), function () {
            for (const [key, value] of Object.entries(exports)) {
                this.setExport(key, value);
            }
        }, {context});
    });
    await module.evaluate();
    module.namespace.setup_instrument_settings(instruments);
    return {updates, listeners, segment};
}

for (const storedId of [null, 'removed', 'toString', 'first']) {
    test(`instrument selection with persisted ID ${storedId}`, async () => {
        // Retain valid storage; missing, stale and inherited IDs use the API default.
        const {updates, listeners, segment} = await setup({
            first: {name: 'First'},
            preferred: {name: 'Preferred', default: true},
        }, storedId);
        const expected = storedId === 'first' ? 'first' : 'preferred';
        assert.equal(segment.value, expected);
        assert.deepEqual(updates, [expected]);
        assert.deepEqual(segment.children.map(button => button.value), ['first', 'preferred']);
        listeners.ionChange({detail: {value: 'first'}});
        assert.deepEqual(updates, [expected, 'first']);
    });
}

test('first instrument is the fallback without an API default', async () => {
    // Use dictionary order when neither storage nor an API default selects an ID.
    const {updates} = await setup({demo: {name: 'Demo'}, second: {name: 'Second'}}, null);
    assert.deepEqual(updates, ['demo']);
});

test('the documented single-instrument example selects its default', async () => {
    // Verify the JSDoc example through the exported function.
    const {updates} = await setup({demo: {name: 'Demo camera', default: true}}, null);
    assert.deepEqual(updates, ['demo']);
});

test('empty instruments or an absent selector do not activate controls', async () => {
    // Avoid updating an undefined instrument or binding unusable controls.
    for (const [instruments, present] of [[{}, true], [{demo: {name: 'Demo'}}, false]]) {
        const {updates, listeners, segment} = await setup(instruments, null, present);
        assert.deepEqual(updates, []);
        assert.deepEqual(listeners, {});
        assert.deepEqual(segment.children, []);
    }
});

for (const present of [true, false]) {
    test(`theme settings ${present ? 'populate choices and handle changes' : 'allow an absent selector'}`, async () => {
        // Initialize the saved theme and connect user changes only when controls exist.
        const updates = [], listeners = {}, segment = {children: [],
            appendChild(child) { this.children.push(child); },
            addEventListener(name, callback) { listeners[name] = callback; },
        };
        const api = await loadModule('settings.js', {document: {
            querySelector: selector => {
                assert.equal(selector, '#theme-segment');
                return present ? segment : null;
            },
            createElement: () => ({children: [], appendChild(child) { this.children.push(child); }}),
        }}, {
            './instrument': {get_instrumentID() {}, update_instrument() {}},
            './theme': {
                get_theme: () => 'dark', update_theme: theme => updates.push(theme),
                themes: ['Light', 'Dark', 'Auto'], theme_icons: ['sunny', 'moon', 'contrast'],
            },
        });
        api.setup_theme_settings();
        if (present) {
            assert.equal(segment.value, 'dark');
            assert.deepEqual(segment.children.map(button => button.value), ['light', 'dark', 'auto']);
            assert.deepEqual(segment.children.map(button => button.children[0].innerHTML), ['Light', 'Dark', 'Auto']);
            assert.deepEqual(segment.children.map(button => button.children[1].name), ['sunny', 'moon', 'contrast']);
            assert.deepEqual(updates, ['dark']);
            listeners.ionChange({detail: {value: 'auto'}});
            assert.deepEqual(updates, ['dark', 'auto']);
        } else {
            assert.deepEqual(segment.children, []);
            assert.deepEqual(updates, []);
            assert.deepEqual(listeners, {});
        }
    });
}
