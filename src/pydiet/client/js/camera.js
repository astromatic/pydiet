// Manage camera settings
// Copyright CEA/CFHT/CNRS/UParisSaclay
// Licensed under MIT

export const	cameras = ["MegaCam", "WIRCam"];


// Get previously stored camera
export function get_camera() {
	return localStorage.getItem('pyDIETDefaultCamera');
}


// Update camera settings
export function update_camera(camera) {
	if (camera) {
		// Store new camera choice in local storage
		localStorage.setItem('pyDIETDefaultCamera', camera);
	} else {
		// Get previously stored camera
		camera = get_camera();
	}
}


