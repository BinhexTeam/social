/** @odoo-module */

import {registry} from "@web/core/registry";

export const socialXService = {
    dependencies: ["orm"],

    /**
     * Returns an object with the following methods:
     * - `createXComment`: Creates a comment on a social network post.
     *
     * @param {Object} env - web environment
     * @param {Object} services - services to use
     * @param {Object} services.orm - ORM service
     * @returns {Object} - an object with the methods `createXComment`
     */
    async start(env, {orm}) {
        return {
            /**
             * Creates a comment on a social network post.
             *
             * @param {Number} post_account_id - The ID of the post account to which the comment belongs.
             * @param {String} comment - The comment text.
             * @param {String} [image_base64] - The image data as a base64 string.
             * @returns {Promise<Object[]>} - A promise that resolves to an array of comments.
             */
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
