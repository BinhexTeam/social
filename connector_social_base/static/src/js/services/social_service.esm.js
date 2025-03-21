/** @odoo-module */

import {registry} from "@web/core/registry";

export const socialService = {
    dependencies: ["orm"],

    async start(env, {orm}) {
        return {
            async getComments(post_account_id = null) {
                if (!post_account_id) {
                    return [];
                }
                return await orm.call("social.network.post.account", "get_comments", [
                    post_account_id,
                ]);
            },
            async likeComment(post_account_id, comment_id, actor_urn) {
                if (!post_account_id || !comment_id || !actor_urn) {
                    return {
                        success: false,
                        message: "An error occurred while liking the comment",
                    };
                }
                return await orm.call(
                    "social.network.post.account",
                    "action_like_comment",
                    [[post_account_id], comment_id, actor_urn]
                );
            },
        };
    },
};

registry.category("services").add("social_service", socialService);
