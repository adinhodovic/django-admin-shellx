# Django Admin Shell

A Django Web Shell using Xterm.js and Django Channels.

## Installation

Install the package using pip:

```bash
pip install django-admin-shellx
```

Add `django_admin_shellx`, `channels` or `daphne` and `django_admin_shellx_custom_admin` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    `daphne`, # If you are using daphne, import it first
    # ...
    'django_admin_shellx',
    # ...
]

Since the package uses websockets you'll need to add the url patterns to your ASGI application:

```python

...

from django_admin_shellx.urls import websocket_urlpatterns

# pylint: disable=unused-import,wrong-import-position
import django_admin_shellx.urls

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)

If you do not have an ASGI application, you'll need to create one. You can use the `channels` package to do so.:

```python
# settings/asgi.py
import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from django_admin_shellx.urls import websocket_urlpatterns

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings")
# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing code that may import ORM models.
django_asgi_app = get_asgi_application()

# pylint: disable=unused-import,wrong-import-position
import django_admin_shellx.urls

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
```

Note: Daphne replaces runserver to run as a ASGI application. If you are using Daphne, you'll need to import it first in your ASGI application.

```bash

Lastly, we'll need to add the custom admin to add terminal links to the admin by using a custom admin class, add the following to your `INSTALLED_APPS`:

```python
installed_apps = [
    ...
    'django_admin_shellx_custom_admin.apps.DjangoAdminShellXCustomAdminConfig',
]
```

The above is optional and only adds a `view` button to the admin that links to the shell. Otherwise, there will not be a link since it's not a Model and can not be added to the admin. The terminal will either be accessible through the path `/admin/django_admin_shellx/terminalcommand/terminal/` or through the link in the admin.

## Usage

Head over to the admin and click on the `Terminal` link. You'll be presented with a terminal that you can use to run commands. The default commands are `./manage.py shell_plus`, `./manage.py shell` and `/bin/bash`. You can change the default commands by setting the `DJANGO_ADMIN_SHELLX_COMMAND` setting.

Each command is saved in the database and can be accessed through the admin. You can also add new commands through the admin and favorite existing commands. Each command ran is also saved as a [LogEntry](https://docs.djangoproject.com/en/dev/ref/contrib/admin/#logentry-objects)

### ASGI Notes


### Settings

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY | Allow only SuperUsers to access the admin shellx. | `boolean` | `True` | no |
| DJANGO_ADMIN_SHELLX_COMMAND | The default commands to use when opening the terminal. | `list[list[str]]` |  [["./manage.py", "shell_plus"], ["./manage.py", "shell"], ["/bin/bash"]] | no |
