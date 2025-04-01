/** @odoo-module **/

import {Component, onMounted, useRef} from "@odoo/owl";
import {SocialNetworkFilter} from "../social_network_filter/social_network_filter.esm";
import {useService} from "@web/core/utils/hooks";

export class SocialNetworkChartAccount extends Component {
    static template = "connector_social_base.SocialNetworkChartAccount";
    static props = {
        socialChartAccount: {type: Object, required: true},
    };
    static components = {
        SocialNetworkFilter,
    };

    /**
     * Sets up the component.
     *
     * This method is called once, when the component is set up.
     * It sets up the component's services and initializes its state.
     *
     */
    setup() {
        super.setup();
        this.ormService = useService("orm");
        this.chartCtx = useRef("chartAccount");
        this.chart = null;
        onMounted(this.loadChart);
    }

    /**
     * @returns {Object} The social chart account this component is attached to.
     *
     * This property is a shortcut to access the social chart account that has
     * been given as a prop to this component.
     *
     * @note This property is read-only.
     */
    get chartAccount() {
        return this.props.socialChartAccount;
    }

    /**
     * Creates a new chart.
     *
     * This method takes two arguments that are used to create a new chart with
     * the given labels and datasets. If no arguments are provided, the chart
     * will be created using the labels and datasets from the social chart
     * account that has been given as a prop to this component.
     *
     * @param {string[]} [labels] The labels of the chart.
     * @param {Object} [datasets] The datasets of the chart.
     * @returns {void}
     */
    loadChart(labels, datasets) {
        if (this.chart) this.chart.destroy();

        this.chart = new Chart(this.chartCtx.el, {
            type: "line",
            data: {
                labels: labels ? labels : this.chartAccount.labels,
                datasets: datasets ? datasets : this.chartAccount.datasets,
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: () => this.chartAccount.chartLabel,
                    },
                },
            },
        });
    }

    /**
     * Handles the filtering of chart statistics based on the given filter
     * criteria.
     *
     * This method is called when the user wants to filter the chart statistics.
     * It takes four arguments, which are used to filter the chart statistics:
     * - `id`: The ID of the social network account for which the chart
     * statistics should be filtered.
     * - `startDate`: The start date of the filter. If this argument is not
     * provided, the start date will not be taken into account.
     * - `endDate`: The end date of the filter. If this argument is not
     * provided, the end date will not be taken into account.
     * - `chartFilterType`: The type of the filter. If this argument is not
     * provided, the filter will not be taken into account.
     *
     * @param {{id: Number, startDate: DateTime, endDate: DateTime, chartFilterType: String}} params - The filter criteria.
     *
     */
    async onFilterChart({id, startDate, endDate, chartFilterType}) {
        let updateChart = [];
        let start_date = null;
        let end_date = null;
        if (startDate) start_date = startDate.toFormat("yyyy-MM-dd");
        if (endDate) end_date = endDate.toFormat("yyyy-MM-dd");
        if (start_date || end_date || chartFilterType)
            updateChart = await this.ormService.call(
                "social.network.account",
                "get_chart_account_statistics",
                [id, start_date, end_date, chartFilterType.toUpperCase()]
            );
        if (updateChart.length > 0)
            this.loadChart(updateChart[0].labels, updateChart[0].datasets);
    }

    /**
     * Called when the user wants to clear the chart filters.
     *
     * This method will call `loadChart` without any parameter, which will
     * clear the filters and show the full data.
     *
     * @returns {void}
     */
    clearFilterChart() {
        this.loadChart();
    }
}
