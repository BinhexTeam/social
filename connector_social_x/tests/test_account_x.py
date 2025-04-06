# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command

from odoo.addons.connector_social_base.tests.test_social_common import (
    TestSocialNetworkCommon,
)

PATCH_ACCOUNT_X = (
    "odoo.addons.connector_social_x.models."
    "social_network_account.SocialNetworkAccount.{}"
)
PATCH_POST_ACCOUNT_X = (
    "odoo.addons.connector_social_x.models."
    "social_network_post_account.SocialNetworkPostAccount.{}"
)


class TestSocialNetworkCommonX(TestSocialNetworkCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SocialMediaX = cls.SocialMedia.create(
            {
                "name": "linkedin",
                "media_type": "x",
            }
        )

        cls.SocialAccountX = cls.SocialAccount.create(
            {
                "name": "Linkedin Account",
                "media_id": cls.SocialMediaX.id,
                "access_token": "fake-token",
            }
        )

        cls.SocialPostX = cls.SocialPost.create(
            {
                "message": "Test Message",
                "account_ids": [Command.set(cls.SocialAccountX.ids)],
            }
        )

        post_account = {
            "message": "Test Message",
            "account_id": cls.SocialAccountX.id,
            "media_id": cls.SocialMediaX.id,
            "post_id": cls.SocialPostX.id,
            "state": "posted",
        }

        cls.SocialPostAccountX = cls.SocialPostAccount.create(post_account)

        post_account.update(
            {
                "state": "ready",
            }
        )
        cls.SocialPostAccountReadyX = cls.SocialPostAccount.create(post_account)
