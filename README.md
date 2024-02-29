# Django Admin Shell

A Django Web Shell using Xterm.js and Django Channels.

Note: This package depends on websockets therefore you'll need to use an ASGI application to use it. If you are not using Django channels then read through the official [Channels' documentation on installing Channels](https://channels.readthedocs.io/en/latest/installation.html), also see the [Channels' documentation on running ASGI applications](https://channels.readthedocs.io/en/latest/deploying.html).

## Features

- Fully responsive terminal using Xterm.js.
- Accessible through the admin.
- Authentication with Django auth, configurable to allow only superusers.
- The commands written are tied to a user.
- Saves command in a new model and create favorite commands.
- Filterable command history.
- LogEntry of all commands ran.
- Custom admin site to add Terminal links to the admin.

## Installation

Install the package using pip:

```bash
pip install django-admin-shellx
```

Add `django_admin_shellx`, `channels` or `daphne` and `django_admin_shellx_custom_admin` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    'daphne', # If you are using daphne, import it first
    # ...
    'django_admin_shellx',
    # ...
]
```

Add your ASGI application to your settings:

```python
ASGI_APPLICATION = "config.asgi.application"

# Optional
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [env("REDIS_URL")],
        },
    },
}
```

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
```

If you do not have an ASGI application, you'll need to create one. You can use the `channels` package to do so:

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

Note: Daphne replaces `runserver` to run as a ASGI application. If you are using Daphne, you'll need to import it first in your ASGI application.

Lastly, we'll need to use a custom admin site to add terminal links to the admin, add the following to your `INSTALLED_APPS`:

```python
installed_apps = [
    ...
    'django_admin_shellx_custom_admin.apps.DjangoAdminShellXCustomAdminConfig',
]
```

The above is optional and only adds a `view` button to the admin that links to the terminal. Otherwise, there will not be a link since it's not a model and can not be added to the admin. The terminal will either be accessible through the path `/admin/django_admin_shellx/terminalcommand/terminal/` and if you use the custom admin site, it will be accessible through a link in the admin.

## Usage

Head over to the admin and click on the `Terminal` link. You'll be presented with a terminal that you can use to run commands. The default commands are `./manage.py shell_plus`, `./manage.py shell` and `/bin/bash`. You can change the default commands by setting the `DJANGO_ADMIN_SHELLX_COMMAND` setting.

Each command is saved in the database and can be accessed through the admin. You can also add new commands through the admin and favorite existing commands. Each command ran is also saved as a [LogEntry](https://docs.djangoproject.com/en/dev/ref/contrib/admin/#logentry-objects).

### ASGI Notes

As mentioned previously, read through the official [Channels' documentation on installing Channels](https://channels.readthedocs.io/en/latest/installation.html), also see the [Channels' documentation on running ASGI applications](https://channels.readthedocs.io/en/latest/deploying.html). I'll add small snippets to help you get started.

In the guide above `daphne` is used as the ASGI application and this will replace the command `runserver` to run as a ASGI application. In production, you'll need to run `daphne` instead of `gunicorn` to use the websockets. An example is shown below:

```bash
daphne config.asgi:application -b 127.0.0.1 -p 80
```

Alternatively, you can run your ASGI application on a separate port and run your WSGI application as per default.

```bash
daphne config.asgi:application -b 127.0.0.1 -p 8001
gunicorn -b 127.0.0.1:80 config.wsgi
```

You can also replace `daphne` with `channels` if you want to for example use `runserver_plus` which does not work with `daphne`. Then, you'll need to run both an ASGI and WSGI application locally.

```bash
./manage.py runserver -p 8000
daphne config.asgi:application -b 127.0.0.1 -p 8001
```

### Settings

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY | Allow only SuperUsers to access the admin shellx. | `boolean` | `True` | no |
| DJANGO_ADMIN_SHELLX_COMMANDS | The default commands to use when opening the terminal. | `list[list[str]]` |  [["./manage.py", "shell_plus"], ["./manage.py", "shell"], ["/bin/bash"]] | no |
| DJANGO_ADMIN_SHELLX_WS_PORT | The port to use for the websocket. | `int` | None | no |
