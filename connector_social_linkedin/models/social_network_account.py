# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import itertools
from datetime import date, datetime, timedelta

import requests
from dateutil.relativedelta import relativedelta
from linkedin_api.clients.restli.client import RestliClient
from werkzeug.urls import url_join, url_quote

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.connector_social_base.social_utils import (
    _generate_timestamps,
    convert_to_date,
    get_weeks,
    social_url_encode,
)

from ..social_linkedin_utils import (
    _FIELDS_CAMPAIGN_LINKEDIN,
    _FIELDS_STATISTIC_LINKEDIN,
    _URL_AUTH_V2_LINKEDIN,
    _URL_LINKEDIN,
    _URL_REST_LINKEDIN,
    _URL_V2_LINKEDIN,
    _URN_ORGANIZATION_LINKEDIN,
    _VERSION_STRING,
)


class SocialNetworkAccount(models.Model):
    _inherit = "social.network.account"

    linkedin_account_id = fields.Char(
        compute="_compute_linkedin_account_id", store=True
    )
    linkedin_account_urn = fields.Char()
    linkedin_refresh_token_expires_in = fields.Date()

    @api.model
    def _get_restli_client(self):
        return RestliClient()

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

    @api.model
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
                "author": f"{_URN_ORGANIZATION_LINKEDIN}{self.linkedin_account_id}",
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

            response = self._get_restli_client.create(
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
        response_organizations = self._get_restli_client.batch_get(
            resource_path="/organizations",
            ids=organization_ids,
            access_token=access_token,
            version_string=_VERSION_STRING,
        )
        return response_organizations.results.items()

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
                linkedin_account_urn = f"{_URN_ORGANIZATION_LINKEDIN}{organization_id}"
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

    def _get_posts(self, params_fields=None, params_values=None):
        params_fields = params_fields or ["q", "authors"]
        params_values = params_values or {
            "q": "authors",
            "authors": [f"{_URN_ORGANIZATION_LINKEDIN}{self.linkedin_account_id}"],
        }
        response = self._request_linkedin(
            endpoint="/ugcPosts",
            headers=self.media_id._get_linkedin_headers(self.access_token),
            params_fields=params_fields,
            params_values=params_values,
            linkedin_v2=True,
            return_json=False,
        )
        if response.status_code == 200:
            response_ugc_posts = response.json()
            if "ids" in params_fields:
                ugc_posts = response_ugc_posts.get("results", [])
            else:
                ugc_posts = [
                    {
                        "id": post["id"],
                        "share_content": post.get("specificContent", {}).get(
                            "com.linkedin.ugc.ShareContent", {}
                        ),
                    }
                    for post in response_ugc_posts.get("elements", [])
                ]
        else:
            raise ValidationError(f"Error in get ugc posts: {response.json()}")
        return ugc_posts

    def _get_entity_share_statistics(
        self,
        posts=None,
        params_fields=None,
        params_values=None,
        params_values_char_ignore=None,
    ):
        if not params_fields:
            params_fields = ["q", "organizationalEntity"]
        if not params_values:
            params_values = {
                "q": "organizationalEntity",
                "organizationalEntity": f"{_URN_ORGANIZATION_LINKEDIN}"
                f"{self.linkedin_account_id}",
            }
        if posts:
            params_fields.append("shares")
            params_values.update(
                {
                    "shares": [
                        "{}".format(
                            ",".join(list(map(lambda val: val.get("id"), posts)))
                        )
                    ]
                }
            )
        response = self._request_linkedin(
            endpoint="/organizationalEntityShareStatistics",
            headers=self.media_id._get_linkedin_headers(self.access_token),
            params_fields=params_fields,
            params_values=params_values,
            params_values_char_ignore=params_values_char_ignore,
            linkedin_v2=True,
            return_json=False,
        )
        if response.status_code == 200:
            data = response.json().get("elements", [])
        else:
            raise ValidationError(f"Error in get ugc posts: {response.json()}")
        return data

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
                ugc_posts = account._get_posts()
                # POSTS REACTIONS
                post_reactions = account._get_entity_share_statistics(posts=ugc_posts)

                post_data_reactions = {}
                if any(
                    post_reaction.get("share", False)
                    for post_reaction in post_reactions
                ):
                    post_data_reactions = {
                        post_reaction["share"]: (
                            post_reaction.get("totalShareStatistics", {}).get(
                                "clickCount", 0
                            ),
                            post_reaction.get("totalShareStatistics", {}).get(
                                "likeCount", 0
                            ),
                            post_reaction.get("totalShareStatistics", {}).get(
                                "commentCount", 0
                            ),
                            post_reaction.get("totalShareStatistics", {}).get(
                                "shareCount", 0
                            ),
                            post_reaction.get("totalShareStatistics", {}).get(
                                "engagement", 0
                            ),
                            post_reaction.get("totalShareStatistics", {}).get(
                                "impressionCount", 0
                            ),
                        )
                        for post_reaction in post_reactions
                    }

                for ugc_post in ugc_posts:
                    post_account = PostAccount.search(
                        [("linkedin_post_account_urn", "=", ugc_post.get("id"))]
                    )
                    share_content = ugc_post.get("share_content", {})
                    post_id = ugc_post.get("id")
                    post_data_reaction = post_data_reactions.get(post_id, {})
                    data = {
                        "linkedin_post_account_urn": post_id,
                        "post_account_url": f"https://www.linkedin.com/feed/update/{post_id}",
                        "message": share_content.get("shareCommentary", {}).get(
                            "text", ""
                        ),
                        "account_id": account.id,
                        "click_count": post_data_reaction[0]
                        if post_data_reaction
                        else 0,
                        "like_count": post_data_reaction[1]
                        if post_data_reaction
                        else 0,
                        "comment_count": post_data_reaction[2]
                        if post_data_reaction
                        else 0,
                        "share_count": post_data_reaction[3]
                        if post_data_reaction
                        else 0,
                        "engagement": post_data_reaction[4]
                        if post_data_reaction
                        else 0,
                        "impression_count": post_data_reaction[5]
                        if post_data_reaction
                        else 0,
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
                update_account_data = {
                    "post_account_ids": post_accounts,
                }

                entity_statistics = account._get_entity_share_statistics()
                if len(entity_statistics) > 0:
                    share_statistics = entity_statistics[0].get(
                        "totalShareStatistics", {}
                    )
                    update_account_data.update(
                        {
                            "click_count": share_statistics.get("clickCount", 0),
                            "like_count": share_statistics.get("likeCount", 0),
                            "impression_count": share_statistics.get(
                                "impressionCount", 0
                            ),
                            "comment_count": share_statistics.get("commentCount", 0),
                            "share_count": share_statistics.get("shareCount", 0),
                            "engagement": round(
                                share_statistics.get("engagement", 0), 2
                            ),
                        }
                    )

                account.write(update_account_data)
        return self._get_account_statistics(statistics=statistics)

    def _get_account_statistics(self, statistics=None):
        data = self.search_read(
            [("media_type", "=", "linkedin")],
            [
                "name",
                "company_id",
                "media_id",
                "account_url",
                "impression_count",
                "interactions_count",
                "engagement",
            ],
        )
        if statistics:
            data = list(
                itertools.chain(
                    statistics,
                    data,
                )
            )
        return data

    def _get_default_filter_date(self, start_date, end_date, time_date=False):
        start = start_date or (datetime.now() - relativedelta(months=1))
        end = end_date or (datetime.now())
        if time_date:
            return _generate_timestamps(date_start=start, date_end=end)
        return start, end

    def _get_chart_account_statistics(
        self, start_date=None, end_date=None, granularity="WEEK"
    ):
        data = super()._get_chart_account_statistics(start_date, end_date, granularity)
        account_ids = self or self.search([("media_type", "=", "linkedin")])
        data_linkedin = []
        for account in account_ids:
            start_date_time, end_date_time = account._get_default_filter_date(
                start_date, end_date, time_date=True
            )
            start_date, end_date = account._get_default_filter_date(
                start_date, end_date
            )

            params_fields = ["q", "organizationalEntity", "timeIntervals", "count"]
            params_values = {
                "q": "organizationalEntity",
                "organizationalEntity": f"{_URN_ORGANIZATION_LINKEDIN}"
                f"{account.linkedin_account_id}",
                "timeIntervals": f"(timeRange:(start:{start_date_time},"
                f"end:{end_date_time})"
                f",timeGranularityType:{granularity})",
                "count": 100,
            }
            params_values_char_ignore = {"timeIntervals": [{"all": ":"}]}
            account_share_statistics = account._get_entity_share_statistics(
                params_fields=params_fields,
                params_values=params_values,
                params_values_char_ignore=params_values_char_ignore,
            )
            freq = "W-MON"
            if granularity == "DAY":
                freq = "D"
            elif granularity == "MONTH":
                freq = "ME"
            chart_weeks = get_weeks(start_date, end_date, freq=freq)

            if account_share_statistics:

                def map_chart_data(share_statistics, label, key_data="clickCount"):
                    dataset = {
                        "pointStyle": "circle",
                        "pointRadius": 10,
                        "pointHoverRadius": 15,
                        "label": _(label),
                        "data": [
                            share_statistic.get("totalShareStatistics", {}).get(
                                key_data, 0
                            )
                            for share_statistic in share_statistics
                        ],
                    }
                    return dataset

                data_linkedin.append(
                    {
                        "id": account.id,
                        "name": account.name,
                        "chartLabel": _("Statistics (Weeks)"),
                        "labels": [week for week in chart_weeks],
                        "datasets": [
                            map_chart_data(
                                account_share_statistics, "Clicks", "clickCount"
                            ),
                            map_chart_data(
                                account_share_statistics, "Shares", "shareCount"
                            ),
                            map_chart_data(
                                account_share_statistics, "Likes", "likeCount"
                            ),
                            map_chart_data(
                                account_share_statistics, "Comments", "commentCount"
                            ),
                            map_chart_data(
                                account_share_statistics,
                                "Impressions",
                                "impressionCount",
                            ),
                            map_chart_data(
                                account_share_statistics, "Engagement", "engagement"
                            ),
                        ],
                    }
                )
        return list(itertools.chain(data, data_linkedin))

    def _get_campaigns(self, start_date=None, end_date=None, campaign_ids=None):
        start_time, end_time = _generate_timestamps(start_date, end_date)
        param_values = {
            "q": "search",
            "search": f"(startDate:(values:{start_time}),"
            f"endDate:(values:{end_time}),test:true)",
            "fields": _FIELDS_CAMPAIGN_LINKEDIN,
            "count": 100,
        }
        params_values_char_ignore = {"search": [{"all": ":"}]}
        if campaign_ids:
            search_campaign = param_values["search"].strip("()")
            param_values[
                "search"
            ] = f"({search_campaign},campaigns:(values:List({','.join(campaign_ids)})))"
            params_values_char_ignore = {"search": [{"1,2,3,4,5,6,7": ":"}]}
        response = self._request_linkedin(
            endpoint="/adCampaignsV2",
            headers=self.media_id._get_linkedin_headers(self.access_token),
            params_fields=["q", "search", "fields", "count"],
            params_values=param_values,
            params_values_char_ignore=params_values_char_ignore,
            return_json=False,
            linkedin_v2=True,
        )

        if response.status_code == 200:
            campaigns = response.json().get("elements", [])
        else:
            raise ValidationError(f"Error in get campaigns: {response.json()}")
        return campaigns

    def _get_statistics(self, ads_ids=None, start_date=None, end_date=None):
        start_date, end_date = self._get_default_filter_date(start_date, end_date)
        start_date = (
            start_date.strftime("%Y-%m-%d").split("-")
            if not isinstance(start_date, str)
            else start_date
        )
        parse_start_date = "(year:{},month:{},day:{})".format(
            start_date[0],
            int(start_date[1]),
            int(start_date[2]),
        )
        end_date = (
            end_date.strftime("%Y-%m-%d").split("-")
            if not isinstance(end_date, str)
            else end_date
        )
        parse_end_date = (
            f"(year:{end_date[0]},month:{int(end_date[1])},day:{int(end_date[2])})"
        )
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
        if ads_ids:
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

    def _get_statistics_ads(self, ads_ids, start_date, end_date):
        return self._get_statistics(
            ads_ids=ads_ids, start_date=start_date, end_date=end_date
        )

    def _load_ads(self, start_date=None, end_date=None):
        start_date, end_date = self._get_default_filter_date(start_date, end_date)
        response = self._request_linkedin(
            endpoint="/adCreativesV2",
            headers=self.media_id._get_linkedin_headers(self.access_token),
            params_fields=["q", "search", "fields", "count"],
            params_values={
                "q": "search",
                "search": "(test:true)",
                "fields": "id,reference,test,campaign,"
                "changeAuditStamps,servingStatuses",
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

        # STATISTICS
        ads_ids = list(map(lambda x: x["id"], ads))
        ads_statistics = self._get_statistics_ads(
            ads_ids, start_date=None, end_date=None
        )

        # CAMPAIGNS
        campaign_ids = list(map(lambda x: x["campaign"], ads))
        ads_campaigns = self._get_campaigns(
            start_date, end_date, campaign_ids=campaign_ids
        )

        # POSTS
        post_ids = list(
            map(
                lambda x: x["reference"],
                list(filter(lambda x: x.get("reference", False), ads)),
            )
        )
        ads_ugc_posts = self._get_posts(
            **{"params_fields": ["ids"], "params_values": {"ids": post_ids}}
        )

        ads_parse = []
        for ad in ads:
            statistic = list(
                filter(
                    lambda x: f"urn:li:sponsoredAccount:{ad['id']}" in x["pivotValues"],
                    ads_statistics,
                )
            )
            campaign = list(
                filter(
                    lambda x: int(ad["campaign"].split(":")[-1]) == x["id"],
                    ads_campaigns,
                )
            )
            post = {}
            if ad.get("reference", False):
                post = {
                    "id": ads_ugc_posts[ad["reference"]]["id"],
                    "name": ads_ugc_posts[ad["reference"]]
                    .get("specificContent", {})
                    .get("com.linkedin.ugc.ShareContent", {})
                    .get("shareCommentary", {})
                    .get("text", ""),
                }
            account_id = campaign[0]["account"].split(":")[-1]
            ad.update(
                {
                    "media_type": self.media_type,
                    "statistic": statistic[0] if len(statistic) > 0 else {},
                    "campaign": campaign[0] if len(campaign) > 0 else {},
                    "created": convert_to_date(
                        miliseconds=ad["changeAuditStamps"]["created"]["time"],
                        expire_date=False,
                        format_date="%d/%m/%Y",
                    ),
                    "status": ", ".join(ad["servingStatuses"]),
                    "post": post,
                    "url": f"{_URL_LINKEDIN}{account_id}/"
                    f"creatives?creativeIds={url_quote([ad['id']])}",
                }
            )
            ads_parse.append(ad)
        return ads_parse

    def _load_ads_accounts(self):
        ads = super()._load_ads_accounts()
        account_ids = self.search([("media_type", "=", "linkedin")])
        for account in account_ids:
            ads_linkedin = account._load_ads()
            ads = list(itertools.chain(ads, ads_linkedin))
        return {
            "ads": ads,
        }
