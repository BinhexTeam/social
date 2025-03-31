/** @odoo-module */

/**
 * Validate that the start date is before (or equal to) the end date.
 * @param {String} startDate - The start date in any format understood by the luxon library.
 * @param {String} endDate - The end date in any format understood by the luxon library.
 * @returns {Boolean} whether the start date is before (or equal to) the end date.
 */
export function validateRangeDate(startDate, endDate) {
    if (startDate && endDate) {
        return startDate <= endDate;
    }
    return true;
}
