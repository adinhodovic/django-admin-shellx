import json
from asyncio.exceptions import CancelledError

import pytest
from channels.testing import WebsocketCommunicator

from django_admin_shellx.consumers import TerminalConsumer

from .conftest import BASIC_BASH_COMMANDS

pytestmark = pytest.mark.django_db


@pytest.mark.asyncio
async def test_settings_custom_command(settings, superuser_logged_in):
    settings.DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY = False
    settings.DJANGO_ADMIN_SHELLX_COMMANDS = BASIC_BASH_COMMANDS
    communicator = WebsocketCommunicator(TerminalConsumer.as_asgi(), "/testws/")
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
    communicator = WebsocketCommunicator(TerminalConsumer.as_asgi(), "/testws/")
    communicator.scope["user"] = superuser_logged_in
    connected, _ = await communicator.connect()
    assert connected

    # Ensure we go past the initial bash messages returned (shell startup)
    response = await communicator.receive_from()
    assert "Shell Plus" in response

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_closes_connection_on_exit(settings, superuser_logged_in):
    settings.DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY = False
    settings.DJANGO_ADMIN_SHELLX_COMMANDS = BASIC_BASH_COMMANDS
    communicator = WebsocketCommunicator(TerminalConsumer.as_asgi(), "/testws/")
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

    # Wait 5 seconds for the shell to close
    await communicator.wait(1)

    await communicator.send_to(
        text_data=json.dumps({"action": "input", "data": {"message": "ls"}})
    )
    with pytest.raises(CancelledError):
        await communicator.receive_from()
