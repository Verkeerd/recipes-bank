import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.core.auth import get_current_user
from app.core.services import Services
from app.core.service_factory import get_services

from app.domain.schema import RecipeRequest, RecipeUpdate, RecipeResponse
from app.domain.schema.recipe.recipe_query import RecipeQuery


recipe_router = APIRouter(prefix="/recipe", tags=["Recipes"])


@recipe_router.get(
    "/",
    response_model=list[RecipeResponse],
    summary="Get all recipes",
    description="""
Retrieve all recipes in the system.

Returns full recipe objects including:
- ingredients
- ordered steps
- metadata (vegetarian flag, servings)
""",
)
def get_recipes(services: Services = Depends(get_services)):
    """
    Fetch all recipes.

    Returns:
        list[RecipeResponse]: List of recipes
    """
    return [RecipeResponse.from_orm_recipe(r) for r in services.recipe.get_all_recipes()]


@recipe_router.post(
    "/",
    response_model=RecipeResponse,
    status_code=201,
    summary="Create a recipe",
    description="""
Create a new recipe.

### Authentication
Required (JWT Bearer token)

### Notes
- Recipes must include at least:
  - 1 ingredient
  - 1 step
- Steps can be sent as strings or structured objects
- Vegetarian flag is stored at recipe level (not ingredient level)
""",
    responses={
        201: {"description": "Recipe successfully created"},
        401: {"description": "Unauthorized"},
        422: {"description": "Validation error"},
    },
)
def create_recipe(
    recipe: RecipeRequest,
    services: Services = Depends(get_services),
    user=Depends(get_current_user)
):
    """
    Create a recipe.

    Args:
        recipe: Recipe creation payload
        services: Service container
        user: Authenticated user

    Returns:
        RecipeResponse: Created recipe
    """
    return RecipeResponse.from_orm_recipe(services.recipe.create_recipe(recipe))


@recipe_router.get(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Get recipe by ID",
    description="Retrieve a single recipe using its UUID.",
    responses={
        404: {"description": "Recipe not found"},
    },
)
def get_recipe(
    recipe_id: uuid.UUID,
    services: Services = Depends(get_services),
):
    """
    Fetch a recipe by ID.

    Args:
        recipe_id: UUID of the recipe

    Returns:
        RecipeResponse: Recipe data

    Raises:
        HTTPException: If recipe is not found
    """
    recipe = services.recipe.get_recipe(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return RecipeResponse.from_orm_recipe(recipe)


@recipe_router.put(
    "/{recipe_id}",
    response_model=RecipeResponse,
    summary="Update a recipe",
    description="""
Update an existing recipe.

### Authentication
Required (JWT Bearer token)

### Behavior
- Partial updates allowed
- Fields not provided remain unchanged
- Ingredients and steps can be replaced entirely if provided
""",
    responses={
        401: {"description": "Unauthorized"},
        404: {"description": "Recipe not found"},
    },
)
def update_recipe(
    recipe_id: uuid.UUID,
    recipe: RecipeUpdate,
    services: Services = Depends(get_services),
    user=Depends(get_current_user)
):
    """
    Update a recipe.

    Args:
        recipe_id: UUID of the recipe
        recipe: Partial update payload
        services: Service container
        user: Authenticated user

    Returns:
        RecipeResponse: Updated recipe

    Raises:
        HTTPException: If recipe is not found
    """
    updated = services.recipe.update_recipe(recipe_id, recipe)

    if not updated:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return RecipeResponse.from_orm_recipe(updated)


@recipe_router.delete(
    "/{recipe_id}",
    summary="Delete a recipe",
    description="""
Delete a recipe by ID.

### Authentication
Required (JWT Bearer token)

### Notes
- Permanent deletion
- No soft delete implemented
""",
    responses={
        200: {"description": "Recipe deleted successfully"},
        401: {"description": "Unauthorized"},
        404: {"description": "Recipe not found"},
    },
)
def delete_recipe(
    recipe_id: uuid.UUID,
    services: Services = Depends(get_services),
    user=Depends(get_current_user)
):
    """
    Delete a recipe.

    Args:
        recipe_id: UUID of the recipe
        services: Service container
        user: Authenticated user

    Returns:
        dict: Success message

    Raises:
        HTTPException: If recipe is not found
    """
    deleted = services.recipe.delete_recipe(recipe_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {"message": "Recipe deleted successfully"}


@recipe_router.post(
    "/query",
    response_model=list[RecipeResponse],
    summary="Query recipes",
    description="""
Search recipes using flexible filters.

### Supported filters:
- description keywords (include/exclude)
- ingredients (include/exclude)
- vegetarian flag
- number of servings

### Behavior:
- All filters are optional
- Empty result returns 404
""",
    responses={
        404: {"description": "No recipes found matching filters"},
    },
)
def query_recipes(
    request: RecipeQuery,
    services: Services = Depends(get_services),
):
    """
    Query recipes based on filters.

    Args:
        request: Query filter object
        services: Service container

    Returns:
        list[RecipeResponse]: Matching recipes

    Raises:
        HTTPException: If no recipes match filters
    """
    fetched = services.recipe.query_recipe(request)

    if not fetched:
        raise HTTPException(status_code=404, detail="No recipes with the given filters found")

    return [RecipeResponse.from_orm_recipe(recipe) for recipe in fetched]
