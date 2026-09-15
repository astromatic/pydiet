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
 * The persisted instrument is selected if its ID is in `instruments`.
 * Otherwise the first API default, or ultimately the first instrument, is
 * selected. An empty instrument dictionary leaves the selector inactive.
 * Selection changes rebuild the ETC form.
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
	const instrument_segment = document.querySelector("#instrument-segment");
	if (instrument_segment) {
		const ids = Object.keys(instruments);
		if (!ids.length) {
			return;
		}
		const stored_id = get_instrumentID();
		const i_default = ids.includes(stored_id) ? stored_id :
			(ids.find(id => instruments[id].default) ?? ids[0]);
		for (const i of ids) {
			let button = document.createElement("ion-segment-button"),
				icon = document.createElement("ion-icon"),
				label = document.createElement("ion-label");
			button.value = i;
			const instrument = instruments[i];
			label.innerHTML = instrument.name;
			button.appendChild(label);
			icon.name = "videocam";
			button.appendChild(icon);
			instrument_segment.appendChild(button);
		}
		instrument_segment.value = i_default;
		update_instrument(i_default);
		instrument_segment.addEventListener('ionChange', (event) => {
			update_instrument(event.detail.value);
		});
	}
}
