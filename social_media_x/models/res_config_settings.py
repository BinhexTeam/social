# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    x_use_account = fields.Boolean(
        string="Account x",
        config_parameter="social_media_x.x_use_account",
    )
    x_api_key = fields.Char(
        string="API Key",
        config_parameter="social_media_x.x_api_key",
    )
    x_api_secret = fields.Char(
        string="API Secret",
        compute="_compute_x_api_secret",
        inverse="_inverse_x_api_secret",
    )

    @api.onchange("x_use_account")
    def _onchange_x_use_account(self):
        if not self.x_use_account:
            self.x_api_key = False
            self.x_api_secret = False

    @api.depends("x_use_account")
    def _compute_x_api_secret(self):
        for record in self:
            if self.env.user.has_group("base.group_system"):
                record.x_api_secret = (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("social_media_x.x_api_secret")
                )
            else:
                record.x_api_secret = None

    def _inverse_x_api_secret(self):
        for record in self:
            if self.env.user.has_group("base.group_system"):
                self.env["ir.config_parameter"].sudo().set_param(
                    "social_media_x.x_api_secret", record.x_api_secret
                )
