/**
 * @file Derive API and UI URLs from the page's configured root path.
 */
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT

const root_path = document.querySelector('#root_path').content;


/**
 * Application root URL from `#root_path` metadata.
 * @type {string}
 */
export const root_url = root_path,
	/**
	 * Exposure-time calculator API root URL.
	 * @type {string}
	 */
	etc_url = root_url + "/api",
	/**
	 * Root URL for UI components.
	 * @type {string}
	 */
	ui_url = root_url + "/ui",
	/**
	 * Root URL for UI authentication components.
	 * @type {string}
	 */
	ui_auth_url = ui_url + "/auth";
