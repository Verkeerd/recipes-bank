import uuid

from fastapi import APIRouter, Depends, HTTPException

from app.core.dependencies import get_services
from app.core.services import Services

from app.domain.schema import RecipeRequest, RecipeUpdate, RecipeResponse


recipe_router = APIRouter(prefix="/recipe", tags=["Recipes"])


@recipe_router.get("/", response_model=list[RecipeResponse])
def get_recipes(services: Services = Depends(get_services)):
    return [RecipeResponse.from_orm_recipe(r) for r in services.recipe.get_all_recipes()]

@recipe_router.post("/", response_model=RecipeResponse)
def create_recipe(
    recipe: RecipeRequest,
    services: Services = Depends(get_services),
):
    return RecipeResponse.from_orm_recipe(services.recipe.create_recipe(recipe))

@recipe_router.get("/{recipe_id}", response_model=RecipeResponse)
def get_recipe(
    recipe_id: uuid.UUID,
    services: Services = Depends(get_services),
):
    recipe = services.recipe.get_recipe(recipe_id)

    if not recipe:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return RecipeResponse.from_orm_recipe(recipe)

@recipe_router.put("/{recipe_id}", response_model=RecipeResponse)
def update_recipe(
    recipe_id: uuid.UUID,
    recipe: RecipeUpdate,
    services: Services = Depends(get_services),
):
    updated = services.recipe.update_recipe(recipe_id, recipe)

    if not updated:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return RecipeResponse.from_orm_recipe(updated)

@recipe_router.delete("/{recipe_id}")
def delete_recipe(
    recipe_id: uuid.UUID,
    services: Services = Depends(get_services),
):
    deleted = services.recipe.delete_recipe(recipe_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Recipe not found")

    return {"message": "Recipe deleted successfully"}
