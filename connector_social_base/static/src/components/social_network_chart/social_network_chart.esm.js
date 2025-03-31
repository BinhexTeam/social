/** @odoo-module **/

import {Component, onWillStart, useState} from "@odoo/owl";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
import {SocialNetworkChartAccount} from "../social_network_chart_account/social_network_chart_account.esm";

export class SocialNetworkChart extends Component {
    static template = "connector_social_base.SocialNetworkChart";
    static components = {
        SocialNetworkChartAccount,
    };

    setup() {
        super.setup();
        this.ormService = useService("orm");
        this.notification = useService("notification");
        this.socialAccountStatistics = [];
        onWillStart(async () => {
            await this._loadAccountStatistics();
        });
    }

    async _loadAccountStatistics() {
        this.socialAccountStatistics = await this.ormService.call(
            "social.network.account",
            "get_chart_account_statistics",
            [[]],
        );
    }
}

registry.category("actions").add("social_network_chart", SocialNetworkChart);

