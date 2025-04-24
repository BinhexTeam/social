# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class SocialMediaBaseMixin(models.AbstractModel):
    _name = "social.media.base.mixin"
    _description = "Social Media Base Mixin"

    def _get_account_api(self, media_type):
        return False, False

    def _get_account_by_media(self):
        return self.env["social.network.account"].search_count(
            [("media_id", "=", self.id)]
        )
