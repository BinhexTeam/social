/** @odoo-module **/
import {NetworkPostAccountKanbanRecord} from "@connector_social_base/js/views/kanban/network_post_account_kanban_record.esm";
import {patch} from "@web/core/utils/patch";
import {useService} from "@web/core/utils/hooks";

patch(NetworkPostAccountKanbanRecord.prototype, {
    setup() {
        super.setup();
        this.socialLinkedinService = useService("social_linkedin_service");
    },

    async validPostExist() {
        super.validPostExist();
        return await this.socialLinkedinService.validPostLinkedinExist(
            this.record.id.raw_value
        );
    },
});
