import assert from 'node:assert/strict';
import test from 'node:test';
import {loadModule} from './helpers.mjs';

function target() {
    return {
        innerHTML: 'old content', appended: null,
        firstElementChild: {remove() {}},
        appendChild(node) { this.appended = node; },
        insertAdjacentHTML(position, html) {
            assert.equal(position, 'beforeend');
            this.innerHTML += html;
        },
        querySelectorAll: () => [],
    };
}

test('node injection replaces content, returns the node, and can clear it', async () => {
    // Replacement works in module scope and does not overwrite window.parent.
    const element = target(), node = {textContent: 'Ready'}, frameParent = {};
    const globals = {document: {querySelector: () => element}, parent: frameParent};
    const api = await loadModule('dom.js', globals);
    assert.equal(api.inject_node('#message', node), node);
    assert.equal(element.innerHTML, '');
    assert.equal(element.appended, node);
    assert.equal(globals.parent, frameParent);
    element.appended = null;
    assert.equal(api.inject_node('#message', null), null);
    assert.equal(element.appended, null);
});

test('HTML injection replaces content and recreates inline and external scripts', async () => {
    // Copy security/type attributes and preserve script source or inline text.
    const element = target(), replacements = [], created = [];
    element.querySelectorAll = selector => {
        assert.equal(selector, 'script');
        return [
            {attributes: [{name: 'nonce', value: 'demo'}], src: '', textContent: 'render()', replaceWith: node => replacements.push(node)},
            {attributes: [{name: 'type', value: 'module'}], src: '/plot.js', replaceWith: node => replacements.push(node)},
        ];
    };
    const api = await loadModule('dom.js', {document: {
        querySelector: () => element,
        createElement: tag => {
            assert.equal(tag, 'script');
            const node = {attributes: {}, setAttribute(name, value) { this.attributes[name] = value; }};
            created.push(node);
            return node;
        },
    }});
    api.inject_html('#message', '<p>Ready</p>');
    assert.equal(element.innerHTML, '<p>Ready</p>');
    assert.deepEqual(replacements, created);
    assert.equal(replacements[0].textContent, 'render()');
    assert.equal(replacements[0].attributes.nonce, 'demo');
    assert.equal(replacements[1].src, '/plot.js');
    assert.equal(replacements[1].attributes.type, 'module');
});

test('DOM helpers reject absent targets', async () => {
    // Missing template slots surface the documented TypeError.
    const api = await loadModule('dom.js', {document: {querySelector: () => null}});
    assert.throws(() => api.inject_node('#missing', {}), {name: 'TypeError'});
    assert.throws(() => api.inject_html('#missing', ''), {name: 'TypeError'});
});

test('DOM helpers insert into an empty target', async () => {
    // Empty template slots need no existing child to be removed.
    const element = target();
    element.firstElementChild = null;
    element.innerHTML = '';
    const api = await loadModule('dom.js', {document: {querySelector: () => element}});
    api.inject_html('#message', '<p>Ready</p>');
    assert.equal(element.innerHTML, '<p>Ready</p>');
    const node = {textContent: 'Ready'};
    assert.equal(api.inject_node('#message', node), node);
    assert.equal(element.appended, node);
});
