/** @odoo-module **/

import {onWillStart, useSubEnv} from "@odoo/owl";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {SocialNetworkAccount} from "@connector_social_base/components/social_network_account/social_network_account.esm";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";

export class NetworkPostAccountKanbanController extends KanbanController {
    /**
     * @override
     */
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.model.SyncPosts = false;
        onWillStart(async () => {
            if (this.isViewPostNetwork) return;
            this.socialAccounts = await this.model._loadAccounts();
            await this._onUpdatePostsAndStatistics();
        });
        useSubEnv({
            model: this.model,
        });
    }

    /**
     * Checks if the current Kanban view is for the `social.network.post` model.
     * @type {Boolean}
     */
    get isViewPostNetwork() {
        return this.model.config.resModel === "social.network.post";
    }

    /**
     * @private
     * @returns {Promise<any>}
     */
    _onAddAccount() {
        return this.actionService.doAction(
            "connector_social_base.social_media_act_window_kanban"
        );
    }

    /**
     * Opens the form view of the `social.network.post` model to create a new post.
     *
     * @private
     * @returns {Promise<any>}
     */
    _onAddPost() {
        return this.actionService.doAction({
            name: _t("New Post"),
            type: "ir.actions.act_window",
            res_model: "social.network.post",
            views: [[false, "form"]],
        });
    }

    /**
     * Syncs all posts and statistics from all social media accounts.
     *
     * 1. Sets `SyncPosts` to `true` to prevent other sync requests.
     * 2. Calls `onUpdatePostsAndStatistics` model method to sync all posts and statistics.
     * 3. Sets `socialAccounts` to the result of the model method.
     * 4. Reloads the Kanban view.
     * 5. Sets `SyncPosts` back to `false`.
     *
     * @private
     * @returns {Promise<void>}
     */
    async _onUpdatePostsAndStatistics() {
        this.model.SyncPosts = true;
        const data = await this.model.onUpdatePostsAndStatistics();
        this.socialAccounts = JSON.parse(data);
        this.model.load();
        this.model.SyncPosts = false;
    }
}

NetworkPostAccountKanbanController.components = {
    ...KanbanController.components,
    SocialNetworkAccount,
};
NetworkPostAccountKanbanController.template = "connector_social_base.KanbanView";
