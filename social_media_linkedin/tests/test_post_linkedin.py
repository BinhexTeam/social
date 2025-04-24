# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from unittest.mock import MagicMock, patch

from odoo.exceptions import ValidationError

from odoo.addons.social_media_base.tests.test_social_common import (
    PATCH_SOCIAL_BASE_UTILS,
)
from odoo.addons.social_media_linkedin.tests.test_common_linkedin import (
    PATCH_ACCOUNT_LINKEDIN,
    PATCH_POST_ACCOUNT_LINKEDIN,
    TestSocialNetworkCommonLinkedin,
)


class TestSocialPostLinkedin(TestSocialNetworkCommonLinkedin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

    @patch(
        "odoo.addons.social_media_linkedin.models.social_network_account.requests.get"
    )
    def test_get_assets_save(self, mock_get):
        fake_content = b"fake image data"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.content = fake_content
        mock_get.return_value = mock_response
        media_1 = {
            "media": "test_image.jpg",
            "originalUrl": "https://fake-url.com/test_image.jpg",
        }
        self.env["ir.attachment"].create(
            {
                "name": "existing_image.jpg",
                "type": "binary",
                "datas": base64.b64encode(b"existing").decode(),
            }
        )
        share_content = {
            "media": [
                media_1,
                {
                    "media": "existing_image.jpg",
                    "originalUrl": "https://fake-url.com/existing_image.jpg",
                },
            ]
        }
        with patch.object(
            type(self.SocialAccountLinkedin),
            "_request_linkedin",
            return_value=mock_response,
        ):
            attachments = self.SocialPostAccountLinkedin._get_assets_save(share_content)
        self.assertEqual(len(attachments), 1)
        self.assertEqual(attachments[0][2]["name"], "test_image.jpg")
        self.assertEqual(attachments[0][2]["datas"], base64.b64encode(fake_content))

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    def test_linkedin_advertising_accounts_success(self, mock_request_linkedin):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "paging": {"total": 1},
            "elements": [{"id": 123, "test": True}],
        }
        mock_request_linkedin.return_value = mock_response
        ad_account_id = self.SocialPostAccountLinkedin._linkedin_advertising_accounts()
        self.assertEqual(ad_account_id, "urn:li:sponsoredAccount:123")
        mock_request_linkedin.assert_called_once()

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    def test_linkedin_advertising_accounts_error(self, mock_request_linkedin):
        mock_response = MagicMock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"message": "Unauthorized"}
        mock_request_linkedin.return_value = mock_response
        with self.assertRaises(Exception) as context:
            self.SocialPostAccountLinkedin._linkedin_advertising_accounts()
        self.assertIn(
            "Error get advertising account in Linkedin", str(context.exception)
        )

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_linkedin_advertising_accounts"))
    def test_existing_campaign_group(self, mock_ad_accounts, mock_request):
        mock_ad_accounts.return_value = "urn:li:sponsoredAccount:123"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        urn = self.SocialPostAccountCampaignLinkedin._action_campaign_group()
        self.assertEqual(urn, "urn:li:sponsoredCampaignGroup:456")

    @patch(PATCH_SOCIAL_BASE_UTILS.format("_generate_timestamps"))
    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_linkedin_advertising_accounts"))
    def test_create_new_campaign_group(
        self, mock_ad_accounts, mock_request, mock_timestamps
    ):
        mock_ad_accounts.return_value = "urn:li:sponsoredAccount:999"
        mock_request.side_effect = [
            MagicMock(status_code=404),
            MagicMock(status_code=201, headers={"Location": "/adCampaignGroupsV2/456"}),
        ]
        mock_timestamps.return_value = (111111, 222222)
        urn = self.SocialPostAccountCampaignLinkedin._action_campaign_group()
        self.assertEqual(urn, "urn:li:sponsoredCampaignGroup:456")
        self.assertEqual(
            self.SocialCampaignGroupLinkedin.linkedin_urn,
            "urn:li:sponsoredCampaignGroup:456",
        )

    #
    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_linkedin_advertising_accounts"))
    def test_campaign_group_error(self, mock_ad_accounts, mock_request):
        mock_ad_accounts.return_value = "urn:li:sponsoredAccount:111"
        mock_request.side_effect = [
            MagicMock(status_code=404),
            MagicMock(status_code=400, json=lambda: {"error": "Invalid request"}),
        ]
        with self.assertRaises(ValidationError) as e:
            self.SocialPostAccountCampaignLinkedin._action_campaign_group()
        self.assertIn("Error creating group campaign in Linkedin", str(e.exception))

    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_linkedin_advertising_accounts"))
    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_action_campaign_group"))
    def test_existing_campaign(self, mock_group, mock_request, mock_ad_account):
        mock_group.return_value = "urn:li:sponsoredCampaignGroup:123"
        mock_ad_account.return_value = "urn:li:sponsoredAccount:999"
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response

        urn = self.SocialPostAccountCampaignLinkedin._action_campaign()
        self.assertEqual(urn, "urn:li:sponsoredCampaign:001")

    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_linkedin_advertising_accounts"))
    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_action_campaign_group"))
    def test_create_new_campaign(self, mock_group, mock_request, mock_ad_account):
        mock_group.return_value = "urn:li:sponsoredCampaignGroup:123"
        mock_ad_account.return_value = "urn:li:sponsoredAccount:999"
        mock_request.side_effect = [
            MagicMock(status_code=404),
            MagicMock(status_code=201, headers={"Location": "/adCampaignsV2/001"}),
        ]
        urn = self.SocialPostAccountCampaignLinkedin._action_campaign()
        self.assertEqual(urn, "urn:li:sponsoredCampaign:001")
        self.assertEqual(
            self.SocialCampaignLinkedin.linkedin_urn, "urn:li:sponsoredCampaign:001"
        )

    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_linkedin_advertising_accounts"))
    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_action_campaign_group"))
    def test_error_creating_campaign(self, mock_group, mock_request, mock_ad_account):
        mock_group.return_value = "urn:li:sponsoredCampaignGroup:456"
        mock_ad_account.return_value = "urn:li:sponsoredAccount:000"
        mock_request.side_effect = [
            MagicMock(status_code=404),
            MagicMock(status_code=400, json=lambda: {"error": "Bad Request"}),
        ]
        with self.assertRaises(ValidationError) as ctx:
            self.SocialPostAccountCampaignLinkedin._action_campaign()
        self.assertIn("Error creating campaign in Linkedin", str(ctx.exception))

    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_action_campaign_post"))
    @patch(PATCH_ACCOUNT_LINKEDIN.format("create_restclient_linkedin"))
    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_action_post"), autospec=True)
    def test_action_post_success(
        self, mock_super_post, mock_create_post, mock_campaign_post
    ):
        mock_super_post.return_value = True
        mock_create_post.return_value = "1234567890"
        mock_campaign_post.return_value = "999"
        with patch.object(
            type(self.SocialPostAccountLinkedin),
            "filter_by_media_types",
            return_value=self.SocialPostAccount.browse(
                self.SocialPostAccountLinkedin.id
            ),
        ):
            result = self.SocialPostAccountLinkedin._action_post()
            self.assertTrue(result)
            self.assertEqual(
                self.SocialPostAccountLinkedin.linkedin_post_account_urn, "1234567890"
            )
            self.assertEqual(self.SocialPostAccountLinkedin.state, "posted")

    @patch(PATCH_ACCOUNT_LINKEDIN.format("create_restclient_linkedin"))
    @patch(PATCH_POST_ACCOUNT_LINKEDIN.format("_action_post"), autospec=True)
    def test_action_post_failure(self, mock_super_post, mock_create_post):
        mock_super_post.return_value = True
        mock_create_post.return_value = False
        with patch.object(
            type(self.SocialPostAccountReadyLinkedin),
            "filter_by_media_types",
            return_value=self.env["social.network.post.account"].browse(
                self.SocialPostAccountReadyLinkedin.id
            ),
        ):
            result = self.SocialPostAccountReadyLinkedin._action_post()
            self.assertTrue(result)
            self.assertFalse(
                self.SocialPostAccountReadyLinkedin.linkedin_post_account_urn
            )
            self.assertEqual(self.SocialPostAccountReadyLinkedin.state, "ready")

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    def test_like_success(self, mock_request):
        author_urn = "urn:li:person:abc"
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_request.return_value = mock_response
        result = self.SocialPostAccountLinkedin.action_like_post(author_urn=author_urn)
        self.assertTrue(result["success"])
        self.assertEqual(result["message"], "")

        mock_response = MagicMock()
        mock_response.status_code = 409
        mock_request.return_value = mock_response
        result = self.SocialPostAccountLinkedin.action_like_post(author_urn=author_urn)
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "You have already reacted to this post.")

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        result = self.SocialPostAccountLinkedin.action_like_post(author_urn=author_urn)
        self.assertFalse(result["success"])
        self.assertEqual(
            result["message"], "The post does not exist or has been deleted."
        )

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal error occurred."}
        mock_request.return_value = mock_response

        result = self.SocialPostAccountLinkedin.action_like_post(author_urn=author_urn)
        self.assertFalse(result["success"])
        self.assertEqual(result["message"], "Internal error occurred.")

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    def test_get_comments_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "elements": [
                {
                    "id": "comment1",
                    "message": {"text": "Great post!"},
                    "lastModified": {"actor": {"id": "actor1"}, "time": 1609459200000},
                    "content": [{"url": "http://example.com/image1.jpg"}],
                }
            ]
        }
        mock_request.return_value = mock_response
        result = self.SocialPostAccountLinkedin.get_comments()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], "comment1")
        self.assertEqual(result[0]["text"], "Great post!")
        self.assertEqual(result[0]["actor"]["id"], "actor1")
        self.assertEqual(result[0]["images_url"], ["http://example.com/image1.jpg"])

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal Server Error"}
        mock_request.return_value = mock_response
        with self.assertRaises(ValidationError):
            self.SocialPostAccountLinkedin.get_comments()

        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"elements": []}
        mock_request.return_value = mock_response
        result = self.SocialPostAccountLinkedin.get_comments()
        self.assertEqual(result, [])

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    @patch(PATCH_ACCOUNT_LINKEDIN.format("_prepare_images_for_post"))
    def test_create_linkedin_comment_success(self, mock_prepare_images, mock_request):
        mock_prepare_images.return_value = [{"media": "asset_123"}]
        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"message": "Comment created successfully"}
        mock_request.return_value = mock_response
        comment = "Great post!"
        image_base64 = "base64string"
        result = self.SocialPostAccountLinkedin.create_linkedin_comment(
            comment, image_base64
        )
        self.assertEqual(result["success"], True)

        mock_response = MagicMock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"message": "Comment created successfully"}
        mock_request.return_value = mock_response
        image_base64 = None
        result = self.SocialPostAccountLinkedin.create_linkedin_comment(
            comment, image_base64
        )
        self.assertEqual(result["success"], True)

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    def test_delete_linkedin_comment_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 204
        mock_request.return_value = mock_response
        comment_id = "123456"
        actor_urn = "urn:li:person:abc123"
        result = self.SocialPostAccountLinkedin.delete_linkedin_comment(
            comment_id, actor_urn
        )
        self.assertEqual(result["success"], True)

        mock_response = MagicMock()
        mock_response.status_code = 500  # Código de error para DELETE
        mock_response.json.return_value = {"message": "Internal Server Error"}
        mock_request.return_value = mock_response
        result = self.SocialPostAccountLinkedin.delete_linkedin_comment(
            comment_id, actor_urn
        )
        self.assertEqual(result["success"], False)

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_response.json.return_value = {"message": "Not Found"}
        mock_request.return_value = mock_response
        result = self.SocialPostAccountLinkedin.delete_linkedin_comment(
            comment_id, actor_urn
        )
        self.assertEqual(result["success"], False)

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    def test_get_linkedin_comment_success(self, mock_request):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_request.return_value = mock_response
        result = self.SocialPostAccountLinkedin.get_linkedin_comment()
        self.assertEqual(result, True)

        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_request.return_value = mock_response
        result = self.SocialPostAccountReadyLinkedin.get_linkedin_comment()
        self.assertEqual(result, False)
        self.assertEqual(
            self.SocialPostAccountReadyLinkedin.linkedin_post_account_urn, False
        )

        mock_response = MagicMock()
        mock_response.status_code = 500
        mock_response.json.return_value = {"message": "Internal Server Error"}
        mock_request.return_value = mock_response
        result = self.SocialPostAccountReadyLinkedin.get_linkedin_comment()
        self.assertEqual(result, False)
        self.assertEqual(
            self.SocialPostAccountReadyLinkedin.linkedin_post_account_urn, False
        )
