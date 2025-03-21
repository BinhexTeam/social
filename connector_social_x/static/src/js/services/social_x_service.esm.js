/** @odoo-module */

import {registry} from "@web/core/registry";

export const socialXService = {
    dependencies: ["orm"],

    async start(env, {orm}) {
        return {
            async createXComment(post_account_id, comment, image_base64) {
                if (!post_account_id) {
                    return [];
                }
                return await orm.call(
                    "social.network.post.account",
                    "create_x_comment",
                    [post_account_id, comment, image_base64]
                );
            },
        };
    },
};

registry.category("services").add("social_x_service", socialXService);
