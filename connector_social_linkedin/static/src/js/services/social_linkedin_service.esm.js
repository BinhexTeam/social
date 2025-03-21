/** @odoo-module */

import {registry} from "@web/core/registry";

export const socialLinkedinService = {
    dependencies: ["orm"],

    async start(env, {orm}) {
        return {
            async createLinkedinComment(post_account_id, comment, image_base64) {
                if (!post_account_id) {
                    return [];
                }
                return await orm.call(
                    "social.network.post.account",
                    "create_linkedin_comment",
                    [post_account_id, comment, image_base64]
                );
            },
            async deleteLinkedinComment(post_account_id, comment_id, actor_urn) {
                if (!post_account_id) {
                    return [];
                }
                return await orm.call(
                    "social.network.post.account",
                    "delete_linkedin_comment",
                    [post_account_id, comment_id, actor_urn]
                );
            },
            async validPostLinkedinExist(post_account_id) {
                if (!post_account_id) {
                    return false;
                }
                return await orm.call(
                    "social.network.post.account",
                    "get_linkedin_comment",
                    [post_account_id]
                );
            },
        };
    },
};

registry.category("services").add("social_linkedin_service", socialLinkedinService);
