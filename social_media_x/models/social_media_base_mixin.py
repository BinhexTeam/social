# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class SocialMediaBaseMixin(models.AbstractModel):
    _inherit = "social.media.base.mixin"

    def _get_account_api(self, media_type):
        res = super()._get_account_api(media_type)
        irConfigParameter = self.env["ir.config_parameter"].sudo()
        if media_type == "x":
            api_key = irConfigParameter.get_param(
                f"social_media_{media_type}.{media_type}_api_key", ""
            )
            api_secret = irConfigParameter.get_param(
                f"social_media_{media_type}.{media_type}_api_secret", ""
            )
            return api_key, api_secret
        return res
