/** @odoo-module **/

import {SocialNetworkCommentDialog} from "@connector_social_base/components/social_network_comment_dialog/social_network_comment_dialog.esm";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(SocialNetworkCommentDialog.prototype, {
    setup() {
        super.setup();
        this.socialLinkedinService = useService("social_linkedin_service");
    },

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
