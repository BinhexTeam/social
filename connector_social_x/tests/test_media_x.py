# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import tweepy
from odoo.fields import Command
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch
from odoo.addons.base.tests.common import SavepointCaseWithUserDemo
from odoo.addons.connector_social_x.tests.test_common_x import (
    TestSocialNetworkCommonX,
)

PATCH_ACCOUNT_X = (
    "odoo.addons.connector_social_x.models."
    "social_network_account.SocialNetworkAccount.{}"
)
PATCH_POST_ACCOUNT_X = (
    "odoo.addons.connector_social_x.models."
    "social_network_post_account.SocialNetworkPostAccount.{}"
)

PATCH_X_UTILS = "odoo.addons.connector_social_x.social_x_utils.{}"


class TestSocialNetworkAccountX(TestSocialNetworkCommonX):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @patch("odoo.addons.connector_social_linkedin.models.social_network_account.requests.post")
    def test_get_access_token_success(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {"access_token": "fake_token"}
        mock_post.return_value = mock_response

        token = self.SocialAccountX._get_access_token_oauth2()
        self.assertEqual(token, "fake_token")
        mock_post.assert_called_once()
        self.assertIn("Authorization", mock_post.call_args[1]["headers"])

        mock_response = MagicMock()
        mock_response.json.return_value = {}
        mock_post.return_value = mock_response
        token = self.SocialAccountX._get_access_token_oauth2()
        self.assertFalse(token)

        mock_post.side_effect = Exception("Connection failed")
        with self.assertRaises(Exception) as context:
            self.SocialAccountX._get_access_token_oauth2()
        self.assertIn("Connection failed", str(context.exception))

    @patch("tweepy.Client")
    @patch(PATCH_ACCOUNT_X.format("get_client_api"))
    def test_get_client_api_v2(self, mock_tweepy_client, mock_get_client_api):
        client_mock = MagicMock()
        mock_tweepy_client.return_value = client_mock
        mock_get_client_api.api_key = "test_api_key"
        mock_get_client_api.api_secret = "test_api_secret"
        mock_get_client_api.access_token = "test_access_token"
        mock_get_client_api.access_token_secret = "test_secret_token"

        client = self.SocialAccountX.get_client_api(
            consumer_key="test_api_key",
            consumer_secret="test_api_secret",
            bearer_token="test_bearer_token",
            access_token="test_access_token",
            access_token_secret="test_secret_token",
        )

        mock_tweepy_client.assert_called_once_with(
            bearer_token="test_bearer_token",
            consumer_key="test_api_key",
            consumer_secret="test_api_secret",
            access_token="test_access_token",
            access_token_secret="test_secret_token",
        )
        self.assertEqual(client, client_mock)

    @patch("tweepy.API")
    def test_prepare_medias_for_tweet_with_base64_string(self, mock_tweepy_api):
        image_content = b"fake_image_data"
        encoded_image = base64.b64encode(image_content).decode("utf-8")
        base64_image_str = f"data:image/jpeg;base64,{encoded_image}"
        mock_api_instance = MagicMock()
        mock_api_instance.media_upload.return_value.media_id = 987654321
        mock_tweepy_api.return_value = mock_api_instance
        result = self.SocialAccountX._prepare_medias_for_tweet(image_datas=base64_image_str)
        self.assertIsInstance(result, list)
        self.assertIn(987654321, result)
        mock_api_instance.media_upload.assert_called_once()

    @patch(PATCH_ACCOUNT_X.format("_prepare_medias_for_tweet"))
    @patch("tweepy.Client")
    def test_create_tweet_success(self, mock_tweepy_client, mock_prepare_media):
        mock_prepare_media.return_value = [1111]
        mock_client_instance = MagicMock()
        mock_client_instance.create_tweet.return_value.data = {"id": "1234567890"}
        mock_tweepy_client.return_value = mock_client_instance
        message = "Test tweet message"
        image_ids = [MagicMock()]
        tweet_id = self.SocialAccountX.create_tweet(message=message, image_ids=image_ids)
        self.assertEqual(tweet_id, "1234567890")
        mock_client_instance.create_tweet.assert_called_once_with(
            text=message, media_ids=[1111]
        )
        mock_prepare_media.assert_called_once_with(image_ids)
