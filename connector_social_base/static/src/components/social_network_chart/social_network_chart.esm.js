/** @odoo-module **/
import {Component, onWillStart} from "@odoo/owl";
import {SocialNetworkChartAccount} from "@connector_social_base/components/social_network_chart_account/social_network_chart_account.esm";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class SocialNetworkChart extends Component {
    static template = "connector_social_base.SocialNetworkChart";
    static components = {
        SocialNetworkChartAccount,
    };

    /**
     * Sets up the component.
     *
     * @private
     */
    setup() {
        super.setup();
        this.ormService = useService("orm");
        this.socialAccountStatistics = [];
        onWillStart(async () => {
            await this._loadAccountStatistics();
        });
    }

    /**
     * Loads the statistics for the social network accounts.
     *
     * @private
     * @returns {Promise<void>}
     */
    async _loadAccountStatistics() {
        this.socialAccountStatistics = await this.ormService.call(
            "social.network.account",
            "get_chart_account_statistics",
            [[]]
        );
    }
}

registry.category("actions").add("social_network_chart", SocialNetworkChart);
