# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import itertools
import logging

from odoo import _, fields, models

_logger = logging.getLogger(__name__)


class SocialNetworkPostAccount(models.Model):
    _inherit = "social.network.post.account"

    x_post_account_id = fields.Char()
    x_post_url = fields.Char()

    def _action_post(self):
        res = super()._action_post()
        post_accounts = self.filter_by_media_types(["x"])
        for post_account in post_accounts:
            post_account_id = post_account.account_id.create_tweet(
                message=post_account.message,
                image_ids=post_account.image_ids,
            )
            if post_account_id:
                post_account.write(
                    {
                        "x_post_account_id": post_account_id,
                        "post_account_url": f"https://x.com/{self.account_id.username}/status/{post_account_id}",
                        "published_date": fields.Datetime.now(),
                        "state": "posted",
                    }
                )
        return res

    def get_comments(self):
        data = super().get_comments()
        comments = []
        if "x" == self.account_id.media_type:
            try:
                client_api = self.account_id.get_client_api(
                    bearer_token=self.account_id.x_access_token_oauth2
                )
                query = (
                    f"conversation_id:{self.x_post_account_id} "
                    f"to:{self.account_id.username}"
                )
                response = client_api.search_recent_tweets(
                    query=query, tweet_fields=["id", "text", "author_id", "created_at"]
                )
                comments = [
                    {
                        "id": comment.data.get("id"),
                        "text": comment.data.get("text").split(" ")[0],
                        "actor": comment.data.get("author_id", {}),
                        "published_time": comment.data.get("created_at", ""),
                        "images_url": [
                            val.get("media_key", {})
                            for val in comment.get("includes", {}).get("media", {})
                        ],
                    }
                    for comment in response
                ]

            except Exception as e:
                _logger.error(f"Error Get Comments for Tweet: {e}")
        return list(itertools.chain(data, comments))

    def create_x_comment(self, comment, image_base64):
        if "x" == self.account_id.media_type:
            try:
                client_api = self.account_id.get_client_api()
                media_ids = []
                if image_base64:
                    media_ids = self.account_id._prepare_medias_for_tweet(
                        image_datas=image_base64
                    )
                client_api.create_tweet(
                    text=comment,
                    in_reply_to_tweet_id=self.x_post_account_id,
                    media_ids=media_ids,
                )
            except Exception as e:
                _logger.error(f"Error Comment Tweet: {e}")
                return {
                    "success": False,
                    "message": _(
                        "An error occurred while commenting, please try again later."
                    ),
                }

    def action_like_post(self, author_urn=None):
        res = super().action_like_post(author_urn)
        if self.media_id.media_type == "x":
            like_ok = False
            try:
                client_api = self.account_id.get_client_api()
                client_api.like(self.x_post_account_id)
                like_ok = True
            except Exception as e:
                _logger.error(f"Error Like Tweet: {e}")
            return {"success": like_ok, "message": ""}
        return res
