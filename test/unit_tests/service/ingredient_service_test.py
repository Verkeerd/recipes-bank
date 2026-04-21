import uuid
from unittest.mock import MagicMock

from app.domain.model import Ingredient, RecipeIngredient
from app.service.ingredient_service import IngredientService


class DummyItem:
    def __init__(self, name, amount, unit):
        self.name = name
        self.amount = amount
        self.unit = unit


def test_add_ingredients_creates_new_ingredient_when_not_found():
    # Arrange
    repo = MagicMock()
    service = IngredientService(repo)

    item = DummyItem(name="sugar", amount=100, unit="g")

    repo.get_by_name.return_value = None

    # Act
    result = service.add_ingredients([item])

    # Assert
    repo.get_by_name.assert_called_once_with("sugar")
    repo.add.assert_called_once()

    added_ingredient = repo.add.call_args[0][0]
    assert isinstance(added_ingredient, Ingredient)
    assert added_ingredient.name == "sugar"

    assert len(result) == 1
    assert isinstance(result[0], RecipeIngredient)
    assert result[0].amount == 100
    assert result[0].unit == "g"


def test_add_ingredients_reuses_existing_ingredient():
    # Arrange
    repo = MagicMock()
    service = IngredientService(repo)

    existing = Ingredient(name="salt", uuid=uuid.uuid4())
    item = DummyItem(name="salt", amount=5, unit="g")

    repo.get_by_name.return_value = existing

    # Act
    result = service.add_ingredients([item])

    # Assert
    repo.get_by_name.assert_called_once_with("salt")
    repo.add.assert_not_called()

    assert len(result) == 1
    assert result[0].ingredient == existing
    assert result[0].amount == 5
    assert result[0].unit == "g"


def test_add_ingredients_multiple_items_mixed_existing_and_new():
    # Arrange
    repo = MagicMock()
    service = IngredientService(repo)

    existing = Ingredient(name="salt", uuid=uuid.uuid4())

    items = [
        DummyItem("salt", 5, "g"),     # existing
        DummyItem("sugar", 10, "g"),   # new
    ]

    def side_effect(name):
        return existing if name == "salt" else None

    repo.get_by_name.side_effect = side_effect

    # Act
    result = service.add_ingredients(items)

    # Assert
    assert repo.get_by_name.call_count == 2
    repo.add.assert_called_once()

    assert len(result) == 2

    assert result[0].ingredient == existing

    new_ingredient = repo.add.call_args[0][0]
    assert result[1].ingredient == new_ingredient