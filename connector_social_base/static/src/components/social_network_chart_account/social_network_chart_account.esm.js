/** @odoo-module **/

import {Component, useState, useRef, onMounted} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";

export class SocialNetworkChartAccount extends Component {
    static template = "connector_social_base.SocialNetworkChartAccount";
    static props = {
        socialChartAccount: {type: Object, required: true},
    };

    setup() {
        super.setup();
        this.ormService = useService("orm");
        this.notification = useService("notification");
        this.chart = useRef("chartAccount");
        this.state = useState({
            isCollapsed: false,
            chartLabel: "Chart",
            chartLabels: ["Day 1", "Day 2", "Day 3", "Day 4", "Day 5", "Day 6"],
            chartDatasets: [
                {
                    label: _t("Clicks"),
                    data: [45,56,89,3,94,23],
                    // borderColor: Utils.CHART_COLORS.red,
                    // backgroundColor: Utils.transparentize(Utils.CHART_COLORS.red, 0.5),
                    pointStyle: "circle",
                    pointRadius: 10,
                    pointHoverRadius: 15,
                }
            ],
        });
        onMounted(this.loadChart);
    }

    get chartAccount() {
        console.warn(this.props.socialChartAccount);
        return this.props.socialChartAccount;
    }

    loadChart() {
        let ctx = this.chart.el;
        return new Chart(ctx, {
            type: "line",
            data: {
                labels: this.props.socialChartAccount.labels,
                datasets: this.props.socialChartAccount.datasets,
            },
            options: {
                responsive: true,
                plugins: {
                    title: {
                        display: true,
                        text: (ctx) => this.props.socialChartAccount.chartLabel,
                    },
                },
            },
        });
    }
}

