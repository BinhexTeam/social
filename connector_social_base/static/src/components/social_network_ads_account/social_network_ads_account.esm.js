/** @odoo-module **/

import {Component, onWillStart} from "@odoo/owl";
import {SocialNetworkAds} from "../social_network_ads/social_network_ads.esm";
import {SocialNetworkCampaign} from "../social_network_campaign/social_network_campaign.esm";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

export class SocialNetworkAdsAccount extends Component {
    static template = "connector_social_base.SocialNetworkAdsAccount";
    static components = {
        SocialNetworkCampaign,
        SocialNetworkAds,
    };

    setup() {
        this.ormService = useService("orm");
        onWillStart(async () => {
            this.campaigns = await this._loadCampaigns();
            this.ads_account = await this._loadAdsAccount();
        });
    }

    async _loadCampaigns() {
        return await this.ormService.call(
            "social.network.account",
            "load_campaigns_accounts",
            [[]]
        );
    }

    async _loadAdsAccount() {
        return await this.ormService.call(
            "social.network.account",
            "load_ads_accounts",
            [[]]
        );
    }
}

registry.category("actions").add("social_network_ads_account", SocialNetworkAdsAccount);
