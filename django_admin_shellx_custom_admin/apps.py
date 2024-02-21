from django.contrib.admin.apps import AdminConfig


class CustomAdminConfig(AdminConfig):
    default_site = "django_admin_shellx_custom_admin.admin.CustomAdminSite"
