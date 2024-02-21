from django.contrib.admin.apps import AdminConfig


class CustomAdminConfig(AdminConfig):
    default_site = "django_custom_admin_custom_admin.admin.CustomAdminSite"
