/** @odoo-module **/
import {Component, onWillStart} from "@odoo/owl";
import {SocialNetworkChartAccount} from "@connector_social_base/components/components.esm";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

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
            [[]]
        );
    }
}

registry.category("actions").add("social_network_chart", SocialNetworkChart);
