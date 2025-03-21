import logging

from odoo import http
from odoo.http import request, route

_logger = logging.getLogger(__name__)


class SocialNetwork(http.Controller):
    @route(
        ["/linkedin/callback"],
        type="http",
        auth="user",
    )
    def social_linkedin(self, access_token=None, code=None, state=None, **kwargs):
        try:
            if not access_token:
                access_token = request.env[
                    "social.network.account"
                ].get_access_token_linkedin(code, request.httprequest.path)
            request.env["social.network.account"].create_account_linkedin(access_token)
        except Exception as e:
            _logger.error(e)
            return request.redirect("/web")
        return request.redirect("/")
