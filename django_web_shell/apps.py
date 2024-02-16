from django.apps import AppConfig


class DjangoWebShellConfig(AppConfig):
    name = 'django_web_shell'

    def ready(self):
        try:
            # pylint: disable=unused-import
            import django_web_shell.signals
        except ImportError:
            pass
