from django.contrib import admin
from django.urls import path

from django_web_repl.views import TerminalView


class CustomAdminSite(admin.AdminSite):  # pylint: disable=too-few-public-methods

    def get_urls(self):

        urls = super().get_urls()
        urls.insert(
            0,
            path(
                "terminal/",
                self.admin_view(TerminalView.as_view()),
                name="terminal",
            ),
        )
        return urls

    def get_app_list(self, request, app_label=None):
        app_list = [
            {
                "name": "Terminal",
                "app_label": "terminal",
                "models": [
                    {
                        "name": "Terminal",
                        "object_name": "Terminal",
                        "admin_url": "/admin/terminal/",
                        "view_only": True,
                    }
                ],
            }
        ] + super().get_app_list(request)
        return app_list
