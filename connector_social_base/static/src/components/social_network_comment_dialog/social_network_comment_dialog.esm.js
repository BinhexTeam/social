/** @odoo-module **/

import {
    Component,
    onMounted,
    onWillStart,
    onWillUnmount,
    useRef,
    useState,
} from "@odoo/owl";
import {useBus, useService} from "@web/core/utils/hooks";
import {Dialog} from "@web/core/dialog/dialog";
import {FileUploader} from "@web/views/fields/file_handler";
import {SocialNetworkComment} from "../social_network_comment/social_network_comment.esm";
import {SocialNetworkImagesDialog} from "../social_network_images_dialog/social_network_images_dialog.esm";
import {_t} from "@web/core/l10n/translation";
import {useEmojiPicker} from "@web/core/emoji_picker/emoji_picker";

export class SocialNetworkCommentDialog extends Component {
    static template = "connector_social_base.SocialNetworkCommentDialog";
    static components = {
        Dialog,
        FileUploader,
        SocialNetworkComment,
    };
    static props = {
        title: {type: String, required: true},
        images: {type: Array, required: true},
        post: {type: Object, required: true},
        close: {type: Function},
    };

    setup() {
        super.setup();
        this.dialogService = useService("dialog");
        this.socialService = useService("social_service");
        this.notificationService = useService("notification");
        this.commentTextarea = useRef("comment-textarea");
        this.btnRemoveImageRef = useRef("btn-remove-image");
        this.intervalRefreshComment = null;
        this._onSelectEmoji = this._onSelectEmoji.bind(this);
        useEmojiPicker(useRef("social-emoji"), {
            onSelect: (str) => this._onSelectEmoji(str),
            onClose: () => this.state.autofocus++,
        });

        this.state = useState({
            imageSrc: "",
            commentEmpty: true,
            comments: [],
        });

        onWillStart(async () => {
            this.state.comments = await this.socialService.getComments(
                this.props.post.id.raw_value
            );
        });

        useBus(this.env.bus, "SOCIAL:RELOAD_COMMENTS", async () => {
            await this.updateListComments();
        });

        // Refresh comments every 15 seconds
        onMounted(() => {
            this.intervalRefreshComment = setInterval(() => {
                this.updateListComments();
            }, 60000);
        });

        onWillUnmount(() => {
            clearInterval(this.intervalRefreshComment);
        });
    }

    _onSelectEmoji(str) {
        const textarea = this.commentTextarea.el;
        const selectionStart = textarea.selectionStart;
        this.state.commentEmpty = false;
        textarea.value =
            textarea.value.slice(0, selectionStart) +
            str +
            textarea.value.slice(selectionStart);
        textarea.focus();
        textarea.setSelectionRange(
            selectionStart + str.length,
            selectionStart + str.length
        );
    }

    onSelectImage({data, type}) {
        this.state.imageSrc = "data:" + type + ";base64," + data;
    }

    onKeyDownComment(ev) {
        this.state.commentEmpty = !ev.target.value;
    }

    removeImage() {
        this.state.imageSrc = null;
    }

    get comments() {
        return this.state.comments;
    }

    async updateListComments() {
        this.state.comments = await this.socialService.getComments(
            this.props.post.id.raw_value
        );
    }

    cleanAreaComment() {
        this.state.commentEmpty = true;
        this.state.imageSrc = "";
        this.commentTextarea.el.value = "";
    }

    async _onCreateComment() {
        return {};
    }

    async onCreateComment(ev) {
        ev.stopPropagation();
        const result = await this._onCreateComment();
        const message =
            result.message === undefined ? _t("Comment created") : result.message;
        const type_notif = result.success === true ? "success" : "danger";
        this.notificationService.add(message, {
            type: type_notif,
        });
        this.cleanAreaComment();
        await this.updateListComments();
    }

    onShowAllImages(ev) {
        ev.stopPropagation();
        this.dialogService.add(SocialNetworkImagesDialog, {
            title: _t("All Images"),
            images: JSON.parse(this.props.post.image_urls.raw_value),
        });
    }

    onMouseOverImage() {
        this.btnRemoveImageRef.el.classList.toggle("d-none");
    }

    onMouseLeaveImage() {
        this.btnRemoveImageRef.el.classList.toggle("d-none");
    }
}
