import pytest
from django.urls import reverse

from .factories import TerminalCommandFactory

pytestmark = pytest.mark.django_db


def test_list_commands_anonymous(client):
    res = client.get(reverse("admin:django_admin_shellx_terminalcommand_terminal"))
    assert res.status_code == 302
    assert (
        res.url
        == "/admin/login/?next=/admin/django_admin_shellx/terminalcommand/terminal/"
    )


def test_list_commands_staff_user(user_client):
    # Requires super user by default
    user_client.user.is_staff = True
    user_client.user.save()
    res = user_client.get(reverse("admin:django_admin_shellx_terminalcommand_terminal"))
    assert res.status_code == 403


def test_list_commands(admin_client):
    tc = TerminalCommandFactory()
    res = admin_client.get(
        reverse("admin:django_admin_shellx_terminalcommand_terminal")
    )

    assert res.status_code == 200
    assert res.context["commands"]
    assert res.context["commands"][0].command == tc.command


def test_list_favorite_commands(admin_client):
    tc = TerminalCommandFactory(command="test", favorite=True)
    TerminalCommandFactory(command="ls", favorite=False)
    res = admin_client.get(
        reverse("admin:django_admin_shellx_terminalcommand_terminal"),
        {"favorite": "true"},
    )

    assert res.status_code == 200
    assert res.context["commands"]
    assert len(res.context["commands"]) == 1
    assert res.context["commands"][0].command == tc.command


def test_list_search_commands(admin_client):
    tc = TerminalCommandFactory(command="test")
    TerminalCommandFactory(command="ls")
    res = admin_client.get(
        reverse("admin:django_admin_shellx_terminalcommand_terminal"),
        {"search": "test"},
    )

    assert res.status_code == 200
    assert res.context["commands"]
    assert len(res.context["commands"]) == 1
    assert res.context["commands"][0].command == tc.command


def test_list_user_commands(admin_client):
    tc = TerminalCommandFactory()
    TerminalCommandFactory()
    res = admin_client.get(
        reverse("admin:django_admin_shellx_terminalcommand_terminal"),
        {"username": tc.created_by.username},
    )

    assert res.status_code == 200
    assert res.context["commands"]
    assert len(res.context["commands"]) == 1
    assert res.context["commands"][0].command == tc.command
