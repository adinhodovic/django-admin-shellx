from django.conf import settings
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.html import format_html, mark_safe
from django.views.generic.base import TemplateView

from .models import TerminalCommand


class TerminalView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):

    def test_func(self):
        super_user_required = getattr(
            settings, "DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY", True
        )

        if super_user_required and not self.request.user.is_superuser:
            return False
        return True

    def get_template_names(self):  # pyright: ignore [reportIncompatibleMethodOverride]
        if self.request.headers.get("Hx-Request") == "true":
            template_name = "django_admin_shellx/terminal_table.html"
        else:
            template_name = "django_admin_shellx/terminal.html"

        return [template_name]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Add admin site context to the template
        context.update(admin.site.each_context(self.request))

        ws_port = getattr(settings, "DJANGO_ADMIN_SHELLX_WS_PORT", None)
        context["ws_port"] = ws_port

        commands = TerminalCommand.objects.order_by("-execution_count")
        favorite = self.request.GET.get("favorite", None)
        if favorite:
            commands = commands.filter(favorite=bool(favorite))

        username = self.request.GET.get("username", None)
        if username and username != "All":
            commands = commands.filter(created_by__username=username)

        search = self.request.GET.get("search", None)
        if search:
            commands = commands.filter(command__icontains=search)

        commands = commands[:20]
        context["commands"] = commands

        usernames = (
            get_user_model()
            .objects.filter(
                id__in=TerminalCommand.objects.values_list("created_by_id").distinct()
            )
            .values_list("username", flat=True)
        )
        if self.request.user.username in usernames:
            usernames = [self.request.user.username] + [
                username
                for username in usernames
                if username != self.request.user.username
            ]
        context["usernames"] = usernames

        log_entries = LogEntry.objects.filter(
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

        context["log_entries"] = log_entries

        return context


@login_required
def toggle_favorite(request, pk):
    instance = get_object_or_404(TerminalCommand, pk=pk)

    super_user_required = getattr(settings, "DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY", True)
    if super_user_required and not request.user.is_superuser:
        raise PermissionDenied("Only superuser can toggle favorite")

    if request.method == "GET":
        # Toggle the 'favorite' field
        instance.favorite = not instance.favorite
        instance.save()

        color = "text-yellow-400" if instance.favorite else ""
        return HttpResponse(
            format_html(  # pyright: ignore [reportArgumentType]
                "<div class='tooltip' data-tip='Favorite Command'><i class='fa fa-star {}'></i></div>",
                mark_safe(color),
            )
        )

    return JsonResponse({"status": "error", "message": "Only GET requests are allowed"})
