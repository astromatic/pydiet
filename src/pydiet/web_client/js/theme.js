/**
 * @file Persist and apply light, dark, and automatic themes.
 */
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT

/**
 * Display names of the supported themes.
 * @type {string[]}
 */
export const	themes = ["Light", "Dark", "Auto"],
	/**
	 * Ionic icon names corresponding to {@link themes}.
	 * @type {string[]}
	 */
	theme_icons = ["sunny", "moon", "contrast"];


// Use matchMedia to check the user preference for dark/light themes
const prefersdark = window.matchMedia('(prefers-color-scheme: dark)');

// Add or remove the "dark" class based on if the media query matches
function toggle_dark_theme(isdark) {
	document.body.classList.toggle('dark', isdark);
}


/**
 * Return the persisted theme selection.
 *
 * @returns {?string} Stored lower-case theme name, or `null` when unset.
 *
 * @example
 * localStorage.setItem('pyDIETDefaultTheme', 'dark');
 * get_theme(); // 'dark'
 */
export function get_theme() {
	return localStorage.getItem('pyDIETDefaultTheme');
}


/**
 * Persist and apply a theme selection.
 *
 * Names containing `"dark"` enable dark mode; names containing `"light"`
 * disable it. Other, missing, or non-string values follow the operating-system
 * preference. A truthy value is stored before application.
 *
 * @param {?string} theme - Theme selection, or a falsy value to reuse storage.
 * @returns {void}
 *
 * @example
 * update_theme('dark');
 * document.body.classList.contains('dark'); // true
 */
export function update_theme(theme) {
	if (theme) {
		// Store new theme choice in local storage
		localStorage.setItem('pyDIETDefaultTheme', theme);
	} else {
		// Get previously stored theme
		theme = get_theme();
	}
	// Toggle theme if necessary
	toggle_dark_theme(
		(typeof(theme) === "string" && theme.includes("dark"))
		|| (
			!(typeof(theme) === "string" && theme.includes("light"))
			&& prefersdark.matches
		)
	);
}
