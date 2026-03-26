// Manage instruments
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT

import { loadingController } from '@ionic/core';
import { etc_url } from "./url";
import {update_etcform} from "./etc";
import { fetch_data} from "./fetch";

let	instruments_cache = null;

export async function get_instruments() {
	if (!instruments_cache) {
		const	loading =  await loadingController.create({
			message: 'Loading instruments ...',
			duration: 10000
		});
		loading.present();
		instruments_cache = fetch_data(etc_url + "/instruments");
		loading.dismiss();
	}
	return instruments_cache;
}


// Get previously stored instrument
export function get_instrumentID() {
	return localStorage.getItem('pyDIETDefaultInstrument');
}


// Update stored instrument setting
export function update_instrument(instrumentID) {
	get_instruments().then( (instruments) => {
		instrument = instruments[instrumentID];
		update_etcform(instrument);
		// Store new instrument setting in local storage
		localStorage.setItem('pyDIETDefaultInstrument', instrumentID);
		return instrumentID;
	});
}


// Get previously stored filter
export function get_filterID(instrumentID) {
	return localStorage.getItem('pyDIETDefaultFilter_' + instrumentID);
}


// Update stored filter setting
export function update_filter(instrumentID, filterID) {
	if (filterID) {
		// Store new filter setting in local storage
		localStorage.setItem('pyDIETDefaultFilter_' + instrumentID, filterID);
		return filterID;
	} else {
		// Return previously stored filter
		return get_filterID(instrumentID);
	}
}


