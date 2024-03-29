import json
from asyncio import sleep
from asyncio.exceptions import CancelledError

import pytest
from channels.db import database_sync_to_async
from django.contrib.admin.models import LogEntry

from django_admin_shellx.consumers import TerminalConsumer
from django_admin_shellx.models import TerminalCommand

from .conftest import BASIC_BASH_COMMANDS, DefaultTimeoutWebsocketCommunicator

pytestmark = pytest.mark.django_db


@pytest.mark.asyncio
async def test_settings_custom_command(settings, superuser_logged_in):
    settings.DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY = False
    settings.DJANGO_ADMIN_SHELLX_COMMANDS = BASIC_BASH_COMMANDS
    communicator = DefaultTimeoutWebsocketCommunicator(
        TerminalConsumer.as_asgi(), "/testws/"
    )
    communicator.scope["user"] = superuser_logged_in
    connected, _ = await communicator.connect()
    assert connected

    # Ensure we go past the initial bash messages returned (shell startup)
    response = await communicator.receive_from()
    assert "bash-" in response

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_settings_default_shell_plus(settings, superuser_logged_in):
    settings.DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY = False
    communicator = DefaultTimeoutWebsocketCommunicator(
        TerminalConsumer.as_asgi(), "/testws/"
    )
    communicator.scope["user"] = superuser_logged_in
    connected, _ = await communicator.connect()
    assert connected

    # Ensure we go past the initial bash messages returned (shell startup)
    response = await communicator.receive_from()
    assert "Shell Plus" in response

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_closes_connection_on_exit(settings, superuser_logged_in):
    settings.DJANGO_ADMIN_SHELLX_COMMANDS = BASIC_BASH_COMMANDS
    communicator = DefaultTimeoutWebsocketCommunicator(
        TerminalConsumer.as_asgi(), "/testws/"
    )
    communicator.scope["user"] = superuser_logged_in
    connected, _ = await communicator.connect()
    assert connected

    # Ensure we go past the initial bash messages returned (shell startup)
    await communicator.receive_from()

    # Test sending text
    await communicator.send_to(
        text_data=json.dumps({"action": "input", "data": {"message": "exit"}})
    )
    response = await communicator.receive_from()
    assert response == '{"message": "exit"}'

    # Wait for the shell to close
    await communicator.wait()

    await communicator.send_to(
        text_data=json.dumps({"action": "input", "data": {"message": "ls"}})
    )
    with pytest.raises(CancelledError):
        await communicator.receive_from()


@database_sync_to_async
def get_log_entry():
    return LogEntry.objects.count(), LogEntry.objects.first()


@database_sync_to_async
def get_terminal_command():
    return TerminalCommand.objects.count(), TerminalCommand.objects.first()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_command_creates_objects(superuser_logged_in):
    communicator = DefaultTimeoutWebsocketCommunicator(
        TerminalConsumer.as_asgi(), "/testws/"
    )
    communicator.scope["user"] = superuser_logged_in
    connected, _ = await communicator.connect()
    assert connected

    # Ensure we go past the initial bash messages returned (shell startup)
    await communicator.receive_from()

    # Test sending text
    await communicator.send_to(
        text_data=json.dumps({"action": "save_history", "data": {"command": ">>> ls"}})
    )
    await communicator.receive_from()

    log_entry_count, log_entry = await get_log_entry()
    terminal_command_count, terminal_command = await get_terminal_command()

    assert log_entry_count == 1
    assert terminal_command_count == 1

    assert log_entry.user_id == superuser_logged_in.id
    assert log_entry.object_id == str(terminal_command.id)

    assert terminal_command.command == "ls"
    assert terminal_command.prompt == "django-shell"
    assert terminal_command.created_by_id == superuser_logged_in.id
    assert terminal_command.execution_count == 1

    await communicator.disconnect()


@pytest.mark.asyncio
@pytest.mark.django_db(transaction=True)
async def test_command_increments_execution_count(settings, superuser_logged_in):
    settings.DJANGO_ADMIN_SHELLX_COMMANDS = BASIC_BASH_COMMANDS
    communicator = DefaultTimeoutWebsocketCommunicator(
        TerminalConsumer.as_asgi(), "/testws/"
    )
    communicator.scope["user"] = superuser_logged_in
    connected, _ = await communicator.connect()
    assert connected

    # Ensure we go past the initial bash messages returned (shell startup)
    await communicator.receive_from()

    json_data = json.dumps(
        {"action": "save_history", "data": {"command": "[adin@adin test]$ ls"}}
    )
    # Test sending text
    await communicator.send_to(text_data=json_data)
    await communicator.send_to(text_data=json_data)
    await sleep(1)

    log_entry_count, _ = await get_log_entry()
    terminal_command_count, terminal_command = await get_terminal_command()

    assert log_entry_count == 2
    assert terminal_command_count == 1

    assert terminal_command.command == "ls"
    assert terminal_command.prompt == "shell"
    assert terminal_command.created_by_id == superuser_logged_in.id
    assert terminal_command.execution_count == 2

    await communicator.disconnect()
