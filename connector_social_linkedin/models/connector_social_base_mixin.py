# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class ConnectorSocialBaseMixin(models.AbstractModel):
    _inherit = "connector.social.base.mixin"

    def _get_account_api(self, media_type):
        res = super()._get_account_api(media_type)
        irConfigParameter = self.env["ir.config_parameter"].sudo()
        if media_type == "linkedin":
            client_id = irConfigParameter.get_param(
                f"connector_social_{media_type}.{media_type}_client", ""
            )
            client_secret = irConfigParameter.get_param(
                f"connector_social_{media_type}.{media_type}_secret", ""
            )
            return client_id, client_secret
        return res
