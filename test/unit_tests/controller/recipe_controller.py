import uuid
import pytest
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.controller.recipe_controller import recipe_router
from app.core.auth import get_current_user
from app.core.service_factory import get_services


def fake_user():
    return MagicMock(id=uuid.uuid4(), username="testuser")


class FakeRecipeService:
    def __init__(self):
        self.get_all_recipes = MagicMock()
        self.create_recipe = MagicMock()
        self.get_recipe = MagicMock()
        self.update_recipe = MagicMock()
        self.delete_recipe = MagicMock()
        self.query_recipe = MagicMock()


class FakeServices:
    def __init__(self):
        self.recipe = FakeRecipeService()

def create_pasta_recipe():
    recipe = MagicMock()
    recipe.id = uuid.uuid4()
    recipe.name = "Pasta"
    recipe.description = "Simple pasta recipe"
    recipe.vegetarian = True
    recipe.servings = 2
    recipe.recipe_ingredients = []
    recipe.steps = []

    return recipe

@pytest.fixture
def client():
    app = FastAPI()
    app.include_router(recipe_router)

    fake_services = FakeServices()

    def override_get_services():
        return fake_services

    def override_get_current_user():
        return fake_user()

    app.dependency_overrides[get_services] = override_get_services
    app.dependency_overrides[get_current_user] = override_get_current_user

    return TestClient(app), fake_services

def test_get_recipes(client):
    client, services = client

    recipe1 = create_pasta_recipe()

    recipe2 = MagicMock()
    recipe2.id = uuid.uuid4()
    recipe2.name = "Soup"
    recipe2.description = "Flavorful Soup"
    recipe2.vegetarian = False
    recipe2.servings = 1
    recipe2.recipe_ingredients = []
    recipe2.steps = []

    services.recipe.get_all_recipes.return_value = [recipe1, recipe2]

    response = client.get("/recipe/")

    assert response.status_code == 200
    services.recipe.get_all_recipes.assert_called_once()


def test_create_recipe(client):
    client, services = client

    services.recipe.create_recipe.return_value = create_pasta_recipe()

    response = client.post(
        "/recipe/",
        json={
            "name": "Pasta",
            "description": "desc",
            "ingredients": [{"name": "salt", "amount": 1, "unit": "tsp"}],
            "steps": ["boil water"],
            "vegetarian": True,
            "servings": 2,
        },
    )

    assert response.status_code == 200
    services.recipe.create_recipe.assert_called_once()

def test_get_recipe_success(client):
    client, services = client

    services.recipe.get_recipe.return_value = create_pasta_recipe()

    response = client.get(f"/recipe/{uuid.uuid4()}")

    assert response.status_code == 200
    services.recipe.get_recipe.assert_called_once()

def test_get_recipe_not_found(client):
    client, services = client

    services.recipe.get_recipe.return_value = None

    response = client.get(f"/recipe/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"

def test_update_recipe_success(client):
    client, services = client

    services.recipe.update_recipe.return_value = create_pasta_recipe()

    response = client.put(
        f"/recipe/{uuid.uuid4()}",
        json={
            "name": "Updated",
            "vegetarian": False,
            "ingredients": None,
            "steps": None,
            "servings": None,
        },
    )

    assert response.status_code == 200
    services.recipe.update_recipe.assert_called_once()

def test_update_recipe_not_found(client):
    client, services = client

    services.recipe.update_recipe.return_value = None

    response = client.put(
        f"/recipe/{uuid.uuid4()}",
        json={
            "name": "Updated",
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"

def test_delete_recipe_success(client):
    client, services = client

    services.recipe.delete_recipe.return_value = True

    response = client.delete(f"/recipe/{uuid.uuid4()}")

    assert response.status_code == 200
    assert response.json() == {"message": "Recipe deleted successfully"}

def test_delete_recipe_not_found(client):
    client, services = client

    services.recipe.delete_recipe.return_value = False

    response = client.delete(f"/recipe/{uuid.uuid4()}")

    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found"


def test_query_recipes_success(client):
    client, services = client

    recipe1 = create_pasta_recipe()
    recipe2 = create_pasta_recipe()
    recipe2.name = "Soup"

    services.recipe.query_recipe.return_value = [recipe1, recipe2]

    response = client.post(
        "/recipe/query",
        json={
            "description_include": None,
            "description_exclude": None,
            "ingredients_include": None,
            "ingredients_exclude": None,
            "vegetarian": None,
            "servings": None,
        },
    )

    assert response.status_code == 200
    services.recipe.query_recipe.assert_called_once()


def test_query_recipes_not_found(client):
    client, services = client
    services.recipe.query_recipe.return_value = []

    response = client.post(
        "/recipe/query",
        json={
            "description_include": None,
            "description_exclude": None,
            "ingredients_include": None,
            "ingredients_exclude": None,
            "vegetarian": None,
            "servings": None,
        },
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "No recipes with the given filters found"


def test_query_recipes_passes_request_to_service(client):
    client, services = client

    services.recipe.query_recipe.return_value = [create_pasta_recipe()]

    payload = {
        "description_include": ["boil"],
        "description_exclude": None,
        "ingredients_include": ["salt"],
        "ingredients_exclude": None,
        "vegetarian": True,
        "servings": 2,
    }

    response = client.post("/recipe/query", json=payload)

    assert response.status_code == 200

    # ensure request object was passed
    args, _ = services.recipe.query_recipe.call_args
    request = args[0]

    assert request.vegetarian is True
    assert request.servings == 2

def test_query_recipes_does_not_modify_response(client):
    client, services = client

    recipe = create_pasta_recipe()
    services.recipe.query_recipe.return_value = [recipe]

    response = client.post(
        "/recipe/query",
        json={
            "description_include": None,
            "description_exclude": None,
            "ingredients_include": None,
            "ingredients_exclude": None,
            "vegetarian": None,
            "servings": None,
        },
    )

    assert response.status_code == 200
    services.recipe.query_recipe.assert_called_once()
