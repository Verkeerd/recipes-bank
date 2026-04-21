import os
import uuid
import pytest
from unittest.mock import MagicMock

from fastapi import HTTPException

from app.service.auth_service import AuthService
from app.domain.schema.user_request import UserRequest


# -----------------------
# FIX ENV (IMPORTANT)
# -----------------------
os.environ["SECRET_AUTH_KEY"] = "test-secret"


# -----------------------
# FIXTURES
# -----------------------
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
        name="John",
        email="john@test.com",
        username="john",
        password="password123",
    )


# -----------------------
# TESTS
# -----------------------
def test_add_user_success(auth_service, user_repo, user_request):
    user = MagicMock()
    user.username = "john"
    user.account = MagicMock()

    user_repo.save.return_value = user

    result = auth_service.add_user(user_request)

    assert result.username == "john"
    assert result.account is not None
    user_repo.save.assert_called_once()


def test_add_user_duplicate_username(auth_service, user_repo, user_request):
    user_repo.save.side_effect = Exception("user_username_key")

    with pytest.raises(Exception):
        auth_service.add_user(user_request)


def test_password_hashing_and_verification(auth_service):
    password = "secret"

    hashed = auth_service.encrypt_password(password)

    assert hashed != password
    assert auth_service.verify_password(password, hashed) is True
    assert auth_service.verify_password("wrong", hashed) is False


def test_authenticate_user_success(auth_service, user_repo):
    user = MagicMock()
    user.username = "john"
    user.account.password = auth_service.encrypt_password("password123")

    user_repo.get_by_username.return_value = user

    result = auth_service.authenticate_user("john", "password123")

    assert result == user


def test_authenticate_user_wrong_password(auth_service, user_repo):
    user = MagicMock()
    user.username = "john"
    user.account.password = auth_service.encrypt_password("password123")

    user_repo.get_by_username.return_value = user

    result = auth_service.authenticate_user("john", "wrong")

    assert result is None


def test_authenticate_user_not_found(auth_service, user_repo):
    user_repo.get_by_username.return_value = None

    result = auth_service.authenticate_user("john", "password")

    assert result is None


def test_create_access_token_contains_sub(auth_service):
    token = auth_service.create_access_token({"username": "john"})

    assert isinstance(token, str)

    # decode manually to verify payload
    payload = auth_service.get_user_from_token.__func__.__globals__["jwt"].decode(
        token,
        "test-secret",
        algorithms=["HS256"],
    )

    assert payload["sub"] == "john"


def test_get_user_from_token_success(auth_service, user_repo):
    token = auth_service.create_access_token({"username": "john"})

    user = MagicMock()
    user.username = "john"

    user_repo.get_by_username.return_value = user

    result = auth_service.get_user_from_token(token)

    assert result == user


def test_get_user_from_token_invalid(auth_service):
    result = auth_service.get_user_from_token("invalid.token.here")

    assert result is None