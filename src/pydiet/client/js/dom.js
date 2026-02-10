// DOM manipulation routines
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under GPL v3

// Inject HTML in the selected node.
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

