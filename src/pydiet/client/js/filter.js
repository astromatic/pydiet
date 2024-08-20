// Manage filter settings
// Copyright CEA/CFHT/CNRS/UParisSaclay
// Licensed under MIT

import {etc_url} from "./url";
import {fetch_data} from "./fetch";

export async function get_instruments() {
	return await fetch_data(etc_url + "/instruments");
}


// Get previously stored filter
export function get_filter() {
	filter =  localStorage.getItem('pyDIETDefaultFilter');
    return filter;
}


// Update filter settings
export function update_filter(filter) {
	if (filter) {
		// Store new filter choice in local storage
		localStorage.setItem('pyDIETDefaultFilter', filter);
	} else {
		// Get previously stored filter
		camera = get_filter();
	}
}


