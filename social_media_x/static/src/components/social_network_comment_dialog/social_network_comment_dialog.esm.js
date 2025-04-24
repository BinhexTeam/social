/** @odoo-module **/

import {SocialNetworkCommentDialog} from "@social_media_base/components/social_network_comment_dialog/social_network_comment_dialog.esm";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(SocialNetworkCommentDialog.prototype, {
    /**
     * Sets up the component's services.
     *
     * This method is overridden to set up the `socialXService` service.
     */
    setup() {
        super.setup();
        this.socialXService = useService("social_x_service");
    },

    /**
     * Creates a comment for a post.
     *
     * If the post's media type is "x", it utilizes the `createXComment` method
     * from the `socialXService` to create the comment with the provided post ID,
     * comment text, and image source. Otherwise, it falls back to the parent
     * class's `_onCreateComment` method.
     *
     * @returns {Object}
     *   The response from the social service, containing a `success` property indicating
     *   whether the comment was created successfully, and a `message` property with the
     *   relevant message for the user.
     */
    async _onCreateComment() {
        if (this.props.post.media_type.raw_value === "x") {
            return await this.socialXService.createXComment(
                this.props.post.id.raw_value,
                this.commentTextarea.el.value,
                this.state.imageSrc
            );
        }
        return super._onCreateComment();
    },
});
