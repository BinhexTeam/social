/** @odoo-module **/

import {onWillStart, useSubEnv} from "@odoo/owl";
import {KanbanController} from "@web/views/kanban/kanban_controller";
import {SocialNetworkAccount} from "@connector_social_base/components/components.esm";
import {_t} from "@web/core/l10n/translation";
import {useService} from "@web/core/utils/hooks";

export class NetworkPostAccountKanbanController extends KanbanController {
    setup() {
        super.setup();
        this.actionService = useService("action");
        this.model.SyncPosts = false;
        onWillStart(async () => {
            // Await this._onUpdatePostsAndStatistics();
            this.socialAccounts = await this.model._loadAccounts();
        });
        useSubEnv({
            model: this.model,
        });
    }

    get isViewPostNetwork() {
        return this.model.config.resModel === "social.network.post";
    }

    _onAddAccount() {
        return this.actionService.doAction(
            "connector_social_base.social_media_act_window_kanban"
        );
    }

    _onAddPost() {
        return this.actionService.doAction({
            name: _t("New Post"),
            type: "ir.actions.act_window",
            res_model: "social.network.post",
            views: [[false, "form"]],
        });
    }

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
