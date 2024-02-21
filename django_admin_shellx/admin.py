from django.contrib import admin
from django.urls import path, reverse

from django_admin_shellx.views import TerminalView

from .models import TerminalCommand


@admin.register(TerminalCommand)
class TerminalCommandAdmin(admin.ModelAdmin):
    list_display = ("command", "created_by", "execution_count")

    def get_urls(self):

        urls = super().get_urls()
        urls.insert(
            0,
            path(
                "terminal/",
                self.admin_site.admin_view(TerminalView.as_view()),
                name="terminal",
            ),
        )
        return urls
