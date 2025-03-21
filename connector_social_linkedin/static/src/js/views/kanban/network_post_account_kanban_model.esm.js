/** @odoo-module **/

import {NetworkPostAccountKanbanModel} from "@connector_social_base/js/views/kanban/network_post_account_kanban_model.esm";
import {patch} from "@web/core/utils/patch";

patch(NetworkPostAccountKanbanModel.prototype, {
    /**
     * Handles the like button click for a post in the kanban view
     * @param {Object} record - the current record
     * @returns {Promise} resolves with the result of the RPC call
     */
    async onLikePost(record) {
        super.onLikePost();
        const post_id = record.id.value;
        const author_urn = record.linkedin_account_urn.value;
        return await this.orm.silent.call(
            "social.network.post.account",
            "action_like_post",
            [[post_id], author_urn]
        );
    },
});
