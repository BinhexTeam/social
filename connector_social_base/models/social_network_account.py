# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models
from odoo.tools import float_is_zero


class SocialNetworkAccount(models.Model):
    _name = "social.network.account"
    _inherit = "connector.social.base.mixin"
    _description = "Social Account"

    """
        This model defines the accounts associated with the different social networks.
    """

    name = fields.Char()
    active = fields.Boolean(default=True)
    username = fields.Char()
    media_id = fields.Many2one("social.network.media", ondelete="restrict")
    media_type = fields.Selection(related="media_id.media_type")
    company_id = fields.Many2one(
        "res.company", "Company", default=lambda self: self.env.company
    )
    advertising_account_id = fields.Char()
    post_account_ids = fields.One2many("social.network.post.account", "account_id")

    # STATISTICS
    interactions_count = fields.Integer(
        help="""
            Indicates the interactions with the
            publication (clicks, likes, comments,shares).
        """
    )
    total_views = fields.Integer(
        help="""
            Total number of views, which may include
            multiple views by the same user.
        """
    )
    engagement_rate = fields.Float(compute="_compute_engagement_rate", store=True)
    account_url = fields.Char(compute="_compute_account_url", store=True)
    enviroment = fields.Selection(
        [("test", "Test"), ("production", "Production")], default="test"
    )

    # SECURITY
    access_token = fields.Char()
    refresh_access_token = fields.Char()
    is_valid_token_access = fields.Boolean(default=False)
    expire_access_token_date = fields.Date()

    def _compute_display_name(self):
        for account in self:
            account.display_name = (
                f"[{account.media_type.upper()}] {account.name}"
                if account.media_type
                else account.name
            )

    def _fields_account_url(self):
        return []

    @api.depends(lambda self: [val[0] for val in self._fields_account_url()])
    def _compute_account_url(self):
        for account in self:
            for val_url in account._fields_account_url():
                account.account_url = (
                    val_url[1] if account.media_id.media_type in val_url[0] else ""
                )

    @api.depends("interactions_count", "total_views")
    def _compute_engagement_rate(self):
        for account in self:
            account.engagement_rate = float_is_zero(
                account.interactions_count / account.total_views
                if account.total_views > 0
                else 0,
                2,
            )

    def _update_posts_statistics(self, update_all_accounts):
        return []

    def update_posts_statistics(self, update_all_accounts=False):
        """
        Update posts and  statistics
        """
        return json.dumps(self._update_posts_statistics(update_all_accounts))

    def validate_active_access_token(self):
        pass

    def _load_ads_accounts(self):
        return []

    def load_ads_accounts(self):
        return self._load_ads_accounts()

    def _load_campaigns_accounts(self):
        return []

    def load_campaigns_accounts(self):
        return self._load_campaigns_accounts()
