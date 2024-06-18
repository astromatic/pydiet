// Manage web interface settings
// Copyright CEA/CFHT/CNRS/UParisSaclay
// Licensed under MIT

// Use matchMedia to check the user preference for dark/light themes
export const prefersdark = window.matchMedia('(prefers-color-scheme: dark)');

// Add or remove the "dark" class based on if the media query matches
export function toggle_dark_theme(isdark) {
	document.body.classList.toggle('dark', isdark);
}

