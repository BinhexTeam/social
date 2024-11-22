from odoo import _, fields, models
from odoo.exceptions import UserError

from ..utils import ollama


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ollama_api_url = fields.Char(
        string="Ollama API URL",
        help="Provide the URL for the Ollama API",
        config_parameter="ollama_integration.ollama_api_url",
    )

    ollama_model = fields.Char(
        help="Specify the model for Ollama (e.g., llama3.2)",
        config_parameter="ollama_integration.ollama_model",
    )

    def action_test_ollama_connection(self):
        """Test the connection to Ollama API with the provided URL and model."""

        response = ollama.post_ollama_chat(
            api_url=self.ollama_api_url, model=self.ollama_model, prompt="Hello World"
        )
        if response:
            response_message = ollama.get_response_message_content(response)
            if response_message:
                raise UserError(
                    _(f"Connection succesfull, API responded: {str(response_message)}")
                )
            else:
                raise UserError(
                    _("Something went wrong, check the logs for more information")
                )
        else:
            raise UserError(
                _("Something went wrong, check the logs for more information")
            )
