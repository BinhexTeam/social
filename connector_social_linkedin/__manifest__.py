# Copyright 2025 Binhex <https://www.binhex.cloud>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

{
    "name": "Connector Social Linkedin",
    "summary": """Integration of the LinkedIn social network.""",
    "version": "17.0.1.0.0",
    "license": "AGPL-3",
    "author": "Binhex <https://www.binhex.cloud>,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/social",
    "depends": [
        "base",
        "connector_social_base",
    ],
    "data": [
        "data/social_network_media_data.xml",
        "views/res_config_settings_views.xml",
        "views/social_network_post_account_views.xml",
        "views/connector_social_linkedin_menus.xml",
    ],
    "assets": {
        "web.assets_backend": [
            # COMPONENTS
            "connector_social_linkedin/static/src/js/components/**/*.js",
            # SERVICES
            "connector_social_linkedin/static/src/js/services/**/*.js",
            # KANBAN
            "connector_social_linkedin/static/src/js/views/**/*.js",
        ],
    },
    "external_dependencies": {
        "python": [
            "linkedin-api-client",
        ],
    },
}
