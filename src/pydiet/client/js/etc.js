// Manage web interface settings
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under GPL v3

import {inject_node} from "./dom";
import {fetch_data, fetch_html} from "./fetch";
import {get_filterID, update_filter} from "./instrument";
import {plot_filter} from "./plot";
import {etc_url, ui_url} from "./url";

export async function update_etcform(instrument) {
	fetch_html(
		"#content-slot",
		ui_url + "/" + instrument.id + "/etc_form"
	).then( (result) => { 
		const etc_form = document.querySelector('#etc-form');
		update_snr_etime();
		update_filters(instrument);
		etc_form.addEventListener('submit', async function (e){
			// Prevent default behavior on submit
			e.preventDefault();
			const data = Object.fromEntries(new FormData(this));
			fetch_html(
				'#modal-slot',
				ui_url + '/' + instrument.id + '/etc_results/query?'
					+ new URLSearchParams(data)
			);
		});
	});
}

function update_snr_etime() {
	if ((select_compute = document.querySelector('#select-compute'))) {
		select_compute.addEventListener('ionChange', (event) => {    
			const input = document.querySelector('#input-snr-etime'),
				ctype = event.detail.value;
			if (ctype == 'snr' && input.name == 'snr') {
				input.name = 'etime';
				input.label = "Exposure Time (s)"
			} else if (ctype == 'etime' && input.name == 'etime') {
				input.name = 'snr';
				input.label = "SNR"
			}
		});
	}
}

function update_filters(instrument) {
	if ((select_filters = document.querySelector("#select-filters"))) {
		while (select_filters.firstChild) {
			select_filters.lastChild.remove()
		}
		const	instrumentID = instrument.id,
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
			const	filterID = event.detail.value;
			update_filter(instrumentID, filterID);
			fetch_html(
				'#modal-slot',
				ui_url + '/common/plot_filter'
			).then( (result) => {
				plot_filter(
					filters[filterID],
					document.getElementById('filter-canvas').getContext('2d')
				);
			});
		});
	}
}



