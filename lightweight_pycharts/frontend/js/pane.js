import { indicator } from "./indicator.js";
import { createChart } from "./lib/pkg.js";
import { primitives } from "./lwpc-plugins/primitives.js";
import { TrendLine } from "./lwpc-plugins/trend-line/trend-line.js";
import * as u from "./util.js";
export class Pane {
    constructor(id, div, flex_width = 1, flex_height = 1, chart_opts = u.DEFAULT_PYCHART_OPTS) {
        this.id = '';
        this.indicators = new Map();
        this.primitives_left = new Map();
        this.primitives_right = new Map();
        this.primitives_overlay = new Map();
        this.id = id;
        this.div = div;
        this.flex_width = flex_width;
        this.flex_height = flex_height;
        this.chart = createChart(this.div, chart_opts);
        this.chart_div = this.chart.chartElement();
        this.whitespace_series = this.chart.addLineSeries();
        this.primitive_left = this.chart.addLineSeries({ priceScaleId: 'left', visible: false, autoscaleInfoProvider: undefined });
        this.primitive_right = this.chart.addLineSeries({ priceScaleId: 'right', visible: false, autoscaleInfoProvider: undefined });
        this.primitive_overlay = this.chart.addLineSeries({
            visible: false,
            priceScaleId: '',
            autoscaleInfoProvider: () => ({
                priceRange: {
                    minValue: 0,
                    maxValue: 100,
                },
            })
        });
        this.assign_active_pane = this.assign_active_pane.bind(this);
        this.chart_div.addEventListener('mousedown', () => {
            this.assign_active_pane();
            this.chart.timeScale().applyOptions({
                'shiftVisibleRangeOnNewBar': false,
                'allowShiftVisibleRangeOnWhitespaceReplacement': false,
                'rightBarStaysOnScroll': false
            });
        });
        window.document.addEventListener('mouseup', () => {
            this.chart.timeScale().applyOptions({
                'shiftVisibleRangeOnNewBar': true,
                'allowShiftVisibleRangeOnWhitespaceReplacement': true,
                'rightBarStaysOnScroll': true
            });
        });
    }
    assign_active_pane() {
        if (window.active_pane)
            window.active_pane.div.removeAttribute('active');
        window.active_pane = this;
        window.active_pane.div.setAttribute('active', '');
    }
    set_whitespace_data(data, primitive_data) {
        this.whitespace_series.setData(data);
        this.primitive_left.setData([primitive_data]);
        this.primitive_right.setData([primitive_data]);
        this.primitive_overlay.setData([primitive_data]);
    }
    update_whitespace_data(data, primitive_data) {
        this.whitespace_series.update(data);
        this.primitive_left.setData([primitive_data]);
        this.primitive_right.setData([primitive_data]);
        this.primitive_overlay.setData([primitive_data]);
    }
    add_indicator(_id, type) {
        this.indicators.set(_id, new indicator(_id, type, this));
    }
    remove_indicator(_id) {
        let indicator = this.indicators.get(_id);
        if (indicator === undefined)
            return;
        indicator.delete();
        this.indicators.delete(_id);
    }
    add_primitive(_id, _type, params) {
        let primitive_type = primitives.get(_type);
        if (primitive_type === undefined)
            return;
        let new_obj = new primitive_type(params);
        this.primitives_right.set(_id, new_obj);
        this.primitive_right.attachPrimitive(new_obj);
    }
    remove_primitive(_id) {
        let _obj = this.primitives_right.get(_id);
        if (_obj === undefined)
            return;
        this.primitive_right.detachPrimitive(_obj);
        this.primitives_right.delete(_id);
    }
    update_primitive(_id, params) {
        let _obj = this.primitives_right.get(_id);
        if (_obj === undefined)
            return;
        _obj.updateData(params);
    }
    resize(width, height) {
        let this_width = width * this.flex_width;
        let this_height = height * this.flex_height;
        this.div.style.width = `${this_width}px`;
        this.div.style.height = `${this_height}px`;
        this.chart.resize(this_width, this_height, false);
    }
    create_line(point1, point2) {
        const trend = new TrendLine({ p1: point1, p2: point2 });
        this.primitive_right.attachPrimitive(trend);
    }
    fitcontent() { this.chart.timeScale().fitContent(); }
    autoscale_time_axis() { this.chart.timeScale().resetTimeScale(); }
    update_timescale_opts(newOpts) { this.chart.timeScale().applyOptions(newOpts); }
}
Pane._special_id_ = 'main';
