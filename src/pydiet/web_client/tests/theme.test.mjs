import assert from 'node:assert/strict';
import test from 'node:test';
import {loadModule, storage} from './helpers.mjs';

for (const prefersDark of [false, true]) {
    test(`theme selection respects explicit choices and system preference ${prefersDark}`, async () => {
        // Persist manual choices and reuse storage when no new choice is supplied.
        const localStorage = storage();
        let dark;
        const api = await loadModule('theme.js', {
            localStorage,
            window: {matchMedia: query => {
                assert.equal(query, '(prefers-color-scheme: dark)');
                return {matches: prefersDark};
            }},
            document: {body: {classList: {toggle: (name, value) => {
                assert.equal(name, 'dark');
                dark = value;
            }}}},
        });
        assert.equal(api.get_theme(), null);
        api.update_theme();
        assert.equal(dark, prefersDark);
        for (const [theme, expected] of [['dark', true], ['light', false], ['auto', prefersDark], ['unknown', prefersDark]]) {
            api.update_theme(theme);
            assert.equal(dark, expected);
            assert.equal(api.get_theme(), theme);
            api.update_theme();
            assert.equal(dark, expected);
        }
    });
}
