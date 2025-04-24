import logging

from odoo import http
from odoo.http import request, route

_logger = logging.getLogger(__name__)


class SocialMediaLinkedin(http.Controller):
    @route(
        ["/linkedin/callback"],
        type="http",
        auth="user",
    )
    def social_linkedin(self, access_token=None, code=None, **kwargs):
        try:
            if not access_token:
                access_token = request.env[
                    "social.network.account"
                ].get_access_token_linkedin(code, request.httprequest.path)
            request.env["social.network.account"].create_account_linkedin(access_token)
        except Exception as e:
            _logger.error(f"Error creating Linkedin account: {e}")
        return request.redirect("/web")

    @route(
        ["/linkedin/webhook"],
        type="http",
        auth="user",
    )
    def social_linkedin_webhook(self, **kwargs):
        _logger.error(f"WEBHOOK LINKEDIN: {kwargs}")
