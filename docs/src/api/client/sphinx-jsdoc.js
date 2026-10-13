/**
 * @file Adapt JSDoc links and wildcard types for Sphinx's reStructuredText renderer.
 * This plugin applies only to Sphinx builds; standalone JSDoc uses its own config.
 */

exports.handlers = {
    /**
     * Convert documented symbol links and wildcard types before Sphinx reads them.
     *
     * @param {object} event - JSDoc processing-complete event.
     * @param {object[]} event.doclets - Parsed documentation records.
     * @returns {void}
     */
    processingComplete(event) {
        const symbols = new Map();
        for (const doclet of event.doclets) {
            if (doclet.undocumented || !doclet.meta ||
                !['function', 'constant', 'member'].includes(doclet.kind)) {
                continue;
            }
            const module = doclet.meta.filename.replace(/\.js$/, ''),
                role = doclet.kind === 'function' ? 'func' : 'attr';
            // Ambiguous short names stay readable without creating a wrong link.
            symbols.set(doclet.longname, symbols.has(doclet.longname) ? null :
                `:js:${role}:\`${module}.${doclet.longname}\``);
        }
        function adapt(record) {
            if (!record || typeof record !== 'object') {
                return;
            }
            if (typeof record.description === 'string') {
                record.description = record.description.replace(
                    /\{@link\s+([^\s}]+)\}/g,
                    (match, name) => symbols.get(name) || `\`\`${name}\`\``
                );
            }
            if (record.type && Array.isArray(record.type.names)) {
                // A bare wildcard would become "*****", an invalid RST transition.
                record.type.names = record.type.names.map(name => name === '*' ? 'any' : name);
            }
            for (const value of Object.values(record)) {
                if (Array.isArray(value)) {
                    value.forEach(adapt);
                }
            }
        }
        event.doclets.forEach(adapt);
    },
};
