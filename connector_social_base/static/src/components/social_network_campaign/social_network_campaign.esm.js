/** @odoo-module **/

import {Component} from "@odoo/owl";

export class SocialNetworkCampaign extends Component {
    static template = "connector_social_base.SocialNetworkCampaign";
    static props = {
        socialCampaign: {type: Object, required: true},
    };

    get campaign() {
        return this.props.socialCampaign;
    }

    get statistic() {
        return this.props.socialCampaign.statistic;
    }
}
