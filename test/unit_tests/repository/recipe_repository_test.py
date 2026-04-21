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


def test_apply_vegetarian_filter_applies_true_filter():
    # Arrange
    query = MagicMock()
    filtered_query = MagicMock()
    query.filter.return_value = filtered_query

    # Act
    result = RecipeRepository.apply_vegetarian_filter(query, True)

    # Assert
    query.filter.assert_called_once()
    assert result == filtered_query


def test_apply_vegetarian_filter_with_none_does_not_fail():
    # Arrange
    query = MagicMock()

    # Act
    result = RecipeRepository.apply_vegetarian_filter(query, None)

    # Assert
    assert result == query


def test_apply_servings_filter_applies_when_value_present():
    # Arrange
    query = MagicMock()
    filtered_query = MagicMock()
    query.filter.return_value = filtered_query

    # Act
    result = RecipeRepository.apply_servings_filter(query, 4)

    # Assert
    query.filter.assert_called_once()
    assert result == filtered_query


def test_apply_servings_filter_skips_when_none():
    # Arrange
    query = MagicMock()

    # Act
    result = RecipeRepository.apply_servings_filter(query, None)

    # Assert
    assert result == query

def test_apply_ingredient_filters_no_terms_returns_query():
    # Arrange
    query = MagicMock()

    # Act
    result = RecipeRepository.apply_ingredient_filters(query)

    # Assert
    assert result == query
    query.join.assert_not_called()

def test_apply_ingredient_filters_with_include_terms_builds_filter():
    # Arrange
    query = MagicMock()
    joined = MagicMock()
    filtered = MagicMock()

    query.join.return_value = joined
    joined.join.return_value = joined
    joined.filter.return_value = filtered

    # Act
    result = RecipeRepository.apply_ingredient_filters(
        query,
        include_terms=["tomato", "cheese"]
    )

    # Assert
    query.join.assert_called()
    joined.filter.assert_called()
    assert result == filtered

def test_apply_ingredient_filters_with_exclude_terms():
    # Arrange
    query = MagicMock()
    joined = MagicMock()
    filtered = MagicMock()

    query.join.return_value = joined
    joined.join.return_value = joined
    joined.filter.return_value = filtered

    # Act
    result = RecipeRepository.apply_ingredient_filters(
        query,
        exclude_terms=["nuts"]
    )

    # Assert
    joined.filter.assert_called()
    assert result == filtered

def test_apply_step_filters_with_include_terms():
    # Arrange
    query = MagicMock()
    filtered = MagicMock()
    query.filter.return_value = filtered

    # Act
    result = RecipeRepository.apply_step_filters(
        query,
        include_terms=["boil", "fry"]
    )

    # Assert
    query.filter.assert_called()
    assert result == filtered

def test_apply_step_filters_with_exclude_terms():
    # Arrange
    query = MagicMock()
    filtered = MagicMock()
    query.filter.return_value = filtered

    # Act
    result = RecipeRepository.apply_step_filters(
        query,
        exclude_terms=["burnt"]
    )

    # Assert
    query.filter.assert_called()
    assert result == filtered

def test_build_query_applies_all_filters(repository, db_session):
    # Arrange
    request = MagicMock()
    request.description_include = ["boil"]
    request.description_exclude = ["burnt"]
    request.ingredients_include = ["egg"]
    request.ingredients_exclude = ["milk"]
    request.vegetarian = True
    request.servings = 2

    base_query = MagicMock()
    db_session.query.return_value = base_query
    base_query.distinct.return_value = base_query

    # chain mocks for filter methods
    base_query.filter.return_value = base_query
    base_query.join.return_value = base_query

    # Act
    result = repository.build_query(request)

    # Assert
    db_session.query.assert_called_once_with(Recipe)
    base_query.distinct.assert_called_once()

    assert result == base_query