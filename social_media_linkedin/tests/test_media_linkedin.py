# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from unittest.mock import patch

from odoo.addons.social_media_linkedin.tests.test_common_linkedin import (
    TestSocialNetworkCommonLinkedin,
)

PATCH_UTILS = "odoo.addons.social_media_linkedin.social_linkedin_utils.{}"


class TestSocialNetworkLinkedin(TestSocialNetworkCommonLinkedin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @patch(
        PATCH_UTILS.format("_HEADERS_LINKEDIN"),
        {
            "X-Restli-Protocol-Version": "2.0.0",
            "LinkedIn-Version": "202411",
        },
    )
    def test_get_linkedin_headers_with_token_and_content_type(self):
        access_token = "fake-token"
        content_type = "application/json"
        headers = self.SocialMedia._get_linkedin_headers(access_token, content_type)

        self.assertIn("Authorization", headers)
        self.assertEqual(headers["Authorization"], f"Bearer {access_token}")
        self.assertIn("Content-Type", headers)
        self.assertEqual(headers["Content-Type"], content_type)
        self.assertIn("LinkedIn-Version", headers)
        self.assertIn("X-Restli-Protocol-Version", headers)

    def test_action_add_account_linkedin(self):
        self.SocialMediaLinkedin.media_type = "linkedin"
        self.SocialMediaLinkedin.csrf_state_token = "fake_state_token"
        result = self.SocialMediaLinkedin._action_add_account()
        self.assertEqual(result["type"], "ir.actions.act_url")
