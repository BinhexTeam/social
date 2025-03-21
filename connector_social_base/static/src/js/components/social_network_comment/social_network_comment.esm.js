/** @odoo-module **/

import {Component} from "@odoo/owl";
import {Dropdown} from "@web/core/dropdown/dropdown";
import {DropdownItem} from "@web/core/dropdown/dropdown_item";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";

export class SocialNetworkComment extends Component {
    static template = "connector_social_base.SocialNetworkComment";
    static components = {
        Dropdown,
        DropdownItem,
    };
    static props = {
        socialComment: {type: Object, required: true},
        post: {type: Object, required: true},
    };

    setup() {
        super.setup();
        this.socialService = useService("social_service");
        this.notificationService = useService("notification");
        this.dialogService = useService("dialog");
        this.effectService = useService("effect");
    }

    async _onDeleteComment() {
        return {};
    }

    async onDeleteComment() {
        const result = await this._onDeleteComment();
        const message =
            result.message === undefined ? _t("Comment deleted") : result.message;
        const type_notif = result.success === true ? "success" : "danger";
        this.notificationService.add(message, {
            type: type_notif,
        });
        this.env.bus.trigger("SOCIAL:RELOAD_COMMENTS");
    }

    mediaNotLikeEnable() {
        return [];
    }

    async onLikeComment() {
        const response = await this.socialService.likeComment(
            this.props.post.id.raw_value,
            this.props.socialComment.id,
            this.props.post.linkedin_account_urn.raw_value
        );
        if (response.success) {
            this.effectService.add({
                type: "rainbow_man",
                message: _t("You have liked the post."),
                imgUrl: "/connector_social_base/static/src/img/like.png",
                fadeout: "fast",
            });
        } else {
            this.notificationService.add(_t(response.message), {type: "info"});
        }
    }

    _onReplyComment() {
        return {};
    }

    onReplyComment() {
        this.env.bus.trigger("SOCIAL:RELOAD_COMMENTS");
    }

    _onEditComment() {
        return {};
    }

    onEditComment() {
        this.env.bus.trigger("SOCIAL:RELOAD_COMMENTS");
    }

    editComment() {
        return;
    }
}
