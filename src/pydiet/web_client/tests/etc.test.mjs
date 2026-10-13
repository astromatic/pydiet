import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import test from 'node:test';
import {createContext, SourceTextModule, SyntheticModule} from 'node:vm';
import {loadModule} from './helpers.mjs';

const source = await readFile(new URL('../js/etc.js', import.meta.url), 'utf8');

async function setup(filters, storedId, present = true) {
    const updates = [];
    const listeners = {};
    const select = {
        children: [],
        get firstChild() { return this.children[0]; },
        get lastChild() { return this.children.at(-1); },
        appendChild(child) {
            this.children.push(child);
            child.remove = () => this.children.splice(this.children.indexOf(child), 1);
        },
    };
    select.appendChild({value: 'placeholder'});
    const context = createContext({
        document: {
            querySelector: selector => selector === '#etc-form' ? {
                addEventListener(name, callback) { listeners[name] = callback; },
            } : present ? select : null,
            createElement: () => ({}),
        },
    });
    const module = new SourceTextModule(source, {
        context, identifier: new URL('../js/etc.js', import.meta.url).href,
    });
    await module.link(specifier => {
        const exports = {
            './dom': {inject_node() {}},
            './fetch': {fetch_data() {}, fetch_html: () => Promise.resolve()},
            './instrument': {
                get_filterID: () => storedId,
                update_filter: (instrument, filter) => updates.push([instrument, filter]),
            },
            './plot': {plot_filter() {}},
            './url': {etc_url: '/api', ui_url: '/ui'},
        }[specifier];
        return new SyntheticModule(Object.keys(exports), function () {
            for (const [key, value] of Object.entries(exports)) {
                this.setExport(key, value);
            }
        }, {context});
    });
    await module.evaluate();
    await module.namespace.update_etcform({id: 'demo', filters: {transmissions: filters}});
    return {updates, listeners, select};
}

for (const storedId of [null, 'removed', 'toString', 'first', 'upload']) {
    test(`filter selection with persisted ID ${storedId}`, async () => {
        // Prefer valid storage, then a configured default even when it is not first.
        const {updates, listeners, select} = await setup({
            first: {name: 'First'},
            preferred: {name: 'Preferred', default: true},
            other: {name: 'Other', default: true},
        }, storedId);
        const expected = ['first', 'upload'].includes(storedId) ? storedId : 'preferred';
        assert.equal(select.value, expected);
        assert.deepEqual(updates, [['demo', expected]]);
        assert.deepEqual(select.children.map(option => option.value),
            ['first', 'preferred', 'other', 'upload']);
        assert.equal(select.children[1].innerHTML, 'Preferred');
        assert.equal(typeof listeners.submit, 'function');
    });
}

test('first filter is the fallback without a configured default', async () => {
    // Preserve dictionary order when no stored or configured selection applies.
    const {updates, select} = await setup({first: {name: 'First'}, second: {name: 'Second'}}, null);
    assert.equal(select.value, 'first');
    assert.deepEqual(updates, [['demo', 'first']]);
});

test('an empty filter collection offers upload', async () => {
    // Keep the upload option usable when the instrument has no configured filters.
    const {updates, select} = await setup({}, 'removed');
    assert.equal(select.value, 'upload');
    assert.deepEqual(updates, [['demo', 'upload']]);
    assert.deepEqual(select.children.map(option => option.value), ['upload']);
});

test('an absent filter selector does not change persisted selection', async () => {
    // Custom forms without the filter menu still attach submission handling.
    const {updates, listeners} = await setup({demo: {name: 'Demo'}}, null, false);
    assert.deepEqual(updates, []);
    assert.equal(typeof listeners.submit, 'function');
});

for (const uploadSize of [undefined, 0, 128]) {
    test(`form submission uses ${uploadSize ? 'POST for an upload' : 'GET without an upload'} (${uploadSize})`, async () => {
        // Prevent browser navigation and retain form fields for the results request.
        const calls = [], fields = [['brightness', '22'], ['filter', 'g']];
        if (uploadSize !== undefined) fields.push(['filter_upload', {size: uploadSize}]);
        let submit, formData, prevented = false;
        const form = {addEventListener: (name, callback) => {
            assert.equal(name, 'submit');
            submit = callback;
        }};
        class FormData {
            constructor(element) { assert.equal(element, form); formData = this; }
            [Symbol.iterator]() { return fields[Symbol.iterator](); }
        }
        const api = await loadModule('etc.js', {
            FormData,
            document: {querySelector: selector => selector === '#etc-form' ? form : null},
        }, {
            './dom': {inject_node() {}},
            './fetch': {fetch_data() {}, fetch_html: async (...args) => { calls.push(args); return true; }},
            './instrument': {get_filterID() {}, update_filter() {}},
            './plot': {plot_filter() {}},
            './url': {etc_url: '/prefix/api', ui_url: '/prefix/ui'},
        });
        await api.update_etcform({id: 'demo', filters: {transmissions: {}}});
        await new Promise(resolve => setImmediate(resolve));
        assert.deepEqual(calls[0], ['#content-slot', '/prefix/ui/demo/etc_form']);
        await submit.call(form, {preventDefault() { prevented = true; }});
        assert.equal(prevented, true);
        assert.equal(calls[1][0], '#modal-slot');
        assert.equal(calls[1][1], '/prefix/ui/demo/etc_results/query');
        assert.equal(calls[1][2].data, formData);
        assert.equal(calls[1][2].method, uploadSize ? 'post' : undefined);
    });
}
