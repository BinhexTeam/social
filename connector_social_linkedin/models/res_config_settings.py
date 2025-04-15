# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    linkedin_use_account = fields.Boolean(
        string="Account Linkedin",
        config_parameter="connector_social_linkedin.linkedin_use_account",
    )
    linkedin_client = fields.Char(
        string="Linkedin Client ID",
        config_parameter="connector_social_linkedin.linkedin_client",
    )
    linkedin_secret = fields.Char(
        string="Linkedin Client Secret",
        compute="_compute_linkedin_secret",
        inverse="_inverse_linkedin_secret",
    )

    @api.onchange("linkedin_use_account")
    def _onchange_linkedin_use_account(self):
        if not self.linkedin_use_account:
            self.linkedin_client = False
            self.linkedin_secret = False

    @api.depends("linkedin_use_account")
    def _compute_linkedin_secret(self):
        for record in self:
            if self.env.user.has_group("base.group_system"):
                record.linkedin_secret = (
                    self.env["ir.config_parameter"]
                    .sudo()
                    .get_param("connector_social_linkedin.linkedin_secret")
                )
            else:
                record.linkedin_secret = None

    def _inverse_linkedin_secret(self):
        for record in self:
            if self.env.user.has_group("base.group_system"):
                self.env["ir.config_parameter"].sudo().set_param(
                    "connector_social_linkedin.linkedin_secret", record.linkedin_secret
                )
