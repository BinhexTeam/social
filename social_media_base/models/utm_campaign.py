# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class UtmCampaign(models.Model):
    _inherit = "utm.campaign"

    campaign_group_id = fields.Many2one("utm.group.campaign", string="Campaign group")
