from unittest.mock import MagicMock

import pytest
import uuid

from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.database import Base
from app.core.services import Services
from app.core.service_factory import get_services

from app.controller.recipe_controller import recipe_router

from app.repository.recipe_repository import RecipeRepository
from app.repository.ingredient_repository import IngredientRepository
from app.service.recipe_service import RecipeService
from app.service.ingredient_service import IngredientService


TEST_DB_URL = "sqlite:///./test.db"  # important: NOT in-memory for stability

engine = create_engine(
    TEST_DB_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(bind=engine)


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

    app.dependency_overrides[get_services] = override_get_services

    return TestClient(app)


# -----------------------
# TEST HELPERS
# -----------------------

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


# -----------------------
# TESTS
# -----------------------

def test_get_recipes_empty(client):
    response = client.get("/recipe/")

    assert response.status_code == 200
    assert response.json() == []


def test_create_and_get_recipe(client):
    create_resp = client.post("/recipe/", json=create_payload())

    assert create_resp.status_code == 200

    data = create_resp.json()
    recipe_id = data["id"]

    get_resp = client.get(f"/recipe/{recipe_id}")

    assert get_resp.status_code == 200
    assert get_resp.json()["name"] == "Pasta"


def test_update_recipe_flow(client):
    create_resp = client.post("/recipe/", json=create_payload(name="Old"))
    recipe_id = create_resp.json()["id"]

    update_resp = client.put(
        f"/recipe/{recipe_id}",
        json={
            "name": "New Name",
            "vegetarian": False,
        },
    )
    print(update_resp.json())
    
    assert update_resp.status_code == 200
    assert update_resp.json()["name"] == "New Name"


def test_delete_recipe_flow(client):
    create_resp = client.post("/recipe/", json=create_payload(name="To Delete"))
    recipe_id = create_resp.json()["id"]

    delete_resp = client.delete(f"/recipe/{recipe_id}")
    assert delete_resp.status_code == 200

    get_resp = client.get(f"/recipe/{recipe_id}")
    assert get_resp.status_code == 404