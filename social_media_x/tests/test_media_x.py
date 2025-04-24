# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.social_media_x.tests.test_common_x import (
    PATCH_MEDIA_X,
    TestSocialNetworkCommonX,
)


class TestSocialNetworkMediaX(TestSocialNetworkCommonX):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

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
