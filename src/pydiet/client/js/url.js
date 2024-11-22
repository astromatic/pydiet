// Root URLs for APIs 
// Copyright CFHT/CNRS/IAP/SorbonneU
// Licensed under GPL v3

const root_path = document.querySelector('#root_path').content;

// Root URL
export const root_url = root_path,
	etc_url = root_url + "/etc",
// Root URL for UI components
	ui_url = root_url + "/ui",
	ui_auth_url = ui_url + "/auth";

