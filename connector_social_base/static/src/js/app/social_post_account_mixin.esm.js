/** @odoo-module */
import {SocialNetworkImagesDialog} from "../../components/social_network_images_dialog/social_network_images_dialog.esm";
import {_t} from "@web/core/l10n/translation";

export const SocialPostAccountMixin = (T) =>
    class extends T {
        /**
         * Handles the click on "Show more" button for the post's message.
         *
         * @param {MouseEvent} ev - The click event.
         */
        onShowMoreMessage(ev) {
            ev.stopPropagation();
            this.record.messageLength = this.record.message.raw_value.length;
        }

        /**
         * Handles the click on the "Show all images" button.
         *
         * Opens a dialog with all images of the post.
         *
         * @param {MouseEvent} ev
         *   The click event.
         */
        onShowAllImages(ev) {
            ev.stopPropagation();
            this.dialogService.add(SocialNetworkImagesDialog, {
                title: _t("All Images"),
                images: JSON.parse(this.record.image_urls.raw_value),
                fullscreen: true,
            });
        }

        /**
         * Handles the click on the "Like" button.
         *
         * Calls the ORM method `onLikePost` to like the post. If the like
         * is successful, shows a notification. Otherwise, shows a message
         * as a notification.
         *
         * @param {MouseEvent} ev - The click event on the "Like" button.
         */
        async onLikePost(ev) {
            ev.stopPropagation();
            const response = await this.env.model.onLikePost(this.record);
            if (response.success) {
                this.effectService.add({
                    type: "rainbow_man",
                    message: _t("You have liked the post."),
                    imgUrl: "/connector_social_base/static/src/img/like.png",
                    fadeout: "fast",
                });
            } else {
                this.notification.add(_t(response.message), {type: "info"});
            }
        }
    };
