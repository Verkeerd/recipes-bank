import uuid
from unittest.mock import MagicMock

import pytest

from app.domain.model import Recipe, RecipeStep
from app.service.recipe_service import RecipeService


# =========================
# FIXTURES
# =========================

@pytest.fixture
def repo():
    repo = MagicMock()
    repo.db = MagicMock()
    return repo


@pytest.fixture
def ingredient_service():
    return MagicMock()


@pytest.fixture
def service(repo, ingredient_service):
    return RecipeService(repo, ingredient_service)


def build_update(
    name=None,
    ingredients=None,
    steps=None,
    vegetarian=None,
    servings=None,
):
    data = MagicMock()
    data.name = name
    data.ingredients = ingredients
    data.steps = steps
    data.vegetarian = vegetarian
    data.servings = servings
    return data


def test_create_recipe_success(service, repo, ingredient_service):
    """
    Service must create all building blocks of a recipe.

    Add ingredients to the database through the ingredient service. Add these
    ingredients with an amount and unit to the recipe. Number steps and add these
    to the recipe and add this recipe to the database.
    """
    # Arrange
    request = MagicMock()
    request.name = "Pasta"
    request.description = "a la dente"
    request.vegetarian = True
    request.servings = 2
    request.ingredients = ["pasta"]
    request.steps = [MagicMock(description="boil pasta for 20 minutes.")]

    ingredient_service.add_ingredients.return_value = [MagicMock()]
    repo.refresh.return_value = "final_recipe"

    # Act
    result = service.create_recipe(request)

    # Assert
    repo.add.assert_called_once()
    repo.db.commit.assert_called_once()
    repo.refresh.assert_called_once()

    assert result == "final_recipe"


def test_number_recipe_steps(service):
    """Service must number the steps with increments of one."""
    # Arrange
    steps = [
        MagicMock(description="step1"),
        MagicMock(description="step2"),
    ]

    # Act
    result = service.number_recipe_steps(steps)

    # Assert
    assert len(result) == 2
    assert result[0].step_number == 1
    assert result[0].description == "step1"
    assert result[1].step_number == 2


def test_update_recipe_full_update(service, repo, ingredient_service):
    # Arrange
    recipe = Recipe()

    repo.get_by_id.return_value = recipe
    repo.refresh.return_value = "updated"

    data = MagicMock()
    data.name = "Honey Milk"
    data.vegetarian = False
    data.servings = 1

    milk = MagicMock()
    milk.name = "milk"
    milk.amount = 250
    milk.unit = "ml"

    honey = MagicMock()
    honey.name = "honey"
    honey.amount = 2
    honey.unit = "tsp"

    data.ingredients = [milk, honey]

    step = MagicMock()
    step.description = "step"
    data.steps = [step]

    recipe_ingredients = [MagicMock(), MagicMock()]
    ingredient_service.add_ingredients.return_value = recipe_ingredients

    # Act
    result = service.update_recipe(uuid.uuid4(), data)

    # Assert
    assert recipe.name == "Honey Milk"
    assert recipe.vegetarian is False

    ingredient_service.add_ingredients.assert_called_once()

    passed_args = ingredient_service.add_ingredients.call_args[0][0]
    assert len(passed_args) == 2
    assert passed_args[0].name == "milk"
    assert passed_args[1].name == "honey"

    assert recipe.recipe_ingredients == recipe_ingredients

    repo.db.commit.assert_called_once()
    repo.refresh.assert_called_once_with(recipe)

    assert result == "updated"


@pytest.mark.parametrize(
    "field, value",
    [
        ("name", "new name"),
        ("vegetarian", True),
        ("servings", 5),
    ],
)
def test_update_recipe_single_fields(service, repo, field, value):
    # Arrange
    recipe = Recipe(name="old", vegetarian=False, servings=1)

    repo.get_by_id.return_value = recipe
    repo.refresh.return_value = recipe

    data = build_update(**{field: value})

    # Act
    service.update_recipe(uuid.uuid4(), data)

    # Assert
    assert getattr(recipe, field) == value
    repo.db.commit.assert_called_once()


def test_update_recipe_only_steps(service, repo):
    # Arrange
    recipe = Recipe(name="old")

    repo.get_by_id.return_value = recipe
    repo.refresh.return_value = recipe

    step1 = MagicMock()
    step1.description = "first"

    step2 = MagicMock()
    step2.description = "second"

    data = build_update(
        steps=[step1, step2],
        ingredients=None,
        name=None,
        vegetarian=None,
        servings=None,
    )

    # Act
    service.update_recipe(uuid.uuid4(), data)

    # Assert
    assert len(recipe.steps) == 2

    assert recipe.steps[0].step_number == 1
    assert recipe.steps[0].description == "first"

    assert recipe.steps[1].step_number == 2
    assert recipe.steps[1].description == "second"

    repo.db.commit.assert_called_once()


def test_update_recipe_only_ingredients(service, repo, ingredient_service):
    # Arrange
    recipe = Recipe(name="old")

    repo.get_by_id.return_value = recipe
    repo.refresh.return_value = recipe

    milk = MagicMock()
    milk.name = "milk"
    milk.amount = 250
    milk.unit = "ml"

    honey = MagicMock()
    honey.name = "honey"
    honey.amount = 2
    honey.unit = "tsp"

    data = build_update(
        ingredients=[milk, honey],
        steps=None,
        name=None,
        vegetarian=None,
        servings=None,
    )

    ri1 = MagicMock()
    ri2 = MagicMock()

    ingredient_service.add_ingredients.return_value = [ri1, ri2]

    # Act
    service.update_recipe(uuid.uuid4(), data)

    # Assert
    ingredient_service.add_ingredients.assert_called_once()

    passed_args = ingredient_service.add_ingredients.call_args[0][0]

    assert len(passed_args) == 2
    assert passed_args[0].name == "milk"
    assert passed_args[1].name == "honey"

    assert recipe.recipe_ingredients == [ri1, ri2]

    repo.db.commit.assert_called_once()


def test_get_all_recipes(service, repo):
    # Arrange
    repo.get_all.return_value = ["first_recipe", "second_recipe"]

    # Act
    result = service.get_all_recipes()

    # Assert
    assert result == ["first_recipe", "second_recipe"]
    repo.get_all.assert_called_once()


def test_delete_recipe_success(service, repo):
    # Arrange
    recipe = Recipe()
    repo.get_by_id.return_value = recipe

    # Act
    result = service.delete_recipe(uuid.uuid4())

    # Assert
    assert result is True
    repo.delete.assert_called_once_with(recipe)
    repo.db.commit.assert_called_once()


def test_delete_recipe_not_found(service, repo):
    # Arrange
    repo.get_by_id.return_value = None

    # Act
    result = service.delete_recipe(uuid.uuid4())

    # Assert
    assert result is False
    repo.delete.assert_not_called()
    repo.db.commit.assert_not_called()