# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import itertools
from datetime import date, datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta
from linkedin_api.clients.restli.client import RestliClient
from werkzeug.urls import url_join, url_quote

from odoo import api, fields, models
from odoo.exceptions import ValidationError
from odoo.tools import float_round

from odoo.addons.connector_social_base.social_utils import (
    _generate_timestamps,
    convert_to_date,
    social_url_encode,
)

from ..social_linkedin_utils import (
    _FIELDS_CAMPAIGN_LINKEDIN,
    _FIELDS_STATISTIC_LINKEDIN,
    _URL_AUTH_V2_LINKEDIN,
    _URL_LINKEDIN,
    _URL_REST_LINKEDIN,
    _URL_V2_LINKEDIN,
    _VERSION_STRING,
)


class SocialNetworkAccount(models.Model):
    _inherit = "social.network.account"

    restli_client = RestliClient()

    linkedin_account_id = fields.Char(
        compute="_compute_linkedin_account_id", store=True
    )
    linkedin_account_urn = fields.Char()
    linkedin_refresh_token_expires_in = fields.Date()

    def _fields_account_url(self):
        return super()._fields_account_url() + [
            (
                "linkedin_account_urn",
                "https://www.linkedin.com/company/{}/admin/dashboard/".format(
                    self.linkedin_account_id
                ),
            )
        ]

    @api.depends("linkedin_account_urn")
    def _compute_linkedin_account_id(self):
        for social_account in self:
            if social_account.linkedin_account_urn:
                social_account.linkedin_account_id = (
                    social_account.linkedin_account_urn.split(":")[-1]
                )

    def _request_linkedin(
        self,
        method="GET",
        endpoint=None,
        params=None,
        headers=None,
        timeout=5,
        linkedin_v2=False,
        data=None,
        token=False,
        return_json=True,
        json_data=None,
        params_fields=None,
        params_values=None,
        params_values_char_ignore=None,
        complete_url=False,
    ):
        base_url_linkedin = _URL_REST_LINKEDIN
        if linkedin_v2:
            base_url_linkedin = _URL_V2_LINKEDIN
        elif token:
            base_url_linkedin = _URL_AUTH_V2_LINKEDIN
        url = base_url_linkedin + endpoint if not complete_url else complete_url
        if params_fields:
            url += "?"
            url_params = []
            for param_field in params_fields:
                url_params.append(
                    social_url_encode(
                        param_field, params_values, params_values_char_ignore
                    )
                )
            url += "&".join(url_params)
        response = requests.request(
            method=method,
            url=url,
            params=params,
            timeout=timeout,
            headers=headers,
            data=data,
            json=json_data,
        )
        if return_json and response.status_code == 200:
            return response.json()
        return response

    def _refresh_token(self):
        pass

    def validate_linkedin_access_token(self, access_token):
        irConfigParameter = self.env["ir.config_parameter"].sudo()
        data = {
            "client_id": irConfigParameter.get_param(
                "connector_social_linkedin.linkedin_client", ""
            ),
            "client_secret": irConfigParameter.get_param(
                "connector_social_linkedin.linkedin_secret", ""
            ),
            "token": access_token,
        }
        response = self._request_linkedin(
            method="POST",
            endpoint="/introspectToken",
            data=data,
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            token=True,
        )
        if response and response.get("active", False):
            return True
        return False

    def _prepare_url_upload_asset(self, feedshare="image"):
        json_data = {
            "registerUploadRequest": {
                "owner": self.linkedin_account_urn,
                "recipes": [f"urn:li:digitalmediaRecipe:feedshare-{feedshare}"],
                "serviceRelationships": [
                    {
                        "identifier": "urn:li:userGeneratedContent",
                        "relationshipType": "OWNER",
                    }
                ],
            }
        }
        if feedshare == "video":
            json_data["registerUploadRequest"]["supportedUploadMechanism"] = [
                "SYNCHRONOUS"
            ]
        asset = self._request_linkedin(
            method="POST",
            endpoint="/assets",
            headers=self.media_id._get_linkedin_headers(self.access_token),
            params_fields=["action"],
            params_values={"action": "registerUpload"},
            json_data=json_data,
            linkedin_v2=True,
        )
        value_upload_asset = asset.get("value", {})
        return value_upload_asset.get("asset", {}), value_upload_asset.get(
            "uploadMechanism", {}
        ).get("com.linkedin.digitalmedia.uploading.MediaUploadHttpRequest", {}).get(
            "uploadUrl", {}
        )

    def _prepare_url_upload_image(self):
        image = self._request_linkedin(
            method="POST",
            endpoint="/images",
            headers=self.media_id._get_linkedin_headers(self.access_token),
            params_fields=["action"],
            params_values={"action": "initializeUpload"},
            json_data={
                "initializeUploadRequest": {
                    "owner": self.linkedin_account_urn,
                }
            },
        )
        value_upload_image = image.get("value", {})
        return value_upload_image.get("image", {}), value_upload_image.get("uploadUrl")

    def _prepare_images_for_post(self, image_ids=None, image_datas=None):
        images_upload = []
        if image_datas:
            image_ids = [image_datas.split(",")[-1]]
        for image in image_ids or []:
            value_upload_asset, url_upload_asset = self._prepare_url_upload_asset()
            upload_image = self._request_linkedin(
                method="PUT",
                complete_url=url_upload_asset,
                headers=self.media_id._get_linkedin_headers(
                    self.access_token, content_type="application/octet-stream"
                ),
                data=base64.b64decode(image.datas)
                if not isinstance(image, str)
                else base64.b64decode(image),
                linkedin_v2=True,
                return_json=False,
            )
            if upload_image.status_code == 201:
                images_upload.append(value_upload_asset)
        return images_upload

    def _prepare_videos_for_post(self, video_ids):
        videos_upload = []
        for video in video_ids:
            value_upload_asset, url_upload_asset = self._prepare_url_upload_asset(
                feedshare="video"
            )

            upload_image = self._request_linkedin(
                method="PUT",
                complete_url=url_upload_asset,
                headers=self.media_id._get_linkedin_headers(
                    self.access_token, content_type="application/octet-stream"
                ),
                data=base64.b64decode(video.datas),
                linkedin_v2=True,
            )
            if upload_image.status_code == 201:
                videos_upload.append(value_upload_asset)
        return videos_upload

    def create_restclient_linkedin(self, resource_path, message, image_ids, video_ids):
        if self.access_token:
            assets_image_post = self._prepare_images_for_post(image_ids)
            assets_video_post = self._prepare_videos_for_post(video_ids)
            medias = []
            media_category = "NONE"
            if assets_image_post:
                medias = [
                    {
                        "status": "READY",
                        "media": asset_id,
                    }
                    for asset_id in assets_image_post
                ]
                media_category = "IMAGE"
            elif assets_video_post:
                medias = [
                    {
                        "status": "READY",
                        "media": asset_id,
                    }
                    for asset_id in assets_video_post
                ]
                media_category = "VIDEO"

            entity_post = {
                "author": f"urn:li:organization:{self.linkedin_account_id}",
                "lifecycleState": "PUBLISHED",
                "specificContent": {
                    "com.linkedin.ugc.ShareContent": {
                        "shareCommentary": {"text": message},
                        "shareMediaCategory": media_category,
                        "media": medias,
                    }
                },
                # PUBLIC, CONNECTIONS (Private)
                "visibility": {"com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"},
            }

            if assets_image_post:
                entity_post["specificContent"]["com.linkedin.ugc.ShareContent"][
                    "media"
                ] = [
                    {
                        "status": "READY",
                        "media": asset_id,
                    }
                    for asset_id in assets_image_post
                ]

            response = self.restli_client.create(
                resource_path=resource_path,
                entity=entity_post,
                access_token=self.access_token,
            )
            if response.status_code == 201 and response.entity_id:
                return response.entity_id
            return False

    def get_access_token_linkedin(self, authorization_code, redirect_endpoint_uri):
        irConfigParameter = self.env["ir.config_parameter"].sudo()
        params = {
            "grant_type": "authorization_code",
            "code": authorization_code,
            "client_id": irConfigParameter.get_param(
                "connector_social_linkedin.linkedin_client", ""
            ),
            "client_secret": irConfigParameter.get_param(
                "connector_social_linkedin.linkedin_secret", ""
            ),
            "redirect_uri": url_join(self.get_base_url(), redirect_endpoint_uri),
        }
        return self._request_linkedin(
            endpoint="/accessToken", params=params, timeout=20, token=True
        )

    def get_account_linkedin(self, access_token):
        response = self._request_linkedin(
            endpoint="/organizationAcls",
            headers=self.media_id._get_linkedin_headers(access_token),
            params={"q": "roleAssignee", "role": "ADMINISTRATOR", "state": "APPROVED"},
        )
        organization_ids = [
            organization["organization"].split(":")[-1]
            for organization in response.get("elements", [])
        ]
        response = self.restli_client.batch_get(
            resource_path="/organizations",
            ids=organization_ids,
            access_token=access_token,
            version_string=_VERSION_STRING,
        )

        return response.results.items()

    def create_account_linkedin(self, token):
        access_token = token.get("access_token", False)
        if access_token:
            organizations = self.get_account_linkedin(access_token)
            expire_token = date.today() + timedelta(
                days=token.get("expires_in", 0) / 86400
            )
            expire_refresh_token = convert_to_date(
                seconds=token.get("linkedin_refresh_token_expires_in", 0) / 86400,
            )

            for organization_id, organization in organizations:
                linkedin_account_urn = f"urn:li:organization:{organization_id}"
                self.create(
                    {
                        "name": organization.get("localizedName", False),
                        "username": organization.get("vanityName", False),
                        "linkedin_account_id": organization_id,
                        "linkedin_account_urn": linkedin_account_urn,
                        "media_id": self.env.ref(
                            "connector_social_linkedin.social_network_media_linkedin"
                        ).id,
                        "access_token": access_token,
                        "refresh_access_token": token.get("refresh_token", False),
                        "expire_access_token_date": expire_token,
                        "linkedin_refresh_token_expires_in": expire_refresh_token,
                        "is_valid_token_access": True,
                    }
                )

    def validate_active_access_token(self):
        res = super().validate_active_access_token()
        if (
            self.media_id.id
            == self.env.ref(
                "connector_social_linkedin.social_network_media_linkedin"
            ).id
        ):
            self.is_valid_token_access = self.validate_linkedin_access_token(
                self.access_token
            )
        return res

    def _update_posts_statistics(self, update_all_accounts=False):
        statistics = super()._update_posts_statistics(update_all_accounts)
        PostAccount = self.env["social.network.post.account"]
        account_ids = (
            self.search([("media_type", "=", "linkedin")])
            if update_all_accounts
            else self
        )
        for account in account_ids:
            post_accounts = []
            if account.linkedin_account_id:
                # POSTS
                response_ugc_posts = self._request_linkedin(
                    endpoint="/ugcPosts",
                    headers=self.media_id._get_linkedin_headers(account.access_token),
                    params_fields=["q", "authors"],
                    params_values={
                        "q": "authors",
                        "authors": [
                            f"urn:li:organization:{account.linkedin_account_id}"
                        ],
                    },
                    linkedin_v2=True,
                    return_json=False,
                )
                if response_ugc_posts.status_code == 200:
                    ugc_posts = response_ugc_posts.json().get("elements", [])
                else:
                    raise ValidationError(
                        f"Error in get ugc posts: {response_ugc_posts.json()}"
                    )

                # POSTS REACTIONS
                post_reactions = self._request_linkedin(
                    endpoint="/socialActions",
                    headers=self.media_id._get_linkedin_headers(account.access_token),
                    params_fields=["ids"],
                    params_values={
                        "ids": [
                            "{}".format(
                                ",".join(
                                    list(map(lambda val: val.get("id"), ugc_posts))
                                )
                            )
                        ]
                    },
                    linkedin_v2=True,
                )

                post_data_reactions = {
                    post_id: (
                        post_data["likesSummary"]["totalLikes"],
                        post_data["commentsSummary"]["aggregatedTotalComments"],
                    )
                    for post_id, post_data in post_reactions.get("results", []).items()
                }

                for ugc_post in ugc_posts:
                    post_account = PostAccount.search(
                        [("linkedin_post_account_urn", "=", ugc_post.get("id"))]
                    )
                    share_content = ugc_post.get("specificContent", {}).get(
                        "com.linkedin.ugc.ShareContent", {}
                    )
                    data = {
                        "linkedin_post_account_urn": ugc_post.get("id"),
                        "post_account_url": "https://www.linkedin.com/feed/update/{}".format(
                            ugc_post.get("id")
                        ),
                        "message": share_content.get("shareCommentary", {}).get(
                            "text", ""
                        ),
                        "account_id": account.id,
                        "likes_count": post_data_reactions.get(
                            ugc_post.get("id"), (0, 0)
                        )[0],
                        "comments_count": post_data_reactions.get(
                            ugc_post.get("id"), (0, 0)
                        )[1],
                        "published_date": convert_to_date(
                            miliseconds=ugc_post.get("firstPublishedAt", 0),
                            expire_date=False,
                        ),
                        "actor_urn": ugc_post.get("created", {}).get("actor", False),
                    }

                    attach_images = PostAccount._get_assets_save(share_content)
                    data.update({"image_ids": attach_images})

                    if not post_account:
                        post_accounts.append((0, 0, data))
                    else:
                        post_accounts.append((1, post_account.id, data))

                response_organization_statistics = self._request_linkedin(
                    endpoint="/organizationalEntityShareStatistics",
                    headers=self.media_id._get_linkedin_headers(account.access_token),
                    params={
                        "q": "organizationalEntity",
                        "organizationalEntity": account.linkedin_account_urn,
                    },
                )
                organization_statistics = response_organization_statistics.get(
                    "elements", []
                )

                def map_statistics(x, interaction=False, engagement=False):
                    share_statistics = x.get("totalShareStatistics", 0)
                    total_views = share_statistics.get("impressionCount", 0)
                    if interaction:
                        return (
                            share_statistics.get("shareCount", 0)
                            + share_statistics.get("clickCount", 0)
                            + share_statistics.get("likeCount", 0)
                            + share_statistics.get("commentCount", 0)
                        )
                    elif engagement:
                        return (
                            float_round(
                                share_statistics.get("engagement", 0) / total_views, 2
                            )
                            if total_views > 0
                            else 0
                        )
                    return total_views

                account.write(
                    {
                        "total_views": sum(
                            list(
                                map(
                                    lambda x: map_statistics(x), organization_statistics
                                )
                            )
                        ),
                        "interactions_count": sum(
                            list(
                                map(
                                    lambda x: map_statistics(x, interaction=True),
                                    organization_statistics,
                                )
                            )
                        ),
                        "engagement_rate": sum(
                            list(
                                map(
                                    lambda x: map_statistics(x, engagement=True),
                                    organization_statistics,
                                )
                            )
                        ),
                        "post_account_ids": post_accounts,
                    }
                )
        return list(
            itertools.chain(
                statistics,
                self.search_read(
                    [("media_type", "=", "linkedin")],
                    [
                        "name",
                        "company_id",
                        "media_id",
                        "total_views",
                        "interactions_count",
                        "engagement_rate",
                    ],
                ),
            )
        )

    def get_ads_filter_date(self, start_date, end_date):
        start = start_date or (datetime.now() - relativedelta(months=1))
        end = end_date or (datetime.now())
        return start, end

    def _get_campaigns(self, start_date, end_date):
        start_time, end_time = _generate_timestamps(start_date, end_date)
        response = self._request_linkedin(
            endpoint="/adCampaignsV2",
            headers=self.media_id._get_linkedin_headers(self.access_token),
            params_fields=["q", "search", "fields", "count"],
            params_values={
                "q": "search",
                "search": f"(startDate:(values:{start_time}),endDate:(values:{end_time}),test:true)",
                "fields": _FIELDS_CAMPAIGN_LINKEDIN,
                "count": 100,
            },
            params_values_char_ignore={"search": [{"all": ":"}]},
            return_json=False,
            linkedin_v2=True,
        )

        if response.status_code == 200:
            campaigns = response.json().get("elements", [])
        else:
            raise ValidationError(f"Error in get campaigns: {response.json()}")
        return campaigns

    def _get_statistics(
        self, campaign_ids=None, ads_ids=None, start_date=None, end_date=None
    ):
        start_date, end_date = self.get_ads_filter_date(start_date, end_date)
        start_date = start_date.strftime("%Y-%m-%d").split("-")
        parse_start_date = "(year:{},month:{},day:{})".format(
            start_date[0],
            start_date[1],
            start_date[2],
        )
        end_date = end_date.strftime("%Y-%m-%d").split("-")
        parse_end_date = f"(year:{end_date[0]},month:{end_date[1]},day:{end_date[2]})"
        dateStatisticsRange = f"(start:{parse_start_date},end:{parse_end_date})"

        params_fields = [
            "q",
            "pivots",
            "timeGranularity",
            "dateRange",
            "fields",
            "count",
        ]
        params_values = {
            "q": "statistics",
            "pivots": ["CAMPAIGN"],
            "timeGranularity": "ALL",
            "dateRange": dateStatisticsRange,
            "fields": _FIELDS_STATISTIC_LINKEDIN,
            "count": 100,
        }
        if campaign_ids:
            params_fields.append("campaigns")
            params_values.update(
                {
                    "campaigns": list(
                        map(lambda x: f"urn:li:sponsoredCampaign:{x}", campaign_ids)
                    ),
                }
            )
        elif ads_ids:
            params_fields.append("accounts")
            params_values.update(
                {
                    "pivots": ["CREATIVE"],
                    "accounts": list(
                        map(lambda x: f"urn:li:sponsoredAccount:{x}", ads_ids)
                    ),
                }
            )
        response = self._request_linkedin(
            endpoint="/adAnalyticsV2",
            headers=self.media_id._get_linkedin_headers(self.access_token),
            params_fields=params_fields,
            params_values=params_values,
            params_values_char_ignore={"dateRange": [{"all": ":"}]},
            return_json=False,
            linkedin_v2=True,
        )

        if response.status_code == 200:
            statistics = response.json().get("elements", [])
        else:
            raise ValidationError(
                f"Error in get campaigns statistics: {response.json()}"
            )
        return statistics

    def _get_statistics_campaign(self, campaign_ids, start_date, end_date):
        return self._get_statistics(
            campaign_ids=campaign_ids, start_date=start_date, end_date=end_date
        )

    def _load_campaigns(self, start_date=None, end_date=None):
        campaigns_parse = []
        start_date, end_date = self.get_ads_filter_date(start_date, end_date)
        campaigns = self._get_campaigns(start_date, end_date)
        campaign_ids = list(map(lambda x: x["id"], campaigns))
        campaigns_statistics = self._get_statistics_campaign(
            campaign_ids, start_date, end_date
        )
        for campaign in campaigns:
            statistic = list(
                filter(
                    lambda x: f"urn:li:sponsoredCampaign:{campaign['id']}"
                    in x["pivotValues"],
                    campaigns_statistics,
                )
            )
            campaign.update(
                {
                    "advertising_account_url": (
                        f"{_URL_LINKEDIN}/campaignmanager/accounts/{campaign['account'].split(':')[-1]}"
                    ),
                    "campaign_group_url": (
                        f"{_URL_LINKEDIN}/campaignmanager/accounts/{campaign['account'].split(':')[-1]}"
                        f"/campaign-groups?campaignGroupIds={url_quote([739284574])}"
                    ),
                    "organization_url": self.account_url,
                    "media_type": self.media_type,
                    "start_campaign": convert_to_date(
                        miliseconds=campaign["runSchedule"]["start"],
                        expire_date=False,
                        format_date="%Y-%m-%d",
                    ),
                    "end_campaign": convert_to_date(
                        miliseconds=campaign["runSchedule"]["end"],
                        expire_date=False,
                        format_date="%Y-%m-%d",
                    ),
                    "statistic": statistic[0] if len(statistic) > 0 else {},
                }
            )
            campaigns_parse.append(campaign)
        return campaigns_parse

    def _load_campaigns_accounts(self):
        campaigns = super()._load_campaigns_accounts()
        account_ids = self.search([("media_type", "=", "linkedin")])
        for account in account_ids:
            campaigns = list(itertools.chain(campaigns, account._load_campaigns()))
        return campaigns

    def _get_statistics_ads(self, ads_ids, start_date, end_date):
        return self._get_statistics(
            ads_ids=ads_ids, start_date=start_date, end_date=end_date
        )

    def _load_ads(self):
        response = self._request_linkedin(
            endpoint="/adCreativesV2",
            headers=self.media_id._get_linkedin_headers(self.access_token),
            params_fields=["q", "search", "fields", "count"],
            params_values={
                "q": "search",
                "search": "(test:true)",
                "fields": "id,reference,test,campaign,status,changeAuditStamps,servingStatuses",
                "count": 100,
            },
            params_values_char_ignore={"search": [{"1,2,6": ":"}]},
            return_json=False,
            linkedin_v2=True,
        )
        if response.status_code == 200:
            ads = response.json().get("elements", [])
        else:
            raise ValidationError(f"Error in get ads: {response.json()}")

        ads_ids = list(map(lambda x: x["id"], ads))
        ads_statistics = self._get_statistics_ads(
            ads_ids, start_date=None, end_date=None
        )
        ads_parse = []
        for ad in ads:
            statistic = list(
                filter(
                    lambda x: f"urn:li:sponsoredAccount:{ad['id']}" in x["pivotValues"],
                    ads_statistics,
                )
            )
            ad.update(
                {
                    "media_type": self.media_type,
                    "statistic": statistic[0] if len(statistic) > 0 else {},
                }
            )
            ads_parse.append(ad)

        return ads_parse

    def _load_ads_accounts(self):
        ads = super()._load_ads_accounts()
        account_ids = self.search([("media_type", "=", "linkedin")])
        for account in account_ids:
            ads = list(itertools.chain(ads, account._load_ads()))
        return ads
