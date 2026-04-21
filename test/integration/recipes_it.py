import uuid
from unittest.mock import MagicMock

import pytest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.auth import get_current_user
from app.core.database import Base
from app.core.services import Services
from app.core.service_factory import get_services

from app.controller.recipe_controller import recipe_router

from app.repository.recipe_repository import RecipeRepository
from app.repository.ingredient_repository import IngredientRepository
from app.service.recipe_service import RecipeService
from app.service.ingredient_service import IngredientService


TEST_DB_URL = "sqlite:///./test.db"

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(bind=engine)


def fake_user():
    return MagicMock(id=uuid.uuid4(), username="testuser")


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def services(db_session):
    recipe_repo = RecipeRepository(db_session)
    ingredient_repo = IngredientRepository(db_session)

    ingredient_service = IngredientService(ingredient_repo)
    recipe_service = RecipeService(recipe_repo, ingredient_service)

    return Services(
        recipe=recipe_service,
        ingredient=ingredient_service,
        auth=MagicMock(),  # not needed for these tests
    )


@pytest.fixture
def client(services):
    app = FastAPI()
    app.include_router(recipe_router)

    def override_get_services():
        return services

    app.dependency_overrides[get_current_user] = fake_user
    app.dependency_overrides[get_services] = override_get_services

    return TestClient(app)


def create_payload(**overrides):
    base = {
        "name": "Pasta",
        "description": "desc",
        "ingredients": [{"name": "salt", "amount": 1, "unit": "tsp"}],
        "steps": ["boil water"],
        "vegetarian": True,
        "servings": 2,
    }
    base.update(overrides)
    return base


def create_recipe_in_db(client, payload):
    response = client.post("/recipe/", json=payload)
    assert response.status_code == 200
    return response.json()


def test_get_recipes_empty(client):
    # Arrange
    response = client.get("/recipe/")

    # Assert
    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_recipe(client):
    # Arrange
    create_resp = client.post("/recipe/", json=create_payload())

    assert create_resp.status_code == 200

    data = create_resp.json()
    recipe_id = data["id"]

    # Act
    get_resp = client.get(f"/recipe/{recipe_id}")

    # Assert
    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Pasta"


def test_update_recipe_flow(client):
    # Arrange
    create_resp = client.post("/recipe/", json=create_payload(name="Old"))
    recipe_id = create_resp.json()["id"]

    # Act
    update_resp = client.put(
        f"/recipe/{recipe_id}",
        json={
            "name": "New Name",
            "vegetarian": False,
        },
    )

    # Assert
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "New Name"


def test_delete_recipe_flow(client):
    create_resp = client.post("/recipe/", json=create_payload(name="To Delete"))
    recipe_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/recipe/{recipe_id}")
    assert delete_resp.status_code == 200

    get_resp = client.get(f"/recipe/{recipe_id}")
    assert get_resp.status_code == 404


def test_query_recipes_returns_results(client):
    # Arrange
    create_recipe_in_db(client, create_payload(name="Pasta", vegetarian=True))
    create_recipe_in_db(client, create_payload(name="Chicken Soup", vegetarian=False))

    # Act
    response = client.post(
        "/recipe/query",
        json={
            "description_include": None,
            "description_exclude": None,
            "ingredients_include": None,
            "ingredients_exclude": None,
            "vegetarian": True,
            "servings": None,
        },
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Pasta"


def test_query_recipes_returns_404_when_empty(client):
    # Act
    response = client.post(
        "/recipe/query",
        json={
            "vegetarian": True,
            "description_include": None,
            "description_exclude": None,
            "ingredients_include": None,
            "ingredients_exclude": None,
            "servings": None,
        },
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "No recipes with the given filters found"


def test_query_recipes_by_servings(client):
    # Arrange
    create_recipe_in_db(client, create_payload(name="A", servings=2))
    create_recipe_in_db(client, create_payload(name="B", servings=4))

    # Act
    response = client.post(
        "/recipe/query",
        json={
            "servings": 2,
            "vegetarian": None,
            "description_include": None,
            "description_exclude": None,
            "ingredients_include": None,
            "ingredients_exclude": None,
        },
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["servings"] == 2


def test_query_recipes_by_ingredient_include(client):
    # Arrange
    create_recipe_in_db(
        client,
        create_payload(
            name="Pasta",
            ingredients=[{"name": "salt", "amount": 1, "unit": "tsp"}],
        ),
    )

    create_recipe_in_db(
        client,
        create_payload(
            name="Cake",
            ingredients=[{"name": "sugar", "amount": 100, "unit": "g"}],
        ),
    )

    # Act
    response = client.post(
        "/recipe/query",
        json={
            "ingredients_include": ["salt"],
            "ingredients_exclude": None,
            "vegetarian": None,
            "servings": None,
            "description_include": None,
            "description_exclude": None,
        },
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Pasta"


def test_query_recipes_excludes_ingredients(client):
    # Arrange
    create_recipe_in_db(
        client,
        create_payload(
            name="Pasta",
            ingredients=[{"name": "milk", "amount": 1, "unit": "l"}],
        ),
    )

    create_recipe_in_db(
        client,
        create_payload(
            name="Soup",
            ingredients=[{"name": "water", "amount": 1, "unit": "l"}],
        ),
    )

    # Act
    response = client.post(
        "/recipe/query",
        json={
            "ingredients_exclude": ["milk"],
            "ingredients_include": None,
            "vegetarian": None,
            "servings": None,
            "description_include": None,
            "description_exclude": None,
        },
    )

    # Assert
    assert response.status_code == 200
    data = response.json()

    assert all("milk" not in str(r["ingredients"]) for r in data)