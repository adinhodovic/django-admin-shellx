# Django Admin Shell

A Django Web Shell using Xterm.js and Django Channels.

Note: This package depends on websockets therefore you'll need to use an ASGI application to use it. If you are not using Django channels then read through the official [Channels' documentation on installing Channels](https://channels.readthedocs.io/en/latest/installation.html), also see the [Channels' documentation on running ASGI applications](https://channels.readthedocs.io/en/latest/deploying.html).

## Demo

![GIF](./images/django-admin-shellx-demo.gif)
_The demo is from [Django.wtf's](https://django.wtf/) admin._

## Features

- Fully responsive terminal using Xterm.js.
- Accessible through the admin.
- Authentication with Django auth, configurable to allow only superusers.
- The commands written are tied to a user.
- Saves command in a new model and create favorite commands.
- Filterable command history.
- LogEntry of all commands ran.
- Custom admin site to add Terminal links to the admin.
- Full screen mode.
- Working autocomplete.

## Installation

Install the package using pip:

```bash
pip install django-admin-shellx
```

Add `django_admin_shellx` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'django_admin_shellx',
    # ...
]
```

Since the package uses websockets you'll need to add the url patterns to your ASGI application:

```python
...
from django_admin_shellx.urls import websocket_urlpatterns

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(URLRouter(websocket_urlpatterns))
        ),
    }
)
```

Lastly, we'll need to use a custom admin site to add a link to the terminal, add the following to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    ...
    "django_admin_shellx",
    "django_admin_shellx_custom_admin.apps.CustomAdminConfig",
]
```

Ensure to remove the default `admin` app from the `INSTALLED_APPS` if you are using the custom admin site.

```python
INSTALLED_APPS = [
    ...
    # 'django.contrib.admin',
    ...
]
```

The above is optional and only adds a `view` button to the admin that links to the terminal. Otherwise, there will not be a link since it's not a model and can not be added to the admin. The terminal will either be accessible through the path `/admin/django_admin_shellx/terminalcommand/terminal/` and if you use the custom admin site, it will be accessible through a link in the admin.

## Usage

Head over to the admin and click on the `Terminal` link. You'll be presented with a terminal that you can use to run commands. The default commands are `./manage.py shell_plus`, `./manage.py shell` and `/bin/bash`. You can change the default commands by setting the `DJANGO_ADMIN_SHELLX_COMMAND` setting.

Each command is saved in the database and can be accessed through the admin. You can also add new commands through the admin and favorite existing commands. Each command ran is also saved as a [LogEntry](https://docs.djangoproject.com/en/dev/ref/contrib/admin/#logentry-objects).

### Settings

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY | Only allow superusers to access the admin shellx. | `boolean` | `True` | no |
| DJANGO_ADMIN_SHELLX_COMMANDS | The default commands to use when opening the terminal. | `list[list[str]]` |  [["./manage.py", "shell_plus"], ["./manage.py", "shell"], ["/bin/bash"]] | no |
| DJANGO_ADMIN_SHELLX_WS_PORT | The port to use for the websocket. | `int` | None | no |
