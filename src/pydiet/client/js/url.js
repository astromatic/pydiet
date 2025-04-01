// Root URLs for APIs 
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under GPL v3

const root_path = document.querySelector('#root_path').content;


export const root_url = root_path,	// Root URL
	etc_url = root_url + "/etc",
	ui_url = root_url + "/ui",		// Root URL for UI components
	ui_auth_url = ui_url + "/auth";

