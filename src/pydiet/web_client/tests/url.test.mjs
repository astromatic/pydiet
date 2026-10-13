import assert from 'node:assert/strict';
import test from 'node:test';
import {loadModule} from './helpers.mjs';

for (const root of ['', '/calculator', 'https://example.test/calculator']) {
    test(`service URLs preserve the configured root ${JSON.stringify(root)}`, async () => {
        // Support both root hosting and installations behind a URL prefix.
        const api = await loadModule('url.js', {document: {querySelector: selector => {
            assert.equal(selector, '#root_path');
            return {content: root};
        }}});
        assert.equal(api.root_url, root);
        assert.equal(api.etc_url, `${root}/api`);
        assert.equal(api.ui_url, `${root}/ui`);
        assert.equal(api.ui_auth_url, `${root}/ui/auth`);
    });
}
