from django.contrib import admin
from django.contrib.admin.views.decorators import staff_member_required
from django.views.generic.base import TemplateView


class TerminalView(TemplateView):
    template_name = "django_web_repl/terminal.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update(admin.site.each_context(self.request))
        return context
