/** @odoo-module */

import {registry} from "@web/core/registry";

export const socialLinkedinService = {
    dependencies: ["orm"],

    async start(env, {orm}) {
        return {
            /**
             * @param {Number} post_account_id - The id of the SocialNetworkPostAccount record
             * @param {String} comment - The comment to be posted
             * @param {String} image_base64 - The base64 encoded image to be posted
             * @returns {Promise<Object[]>} The result of the server call to create a comment
             */
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
            /**
             * Delete a comment on a social network post.
             * @param {Number} post_account_id - The id of the SocialNetworkPostAccount record
             * @param {String} comment_id - The id of the comment to be deleted
             * @param {String} actor_urn - The URN of the actor performing the action
             * @returns {Promise<Object[]>} The result of the server call to delete a comment
             */
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
            /**
             * Checks if a post already exists on LinkedIn.
             * @param {Number} post_account_id - The id of the SocialNetworkPostAccount record
             * @returns {Promise<Boolean>} Whether the post exists
             */
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
