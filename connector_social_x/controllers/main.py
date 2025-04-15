import logging

from odoo import http
from odoo.http import request, route

_logger = logging.getLogger(__name__)


class SocialNetwork(http.Controller):
    @route(
        ["/social_x/callback"],
        type="http",
        auth="user",
    )
    def social_x(self, **kwargs):
        try:
            access_token, access_token_secret = (
                request.env["social.network.account"].sudo()._get_access_token(kwargs)
            )
            if access_token and access_token_secret:
                request.env["social.network.account"].create_account_x(
                    access_token, access_token_secret
                )
        except Exception as e:
            _logger.error(e)
        return request.redirect("/web")
