from django.contrib import admin
from django.urls import path

from django_admin_shellx.views import TerminalView, toggle_favorite

from .models import TerminalCommand


@admin.register(TerminalCommand)
class TerminalCommandAdmin(admin.ModelAdmin):
    readonly_fields = ("created", "modified")
    list_display = ("command", "created_by", "execution_count")
    fields = (
        "created",
        "modified",
        "prompt",
        "command",
        "created_by",
        "execution_count",
        "favorite",
    )

    def get_urls(self):

        urls = super().get_urls()
        urls.insert(
            0,
            path(
                "toggle_favorite/<int:pk>/",
                self.admin_site.admin_view(toggle_favorite),
                name="django_admin_shellx_terminalcommand_toggle_favorite",
            ),
        )
        urls.insert(
            0,
            path(
                "terminal/",
                self.admin_site.admin_view(TerminalView.as_view()),
                name="django_admin_shellx_terminalcommand_terminal",
            ),
        )
        return urls
