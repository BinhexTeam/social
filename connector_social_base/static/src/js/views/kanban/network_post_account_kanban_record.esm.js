/** @odoo-module **/
import {onWillStart, useEffect, useRef} from "@odoo/owl";
import {KanbanRecord} from "@web/views/kanban/kanban_record";
import {SocialNetworkCommentDialog} from "@connector_social_base/js/components/social_network_comment_dialog/social_network_comment_dialog.esm";
import {SocialPostAccountMixin} from "@connector_social_base/js/app/connector_social_base_mixins.esm";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";

export class NetworkPostAccountKanbanRecord extends SocialPostAccountMixin(
    KanbanRecord
) {
    setup() {
        super.setup();
        this.record.messageLength = 150;
        this.record.countShowImage = 2;
        this.rootRef = useRef("root");
        this.dialogService = useService("dialog");
        this.effectService = useService("effect");
        this.messageNotExistPost = _t("The post does not exist or has been deleted.");
        onWillStart(async () => {
            this.record.accountsBasic = await this.env.model._loadAccountsBasic();
            this.record.published_date = luxon.DateTime.fromISO(
                this.record.published_date.raw_value
            ).toFormat("d/M/y");
        });

        // Show all message
        useEffect(
            (value) => {
                if (value) {
                    value.addEventListener("click", this.onShowMoreMessage.bind(this));
                    return () => {
                        value.removeEventListener(
                            "click",
                            this.onShowMoreMessage.bind(this)
                        );
                    };
                }
            },
            () => [this.rootRef.el.querySelector(".show-more-message")]
        );

        // Like or dislike post
        useEffect(
            (value) => {
                if (value) {
                    value.addEventListener("click", this.onLikePost.bind(this));
                    return () => {
                        value.removeEventListener("click", this.onLikePost.bind(this));
                    };
                }
            },
            () => [this.rootRef.el.querySelector(".social-like-post")]
        );

        // Show all images
        useEffect(
            (value) => {
                if (value) {
                    value.addEventListener("click", this.onShowAllImages.bind(this));
                    return () => {
                        value.removeEventListener(
                            "click",
                            this.onShowAllImages.bind(this)
                        );
                    };
                }
            },
            () => [this.rootRef.el.querySelector(".social-all-images")]
        );

        // Post Comments
        useEffect(
            (value) => {
                if (value) {
                    value.addEventListener("click", this.onPostComment.bind(this));
                    return () => {
                        value.removeEventListener(
                            "click",
                            this.onPostComment.bind(this)
                        );
                    };
                }
            },
            () => [this.rootRef.el.querySelector(".social-post-comment")]
        );
    }

    onPostComment(ev) {
        ev.stopPropagation();
        this.dialogService.add(SocialNetworkCommentDialog, {
            title: _t("Post Comment"),
            post: this.record,
            images: JSON.parse(this.record.image_urls.raw_value),
        });
    }

    validPostExist() {
        return true;
    }

    messagePostNotExist() {
        this.notification.add(this.messageNotExistPost, {
            type: "info",
        });
    }

    async onGlobalClick(ev) {
        const kanban_social = ev.target.closest("div.oe_kanban_social_dashboard");
        // Checking if the post exists
        if (kanban_social !== null && !this.record.post_account_url.value) {
            this.messagePostNotExist();
        } else if (kanban_social !== null && this.record.post_account_url.raw_value) {
            const post_exist = await this.validPostExist();
            if (post_exist) {
                window.open(this.record.post_account_url.value, "_blank");
            } else {
                this.messagePostNotExist();
            }
        }
        return super.onGlobalClick(ev);
    }
}

NetworkPostAccountKanbanRecord.components = {
    ...KanbanRecord.components,
};
