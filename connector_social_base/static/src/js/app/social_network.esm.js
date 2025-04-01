/** @odoo-module */

export const SocialNetworkMixin = (T) =>
  class extends T {
    /**
     * Validates that the start date is before or equal to the end date.
     * If the dates are invalid, it displays a notification and clears the input values.
     */
    validateRangeDate(startDate, endDate) {
      if (startDate && endDate) {
        return startDate <= endDate;
      }
      return true;
    }
  };
