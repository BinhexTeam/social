# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SocialNetworkPostAccount(models.Model):
    _name = "social.network.post.account"
    _inherit = ["mail.thread", "mail.activity.mixin", "social.network.post.mixin"]
    _description = "Social Live Post"

    post_id = fields.Many2one("social.network.post", ondelete="restrict")
    active = fields.Boolean(default=True)
    account_id = fields.Many2one(
        "social.network.account", ondelete="restrict", required=True
    )
    media_id = fields.Many2one(
        "social.network.media", related="account_id.media_id", required=True
    )
    media_type = fields.Selection(related="media_id.media_type")

    state = fields.Selection(
        [
            ("ready", "Ready"),
            ("posting", "Posting"),
            ("posted", "Posted"),
            ("failed", "Failed"),
        ],
        default="ready",
    )
    published_date = fields.Datetime()
    published = fields.Boolean(default=True)
    message = fields.Text(required=True)
    comments_count = fields.Integer()
    likes_count = fields.Integer()
    video_ids = fields.Many2many(
        "ir.attachment",
        relation="social_network_post_account_video_rel",
        column1="post_id",
        column2="video_id",
        ondelete="restrict",
    )

    image_ids = fields.Many2many(
        "ir.attachment",
        column1="post_id",
        column2="image_id",
        ondelete="restrict",
        relation="social_network_post_account_image_rel",
    )
    failed_description = fields.Html()
    post_account_url = fields.Char()
    author = fields.Char(related="account_id.name")
    actor_urn = fields.Char()

    def action_like_post(self, author_urn=None):
        return {"success": True, "message": ""}

    def action_like_comment(self, author_urn=None):
        return {"success": True, "message": ""}

    def _action_post(self):
        """
        Post on social network
        """
        pass

    def _action_campaign_post(self, post_id):
        pass

    def delete_post_account(self):
        pass

    def filter_by_media_types(self, media_types):
        return self.env["social.network.post.account"].search(
            [
                ("media_type", "in", media_types),
                ("state", "in", ("ready", "failed")),
            ]
        )

    def get_comments(self):
        return []
