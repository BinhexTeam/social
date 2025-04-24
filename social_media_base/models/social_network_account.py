# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import json

from odoo import api, fields, models


class SocialNetworkAccount(models.Model):
    _name = "social.network.account"
    _inherit = "social.media.base.mixin"
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
    comment_count = fields.Integer()
    like_count = fields.Integer()
    click_count = fields.Integer()
    share_count = fields.Integer()
    interactions_count = fields.Integer(
        compute="_compute_interactions_count",
        store=True,
        help="""
            Indicates the interactions with the
            publication (clicks, likes, comments,shares).
        """,
    )
    impression_count = fields.Integer(
        help="""
            Total number of views, which may include
            multiple views by the same user.
        """
    )
    engagement = fields.Float()

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

    @api.depends("click_count", "like_count", "share_count", "comment_count")
    def _compute_interactions_count(self):
        for account in self:
            account.interactions_count = (
                account.click_count
                + account.like_count
                + account.share_count
                + account.comment_count
            )

    def _get_chart_account_statistics(self, start_date, end_date, granularity):
        return []

    def get_chart_account_statistics(
        self, start_date=None, end_date=None, granularity="WEEK"
    ):
        return self._get_chart_account_statistics(start_date, end_date, granularity)

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
        return {}

    def load_ads_accounts(self):
        return self._load_ads_accounts()
