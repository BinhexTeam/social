/** @odoo-module **/
import {useRef, useState} from "@odoo/owl";
import {SocialNetwork} from "../../js/app/social_network.esm";

const {DateTime} = luxon;

export class SocialNetworkFilter extends SocialNetwork {
    static template = "connector_social_base.SocialNetworkFilter";
    static props = {
        startDate: {type: String, required: true},
        endDate: {type: String, required: true},
        posts: {type: Array, optional: true},
        objectId: {type: Number, optional: true},
        campaigns: {type: Array, optional: true},
        clearFilter: {type: Function, required: true},
        filter: {type: Function, required: true},
        filterGranularity: {type: Boolean, optional: true},
    };

    /**
     * Setups the component by storing the references of the different HTML
     * elements of the filter panel and by setting the state of the component.
     */
    setup() {
        super.setup();
        this.startDate = useRef("start_date");
        this.endDate = useRef("end_date");
        this.filterCampaign = useRef("filter_campaign");
        this.filterPost = useRef("filter_post");
        this.chartFilterType = useRef("chart_filter_type");
        this.state = useState({
            loadFilter: false,
        });
    }

    /**
     * The list of campaigns associated with the social network.
     *
     * @returns {Array<Object>} An array of objects that represent the campaigns
     * associated with the social network.
     */
    get campaigns() {
        return this.props.campaigns;
    }

    /**
     * Retrieves the list of social network posts.
     *
     * @returns {Array<Object>} An array of posts associated with the social network.
     */
    get posts() {
        return this.props.posts;
    }

    /**
     * The granularity of the filter.
     *
     * @type {Boolean}
     */
    get filterGranularity() {
        return this.props.filterGranularity;
    }

    /**
     * Resets the filter panel to its initial state by clearing all the filters
     * and resetting the filter type to "week".
     */
    onClearFilter() {
        if (this.startDate.el) this.startDate.el.value = "";
        if (this.endDate.el) this.endDate.el.value = "";
        if (this.filterCampaign.el) this.filterCampaign.el.value = "";
        if (this.filterPost.el) this.filterPost.el.value = "";
        if (this.chartFilterType.el) this.chartFilterType.el.value = "week";
        this.props.clearFilter();
    }

    /**
     * Retrieves the values of the filter inputs and calls the filter function
     * with them.
     *
     * @returns {Promise<void>}
     */
    async onFilter() {
        let startDate = null;
        let endDate = null;
        let filterCampaign = null;
        let filterPost = null;
        let chartFilterType = null;
        if (this.startDate.el)
            startDate = this.startDate.el.value
                ? DateTime.fromISO(this.startDate.el.value)
                : null;
        if (this.endDate.el)
            endDate = this.endDate.el.value
                ? DateTime.fromISO(this.endDate.el.value)
                : null;
        if (this.filterCampaign.el) filterCampaign = this.filterCampaign.el.value;
        if (this.filterPost.el) filterPost = this.filterPost.el.value;
        if (this.chartFilterType.el) chartFilterType = this.chartFilterType.el.value;

        await this.props.filter({
            id: this.props.objectId,
            startDate: startDate,
            endDate: endDate,
            campaign: filterCampaign,
            post: filterPost,
            chartFilterType: chartFilterType,
        });
    }
}
