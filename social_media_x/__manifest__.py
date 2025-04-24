# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Social Media X",
    "summary": """Integration of the X social network.""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Binhex <https://www.binhex.cloud>,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/social",
    "depends": [
        "base",
        "social_media_base",
    ],
    "data": [
        "data/social_network_media_data.xml",
        "views/res_config_settings_views.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # COMPONENTS
            "social_media_x/static/src/components/**/*.js",
            # SERVICES
            "social_media_x/static/src/js/services/**/*.js",
        ],
    },
    "external_dependencies": {
        "python": [
            "tweepy",
        ],
    },
}
