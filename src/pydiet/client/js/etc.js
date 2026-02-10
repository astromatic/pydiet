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
			filters = instrument.transmissions;
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
		select_filters.addEventListener('ionChange', (event) => {
			const	filterID = event.detail.value;
            if (filterID == 'upload') return;
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



