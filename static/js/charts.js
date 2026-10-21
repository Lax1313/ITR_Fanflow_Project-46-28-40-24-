/*
 * FanFlow chart color helper.
 *
 * Reads the current theme's colors straight from CSS variables so every
 * chart automatically matches Light or Dark mode with no duplicated
 * hex codes anywhere. Charts are re-created (not just recolored) when
 * the theme toggles, since Chart.js doesn't live-update colors otherwise.
 */

function fanflowChartColors() {
    var style = getComputedStyle(document.documentElement);
    var get = function (name) { return style.getPropertyValue(name).trim(); };
    return {
        palette: [
            get('--chart-1'), get('--chart-2'), get('--chart-3'), get('--chart-4'),
            get('--chart-5'), get('--chart-6'), get('--chart-7'), get('--chart-8'),
        ],
        accent: get('--accent'),
        success: get('--success'),
        danger: get('--danger'),
        warning: get('--warning'),
        info: get('--info'),
        text: get('--text-primary'),
        grid: get('--border-color'),
    };
}

/*
 * Registers a chart-builder function to run now, and again every time the
 * theme is toggled (destroying the old chart instance first so colors
 * actually refresh). `key` must be unique per canvas on the page.
 */
var _fanflowCharts = {};

function fanflowRegisterChart(key, buildFn) {
    if (_fanflowCharts[key]) {
        _fanflowCharts[key].destroy();
    }
    _fanflowCharts[key] = buildFn(fanflowChartColors());
}

document.addEventListener('fanflow-theme-changed', function () {
    Object.keys(window.fanflowChartBuilders || {}).forEach(function (key) {
        fanflowRegisterChart(key, window.fanflowChartBuilders[key]);
    });
});
