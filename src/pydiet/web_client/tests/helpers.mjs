import {readFile} from 'node:fs/promises';
import {createContext, SourceTextModule, SyntheticModule} from 'node:vm';

/**
 * Evaluate a fresh browser module with explicit globals and dependency doubles.
 * @param {string} filename - Filename relative to the client js directory.
 * @param {object} [globals={}] - Browser globals for this isolated context.
 * @param {object} [dependencies={}] - Exports keyed by import specifier.
 * @returns {Promise<object>} The evaluated module's exports.
 */
export async function loadModule(filename, globals = {}, dependencies = {}) {
    const url = new URL(`../js/${filename}`, import.meta.url);
    const context = createContext(globals);
    const module = new SourceTextModule(await readFile(url, 'utf8'), {
        context, identifier: url.href,
    });
    await module.link(specifier => {
        if (!Object.hasOwn(dependencies, specifier)) {
            throw new Error(`Missing test dependency: ${specifier}`);
        }
        const exports = dependencies[specifier];
        return new SyntheticModule(Object.keys(exports), function () {
            for (const [key, value] of Object.entries(exports)) this.setExport(key, value);
        }, {context});
    });
    await module.evaluate();
    return module.namespace;
}

/**
 * Create an independent localStorage double with browser string conversion.
 * @returns {object} Storage with getItem and setItem methods.
 */
export function storage() {
    const values = new Map();
    return {
        getItem: key => values.get(String(key)) ?? null,
        setItem: (key, value) => values.set(String(key), String(value)),
    };
}
