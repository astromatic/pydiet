import assert from 'node:assert/strict';
import test from 'node:test';
import {loadModule} from './helpers.mjs';

test('transmission charts pair independent wavelength grids and retain physical axes', async () => {
    // Check the application data sent to Chart.js without testing Chart.js rendering.
    const charts = [], plugins = [], window = {}, plugin = {};
    class Chart {
        static register(value) { plugins.push(value); }
        constructor(canvas, config) { charts.push({canvas, config}); }
    }
    const api = await loadModule('plot.js', {window}, {
        'chart.js/auto': {default: Chart},
        'chartjs-plugin-zoom': {default: plugin},
    });
    const filter = {
        name: 'g', wave: {value: [400, 500], unit: 'nm'},
        response: {value: [0.2, 0.8]}, wave_range: {value: [390, 510]},
    };
    const atmosphere = {wave: {value: [410, 450, 490]}, response: {value: [0.9, 0.95, 0.8]}};
    api.plot_filter(filter, atmosphere, 'transmission-chart');
    assert.deepEqual(plugins, [plugin]);
    assert.equal(window.plot_filter, api.plot_filter);
    assert.equal(charts[0].canvas, 'transmission-chart');
    const {data, options} = charts[0].config;
    assert.equal(charts[0].config.type, 'line');
    assert.deepEqual(JSON.parse(JSON.stringify(data.datasets.map(dataset => dataset.data))), [
        [{x: 410, y: 0.9}, {x: 450, y: 0.95}, {x: 490, y: 0.8}],
        [{x: 400, y: 0.2}, {x: 500, y: 0.8}],
    ]);
    assert.deepEqual(Array.from(data.datasets, dataset => dataset.label), ['Atmosphere', 'Instrument']);
    assert.equal(options.scales.x.title.text, 'Wavelength [nm]');
    assert.equal(options.scales.x.min, 390);
    assert.equal(options.scales.x.max, 510);
    assert.equal(options.scales.y.min, 0);
    assert.equal(options.scales.y.max, 1);
});
