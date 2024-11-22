from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def get_ollama_bot_partners(self):
        bot_users = self.env["res.users"].get_bot_users()
        return self.env["res.partner"].search([("user_id", "in", bot_users.ids)])
