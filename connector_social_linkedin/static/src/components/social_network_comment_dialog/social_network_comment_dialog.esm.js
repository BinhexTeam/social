/** @odoo-module **/

import {SocialNetworkCommentDialog} from "@connector_social_base/components/social_network_comment_dialog/social_network_comment_dialog.esm";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(SocialNetworkCommentDialog.prototype, {
    /**
     * Initializes the component by setting up services.
     *
     * This method is overridden to set up the `socialLinkedinService` service.
     */
    setup() {
        super.setup();
        this.socialLinkedinService = useService("social_linkedin_service");
    },

    /**
     * Creates a comment.
     *
     * If the post is a linkedin post, it calls the `createLinkedinComment` method
     * of the `socialLinkedinService` to create the comment. Otherwise, it calls
     * the `_onCreateComment` method of the parent class.
     *
     * @returns {Object}
     *   The response from the social service, with a `success` property set to
     *   `true` if the comment was created successfully, and a `message` property
     *   set to the message to display to the user.
     */
    async _onCreateComment() {
        if (this.props.post.media_type.raw_value === "linkedin") {
            const response = await this.socialLinkedinService.createLinkedinComment(
                this.props.post.id.raw_value,
                this.commentTextarea.el.value,
                this.state.imageSrc
            );
            return response;
        }
        return super._onCreateComment();
    },
});
