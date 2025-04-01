# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


from odoo import models


class ConnectorSocialBaseMixin(models.AbstractModel):
    _name = "connector.social.base.mixin"
    _description = "Connector Social Base Mixin"

    def _get_account_api(self, media_type):
        irConfigParameter = self.env["ir.config_parameter"].sudo()
        if media_type == "linkedin":
            client_id = irConfigParameter.get_param(
                f"connector_social_{media_type}.{media_type}_client", ""
            )
            client_secret = irConfigParameter.get_param(
                f"connector_social_{media_type}.{media_type}_secret", ""
            )
            return client_id, client_secret
        elif media_type == "x":
            api_key = irConfigParameter.get_param(
                f"connector_social_{media_type}.{media_type}_api_key", ""
            )
            api_secret = irConfigParameter.get_param(
                f"connector_social_{media_type}.{media_type}_api_secret", ""
            )
            return api_key, api_secret

    def _get_account_by_media(self):
        return self.env["social.network.account"].search_count(
            [("media_id", "=", self.id)]
        )
