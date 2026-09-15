/**
 * @file DOM content replacement helpers.
 */
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT

/**
 * Replace an element's contents with HTML and execute inserted scripts.
 *
 * Existing contents are removed before insertion. Script elements are replaced
 * with newly created elements so that both inline and external scripts run.
 *
 * @param {string} selector - CSS selector for the target element.
 * @param {string} html - HTML markup to insert.
 * @returns {void}
 * @throws {TypeError} If the selector does not match an element.
 *
 * @example
 * inject_html('#message', '<strong>Ready</strong>');
 */
export function inject_html(selector, html) {
	parent = document.querySelector(selector)
	if (parent.firstElementChild) {
		parent.firstElementChild.remove();
		parent.innerHTML = "";
	}
	parent.insertAdjacentHTML("beforeend", html);

	// Now find scripts inside what was inserted and re-insert them
	const scripts = parent.querySelectorAll('script');
	scripts.forEach(oldScript => {
		// Only re-run scripts that came from our insertion:
		// (If needed, scope this by inserting into a wrapper element and querying inside it.)
		const newScript = document.createElement('script');

		// Copy attributes (type, src, nonce, etc.)
		for (const { name, value } of oldScript.attributes) {
			newScript.setAttribute(name, value);
		}

		if (oldScript.src) {
			// External script
			newScript.src = oldScript.src;
			// Optional: preserve async/defer behavior if you set it
		} else {
			// Inline script
			newScript.textContent = oldScript.textContent;
		}

		oldScript.replaceWith(newScript);
	});
}


/**
 * Replace an element's contents with a DOM node.
 *
 * Passing a falsy node clears the target without appending a replacement.
 *
 * @param {string} selector - CSS selector for the target element.
 * @param {?Node} node - Node to append, or a falsy value to only clear the target.
 * @returns {?Node} The supplied node.
 * @throws {TypeError} If the selector does not match an element.
 *
 * @example
 * const status = document.createElement('span');
 * status.textContent = 'Ready';
 * inject_node('#message', status);
 */
export function inject_node(selector, node) {
	parent = document.querySelector(selector)
	if (parent.firstElementChild) {
		parent.firstElementChild.remove();
		parent.innerHTML = "";
	}
	if (node) {
		parent.appendChild(node);
	}
	return node;
}
