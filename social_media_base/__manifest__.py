# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Social Media Base",
    "summary": """Basic module for social media management.""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Binhex <https://www.binhex.cloud>,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/social",
    "depends": ["base", "web", "mail", "utm"],
    "data": [
        "security/ir.model.access.csv",
        "data/ir_cron_data.xml",
        "views/social_network_media_views.xml",
        "views/social_network_account_views.xml",
        "views/social_network_post_views.xml",
        "views/social_network_post_account_views.xml",
        "views/utm_group_campaign_views.xml",
        "views/social_network_action_client_views.xml",
        "views/res_config_settings_views.xml",
        "views/social_media_base_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # LIBS
            "social_media_base/static/src/lib/**/*.js",
            # GENERAL
            "social_media_base/static/src/xml/**/*.xml",
            "social_media_base/static/src/scss/**/*.scss",
            # MIXINS
            "social_media_base/static/src/js/app/**/*.js",
            # SERVICES
            "social_media_base/static/src/js/services/**/*.js",
            # COMPONENTS
            "social_media_base/static/src/components/**/*.xml",
            "social_media_base/static/src/components/**/*.js",
            "social_media_base/static/src/components/**/*.scss",
            # VIEWS
            "social_media_base/static/src/js/views/**/*.xml",
            "social_media_base/static/src/js/views/**/*.scss",
            "social_media_base/static/src/js/views/**/*.js",
        ],
    },
    "external_dependencies": {
        "python": [
            "pandas",
        ],
    },
}
