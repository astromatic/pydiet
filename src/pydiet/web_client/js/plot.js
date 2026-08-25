/**
 * @file Plot instrument and atmospheric transmission curves.
 */
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under MIT

import Chart from 'chart.js/auto';
import zoomPlugin from 'chartjs-plugin-zoom';

Chart.register(zoomPlugin);

/**
 * Create an interactive transmission chart.
 *
 * The initial wavelength limits come from `filter.wave_range`; `wave_min` and
 * `wave_max` are currently accepted but ignored. Chart.js zooming and panning
 * are enabled, including shift-drag zoom.
 *
 * @param {object} filter - Instrument transmission model.
 * @param {string} filter.name - Filter display name.
 * @param {{value: number[], unit: string}} filter.wave - Wavelength samples.
 * @param {{value: number[]}} filter.response - Transmission samples.
 * @param {{value: number[]}} filter.wave_range - Initial wavelength limits.
 * @param {object} atmosphere - Atmospheric transmission model.
 * @param {{value: number[]}} atmosphere.wave - Wavelength samples.
 * @param {{value: number[]}} atmosphere.response - Transmission samples.
 * @param {HTMLCanvasElement|string} canvas - Canvas or canvas ID accepted by Chart.js.
 * @param {number} [wave_min] - Currently unused requested lower wavelength.
 * @param {number} [wave_max] - Currently unused requested upper wavelength.
 * @returns {void}
 *
 * @example
 * plot_filter(
 *   {
 *     name: 'g',
 *     wave: {value: [400, 500], unit: 'nm'},
 *     response: {value: [0.2, 0.8]},
 *     wave_range: {value: [400, 500]}
 *   },
 *   {wave: {value: [400, 500]}, response: {value: [0.9, 0.95]}},
 *   'transmission-chart'
 * );
 */
export function plot_filter(filter, atmosphere, canvas, wave_min, wave_max) {
	const fwave = filter.wave.value,
		fresponse = filter.response.value,
		awave = atmosphere.wave.value,
		aresponse = atmosphere.response.value,
		unit = filter.wave.unit,
		chart = new Chart(
			canvas,
			{
				type: 'line',
				data: {
					datasets:	[
						{
							label: 'Atmosphere',
							data: awave.map((x, i) => ({ x, y: aresponse[i] })),
							fill: true
						},
						{
							label: 'Instrument',
							data: fwave.map((x, i) => ({ x, y: fresponse[i] })),
							fill: true
						}
					]
				},
				options: {
					pointRadius: 0,
					maintainAspectRatio: false,
					interaction: {
						mode: 'nearest',
						intersect: true
					},
					scales: {
						x: {
							type: 'linear',
							title: {
								display: true,
								text: 'Wavelength [' + unit + ']'
							},
							min: filter.wave_range.value[0],
							max: filter.wave_range.value[1]

						},
						y: {
							title: {
								display: true,
								text: 'Transmission',
							},
							min: 0.,
							max: 1.
						}
					},
					plugins: {
						title: {
							display: false,
							text: filter.name + ' filter',
						},
						legend: {display: false},
						zoom: {
							zoom: {
								wheel: {enabled: true},
								pinch: {enabled: true},
								drag: {enabled: true, modifierKey: 'shift'},
								scaleMode: 'xy',
								mode: 'xy'},
							pan: {enabled: true, scaleMode: 'xy'},
							limits: {
								x: {min: 'original', max: 'original'},
								y: {min: 'original', max: 'original'}
							}
						}
					}
				}
			}
		);
};


window.plot_filter = plot_filter;
