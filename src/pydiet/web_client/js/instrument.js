/**
 * @file Load instruments and persist instrument/filter selections.
 */
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT

import { loadingController } from '@ionic/core';
import { etc_url } from "./url";
import {update_etcform} from "./etc";
import { fetch_data} from "./fetch";

let	instruments_cache = null;

/**
 * Load the available instruments, caching the request promise.
 *
 * The first call briefly presents an Ionic loading indicator and requests the
 * `/api/instruments` endpoint. Later calls reuse the same promise, including a
 * promise that resolved to `false` after a failed request.
 *
 * @returns {Promise<object|false>} Instrument mapping, or `false` on failure.
 *
 * @example
 * const instruments = await get_instruments();
 * if (instruments) console.log(Object.keys(instruments));
 */
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


/**
 * Return the persisted default instrument identifier.
 *
 * @returns {?string} Stored identifier, or `null` when no choice exists.
 *
 * @example
 * localStorage.setItem('pyDIETDefaultInstrument', 'megacam');
 * get_instrumentID(); // 'megacam'
 */
export function get_instrumentID() {
	return localStorage.getItem('pyDIETDefaultInstrument');
}


/**
 * Select an instrument and asynchronously rebuild the ETC form.
 *
 * The selection is persisted after the cached instrument request resolves.
 * This function does not return the asynchronous operation.
 *
 * @param {string} instrumentID - Key in the instrument mapping.
 * @returns {void}
 */
export function update_instrument(instrumentID) {
	get_instruments().then( (instruments) => {
		instrument = instruments[instrumentID];
		update_etcform(instrument);
		// Store new instrument setting in local storage
		localStorage.setItem('pyDIETDefaultInstrument', instrumentID);
		return instrumentID;
	});
}


/**
 * Return the persisted filter identifier for an instrument.
 *
 * @param {string} instrumentID - Instrument identifier.
 * @returns {?string} Stored filter identifier, or `null` if none exists.
 *
 * @example
 * localStorage.setItem('pyDIETDefaultFilter_megacam', 'g');
 * get_filterID('megacam'); // 'g'
 */
export function get_filterID(instrumentID) {
	return localStorage.getItem('pyDIETDefaultFilter_' + instrumentID);
}


/**
 * Store or retrieve the selected filter for an instrument.
 *
 * A truthy `filterID` is persisted and returned. A falsy value leaves storage
 * unchanged and returns the previously stored identifier.
 *
 * @param {string} instrumentID - Instrument identifier.
 * @param {?string} filterID - Filter identifier to store.
 * @returns {?string} New or previously stored filter identifier.
 *
 * @example
 * update_filter('megacam', 'g'); // 'g'
 * update_filter('megacam'); // 'g'
 */
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

