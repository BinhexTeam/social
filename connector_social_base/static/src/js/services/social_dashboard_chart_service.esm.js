/** @odoo-module */

import {registry} from "@web/core/registry";

export const socialDashboardChartService = {
    dependencies: ["orm"],

    async start(env, {orm}) {
        return {
            _loadAccounts() {
                return orm.searchRead(
                    "social.network.account",
                    [],
                    [
                        "id",
                        "name",
                        "company_id",
                        "media_id",
                        "account_url",
                        "total_views",
                        "interactions_count",
                        "engagement_rate",
                    ]
                );
            },
        };
    },
};

registry
    .category("services")
    .add("social_dashboard_chart_service", socialDashboardChartService);
