/** @odoo-module **/

import {Component, onWillStart, useState} from "@odoo/owl";
import {SocialNetworkAds} from "../social_network_ads/social_network_ads.esm";
import {SocialNetworkFilter} from "../social_network_filter/social_network_filter.esm";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";

const {DateTime} = luxon;

export class SocialNetworkAdsAccount extends Component {
    static template = "connector_social_base.SocialNetworkAdsAccount";
    static components = {
        SocialNetworkAds,
        SocialNetworkFilter,
    };

    /**
     * Initializes the component by setting up services and initializing state.
     *
     * This method sets up the ORM and notification services, and initializes
     * the state variables for social ads, campaigns, and posts. It also
     * triggers the loading of ad accounts before the component starts.
     */
    setup() {
        this.ormService = useService("orm");
        this.notification = useService("notification");
        this.socialAdsAccount = [];
        this.campaigns = [];
        this.posts = [];
        this.social_state = useState({
            socialAds: [],
            loaderAds: false,
        });
        onWillStart(async () => {
            await this._loadAdsAccount();
        });
    }

    /**
     * Filter ads based on a given campaign, post, and date range.
     *
     * @param {Object} item - The ad to be filtered.
     * @param {String} [campaign] - The id of the campaign to filter by.
     * @param {String} [post] - The id of the post to filter by.
     * @param {DateTime} [startDate] - The start date of the range to filter by.
     * @param {DateTime} [endDate] - The end date of the range to filter by.
     * @returns {Boolean} - Whether the ad should be shown given the filter criteria.
     */
    filter_ads(item, campaign, post, startDate, endDate) {
        const created = DateTime.fromFormat(item.created, "dd/MM/yyyy");
        return (
            (campaign ? item.campaign.id === parseInt(campaign, 10) : true) &&
            (post ? item.reference === post : true) &&
            (startDate ? created >= startDate : true) &&
            (endDate ? created <= endDate : true)
        );
    }

    /**
     * Handles the filtering of ads based on campaign, post, and date range.
     *
     * If no campaign, post, or date range is selected, a notification is
     * displayed asking the user to select a filter. If some filter criteria
     * are selected, the ads are filtered based on the `filter_ads` method and
     * the filtered ads are stored in the component's state. If no filter
     * criteria are selected, the filter is cleared and all ads are shown again.
     *
     * @param {{startDate: DateTime, endDate: DateTime, campaign: String, post: String}} params - The filter criteria.
     */
    onFilterAds({startDate, endDate, campaign, post}) {
        if (!campaign && !post && !startDate && !endDate) {
            this.notification.add(
                _t("Please select a campaign or a post or a range date."),
                {
                    type: "danger",
                }
            );
        } else if (campaign || post || startDate || endDate) {
            this.social_state.socialAds = this.socialAdsAccount.ads.filter((item) => {
                return this.filter_ads(item, campaign, post, startDate, endDate);
            });
        } else {
            this.clearFilter();
        }
    }

    /**
     * Clears the filter and displays all ads again.
     *
     * When called, this method resets the `socialAds` state to the original
     * list of ads retrieved from the server, effectively clearing any
     * filtering criteria.
     */
    clearFilter() {
        this.social_state.socialAds = this.socialAdsAccount.ads;
    }

    /**
     * Gets the ads after applying the filter criteria.
     *
     * @returns {Object[]} - The ads after applying the filter criteria.
     */
    get ads() {
        return this.social_state.socialAds;
    }

    /**
     * Loads all ads again from the server.
     *
     * This method is triggered by the "Sync ads" button and is used to
     * reload all ads from the server. It will clear any filtering criteria
     * and display all ads again.
     *
     * @returns {Promise<void>}
     */
    async onUpdateAllAds() {
        await this._loadAdsAccount();
    }

    /**
     * Loads all ads from the server.
     *
     * This method is called when the user clicks on the "Sync ads" button.
     * It will clear any filtering criteria, set the `loaderAds` state to
     * `true`, and load all ads from the server. After loading the ads,
     * it sets the `loaderAds` state to `false` and updates the component's
     * state with the retrieved ads.
     *
     * @returns {Promise<void>}
     */
    async _loadAdsAccount() {
        this.social_state.loaderAds = true;
        const adsAccount = await this.ormService.call(
            "social.network.account",
            "load_ads_accounts",
            [[]]
        );
        this.socialAdsAccount = adsAccount;
        this.social_state.socialAds = adsAccount.ads;
        this.campaigns = adsAccount.campaigns;
        this.posts = adsAccount.posts;
        this.social_state.loaderAds = false;
    }
}

registry.category("actions").add("social_network_ads_account", SocialNetworkAdsAccount);
