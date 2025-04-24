/** @odoo-module */

export const SocialNetworkMixin = (T) =>
    class extends T {
        /**
         * Validates whether the start date is less than or equal to the end date.
         *
         * @param {Date} startDate - The starting date of the range.
         * @param {Date} endDate - The ending date of the range.
         * @returns {Boolean} - Returns true if both dates are provided and the start date
         *                      is less than or equal to the end date, otherwise returns true
         *                      if either date is not provided.
         */
        validateRangeDate(startDate, endDate) {
            if (startDate && endDate) {
                return startDate <= endDate;
            }
            return true;
        }
    };
