// Manage web interface settings
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under GPL v3

import Chart from 'chart.js/auto';
import zoomPlugin from 'chartjs-plugin-zoom';

Chart.register(zoomPlugin);

export function plot_filter(filter, atmosphere, canvas) {
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
							min: 250.,
							max: 1050.

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

