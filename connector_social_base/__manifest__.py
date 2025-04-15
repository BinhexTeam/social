# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Connector Social Base",
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
        "views/utm_campaign_views.xml",
        "views/utm_group_campaign_views.xml",
        "views/social_network_action_client_views.xml",
        "views/res_config_settings_views.xml",
        "views/connector_social_base_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # LIBS
            "connector_social_base/static/src/lib/**/*.js",
            # GENERAL
            "connector_social_base/static/src/xml/**/*.xml",
            "connector_social_base/static/src/scss/**/*.scss",
            # MIXINS
            "connector_social_base/static/src/js/app/**/*.js",
            # SERVICES
            "connector_social_base/static/src/js/services/**/*.js",
            # COMPONENTS
            "connector_social_base/static/src/components/**/*.xml",
            "connector_social_base/static/src/components/**/*.js",
            "connector_social_base/static/src/components/**/*.scss",
            # VIEWS
            "connector_social_base/static/src/js/views/**/*.xml",
            "connector_social_base/static/src/js/views/**/*.scss",
            "connector_social_base/static/src/js/views/**/*.js",
        ],
    },
    "external_dependencies": {
        "python": [
            "pandas",
        ],
    },
}
