/** @odoo-module */
import {Component, useRef} from "@odoo/owl";
import {SocialNetworkMixin} from "./social_network_mixin.esm";
import {_t} from "@web/core/l10n/translation";

export class SocialNetwork extends SocialNetworkMixin(Component) {
    /**
     * Set up the component, hooking up the references to the `start_date` and
     * `end_date` inputs.
     *
     * @override
     */
    setup() {
        super.setup();
        this.startDate = useRef("start_date");
        this.endDate = useRef("end_date");
    }

    /**
     * Checks if the start date is less than the end date
     * If not, it will show a notification and reset the start and end date fields.
     */
    onValidateRangeDate() {
        const valid_date = this.validateRangeDate(
            this.startDate.el.value,
            this.endDate.el.value
        );
        if (!valid_date) {
            this.env.services.notification.add(
                _t("Start date must be less than end date."),
                {
                    type: "danger",
                    fast: true,
                }
            );
            this.startDate.el.value = "";
            this.endDate.el.value = "";
        }
    }
}
