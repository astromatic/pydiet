// Manage web interface settings
// Copyright CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under GPL v3

import {get_camera} from "./camera";
import {fetch_html} from "./fetch";
import {etc_url} from "./url";

const etc_form = document.querySelector('#etc-form');
etc_form.addEventListener('submit', async function (e){
	// Prevent default behavior on submit
	e.preventDefault();
	const data = Object.fromEntries(new FormData(this));
	fetch_html(
		'#modal-slot',
		etc_url + '/' + get_camera() + '?' + new URLSearchParams(data)
	);
});

