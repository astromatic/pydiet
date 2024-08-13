// Fetch HTML components
// Copyright CFHT/CNRS/IAP/SorbonneU
// Licensed under GPL v3

export async function fetch_html(selector, url) {
	return await fetch(url, {credentials: "include"})
		.then( (response) => {
			// The API call was successful!
			if (!response.ok) {
				throw new Error("Unauthorized API endpoint:" + response.url);
			}
			return response.text();
		}).then( (html) => {
			// Remove possible remaining modal
			// Insert the HTML string into the current element
			parent = document.querySelector(selector)
			if (parent.firstElementChild) {
				parent.firstElementChild.remove();
			}
			parent.insertAdjacentHTML("beforeend", html);
			return true;
		}).catch( (err) => {
			// There was an error
			return false;
		});
};

