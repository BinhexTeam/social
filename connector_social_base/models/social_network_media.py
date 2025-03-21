# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import hmac


class SocialNetworkMedia(models.Model):
    _name = "social.network.media"
    _inherit = "connector.social.base.mixin"
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
                self.env(su=True), "social_linkedin-account-csrf-token", media.id
            )

    def _action_add_account(self):
        """
        Social network modules that inherit from this one should
        override this method as needed; the method is intended
        to redirect to the social network authorization.
        """
        pass

    def _action_valid_add_account(self):
        if (
            self.env["social.network.account"].search_count(
                [("media_id", "=", self.id)]
            )
            == 0
        ):
            irConfigParameter = self.env["ir.config_parameter"].sudo()
            client_id = None
            if self.media_type == "linkedin":
                client_id = irConfigParameter.get_param(
                    f"connector_social_{self.media_type}.{self.media_type}_client", ""
                )
            elif self.media_type == "x":
                client_id = irConfigParameter.get_param(
                    f"connector_social_{self.media_type}.{self.media_type}_api_key", ""
                )
            if client_id:
                return True
            else:
                raise ValidationError(
                    _(
                        "You must provide a client ID before setting "
                        "up your account. Go to Social/Settings."
                    )
                )
        return self.env.ref(
            "connector_social_base.social_network_post_account_act_window_kanban"
        ).read()[0]

    def action_add_account(self, company_id=None):
        self.ensure_one()
        action_account = self._action_valid_add_account()
        if not isinstance(action_account, bool):
            return action_account
        return self._action_add_account()

    def _get_url_redirect(self):
        pass
