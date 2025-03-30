/** @odoo-module **/

import {Component} from "@odoo/owl";

export class SocialNetworkAccount extends Component {
    static template = "connector_social_base.SocialNetworkAccount";
    static props = {
        socialAccounts: {type: Array},
    };
}
