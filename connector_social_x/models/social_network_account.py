# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
import io
import itertools
import logging

import requests
import tweepy

from odoo import fields, models

from ..social_x_utils import _get_oauth

_logger = logging.getLogger(__name__)


class SocialNetworkAccount(models.Model):
    _inherit = "social.network.account"

    x_access_token_oauth2 = fields.Char(help="Read tweets")
    x_access_token_oauth1 = fields.Char(help="Post, like, comment, answer")
    x_access_secret_oauth1 = fields.Char()
    x_account_id = fields.Char()

    def _fields_account_url(self):
        return super()._fields_account_url() + [
            (
                "x_account_id",
                f"https://x.com/{self.username}",
            )
        ]

    def _get_access_token_oauth2(self):
        api_key, api_secret = self._get_account_api(media_type="x")
        credentials = f"{api_key}:{api_secret}".encode()
        b64_credentials = base64.b64encode(credentials).decode("utf-8")
        url = "https://api.twitter.com/oauth2/token"
        headers = {
            "Authorization": f"Basic {b64_credentials}",
            "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
        }
        data = {"grant_type": "client_credentials"}

        response = requests.post(url, headers=headers, data=data, timeout=10)
        token = response.json().get("access_token", False)
        return token

    def _get_access_token(self, kwargs):
        url = "https://api.twitter.com/oauth/access_token"
        api_key, api_secret = self._get_account_api(media_type="x")
        auth = _get_oauth(api_key, api_secret, request_access_token=kwargs)
        oauth_verifier = kwargs.get("oauth_verifier")
        response = requests.post(
            url, auth=auth, data={"oauth_verifier": oauth_verifier}, timeout=10
        )
        access_tokens = dict(x.split("=") for x in response.text.split("&"))
        access_token = access_tokens["oauth_token"]
        access_token_secret = access_tokens["oauth_token_secret"]
        return access_token, access_token_secret

    def get_client_api(
        self,
        client_api=True,
        x_access_token_oauth1=None,
        x_access_secret_oauth1=None,
        bearer_token=None,
    ):
        api_key, api_secret = self._get_account_api(media_type="x")
        if client_api:
            return tweepy.Client(
                bearer_token=bearer_token,
                consumer_key=api_key,
                consumer_secret=api_secret,
                access_token=x_access_token_oauth1 or self.x_access_token_oauth1,
                access_token_secret=x_access_secret_oauth1
                or self.x_access_secret_oauth1,
            )
        auth = tweepy.OAuth1UserHandler(
            consumer_key=api_key,
            consumer_secret=api_secret,
            access_token=x_access_token_oauth1 or self.x_access_token_oauth1,
            access_token_secret=x_access_secret_oauth1 or self.x_access_secret_oauth1,
        )
        return tweepy.API(auth)

    def create_account_x(self, x_access_token_oauth1, x_access_secret_oauth1):
        client = self.get_client_api(
            x_access_token_oauth1=x_access_token_oauth1,
            x_access_secret_oauth1=x_access_secret_oauth1,
        )
        try:
            data = client.get_me().data
            values = {
                "x_account_id": data.id,
                "name": data.name,
                "username": data.username,
                "media_id": self.env.ref(
                    "connector_social_x.social_network_media_x"
                ).id,
                "x_access_token_oauth1": x_access_token_oauth1,
                "x_access_secret_oauth1": x_access_secret_oauth1,
            }
            access_token_oauth2 = self._get_access_token_oauth2()
            if access_token_oauth2:
                values.update({"x_access_token_oauth2": access_token_oauth2})
            self.create(values)
        except Exception as e:
            _logger.error(f"Error Request Client Me: {e}")

    def _prepare_medias_for_tweet(self, image_ids=None, image_datas=None):
        media_ids = []
        if image_datas:
            image_ids = [image_datas.split(",")[-1]]
        api = self.get_client_api(client_api=False)
        for image in image_ids:
            image_file = io.BytesIO(
                base64.b64decode(image.datas)
                if not isinstance(image, str)
                else base64.b64decode(image)
            )
            media = api.media_upload(
                filename=(image.name if not isinstance(image, str) else False)
                or "imagen.jpg",
                file=image_file,
            )
            media_ids.append(media.media_id)
        return media_ids

    def create_tweet(self, message, image_ids):
        client_api = self.get_client_api()
        try:
            tweet = client_api.create_tweet(
                text=message, media_ids=self._prepare_medias_for_tweet(image_ids)
            )
            return tweet.data.get("id", False)
        except Exception as e:
            _logger.error(f"Error Request Client Tweet: {e}")

    def _update_posts_statistics(self, update_all_accounts=False):
        statistics = super()._update_posts_statistics(update_all_accounts)
        PostAccount = self.env["social.network.post.account"]
        account_ids = (
            self.search([("media_type", "=", "x")]) if update_all_accounts else self
        )
        try:
            for account in account_ids:
                post_accounts = []
                client_api = self.get_client_api(
                    bearer_token=account.x_access_token_oauth2
                )
                response = client_api.get_users_tweets(
                    id=account.x_account_id,
                    max_results=100,
                    tweet_fields=[
                        "id",
                        "text",
                        "created_at",
                        "author_id",
                        "public_metrics",
                        "attachments",
                    ],
                    exclude=["retweets", "replies"],
                )
                if not response.data:
                    _logger.error("Get Tweets: {}".format("\n".join(response.errors)))
                    return statistics

                for val_x in response.data:
                    post_account = PostAccount.search(
                        [("x_post_account_id", "=", val_x.id)]
                    )
                    message = val_x.text.split(" ")
                    data = {
                        "x_post_account_id": val_x.get("id"),
                        "post_account_url": message[1],
                        "message": message[0],
                        "account_id": account.id,
                        "likes_count": 0,
                        "comments_count": 0,
                        "actor_urn": val_x.author_id,
                    }

                    if not post_account:
                        post_accounts.append((0, 0, data))
                    else:
                        post_accounts.append((1, post_account.id, data))
                if len(post_accounts) > 0:
                    account.write({"post_account_ids": post_accounts})

        except Exception as e:
            _logger.error(f"Error Get Tweets: {e}")
        return list(
            itertools.chain(
                statistics,
                self.search_read(
                    [("media_type", "=", "x")],
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
