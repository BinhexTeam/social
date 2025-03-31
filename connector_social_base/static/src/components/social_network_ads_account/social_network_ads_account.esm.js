/** @odoo-module **/

import {Component, onWillStart, useState, useRef} from "@odoo/owl";
import {SocialNetworkAds} from "../social_network_ads/social_network_ads.esm";
import {_t} from "@web/core/l10n/translation";
import {registry} from "@web/core/registry";
import {useService} from "@web/core/utils/hooks";
const {DateTime} = luxon;

export class SocialNetworkAdsAccount extends Component {
    static template = "connector_social_base.SocialNetworkAdsAccount";
    static components = {
        SocialNetworkAds,
    };

    setup() {
        this.ormService = useService("orm");
        this.notification = useService("notification");
        this.socialAdsAccount = [];
        this.campaigns = [];
        this.posts = [];
        this.social_state = useState({
            socialAds: [],
            loaderAds: false,
            filterAds: false,
        });
        this.startDate = useRef("start_date");
        this.endDate = useRef("end_date");
        this.filter_campaign = useRef("filter_campaign");
        this.filter_post = useRef("filter_post");
        onWillStart(async () => {
            await this._loadAdsAccount();

        });
    }

    onValidateRangeDate() {
        if (this.startDate.el.value && this.endDate.el.value) {
            if (this.startDate.el.value > this.endDate.el.value) {
                this.notification.add(_t("Start date must be less than end date."), {
                    type: "danger",
                    fast: true,
                });
                this.startDate.el.val("");
            }
        }
    }

    onFilterCampaign() {
        let campaign = this.filter_campaign.el.value;
        if (campaign) {
            this.onFilterAds();
        } else {
            this.onFilterAds(true);
        }
    }

    onFilterPosts() {
        let post = this.filter_post.el.value;
        if (post) {
            this.onFilterAds();
        } else {
            this.onFilterAds(false, true);
        }
    }

    filter_ads(item, campaign, post, startDate, endDate) {
        let created = DateTime.fromFormat(item.created, "dd/MM/yyyy");
        let filterAds = "";
        if (campaign && post && startDate && endDate) {
            filterAds = item.campaign.id === parseInt(campaign)
                && item.reference === post
                && created >= startDate && created <= endDate;
        } else if (!campaign && post && startDate && endDate) {
            filterAds = created >= startDate && created <= endDate
                && item.reference === post;
        } else if (!post && campaign && startDate && endDate) {
            filterAds = created >= startDate && created <= endDate
                && item.campaign.id === parseInt(campaign);
        } else if (post && campaign && !startDate && !endDate) {
            filterAds = item.reference === post
                && item.campaign.id === parseInt(campaign);
        } else if (!post && !campaign && startDate && endDate) {
            filterAds = created >= startDate && created <= endDate;
        } else if (!post && !campaign && !startDate && endDate) {
            filterAds = created <= endDate;
        } else if (!post && !campaign && startDate && !endDate) {
            filterAds = created >= startDate;
        } else if (post && !campaign && !startDate && !endDate) {
            filterAds = item.reference === post;
        } else if (campaign && !post && !startDate && !endDate) {
            filterAds = item.campaign.id === parseInt(campaign);
        }
        return filterAds;
    }

    onFilterAds(not_campaign = false, not_post = false) {
        this.social_state.filterAds = true;
        let campaign = this.filter_campaign.el.value;
        let post = this.filter_post.el.value;
        let startDate = this.startDate.el.value ? DateTime.fromISO(this.startDate.el.value) : null;
        let endDate = this.endDate.el.value ? DateTime.fromISO(this.endDate.el.value) : null;

        if ((typeof not_campaign === "boolean" && !not_campaign || typeof not_campaign !== "boolean") &&
            (typeof not_post === "boolean" && !not_post || typeof not_post !== "boolean")
            && !campaign && !post && !startDate && !endDate) {
            this.notification.add(_t("Please select a campaign or a post or a range date."), {
                type: "danger",
            });
        } else if (campaign || post || startDate || endDate) {
            this.social_state.socialAds = this.socialAdsAccount.ads.filter(item => {
                return this.filter_ads(item, campaign, post, startDate, endDate);
            });
        } else {
            this.clearFilter();
        }
        this.social_state.filterAds = false;
    }

    clearFilter() {
        this.social_state.socialAds = this.socialAdsAccount.ads;
        this.filter_campaign.el.value = "";
        this.filter_post.el.value = "";
        this.startDate.el.value = "";
        this.endDate.el.value = "";
    }

    get ads() {
        return this.social_state.socialAds;
    }

    async onUpdateAllAds() {
        await this._loadAdsAccount();
    }

    async _loadAdsAccount() {
        this.social_state.loaderAds = true;
        let adsAccount = await this.ormService.call(
            "social.network.account",
            "load_ads_accounts",
            [[]],
        );
        this.socialAdsAccount = adsAccount;
        this.social_state.socialAds = adsAccount.ads;
        this.campaigns = adsAccount.campaigns;
        this.posts = adsAccount.posts;
        this.social_state.loaderAds = false;
    }
}

registry.category("actions").add("social_network_ads_account", SocialNetworkAdsAccount);
