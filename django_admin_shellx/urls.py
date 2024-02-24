from django.urls import re_path

from . import consumers

app_name = "django_admin_shellx"

urlpatterns = []

websocket_urlpatterns = [
    re_path(
        r"ws/terminal/(?P<terminal_session>\w+)/$", consumers.TerminalConsumer.as_asgi()
    ),
]
