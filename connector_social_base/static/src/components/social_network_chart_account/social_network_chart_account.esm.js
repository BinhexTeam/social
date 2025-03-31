/** @odoo-module **/

import {Component, onMounted, useRef} from "@odoo/owl";
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
        onMounted(this.loadChart);
    }

    get chartAccount() {
        return this.props.socialChartAccount;
    }

    loadChart() {
        const ctx = this.chart.el;
        return new Chart(ctx, {
            type: "line",
            data: {
                labels: this.chartAccount.labels,
                datasets: this.chartAccount.datasets,
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
}
