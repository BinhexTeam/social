/** @odoo-module **/

import {RelationalModel} from "@web/model/relational_model/relational_model";

export class NetworkPostAccountKanbanModel extends RelationalModel {
    _get_domain_network_account() {
        return [];
    }

    _loadAccounts() {
        return this.orm.searchRead(
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

    _loadAccountsBasic() {
        return this.orm.searchRead(
            "social.network.account",
            this._get_domain_network_account(),
            ["id", "name"]
        );
    }

    onUpdatePostsAndStatistics() {
        return this.orm.silent.call(
            "social.network.account",
            "update_posts_statistics",
            [[], true]
        );
    }

    onLikePost(record) {
        if (!record) return;
        return;
    }
}
