// Manage web interface settings
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under GPL v3
import {get_instrumentID, update_instrument} from "./instrument";
import {get_theme, update_theme, themes, theme_icons} from "./theme";

// Manage theme changes
export function setup_theme_settings() {
	if ((theme_segment = document.querySelector("#theme-segment"))) {
		for (t in themes) {
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
		theme_segment.value = theme = get_theme();
		update_theme(theme);
		theme_segment.addEventListener('ionChange', (event) => {
			update_theme(event.detail.value);
		});
	}
}

// Manage instrument changes
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

