import pytest
from django.contrib.auth.models import User  # pylint: disable=imported-auth-user

from .factories import UserFactory

BASIC_BASH_COMMANDS = [
    ["env", "-i", "bash", "--norc", "--noprofile"],
]


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
@pytest.mark.django_db
def user_logged_in(client, user):  # pylint: disable=redefined-outer-name
    """
    Creates an authenticated user client.
    """
    client.force_login(user)
    return user


@pytest.fixture
@pytest.mark.django_db
def superuser_logged_in(user_logged_in):  # pylint: disable=redefined-outer-name
    user_logged_in.is_superuser = True
    user_logged_in.save()
    return user_logged_in
