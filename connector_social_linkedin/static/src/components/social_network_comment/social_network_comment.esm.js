/** @odoo-module **/

import {SocialNetworkComment} from "@connector_social_base/components/social_network_comment/social_network_comment.esm";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(SocialNetworkComment.prototype, {
    setup() {
        super.setup();
        this.socialLinkedinService = useService("social_linkedin_service");
    },
    async _onDeleteComment() {
        let result = super._onDeleteComment();
        result = await this.socialLinkedinService.deleteLinkedinComment(
            this.props.post.id.raw_value,
            this.props.socialComment.id,
            this.props.socialComment.actor
        );
        return result;
    },

    mediaNotLikeEnable() {
        const values = super.mediaNotLikeEnable();
        values.push("linkedin");
        return values;
    },
});
