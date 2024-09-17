// Manage web interface settings
// Copyright CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under GPL v3

import {get_camera} from "./camera";
import {fetch_data, fetch_html} from "./fetch";
import {etc_url} from "./url";

const etc_form = document.querySelector('#etc-form');
etc_form.addEventListener('submit', async function (e){
	// Prevent default behavior on submit
	e.preventDefault();
	const data = Object.fromEntries(new FormData(this)),
	    camera = get_camera()
	fetch_data(etc_url + '/' + camera + '?' + new URLSearchParams(data))
	fetch_html(
		'#modal-slot',
		etc_url + '/' + camera + '?' + new URLSearchParams(data)
	);
});

