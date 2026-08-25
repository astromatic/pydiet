/**
 * @file Fetch JSON data and HTML interface fragments.
 */
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT

import {inject_html} from "./dom";


/**
 * Fetch and decode JSON using the browser's current credentials.
 *
 * HTTP, network, and JSON-decoding errors are converted to `false`.
 *
 * @param {string|URL} url - Resource URL.
 * @returns {Promise<*|false>} Decoded JSON value, or `false` on failure.
 *
 * @example
 * const instruments = await fetch_data('/api/instruments');
 * if (instruments === false) console.error('Request failed');
 */
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


/**
 * Fetch an HTML fragment and inject it into an element.
 *
 * GET data is encoded as query parameters. Any method other than the literal
 * string `"get"` sends a POST request whose body is `data`. Request and
 * injection errors are converted to `false`.
 *
 * @param {string} selector - CSS selector passed to {@link inject_html}.
 * @param {string|URL} url - Resource URL.
 * @param {object} [options={}] - Request options.
 * @param {string} [options.method='get'] - Request method selector.
 * @param {*} [options.data] - Query values for GET or request body for POST.
 * @returns {Promise<boolean>} `true` after successful injection; otherwise `false`.
 *
 * @example
 * await fetch_html('#results', '/ui/demo/results', {
 *   data: {brightness: 20, snr: 10}
 * });
 */
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
