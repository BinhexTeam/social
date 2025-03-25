/** @odoo-module **/

import {SocialNetworkCommentDialog} from "@connector_social_base/components/social_network_comment_dialog/social_network_comment_dialog.esm";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(SocialNetworkCommentDialog.prototype, {
    setup() {
        super.setup();
        this.socialXService = useService("social_x_service");
    },

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
