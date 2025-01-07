// Manage web interface settings
// Copyright 2024,2025 CFHT/CNRS/OSUPS/CEA/UParisSaclay
// Licensed under GPL v3

import Chart from 'chart.js/auto';
import zoomPlugin from 'chartjs-plugin-zoom';

Chart.register(zoomPlugin);

export function plot_filter(filter, canvas) {
	console.log(filter.response.response);
	const wave = filter.response.wave.value,
		response = filter.response.response.value,
		unit = filter.response.wave.unit,
		chart = new Chart(
			canvas,
			{
				type: 'line',
				data: {
					labels: wave.map((w) => Math.round(w)),
					datasets:	[{
						label: 'Filter response',
						data: response,
						fill: true
					}]
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
							title: {
								display: true,
								text: 'Wavelength [' + unit + ']'
							}
						},
						y: {
							title: {
								display: true,
								text: 'Tranmission [%]'
							}
						}
					},
					plugins: {
						title: {
							display: true,
							text: filter.id,
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




