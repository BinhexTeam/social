/** @odoo-module **/

import {browser} from "@web/core/browser/browser";
import {Component} from "@odoo/owl";

export class SocialNetworkAds extends Component {
    static template = "connector_social_base.SocialNetworkAds";
    static props = {
        socialAds: {type: Object, required: true},
    };

    get ads() {
        return this.props.socialAds;
    }

    get statistic() {
        return this.props.socialAds.statistic;
    }

    get campaign() {
        return this.props.socialAds.campaign;
    }

    get post() {
        return this.props.socialAds.post;
    }

    onAdsClick() {
        return browser.open(this.ads.url);
    }
}
