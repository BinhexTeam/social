import logging

from odoo import _, api, models

from ..utils import ollama

_logger = logging.getLogger(__name__)


class Channel(models.Model):
    _inherit = "mail.channel"

    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, *, message_type="notification", **kwargs):
        message = super(
            Channel,
            self.with_context(mail_create_nosubscribe=True, mail_post_autofollow=False),
        ).message_post(message_type=message_type, **kwargs)

        message_author_id = message.author_id.id if message.author_id else None

        prompt = message.body

        if not prompt:
            return message

        message_channel_id = self.env["mail.channel"].browse(message.res_id)
        message_recipient_ids = message_channel_id.channel_member_ids.filtered(
            lambda m: m.partner_id.id != message_author_id
        )
        message_recipient_partner_ids = message_recipient_ids.mapped("partner_id.id")

        if (
            message_author_id
            not in self.env["res.partner"].get_ollama_bot_partners().ids
            and not self.env["res.users"]
            .search([("partner_id", "=", message_author_id)], limit=1)
            .is_ollama_bot
        ):
            for recipient in message_recipient_partner_ids:
                recipient_user = self.env["res.users"].search(
                    [("partner_id", "=", recipient)], limit=1
                )
                if not recipient_user.is_ollama_bot:
                    continue
                else:
                    self.with_delay()._get_ollama_response_task(
                        self.id, prompt, recipient_user.id
                    )

        return message

    @api.model
    def _get_ollama_response_task(self, channel_id, prompt, user_id):
        """Método encolado para obtener la respuesta de Ollama."""

        target_channel = self.browse(channel_id)
        user = self.env["res.users"].browse(user_id)

        api_url = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("ollama_integration.ollama_api_url")
        )
        model = user.ollama_model or self.env["ir.config_parameter"].sudo().get_param(
            "ollama_integration.ollama_model"
        )

        response = ollama.post_ollama_chat(api_url, model, prompt)
        if response:
            response_message = ollama.get_response_message_content(response)
            if not response_message:
                response_message = _(
                    "I wasn't able to communicate with Ollama this time,"
                    "please ask you provider to check the logs for more details"
                )
        else:
            response_message = _(
                "I wasn't able to communicate with Ollama this time, please ask"
                " you provider to check the logs for more details"
            )

        message = target_channel.with_user(user).message_post(
            body=response_message,
            message_type="comment",
            subtype_xmlid="mail.mt_comment",
        )
        self.env["bus.bus"]._sendone(
            (self._cr.dbname, "mail.channel", channel_id),
            "new_message",
            {"type": "new_message", "message_id": message.id},
        )
