# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime
from unittest.mock import MagicMock, patch

from odoo.exceptions import ValidationError

from odoo.addons.social_media_x.tests.test_common_x import (
    PATCH_ACCOUNT_X,
    TestSocialCommonX,
)


class TestSocialPostAccountX(TestSocialCommonX):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.test_response_errors = ["Error 1", "Error 2"]

    def test_create_x_comment(self):
        mock_client = MagicMock()
        with patch.object(
            type(self.SocialAccountX), "get_client_api", return_value=mock_client
        ) as mock_get_client_api, patch.object(
            type(self.SocialAccountX),
            "_prepare_medias_for_tweet",
            return_value=mock_client,
        ) as mock_medias_for_tweet:
            post_data = {
                "body": "Test Comment",
                "attachment_ids": [1],
            }
            self.SocialPostAccountX.create_x_comment(post_data)
            mock_medias_for_tweet.assert_called_once()
            self.assertEqual(mock_get_client_api.call_count, 1)

    def test_create_comment(self):
        mock_client = MagicMock()
        with patch.object(
            type(self.SocialPostAccountX), "create_x_comment", return_value=mock_client
        ) as mock_create_comment:
            post_data = {
                "body": "Test Comment",
                "attachment_ids": [1],
            }
            self.SocialPostAccountX.create_comment(post_data)
            mock_create_comment.assert_called_once()

    def test_compute_post_statistics_x(self):
        post_account_values = {
            "post_id": self.SocialPostX.id,
            "account_id": self.SocialAccountX.id,
            "message": "Message Test XX",
            "click_count": 5,
            "comment_count": 2,
            "retweet_count": 3,
            "quote_count": 2,
        }
        self.SocialPostAccount.create(post_account_values)
        post_account_values.update(
            {
                "message": "Message Test X",
                "click_count": 5,
                "comment_count": 1,
                "retweet_count": 5,
                "quote_count": 1,
            }
        )
        self.SocialPostAccount.create(post_account_values)
        expected = (5 + 5) + (2 + 1) + (3 + 5) + (2 + 1)
        self.assertEqual(self.SocialPostX.count_post_interactions, expected)

    @patch(PATCH_ACCOUNT_X.format("SocialAccount.get_client_api"))
    @patch(
        "odoo.addons.social_media_base.models.social_post_account.SocialPostAccount._delete_post_account"
    )
    @patch(PATCH_ACCOUNT_X.format("SocialAccount._valid_time_request"))
    def test_delete_post_account(
        self, mock_valid_time_request, mock_delete_post_account, mock_get_client_api
    ):
        mock_get_client_api.delete_tweet.return_value = True
        mock_valid_time_request.return_value = True
        self.SocialPostAccountX._delete_post_account()
        mock_delete_post_account.assert_called_once()

    def test_delete_post_account_raises_response_errors(self):
        post_account = self.SocialPostAccountX
        self.assertTrue(post_account)
        self.assertEqual(post_account.media_id.media_type, "x")
        post_account.write({"x_post_account_id": "123"})
        fake_client = MagicMock()
        fake_response = MagicMock()
        fake_response.errors = self.test_response_errors
        fake_client.delete_tweet.return_value = fake_response
        with patch.object(
            type(post_account.account_id),
            "_valid_time_request",
            autospec=True,
            return_value=True,
        ), patch.object(
            type(post_account.account_id),
            "get_client_api",
            autospec=True,
            return_value=fake_client,
        ):
            with self.assertRaises(ValidationError) as ctx:
                post_account._delete_post_account()

        self.assertIn("Error 1, Error 2", str(ctx.exception))
        fake_client.delete_tweet.assert_called_once_with("123")

    def test_get_assets_save_x(self):
        fake_medias = ["media1"]
        media_map = {"media1": ("media_key1", "www.media_url_1", "media_type1")}
        attachment = self.env["ir.attachment"].create(
            {
                "name": "media_key1",
                "type": "binary",
                "res_model": self.SocialPostAccountX._name,
                "res_id": self.SocialPostAccountX.id,
                "datas": self.image_base64,
            }
        )
        with patch.object(
            type(self.SocialPostAccount),
            "_map_medias_account",
            autospec=True,
            return_value=attachment,
        ) as mock_map_medias:
            attachments = self.SocialPostAccountX._get_assets_save_x(
                fake_medias, media_map
            )
            self.assertEqual(len(attachments), 1)
            self.assertEqual(attachments[0]["type"], "binary")
            self.assertEqual(attachments[0]["res_model"], self.SocialPostAccountX._name)
            self.assertEqual(attachments[0]["res_id"], self.SocialPostAccountX.id)
            mock_map_medias.assert_called_once()

    def test_get_assets_save_x_failed(self):
        fake_medias = ["media1"]
        media_map = {"media1": ("media_key1", "www.media_url_1", "media_type1")}
        with patch.object(
            type(self.SocialPostAccount),
            "_get_medias_account",
            autospec=True,
            return_value=["media1"],
        ) as mock_get_medias:
            attachments = self.SocialPostAccountX._get_assets_save_x(
                fake_medias, media_map
            )
            self.assertEqual(len(attachments), 0)
            mock_get_medias.assert_called_once()

    @patch(PATCH_ACCOUNT_X.format("SocialAccount.get_client_api"))
    @patch(
        "odoo.addons.social_media_x.models.social_post_account.SocialPostAccount.get_post_x"
    )
    @patch(PATCH_ACCOUNT_X.format("SocialAccount._valid_time_request"))
    def test_get_post_x(
        self, mock_valid_time_request, mock_get_post_x, mock_get_client_api
    ):
        mock_get_client_api.get_tweet.return_value = True
        mock_valid_time_request.return_value = True
        self.SocialPostAccountX.get_post_x()
        mock_get_post_x.assert_called_once()

    def test_get_post_x_raises_response_errors(self):
        post_account = self.SocialPostAccountX
        self.assertTrue(post_account)
        self.assertEqual(post_account.media_id.media_type, "x")
        post_account.write({"x_post_account_id": "123"})
        fake_client = MagicMock()
        fake_response = MagicMock()
        fake_response.errors = self.test_response_errors
        fake_client.get_tweet.return_value = fake_response
        with patch.object(
            type(post_account.account_id),
            "_valid_time_request",
            autospec=True,
            return_value=True,
        ), patch.object(
            type(post_account.account_id),
            "get_client_api",
            autospec=True,
            return_value=fake_client,
        ):
            with self.assertRaises(ValidationError) as ctx:
                post_account.get_post_x()

        self.assertIn("Error 1, Error 2", str(ctx.exception))

    def test_get_comments(self):
        now = datetime.now()
        fake_comment = MagicMock()
        fake_comment.id = "comment_id1"
        fake_comment.text = "Comment 1"
        fake_comment.author_id = "author_1"
        fake_comment.created_at = now
        fake_user = MagicMock()
        fake_user.id = "author_1"
        fake_user.created_at = now
        fake_user.profile_image_url = "https://www.fake.media/url_image"
        fake_response = MagicMock()
        fake_response.data = [fake_comment]
        fake_response.includes = {"users": [fake_user]}
        fake_response.errors = self.test_response_errors
        fake_client = MagicMock()
        fake_client.search_recent_tweets.return_value = fake_response
        with patch.object(
            type(self.SocialPostAccountX.account_id),
            "_valid_time_request",
            autospec=True,
            return_value=True,
        ), patch.object(
            type(self.SocialPostAccountX.account_id),
            "get_client_api",
            autospec=True,
            return_value=fake_client,
        ):
            comments = self.SocialPostAccountX.get_comments()
            self.assertEqual(len(comments["data"]), 1)
            self.assertEqual(comments["data"][0]["id"], "comment_id1")
            self.assertEqual(comments["data"][0]["text"], "Comment 1")

    def test_action_post(self):
        self.SocialPostAccountX.write({"state": "ready"})
        with patch.object(
            type(self.SocialPostX),
            "filter_by_media_types",
            autospec=True,
            return_value=self.SocialPostAccountX,
        ) as mock_filter_by_media_types, patch.object(
            type(self.SocialPostAccountX.account_id),
            "create_tweet",
            autospec=True,
            return_value="122809890045",
        ) as mock_create_tweet:
            self.SocialPostAccountX._action_post(self.SocialPostX)
            self.assertEqual(self.SocialPostAccountX.x_post_account_id, "122809890045")
            self.assertEqual(self.SocialPostAccountX.state, "posted")
            self.assertIn(
                self.SocialPostAccountX.account_id.username,
                self.SocialPostAccountX.post_account_url,
            )
            mock_filter_by_media_types.assert_called_once()
            mock_create_tweet.assert_called_once()

    def test_action_post_failed(self):
        self.SocialPostAccountX.write({"state": "ready"})
        with patch.object(
            type(self.SocialPostX),
            "filter_by_media_types",
            autospec=True,
            return_value=self.SocialPostAccountX,
        ) as mock_filter_by_media_types, patch.object(
            type(self.SocialPostAccountX.account_id),
            "create_tweet",
            autospec=True,
            return_value=False,
        ) as mock_create_tweet:
            self.SocialPostAccountX._action_post(self.SocialPostX)
            self.assertEqual(self.SocialPostAccountX.state, "failed")
            mock_filter_by_media_types.assert_called_once()
            mock_create_tweet.assert_called_once()
