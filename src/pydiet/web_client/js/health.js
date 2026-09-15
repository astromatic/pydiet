/**
 * @file Periodically reflect API health in the web interface.
 */
// Copyright 2026 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT
import {etc_url} from "./url";

const	health_url = etc_url + "/health",
	health_interval = 10_000,	// in ms
	health_timeout = 2_000,	// in ms
	health_element = document.getElementById("health-monitor");


function set_status(status, title) {
	health_element.classList.toggle("ok", status);
	health_element.classList.toggle("fail", !status);
	health_element.title = title;
}

async function check_health() {

	const	controller = new AbortController(),
		timeout_id = setTimeout(() => controller.abort(), health_timeout);

	try {
		const response = await fetch(health_url, {
			method: 'get',
			cache: 'no-store',
			signal: controller.signal,
			headers: {'accept': 'application/json'}
		});

		if (!response.ok) {
			set_status(false, `Status failed: HTTP ${response.status}`);
			return;
		}

		const data = await response.json();
		if (data.ok === true) {
			set_status(true, "Server OK");
		} else {
			set_status(false, "Server failed");
		}
	} catch (error) {
		set_status(false, "Server down or unreachable");
	} finally {
		clearTimeout(timeout_id);
	}
}

/**
 * Start API health monitoring.
 *
 * A check runs immediately and then every ten seconds. Each request is aborted
 * after two seconds. The element with ID `health-monitor` receives either the
 * `ok` or `fail` class and a corresponding title.
 *
 * @returns {void}
 * @throws {TypeError} If the health-monitor element is absent when status is set.
 *
 * @example
 * // HTML: <span id="health-monitor"></span>
 * setup_health();
 */
export function setup_health() {

	check_health();
	setInterval(check_health, health_interval);
}
