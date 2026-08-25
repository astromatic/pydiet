/**
 * @file Populate theme and instrument setting controls.
 */
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT
import {get_instrumentID, update_instrument} from "./instrument";
import {get_theme, update_theme, themes, theme_icons} from "./theme";

/**
 * Populate and activate the theme selector when present.
 *
 * Three Ionic segment buttons are appended to `#theme-segment`. The persisted
 * theme is applied immediately and later `ionChange` events update it.
 *
 * @returns {void}
 *
 * @example
 * // HTML: <ion-segment id="theme-segment"></ion-segment>
 * setup_theme_settings();
 */
export function setup_theme_settings() {
	const theme_segment = document.querySelector("#theme-segment");
	if ((theme_segment)) {
		for (var t in themes) {
			let	button = document.createElement("ion-segment-button"),
				icon = document.createElement("ion-icon"),
				label = document.createElement("ion-label");
			button.value = themes[t].toLowerCase();
			label.innerHTML = themes[t];
			button.appendChild(label);
			icon.name = theme_icons[t];
			button.appendChild(icon);
			theme_segment.appendChild(button);
		}
		const theme = theme_segment.value = get_theme();
		update_theme(theme);
		theme_segment.addEventListener('ionChange', (event) => {
			update_theme(event.detail.value);
		});
	}
}

/**
 * Populate and activate the instrument selector when present.
 *
 * The persisted instrument is selected when available. Otherwise the API's
 * default instrument, or ultimately an instrument encountered during
 * iteration, is selected. Selection changes rebuild the ETC form.
 *
 * @param {object<string, object>} instruments - Instruments keyed by identifier.
 * @returns {void}
 *
 * @example
 * setup_instrument_settings({
 *   demo: {name: 'Demo camera', default: true}
 * });
 */
export function setup_instrument_settings(instruments) {
	if ((instrument_segment = document.querySelector("#instrument-segment"))) {
		let i_default = get_instrumentID();
		for (i in instruments) {
			let button = document.createElement("ion-segment-button"),
				icon = document.createElement("ion-icon"),
				label = document.createElement("ion-label");
			button.value = i;
			instrument = instruments[i]
			label.innerHTML = instrument.name;
			button.appendChild(label);
			icon.name = "videocam";
			button.appendChild(icon);
			instrument_segment.appendChild(button);
			// Identify default instrument (or first in the dictionary instead)
			if (!i_default && (instrument.default || !i_default)) {
				i_default = i;
			}
		}
		instrument_segment.value = i_default;
		update_instrument(i_default);
		instrument_segment.addEventListener('ionChange', (event) => {
			update_instrument(event.detail.value);
		});
	}
}
