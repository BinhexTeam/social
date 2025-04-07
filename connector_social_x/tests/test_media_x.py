# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import MagicMock, patch

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
