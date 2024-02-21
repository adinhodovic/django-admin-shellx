import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth.models import User

from .factories import UserFactory


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
@pytest.mark.django_db
def user_logged_in(client, user):
    """
    Creates an authenticated user client.
    """
    client.force_login(user)
    return user


@pytest.fixture
@pytest.mark.django_db
def superuser_logged_in(user_logged_in):
    user_logged_in.is_superuser = True
    user_logged_in.save()
    return user_logged_in


class AuthWebsocketCommunicator(WebsocketCommunicator):
    def __init__(self, application, path, headers=None, subprotocols=None, user=None):
        super(AuthWebsocketCommunicator, self).__init__(
            application, path, headers, subprotocols
        )
        if user is not None:
            self.scope["user"] = user
