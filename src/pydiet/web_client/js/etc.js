/**
 * @file Build and submit the exposure-time calculator form.
 */
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT

import {inject_node} from "./dom";
import {fetch_data, fetch_html} from "./fetch";
import {get_filterID, update_filter} from "./instrument";
import {plot_filter} from "./plot";
import {etc_url, ui_url} from "./url";

/**
 * Replace the current ETC form for an instrument and attach submission logic.
 *
 * The form fragment is loaded asynchronously. After insertion, filter options
 * are populated and form submission loads results into `#modal-slot`. A filter
 * upload switches the results request from GET query parameters to POST form
 * data.
 *
 * @param {object} instrument - Instrument returned by the instruments API.
 * @param {string} instrument.id - Instrument identifier used in UI URLs.
 * @param {object} instrument.filters - Instrument filter configuration.
 * @returns {Promise<void>} Resolves before the fragment request necessarily completes.
 *
 * @example
 * await update_etcform({
 *   id: 'demo',
 *   filters: {transmissions: {g: {name: 'g', default: true}}}
 * });
 */
export async function update_etcform(instrument) {
	fetch_html(
		"#content-slot",
		ui_url + "/" + instrument.id + "/etc_form"
	).then( (result) => { 
		const etc_form = document.querySelector('#etc-form');
		update_filters(instrument);
		etc_form.addEventListener('submit', async function (e){
			// Prevent default behavior on submit
			e.preventDefault();
			const data = new FormData(this),
				datao = Object.fromEntries(data),
				upload = (datao.filter_upload && datao.filter_upload.size > 0);
			fetch_html(
				'#modal-slot',
				ui_url + '/' + instrument.id + '/etc_results/query',
				upload ? {method: 'post', data: data} : {data: data}
			);
		});
	});
}


function update_filters(instrument) {
	if ((select_filters = document.querySelector("#select-filters"))) {
		while (select_filters.firstChild) {
			select_filters.lastChild.remove()
		}
		const	instrumentID = instrument.id,
			filters = instrument.filters.transmissions;
		let f_default = get_filterID(instrumentID);
		for (f in filters) {
			let  option = document.createElement("ion-select-option");
			option.value = f;
			filter = filters[f]
			option.innerHTML = filter.name;
			select_filters.appendChild(option);
			// Identify default instrument (or first in the dictionary instead)
			if (!f_default && (filter.default || !f_default)) {
				f_default = f;
			}
		}
		option = document.createElement("ion-select-option");
		option.value = 'upload';
		option.innerHTML = "upload";
	    select_filters.appendChild(option);       
		select_filters.value = f_default;
		update_filter(instrumentID, f_default);
	}
}


