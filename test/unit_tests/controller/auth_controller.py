import os
import uuid

import pytest
from fastapi.testclient import TestClient
from fastapi import HTTPException
from unittest.mock import MagicMock

from app.domain.schema.user_response import UserResponse
from app.main import app
from app.core.auth import get_auth_service
from app.service.auth_service import AuthService

os.environ["SECRET_AUTH_KEY"] = "test-secret"


@pytest.fixture
def auth_service_mock():
    return MagicMock(spec=AuthService)


@pytest.fixture
def client(auth_service_mock):
    app.dependency_overrides[get_auth_service] = lambda: auth_service_mock
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_create_user_success(client, auth_service_mock):
    # Arrange
    auth_service_mock.add_user.return_value = UserResponse(
        id = uuid.uuid4(),
        username="jan",
        email="jan@test.com",
        name="Jan"
    )

    # Act
    response = client.post(
        "/auth/create",
        json={
            "username": "jan",
            "email": "jan@test.com",
            "name": "Jan",
            "password": "password123"
        }
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["username"] == "jan"


def test_create_user_duplicate_username(client, auth_service_mock):
    # Arrange
    auth_service_mock.add_user.side_effect = HTTPException(
        status_code=409,
        detail="Username already exists"
    )

    # Act
    response = client.post(
        "/auth/create",
        json={
            "username": "jan",
            "email": "jan@test.com",
            "name": "Jan",
            "password": "password123"
        }
    )

    # Assert
    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"


def test_login_success(client, auth_service_mock):
    # Arrange
    user = MagicMock()
    user.username = "jan"

    auth_service_mock.authenticate_user.return_value = user
    auth_service_mock.create_access_token.return_value = "fake-jwt-token"

    # Act
    response = client.post(
        "/auth/login",
        data={
            "username": "jan",
            "password": "password123"
        }
    )

    # Assert
    assert response.status_code == 200
    assert response.json()["access_token"] == "fake-jwt-token"
    assert response.json()["token_type"] == "bearer"


def test_login_invalid_credentials(client, auth_service_mock):
    # Arrange
    auth_service_mock.authenticate_user.return_value = None

    # Act
    response = client.post(
        "/auth/login",
        data={
            "username": "jan",
            "password": "wrong_password"
        }
    )

    # Assert
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_calls_token_creation(client, auth_service_mock):
    # Arrange
    user = MagicMock()
    user.username = "jan"

    auth_service_mock.authenticate_user.return_value = user
    auth_service_mock.create_access_token.return_value = "jwt-token"

    # Act
    client.post(
        "/auth/login",
        data={"username": "jan", "password": "password123"}
    )

    # Assert
    auth_service_mock.create_access_token.assert_called_once()

    _, kwargs = auth_service_mock.create_access_token.call_args

    assert kwargs["expires_minutes"] == 60
    assert kwargs["data"]["sub"] == "jan"