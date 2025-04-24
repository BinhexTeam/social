# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo.tests import TransactionCase

PATCH_SOCIAL_BASE_UTILS = "odoo.addons.social_media_base.social_utils.{}"
PATCH_SOCIAL_BAS_MODELS = "odoo.addons.social_media_base.models"
PATCH_SOCIAL_BASE_MIXIN = "{}.social_media_base_mixin.SocialMediaBaseMixin.{}".format(
    PATCH_SOCIAL_BAS_MODELS, "{}"
)


class TestSocialNetworkCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SocialMedia = cls.env["social.network.media"]
        cls.SocialAccount = cls.env["social.network.account"]
        cls.SocialPost = cls.env["social.network.post"]
        cls.SocialPostAccount = cls.env["social.network.post.account"]
        cls.UtmGroupCampaign = cls.env["utm.group.campaign"]
        cls.UtmCampaign = cls.env["utm.campaign"]
