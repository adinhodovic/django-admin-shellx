from django.contrib.admin.apps import AdminConfig


class CustomAdminConfig(AdminConfig):
    default_site = "django_web_repl_custom_admin.admin.CustomAdminSite"
