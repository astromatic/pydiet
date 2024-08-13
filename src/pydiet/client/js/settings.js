// Manage web interface settings
// Copyright CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under GPL v3
import {cameras, get_camera, update_camera} from "./camera";
import {get_theme, update_theme, themes, theme_icons} from "./theme";

// Manage theme changes
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
	theme_segment.value = get_theme();
	theme_segment.addEventListener('ionChange', (event) => {
		update_theme(event.detail.value);
	});
}

// Manage camera changes
if ((camera_segment = document.querySelector("#camera-segment"))) {
	for (c in cameras) {
		let	button = document.createElement("ion-segment-button"),
			icon = document.createElement("ion-icon"),
			label = document.createElement("ion-label");
		button.value = cameras[c].toLowerCase();
		label.innerHTML = cameras[c];
		button.appendChild(label);
		icon.name = "videocam";
		button.appendChild(icon);
		camera_segment.appendChild(button);
	}
	camera_segment.value = get_camera();
	camera_segment.addEventListener('ionChange', (event) => {
		update_camera(event.detail.value);
	});
}
