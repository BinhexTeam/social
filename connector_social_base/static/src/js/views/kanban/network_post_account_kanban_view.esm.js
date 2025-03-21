/** @odoo-module **/

import {NetworkPostAccountKanbanController} from "./network_post_account_kanban_controller.esm";
import {NetworkPostAccountKanbanModel} from "./network_post_account_kanban_model.esm";
import {NetworkPostAccountKanbanRenderer} from "./network_post_account_kanban_renderer.esm";
import {kanbanView} from "@web/views/kanban/kanban_view";
import {registry} from "@web/core/registry";

export const NetworkPostAccountKanbanView = {
    ...kanbanView,
    Controller: NetworkPostAccountKanbanController,
    Model: NetworkPostAccountKanbanModel,
    Renderer: NetworkPostAccountKanbanRenderer,
    buttonTemplate: "NetworkPostAccountKanbanView.buttons",
};

registry.category("views").add("social_network_kanban", NetworkPostAccountKanbanView);
