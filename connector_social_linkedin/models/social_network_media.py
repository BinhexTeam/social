# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from werkzeug.urls import url_encode, url_join

from odoo import _, fields, models
from odoo.exceptions import ValidationError

from ..social_linkedin_utils import (
    _HEADERS_LINKEDIN,
    _SCOPE_LINKEDIN,
    _URL_AUTH_V2_LINKEDIN,
)


class SocialMediaOca(models.Model):
    _inherit = "social.network.media"

    media_type = fields.Selection(
        selection_add=[("linkedin", "Linkedin")], default="linkedin"
    )

    def _get_linkedin_headers(self, access_token=None, content_type=None):
        headers = _HEADERS_LINKEDIN
        if access_token:
            headers.update({"Authorization": "Bearer %s" % access_token})
        if content_type:
            headers.update({"Content-Type": content_type})
        return headers

    def _get_url_redirect(self):
        if self.media_type == "linkedin":
            return url_join(self.get_base_url(), "/linkedin/callback")
        else:
            return super()._get_url_redirect()

    def _action_add_account(self):
        result = super()._action_add_account()
        if self.media_type == "linkedin":
            api_client, api_secret = self._get_account_api(media_type="linkedin")
            params = {
                "response_type": "code",
                "client_id": api_client,
                "redirect_uri": self._get_url_redirect(),
                "state": self.csrf_state_token,
                "scope": " ".join(_SCOPE_LINKEDIN),
            }
            url_aut = f"{_URL_AUTH_V2_LINKEDIN}/authorization?{url_encode(params)}"
            return {
                "type": "ir.actions.act_url",
                "url": url_aut,
                "target": "self",
            }
        else:
            return result

    def _action_valid_add_account(self):
        result = super()._action_valid_add_account()
        if self.media_type == "linkedin":
            if self._get_account_by_media() == 0:
                irConfigParameter = self.env["ir.config_parameter"].sudo()
                client_id = irConfigParameter.get_param(
                    f"connector_social_{self.media_type}.{self.media_type}_client", ""
                )
                if client_id:
                    result = False
                else:
                    raise ValidationError(
                        _(
                            """
                                You must provide a Client ID and Client secret
                                before setting up your account.
                                Go to Social/Settings.
                            """
                        )
                    )
            else:
                result = True
        return result
