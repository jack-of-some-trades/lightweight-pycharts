import { Legend } from "./legend.js";
import { AnySeries, AnySeriesData, CandlestickData, CandlestickSeriesOptions, DeepPartial as DP, DeepPartial, HorzScaleOptions, IChartApi, TimeChartOptions, createChart } from "./lib/pkg.js";
import { TrendLine } from "./lwpc-plugins/trend-line/trend-line.js";
import { RoundedCandleSeries } from "./plugins/rounded-candles-series/rounded-candles-series.js";
import * as u from "./util.js";

//The portion of a chart where things are actually drawn
export class Pane {
    id: string = ''
    div: HTMLDivElement
    flex_width: number
    flex_height: number
    legend?: Legend
    main_series: AnySeries
    series: AnySeries[] = []

    private chart: IChartApi
    private chart_div: HTMLDivElement

    constructor(
        id: string,
        div: HTMLDivElement,
        flex_width: number = 1,
        flex_height: number = 1,
        chart_opts: DP<TimeChartOptions> = u.DEFAULT_PYCHART_OPTS
    ) {
        this.id = id
        this.div = div
        this.flex_width = flex_width
        this.flex_height = flex_height

        //Only One Chart per pane, so this is the only definition needed
        this.chart = createChart(this.div, chart_opts);
        this.chart_div = this.chart.chartElement()

        this.chart_div.addEventListener('mousedown', this.assign_active_pane.bind(this))

        this.main_series = this.chart.addCandlestickSeries()
        // this.main_series = this.chart.addCustomSeries(new RoundedCandleSeries())
    }

    /**
     * Update Global 'active_pane' reference to this instance. 
     */
    assign_active_pane() {
        if (window.active_pane)
            window.active_pane.div.removeAttribute('active')

        window.active_pane = this
        window.active_pane.div.setAttribute('active', '')
    }

    set_main_series(series_type: u.Series_Type, data: AnySeriesData) {
        let new_series: AnySeries
        switch (series_type) {
            case (u.Series_Type.LINE):
                new_series = this.chart.addLineSeries(); break;
            case (u.Series_Type.AREA):
                new_series = this.chart.addAreaSeries(); break;
            case (u.Series_Type.HISTOGRAM):
                new_series = this.chart.addHistogramSeries(); break;
            case (u.Series_Type.BASELINE):
                new_series = this.chart.addBaselineSeries(); break;
            case (u.Series_Type.BAR):
                new_series = this.chart.addBarSeries(); break;
            case (u.Series_Type.CANDLESTICK):
                new_series = this.chart.addCandlestickSeries(); break;
            case (u.Series_Type.ROUNDED_CANDLE):
                new_series = this.chart.addCustomSeries(new RoundedCandleSeries()); break;
            default:
                return // Whitespace
        }
        this.chart.removeSeries(this.main_series)
        //@ts-ignore (Type Checking Done in Python, Data should already be updated if it needed to be)
        new_series.setData(data)
        this.main_series = new_series
    }

    /**
     * Sets The Data of a Series to the data list given.
     * @param dtype The type of data Series given
     * @param data The List of Data. It is trusted that this data actually matches the dtype given
     * @param series The Data Series to be updated. Can be any of the base SeriesAPI types
     */
    set_main_data(data: AnySeriesData[]) {
        if (data.length === 0) {
            //Delete Present Data if none was given.
            this.main_series.setData([])
            return
        } else if (this.main_series === undefined) {
            return
        }

        //Type checking presumed to have been done on the python side
        this.main_series.setData(data)
        this.autoscale_time_axis()
    }

    /**
     * Resize the Pane given the Pane's flex size
     * @param width Total Frame Width in px
     * @param height Total Frame Height in px
     */
    resize(width: number, height: number) {
        let this_width = width * this.flex_width
        let this_height = height * this.flex_height

        this.div.style.width = `${this_width}px`
        this.div.style.height = `${this_height}px`
        this.chart.resize(this_width, this_height, false)
    }

    add_candlestick_series(options?: DP<CandlestickSeriesOptions>) {
        this.series.push(this.chart.addCandlestickSeries(options))
    }

    create_line() {
        const data = this.main_series.data() as CandlestickData[]
        const dataLength = data.length
        console.log(data[0].time)
        const point1 = {
            time: data[dataLength - 50].time,
            value: data[dataLength - 50].close * 0.9,
        };
        const point2 = {
            time: data[dataLength - 5].time,
            value: data[dataLength - 5].close * 1.1,
        };
        const trend = new TrendLine(point1, point2);
        this.main_series.attachPrimitive(trend);
    }


    fitcontent() { this.chart.timeScale().fitContent() }
    autoscale_time_axis() { this.chart.timeScale().resetTimeScale() }
    update_timescale_opts(newOpts: DeepPartial<HorzScaleOptions>) { this.chart.timeScale().applyOptions(newOpts) }
}