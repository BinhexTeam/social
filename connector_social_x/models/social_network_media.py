# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

import requests
from werkzeug.urls import url_encode

from odoo import _, fields, models

from ..social_x_utils import _get_oauth

_logger = logging.getLogger(__name__)


class SocialMediaOca(models.Model):
    _inherit = "social.network.media"

    media_type = fields.Selection(selection_add=[("x", "X")])

    def _get_url_authorize(self):
        try:
            url = "https://api.twitter.com/oauth/request_token"
            api_key, api_secret = self._get_account_api(media_type="x")
            auth = _get_oauth(api_key, api_secret)
            response = requests.post(url, auth=auth, timeout=5)
            tokens = dict(x.split("=") for x in response.text.split("&"))
            params = {"oauth_token": tokens["oauth_token"]}
            url_aut = f"https://api.twitter.com/oauth/authorize?{url_encode(params)}"
            return {
                "type": "ir.actions.act_url",
                "url": url_aut,
                "target": "self",
            }
        except Exception as e:
            _logger.error(f"Error get url authorize {e}")
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "target": "new",
                "params": {
                    "message": _(
                        """
                        Account access could not be authorized.
                        Please check your settings or try again later.
                    """
                    ),
                    "type": "danger",
                    "sticky": False,
                    "next": {"type": "ir.actions.act_window_close"},
                },
            }

    def _action_add_account(self):
        result = super()._action_add_account()
        if self.media_type == "x":
            return self._get_url_authorize()
        else:
            return result
