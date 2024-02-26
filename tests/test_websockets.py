import json

import pytest

from django_admin_shellx.consumers import TerminalConsumer

from .conftest import BASIC_BASH_COMMANDS, DefaultTimeoutWebsocketCommunicator

pytestmark = pytest.mark.django_db


@pytest.mark.asyncio
async def test_websocket_rejects_unauthenticated():
    communicator = DefaultTimeoutWebsocketCommunicator(
        TerminalConsumer.as_asgi(), "/testws/"
    )
    connected, subprotocol = await communicator.connect()
    assert not connected
    assert subprotocol == 4401
    await communicator.disconnect()


@pytest.mark.asyncio
async def test_websocket_accepts_authenticated_user(settings, user_logged_in):
    settings.DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY = False

    communicator = DefaultTimeoutWebsocketCommunicator(
        TerminalConsumer.as_asgi(), "/testws/"
    )
    communicator.scope["user"] = user_logged_in
    connected, _ = await communicator.connect()
    assert connected
    # Test sending text
    await communicator.send_to(
        text_data=json.dumps({"action": "input", "data": {"message": "ls"}})
    )
    response = await communicator.receive_from()
    assert response == '{"message": "ls"}'

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_websocket_accepts_authenticated_superuser(superuser_logged_in):
    communicator = DefaultTimeoutWebsocketCommunicator(
        TerminalConsumer.as_asgi(), "/testws/"
    )
    communicator.scope["user"] = superuser_logged_in
    connected, _ = await communicator.connect()
    assert connected
    # Test sending text
    await communicator.send_to(
        text_data=json.dumps({"action": "input", "data": {"message": "ls"}})
    )
    response = await communicator.receive_from()
    assert response == '{"message": "ls"}'

    await communicator.disconnect()


@pytest.mark.asyncio
async def test_websocket_send_command(settings, superuser_logged_in):
    settings.DJANGO_ADMIN_SHELLX_SUPERUSER_ONLY = False
    settings.DJANGO_ADMIN_SHELLX_COMMANDS = BASIC_BASH_COMMANDS
    communicator = DefaultTimeoutWebsocketCommunicator(
        TerminalConsumer.as_asgi(), "/testws/"
    )
    communicator.scope["user"] = superuser_logged_in
    connected, _ = await communicator.connect()
    assert connected

    # Ensure we go past the initial bash messages returned (shell startup)
    await communicator.receive_from()

    await communicator.send_to(
        text_data=json.dumps({"action": "input", "data": {"message": "ls\r"}})
    )

    # Command returned from the bash command
    await communicator.receive_from()

    response = await communicator.receive_from()
    assert "LICENSE" in response

    await communicator.disconnect()
