from django.contrib import admin
from django.urls import reverse


class CustomAdminSite(admin.AdminSite):  # pylint: disable=too-few-public-methods

    def get_app_list(self, request, app_label=None):
        app_list = super().get_app_list(request, app_label)

        for app in app_list:
            if app["app_label"] == "django_admin_shellx":
                app["models"].insert(
                    0,
                    {
                        "name": "Terminal",
                        "object_name": "Terminal",
                        "admin_url": f"{reverse('admin:django_admin_shellx_terminalcommand_changelist')}terminal/",
                        "view_only": True,
                    },
                )
                break

        return app_list
