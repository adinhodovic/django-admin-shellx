from django.conf import settings
from django.contrib import admin
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.views.generic.base import TemplateView


class TerminalView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = "django_web_repl/terminal.html"

    def test_func(self):
        super_user_required = getattr(settings, "DJANGO_WEB_REPL_SUPERUSER_ONLY", False)
        if super_user_required and not self.request.user.is_superuser:
            return False
        return True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))
        return context
