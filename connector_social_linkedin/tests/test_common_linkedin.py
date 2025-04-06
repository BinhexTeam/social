# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.addons.connector_social_base.tests.test_social_common import (
    TestSocialNetworkCommon,
)


class TestSocialNetworkCommonLinkedin(TestSocialNetworkCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SocialMediaLinkedin = cls.SocialMedia.create(
            {
                "name": "linkedin",
                "media_type": "linkedin",
            }
        )

        cls.SocialAccountLinkedin = cls.SocialAccount.create(
            {
                "name": "Linkedin Account",
                "media_id": cls.SocialMediaLinkedin.id,
                "linkedin_account_urn": "urn:li:organization:123456",
                "access_token": "fake-token",
            }
        )
