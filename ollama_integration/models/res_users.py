from odoo import api, fields, models


class ResUsers(models.Model):

    _inherit = "res.users"

    is_ollama_bot = fields.Boolean("Is Bot User")
    ollama_model = fields.Char(help="llama3.2")

    @api.model
    def _keep_user_online(self):
        """
        Method to keep the user online by updating their presence.
        """
        bots_list = self.get_bot_users()
        for user in bots_list:
            presence = self.env["bus.presence"].search(
                [("user_id", "=", user.id)], limit=1
            )
            if presence:
                presence.sudo().write({"last_poll": fields.Datetime.now()})
            else:
                self.env["bus.presence"].sudo().create(
                    {
                        "user_id": user.id,
                        "last_poll": fields.Datetime.now(),
                    }
                )

    def get_bot_users(self):
        """
        Method to get a list of bot users.
        """
        return self.env["res.users"].search([("is_ollama_bot", "=", True)])
