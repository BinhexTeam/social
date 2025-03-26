# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

_logger = logging.getLogger(__name__)


class UtmCampaign(models.Model):
    _inherit = "utm.campaign"

    linkedin_urn = fields.Char(string="Linkedin URN", copy=False)
    campaign_group_id = fields.Many2one(
        "utm.group.campaign", string="Campaign group", required=True
    )
    media_id = fields.Many2one("social.network.media", string="Media", required=True)
    account_id = fields.Many2one(
        "social.network.account", string="Account", required=True
    )
    unit_cost = fields.Float(help="Cost per post", required=True)
    daily_budget = fields.Float(help="Maximum daily campaign spending", required=True)
    currency_id = fields.Many2one(
        "res.currency", related="campaign_group_id.currency_id", required=True
    )

    @api.constrains("daily_budget")
    def _check_daily_budget(self):
        for campaign in self:
            if campaign.campaign_group_id.total_budget < sum(
                campaign.campaign_group_id.campaign_ids.mapped("daily_budget")
            ):
                raise ValidationError(
                    _(
                        """The amount you want to add exceeds
                        the campaign group limit."""
                    )
                )
