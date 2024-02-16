from django.apps import AppConfig


class DjangoWebRepl(AppConfig):
    name = "django_web_repl"

    def ready(self):
        try:
            # pylint: disable=unused-import
            import django_web_repl.signals
        except ImportError:
            pass
