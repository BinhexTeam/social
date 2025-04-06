# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import MagicMock, patch

from odoo.addons.connector_social_base.tests.test_social_common import (
    PATCH_SOCIAL_BASE_MIXIN,
)
from odoo.addons.connector_social_x.tests.test_common_x import (
    PATCH_MEDIA_X,
    TestSocialNetworkCommonX,
)


class TestSocialNetworkMediaX(TestSocialNetworkCommonX):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @patch(
        "odoo.addons.connector_social_linkedin.models.social_network_account.requests.post"
    )
    def test_get_url_authorize_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.text = "oauth_token=test_token&oauth_token_secret=secret"
        mock_post.return_value = mock_response
        result = self.SocialMediaX._get_url_authorize()
        self.assertEqual(result["type"], "ir.actions.act_url")
        self.assertIn("url", result)
        self.assertIn("oauth_token=test_token", result["url"])
        self.assertEqual(result["target"], "self")

        mock_post.side_effect = Exception("Error simulated")
        result = self.SocialMediaX._get_url_authorize()
        self.assertEqual(result["type"], "ir.actions.client")
        self.assertEqual(result["tag"], "display_notification")
        self.assertEqual(result["target"], "new")
        self.assertIn("message", result["params"])
        self.assertEqual(result["params"]["type"], "danger")

    @patch(PATCH_MEDIA_X.format("_get_url_authorize"))
    def test_action_add_account_x(self, mock_get_url_authorize):
        mock_get_url_authorize.return_value = {
            "type": "ir.actions.act_url",
            "url": "https://api.twitter.com/oauth/authorize?oauth_token=test_token",
            "target": "self",
        }

        result = self.SocialMediaX._action_add_account()
        self.assertEqual(result["type"], "ir.actions.act_url")
        self.assertIn("oauth_token=test_token", result["url"])

    @patch(PATCH_SOCIAL_BASE_MIXIN.format("_get_account_by_media"))
    @patch(PATCH_SOCIAL_BASE_MIXIN.format("_get_account_api"))
    def test_action_valid_add_account_x_no_account(
        self, mock_get_account_api, mock_get_account_by_media
    ):
        mock_get_account_by_media.return_value = 0
        mock_get_account_api.return_value = "api_key"
        result = self.SocialMediaX._action_valid_add_account()
        self.assertFalse(result)
