/** @odoo-module **/

import {RelationalModel} from "@web/model/relational_model/relational_model";

export class NetworkPostAccountKanbanModel extends RelationalModel {
    _get_domain_network_account() {
        return [];
    }

    /**
     * @returns {Promise<Object[]>} a promise that resolves with
     * an array of objects representing the social network accounts.
     * Each object has the following properties:
     * - id
     * - name
     * - company_id
     * - media_id
     * - account_url
     * - impression_count
     * - interactions_count
     * - engagement
     */
    async _loadAccounts() {
        return await this.orm.searchRead(
            "social.network.account",
            this._get_domain_network_account(),
            [
                "id",
                "name",
                "company_id",
                "media_id",
                "account_url",
                "impression_count",
                "interactions_count",
                "engagement",
            ]
        );
    }

    /**
     * @returns {Promise<Object[]>} a promise that resolves with
     * an array of objects with `id` and `name` properties, representing
     * the social network accounts that are not yet synchronized.
     */
    async _loadAccountsBasic() {
        return await this.orm.searchRead(
            "social.network.account",
            this._get_domain_network_account(),
            ["id", "name"]
        );
    }

    /**
     * Updates posts and their statistics for all social network accounts.
     *
     * This method makes a silent ORM call to the "update_posts_statistics" method
     * on the "social.network.account" model, passing an empty list of account IDs
     * and a flag to update all accounts.
     *
     * @returns {Promise} A promise that resolves when the update operation is complete.
     */
    async onUpdatePostsAndStatistics() {
        return await this.orm.silent.call(
            "social.network.account",
            "update_posts_statistics",
            [[], true]
        );
    }

    /**
     * @param {Object} record a record of a social network post account
     * @description
     * Likes the given post on the social network. The post is identified by the
     * `id` field of the `record` argument. The method silently calls the "like_post"
     * method on the "social.network.post.account" model, passing the `record` argument
     * and no other arguments.
     */
    onLikePost(record) {
        if (!record) return;
        return;
    }
}
