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

