# Django Admin Shell

A Django Web shell

### Settings

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY | Allow only SuperUsers to access the admin shellx. | `boolean` | `True` | no |
| DJANGO_ADMIN_SHELLX_COMMAND | The default commands to use when opening the terminal. | `list[list[str]]` |  [["./manage.py", "shell_plus"], ["./manage.py", "shell"], ["/bin/bash"]] | no |
