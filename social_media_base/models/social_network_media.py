# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models
from odoo.tools import hmac


class SocialNetworkMedia(models.Model):
    _name = "social.network.media"
    _inherit = "social.media.base.mixin"
    _description = "Social Media"

    """
        This model defines social networks.
    """

    name = fields.Char()
    description = fields.Text()
    media_type = fields.Selection(
        [],
        readonly=True,
    )
    csrf_state_token = fields.Char(
        "CSRF Token",
        compute="_compute_csrf_state_token",
    )
    image = fields.Binary()

    def _compute_csrf_state_token(self):
        for media in self:
            media.csrf_state_token = hmac(
                self.env(su=True),
                f"social_media_{media.media_type}-account-csrf-token",
                media.id,
            )

    def _action_add_account(self):
        """
        Social network modules that inherit from this one should
        override this method as needed; the method is intended
        to redirect to the social network authorization.
        """
        pass

    def _action_valid_add_account(self):
        return True

    def action_add_account(self):
        action_account = self._action_valid_add_account()
        if action_account:
            return self.env.ref(
                "social_media_base.social_network_post_account_act_window_kanban"
            ).read()[0]
        return self._action_add_account()

    def _get_url_redirect(self):
        pass
