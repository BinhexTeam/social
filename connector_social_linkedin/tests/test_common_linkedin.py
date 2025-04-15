# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.fields import Command

from odoo.addons.connector_social_base.tests.test_social_common import (
    TestSocialNetworkCommon,
)

PATCH_ACCOUNT_LINKEDIN = (
    "odoo.addons.connector_social_linkedin.models."
    "social_network_account.SocialNetworkAccount.{}"
)
PATCH_POST_ACCOUNT_LINKEDIN = (
    "odoo.addons.connector_social_linkedin.models."
    "social_network_post_account.SocialNetworkPostAccount.{}"
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

        cls.SocialPostLinkedin = cls.SocialPost.create(
            {
                "message": "Test Message",
                "account_ids": [Command.set(cls.SocialAccountLinkedin.ids)],
            }
        )

        post_account = {
            "message": "Test Message",
            "account_id": cls.SocialAccountLinkedin.id,
            "media_id": cls.SocialMediaLinkedin.id,
            "post_id": cls.SocialPostLinkedin.id,
            "linkedin_post_account_urn": "1234567890",
            "state": "posted",
        }

        cls.SocialPostAccountLinkedin = cls.SocialPostAccount.create(post_account)

        post_account.update(
            {
                "state": "ready",
                "linkedin_post_account_urn": False,
            }
        )
        cls.SocialPostAccountReadyLinkedin = cls.SocialPostAccount.create(post_account)

        cls.SocialCampaignGroupLinkedin = cls.UtmGroupCampaign.create(
            {
                "name": "Campaign Group 1",
                "linkedin_urn": "urn:li:sponsoredCampaignGroup:456",
                "total_budget": 10000,
                "currency_id": cls.env.ref("base.USD").id,
            }
        )

        cls.SocialCampaignLinkedin = cls.UtmCampaign.create(
            {
                "name": "Campaign 1",
                "campaign_group_id": cls.SocialCampaignGroupLinkedin.id,
                "currency_id": cls.SocialCampaignGroupLinkedin.currency_id.id,
                "linkedin_urn": "urn:li:sponsoredCampaign:001",
            }
        )

        cls.SocialPostCampaignLinkedin = cls.SocialPost.create(
            {
                "message": "Test Message for Campaign",
                "account_ids": [Command.set(cls.SocialAccountLinkedin.ids)],
                "campaign_id": cls.SocialCampaignLinkedin.id,
            }
        )

        cls.SocialPostAccountCampaignLinkedin = cls.SocialPostAccount.create(
            {
                "message": "Test Message for Campaign",
                "account_id": cls.SocialAccountLinkedin.id,
                "media_id": cls.SocialMediaLinkedin.id,
                "post_id": cls.SocialPostCampaignLinkedin.id,
            }
        )
