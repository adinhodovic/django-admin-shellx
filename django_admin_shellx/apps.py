from django.apps import AppConfig


class DjangoAdminShellX(AppConfig):
    name = "django_admin_shellx"
    verbose_name = "Django Admin ShellX"

    def ready(self):
        try:
            # pylint: disable=unused-import, import-outside-toplevel
            import django_admin_shellx.signals
        except ImportError:
            pass
