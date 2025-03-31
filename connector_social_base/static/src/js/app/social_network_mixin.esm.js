/** @odoo-module */
import {_t} from "@web/core/l10n/translation";

export const SocialNetworkMixin = (T) =>
    class extends T {
        validateRangeDate(startDate,endDate) {
            if (startDate && endDate) {
                if (startDate > endDate) {
                    this.notification.add(_t("Start date must be less than end date."), {
                        type: "danger",
                        fast: true,
                    });
                    startDate.val("");
                }
            }
        }
    };
