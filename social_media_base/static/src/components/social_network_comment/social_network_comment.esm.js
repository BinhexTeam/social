/** @odoo-module **/

import {Component} from "@odoo/owl";
import {Dropdown} from "@web/core/dropdown/dropdown";
import {DropdownItem} from "@web/core/dropdown/dropdown_item";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";

export class SocialNetworkComment extends Component {
    static template = "social_media_base.SocialNetworkComment";
    static components = {
        Dropdown,
        DropdownItem,
    };
    static props = {
        socialComment: {type: Object, required: true},
        post: {type: Object, required: true},
    };

    /**
     * Sets up the component's services.
     *
     * This method is called once, when the component is set up.
     * It sets up the component's services and initializes its state.
     */
    setup() {
        super.setup();
        this.socialService = useService("social_service");
        this.notificationService = useService("notification");
        this.dialogService = useService("dialog");
        this.effectService = useService("effect");
    }

    /**
     * Delete a comment.
     *
     * This method is overridden by subclasses to implement the logic to delete a
     * comment. It should return an object with a `success` property set to `true`
     * if the comment was deleted successfully, and a `message` property set to
     * the message to display to the user.
     *
     * @returns {Object}
     */
    async _onDeleteComment() {
        return {};
    }

    /**
     * Deletes a comment.
     *
     * This method calls `_onDeleteComment` and notifies the user of the result.
     * It also triggers a bus event to reload the comments.
     */
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

    /**
     * Returns the list of media types for which liking a comment is not
     * supported.
     *
     * This method is overridden by subclasses to implement the logic to
     * determine the list of media types for which liking a comment is not
     * supported. It should return an array of strings, where each string is
     * a media type.
     *
     * @returns {String[]}
     */
    mediaNotLikeEnable() {
        return [];
    }

    /**
     * Likes a comment.
     *
     * This method calls `likeComment` on the social service and notifies the
     * user of the result. It also triggers a bus event to reload the comments.
     */
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
                imgUrl: "/social_media_base/static/src/img/like.png",
                fadeout: "fast",
            });
        } else {
            this.notificationService.add(_t(response.message), {type: "info"});
        }
    }

    /**
     * Replies to a comment.
     *
     * This method is overridden by subclasses to implement the logic to reply
     * to a comment. It should return an object with a `success` property set to
     * `true` if the comment was replied successfully, and a `message` property
     * set to the message to display to the user.
     *
     * @returns {Object}
     */
    _onReplyComment() {
        return {};
    }

    /**
     * Replies to a comment.
     *
     * This method triggers a bus event to reload the comments.
     */
    onReplyComment() {
        this.env.bus.trigger("SOCIAL:RELOAD_COMMENTS");
    }

    /**
     * Edits a comment.
     *
     * This method is overridden by subclasses to implement the logic to edit a
     * comment. It should return an object with a `success` property set to
     * `true` if the comment was edited successfully, and a `message` property
     * set to the message to display to the user.
     *
     * @returns {Object}
     */
    _onEditComment() {
        return {};
    }

    /**
     * Edits a comment.
     *
     * This method triggers a bus event to reload the comments.
     */
    onEditComment() {
        this.env.bus.trigger("SOCIAL:RELOAD_COMMENTS");
    }

    /**
     * Edits a comment.
     *
     * This method is overridden by subclasses to implement the logic to edit a
     * comment. It should return an object with a `success` property set to
     * `true` if the comment was edited successfully, and a `message` property
     * set to the message to display to the user.
     *
     */
    editComment() {
        return;
    }
}
