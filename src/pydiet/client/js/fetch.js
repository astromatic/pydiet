// Fetch HTML components
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under GPL v3

import {inject_html} from "./dom";


export async function fetch_data(url) {
	return await fetch(url, {credentials: "include"})
		.then( (response) => {
			// The API call was successful!
			if (!response.ok) {
				throw new Error("Unauthorized API endpoint:" + response.url);
			}
			return response.json();
		}).catch( (err) => {
			// There was an error
			return false;
		});
};


export async function fetch_html(selector, url, {method='get', data} = {}) {
	return await (method=='get' ?
		fetch(
			data ? url + '?' + new URLSearchParams(data) : url,
			{credentials: 'include'}
		) : fetch(url,
			{
				method: 'post',
				body: data,
				credentials: "include"})
	).then( (response) => {
			// The API call was successful!
			if (!response.ok) {
				throw new Error("Unauthorized API endpoint:" + response.url);
			}
			return response.text();
		}).then( (html) => {
			// Remove possible remaining modal
			// Insert the HTML string into the current element
			inject_html(selector, html);
			return true;
		}).catch( (err) => {
			// There was an error
			return false;
		});
};

