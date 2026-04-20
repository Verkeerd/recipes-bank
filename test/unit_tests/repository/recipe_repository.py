import uuid
import pytest
from unittest.mock import MagicMock

from app.domain.model import Recipe
from app.repository.recipe_repository import RecipeRepository


@pytest.fixture
def db_session():
    return MagicMock()


@pytest.fixture
def repository(db_session):
    return RecipeRepository(db_session)


def test_add_calls_session_add(repository, db_session):
    # Arrange
    recipe = Recipe()

    # Act
    repository.add(recipe)

    # Assert
    db_session.add.assert_called_once_with(recipe)


def test_get_all_builds_query_with_options(repository, db_session):
    # Arrange
    mock_query = MagicMock()
    mock_loaded_query = MagicMock()

    db_session.query.return_value = mock_query
    mock_query.options.return_value = mock_loaded_query
    mock_loaded_query.all.return_value = []

    # Act
    result = repository.get_all()

    # Assert
    db_session.query.assert_called_once_with(Recipe)
    mock_query.options.assert_called_once()
    mock_loaded_query.all.assert_called_once()
    assert result == []


def test_get_by_id_returns_recipe(repository, db_session):
    # Arrange
    recipe_id = uuid.uuid4()

    mock_query = MagicMock()
    mock_loaded_query = MagicMock()
    expected_recipe = Recipe()

    db_session.query.return_value = mock_query
    mock_query.options.return_value = mock_loaded_query
    mock_loaded_query.filter.return_value.first.return_value = expected_recipe

    # Act
    result = repository.get_by_id(recipe_id)

    # Assert
    db_session.query.assert_called_once_with(Recipe)
    mock_loaded_query.filter.assert_called_once()
    assert result == expected_recipe


def test_get_by_id_returns_none(repository, db_session):
    # Arrange
    recipe_id = uuid.uuid4()

    mock_query = MagicMock()
    mock_loaded_query = MagicMock()

    db_session.query.return_value = mock_query
    mock_query.options.return_value = mock_loaded_query
    mock_loaded_query.filter.return_value.first.return_value = None

    # Act
    result = repository.get_by_id(recipe_id)

    # Assert
    assert result is None


def test_delete_calls_session_delete(repository, db_session):
    # Arrange
    recipe = Recipe()

    # Act
    repository.delete(recipe)

    # Assert
    db_session.delete.assert_called_once_with(recipe)


def test_refresh_calls_session_refresh_and_returns_entity(repository, db_session):
    # Arrange
    entity = Recipe()

    # Act
    result = repository.refresh(entity)

    # Assert
    db_session.refresh.assert_called_once_with(entity)
    assert result == entity