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

    /**
     * Initializes the component by setting up services, state, and event listeners.
     *
     * - Sets up dialog, social, and notification services.
     * - Initializes references for comment textarea and remove image button.
     * - Binds the emoji selection handler and initializes the emoji picker.
     * - Defines the state with image source, comment emptiness, and comments array.
     * - Loads initial comments for the post on component start.
     * - Listens for comment reload events to update the comment list.
     * - Sets up a periodic refresh for comments every 60 seconds.
     * - Cleans up the refresh interval on component unmount.
     */
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

    /**
     * Handles the selection of an emoji from the emoji picker.
     *
     * - Grabs the comment textarea element and the current selection start.
     * - Sets the component's comment empty state to false.
     * - Inserts the selected emoji at the current selection start.
     * - Focuses the textarea and sets the selection range to the position
     *   after the inserted emoji.
     *
     * @param {String} str - The selected emoji.
     */
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

    /**
     * Handles the selection of an image from the image selector.
     *
     * - Sets the component's image source state to a base64 encoded
     *   representation of the selected image.
     *
     * @param {{data: String, type: String}} ev
     *   - `data`: The base64 encoded image string.
     *   - `type`: The MIME type of the image.
     */
    onSelectImage({data, type}) {
        this.state.imageSrc = "data:" + type + ";base64," + data;
    }

    /**
     * Updates the comment emptiness state based on the keydown event in the comment textarea.
     *
     * - Sets the `commentEmpty` state to `true` if the textarea value is empty, otherwise `false`.
     *
     * @param {Event} ev - The keydown event from the comment textarea.
     */
    onKeyDownComment(ev) {
        this.state.commentEmpty = !ev.target.value;
    }

    /**
     * Removes the currently selected image.
     *
     * - Sets the `imageSrc` state to `null`, effectively clearing the image source.
     */
    removeImage() {
        this.state.imageSrc = null;
    }

    /**
     * A getter for the comments state.
     *
     * @returns {Array<Object>}
     *   An array of comments. Each comment object has the following properties:
     *   - `id`: The comment's ID.
     *   - `author_id`: The ID of the user who wrote the comment.
     *   - `author_name`: The name of the user who wrote the comment.
     *   - `content`: The content of the comment.
     *   - `create_date`: The timestamp when the comment was created.
     */
    get comments() {
        return this.state.comments;
    }

    /**
     * Updates the list of comments for the post.
     *
     * - Calls the `getComments` method of the `socialService` to retrieve the
     *   list of comments for the post.
     * - Sets the `comments` state with the retrieved list of comments.
     *
     * @returns {Promise<void>}
     *   The promise resolved when the comments are retrieved and the state is
     *   updated.
     */
    async updateListComments() {
        this.state.comments = await this.socialService.getComments(
            this.props.post.id.raw_value
        );
    }

    /**
     * Cleans the comment area by resetting the `commentEmpty` state and
     * clearing the image source and the comment textarea value.
     *
     * @returns {void}
     */
    cleanAreaComment() {
        this.state.commentEmpty = true;
        this.state.imageSrc = "";
        this.commentTextarea.el.value = "";
    }

    /**
     * Creates a comment.
     *
     * This method is overridden by subclasses to implement the logic to create
     * a comment. It should return an object with a `success` property set to
     * `true` if the comment was created successfully, and a `message` property
     * set to the message to display to the user.
     *
     * @returns {Object}
     */
    async _onCreateComment() {
        return {};
    }

    /**
     * Creates a comment.
     *
     * - Calls `_onCreateComment` to create the comment.
     * - Shows a notification with the message returned by `_onCreateComment`.
     * - Cleans the comment area.
     * - Updates the list of comments.
     *
     * @param {Event} ev - The click event on the "Post comment" button.
     *
     * @returns {Promise<void>}
     *   The promise resolved when the comment is created and the notification
     *   is displayed.
     */
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

    /**
     * Opens a dialog to show all images in the post.
     *
     * This method is called when the "Show all images" button is clicked.
     * It stops the event propagation and opens a dialog with all images
     * in the post.
     *
     * @param {Event} ev - The click event on the "Show all images" button.
     */
    onShowAllImages(ev) {
        ev.stopPropagation();
        this.dialogService.add(SocialNetworkImagesDialog, {
            title: _t("All Images"),
            images: JSON.parse(this.props.post.image_urls.raw_value),
        });
    }

    /**
     * Toggles the visibility of the remove image button when the mouse hovers over the image.
     *
     * This method toggles the "d-none" class on the remove image button
     * reference, effectively showing or hiding the button when the mouse
     * enters the image area.
     */
    onMouseOverImage() {
        this.btnRemoveImageRef.el.classList.toggle("d-none");
    }

    /**
     * Toggles the visibility of the remove image button when the mouse leaves the image.
     *
     * This method toggles the "d-none" class on the remove image button
     * reference, effectively showing or hiding the button when the mouse
     * exits the image area.
     */
    onMouseLeaveImage() {
        this.btnRemoveImageRef.el.classList.toggle("d-none");
    }
}
