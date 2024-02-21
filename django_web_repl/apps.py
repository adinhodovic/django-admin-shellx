from django.apps import AppConfig


class DjangoWebRepl(AppConfig):
    name = "django_web_repl"
    verbose_name = "Django Web Repl"

    def ready(self):
        try:
            # pylint: disable=unused-import
            import django_web_repl.signals
        except ImportError:
            pass
