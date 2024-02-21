from django.apps import AppConfig


class DjangoWebRepl(AppConfig):
    name = "django_custom_admin"
    verbose_name = "Django Web Repl"

    def ready(self):
        try:
            # pylint: disable=unused-import
            import django_custom_admin.signals
        except ImportError:
            pass
