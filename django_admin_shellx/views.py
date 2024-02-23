from logging import warn

from django.conf import settings
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic.base import TemplateView

from .models import TerminalCommand


class TerminalView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "django_admin_shellx/terminal.html"

    def test_func(self):
        super_user_required = getattr(
            settings, "DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY", False
        )
        if super_user_required and not self.request.user.is_superuser:
            return False
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add admin site context to the template
        context.update(admin.site.each_context(self.request))

        most_used_commands = TerminalCommand.objects.order_by("-execution_count")[:20]
        favorite_commands = TerminalCommand.objects.filter(favorite=True).order_by(
            "-execution_count"
        )[:20]
        user_commands = TerminalCommand.objects.filter(
            created_by=self.request.user
        ).order_by("-execution_count")[:20]

        log_entries = admin.models.LogEntry.objects.filter(
            content_type__model="terminalcommand"
        ).order_by("-action_time")[:30]

        user_model = get_user_model()
        context["user_reverse_url"] = (
            f"admin:{user_model._meta.app_label}_{user_model._meta.model_name}_change"
        )
        for log in log_entries:
            log.user = user_model.objects.get(id=log.user_id)

            tc = TerminalCommand.objects.filter(id=log.object_id).first()
            if tc:
                log.command = tc

        context["most_used_commands"] = most_used_commands
        context["favorite_commands"] = favorite_commands
        context["user_commands"] = user_commands
        context["log_entries"] = log_entries

        return context
