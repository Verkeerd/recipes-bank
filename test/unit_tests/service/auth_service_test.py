import os
import pytest
from unittest.mock import MagicMock

from app.service.auth_service import AuthService
from app.domain.schema.user_request import UserRequest


os.environ["SECRET_AUTH_KEY"] = "test-secret"


@pytest.fixture
def user_repo():
    repo = MagicMock()
    repo.db = MagicMock()
    return repo


@pytest.fixture
def auth_service(user_repo):
    return AuthService(user_repo)


@pytest.fixture
def user_request():
    return UserRequest(
        name="jan",
        email="jan@test.com",
        username="jan",
        password="password123",
    )


def test_add_user_success(auth_service, user_repo, user_request):
    # Arrange
    user = MagicMock()
    user.username = "jan"
    user.account = MagicMock()

    user_repo.save.return_value = user

    # Act
    result = auth_service.add_user(user_request)

    # Assert
    assert result.username == "jan"
    assert result.account is not None
    user_repo.save.assert_called_once()


def test_add_user_duplicate_username(auth_service, user_repo, user_request):
    # Arrange
    user_repo.save.side_effect = Exception("user_username_key")

    # Act + Assert
    with pytest.raises(Exception):
        auth_service.add_user(user_request)


def test_password_hashing_and_verification(auth_service):
    # Arrange
    password = "secret"

    # Act
    hashed = auth_service.encrypt_password(password)

    # Assert
    assert hashed != password
    assert auth_service.verify_password(password, hashed) is True
    assert auth_service.verify_password("wrong", hashed) is False


def test_authenticate_user_success(auth_service, user_repo):
    # Arrange
    user = MagicMock()
    user.username = "jan"
    user.account.password = auth_service.encrypt_password("password123")

    user_repo.get_by_username.return_value = user

    # Act
    result = auth_service.authenticate_user("jan", "password123")

    # Assert
    assert result == user


def test_authenticate_user_wrong_password(auth_service, user_repo):
    # Arrange
    user = MagicMock()
    user.username = "jan"
    user.account.password = auth_service.encrypt_password("password123")

    user_repo.get_by_username.return_value = user

    # Act
    result = auth_service.authenticate_user("jan", "wrong")

    # Assert
    assert result is None


def test_authenticate_user_not_found(auth_service, user_repo):
    # Arrange
    user_repo.get_by_username.return_value = None

    # Act
    result = auth_service.authenticate_user("jan", "password")

    # Assert
    assert result is None


def test_create_access_token_contains_sub(auth_service):
    # Arrange
    token = auth_service.create_access_token({"username": "jan"})

    assert isinstance(token, str)

    # Act
    payload = auth_service.get_user_from_token.__func__.__globals__["jwt"].decode(
        token,
        "test-secret",
        algorithms=["HS256"],
    )

    # Assert
    assert payload["sub"] == "jan"


def test_get_user_from_token_success(auth_service, user_repo):
    # Arrange
    token = auth_service.create_access_token({"username": "jan"})

    user = MagicMock()
    user.username = "jan"

    user_repo.get_by_username.return_value = user

    # Act
    result = auth_service.get_user_from_token(token)

    # Assert
    assert result == user


def test_get_user_from_token_invalid(auth_service):
    # Act
    result = auth_service.get_user_from_token("invalid.token.here")

    # Assert
    assert result is None