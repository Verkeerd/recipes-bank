import os
import uuid
from unittest.mock import MagicMock

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.controller.auth_controller import auth_router
from app.core.auth import get_auth_service
from app.service.auth_service import AuthService


os.environ["SECRET_AUTH_KEY"] = "test-secret"


@pytest.fixture
def auth_service_mock():
    return MagicMock(spec=AuthService)


@pytest.fixture
def client(auth_service_mock):
    app = FastAPI()
    app.include_router(auth_router)

    def override_get_auth_service():
        return auth_service_mock

    app.dependency_overrides[get_auth_service] = override_get_auth_service

    yield TestClient(app)

    app.dependency_overrides.clear()


def test_create_user_success(client, auth_service_mock):
    fake_user = MagicMock()
    fake_user.username = "jan"
    fake_user.email = "jan@test.com"
    fake_user.name = "Jan"
    fake_user.id = uuid.uuid4()

    auth_service_mock.add_user.return_value = fake_user

    response = client.post(
        "/auth/create",
        json={
            "username": "jan",
            "email": "jan@test.com",
            "name": "Jan",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json()["username"] == "jan"

    auth_service_mock.add_user.assert_called_once()


def test_create_user_duplicate_username(client, auth_service_mock):
    from fastapi import HTTPException

    auth_service_mock.add_user.side_effect = HTTPException(
        status_code=409,
        detail="Username already exists",
    )

    response = client.post(
        "/auth/create",
        json={
            "username": "jan",
            "email": "jan@test.com",
            "name": "Jan",
            "password": "password123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "Username already exists"


def test_login_success(client, auth_service_mock):
    fake_user = MagicMock()
    fake_user.username = "jan"

    auth_service_mock.authenticate_user.return_value = fake_user
    auth_service_mock.create_access_token.return_value = "fake-jwt-token"

    response = client.post(
        "/auth/login",
        data={
            "username": "jan",
            "password": "password123",
        },
    )

    assert response.status_code == 200
    assert response.json()["access_token"] == "fake-jwt-token"
    assert response.json()["token_type"] == "bearer"

    auth_service_mock.authenticate_user.assert_called_once_with(
        "jan", "password123"
    )


def test_login_invalid_credentials(client, auth_service_mock):
    auth_service_mock.authenticate_user.return_value = None

    response = client.post(
        "/auth/login",
        data={
            "username": "jan",
            "password": "wrong",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username or password"


def test_login_calls_token_creation(client, auth_service_mock):
    fake_user = MagicMock()
    fake_user.username = "jan"

    auth_service_mock.authenticate_user.return_value = fake_user
    auth_service_mock.create_access_token.return_value = "jwt-token"

    client.post(
        "/auth/login",
        data={
            "username": "jan",
            "password": "password123",
        },
    )

    auth_service_mock.create_access_token.assert_called_once()

    _, kwargs = auth_service_mock.create_access_token.call_args

    assert kwargs["expires_minutes"] == 60
    assert kwargs["data"]["sub"] == "jan"
