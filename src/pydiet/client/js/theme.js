// Manage web interface settings
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT

export const	themes = ["Light", "Dark", "Auto"],
	theme_icons = ["sunny", "moon", "contrast"];


// Use matchMedia to check the user preference for dark/light themes
const prefersdark = window.matchMedia('(prefers-color-scheme: dark)');

// Add or remove the "dark" class based on if the media query matches
function toggle_dark_theme(isdark) {
	document.body.classList.toggle('dark', isdark);
}


// Get previously stored theme
export function get_theme() {
	return localStorage.getItem('pyDIETDefaultTheme');
}


// Add or remove the "dark" class based on if the media query matches
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


