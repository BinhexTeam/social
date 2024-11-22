import json
import logging

import requests

_logger = logging.getLogger(__name__)


def post_ollama_message(
    api_url, endpoint, model, prompt, role="user", stream=False, options=None
):

    if not all([api_url, endpoint, model, prompt]):
        _logger.error(
            "At least one parameter has not been set (api_url, "
            "endpoint, model, prompt) when calling post_ollama_message"
        )
        return False
    else:
        request_data = {
            "model": model,
            "messages": [{"role": role, "content": prompt}],
            "stream": False,
            "options": options,
        }
        try:
            response = requests.post(api_url + endpoint, json=request_data, timeout=10)
            if response.status_code == 200:
                response.raise_for_status()
                json_response = response.json()
                return json_response
            else:
                _logger.error(
                    f"Connection error, status code {str(response.status_code)}"
                )
                return False
        except requests.exceptions.RequestException as e:
            _logger.error(f"Ollama connection has failed due to {str(e)}")
            return False
        except json.JSONDecodeError as e:
            _logger.error(f"Error decoding JSON due to {str(e)}")
            return False


def get_response_message_content(response):
    message = response.get("message", False)
    if message:
        content = message.get("content", False)
        if content:
            return content
        else:
            _logger.error("No message content received from Ollama")
            return False
    else:
        _logger.error("No message received from Ollama")
        return False


def post_ollama_chat(api_url, model, prompt, role="user", stream=False, options=None):
    return post_ollama_message(api_url, "/api/chat", model, prompt)


def post_ollama_generate(
    api_url, model, prompt, role="user", stream=False, options=None
):
    return post_ollama_message(api_url, "/api/generate", model, prompt)
