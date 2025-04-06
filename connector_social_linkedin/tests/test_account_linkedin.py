# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from datetime import datetime
from unittest.mock import MagicMock, Mock, patch

from odoo.addons.connector_social_base.social_utils import (
    _generate_timestamps,
)
from odoo.addons.connector_social_linkedin.models.social_network_account import (
    SocialNetworkAccount,
)
from odoo.addons.connector_social_linkedin.tests.test_common_linkedin import (
    TestSocialNetworkCommonLinkedin,
)

from ..social_linkedin_utils import (
    _FIELDS_CAMPAIGN_LINKEDIN,
    _FIELDS_STATISTIC_LINKEDIN,
)

PATCH_ACCOUNT_LINKEDIN = (
    "odoo.addons.connector_social_linkedin.models."
    "social_network_account.SocialNetworkAccount.{}"
)


class LinkedinMockMixin:
    def _mock_linkedin(self, return_value, account, attribute="_request_linkedin"):
        return patch.object(type(account), attribute, return_value=return_value)


class TestSocialNetworkLinkedin(LinkedinMockMixin, TestSocialNetworkCommonLinkedin):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.image_base64 = base64.b64encode(b"testimage").decode("utf-8")
        cls.video_data = base64.b64encode(b"testvideo").decode("utf-8")
        cls.video_mock = type("Video", (), {"datas": cls.video_data})()
        cls.mediaAsset = "urn:li:digitalmediaAsset:{}"
        cls.mediaImage = "urn:li:digitalmediaImage:{}"

    def test_action_add_account_valid(self):
        with patch.object(
            type(self.SocialMedia), "_action_valid_add_account", return_value=True
        ):
            action = self.SocialMedia.action_add_account()
            self.assertIn("name", action)
            self.assertEqual(action["type"], "ir.actions.act_window")

    def test_action_add_account_invalid(self):
        with patch.object(
            type(self.SocialMedia), "_action_valid_add_account", return_value=False
        ), patch.object(
            type(self.SocialMedia),
            "action_add_account",
            return_value={"mock": "called"},
        ) as mock_add:
            action = self.SocialMedia.action_add_account()
            self.assertEqual(action, {"mock": "called"})
            mock_add.assert_called_once()

    def test_prepare_url_upload_asset_image(self):
        fake_response = {
            "value": {
                "asset": self.mediaAsset.format("C123"),
                "uploadMechanism": {
                    "com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest": {
                        "uploadUrl": "https://fake.upload.url/image"
                    }
                },
            }
        }

        with self._mock_linkedin(
            return_value=fake_response, account=self.SocialAccountLinkedin
        ) as mock_request:
            asset, upload_url = self.SocialAccountLinkedin._prepare_url_upload_asset(
                feedshare="image"
            )

            self.assertEqual(asset, self.mediaAsset.format("C123"))
            self.assertEqual(upload_url, "https://fake.upload.url/image")

            mock_request.assert_called_once()
            args, kwargs = mock_request.call_args
            self.assertEqual(kwargs["method"], "POST")
            self.assertIn(
                "feedshare-image",
                kwargs["json_data"]["registerUploadRequest"]["recipes"][0],
            )

    def test_prepare_url_upload_asset_video(self):
        with self._mock_linkedin(
            return_value={"value": {"asset": "video_asset"}},
            account=self.SocialAccountLinkedin,
        ) as mock_request:
            asset, upload_url = self.SocialAccountLinkedin._prepare_url_upload_asset(
                feedshare="video"
            )

            self.assertEqual(asset, "video_asset")
            self.assertIsInstance(upload_url, dict)

            json_data = mock_request.call_args[1]["json_data"]
            self.assertIn(
                "SYNCHRONOUS",
                json_data["registerUploadRequest"]["supportedUploadMechanism"],
            )

    def test_prepare_url_upload_image(self):
        fake_response = {
            "value": {
                "image": self.mediaImage.format("C123456"),
                "uploadUrl": "https://fake.upload.url/image",
            }
        }

        with self._mock_linkedin(
            return_value=fake_response, account=self.SocialAccountLinkedin
        ) as mock_request:
            image, upload_url = self.SocialAccountLinkedin._prepare_url_upload_image()

            self.assertEqual(image, self.mediaImage.format("C123456"))
            self.assertEqual(upload_url, "https://fake.upload.url/image")

            mock_request.assert_called_once()

    def test_prepare_images_videos_for_post_success(self):
        mock_upload_asset_image = (
            self.mediaAsset.format("XYZ"),
            "https://fake.upload/asset/image",
        )
        mock_upload_asset_video = (
            self.mediaAsset.format("VID123"),
            "https://fake.upload/asset/video",
        )
        mock_response = Mock()
        mock_response.status_code = 201
        method_asset = "_prepare_url_upload_asset"

        def mock_upload_image_video(mock_upload_asset):
            return self._mock_linkedin(
                return_value=mock_upload_asset,
                attribute=method_asset,
                account=self.SocialAccountLinkedin,
            ), self._mock_linkedin(
                return_value=mock_response, account=self.SocialAccountLinkedin
            )

        val1, val2 = mock_upload_image_video(mock_upload_asset_image)

        with val1, val2:
            images = self.SocialAccountLinkedin._prepare_images_for_post(
                image_ids=[self.image_base64]
            )
            self.assertEqual(len(images), 1)
            self.assertEqual(images[0], self.mediaAsset.format("XYZ"))

        val1, val2 = mock_upload_image_video(mock_upload_asset_video)

        with val1, val2:
            videos = self.SocialAccountLinkedin._prepare_videos_for_post(
                video_ids=[self.video_mock]
            )
            self.assertEqual(len(videos), 1)
            self.assertEqual(videos[0], self.mediaAsset.format("VID123"))

    def test_create_restclient_linkedin_success(self):
        fake_entity_id = "post:1234"
        mock_restli_response = Mock(status_code=201, entity_id=fake_entity_id)

        with patch.object(
            type(self.SocialAccountLinkedin),
            "_prepare_images_for_post",
            return_value=["urn:li:image:ABC"],
        ), patch.object(
            type(self.SocialAccountLinkedin),
            "_prepare_videos_for_post",
            return_value=[],
        ), patch.object(
            type(self.SocialAccountLinkedin), "_get_restli_client"
        ) as mock_restli:
            mock_restli.create.return_value = mock_restli_response

            entity_id = self.SocialAccountLinkedin.create_restclient_linkedin(
                resource_path="/ugcPosts",
                message="Test post message",
                image_ids=["mock-image"],
                video_ids=[],
            )

            self.assertEqual(entity_id, fake_entity_id)
            mock_restli.create.assert_called_once()

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    def test_get_posts(self, mock_request_linkedin):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "elements": [
                {
                    "id": "123",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {"text": "Post 1"}
                    },
                },
                {
                    "id": "456",
                    "specificContent": {
                        "com.linkedin.ugc.ShareContent": {"text": "Post 2"}
                    },
                },
            ]
        }

        mock_request_linkedin.return_value = mock_response

        linkedin_account = self.SocialAccountLinkedin
        posts = linkedin_account._get_posts()

        self.assertEqual(len(posts), 2)
        self.assertEqual(posts[0]["id"], "123")
        self.assertEqual(posts[1]["id"], "456")
        self.assertEqual(posts[0]["share_content"]["text"], "Post 1")
        self.assertEqual(posts[1]["share_content"]["text"], "Post 2")

        mock_request_linkedin.assert_called_once_with(
            endpoint="/ugcPosts",
            headers=self.SocialMediaLinkedin._get_linkedin_headers(
                linkedin_account.access_token
            ),
            params_fields=["q", "authors"],
            params_values={
                "q": "authors",
                "authors": [
                    f"urn:li:organization:{linkedin_account.linkedin_account_id}"
                ],
            },
            linkedin_v2=True,
            return_json=False,
        )

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    def test_get_entity_share_statistics(self, mock_request_linkedin):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "elements": [
                {
                    "organizationalEntity": "urn:li:organization:123",
                    "shareStatistics": {"totalShares": 150},
                },
                {
                    "organizationalEntity": "urn:li:organization:456",
                    "shareStatistics": {"totalShares": 200},
                },
            ]
        }

        mock_request_linkedin.return_value = mock_response

        linkedin_account = self.SocialAccountLinkedin
        posts = [{"id": "post_1"}, {"id": "post_2"}]
        stats = linkedin_account._get_entity_share_statistics(posts=posts)

        self.assertEqual(len(stats), 2)
        self.assertEqual(stats[0]["organizationalEntity"], "urn:li:organization:123")
        self.assertEqual(stats[1]["shareStatistics"]["totalShares"], 200)

        mock_request_linkedin.assert_called_once_with(
            endpoint="/organizationalEntityShareStatistics",
            headers=self.SocialMediaLinkedin._get_linkedin_headers(
                linkedin_account.access_token
            ),
            params_fields=["q", "organizationalEntity", "shares"],
            params_values={
                "q": "organizationalEntity",
                "organizationalEntity": "urn:li:organization:{}".format(
                    linkedin_account.linkedin_account_id
                ),
                "shares": ["post_1,post_2"],
            },
            params_values_char_ignore=None,
            linkedin_v2=True,
            return_json=False,
        )

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_get_entity_share_statistics"))
    @patch(PATCH_ACCOUNT_LINKEDIN.format("_get_default_filter_date"))
    def test_get_chart_account_statistics(
        self, mock_get_default_filter_date, mock_get_entity_share_statistics
    ):
        mock_get_default_filter_date.return_value = (
            "2025-01-01T00:00:00",
            "2025-01-07T23:59:59",
        )

        mock_get_entity_share_statistics.return_value = [
            {
                "totalShareStatistics": {
                    "clickCount": 100,
                    "shareCount": 50,
                    "likeCount": 30,
                }
            },
            {
                "totalShareStatistics": {
                    "clickCount": 200,
                    "shareCount": 100,
                    "likeCount": 70,
                }
            },
        ]

        linkedin_account = self.SocialAccountLinkedin

        result = linkedin_account._get_chart_account_statistics(
            start_date="2025-01-01", end_date="2025-01-07", granularity="WEEK"
        )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["datasets"][0]["data"], [100, 200])
        self.assertEqual(result[0]["datasets"][1]["data"], [50, 100])
        self.assertEqual(result[0]["datasets"][2]["data"], [30, 70])

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    def test_get_campaigns(self, mock_request_linkedin):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "elements": [
                {"id": "123", "name": "Campaign A"},
                {"id": "456", "name": "Campaign B"},
            ]
        }
        mock_request_linkedin.return_value = mock_response
        linkedin_account = self.SocialAccountLinkedin

        startDate = datetime(2025, 1, 1)
        endDate = datetime(2025, 1, 31)

        result = linkedin_account._get_campaigns(
            start_date=startDate, end_date=endDate, campaign_ids=["123"]
        )

        start_time, end_time = _generate_timestamps(startDate, endDate)

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["id"], "123")
        self.assertEqual(result[1]["id"], "456")
        mock_request_linkedin.assert_called_once_with(
            endpoint="/adCampaignsV2",
            headers=self.SocialMediaLinkedin._get_linkedin_headers(
                linkedin_account.access_token
            ),
            params_fields=["q", "search", "fields", "count"],
            params_values={
                "q": "search",
                "search": f"(startDate:(values:{start_time}),endDate:(values:{end_time}),"
                "test:true,campaigns:(values:List(123)))",
                "fields": _FIELDS_CAMPAIGN_LINKEDIN,
                "count": 100,
            },
            params_values_char_ignore={"search": [{"1,2,3,4,5,6,7": ":"}]},
            return_json=False,
            linkedin_v2=True,
        )

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    def test_get_statistics(self, mock_request_linkedin):
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "elements": [
                {
                    "campaign": "123",
                    "statistics": {"clickCount": 100, "impressionCount": 500},
                },
                {
                    "campaign": "456",
                    "statistics": {"clickCount": 200, "impressionCount": 600},
                },
            ]
        }
        mock_request_linkedin.return_value = mock_response

        linkedin_account = self.SocialAccountLinkedin

        result = linkedin_account._get_statistics(
            ads_ids=["123", "456"],
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 31),
        )

        self.assertEqual(len(result), 2)
        self.assertEqual(result[0]["campaign"], "123")
        self.assertEqual(result[1]["campaign"], "456")
        mock_request_linkedin.assert_called_once_with(
            endpoint="/adAnalyticsV2",
            headers=linkedin_account.media_id._get_linkedin_headers(
                linkedin_account.access_token
            ),
            params_fields=[
                "q",
                "pivots",
                "timeGranularity",
                "dateRange",
                "fields",
                "count",
                "accounts",
            ],
            params_values={
                "q": "statistics",
                "pivots": ["CREATIVE"],
                "timeGranularity": "ALL",
                "dateRange": "(start:(year:2025,month:1,day:1),end:(year:2025,month:1,day:31))",
                "fields": _FIELDS_STATISTIC_LINKEDIN,
                "count": 100,
                "accounts": [
                    "urn:li:sponsoredAccount:123",
                    "urn:li:sponsoredAccount:456",
                ],
            },
            params_values_char_ignore={"dateRange": [{"all": ":"}]},
            return_json=False,
            linkedin_v2=True,
        )

    @patch.object(SocialNetworkAccount, "_get_statistics")
    def test_get_statistics_ads_calls_internal_method(self, mock_get_statistics):
        ads_ids = [123, 456]
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)

        expected_result = [{"mock": "data"}]
        mock_get_statistics.return_value = expected_result

        result = self.SocialAccountLinkedin._get_statistics_ads(
            ads_ids, start_date, end_date
        )

        mock_get_statistics.assert_called_once_with(
            ads_ids=ads_ids,
            start_date=start_date,
            end_date=end_date,
        )
        self.assertEqual(result, expected_result)

    @patch(PATCH_ACCOUNT_LINKEDIN.format("_get_statistics_ads"))
    @patch(PATCH_ACCOUNT_LINKEDIN.format("_get_campaigns"))
    @patch(PATCH_ACCOUNT_LINKEDIN.format("_get_posts"))
    @patch(PATCH_ACCOUNT_LINKEDIN.format("_request_linkedin"))
    def test_load_ads(
        self,
        mock_request_linkedin,
        mock_get_posts,
        mock_get_campaigns,
        mock_get_statistics_ads,
    ):
        # Arrange
        fake_ads = [
            {
                "id": 1,
                "reference": "ref1",
                "campaign": "urn:li:sponsoredCampaign:123",
                "changeAuditStamps": {"created": {"time": 1735689600000}},
                "servingStatuses": ["ACTIVE"],
            }
        ]
        fake_stats = [
            {
                "pivotValues": ["urn:li:sponsoredAccount:1"],
                "clicks": 10,
            }
        ]
        fake_campaigns = [
            {
                "id": 123,
                "account": "urn:li:sponsoredAccount:999",
            }
        ]
        fake_posts = {
            "ref1": {
                "id": "ref1",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": "Test post"}
                    }
                },
            }
        }

        mock_request_linkedin.return_value = MagicMock(
            status_code=200, json=lambda: {"elements": fake_ads}
        )
        mock_get_statistics_ads.return_value = fake_stats
        mock_get_campaigns.return_value = fake_campaigns
        mock_get_posts.return_value = fake_posts

        mock_account = MagicMock()
        mock_account.media_type = "linkedin"
        mock_account._get_default_filter_date.side_effect = (
            lambda s, e, time_date=False: ("2025-01-01", "2025-01-31")
            if not time_date
            else (1735689600000, 1738281600000)
        )

        with patch(
            PATCH_ACCOUNT_LINKEDIN.format("_get_default_filter_date"),
            self.SocialAccountLinkedin._get_default_filter_date,
        ):
            mock_account._request_linkedin = mock_request_linkedin
            mock_account._get_statistics_ads = mock_get_statistics_ads
            mock_account._get_campaigns = mock_get_campaigns
            mock_account._get_posts = mock_get_posts

            result = self.SocialAccountLinkedin._load_ads(
                start_date="2025-01-01", end_date="2025-01-31"
            )

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["id"], 1)
        self.assertEqual(result[0]["post"]["name"], "Test post")
        self.assertEqual(result[0]["campaign"]["id"], 123)
        self.assertEqual(result[0]["statistic"]["clicks"], 10)
        self.assertIn("url", result[0])
