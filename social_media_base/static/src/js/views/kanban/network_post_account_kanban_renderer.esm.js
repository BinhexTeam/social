/** @odoo-module **/

import {KanbanRenderer} from "@web/views/kanban/kanban_renderer";
import {NetworkPostAccountKanbanRecord} from "./network_post_account_kanban_record.esm";

export class NetworkPostAccountKanbanRenderer extends KanbanRenderer {}

NetworkPostAccountKanbanRenderer.components = {
    ...KanbanRenderer.components,
    KanbanRecord: NetworkPostAccountKanbanRecord,
};
