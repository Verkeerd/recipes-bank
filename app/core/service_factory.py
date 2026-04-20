from sqlalchemy.orm import Session
from fastapi import Depends

from app.core.database import get_db
from app.service.recipe_service import RecipeService
from app.service.ingredient_service import IngredientService
from app.service.auth_service import AuthService
from app.core.services import Services
from app.repository.recipe_repository import RecipeRepository
from app.repository.ingredient_repository import IngredientRepository
from app.repository.user_repository import UserRepository


def build_services(db: Session) -> Services:
    recipe_repo = RecipeRepository(db)
    ingredient_repo = IngredientRepository(db)
    user_repo = UserRepository(db)

    ingredient_service = IngredientService(ingredient_repo)

    recipe_service = RecipeService(
        recipe_repo,
        ingredient_service=ingredient_service,
    )

    auth_service = AuthService(user_repo)

    return Services(
        recipe=recipe_service,
        ingredient=ingredient_service,
        auth=auth_service,
    )


def get_services(db: Session = Depends(get_db)) -> Services:
    return build_services(db)
