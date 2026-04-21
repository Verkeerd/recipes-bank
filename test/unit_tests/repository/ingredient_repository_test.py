import pytest
from unittest.mock import MagicMock

from app.domain.model import Ingredient
from app.repository.ingredient_repository import IngredientRepository


@pytest.fixture
def db_session():
    return MagicMock()


@pytest.fixture
def repository(db_session):
    return IngredientRepository(db_session)


def test_get_by_name_returns_ingredient(repository, db_session):
    # Arrange
    mock_query = MagicMock()
    mock_filter = MagicMock()
    expected_ingredient = Ingredient("sugar")

    db_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = expected_ingredient

    # Act
    result = repository.get_by_name("sugar")

    # Assert
    db_session.query.assert_called_once_with(Ingredient)
    mock_query.filter.assert_called_once()
    mock_filter.first.assert_called_once()
    assert result == expected_ingredient


def test_get_by_name_returns_none_when_not_found(repository, db_session):
    # Arrange
    mock_query = MagicMock()
    mock_filter = MagicMock()

    db_session.query.return_value = mock_query
    mock_query.filter.return_value = mock_filter
    mock_filter.first.return_value = None

    # Act
    result = repository.get_by_name("nonexistent")

    # Assert
    assert result is None


def test_add_calls_add_and_flush(repository, db_session):
    # Arrange
    ingredient = Ingredient(name="salt")

    # Act
    repository.add(ingredient)

    # Assert
    db_session.add.assert_called_once_with(ingredient)
    db_session.flush.assert_called_once()