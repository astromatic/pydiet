// Manage web interface settings
// Copyright CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under GPL v3

import {get_filterID, get_instrumentID, update_filter} from "./instrument";
import {fetch_data, fetch_html} from "./fetch";
import {etc_url, ui_url} from "./url";

const etc_form = document.querySelector('#etc-form');
etc_form.addEventListener('submit', async function (e){
	// Prevent default behavior on submit
	e.preventDefault();
	const data = Object.fromEntries(new FormData(this)),
	    instrumentID = get_instrumentID(),
		results = fetch_data(etc_url + '/' + instrumentID + '/data?'
			+ new URLSearchParams(data));
	fetch_html(
		'#modal-slot',
		ui_url + '/etc_results?' + new URLSearchParams(await results)
	);
});


export function update_filters(instrument) {
	if ((select_filters = document.querySelector("#select-filters"))) {
		while (select_filters.firstChild) {
			select_filters.lastChild.remove()
		}
		instrumentID = instrument.id;
		filters = instrument.filters;
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
		select_filters.value = f_default;
		update_filter(instrumentID, f_default);
		select_filters.addEventListener('ionChange', (event) => {
			update_filter(instrumentID, event.detail.value);
		});
	}
}
